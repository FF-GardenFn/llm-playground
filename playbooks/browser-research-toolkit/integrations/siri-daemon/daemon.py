#!/usr/bin/env python3
"""
Siri Shortcut → Python daemon bridge for Browser Research Toolkit.

- Runs a local FastAPI server on your Mac (default to 0.0.0.0:8373 via uvicorn command).
- Endpoint /siri parses utterances like:
  • "Research API migration audit on stripe.com/docs, github.com/stripe/*"
  • "triage API migration audit"
  • "open https://docs.google.com/document/d/..."
- Calls your configured orchestrator:
  • orchestrators/chrome-extension/orchestrator.py
  • orchestrators/mcp-clients/runner.py
- Returns clean JSON so Shortcuts can pop a confirmation.

Security:
- Requires Bearer token (set in config.yaml). Rejects unauthenticated calls.
- This is designed for LAN use. Do not expose to WAN. Use a firewall.
- Only runs configured orchestrator paths; no arbitrary shell commands.

Quick start:
  uvicorn daemon:app --host 0.0.0.0 --port 8373
"""
from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import yaml
from collections import deque

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.yaml"


def load_config() -> dict:
    """Load config.yaml if present, otherwise fall back to example."""
    if CONFIG_PATH.exists():
        return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    example = HERE / "config.example.yaml"
    return yaml.safe_load(example.read_text(encoding="utf-8")) if example.exists() else {}


cfg = load_config()
TOKEN = cfg.get("token", "changeme")
PLAYBOOKS = cfg.get("playbooks", {})
SECURITY = cfg.get("security", {})
# Security toggles (defaults disabled)
MAX_UTTER = int(SECURITY.get("max_utterance_len", 0))  # 0 = no limit
STRICT_DOMAINS = bool(SECURITY.get("strict_domain_validation", False))
ENABLE_PII = bool(SECURITY.get("enable_pii_redaction", False))
RATE_LIMIT = int(SECURITY.get("rate_limit_per_minute", 0))  # 0 = disabled

# rate limit buckets per-IP (timestamps in seconds)
_RATE_BUCKETS: dict[str, deque] = {}

app = FastAPI(title="BRT Siri Bridge", version="0.1.0")


def check_auth(req: Request) -> None:
    auth = req.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    if auth.split(" ", 1)[1].strip() != str(TOKEN):
        raise HTTPException(403, "Bad token")
    # Per-IP simple rate limit if enabled
    if RATE_LIMIT > 0:
        ip = (req.client.host if req.client else "?") or "?"
        now = time.time()
        bucket = _RATE_BUCKETS.setdefault(ip, deque())
        # drop entries older than 60s
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT:
            raise HTTPException(429, "Rate limit exceeded")
        bucket.append(now)


class Command(BaseModel):
    action: str
    playbook: str
    task_title: Optional[str] = None
    domains: Optional[List[str]] = None
    phase: Optional[str] = None
    doc_url: Optional[str] = None


def _redact_pii(text: str) -> str:
    if not text:
        return text
    # Emails
    text = re.sub(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+", "[redacted-email]", text)
    # Long numeric sequences (potential keys/phones)
    text = re.sub(r"\b[0-9]{12,}\b", "[redacted-number]", text)
    # Basic API key-like patterns
    text = re.sub(r"\b(sk|key|token|api)[_:-][A-Za-z0-9]{16,}\b", "[redacted-key]", text, flags=re.I)
    return text


_DOMAIN_PAT = re.compile(r"^(?:https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^*\s]*)?\*?$")

def _valid_domain_pattern(p: str) -> bool:
    return bool(_DOMAIN_PAT.match(p))


def run_orchestrator(playbook: str, title: str, domains: List[str], extra_args: Optional[List[str]] = None):
    conf = PLAYBOOKS.get(playbook)
    if not conf:
        raise RuntimeError(f"Unknown playbook: {playbook}")
    orch = conf.get("orchestrator_path")
    if not orch or not Path(orch).exists():
        raise RuntimeError(f"orchestrator not found: {orch}")
    python = conf.get("python", "python3")
    # Defensive: cap args length to avoid abuse from utterances
    safe_title = title.strip()[:200]
    safe_domains = [d.strip()[:200] for d in (domains or []) if d.strip()]
    args = [python, orch, safe_title] + safe_domains
    if extra_args:
        args += list(extra_args)[:4]
    env = os.environ.copy()
    if conf.get("doc_url"):
        env["BRT_SHARED_DOC_URL"] = str(conf["doc_url"])[:1024]
    # Short timeout to avoid hanging the daemon; orchestrators are expected to be quick emitters
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False, env=env)
    return proc.returncode, proc.stdout, proc.stderr


@app.post("/command")
async def command(req: Request, cmd: Command):
    check_auth(req)
    t0 = time.time()
    if cmd.action == "start_task":
        if not cmd.task_title or not cmd.domains:
            raise HTTPException(400, "task_title and domains required")
        rc, out, err = run_orchestrator(cmd.playbook, cmd.task_title, cmd.domains)
        if ENABLE_PII:
            out = _redact_pii(out or "")
            err = _redact_pii(err or "")
        return {"ok": rc == 0, "duration_s": round(time.time() - t0, 2), "stdout": (out or "")[-4000:], "stderr": (err or "")[-4000:]}
    if cmd.action == "run_phase":
        if not cmd.task_title or not cmd.phase:
            raise HTTPException(400, "task_title and phase required")
        phase = cmd.phase.strip().lower()
        if phase not in {"triage", "harvest", "synthesize", "report", "clean"}:
            raise HTTPException(400, "invalid phase")
        rc, out, err = run_orchestrator(cmd.playbook, cmd.task_title, cmd.domains or [], ["--phase", phase])
        if ENABLE_PII:
            out = _redact_pii(out or "")
            err = _redact_pii(err or "")
        return {"ok": rc == 0, "duration_s": round(time.time() - t0, 2), "stdout": (out or "")[-4000:], "stderr": (err or "")[-4000:]}
    if cmd.action == "open_url":
        url = cmd.doc_url or ((cmd.domains or [None])[0])
        if not url:
            raise HTTPException(400, "doc_url or domains[0] required")
        # macOS only; no error if "open" is unavailable
        subprocess.run(["open", url], check=False)
        return {"ok": True, "opened": url}
    raise HTTPException(400, f"Unknown action: {cmd.action}")


class SiriPayload(BaseModel):
    utterance: str
    playbook: str = "chrome"
    doc_url: Optional[str] = None


RE_RESEARCH = re.compile(r"^(?:research|start|open)\s+(.+?)\s+(?:on|about)\s+([\w\.\-\/\*\s,]+)$", re.I)
RE_PHASE = re.compile(r"^(triage|harvest|synthesize|report|clean)\s+(?:task\s+)?(.+)$", re.I)


@app.post("/siri")
async def siri(req: Request, payload: SiriPayload):
    check_auth(req)
    u = (payload.utterance or "").strip()
    if MAX_UTTER and len(u) > MAX_UTTER:
        raise HTTPException(413, "Utterance too long")
    m = RE_RESEARCH.match(u)
    if m:
        title = m.group(1).strip()
        raw_domains = [d.strip() for d in re.split(r"[, ]+", m.group(2).strip()) if d.strip()]
        domains = raw_domains
        if STRICT_DOMAINS:
            domains = [d for d in raw_domains if _valid_domain_pattern(d)]
            if not domains:
                raise HTTPException(400, "No valid domains after strict validation")
        return await command(req, Command(action="start_task", playbook=payload.playbook, task_title=title, domains=domains, doc_url=payload.doc_url))
    m2 = RE_PHASE.match(u)
    if m2:
        phase = m2.group(1).lower()
        title = m2.group(2).strip()
        return await command(req, Command(action="run_phase", playbook=payload.playbook, task_title=title, domains=[], phase=phase))
    if u.lower().startswith("open "):
        url = u.split(" ", 1)[1].strip()
        return await command(req, Command(action="open_url", playbook=payload.playbook, doc_url=url))
    return {"handled": False, "hint": "Try: 'Research <title> on <domain1, domain2>' or 'triage <title>'"}

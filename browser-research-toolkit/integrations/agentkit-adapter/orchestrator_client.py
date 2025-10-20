#!/usr/bin/env python3
"""
Thin client over the existing Chrome Extension orchestrator CLI and STATUS.json.

Purpose
- Provide simple Python-callable functions that mirror the orchestrator CLI
  so external agents (e.g., OpenAI Agents SDK) can call into BRT without
  shelling or reimplementing logic.

Functions
- start_task(title, allowlist, doc_url=None) -> {charter_id, task_dir}
- run_phase(title_or_charter_id, phase) -> {ok, charter_id, phase}
- get_status(title_or_charter_id) -> dict (STATUS.json)

Notes
- This adapter does not change orchestrator behavior. It shells out to
  orchestrators/chrome-extension/orchestrator.py and reads ~/.tab_orchestrator.
- Keep inputs small; this module enforces basic length limits.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path.home() / ".tab_orchestrator" / "tasks"
ORCH_PATH = Path(__file__).resolve().parents[2] / "orchestrators" / "chrome-extension" / "orchestrator.py"
PYTHON = os.environ.get("BRT_PYTHON", "python3")

_MAX_TITLE = 200
_MAX_DOMAINS = 12
_MAX_DOMAIN_LEN = 200


@dataclass
class StartResult:
    charter_id: str
    task_dir: str


def _slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return (s[:60] if len(s) > 60 else s) or "task"


def _latest_task_dir_for_title(title: str) -> Optional[Path]:
    prefix = _slugify(title) + "_"
    if not ROOT.exists():
        return None
    candidates = [p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.name)
    return candidates[-1]


def start_task(title: str, allowlist: List[str], doc_url: Optional[str] = None) -> StartResult:
    title = (title or "").strip()[:_MAX_TITLE]
    if not title:
        raise ValueError("title required")
    domains = [d.strip()[:_MAX_DOMAIN_LEN] for d in (allowlist or []) if d and d.strip()]
    if not domains:
        raise ValueError("allowlist (domains) required")
    if len(domains) > _MAX_DOMAINS:
        domains = domains[:_MAX_DOMAINS]

    env = os.environ.copy()
    if doc_url:
        env["BRT_SHARED_DOC_URL"] = str(doc_url)[:1024]

    proc = subprocess.run(
        [PYTHON, str(ORCH_PATH), title, *domains], capture_output=True, text=True, timeout=90, check=False, env=env
    )
    if proc.returncode != 0:
        raise RuntimeError(f"orchestrator failed: rc={proc.returncode}: {proc.stderr.strip()}")

    # Find created dir by title
    tdir = _latest_task_dir_for_title(title)
    if not tdir:
        raise RuntimeError("task directory not found after orchestrator run")
    return StartResult(charter_id=tdir.name, task_dir=str(tdir))


def run_phase(title_or_charter_id: str, phase: str) -> Dict[str, str]:
    phase = (phase or "").strip().lower()
    if phase not in {"init-group", "triage", "harvest", "synthesize", "report", "clean"}:
        raise ValueError("invalid phase")
    title_or_charter_id = (title_or_charter_id or "").strip()
    if not title_or_charter_id:
        raise ValueError("title_or_charter_id required")

    # Prefer title-based invocation for orchestrator; it resolves latest dir
    args = [PYTHON, str(ORCH_PATH), title_or_charter_id, "--phase", phase]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"orchestrator phase failed: rc={proc.returncode}: {proc.stderr.strip()}")

    # Resolve charter_id
    tdir = _latest_task_dir_for_title(title_or_charter_id)
    charter_id = tdir.name if tdir else title_or_charter_id
    return {"ok": True, "charter_id": charter_id, "phase": phase}


def _status_path_from_any(identifier: str) -> Path:
    # Try as exact directory name first
    p = ROOT / identifier
    if p.exists():
        return p / "STATUS.json"
    # Else assume title -> find latest
    tdir = _latest_task_dir_for_title(identifier)
    if not tdir:
        raise FileNotFoundError(f"task not found for identifier: {identifier}")
    return tdir / "STATUS.json"


def get_status(title_or_charter_id: str) -> Dict:
    sp = _status_path_from_any(title_or_charter_id)
    if not sp.exists():
        return {}
    return json.loads(sp.read_text(encoding="utf-8"))

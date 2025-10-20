#!/usr/bin/env python3
"""
BRT Charter MCP-like HTTP server (minimal).

Purpose
- Expose Charter operations as HTTP tools to be invoked from MCP-capable clients
  or Agents adapters. This is not a full MCP server; it provides a simple, secure
  HTTP JSON API with the same semantics.

Tools (HTTP endpoints)
- POST /tools/brt_start_task         { title, allowlist[], doc_url? }
- POST /tools/brt_advance_phase      { title_or_charter_id, phase }
- GET  /tools/brt_get_status         ?id=<title_or_charter_id>
- POST /tools/brt_add_evidence       { charter_id, url, text, selector?, last_updated? }
- POST /tools/brt_search_evidence    { charter_id, query, k? }
- POST /tools/brt_validate_domain    { charter_id, url }

Security
- Require Authorization: Bearer <token>; token set via env BRT_CHARTER_API_KEY.
- Enforce JSON Content-Type and basic max sizes.
- URL allowlist enforced by reading allowed_domains from CHARTER.md.

Notes
- Evidence store is per-process and ephemeral (task-local), using packages/memory-store.
- This server is intended for localhost/LAN use.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

# Load orchestrator client dynamically by file path to avoid package context
import importlib.util
import types
import sys as _sys

OC_DIR = Path(__file__).resolve().parents[2] / "integrations" / "agentkit-adapter"
OC_FILE = OC_DIR / "orchestrator_client.py"
_oc_spec = importlib.util.spec_from_file_location("agentkit_adapter.orchestrator_client", OC_FILE)
if not _oc_spec or not _oc_spec.loader:  # pragma: no cover
    raise ImportError(f"Failed to load orchestrator_client from {OC_FILE}")
_oc_mod = importlib.util.module_from_spec(_oc_spec)
_sys.modules["agentkit_adapter.orchestrator_client"] = _oc_mod
_oc_spec.loader.exec_module(_oc_mod)  # type: ignore[attr-defined]
StartResult = getattr(_oc_mod, "StartResult")
start_task = getattr(_oc_mod, "start_task")
run_phase = getattr(_oc_mod, "run_phase")
get_status = getattr(_oc_mod, "get_status")

# Dynamic import of memory_store similar to orchestrator
PKG_DIR = Path(__file__).resolve().parents[2] / "packages" / "memory-store"
MEM_FILE = PKG_DIR / "memory.py"

pkg_name = "memory_store"
if pkg_name not in _sys.modules:
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(PKG_DIR)]
    _sys.modules[pkg_name] = pkg
_mem_spec = importlib.util.spec_from_file_location(f"{pkg_name}.memory", MEM_FILE)
if not _mem_spec or not _mem_spec.loader:  # pragma: no cover
    raise ImportError(f"Failed to load Memory module from {MEM_FILE}")
_mem_mod = importlib.util.module_from_spec(_mem_spec)
_sys.modules[f"{pkg_name}.memory"] = _mem_mod
_mem_spec.loader.exec_module(_mem_mod)  # type: ignore[attr-defined]
Memory = getattr(_mem_mod, "Memory")

TASKS_ROOT = Path.home() / ".tab_orchestrator" / "tasks"
API_KEY = os.environ.get("BRT_CHARTER_API_KEY", "changeme")

app = FastAPI(title="BRT Charter Tools", version="0.1.0")

# In-process memory instances per charter
_MEM_INSTANCES: Dict[str, any] = {}


class StartTaskBody(BaseModel):
    title: str
    allowlist: List[str]
    doc_url: Optional[str] = None


class AdvancePhaseBody(BaseModel):
    title_or_charter_id: str
    phase: str


class AddEvidenceBody(BaseModel):
    charter_id: str
    url: str
    text: str
    selector: Optional[str] = "#"
    last_updated: Optional[str] = None


class SearchEvidenceBody(BaseModel):
    charter_id: str
    query: str
    k: int = 5


class ValidateDomainBody(BaseModel):
    charter_id: str
    url: str


async def auth(req: Request) -> None:
    auth = req.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    if auth.split(" ", 1)[1].strip() != str(API_KEY):
        raise HTTPException(403, "Bad token")
    # Size check
    cl = req.headers.get("content-length")
    if cl and int(cl) > 512_000:
        raise HTTPException(413, "Request too large")


def _load_allowed_domains(charter_id: str) -> List[str]:
    # Parse CHARTER.md minimal YAML-like list
    tdir = TASKS_ROOT / charter_id
    cpath = tdir / "CHARTER.md"
    if not cpath.exists():
        return []
    text = cpath.read_text(encoding="utf-8")
    m = re.search(r"allowed_domains:\s*\n((?:[ \t]*- .+\n)+)", text)
    out: List[str] = []
    if not m:
        return out
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            out.append(line[2:].strip())
    return out


def _url_allowed(url: str, allowed: List[str]) -> bool:
    for pat in allowed:
        if pat.endswith("*"):
            if url.startswith(pat[:-1]):
                return True
        else:
            if url.startswith(pat):
                return True
    return False


def _memory_for(charter_id: str):
    mem = _MEM_INSTANCES.get(charter_id)
    if mem is None:
        mem = Memory(charter_id)
        _MEM_INSTANCES[charter_id] = mem
    return mem


@app.post("/tools/brt_start_task")
async def brt_start_task(body: StartTaskBody, _: None = Depends(auth)):
    res: StartResult = start_task(body.title, body.allowlist, body.doc_url)
    return {"charter_id": res.charter_id, "task_dir": res.task_dir}


@app.post("/tools/brt_advance_phase")
async def brt_advance_phase(body: AdvancePhaseBody, _: None = Depends(auth)):
    out = run_phase(body.title_or_charter_id, body.phase)
    return out


@app.get("/tools/brt_get_status")
async def brt_get_status(id: str, _: None = Depends(auth)):
    return get_status(id)


@app.post("/tools/brt_add_evidence")
async def brt_add_evidence(body: AddEvidenceBody, _: None = Depends(auth)):
    allowed = _load_allowed_domains(body.charter_id)
    if allowed and not _url_allowed(body.url, allowed):
        raise HTTPException(400, "URL not allowed by Charter")
    # Cap text size
    text = (body.text or "")
    if len(text) > 200_000:
        raise HTTPException(413, "text too large")
    mem = _memory_for(body.charter_id)
    chunks = mem.add(body.url, text, selector=body.selector or "#", last_updated=body.last_updated)
    return {"added_chunks": len(chunks)}


@app.post("/tools/brt_search_evidence")
async def brt_search_evidence(body: SearchEvidenceBody, _: None = Depends(auth)):
    mem = _memory_for(body.charter_id)
    hits = mem.search(body.query, k=max(1, min(body.k, 20)), filters={"charter_id": body.charter_id})
    return {
        "hits": [
            {
                "score": h.score,
                "snippet": h.snippet,
                "url": h.metadata.get("url"),
                "last_updated": h.metadata.get("last_updated"),
                "selector": h.metadata.get("selector"),
            }
            for h in hits
        ]
    }


@app.post("/tools/brt_validate_domain")
async def brt_validate_domain(body: ValidateDomainBody, _: None = Depends(auth)):
    allowed = _load_allowed_domains(body.charter_id)
    return {"allowed": _url_allowed(body.url, allowed), "allowed_domains": allowed}


@app.get("/health")
async def health():
    return {"ok": True}

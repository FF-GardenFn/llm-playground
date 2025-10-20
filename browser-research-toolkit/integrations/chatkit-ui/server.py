#!/usr/bin/env python3
"""
ChatKit UI (demo-only) — minimal local server to surface STATUS.json and tools.

This is a stub intended to be wrapped by chatkit-python widgets. It provides:
- GET /tasks — list task slugs found under ~/.tab_orchestrator/tasks
- GET /status/{slug} — return STATUS.json
- (optional) POST endpoints could be added to proxy Charter tools.

Security: for local demo only; no auth in baseline. Do not expose to WAN.
"""
from __future__ import annotations

from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
import json

TASKS = Path.home() / ".tab_orchestrator" / "tasks"
app = FastAPI(title="BRT ChatKit UI (Demo)")


@app.get("/tasks")
async def tasks() -> List[str]:
    if not TASKS.exists():
        return []
    return [p.name for p in TASKS.iterdir() if p.is_dir()]


@app.get("/status/{slug}")
async def status(slug: str):
    sp = TASKS / slug / "STATUS.json"
    if not sp.exists():
        raise HTTPException(404, "STATUS.json not found")
    return json.loads(sp.read_text(encoding="utf-8"))

#!/usr/bin/env python3
"""
Agent-facing tool wrappers for Browser Research Toolkit.

These functions are plain Python wrappers around the orchestrator client. In an
Agents SDK environment, you can decorate them (e.g., @function_tool) and
register with an Agent. Keeping them dependency-free makes them easy to reuse.

Tools
- start_task_tool(title, allowlist, doc_url=None)
- run_phase_tool(phase, title)
- get_status_tool(title_or_charter_id)

Usage (pseudo-code, outside this repo):

from agents import function_tool
from agentkit_adapter.agent import start_task_tool

@function_tool
def start_task_tool(...):
    ...

Notes
- This module does not import the Agents SDK; it is integration-agnostic.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .orchestrator_client import get_status, run_phase, start_task


def start_task_tool(title: str, allowlist: List[str], doc_url: Optional[str] = None) -> Dict[str, Any]:
    res = start_task(title, allowlist, doc_url)
    return {"charter_id": res.charter_id, "task_dir": res.task_dir}


def run_phase_tool(phase: str, title: str) -> Dict[str, Any]:
    return run_phase(title, phase)


def get_status_tool(title_or_charter_id: str) -> Dict[str, Any]:
    return get_status(title_or_charter_id)

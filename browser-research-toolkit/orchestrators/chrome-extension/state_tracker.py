#!/usr/bin/env python3
"""
StateTracker — persistent STATUS.json for Browser Research Toolkit tasks.

Responsibilities:
- Initialize ~/.tab_orchestrator/tasks/<slug>/STATUS.json
- Track phases: start_phase(), complete_phase()
- Log errors and per-source progress during /harvest
- Expose get_status()
- Optionally emit benchmark metrics via benchmarks/collector.py if present

This module is designed to be imported dynamically by the orchestrator without
introducing a package dependency. It uses only the standard library and performs
best-effort dynamic loading of the optional benchmark collector.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import time
import importlib.util

ROOT = Path.home() / ".tab_orchestrator"
TASKS = ROOT / "tasks"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _duration_s(start_iso: str, end_iso: str) -> int:
    from datetime import datetime
    s = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    e = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    return int((e - s).total_seconds())


def _read_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _write_json(p: Path, obj: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def _log_metric_safe(task_slug: str, phase: str, metric: str, value: Any, notes: str = "") -> None:
    """Best-effort dynamic import of benchmarks/collector.py."""
    here = Path(__file__).resolve().parent
    mod_path = here / "benchmarks" / "collector.py"
    if not mod_path.exists():
        return
    spec = importlib.util.spec_from_file_location("brt_benchmarks_collector", mod_path)
    if not spec or not spec.loader:
        return
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        getattr(mod, "log_metric")(task_slug, phase, metric, value, notes)  # type: ignore[misc]
    except Exception:
        # Do not crash state tracking on logging failures
        return


@dataclass
class StateTracker:
    charter_id: str

    def __post_init__(self) -> None:
        self.status_file = TASKS / self.charter_id / "STATUS.json"
        if not self.status_file.exists():
            self._init_status()

    # Public API -----------------------------------------------------------
    def start_phase(self, phase: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        state = self._read()
        entry = {
            "phase": phase,
            "status": "in_progress",
            "started_at": _now(),
            "metadata": dict(metadata or {}),
        }
        state["phase_history"].append(entry)
        state["current_phase"] = phase
        state["updated_at"] = _now()
        self._write(state)

    def complete_phase(self, phase: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        state = self._read()
        done = False
        for entry in reversed(state["phase_history"]):
            if entry.get("phase") == phase and entry.get("status") == "in_progress":
                entry["status"] = "completed"
                entry["completed_at"] = _now()
                entry["duration_s"] = _duration_s(entry["started_at"], entry["completed_at"])
                if metadata:
                    entry.setdefault("metadata", {}).update(metadata)
                done = True
                # Benchmarks: log duration as t_<phase>
                dur = entry.get("duration_s")
                if isinstance(dur, int):
                    _log_metric_safe(self.charter_id, phase, f"t_{phase}", dur)
                # Specific counters
                md = entry.get("metadata") or {}
                for key in ("sources_found", "sources_processed"):
                    if key in md:
                        _log_metric_safe(self.charter_id, phase, key, md[key])
                break
        state["updated_at"] = _now()
        self._write(state)
        if not done:
            # If there was no in_progress entry, add completed entry for robustness
            self.start_phase(phase)
            self.complete_phase(phase, metadata=metadata)

    def log_error(self, phase: str, error: str) -> None:
        state = self._read()
        state["errors"].append({
            "phase": phase,
            "error": error,
            "timestamp": _now(),
        })
        state["updated_at"] = _now()
        self._write(state)

    def log_source_processed(self, url: str) -> None:
        """Update the latest in-progress phase (typically harvest) with per-source progress."""
        state = self._read()
        # Find the most recent in-progress entry
        for entry in reversed(state["phase_history"]):
            if entry.get("status") == "in_progress":
                md = entry.setdefault("metadata", {})
                md["sources_processed"] = int(md.get("sources_processed") or 0) + 1
                md["last_processed_url"] = url
                break
        state["updated_at"] = _now()
        self._write(state)

    def get_status(self) -> Dict[str, Any]:
        return self._read()

    # Internals ------------------------------------------------------------
    def _init_status(self) -> None:
        state = {
            "charter_id": self.charter_id,
            "created_at": _now(),
            "updated_at": _now(),
            "current_phase": None,
            "phase_history": [],
            "errors": [],
            "checkpoints": [],
        }
        self._write(state)

    def _read(self) -> Dict[str, Any]:
        return _read_json(self.status_file) or {
            "charter_id": self.charter_id,
            "created_at": _now(),
            "updated_at": _now(),
            "current_phase": None,
            "phase_history": [],
            "errors": [],
            "checkpoints": [],
        }

    def _write(self, state: Dict[str, Any]) -> None:
        _write_json(self.status_file, state)

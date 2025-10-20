#!/usr/bin/env python3
"""
Benchmarks collector for Browser Research Toolkit (local only).

Writes per-event metrics to JSONL and CSV files under
~/.tab_orchestrator/benchmarks.

API:
- log_metric(task_slug, phase, metric, value, notes="")
- analyze_task(task_slug) -> summary dict or None

This is a minimal dependency-free logger for quick A/B and regressions.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import csv
import json
import time

BENCH_DIR = Path.home() / ".tab_orchestrator" / "benchmarks"
BENCH_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log_metric(task_slug: str, phase: str, metric: str, value: Any, notes: str = "") -> None:
    """Append a single metric event to JSONL and a global CSV."""
    timestamp = _now()

    # JSONL: one file per task_slug
    jsonl_file = BENCH_DIR / f"{task_slug}.jsonl"
    entry = {
        "timestamp": timestamp,
        "task_slug": task_slug,
        "phase": phase,
        "metric": metric,
        "value": value,
        "notes": notes,
    }
    with jsonl_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # CSV: cumulative across all runs
    csv_file = BENCH_DIR / "all_runs.csv"
    exists = csv_file.exists()
    with csv_file.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "task_slug", "phase", "metric", "value", "notes"])
        writer.writerow([timestamp, task_slug, phase, metric, value, notes])


def analyze_task(task_slug: str) -> Dict[str, Any] | None:
    """Return simple aggregates for a completed task, or None if missing."""
    jsonl_file = BENCH_DIR / f"{task_slug}.jsonl"
    if not jsonl_file.exists():
        return None

    lines: List[str] = jsonl_file.read_text(encoding="utf-8").splitlines()
    entries: List[Dict[str, Any]] = [json.loads(line) for line in lines if line.strip()]

    # Pull out some common metrics
    def first_metric(name: str) -> Any:
        for e in entries:
            if e.get("metric") == name:
                return e.get("value")
        return None

    def sum_metric(name: str) -> int:
        total = 0
        for e in entries:
            if e.get("metric") == name:
                try:
                    total += int(e.get("value") or 0)
                except Exception:
                    continue
        return total

    summary = {
        "task_slug": task_slug,
        "t_synth_s": first_metric("t_synthesize") or first_metric("t_synth"),
        "sources_processed": sum_metric("sources_processed"),
        "perm_prompts": sum_metric("perm_prompts"),
        "total_events": len(entries),
    }
    return summary

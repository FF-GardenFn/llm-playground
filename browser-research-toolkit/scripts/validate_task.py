#!/usr/bin/env python3
"""
Validate a task run against Charter rules and provenance requirements.

Usage:
  python scripts/validate_task.py <task_slug>

Checks:
- CHARTER.md exists and allowed_domains parsed
- synthesis_snapshot.md exists (created by your /clean step)
- Every citation has URL + last-updated
- All citations are within allowed_domains
- All phases in STATUS.json are completed (if STATUS.json exists)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

TASKS_DIR = Path.home() / ".tab_orchestrator" / "tasks"


def load_charter(charter_path: Path) -> Dict[str, Any]:
    """Parse CHARTER.md into a dict (minimal YAML-like parsing)."""
    text = charter_path.read_text(encoding="utf-8")
    charter: Dict[str, Any] = {}
    # allowed_domains block
    m = re.search(r"allowed_domains:\s*\n((?:[ \t]*- .+\n)+)", text)
    allowed: List[str] = []
    if m:
        block = m.group(1)
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("- "):
                allowed.append(line[2:].strip())
    charter["allowed_domains"] = allowed
    return charter


def extract_citations(doc_text: str) -> List[Dict[str, str]]:
    """Extract all URLs and last-updated dates from synthesis snapshot.
    Pattern: "... https://example.com/... (last updated: 2025-09-14)"
    """
    citations: List[Dict[str, str]] = []
    pattern = r"(https?://[^\s)]+)\s*\(last updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\)"
    for url, date in re.findall(pattern, doc_text):
        citations.append({"url": url, "last_updated": date})
    return citations


def _url_allowed(url: str, allowed: List[str]) -> bool:
    for pat in allowed:
        if pat.endswith("*"):
            if url.startswith(pat[:-1]):
                return True
        else:
            if url.startswith(pat):
                return True
    return False


def validate_task(task_slug: str) -> List[str]:
    """Run all validation checks, return list of violations."""
    task_dir = TASKS_DIR / task_slug
    charter_path = task_dir / "CHARTER.md"
    status_path = task_dir / "STATUS.json"

    violations: List[str] = []

    if not charter_path.exists():
        return [f"Charter not found: {charter_path}"]

    charter = load_charter(charter_path)

    doc_path = task_dir / "synthesis_snapshot.md"
    if not doc_path.exists():
        violations.append("Synthesis snapshot not found. Run /clean with --snapshot flag.")
        return violations

    doc_text = doc_path.read_text(encoding="utf-8")
    citations = extract_citations(doc_text)

    # Check 1: All citations have provenance
    for c in citations:
        if not c.get("url") or not c.get("last_updated"):
            violations.append("Missing provenance in citation.")

    # Check 2: All URLs in allowed_domains
    allowed = charter.get("allowed_domains", [])
    for c in citations:
        url = c["url"]
        if not _url_allowed(url, allowed):
            violations.append(f"Domain violation: {url}")

    # Check 3: Acceptance criteria met (all phases completed)
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        for phase_entry in status.get("phase_history", []):
            if phase_entry.get("status") != "completed":
                violations.append(f"Phase {phase_entry.get('phase')} not completed")

    return violations


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task_slug", help="Task slug to validate (directory name under ~/.tab_orchestrator/tasks)")
    args = ap.parse_args(argv)

    violations = validate_task(args.task_slug)
    if not violations:
        print(f"Task {args.task_slug} passed all validation checks")
        return 0
    else:
        print(f"Task {args.task_slug} has {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 2


if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))

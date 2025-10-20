#!/usr/bin/env python3
"""
Evals runner: orchestrates a simple end-to-end task run for measurement.

This script uses the orchestrator CLI to initialize a Charter and mark phases,
then computes a citation compliance metric using claim_has_citation.py and
logs phase durations via the benchmarks collector if available.

Usage:
  python scripts/evals/runner.py --title "CLS mitigation" --domains developers.chrome.com/* web.dev/* \
      --snapshot ~/.tab_orchestrator/tasks/<slug>/synthesis_snapshot.md

Notes:
- The actual browsing/harvest/synthesize is manual or driven by your agent.
- This runner only automates the timing hooks (start/complete) and scoring.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
ORCH = ROOT / "orchestrators" / "chrome-extension" / "orchestrator.py"
PY = sys.executable or "python3"


def _run(args: List[str], timeout: int = 60) -> int:
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
    else:
        sys.stdout.write(proc.stdout)
    return proc.returncode


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--domains", nargs="+", required=True)
    ap.add_argument("--snapshot", required=False, help="Path to synthesis_snapshot.md (optional)")
    args = ap.parse_args(argv)

    # 1) Start task
    rc = _run([PY, str(ORCH), args.title, *args.domains], timeout=90)
    if rc != 0:
        return rc

    # 2) Mark phases (timing captured by StateTracker)
    for phase in ("triage", "harvest", "synthesize"):
        rc = _run([PY, str(ORCH), args.title, "--phase", phase])
        if rc != 0:
            return rc

    # 3) Optional: compute citation compliance if snapshot provided
    if args.snapshot:
        checker = ROOT / "scripts" / "evals" / "claim_has_citation.py"
        if checker.exists():
            _run([PY, str(checker), args.snapshot])

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

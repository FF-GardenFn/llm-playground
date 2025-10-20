#!/usr/bin/env python3
"""
Check that each claim-like line in a synthesis snapshot has a citation with URL and last-updated.

Usage:
  python scripts/evals/claim_has_citation.py <synthesis_snapshot.md>

This intentionally uses no external dependencies. It is a best-effort linter to
quickly estimate citation compliance.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List

# A simplistic definition of a "claim line": a non-empty line that ends with a period
# or contains a modal verb/verb and is not a heading.
_CLAIM_RE = re.compile(r"[A-Za-z].*(\.|should|must|recommends|reports|indicates|confirms)", re.I)
# Citation pattern: URL plus (last updated: YYYY-MM-DD)
_CITATION_RE = re.compile(r"https?://[^\s)]+\s*\(last updated:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}\)")


def _extract_lines(text: str) -> List[str]:
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        lines.append(s)
    return lines


def score_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = _extract_lines(text)
    if not lines:
        return 100
    claim_lines = [ln for ln in lines if _CLAIM_RE.search(ln)]
    if not claim_lines:
        return 100
    cited = sum(1 for ln in claim_lines if _CITATION_RE.search(ln))
    return int(round(100.0 * cited / max(1, len(claim_lines))))


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot", help="Path to synthesis_snapshot.md")
    args = ap.parse_args(argv)

    path = Path(args.snapshot)
    if not path.exists():
        print("File not found:", path)
        return 2
    pct = score_file(path)
    print(f"citation_compliance_percent={pct}")
    return 0


if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))

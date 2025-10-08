#!/usr/bin/env python3
"""
Emit claim helper (stub)

Purpose
- Provide a thin API for agents to emit structured claims into the shared document during /report.
- Document-only in this baseline; actual integration with Google Docs or Notion is out of scope.

API (proposed)
- format_claim(summary: str, urls: list[str], last_updated: list[str]) -> str
- validate_claim_block(text: str) -> bool
"""
from __future__ import annotations

from typing import List
import re

_CIT_RE = re.compile(r"https?://[^\s)]+\s*\(last updated:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}\)")


def format_claim(summary: str, urls: List[str], last_updated: List[str]) -> str:
    pairs = []
    for i, u in enumerate(urls):
        d = last_updated[i] if i < len(last_updated) else ""
        if d:
            pairs.append(f"{u} (last updated: {d})")
        else:
            pairs.append(u)
    cites = "\n".join(f"- {p}" for p in pairs)
    return f"Claim: {summary.strip()}\nCitations:\n{cites}\n"


def validate_claim_block(text: str) -> bool:
    # Check that at least one citation matches our pattern
    return bool(_CIT_RE.search(text or ""))

"""Parsing utilities for debater client responses.

Keeps regex and text extraction logic separate from client classes
for clarity and easier testing.
"""
import re
from typing import List

from ..debate_tree import Evidence


def parse_evidence(text: str) -> List[Evidence]:
    """Parse evidence citations from LLM response.

    Supports common formats:
    - [Source Name, url]
    - [1] Source: X, URL: Y
    - Evidence: [source] (url)
    """
    evidence_list: List[Evidence] = []

    # Pattern 1: [Source, URL]
    pattern1 = r"\[([^\]]+),\s*([^\]]+)\]"
    matches = re.findall(pattern1, text)
    for source, url in matches:
        source = source.strip()
        url = url.strip()
        if source and ("http" in url or "www" in url):
            evidence_list.append(Evidence(source=source, url=url))

    # Pattern 2: [N] Source: X, URL: Y
    pattern2 = r"\[\d+\]\s*Source:\s*([^,]+),\s*URL:\s*([^\n]+)"
    matches = re.findall(pattern2, text)
    for source, url in matches:
        source = source.strip()
        url = url.strip()
        evidence_list.append(Evidence(source=source, url=url))

    # Pattern 3: Evidence: [source] (url)
    pattern3 = r"Evidence:\s*\[([^\]]+)\]\s*\(([^\)]+)\)"
    matches = re.findall(pattern3, text)
    for source, url in matches:
        source = source.strip()
        url = url.strip()
        evidence_list.append(Evidence(source=source, url=url))

    return evidence_list


def extract_claim_content(text: str) -> str:
    """Extract claim from <claim> tags or fallback to first paragraph.

    Returns a concise string suitable as claim content.
    """
    match = re.search(r"<claim>(.*?)</claim>", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        return lines[0]

    return text.strip()

#!/usr/bin/env python3
"""
Optional NLI helper (stub).

Provides a tiny, dependency-free entailment score approximation based on
lexical overlap and directional containment. Replace with a real model
(e.g., roberta-large-mnli) when available.
"""
from __future__ import annotations

import math
import re
from typing import Tuple

_tok = re.compile(r"\w+", re.UNICODE)


def _tokens(s: str) -> set[str]:
    return set(t.lower() for t in _tok.findall(s))


def entailment_score(premise: str, hypothesis: str) -> float:
    """Return a pseudo entailment probability in [0,1].
    Heuristic: fraction of hypothesis tokens covered by premise tokens with
    a small penalty for extra premise tokens.
    """
    pt = _tokens(premise)
    ht = _tokens(hypothesis)
    if not ht:
        return 0.0
    cover = len(ht & pt) / max(1, len(ht))
    penalty = max(0, (len(pt) - len(ht))) / max(1, len(pt)) * 0.1
    return max(0.0, min(1.0, cover - penalty))


def contradicts(premise: str, hypothesis: str, threshold: float = 0.15) -> bool:
    """Very weak contradiction signal: low entailment both ways implies unknown,
    but if negation cues are present with low entailment, treat as contradiction.
    """
    e_ph = entailment_score(premise, hypothesis)
    e_hp = entailment_score(hypothesis, premise)
    if e_ph > 0.6 or e_hp > 0.6:
        return False
    cues = {"not", "no", "never", "without", "lack"}
    pt = _tokens(premise)
    ht = _tokens(hypothesis)
    return len((pt | ht) & cues) > 0 and (e_ph + e_hp) < (2 * threshold)

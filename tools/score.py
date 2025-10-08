#!/usr/bin/env python3
"""
Lightweight scoring utilities for JSONL evaluation runs.

Supports several basic metrics via CLI:
    - em       (exact match, case-insensitive)
    - substr   (gold substring inside prediction)
    - f1       (bag-of-words token F1)

Usage examples:
    python -m prompt_systems.tools.score \
        --file prompt-systems/evals/datasets/api_docs_mini.jsonl \
        --pred-field prediction --gold-field answer --metric em

The input should be JSONL with fields containing gold answers and (optionally)
model predictions. For metrics to compute meaningfully, records should include
both fields.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from typing import Dict, Iterable, List, Tuple


def load_jsonl(path: str) -> List[Dict]:
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def tokens(s: str) -> List[str]:
    s = normalize_text(re.sub(r"[^\w\s]", " ", s))
    return [t for t in s.split() if t]


def exact_match(pred: str, gold: str) -> float:
    return 1.0 if normalize_text(pred) == normalize_text(gold) else 0.0


def substring_match(pred: str, gold: str) -> float:
    return 1.0 if normalize_text(gold) in normalize_text(pred) else 0.0


def token_f1(pred: str, gold: str) -> float:
    p = tokens(pred)
    g = tokens(gold)
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    # Count overlap using multiset logic
    from collections import Counter

    cp, cg = Counter(p), Counter(g)
    overlap = sum((cp & cg).values())
    prec = overlap / max(1, sum(cp.values()))
    rec = overlap / max(1, sum(cg.values()))
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


METRICS = {
    "em": exact_match,
    "substr": substring_match,
    "f1": token_f1,
}


def score_records(records: Iterable[Dict], pred_field: str, gold_field: str, metric: str) -> Tuple[float, int]:
    fn = METRICS.get(metric)
    if fn is None:
        raise ValueError(f"Unknown metric: {metric}. Choose from {sorted(METRICS)}")
    total = 0
    agg = 0.0
    for r in records:
        if pred_field not in r or gold_field not in r:
            continue
        pred = str(r[pred_field])
        gold = str(r[gold_field])
        agg += float(fn(pred, gold))
        total += 1
    return (0.0, 0) if total == 0 else (agg / total, total)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score a JSONL file with simple metrics")
    ap.add_argument("--file", required=True, help="Path to JSONL file with predictions and gold labels")
    ap.add_argument("--pred-field", default="prediction", help="Field name for predictions (default: prediction)")
    ap.add_argument("--gold-field", default="answer", help="Field name for gold labels (default: answer)")
    ap.add_argument("--metric", default="em", choices=sorted(METRICS.keys()), help="Metric to compute")
    args = ap.parse_args(argv)

    path = args.file
    if not os.path.isfile(path):
        print(f"[score] File not found: {path}")
        return 2

    rows = load_jsonl(path)
    score, used = score_records(rows, args.pred_field, args.gold_field, args.metric)
    print(f"[score] metric={args.metric} used={used} score={score:.4f}")
    if used == 0:
        print("[score] WARNING: No records contained both pred and gold fields.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

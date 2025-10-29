#!/usr/bin/env python3
"""
Evaluation harness (minimal stub).

- Loads a JSONL dataset of {id, question, answer, ...} items.
- Optionally writes a run file under evals/runs/ for bookkeeping.
- Designed to be extended to call different prompt systems/models.

This stub does not generate predictions; it validates dataset format and
creates a metadata run file recording basic stats to help wire up models.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Iterable, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUNS_DIR = os.path.join(os.path.dirname(__file__), "runs")


def load_jsonl(path: str) -> List[Dict]:
    data: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_jsonl(path: str, rows: Iterable[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Minimal eval harness stub")
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional run name. Defaults to dataset basename + timestamp.",
    )
    args = parser.parse_args(argv)

    dataset_path = args.dataset
    if not os.path.isfile(dataset_path):
        print(f"[harness] Dataset not found: {dataset_path}", file=sys.stderr)
        return 2

    print(f"[harness] Loading dataset: {dataset_path}")
    ds = load_jsonl(dataset_path)
    n = len(ds)
    if n == 0:
        print("[harness] WARNING: dataset is empty")

    # Basic schema check for common fields
    sample_keys = set(ds[0].keys()) if n else set()
    print(f"[harness] Items: {n}; sample keys: {sorted(sample_keys)}")

    # Prepare run metadata
    ensure_dir(RUNS_DIR)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = os.path.splitext(os.path.basename(dataset_path))[0]
    run_name = args.run_name or f"{base}-{stamp}"
    meta = {
        "run_name": run_name,
        "dataset": os.path.relpath(dataset_path, ROOT),
        "created_utc": stamp,
        "count": n,
        "fields": sorted(sample_keys),
        "note": "This is a stub run file. Add predictions by extending the harness.",
    }

    out_jsonl = os.path.join(RUNS_DIR, f"{run_name}.jsonl")
    out_meta = os.path.join(RUNS_DIR, f"{run_name}.meta.json")

    # Write a passthrough of the dataset as the run file for now
    write_jsonl(out_jsonl, ds)
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[harness] Wrote run JSONL: {os.path.relpath(out_jsonl, ROOT)}")
    print(f"[harness] Wrote run META:   {os.path.relpath(out_meta, ROOT)}")
    print("[harness] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

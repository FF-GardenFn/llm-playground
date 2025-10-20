#!/usr/bin/env python3
"""
Chunking utilities for browser research text.

- Sliding window chunking with size≈800 tokens, overlap≈160
- SHA256 hash for dedup/drift detection
- MMR sampler for diversity in retrieval results

Tokens are approximated as whitespace-separated words for portability.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Optional, Dict, Any
import hashlib
import time

from .embeddings import cosine


@dataclass
class Chunk:
    id: str
    charter_id: str
    url: str
    selector: str
    text: str
    tokens: int
    split_algo: str
    last_updated: Optional[str]
    created_at: str
    hash: str
    start_idx: int  # token start index within original
    end_idx: int    # token end index within original (exclusive)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_tokens(text: str) -> List[str]:
    # Cheap tokenization: split on whitespace
    return text.split()


def chunk_text(
    charter_id: str,
    url: str,
    selector: str,
    text: str,
    last_updated: Optional[str] = None,
    size: int = 800,
    overlap: int = 160,
) -> List[Chunk]:
    """Sliding window chunking with overlap. Returns list of Chunk objects.
    Records token offsets to allow snippet reconstruction.
    """
    toks = _split_tokens(text)
    n = len(toks)
    if n == 0:
        return []
    step = max(1, size - overlap)
    chunks: List[Chunk] = []
    algo = f"sliding_{size}_{overlap}"
    created = _now_iso()
    for start in range(0, n, step):
        end = min(n, start + size)
        window_tokens = toks[start:end]
        txt = " ".join(window_tokens)
        h = text_hash(txt)
        cid = h  # deterministic id
        chunks.append(
            Chunk(
                id=cid,
                charter_id=charter_id,
                url=url,
                selector=selector,
                text=txt,
                tokens=len(window_tokens),
                split_algo=algo,
                last_updated=last_updated,
                created_at=created,
                hash=h,
                start_idx=start,
                end_idx=end,
            )
        )
        if end == n:
            break
    return chunks


def mmr_select(
    candidates: Sequence[Tuple[List[float], Dict[str, Any]]],
    query_vec: Sequence[float],
    k: int = 5,
    lambda_mult: float = 0.7,
) -> List[Tuple[List[float], Dict[str, Any]]]:
    """Maximal Marginal Relevance selection for diversity.

    candidates: list of (vec, meta)
    Returns up to k selected items in order.
    """
    if not candidates:
        return []
    selected: List[Tuple[List[float], Dict[str, Any]]] = []
    # Precompute similarity to query for all candidates
    sims_q = [cosine(vec, query_vec) for vec, _ in candidates]
    chosen = [False] * len(candidates)

    for _ in range(min(k, len(candidates))):
        best_idx = -1
        best_score = float("-inf")
        for i, (vec_i, _) in enumerate(candidates):
            if chosen[i]:
                continue
            # Relevance to query
            rel = sims_q[i]
            # Dissimilarity to already selected
            if not selected:
                div_term = 0.0
            else:
                div_term = max(cosine(vec_i, s_vec) for s_vec, _ in selected)
            score = lambda_mult * rel - (1 - lambda_mult) * div_term
            if score > best_score:
                best_score = score
                best_idx = i
        if best_idx == -1:
            break
        chosen[best_idx] = True
        selected.append(candidates[best_idx])
    return selected

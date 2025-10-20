#!/usr/bin/env python3
"""
Local, dependency-free embedding utilities using feature hashing.

This is a deterministic, privacy-first stand-in for small local embedding
models (e.g., bge-m3, gte-large). It produces reasonably useful vectors
for short-to-medium text by hashing tokens into a fixed-dimensional space
and normalizing. Suitable for kNN and centroid ops without external deps.

Note: Replace with a real local model when available; keep the same API.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple
import hashlib
import math
import re

# Default embedding dimension (small to keep memory/CPU low)
EMBED_DIM = 384
TOKEN_RE = re.compile(r"\w+", re.UNICODE)


@dataclass(frozen=True)
class EmbeddingConfig:
    dim: int = EMBED_DIM
    # optional namespace to make vectors across different repos incompatible
    namespace: str = "brt_v1"


def _l2_normalize(vec: List[float]) -> List[float]:
    s = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / s for x in vec]


def _hash_token(tok: str, cfg: EmbeddingConfig) -> Tuple[int, int]:
    """Map token to (index, sign) using SHA256 of namespace+token.
    Returns index in [0, dim) and sign in {+1, -1}.
    """
    h = hashlib.sha256((cfg.namespace + "::" + tok).encode("utf-8")).digest()
    # Use first 4 bytes for index, next byte for sign
    idx = int.from_bytes(h[:4], "big", signed=False) % cfg.dim
    sign = 1 if (h[4] & 1) == 0 else -1
    return idx, sign


def _tokenize(text: str) -> List[str]:
    # Lowercase, simple word tokenizer
    return TOKEN_RE.findall(text.lower())


def embed_one(text: str, cfg: EmbeddingConfig | None = None) -> List[float]:
    """Embed a single string to a fixed-length vector.
    Deterministic and stateless.
    """
    cfg = cfg or EmbeddingConfig()
    vec = [0.0] * cfg.dim
    tokens = _tokenize(text)
    if not tokens:
        return vec
    for t in tokens:
        idx, sign = _hash_token(t, cfg)
        vec[idx] += float(sign)
    return _l2_normalize(vec)


def embed(texts: Iterable[str], cfg: EmbeddingConfig | None = None) -> List[List[float]]:
    """Embed a sequence of strings."""
    cfg = cfg or EmbeddingConfig()
    return [embed_one(t, cfg) for t in texts]


def cosine(u: Sequence[float], v: Sequence[float]) -> float:
    # Inputs are expected L2-normalized; still safe if not.
    num = sum((a * b) for a, b in zip(u, v))
    den_u = math.sqrt(sum(a * a for a in u)) or 1.0
    den_v = math.sqrt(sum(b * b for b in v)) or 1.0
    return num / (den_u * den_v)


def centroid(vectors: Sequence[Sequence[float]]) -> List[float]:
    if not vectors:
        return [0.0] * EMBED_DIM
    dim = len(vectors[0])
    c = [0.0] * dim
    for v in vectors:
        for i, x in enumerate(v):
            c[i] += x
    n = float(len(vectors))
    c = [x / n for x in c]
    return _l2_normalize(c)


def mean_pool(texts: Iterable[str], cfg: EmbeddingConfig | None = None) -> List[float]:
    """Convenience: centroid of embeddings for multiple strings."""
    return centroid(embed(texts, cfg))

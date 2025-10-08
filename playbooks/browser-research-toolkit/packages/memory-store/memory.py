#!/usr/bin/env python3
"""
Memory Store: ephemeral, per-charter kNN evidence cache.

API:
- add(url, text, selector="#", last_updated=None): chunk → embed → upsert
- search(query, k=8, filters=None, subtree=None, filter_allowed=True): kNN (+MMR)
- snapshot(out_path): write JSONL audit of current index
- reset(): wipe current in-memory index

Backend: dependency-free in-memory index with cosine similarity. Can be
swapped for FAISS/Chroma by replacing the _Index class.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from pathlib import Path
import json
import os

from .embeddings import embed, embed_one, cosine
from .chunking import chunk_text, Chunk, mmr_select


@dataclass
class Hit:
    score: float
    text: str
    snippet: str
    metadata: Dict[str, Any]


class _Index:
    """Simple in-memory list-based index. Stores (vec, metadata)."""

    def __init__(self) -> None:
        self._vecs: List[List[float]] = []
        self._meta: List[Dict[str, Any]] = []
        self._by_hash: Dict[str, int] = {}

    def upsert(self, vecs: Sequence[Sequence[float]], metas: Sequence[Dict[str, Any]]) -> None:
        assert len(vecs) == len(metas)
        for v, m in zip(vecs, metas):
            h = m.get("hash")
            if isinstance(h, str) and h in self._by_hash:
                # Deduplicate by content hash: replace metadata, keep vector
                idx = self._by_hash[h]
                self._meta[idx] = dict(m)
                continue
            self._by_hash[h] = len(self._vecs)
            self._vecs.append(list(v))
            self._meta.append(dict(m))

    def knn(self, qvec: Sequence[float], topn: int = 24,
            filters: Optional[Dict[str, Any]] = None) -> List[Tuple[float, Dict[str, Any]]]:
        scores: List[Tuple[float, Dict[str, Any]]] = []
        for v, m in zip(self._vecs, self._meta):
            if filters and not _match_filters(m, filters):
                continue
            s = cosine(qvec, v)
            scores.append((s, m))
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:topn]

    def __len__(self) -> int:
        return len(self._vecs)

    def items(self) -> Iterable[Dict[str, Any]]:
        return list(self._meta)

    def clear(self) -> None:
        self._vecs.clear()
        self._meta.clear()
        self._by_hash.clear()


ALLOWED_FILTER_KEYS = {"url_prefixes", "allowed_domains", "selector", "charter_id"}


def _match_filters(meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    # allowed_domains: list of patterns (simple prefix match, '*' suffix allowed)
    if "allowed_domains" in filters:
        allowed = filters["allowed_domains"] or []
        url = str(meta.get("url", ""))
        ok = False
        for pat in allowed:
            if pat.endswith("*"):
                if url.startswith(pat[:-1]):
                    ok = True
                    break
            else:
                if url.startswith(pat):
                    ok = True
                    break
        if not ok:
            return False
    # selector exact match if provided
    if "selector" in filters and meta.get("selector") != filters.get("selector"):
        return False
    if "charter_id" in filters and meta.get("charter_id") != filters.get("charter_id"):
        return False
    # url_prefixes: legacy key
    if "url_prefixes" in filters:
        prefixes = filters["url_prefixes"] or []
        u = str(meta.get("url", ""))
        if not any(u.startswith(p) for p in prefixes):
            return False
    return True


class Memory:
    def __init__(self, charter_id: str, db_path: str | os.PathLike[str] = "~/.brt/memory",
                 backend: str = "inmem") -> None:
        self.charter_id = charter_id
        self.db_path = Path(os.path.expanduser(str(db_path)))
        self.backend = backend
        self._index = _Index()

    # API: add()
    def add(self, url: str, text: str, selector: str = "#", last_updated: Optional[str] = None) -> List[Chunk]:
        chunks = chunk_text(self.charter_id, url, selector, text, last_updated=last_updated,
                            size=800, overlap=160)
        if not chunks:
            return []
        vecs = embed([c.text for c in chunks])
        metas: List[Dict[str, Any]] = []
        for c in chunks:
            metas.append({
                "id": c.id,
                "charter_id": c.charter_id,
                "url": c.url,
                "selector": c.selector,
                "text": c.text,
                "tokens": c.tokens,
                "split_algo": c.split_algo,
                "last_updated": c.last_updated,
                "created_at": c.created_at,
                "hash": c.hash,
                "start_idx": c.start_idx,
                "end_idx": c.end_idx,
            })
        self._index.upsert(vecs, metas)
        return chunks

    # API: search()
    def search(self, query: str, k: int = 8,
               filters: Optional[Dict[str, Any]] = None,
               filter_allowed: bool = True,
               subtree: Optional[str] = None,
               mmr: bool = True) -> List[Hit]:
        # filters enforcement
        f: Dict[str, Any] = dict(filters or {})
        if filter_allowed:
            f.setdefault("charter_id", self.charter_id)
        # subtree is not implemented in in-memory baseline; reserved for concept index filtering
        qv = embed_one(query)
        top = self._index.knn(qv, topn=24, filters=f)
        if not top:
            return []
        # Build candidate list for MMR
        if mmr:
            candidates = [ (embed_one(m["text"]), m) for _, m in top ]
            sel = mmr_select(candidates, qv, k=k, lambda_mult=0.7)
            picked = [(cosine(qv, v), m) for v, m in sel]
            picked.sort(key=lambda x: x[0], reverse=True)
        else:
            picked = top[:k]
        hits: List[Hit] = []
        for score, meta in picked[:k]:
            text = str(meta.get("text", ""))
            snippet = text[:300] + ("…" if len(text) > 300 else "")
            hits.append(Hit(score=score, text=text, snippet=snippet, metadata=meta))
        return hits

    # API: reset()
    def reset(self) -> None:
        self._index.clear()

    # API: snapshot()
    def snapshot(self, out_path: str | os.PathLike[str]) -> str:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for m in self._index.items():
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        return str(out)

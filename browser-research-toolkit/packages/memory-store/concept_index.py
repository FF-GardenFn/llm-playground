#!/usr/bin/env python3
"""
Concept Index (task-local DAG) — minimal, dependency-free baseline.

Provides:
- ConceptIndex(charter_id)
- insert(label, start_id="root") -> str (returns node id under which to attach)
- compare_generality(a, b) -> {"same_level","more_specific","more_general"}
- is_related(concept, node_label, parent_label=None) -> bool
- handle_promotion(concept, node_id) -> str
- resolve_path(query_label) -> "A > B > C" (best-effort path string)

Heuristics are lightweight: embedding cosine, token-length proxy, and
simple lexical overlap. Designed to be replaced or upgraded.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Sequence, Tuple
import re
import time

from .embeddings import embed_one, centroid, cosine


@dataclass
class Node:
    id: str
    label: str
    parent_id: Optional[str]
    children: List[str] = field(default_factory=list)
    centroid: List[float] = field(default_factory=lambda: [])
    support_docs: int = 0
    summary_50w: str = ""
    status: str = "tentative"  # "tentative" | "stable"


class ConceptIndex:
    def __init__(self, charter_id: str) -> None:
        self.charter_id = charter_id
        self.tree: Dict[str, Node] = {}
        self.events: List[Dict[str, str]] = []
        # root node
        root = Node(id="root", label="root", parent_id=None, centroid=embed_one("root"), status="stable")
        self.tree[root.id] = root

    # Public API -----------------------------------------------------------
    def insert(self, concept: str, start_id: str = "root") -> str:
        start = self.tree[start_id]
        decision = self.compare_generality(concept, start.label)
        if decision == "same_level":
            return start.parent_id or start.id
        if decision == "more_specific":
            # try to descend into children that are related
            for cid in start.children:
                child = self.tree[cid]
                if self.is_related(concept, child.label, parent_label=start.label):
                    return self.insert(concept, cid)
            # attach here
            nid = self._ensure_node(concept, parent_id=start.id)
            return nid
        # more_general → promotion path
        return self.handle_promotion(concept, start.id)

    def compare_generality(self, a: str, b: str) -> str:
        """Return relation of a to b: same_level | more_specific | more_general.
        Cheap heuristics: token length and cosine similarity directional bias.
        """
        # Token length proxy (more tokens → more specific)
        len_a = _specificity_score(a)
        len_b = _specificity_score(b)
        if abs(len_a - len_b) <= 0.15 * max(1.0, len_b):
            # tie — same level
            bias = 0.0
        else:
            bias = 1.0 if len_a > len_b else -1.0

        va = embed_one(a)
        vb = embed_one(b)
        sim = cosine(va, vb)
        # Directional hint: if b appears inside a (or vice versa)
        contains_bias = 0.0
        if _contains(b, a):
            contains_bias += 0.5  # a mentions b → a more specific
        if _contains(a, b):
            contains_bias -= 0.5  # b mentions a → a more general

        score = bias + contains_bias
        if score > 0.15:
            return "more_specific"
        if score < -0.15:
            return "more_general"
        return "same_level"

    def is_related(self, concept: str, node_label: str, parent_label: Optional[str] = None) -> bool:
        v = embed_one(concept)
        cn = embed_one(node_label)
        sim = cosine(v, cn)
        if parent_label:
            cp = embed_one(parent_label)
            sim_p = cosine(v, cp)
        else:
            sim_p = 0.0
        return sim >= max(0.35, sim_p + 0.05)

    def handle_promotion(self, concept: str, node_id: str) -> str:
        """Promote concept above node_id by inserting a new parent node if margin is strong.
        Minimal baseline: always create a new parent if concept is sufficiently different.
        """
        node = self.tree[node_id]
        parent_id = node.parent_id
        # Create new parent node
        new_id = self._ensure_node(concept, parent_id=parent_id)
        # Rewire
        self._adopt_child(new_id, node_id)
        if parent_id is not None:
            self._drop_child(parent_id, node_id)
            self._adopt_child(parent_id, new_id)
        self._event("promotion", frm=node_id, to=new_id, reason="more_general")
        return new_id

    def resolve_path(self, query_label: str) -> str:
        """Best-effort human-readable path for a query: e.g., "Performance > CWV > CLS".
        We find the most similar node and return its ancestry path.
        """
        if not self.tree:
            return "root"
        qv = embed_one(query_label)
        best: Tuple[str, float] = ("root", -1.0)
        for nid, n in self.tree.items():
            sim = cosine(qv, embed_one(n.label))
            if sim > best[1]:
                best = (nid, sim)
        return self._path_str(best[0])

    # Private helpers ------------------------------------------------------
    def _ensure_node(self, label: str, parent_id: Optional[str]) -> str:
        nid = _node_id(label)
        if nid in self.tree:
            # update parent if missing
            if parent_id is not None and self.tree[nid].parent_id is None:
                self.tree[nid].parent_id = parent_id
                if parent_id not in self.tree:
                    self.tree[parent_id] = Node(id=parent_id, label=parent_id, parent_id=None)
                self._adopt_child(parent_id, nid)
            return nid
        node = Node(id=nid, label=label, parent_id=parent_id, centroid=embed_one(label))
        self.tree[nid] = node
        if parent_id is not None:
            self._adopt_child(parent_id, nid)
        self._event("insert", frm="", to=nid, reason="attach")
        return nid

    def _adopt_child(self, parent_id: str, child_id: str) -> None:
        p = self.tree[parent_id]
        if child_id not in p.children:
            p.children.append(child_id)

    def _drop_child(self, parent_id: str, child_id: str) -> None:
        p = self.tree[parent_id]
        if child_id in p.children:
            p.children.remove(child_id)

    def _path_str(self, nid: str) -> str:
        seq: List[str] = []
        cur = nid
        while cur is not None:
            n = self.tree[cur]
            seq.append(n.label)
            cur = n.parent_id
        seq.reverse()
        return " > ".join(seq)

    def _event(self, action: str, frm: str, to: str, reason: str) -> None:
        self.events.append({
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "action": action,
            "from": frm,
            "to": to,
            "reason": reason,
        })


# Utility -----------------------------------------------------------------
_slug_re = re.compile(r"[^a-z0-9]+")


def _node_id(label: str) -> str:
    s = _slug_re.sub("_", label.lower()).strip("_")
    s = s[:48]
    if not s:
        s = "node"
    return f"node_{s}"


def _contains(a: str, b: str) -> bool:
    return _slug_re.sub(" ", a.lower()).find(_slug_re.sub(" ", b.lower())) >= 0


def _specificity_score(text: str) -> float:
    # Simple proxy: word count + number of noun-like tokens (approx via capitalization or 3+ chars)
    toks = re.findall(r"[A-Za-z0-9]+", text)
    word_count = len(toks)
    longer = sum(1 for t in toks if len(t) >= 4)
    return word_count + 0.25 * longer

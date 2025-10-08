"""Smart Memory

Combines semantic search with learned access patterns.
Implements multi-factor scoring with time decay.

Scoring: α*S_sem + β*W_learned + γ*C_concept + δ*R_recency
"""
from __future__ import annotations

import sys
import math
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import os

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'browser-research-toolkit' / 'packages' / 'memory-store'))
from embeddings import embed_one, cosine
from memory import Memory, Hit

from .access_tracker import AccessTracker, Feedback


@dataclass
class ScoringConfig:
    """Scoring coefficients and parameters."""
    alpha: float = 0.6      # Semantic weight
    beta: float = 0.3       # Learned weight
    gamma: float = 0.1      # Concept weight
    delta: float = 0.0      # Recency weight (optional)

    # Learned weight sub-coefficients
    a1: float = 1.0         # Explicit votes (pos - neg)
    a2: float = 0.8         # Dwell time (normalized)
    a3: float = 0.6         # Click rank (inverse)
    a4: float = 0.4         # Transfer from similar queries
    a5: float = 0.5         # Time decay penalty
    a6: float = 0.2         # Cross-workspace transfer

    half_life_days: int = 14  # Half-life for time decay


def sigmoid(x: float) -> float:
    """Sigmoid activation."""
    return 1.0 / (1.0 + math.exp(-max(-10, min(10, x))))


class SmartMemory:
    """Memory with learned ranking and multi-factor scoring.

    Features:
    - Semantic search (BRT Memory)
    - Learned access patterns with time decay
    - Implicit feedback (dwell, click rank)
    - Concept hierarchy boost
    - Recency boost
    """

    def __init__(
        self,
        workspace: str,
        charter_id: Optional[str] = None,
        db_path: str | os.PathLike[str] = "~/.brt/adaptive_memory.db",
        memory_path: str | os.PathLike[str] = "~/.brt/memory",
        config: Optional[ScoringConfig] = None
    ):
        self.workspace = workspace
        self.charter_id = charter_id or workspace
        self.config = config or ScoringConfig()

        # Initialize components
        self.tracker = AccessTracker(db_path=db_path)
        self.memory = Memory(charter_id=self.charter_id, db_path=memory_path)

        # Track item_id -> path mapping
        self._item_map: Dict[str, str] = {}

    def add(
        self,
        file_path: str,
        content: str,
        concept: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a file to memory.

        Returns item_id for feedback tracking
        """
        # Add to tracker (content hash + path)
        item_id = self.tracker.add_item(
            workspace=self.workspace,
            path=file_path,
            content=content,
            concept=concept
        )

        self._item_map[file_path] = item_id

        # Add to BRT memory
        url = f"file://{file_path}"
        last_updated = metadata.get("last_updated") if metadata else None

        self.memory.add(
            url=url,
            text=content,
            selector=file_path,
            last_updated=last_updated
        )

        return item_id

    def query(
        self,
        query: str,
        k: int = 8,
        use_learned: bool = True,
        use_concepts: bool = True,
        use_recency: bool = False,
        explain: bool = False
    ) -> List[Hit | Tuple[Hit, Dict[str, float]]]:
        """Query with multi-factor scoring.

        Args:
            query: Search query
            k: Number of results
            use_learned: Enable learned ranking
            use_concepts: Enable concept boost
            use_recency: Enable recency boost
            explain: Return score breakdown

        Returns:
            List of Hit objects, or (Hit, explanation) tuples if explain=True
        """
        # Log query
        query_emb = embed_one(query)
        qid = self.tracker.log_query(
            workspace=self.workspace,
            query=query,
            embedding=query_emb
        )

        # Get semantic results
        semantic_results = self.memory.search(
            query=query,
            k=k * 3,
            mmr=True
        )

        if not semantic_results:
            return []

        # Get query cluster for learned patterns
        cluster_qids = []
        if use_learned:
            cluster_qids = self.tracker.get_similar_queries(
                workspace=self.workspace,
                query_embedding=query_emb,
                threshold=0.35,
                limit=10
            )
            cluster_qids.append(qid)

        # Score and rank
        now_ms = int(time.time() * 1000)
        scored_results = []

        for hit in semantic_results:
            file_path = hit.metadata.get("selector", "")
            item_id = self._item_map.get(file_path)

            # Compute score factors
            s_sem = hit.score  # Already normalized from BRT

            w_learned = 0.0
            if use_learned and item_id and cluster_qids:
                w_learned = self._learned_weight(item_id, cluster_qids, now_ms)

            c_concept = 0.0  # Placeholder (TODO: implement concept similarity)

            r_recency = 0.0  # Placeholder (TODO: implement recency boost)

            # Combined score
            total_score = (
                self.config.alpha * s_sem +
                self.config.beta * w_learned +
                self.config.gamma * c_concept +
                self.config.delta * r_recency
            )

            # Create scored hit
            scored_hit = Hit(
                score=total_score,
                text=hit.text,
                snippet=hit.snippet,
                metadata=hit.metadata
            )

            if explain:
                explanation = {
                    "S_sem": round(s_sem, 3),
                    "W_learned": round(w_learned, 3),
                    "C_concept": round(c_concept, 3),
                    "R_recency": round(r_recency, 3),
                    "total": round(total_score, 3)
                }
                scored_results.append((scored_hit, explanation))
            else:
                scored_results.append(scored_hit)

        # Sort by total score
        if explain:
            scored_results.sort(key=lambda x: x[0].score, reverse=True)
        else:
            scored_results.sort(key=lambda x: x.score, reverse=True)

        return scored_results[:k]

    def _learned_weight(
        self,
        item_id: str,
        cluster_qids: List[str],
        now_ms: int
    ) -> float:
        """Compute learned weight using sigmoid activation.

        W_learned = sigmoid(
            a1 * (pos - neg) +
            a2 * zscore(dwell) +
            a3 * (1 / mean_rank) +
            a4 * transfer -
            a5 * (1 - decay)
        )
        """
        interactions = self.tracker.get_item_interactions(
            item_id=item_id,
            cluster_qids=cluster_qids
        )

        if not interactions:
            return 0.0

        # Extract signals
        pos_cnt = sum(1 for u, _, _, _ in interactions if u == 1)
        neg_cnt = sum(1 for u, _, _, _ in interactions if u == -1)

        dwells = [d for _, d, _, _ in interactions if d and d > 0]
        mean_dwell = (sum(dwells) / len(dwells)) if dwells else 0.0

        ranks = [r for _, _, r, _ in interactions if r and r > 0]
        mean_rank = (sum(ranks) / len(ranks)) if ranks else 999.0

        # Time decay (half-life)
        half_life_ms = self.config.half_life_days * 86400 * 1000
        decays = [
            2 ** (-max(0, now_ms - ts) / half_life_ms)
            for _, _, _, ts in interactions
        ]
        avg_decay = sum(decays) / len(decays) if decays else 0.0

        # Compute components
        votes_term = self.config.a1 * (pos_cnt - neg_cnt)
        dwell_term = self.config.a2 * (mean_dwell / 1000.0)  # Normalize ms to seconds
        rank_term = self.config.a3 * (1.0 / max(1.0, mean_rank))
        transfer_term = 0.0  # TODO: implement cross-query transfer
        decay_term = self.config.a5 * (1.0 - avg_decay)

        x = votes_term + dwell_term + rank_term + transfer_term - decay_term

        return sigmoid(x)

    def log_feedback(
        self,
        query: str,
        file_path: str,
        useful: int,
        dwell_ms: int = 0,
        click_rank: int = 0
    ) -> None:
        """Log feedback with explicit and implicit signals.

        Args:
            query: Query string
            file_path: File that was accessed
            useful: +1 (useful), 0 (neutral), -1 (not useful)
            dwell_ms: Time spent on item (milliseconds)
            click_rank: 1-based rank when clicked
        """
        # Get query ID
        query_emb = embed_one(query)
        qid = self.tracker.log_query(
            workspace=self.workspace,
            query=query,
            embedding=query_emb
        )

        # Get item ID
        item_id = self._item_map.get(file_path)
        if not item_id:
            return

        # Log interaction
        feedback = Feedback(
            useful=useful,
            dwell_ms=dwell_ms,
            click_rank=click_rank
        )

        self.tracker.log_interaction(qid, item_id, feedback)

    def get_stats(self) -> Dict[str, Any]:
        """Get workspace statistics."""
        return self.tracker.get_workspace_stats(self.workspace)

    def close(self) -> None:
        """Close connections."""
        self.tracker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

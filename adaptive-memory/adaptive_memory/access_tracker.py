"""Access Pattern Tracker

Logs query interactions with implicit and explicit feedback.
Schema: items, queries, interactions, workspaces
"""
from __future__ import annotations

import sqlite3
import hashlib
import time
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import os
import json


@dataclass
class Feedback:
    """User feedback for an interaction."""
    useful: int          # +1 (explicit useful), 0 (unknown), -1 (explicit not useful)
    dwell_ms: int = 0    # time spent viewing/using the item
    click_rank: int = 0  # 1-based rank when clicked


def content_hash(text: str) -> str:
    """Generate content hash for deduplication and rename tracking."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]


class AccessTracker:
    """Track query interactions and access patterns.

    Features:
    - Explicit feedback (useful/not useful)
    - Implicit feedback (dwell time, click rank)
    - Content-based deduplication (handles renames)
    - Time-aware decay support
    """

    def __init__(self, db_path: str | os.PathLike[str] = "~/.brt/access_patterns.db"):
        db_path = Path(db_path).expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    def _init_schema(self):
        """Create tables with improved schema."""

        # Items table (keyed by content hash + path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                workspace TEXT NOT NULL,
                item_id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                concept TEXT,
                created_ts INTEGER NOT NULL
            )
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_workspace
            ON items(workspace, content_hash)
        """)

        # Queries table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                qid TEXT PRIMARY KEY,
                workspace TEXT NOT NULL,
                query TEXT NOT NULL,
                issued_ts INTEGER NOT NULL,
                qhash TEXT NOT NULL,
                qembedding TEXT
            )
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_queries_workspace
            ON queries(workspace, qhash)
        """)

        # Interactions table (explicit + implicit feedback)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qid TEXT NOT NULL,
                item_id TEXT NOT NULL,
                useful INTEGER NOT NULL,
                dwell_ms INTEGER,
                click_rank INTEGER,
                ts INTEGER NOT NULL,
                FOREIGN KEY(qid) REFERENCES queries(qid),
                FOREIGN KEY(item_id) REFERENCES items(item_id)
            )
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_item
            ON interactions(item_id, ts)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_qid
            ON interactions(qid, ts)
        """)

        # Workspaces table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                name TEXT PRIMARY KEY,
                created_ts INTEGER NOT NULL
            )
        """)

        self.conn.commit()

    def ensure_workspace(self, workspace: str) -> None:
        """Ensure workspace exists."""
        self.conn.execute("""
            INSERT OR IGNORE INTO workspaces (name, created_ts)
            VALUES (?, ?)
        """, (workspace, int(time.time() * 1000)))
        self.conn.commit()

    def add_item(
        self,
        workspace: str,
        path: str,
        content: str,
        concept: Optional[str] = None
    ) -> str:
        """Add or update an item.

        Returns item_id (content_hash + path suffix for uniqueness)
        """
        self.ensure_workspace(workspace)

        chash = content_hash(content)
        item_id = f"{chash}:{path}"

        self.conn.execute("""
            INSERT OR REPLACE INTO items
            (workspace, item_id, path, content_hash, concept, created_ts)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (workspace, item_id, path, chash, concept, int(time.time() * 1000)))

        self.conn.commit()
        return item_id

    def log_query(
        self,
        workspace: str,
        query: str,
        embedding: Optional[List[float]] = None
    ) -> str:
        """Log a query and return query ID."""
        self.ensure_workspace(workspace)

        qhash = hashlib.sha256(query.lower().encode()).hexdigest()[:16]
        qid = f"{workspace}:{qhash}:{int(time.time() * 1000)}"

        emb_json = json.dumps(embedding) if embedding else None

        self.conn.execute("""
            INSERT OR REPLACE INTO queries
            (qid, workspace, query, issued_ts, qhash, qembedding)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (qid, workspace, query, int(time.time() * 1000), qhash, emb_json))

        self.conn.commit()
        return qid

    def log_interaction(
        self,
        qid: str,
        item_id: str,
        feedback: Feedback
    ) -> None:
        """Log an interaction with explicit or implicit feedback."""
        self.conn.execute("""
            INSERT INTO interactions
            (qid, item_id, useful, dwell_ms, click_rank, ts)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            qid,
            item_id,
            feedback.useful,
            feedback.dwell_ms,
            feedback.click_rank,
            int(time.time() * 1000)
        ))

        self.conn.commit()

    def get_item_interactions(
        self,
        item_id: str,
        cluster_qids: Optional[List[str]] = None,
        since_ts: Optional[int] = None
    ) -> List[tuple]:
        """Get interactions for an item, optionally filtered by query cluster and time.

        Returns: List of (useful, dwell_ms, click_rank, ts) tuples
        """
        if cluster_qids:
            placeholders = ','.join('?' * len(cluster_qids))
            query = f"""
                SELECT useful, dwell_ms, click_rank, ts
                FROM interactions
                WHERE item_id = ? AND qid IN ({placeholders})
            """
            params = [item_id] + cluster_qids
        else:
            query = """
                SELECT useful, dwell_ms, click_rank, ts
                FROM interactions
                WHERE item_id = ?
            """
            params = [item_id]

        if since_ts:
            query += " AND ts >= ?"
            params.append(since_ts)

        return self.conn.execute(query, params).fetchall()

    def get_similar_queries(
        self,
        workspace: str,
        query_embedding: List[float],
        threshold: float = 0.35,
        limit: int = 10
    ) -> List[str]:
        """Find similar queries by embedding cosine similarity.

        Returns list of qids for query cluster.
        """
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'browser-research-toolkit' / 'packages' / 'memory-store'))
        from embeddings import cosine

        rows = self.conn.execute("""
            SELECT qid, qembedding
            FROM queries
            WHERE workspace = ? AND qembedding IS NOT NULL
        """, (workspace,)).fetchall()

        similar = []
        for qid, emb_json in rows:
            if not emb_json:
                continue

            other_emb = json.loads(emb_json)
            sim = cosine(query_embedding, other_emb)

            if sim >= threshold:
                similar.append((sim, qid))

        similar.sort(reverse=True, key=lambda x: x[0])
        return [qid for _, qid in similar[:limit]]

    def get_workspace_stats(self, workspace: str) -> Dict[str, Any]:
        """Get statistics for a workspace."""
        stats = {}

        # Query counts
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM queries WHERE workspace = ?
        """, (workspace,))
        stats['total_queries'] = cursor.fetchone()[0]

        # Interaction counts
        cursor = self.conn.execute("""
            SELECT COUNT(*), AVG(useful), AVG(dwell_ms), AVG(click_rank)
            FROM interactions i
            JOIN queries q ON i.qid = q.qid
            WHERE q.workspace = ?
        """, (workspace,))

        row = cursor.fetchone()
        stats['total_interactions'] = row[0] or 0
        stats['avg_useful'] = round(row[1] or 0, 2)
        stats['avg_dwell_ms'] = round(row[2] or 0, 0)
        stats['avg_click_rank'] = round(row[3] or 0, 1)

        # Item counts
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM items WHERE workspace = ?
        """, (workspace,))
        stats['total_items'] = cursor.fetchone()[0]

        # Last activity
        cursor = self.conn.execute("""
            SELECT MAX(issued_ts) FROM queries WHERE workspace = ?
        """, (workspace,))
        last_ts = cursor.fetchone()[0]
        stats['last_activity_ts'] = last_ts

        return stats

    def list_workspaces(self) -> List[str]:
        """List all workspaces."""
        cursor = self.conn.execute("SELECT name FROM workspaces ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

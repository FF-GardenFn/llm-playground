"""Concept Memory - Day 3

Adds hierarchical concept organization to SmartMemory.
Queries and files are organized into a semantic tree.

Example:
    memory = ConceptualMemory(workspace="myapp")

    # Add files with automatic concept extraction
    memory.add("middleware/auth.py", content, concepts=["Authentication", "JWT"])

    # Query with concept navigation
    results = memory.query("JWT validation")
    # Knows: JWT > Validation sits under Authentication hierarchy

    # Navigate by concept
    path = memory.get_concept_path("JWT tokens")
    # Returns: "Authentication > JWT > Tokens"
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
import os

from brt_core.concept_index import ConceptIndex
from .smart_memory import AdaptiveMemory
from brt_core.memory import Hit


class ConceptualMemory:
    """Memory with hierarchical concept organization.

    Combines:
    - SmartMemory: learned ranking from access patterns
    - ConceptIndex: hierarchical concept tree
    """

    def __init__(
        self,
        workspace: str,
        charter_id: Optional[str] = None,
        db_path: str | os.PathLike[str] = "~/.brt/adaptive_memory.db",
        memory_path: str | os.PathLike[str] = "~/.brt/memory"
    ):
        """Initialize conceptual memory.

        Args:
            workspace: Workspace identifier
            charter_id: Charter ID (defaults to workspace)
            db_path: Path to access tracking database
            memory_path: Path to memory storage
        """
        self.workspace = workspace
        self.charter_id = charter_id or workspace

        # Initialize components
        self.adaptive_memory = AdaptiveMemory(
            workspace=workspace,
            charter_id=self.charter_id,
            db_path=db_path,
            memory_path=memory_path
        )
        self.concept_index = ConceptIndex(charter_id=self.charter_id)

        # Track file -> concepts mapping
        self._file_concepts: Dict[str, List[str]] = {}

    def add(
        self,
        file_path: str,
        content: str,
        concepts: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a file to memory with concept tagging.

        Args:
            file_path: Path to file
            content: File content
            concepts: List of concepts this file relates to
            metadata: Optional metadata
        """
        # Add to adaptive memory (semantic + learned)
        self.adaptive_memory.add(file_path, content, metadata)

        # Build concept hierarchy
        if concepts:
            self._file_concepts[file_path] = concepts
            for concept in concepts:
                # Insert each concept into hierarchy
                # ConceptIndex will automatically organize them hierarchically
                self.concept_index.insert(concept)

    def query(
        self,
        query: str,
        k: int = 8,
        use_learned: bool = True,
        use_concepts: bool = True,
        learned_boost: float = 0.3,
        concept_boost: float = 0.2
    ) -> List[Hit]:
        """Query with concept-aware ranking.

        Args:
            query: Search query
            k: Number of results
            use_learned: Use learned access patterns
            use_concepts: Use concept hierarchy for boosting
            learned_boost: Boost for learned files
            concept_boost: Boost for concept-matched files

        Returns:
            List of hits ranked by combined score
        """
        # Get base results from adaptive memory
        results = self.adaptive_memory.query(
            query=query,
            k=k * 2,  # Get more for concept re-ranking
            use_learned=use_learned,
            learned_boost=learned_boost
        )

        if not results or not use_concepts:
            return results[:k]

        # Find query's concept path
        query_path = self.concept_index.resolve_path(query)
        query_concepts = set(query_path.split(" > "))

        # Re-rank with concept boost
        reranked = []
        for hit in results:
            file_path = hit.metadata.get("selector", "")
            score = hit.score

            # Boost files that share concepts with query
            if file_path in self._file_concepts:
                file_concepts = set(self._file_concepts[file_path])
                overlap = len(query_concepts & file_concepts)
                if overlap > 0:
                    # Boost proportional to concept overlap
                    score = score * (1.0 + concept_boost * overlap / len(query_concepts))

            reranked.append(Hit(
                score=score,
                text=hit.text,
                snippet=hit.snippet,
                metadata=hit.metadata
            ))

        # Sort by adjusted score
        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked[:k]

    def get_concept_path(self, query: str) -> str:
        """Get the hierarchical concept path for a query.

        Args:
            query: Query or concept

        Returns:
            Path string like "A > B > C"
        """
        return self.concept_index.resolve_path(query)

    def get_concept_tree(self) -> Dict[str, Any]:
        """Get the full concept tree as nested dict.

        Returns:
            Tree structure with nodes and children
        """
        def build_subtree(node_id: str) -> Dict[str, Any]:
            node = self.concept_index.tree[node_id]
            return {
                "id": node.id,
                "label": node.label,
                "support_docs": node.support_docs,
                "children": [build_subtree(cid) for cid in node.children]
            }

        return build_subtree("root")

    def get_related_concepts(self, concept: str, threshold: float = 0.35) -> List[str]:
        """Find concepts related to the given concept.

        Args:
            concept: Concept to find relations for
            threshold: Similarity threshold

        Returns:
            List of related concept labels
        """
        related = []
        for node_id, node in self.concept_index.tree.items():
            if node.label == "root":
                continue
            if self.concept_index.is_related(concept, node.label):
                related.append(node.label)
        return related

    def log_feedback(self, query: str, file_path: str, useful: bool) -> None:
        """Log feedback (delegates to adaptive memory).

        Args:
            query: Search query
            file_path: File that was accessed
            useful: Whether it was useful
        """
        self.adaptive_memory.log_feedback(query, file_path, useful)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about memory and concepts.

        Returns:
            Dict with memory stats + concept stats
        """
        memory_stats = self.adaptive_memory.get_stats()
        concept_stats = {
            "total_concepts": len(self.concept_index.tree) - 1,  # Exclude root
            "concept_tree_depth": self._tree_depth(),
            "files_with_concepts": len(self._file_concepts)
        }

        return {
            **memory_stats,
            **concept_stats
        }

    def _tree_depth(self) -> int:
        """Calculate maximum depth of concept tree."""
        def depth(node_id: str) -> int:
            node = self.concept_index.tree[node_id]
            if not node.children:
                return 0
            return 1 + max(depth(cid) for cid in node.children)

        return depth("root")

    def reset_memory(self) -> None:
        """Clear memory (keeps concepts and learned patterns)."""
        self.adaptive_memory.reset_memory()

    def close(self) -> None:
        """Close database connections."""
        self.adaptive_memory.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Demo usage
    print("=== ConceptualMemory Demo ===\n")

    memory = ConceptualMemory(workspace="demo_project", db_path="/tmp/demo_concept.db")

    # Add files with concept tags
    print("Adding files with concepts...")
    memory.add(
        "middleware/auth.py",
        """
        def authenticate(request):
            token = request.headers.get('Authorization')
            return verify_jwt(token)

        def verify_jwt(token):
            return decode_token(token)
        """,
        concepts=["Authentication", "JWT", "Middleware"]
    )

    memory.add(
        "middleware/session.py",
        """
        def create_session(user_id):
            session_id = generate_session_id()
            store_session(session_id, user_id)
            return session_id
        """,
        concepts=["Authentication", "Session Management", "Middleware"]
    )

    memory.add(
        "models/user.py",
        """
        class User:
            def __init__(self, id, email):
                self.id = id
                self.email = email
        """,
        concepts=["Models", "User Management"]
    )

    print("✅ Added 3 files with concepts\n")

    # Show concept tree
    print("=== Concept Hierarchy ===")
    path = memory.get_concept_path("JWT validation")
    print(f"Query 'JWT validation' → Path: {path}\n")

    # Query with concept awareness
    print("=== Concept-Aware Query ===")
    results = memory.query("JWT tokens", k=3, use_concepts=True)
    print(f"Query: 'JWT tokens'")
    print(f"Results ({len(results)}):")
    for i, hit in enumerate(results, 1):
        file_path = hit.metadata.get("selector", "unknown")
        print(f"  {i}. {file_path} (score: {hit.score:.3f})")
    print("  → Files with JWT concept are boosted!\n")

    # Find related concepts
    print("=== Related Concepts ===")
    related = memory.get_related_concepts("JWT")
    print(f"Concepts related to 'JWT': {related[:5]}\n")

    # Stats
    stats = memory.get_stats()
    print(f"Stats:")
    print(f"  - Total concepts: {stats['total_concepts']}")
    print(f"  - Tree depth: {stats['concept_tree_depth']}")
    print(f"  - Files with concepts: {stats['files_with_concepts']}\n")

    memory.close()
    print("✅ Demo complete")

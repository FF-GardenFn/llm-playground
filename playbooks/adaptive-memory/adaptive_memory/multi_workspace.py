"""Multi-Workspace Memory - Day 4

Manages multiple workspaces (codebases) with separate learned patterns.
Allows cross-workspace concept sharing and unified querying.

Example:
    manager = MultiWorkspaceMemory()

    # Add files to different workspaces
    manager.add_file("backend-api", "auth/jwt.py", content)
    manager.add_file("frontend-app", "components/Login.tsx", content)

    # Query specific workspace
    results = manager.query("authentication", workspace="backend-api")

    # Query across all workspaces
    results = manager.query_all("JWT tokens")

    # Compare workspaces
    comparison = manager.compare_workspaces(["backend-api", "frontend-app"])
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any, Set
from pathlib import Path
import os

from .concept_memory import ConceptualMemory
from brt_core.memory import Hit
from brt_core.concept_index import ConceptIndex


class MultiWorkspaceMemory:
    """Manage multiple workspaces with separate learned patterns.

    Each workspace has its own:
    - Access pattern learning (separate per workspace)
    - Semantic memory (separate per workspace)

    Shared across workspaces:
    - Concept hierarchy (optional)
    """

    def __init__(
        self,
        shared_concepts: bool = True,
        db_path: str | os.PathLike[str] = "~/.brt/multi_workspace.db",
        memory_root: str | os.PathLike[str] = "~/.brt/workspaces"
    ):
        """Initialize multi-workspace manager.

        Args:
            shared_concepts: Share concept hierarchy across workspaces
            db_path: Path to shared database
            memory_root: Root directory for workspace-specific data
        """
        self.shared_concepts = shared_concepts
        self.db_path = Path(db_path).expanduser()
        self.memory_root = Path(memory_root).expanduser()
        self.memory_root.mkdir(parents=True, exist_ok=True)

        # Workspace registry
        self._workspaces: Dict[str, ConceptualMemory] = {}

        # Shared concept index (if enabled)
        self._shared_concepts_index: Optional[ConceptIndex] = None
        if shared_concepts:
            self._shared_concepts_index = ConceptIndex(charter_id="shared")

    def add_workspace(self, workspace: str) -> ConceptualMemory:
        """Create or get a workspace.

        Args:
            workspace: Workspace identifier

        Returns:
            ConceptualMemory instance for this workspace
        """
        if workspace in self._workspaces:
            return self._workspaces[workspace]

        # Create workspace-specific paths
        workspace_path = self.memory_root / workspace
        workspace_path.mkdir(parents=True, exist_ok=True)

        memory = ConceptualMemory(
            workspace=workspace,
            db_path=self.db_path,  # Shared DB (access patterns partitioned by workspace)
            memory_path=workspace_path / "memory"
        )

        self._workspaces[workspace] = memory
        return memory

    def get_workspace(self, workspace: str) -> Optional[ConceptualMemory]:
        """Get existing workspace or None.

        Args:
            workspace: Workspace identifier

        Returns:
            ConceptualMemory instance or None
        """
        return self._workspaces.get(workspace)

    def list_workspaces(self) -> List[str]:
        """Get list of all workspace names.

        Returns:
            List of workspace identifiers
        """
        return list(self._workspaces.keys())

    def add_file(
        self,
        workspace: str,
        file_path: str,
        content: str,
        concepts: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a file to a specific workspace.

        Args:
            workspace: Workspace identifier
            file_path: Path to file
            content: File content
            concepts: Concepts associated with this file
            metadata: Optional metadata
        """
        memory = self.add_workspace(workspace)
        memory.add(file_path, content, concepts, metadata)

        # Update shared concept index
        if self.shared_concepts and concepts and self._shared_concepts_index:
            for concept in concepts:
                self._shared_concepts_index.insert(concept)

    def query(
        self,
        query: str,
        workspace: str,
        k: int = 8,
        use_learned: bool = True,
        use_concepts: bool = True
    ) -> List[Hit]:
        """Query a specific workspace.

        Args:
            query: Search query
            workspace: Workspace to query
            k: Number of results
            use_learned: Use learned patterns
            use_concepts: Use concept hierarchy

        Returns:
            List of hits from this workspace
        """
        memory = self.get_workspace(workspace)
        if not memory:
            return []

        return memory.query(
            query=query,
            k=k,
            use_learned=use_learned,
            use_concepts=use_concepts
        )

    def query_all(
        self,
        query: str,
        k: int = 8,
        use_learned: bool = True,
        use_concepts: bool = True,
        workspaces: Optional[List[str]] = None
    ) -> Dict[str, List[Hit]]:
        """Query across multiple workspaces.

        Args:
            query: Search query
            k: Number of results per workspace
            use_learned: Use learned patterns
            use_concepts: Use concept hierarchy
            workspaces: Specific workspaces to query (None = all)

        Returns:
            Dict mapping workspace -> results
        """
        target_workspaces = workspaces or self.list_workspaces()
        results = {}

        for ws in target_workspaces:
            hits = self.query(
                query=query,
                workspace=ws,
                k=k,
                use_learned=use_learned,
                use_concepts=use_concepts
            )
            if hits:
                results[ws] = hits

        return results

    def query_merged(
        self,
        query: str,
        k: int = 8,
        use_learned: bool = True,
        use_concepts: bool = True,
        workspaces: Optional[List[str]] = None
    ) -> List[tuple[str, Hit]]:
        """Query across workspaces and merge results.

        Args:
            query: Search query
            k: Total number of results
            use_learned: Use learned patterns
            use_concepts: Use concept hierarchy
            workspaces: Specific workspaces (None = all)

        Returns:
            List of (workspace, hit) tuples sorted by score
        """
        all_results = self.query_all(
            query=query,
            k=k * 2,  # Get more per workspace for merging
            use_learned=use_learned,
            use_concepts=use_concepts,
            workspaces=workspaces
        )

        # Merge and sort by score
        merged = []
        for ws, hits in all_results.items():
            for hit in hits:
                merged.append((ws, hit))

        merged.sort(key=lambda x: x[1].score, reverse=True)
        return merged[:k]

    def get_shared_concept_path(self, query: str) -> Optional[str]:
        """Get concept path from shared concept index.

        Args:
            query: Query or concept

        Returns:
            Path string or None if shared concepts disabled
        """
        if not self._shared_concepts_index:
            return None
        return self._shared_concepts_index.resolve_path(query)

    def compare_workspaces(self, workspaces: List[str]) -> Dict[str, Any]:
        """Compare statistics across workspaces.

        Args:
            workspaces: List of workspace identifiers

        Returns:
            Comparison dict with stats per workspace
        """
        comparison = {}

        for ws in workspaces:
            memory = self.get_workspace(ws)
            if memory:
                comparison[ws] = memory.get_stats()

        return comparison

    def get_workspace_concepts(self, workspace: str) -> Set[str]:
        """Get all concepts used in a workspace.

        Args:
            workspace: Workspace identifier

        Returns:
            Set of concept labels
        """
        memory = self.get_workspace(workspace)
        if not memory:
            return set()

        concepts = set()
        for node_id, node in memory.concept_index.tree.items():
            if node.label != "root":
                concepts.add(node.label)

        return concepts

    def find_shared_concepts(self, workspaces: List[str]) -> Set[str]:
        """Find concepts that appear in multiple workspaces.

        Args:
            workspaces: List of workspace identifiers

        Returns:
            Set of concepts appearing in 2+ workspaces
        """
        all_concepts = [self.get_workspace_concepts(ws) for ws in workspaces]

        # Find intersection
        if not all_concepts:
            return set()

        shared = all_concepts[0]
        for concepts in all_concepts[1:]:
            shared = shared & concepts

        return shared

    def log_feedback(self, workspace: str, query: str, file_path: str, useful: bool) -> None:
        """Log feedback for a specific workspace.

        Args:
            workspace: Workspace identifier
            query: Search query
            file_path: File that was accessed
            useful: Whether it was useful
        """
        memory = self.get_workspace(workspace)
        if memory:
            memory.log_feedback(query, file_path, useful)

    def close_all(self) -> None:
        """Close all workspace connections."""
        for memory in self._workspaces.values():
            memory.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()


if __name__ == "__main__":
    # Demo usage
    print("=== MultiWorkspaceMemory Demo ===\n")

    manager = MultiWorkspaceMemory(
        shared_concepts=True,
        db_path="/tmp/demo_multi.db",
        memory_root="/tmp/demo_workspaces"
    )

    # Add files to different workspaces
    print("Adding files to different workspaces...\n")

    # Backend API workspace
    manager.add_file(
        "backend-api",
        "auth/jwt.py",
        """
        def create_jwt(user_id):
            payload = {'user_id': user_id}
            return encode_token(payload)

        def verify_jwt(token):
            return decode_token(token)
        """,
        concepts=["Authentication", "JWT", "Backend"]
    )

    manager.add_file(
        "backend-api",
        "auth/session.py",
        """
        def create_session(user_id):
            session_id = generate_id()
            store_session(session_id, user_id)
            return session_id
        """,
        concepts=["Authentication", "Session", "Backend"]
    )

    # Frontend app workspace
    manager.add_file(
        "frontend-app",
        "components/Login.tsx",
        """
        function Login() {
            const handleLogin = async (credentials) => {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    body: JSON.stringify(credentials)
                });
                const { token } = await response.json();
                localStorage.setItem('jwt', token);
            };
        }
        """,
        concepts=["Authentication", "JWT", "Frontend", "React"]
    )

    print("✅ Added files to 2 workspaces\n")

    # List workspaces
    print(f"Workspaces: {manager.list_workspaces()}\n")

    # Query specific workspace
    print("=== Query Specific Workspace ===")
    results = manager.query("JWT tokens", workspace="backend-api", k=3)
    print(f"Query 'JWT tokens' in backend-api:")
    for i, hit in enumerate(results, 1):
        file_path = hit.metadata.get("selector", "unknown")
        print(f"  {i}. {file_path} (score: {hit.score:.3f})")
    print()

    # Query all workspaces
    print("=== Query All Workspaces ===")
    all_results = manager.query_all("authentication", k=2)
    print(f"Query 'authentication' across all workspaces:")
    for ws, hits in all_results.items():
        print(f"  {ws}:")
        for hit in hits:
            file_path = hit.metadata.get("selector", "unknown")
            print(f"    - {file_path} (score: {hit.score:.3f})")
    print()

    # Query merged
    print("=== Merged Query ===")
    merged = manager.query_merged("JWT", k=5)
    print(f"Query 'JWT' merged across workspaces:")
    for ws, hit in merged:
        file_path = hit.metadata.get("selector", "unknown")
        print(f"  [{ws}] {file_path} (score: {hit.score:.3f})")
    print()

    # Shared concepts
    print("=== Shared Concepts ===")
    shared = manager.find_shared_concepts(["backend-api", "frontend-app"])
    print(f"Concepts shared between workspaces: {shared}\n")

    # Shared concept path
    path = manager.get_shared_concept_path("JWT validation")
    print(f"Shared concept path for 'JWT validation': {path}\n")

    # Compare workspaces
    print("=== Workspace Comparison ===")
    comparison = manager.compare_workspaces(["backend-api", "frontend-app"])
    for ws, stats in comparison.items():
        print(f"{ws}:")
        print(f"  - Total concepts: {stats.get('total_concepts', 0)}")
        print(f"  - Files: {stats.get('files_with_concepts', 0)}")
    print()

    manager.close_all()
    print("✅ Demo complete")

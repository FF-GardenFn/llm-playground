#!/usr/bin/env python3
"""
merge_coordinator.py - Merge .ctxpack semantic graphs with conflict detection

Usage:
    python merge_coordinator.py --agents <agent1> <agent2> --output <merged.ctxpack>
    python merge_coordinator.py --agents <agent1> <agent2> --strategy priority --priorities agent1:1,agent2:2
    python merge_coordinator.py --agents <agent1> <agent2> --validate-only
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class MergeConflict(Exception):
    """Exception raised when merge conflicts are detected"""
    def __init__(self, conflicts: List[Dict]):
        self.conflicts = conflicts
        super().__init__(f"Merge conflicts detected: {len(conflicts)}")


class GraphValidationError(Exception):
    """Exception raised when graph validation fails"""
    pass


class MergeCoordinator:
    """Coordinate semantic graph merging with conflict detection"""

    VALID_NODE_TYPES = ["module", "class", "function", "variable", "test", "dependency", "config"]
    VALID_EDGE_TYPES = ["contains", "calls", "imports", "inherits", "depends_on", "tests"]

    def __init__(self, strategy: str = "priority", priorities: Optional[Dict[str, int]] = None):
        self.strategy = strategy
        self.priorities = priorities or {}
        self.conflicts = []

    def load_graph(self, agent_name: str, workspace_base: str = "/tmp/agent-workspaces") -> Dict:
        """Load .ctxpack graph from agent workspace"""
        graph_path = Path(workspace_base) / agent_name / ".ctxpack"

        if not graph_path.exists():
            raise FileNotFoundError(f"No .ctxpack found for agent: {agent_name}")

        with open(graph_path, 'r') as f:
            graph = json.load(f)

        # Ensure metadata exists
        if "metadata" not in graph:
            graph["metadata"] = {}

        graph["metadata"]["agent"] = agent_name

        return graph

    def validate_node_types(self, nodes: List[Dict]) -> None:
        """Validate all nodes have valid types"""
        errors = []

        for node in nodes:
            if "type" not in node:
                errors.append(f"Node {node.get('id', 'unknown')} missing type")
            elif node["type"] not in self.VALID_NODE_TYPES:
                errors.append(f"Node {node['id']} has invalid type: {node['type']}")

        if errors:
            raise GraphValidationError(f"Node type validation failed:\n" + "\n".join(errors))

    def validate_edge_types(self, edges: List[Dict]) -> None:
        """Validate all edges have valid types"""
        errors = []

        for edge in edges:
            if "type" not in edge:
                errors.append(f"Edge {edge.get('source', '?')}→{edge.get('target', '?')} missing type")
            elif edge["type"] not in self.VALID_EDGE_TYPES:
                errors.append(f"Edge has invalid type: {edge['type']}")

        if errors:
            raise GraphValidationError(f"Edge type validation failed:\n" + "\n".join(errors))

    def validate_references(self, nodes: List[Dict], edges: List[Dict]) -> None:
        """Validate all edge references point to existing nodes"""
        node_ids = {node["id"] for node in nodes}
        errors = []

        for edge in edges:
            if edge["source"] not in node_ids:
                errors.append(f"Edge references non-existent source: {edge['source']}")

            if edge["target"] not in node_ids:
                errors.append(f"Edge references non-existent target: {edge['target']}")

        if errors:
            raise GraphValidationError(f"Reference validation failed:\n" + "\n".join(errors))

    def is_acyclic(self, nodes: List[Dict], edges: List[Dict]) -> bool:
        """Check if directed graph is acyclic (DAG)"""
        # Build adjacency list
        graph = {node["id"]: [] for node in nodes}
        for edge in edges:
            if edge["source"] in graph:
                graph[edge["source"]].append(edge["target"])

        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in graph:
            if node_id not in visited:
                if has_cycle(node_id):
                    return False

        return True

    def detect_conflicts(self, graphs: List[Dict]) -> List[Dict]:
        """Detect attribute conflicts across graphs"""
        conflicts = []

        # Index nodes by ID
        nodes_by_id: Dict[str, List[Tuple[str, Dict]]] = {}

        for graph in graphs:
            agent = graph["metadata"].get("agent", "unknown")
            for node in graph["nodes"]:
                node_id = node["id"]
                if node_id not in nodes_by_id:
                    nodes_by_id[node_id] = []
                nodes_by_id[node_id].append((agent, node))

        # Check for conflicts
        for node_id, node_list in nodes_by_id.items():
            if len(node_list) < 2:
                continue

            # Compare all pairs
            for i in range(len(node_list)):
                for j in range(i + 1, len(node_list)):
                    agent1, node1 = node_list[i]
                    agent2, node2 = node_list[j]

                    # Check attribute conflicts
                    attrs1 = node1.get("attributes", {})
                    attrs2 = node2.get("attributes", {})

                    for key in set(attrs1.keys()) & set(attrs2.keys()):
                        if attrs1[key] != attrs2[key]:
                            conflicts.append({
                                "type": "attribute_conflict",
                                "node_id": node_id,
                                "attribute": key,
                                "source1": agent1,
                                "value1": attrs1[key],
                                "source2": agent2,
                                "value2": attrs2[key]
                            })

        return conflicts

    def resolve_conflict(self, conflict: Dict) -> Any:
        """Resolve a single conflict based on strategy"""
        if self.strategy == "priority":
            priority1 = self.priorities.get(conflict["source1"], 0)
            priority2 = self.priorities.get(conflict["source2"], 0)

            if priority2 > priority1:
                return conflict["value2"]
            else:
                return conflict["value1"]

        elif self.strategy == "last-write-wins":
            # Assume source2 is more recent
            return conflict["value2"]

        elif self.strategy == "manual":
            print(f"\nConflict detected:")
            print(f"  Node: {conflict['node_id']}")
            print(f"  Attribute: {conflict['attribute']}")
            print(f"  {conflict['source1']}: {conflict['value1']}")
            print(f"  {conflict['source2']}: {conflict['value2']}")

            choice = input("Choose [1/2/abort]: ").strip()

            if choice == "1":
                return conflict["value1"]
            elif choice == "2":
                return conflict["value2"]
            else:
                raise MergeConflict([conflict])

        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def merge_graphs(self, graphs: List[Dict]) -> Dict:
        """Merge multiple graphs with conflict resolution"""
        if not graphs:
            return {"metadata": {}, "nodes": [], "edges": []}

        # Detect conflicts
        conflicts = self.detect_conflicts(graphs)

        if conflicts:
            print(f"Detected {len(conflicts)} conflicts")
            self.conflicts = conflicts

        # Index nodes by ID
        nodes_by_id = {}

        for graph in graphs:
            agent = graph["metadata"].get("agent", "unknown")

            for node in graph["nodes"]:
                node_id = node["id"]

                if node_id not in nodes_by_id:
                    nodes_by_id[node_id] = node.copy()
                else:
                    # Merge attributes
                    existing_attrs = nodes_by_id[node_id].get("attributes", {})
                    new_attrs = node.get("attributes", {})

                    for key, value in new_attrs.items():
                        if key in existing_attrs and existing_attrs[key] != value:
                            # Conflict - resolve
                            conflict = {
                                "type": "attribute_conflict",
                                "node_id": node_id,
                                "attribute": key,
                                "source1": "existing",
                                "value1": existing_attrs[key],
                                "source2": agent,
                                "value2": value
                            }
                            resolved_value = self.resolve_conflict(conflict)
                            existing_attrs[key] = resolved_value
                        else:
                            existing_attrs[key] = value

                    nodes_by_id[node_id]["attributes"] = existing_attrs

        # Collect all edges (deduplication)
        edges_set = set()
        edges_list = []

        for graph in graphs:
            for edge in graph["edges"]:
                edge_key = (edge["source"], edge["target"], edge["type"])
                if edge_key not in edges_set:
                    edges_set.add(edge_key)
                    edges_list.append(edge)

        # Build merged graph
        merged = {
            "metadata": {
                "merged_from": [g["metadata"].get("agent", "unknown") for g in graphs],
                "merge_strategy": self.strategy,
                "conflicts_detected": len(conflicts),
                "conflicts_resolved": len(conflicts),
                "timestamp": self._get_timestamp()
            },
            "nodes": list(nodes_by_id.values()),
            "edges": edges_list
        }

        return merged

    def validate_graph(self, graph: Dict) -> None:
        """Run all validation checks on merged graph"""
        print("Validating merged graph...")

        # Validate node types
        self.validate_node_types(graph["nodes"])
        print("  ✓ Node types valid")

        # Validate edge types
        self.validate_edge_types(graph["edges"])
        print("  ✓ Edge types valid")

        # Validate references
        self.validate_references(graph["nodes"], graph["edges"])
        print("  ✓ References valid")

        # Check acyclicity
        if not self.is_acyclic(graph["nodes"], graph["edges"]):
            print("  ⚠ Warning: Graph contains cycle")
        else:
            print("  ✓ Graph is acyclic")

        print("Validation complete")

    def write_conflict_report(self, output_path: str) -> None:
        """Write conflict report to JSON file"""
        report = {
            "conflicts": self.conflicts,
            "summary": {
                "total_conflicts": len(self.conflicts),
                "conflict_types": {}
            }
        }

        # Count conflict types
        for conflict in self.conflicts:
            conflict_type = conflict["type"]
            if conflict_type not in report["summary"]["conflict_types"]:
                report["summary"]["conflict_types"][conflict_type] = 0
            report["summary"]["conflict_types"][conflict_type] += 1

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Conflict report written to: {output_path}")

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def main():
    parser = argparse.ArgumentParser(
        description="Merge .ctxpack semantic graphs with conflict detection"
    )

    # Agent arguments
    parser.add_argument("--agents", nargs='+', required=True, help="Agent names to merge")
    parser.add_argument("--workspace", default="/tmp/agent-workspaces", help="Agent workspace base directory")

    # Output arguments
    parser.add_argument("--output", help="Output merged graph file")
    parser.add_argument("--conflict-report", help="Write conflict report to file")

    # Merge strategy
    parser.add_argument("--strategy", choices=["priority", "last-write-wins", "manual"],
                       default="priority", help="Conflict resolution strategy")
    parser.add_argument("--priorities", help="Agent priorities (format: agent1:1,agent2:2)")

    # Validation
    parser.add_argument("--validate-only", action="store_true", help="Validate without merging")

    args = parser.parse_args()

    # Parse priorities
    priorities = {}
    if args.priorities:
        for item in args.priorities.split(','):
            agent, priority = item.split(':')
            priorities[agent.strip()] = int(priority)

    # Create coordinator
    coordinator = MergeCoordinator(strategy=args.strategy, priorities=priorities)

    # Load graphs
    print(f"Loading graphs from {len(args.agents)} agents...")
    graphs = []

    for agent in args.agents:
        try:
            graph = coordinator.load_graph(agent, args.workspace)
            graphs.append(graph)
            print(f"  ✓ Loaded {agent}: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges")
        except FileNotFoundError as e:
            print(f"  ✗ {e}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"  ✗ Invalid JSON in {agent} .ctxpack: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate only
    if args.validate_only:
        print("\nValidating individual graphs...")
        for i, graph in enumerate(graphs):
            print(f"\nGraph {i+1} ({graph['metadata'].get('agent', 'unknown')}):")
            try:
                coordinator.validate_graph(graph)
            except GraphValidationError as e:
                print(f"  ✗ Validation failed: {e}", file=sys.stderr)
                sys.exit(1)

        print("\nAll graphs valid")
        sys.exit(0)

    # Merge graphs
    print(f"\nMerging graphs (strategy: {args.strategy})...")
    try:
        merged = coordinator.merge_graphs(graphs)
    except MergeConflict as e:
        print(f"✗ Merge failed: {e}", file=sys.stderr)
        sys.exit(5)

    print(f"  ✓ Merged successfully")
    print(f"    Total nodes: {len(merged['nodes'])}")
    print(f"    Total edges: {len(merged['edges'])}")
    print(f"    Conflicts resolved: {merged['metadata']['conflicts_resolved']}")

    # Validate merged graph
    try:
        coordinator.validate_graph(merged)
    except GraphValidationError as e:
        print(f"✗ Validation failed: {e}", file=sys.stderr)
        sys.exit(5)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(merged, f, indent=2)

        print(f"\nMerged graph written to: {output_path}")

    # Write conflict report
    if args.conflict_report:
        coordinator.write_conflict_report(args.conflict_report)

    print("\nMerge complete")
    sys.exit(0)


if __name__ == "__main__":
    main()

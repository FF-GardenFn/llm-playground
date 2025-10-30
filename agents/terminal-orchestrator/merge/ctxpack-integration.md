# .ctxpack Integration

Systematic merging of semantic graph contributions from parallel agents with conflict detection, validation, and coherence guarantees.

---

## Table of Contents

1. [Semantic Graph Structure](#semantic-graph-structure)
2. [Merge Algorithms](#merge-algorithms)
3. [Graph Validation](#graph-validation)
4. [Conflict Resolution](#conflict-resolution)
5. [Reference Integrity](#reference-integrity)
6. [Integration Patterns](#integration-patterns)

---

## Semantic Graph Structure

### .ctxpack Format

**Basic Structure** (JSON):
```json
{
  "metadata": {
    "agent": "code-generator",
    "timestamp": "2025-10-28T14:30:52Z",
    "version": "1.0"
  },
  "nodes": [
    {
      "id": "node-1",
      "type": "module",
      "name": "auth_module",
      "attributes": {
        "path": "src/auth/auth_module.py",
        "lines": "1-150"
      }
    },
    {
      "id": "node-2",
      "type": "function",
      "name": "generate_jwt",
      "attributes": {
        "signature": "generate_jwt(user_id: str) -> str",
        "module": "node-1"
      }
    }
  ],
  "edges": [
    {
      "source": "node-1",
      "target": "node-2",
      "type": "contains",
      "label": "module contains function"
    }
  ]
}
```

### Node Types

**Common node types**:
- `module`: Python/JavaScript module or file
- `class`: Class definition
- `function`: Function/method definition
- `variable`: Global variable or constant
- `test`: Test case or test suite
- `dependency`: External dependency (library, package)
- `config`: Configuration file or setting

### Edge Types

**Common edge types**:
- `contains`: Parent-child relationship (module contains function)
- `calls`: Function call relationship (A calls B)
- `imports`: Import relationship (module A imports module B)
- `inherits`: Inheritance relationship (class A inherits from B)
- `depends_on`: Dependency relationship (A depends on B)
- `tests`: Testing relationship (test A tests function B)

---

## Merge Algorithms

### Union Merge (Additive)

**Scenario**: Agents add new nodes/edges without overlap

**Example**:
```
Agent 1 graph:
  nodes: [A, B]
  edges: [A→B]

Agent 2 graph:
  nodes: [C, D]
  edges: [C→D]

Merged graph:
  nodes: [A, B, C, D]
  edges: [A→B, C→D]
```

**Implementation**:
```python
def union_merge(graph1, graph2):
    merged = {
        "metadata": {
            "merged_from": [
                graph1["metadata"]["agent"],
                graph2["metadata"]["agent"]
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "nodes": [],
        "edges": []
    }

    # Merge nodes (simple concatenation)
    merged["nodes"] = graph1["nodes"] + graph2["nodes"]

    # Merge edges (simple concatenation)
    merged["edges"] = graph1["edges"] + graph2["edges"]

    return merged
```

### Overlay Merge (Update Existing)

**Scenario**: Agents update attributes of existing nodes

**Example**:
```
Agent 1 graph:
  nodes: [{id: "node-1", type: "function", name: "auth", attributes: {lines: "10-50"}}]

Agent 2 graph:
  nodes: [{id: "node-1", type: "function", name: "auth", attributes: {tested: true}}]

Merged graph:
  nodes: [{id: "node-1", type: "function", name: "auth", attributes: {lines: "10-50", tested: true}}]
```

**Implementation**:
```python
def overlay_merge(graph1, graph2):
    # Index nodes by ID
    nodes_by_id = {}

    for node in graph1["nodes"]:
        nodes_by_id[node["id"]] = node.copy()

    for node in graph2["nodes"]:
        if node["id"] in nodes_by_id:
            # Merge attributes
            existing = nodes_by_id[node["id"]]
            existing["attributes"].update(node["attributes"])
        else:
            # New node
            nodes_by_id[node["id"]] = node.copy()

    merged = {
        "metadata": {...},
        "nodes": list(nodes_by_id.values()),
        "edges": graph1["edges"] + graph2["edges"]
    }

    return merged
```

### Conflict Detection Merge

**Scenario**: Agents provide contradictory information

**Example**:
```
Agent 1 graph:
  nodes: [{id: "node-1", type: "function", name: "auth", attributes: {status: "implemented"}}]

Agent 2 graph:
  nodes: [{id: "node-1", type: "function", name: "auth", attributes: {status: "removed"}}]

Conflict detected: Node "node-1" has contradictory status (implemented vs removed)
```

**Implementation**:
```python
def conflict_detection_merge(graph1, graph2):
    conflicts = []

    nodes_by_id = {}
    for node in graph1["nodes"]:
        nodes_by_id[node["id"]] = node.copy()

    for node in graph2["nodes"]:
        if node["id"] in nodes_by_id:
            existing = nodes_by_id[node["id"]]

            # Check for attribute conflicts
            for key, value in node["attributes"].items():
                if key in existing["attributes"]:
                    if existing["attributes"][key] != value:
                        # Conflict detected
                        conflicts.append({
                            "node_id": node["id"],
                            "attribute": key,
                            "value1": existing["attributes"][key],
                            "value2": value,
                            "source1": graph1["metadata"]["agent"],
                            "source2": graph2["metadata"]["agent"]
                        })

    if conflicts:
        raise MergeConflictError(conflicts)

    # No conflicts, proceed with overlay merge
    return overlay_merge(graph1, graph2)
```

### Topological Merge (Dependency-Aware)

**Scenario**: Merge respects dependency ordering

**Example**:
```
Agent 1 graph:
  nodes: [A, B]
  edges: [A→B]  # A must be merged before B

Agent 2 graph:
  nodes: [B, C]
  edges: [B→C]  # B must be merged before C

Merge order: A → B → C
```

**Implementation**:
```python
def topological_sort(nodes, edges):
    # Build adjacency list
    graph = {node["id"]: [] for node in nodes}
    in_degree = {node["id"]: 0 for node in nodes}

    for edge in edges:
        graph[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] += 1

    # Kahn's algorithm
    queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
    sorted_nodes = []

    while queue:
        node_id = queue.pop(0)
        sorted_nodes.append(node_id)

        for neighbor in graph[node_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_nodes) != len(nodes):
        raise CyclicGraphError("Graph contains cycle")

    return sorted_nodes

def topological_merge(graphs):
    # Collect all nodes and edges
    all_nodes = []
    all_edges = []

    for graph in graphs:
        all_nodes.extend(graph["nodes"])
        all_edges.extend(graph["edges"])

    # Sort nodes topologically
    sorted_node_ids = topological_sort(all_nodes, all_edges)

    # Reorder nodes
    nodes_by_id = {node["id"]: node for node in all_nodes}
    sorted_nodes = [nodes_by_id[node_id] for node_id in sorted_node_ids]

    merged = {
        "metadata": {...},
        "nodes": sorted_nodes,
        "edges": all_edges
    }

    return merged
```

---

## Graph Validation

### Acyclicity Check

**Requirement**: Directed graph must be acyclic (DAG)

**Implementation**:
```python
def is_acyclic(nodes, edges):
    # DFS-based cycle detection
    graph = {node["id"]: [] for node in nodes}
    for edge in edges:
        graph[edge["source"]].append(edge["target"])

    visited = set()
    rec_stack = set()

    def has_cycle(node_id):
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

# Validate merged graph
if not is_acyclic(merged["nodes"], merged["edges"]):
    raise GraphValidationError("Graph contains cycle")
```

### Node Type Consistency

**Requirement**: All nodes have valid types

**Implementation**:
```python
VALID_NODE_TYPES = ["module", "class", "function", "variable", "test", "dependency", "config"]

def validate_node_types(nodes):
    errors = []

    for node in nodes:
        if "type" not in node:
            errors.append(f"Node {node['id']} missing type")
        elif node["type"] not in VALID_NODE_TYPES:
            errors.append(f"Node {node['id']} has invalid type: {node['type']}")

    if errors:
        raise GraphValidationError(errors)

validate_node_types(merged["nodes"])
```

### Edge Label Consistency

**Requirement**: All edges have valid labels

**Implementation**:
```python
VALID_EDGE_TYPES = ["contains", "calls", "imports", "inherits", "depends_on", "tests"]

def validate_edge_types(edges):
    errors = []

    for edge in edges:
        if "type" not in edge:
            errors.append(f"Edge {edge['source']}→{edge['target']} missing type")
        elif edge["type"] not in VALID_EDGE_TYPES:
            errors.append(f"Edge has invalid type: {edge['type']}")

    if errors:
        raise GraphValidationError(errors)

validate_edge_types(merged["edges"])
```

### Orphaned Node Detection

**Requirement**: No orphaned nodes (nodes with no edges)

**Implementation**:
```python
def find_orphaned_nodes(nodes, edges):
    node_ids = {node["id"] for node in nodes}
    connected_nodes = set()

    for edge in edges:
        connected_nodes.add(edge["source"])
        connected_nodes.add(edge["target"])

    orphaned = node_ids - connected_nodes

    if orphaned:
        print(f"Warning: Orphaned nodes detected: {orphaned}")
        # Optional: Remove orphaned nodes or flag as warning

find_orphaned_nodes(merged["nodes"], merged["edges"])
```

---

## Conflict Resolution

### Attribute-Level Conflicts

**Strategy 1: Last-Write-Wins**
```python
def last_write_wins(conflict):
    # Use value from most recent agent
    return conflict["value2"]  # Agent 2 more recent
```

**Strategy 2: Priority-Based**
```python
AGENT_PRIORITY = {
    "code-generator": 1,
    "code-reviewer": 2,  # Higher priority
    "data-profiler": 1
}

def priority_based_resolution(conflict):
    priority1 = AGENT_PRIORITY.get(conflict["source1"], 0)
    priority2 = AGENT_PRIORITY.get(conflict["source2"], 0)

    if priority2 > priority1:
        return conflict["value2"]
    else:
        return conflict["value1"]
```

**Strategy 3: Merge Values (Lists)**
```python
def merge_list_values(conflict):
    # If both values are lists, merge them
    if isinstance(conflict["value1"], list) and isinstance(conflict["value2"], list):
        return list(set(conflict["value1"] + conflict["value2"]))  # Union

    # Otherwise, use priority
    return priority_based_resolution(conflict)
```

**Strategy 4: Manual Escalation**
```python
def manual_escalation(conflict):
    print(f"Conflict detected:")
    print(f"  Node: {conflict['node_id']}")
    print(f"  Attribute: {conflict['attribute']}")
    print(f"  {conflict['source1']}: {conflict['value1']}")
    print(f"  {conflict['source2']}: {conflict['value2']}")

    choice = input("Choose [1/2/merge/abort]: ")

    if choice == "1":
        return conflict["value1"]
    elif choice == "2":
        return conflict["value2"]
    elif choice == "merge":
        return merge_list_values(conflict)
    else:
        raise MergeAbortedError("User aborted merge")
```

### Edge Conflicts

**Scenario**: Two agents add contradictory edges

**Example**:
```
Agent 1: A→B (type: "calls")
Agent 2: B→A (type: "calls")

Conflict: Creates cycle in call graph
```

**Resolution**:
```python
def resolve_edge_conflict(edge1, edge2):
    # Check if edges create cycle
    if edge1["source"] == edge2["target"] and edge1["target"] == edge2["source"]:
        print(f"Warning: Bidirectional edge detected")
        print(f"  {edge1['source']}→{edge1['target']} ({edge1['type']})")
        print(f"  {edge2['source']}→{edge2['target']} ({edge2['type']})")

        # Strategy: Keep both edges if different types (e.g., "calls" vs "imports")
        if edge1["type"] != edge2["type"]:
            return [edge1, edge2]

        # Strategy: Keep only one (manual choice)
        return [manual_escalation_edge(edge1, edge2)]

    return [edge1, edge2]
```

---

## Reference Integrity

### Dangling References

**Problem**: Edge references non-existent node

**Detection**:
```python
def validate_references(nodes, edges):
    node_ids = {node["id"] for node in nodes}
    errors = []

    for edge in edges:
        if edge["source"] not in node_ids:
            errors.append(f"Edge references non-existent source: {edge['source']}")

        if edge["target"] not in node_ids:
            errors.append(f"Edge references non-existent target: {edge['target']}")

    if errors:
        raise ReferenceIntegrityError(errors)

validate_references(merged["nodes"], merged["edges"])
```

**Auto-Repair** (create missing nodes):
```python
def auto_repair_references(nodes, edges):
    node_ids = {node["id"] for node in nodes}
    missing_nodes = []

    for edge in edges:
        if edge["source"] not in node_ids:
            # Create placeholder node
            missing_nodes.append({
                "id": edge["source"],
                "type": "unknown",
                "name": edge["source"],
                "attributes": {"created_by": "auto_repair"}
            })
            node_ids.add(edge["source"])

        if edge["target"] not in node_ids:
            missing_nodes.append({
                "id": edge["target"],
                "type": "unknown",
                "name": edge["target"],
                "attributes": {"created_by": "auto_repair"}
            })
            node_ids.add(edge["target"])

    return nodes + missing_nodes
```

### Attribute References

**Problem**: Node attribute references another node incorrectly

**Example**:
```json
{
  "id": "function-1",
  "attributes": {
    "module": "module-99"  // module-99 doesn't exist
  }
}
```

**Validation**:
```python
def validate_attribute_references(nodes):
    node_ids = {node["id"] for node in nodes}
    errors = []

    REFERENCE_ATTRIBUTES = ["module", "parent", "tested_by", "depends_on"]

    for node in nodes:
        for attr_name, attr_value in node.get("attributes", {}).items():
            if attr_name in REFERENCE_ATTRIBUTES:
                # Check if reference exists
                if isinstance(attr_value, str) and attr_value not in node_ids:
                    errors.append(f"Node {node['id']} references non-existent {attr_name}: {attr_value}")

    if errors:
        raise ReferenceIntegrityError(errors)

validate_attribute_references(merged["nodes"])
```

---

## Integration Patterns

### Pattern 1: Sequential Integration

**Scenario**: Merge graphs one at a time (A + B, then + C)

**Implementation**:
```python
def sequential_merge(graphs):
    if not graphs:
        return {"nodes": [], "edges": []}

    merged = graphs[0]

    for graph in graphs[1:]:
        merged = overlay_merge(merged, graph)
        validate_references(merged["nodes"], merged["edges"])

    return merged

# Usage
merged = sequential_merge([graph1, graph2, graph3])
```

### Pattern 2: Parallel Integration (All at Once)

**Scenario**: Merge all graphs simultaneously

**Implementation**:
```python
def parallel_merge(graphs):
    all_nodes = []
    all_edges = []

    for graph in graphs:
        all_nodes.extend(graph["nodes"])
        all_edges.extend(graph["edges"])

    # Deduplicate nodes by ID
    nodes_by_id = {}
    for node in all_nodes:
        if node["id"] in nodes_by_id:
            # Merge attributes
            nodes_by_id[node["id"]]["attributes"].update(node["attributes"])
        else:
            nodes_by_id[node["id"]] = node.copy()

    merged = {
        "metadata": {...},
        "nodes": list(nodes_by_id.values()),
        "edges": all_edges
    }

    validate_references(merged["nodes"], merged["edges"])
    return merged
```

### Pattern 3: Layered Integration (Domain Separation)

**Scenario**: Merge graphs by domain (frontend, backend, data)

**Implementation**:
```python
def layered_merge(graphs_by_domain):
    # Merge within each domain first
    domain_merged = {}

    for domain, graphs in graphs_by_domain.items():
        domain_merged[domain] = parallel_merge(graphs)

    # Then merge across domains
    all_graphs = list(domain_merged.values())
    final_merged = parallel_merge(all_graphs)

    return final_merged

# Usage
graphs_by_domain = {
    "frontend": [react_graph1, react_graph2],
    "backend": [api_graph1, api_graph2],
    "data": [db_graph]
}

merged = layered_merge(graphs_by_domain)
```

### Pattern 4: Incremental Integration (Streaming)

**Scenario**: Merge graphs as agents complete (don't wait for all)

**Implementation**:
```python
def incremental_merge(graph_stream):
    merged = {"nodes": [], "edges": []}

    for graph in graph_stream:
        # Merge as soon as available
        merged = overlay_merge(merged, graph)

        # Validate incrementally
        try:
            validate_references(merged["nodes"], merged["edges"])
        except ReferenceIntegrityError as e:
            print(f"Warning: Reference integrity issue: {e}")
            # Continue merging, may resolve later

    # Final validation
    validate_references(merged["nodes"], merged["edges"])
    return merged

# Usage (generator that yields graphs as agents complete)
def agent_graph_stream():
    while agents_running():
        completed_agent = wait_for_agent_completion()
        yield load_graph(completed_agent)

merged = incremental_merge(agent_graph_stream())
```

---

## Complete Merge Workflow

**End-to-End Example**:

```python
def merge_agent_graphs(agent_names):
    """
    Merge .ctxpack graphs from multiple agents with full validation.
    """
    graphs = []

    # Step 1: Load graphs from each agent
    for agent_name in agent_names:
        graph_path = f"/tmp/agent-workspaces/{agent_name}/.ctxpack"

        try:
            with open(graph_path, 'r') as f:
                graph = json.load(f)
                graphs.append(graph)
        except FileNotFoundError:
            print(f"Warning: No .ctxpack found for {agent_name}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {agent_name} .ctxpack")

    if not graphs:
        raise MergeError("No valid graphs to merge")

    # Step 2: Merge graphs
    try:
        merged = parallel_merge(graphs)
    except MergeConflictError as e:
        print("Conflicts detected, attempting resolution...")
        merged = resolve_conflicts_and_merge(graphs, e.conflicts)

    # Step 3: Validate merged graph
    validate_node_types(merged["nodes"])
    validate_edge_types(merged["edges"])
    validate_references(merged["nodes"], merged["edges"])

    # Step 4: Check acyclicity
    if not is_acyclic(merged["nodes"], merged["edges"]):
        print("Warning: Merged graph contains cycle")

    # Step 5: Find orphaned nodes (warning only)
    find_orphaned_nodes(merged["nodes"], merged["edges"])

    # Step 6: Write merged graph
    output_path = "/tmp/agent-outputs/merged.ctxpack"
    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)

    print(f"Successfully merged {len(graphs)} graphs")
    print(f"  Total nodes: {len(merged['nodes'])}")
    print(f"  Total edges: {len(merged['edges'])}")
    print(f"  Output: {output_path}")

    return merged

# Usage
merged = merge_agent_graphs(["code-generator", "code-reviewer", "data-profiler"])
```

---

## Best Practices

1. **Always validate after merge** (references, types, acyclicity)
2. **Use overlay merge by default** (handles node updates)
3. **Detect conflicts early** (before attempting merge)
4. **Provide clear conflict resolution** (manual escalation when needed)
5. **Log all merge operations** (audit trail for debugging)
6. **Test with empty graphs** (handle edge cases)
7. **Use unique node IDs** (avoid collisions across agents)
8. **Document node/edge types** (enforce schema consistency)

---

## Example: Complete Integration Script

See `atools/merge_coordinator.py` for full implementation of semantic graph merging with conflict detection and validation.

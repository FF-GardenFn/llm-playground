# Conflict Detection

**Purpose**: Identify conflicts between agent outputs before merging to prevent integration failures.

**When to Use**: Phase 4 (Merge Strategy) after all agents complete and outputs validated.

**Gate**: Cannot merge until conflicts resolved or resolution strategy determined.

---

## Conflict Types

```
Agent Outputs Validated
    ↓
Conflict Detection
    ├─→ File Conflicts (same file modified by multiple agents)
    ├─→ Semantic Conflicts (contradictory changes)
    ├─→ Dependency Conflicts (incompatible requirements)
    └─→ Schema Conflicts (incompatible data structures)
    ↓
Conflicts found → Apply resolution strategy
No conflicts → Proceed to merge
```

---

## 1. File Conflicts

### Direct File Conflicts

**Scenario**: Multiple agents modify the same file

**Detection**:
```python
def detect_file_conflicts(agent_outputs):
    file_map = {}  # path → list of agents that modified it

    for agent in agent_outputs:
        for file_path in agent["modified_files"]:
            if file_path not in file_map:
                file_map[file_path] = []
            file_map[file_path].append(agent["agent_name"])

    # Find files modified by >1 agent
    conflicts = {
        path: agents
        for path, agents in file_map.items()
        if len(agents) > 1
    }

    return conflicts
```

**Example**:
```json
{
  "file_conflicts": {
    "src/auth.py": ["code-generator", "code-reviewer"],
    "requirements.txt": ["code-generator", "data-profiler"]
  }
}
```

### Resolution Strategies

**1. Last-Write-Wins** (timestamp-based):
```python
def resolve_last_write_wins(file_path, agents):
    latest_agent = max(agents, key=lambda a: a["end_time"])
    return {
        "resolution": "last_write_wins",
        "winner": latest_agent["agent_name"],
        "action": f"Use {file_path} from {latest_agent['agent_name']}"
    }
```

**2. Three-Way Merge** (git-style):
```bash
# Merge file from agent1 and agent2 against common base
git merge-file --theirs \
    outputs/agent1/src/auth.py \
    base/src/auth.py \
    outputs/agent2/src/auth.py

# Check for conflicts
if [ $? -ne 0 ]; then
    echo "Merge conflicts detected - manual resolution required"
fi
```

**3. Manual Review**:
```python
def create_conflict_markers(file_path, agent1_content, agent2_content):
    return f"""
<<<<<<< {agent1['agent_name']}
{agent1_content}
=======
{agent2_content}
>>>>>>> {agent2['agent_name']}
"""
```

---

## 2. Semantic Conflicts

### Contradictory Changes

**Scenario**: Agents make logically incompatible changes

**Example**:
- Agent 1 (code-generator): Implements authentication with JWT tokens
- Agent 2 (code-generator): Implements authentication with session cookies
- **Conflict**: Two incompatible authentication mechanisms

**Detection**:
```python
def detect_semantic_conflicts(agent_outputs):
    conflicts = []

    # Extract semantic features from each agent's .ctxpack
    for i, agent1 in enumerate(agent_outputs):
        ctxpack1 = load_ctxpack(agent1["ctxpack_path"])
        features1 = extract_features(ctxpack1)

        for agent2 in agent_outputs[i+1:]:
            ctxpack2 = load_ctxpack(agent2["ctxpack_path"])
            features2 = extract_features(ctxpack2)

            # Check for contradictions
            contradictions = find_contradictions(features1, features2)
            if contradictions:
                conflicts.append({
                    "agents": [agent1["agent_name"], agent2["agent_name"]],
                    "contradictions": contradictions
                })

    return conflicts

def find_contradictions(features1, features2):
    contradictions = []

    # Check for mutually exclusive features
    if "authentication" in features1 and "authentication" in features2:
        if features1["authentication"]["method"] != features2["authentication"]["method"]:
            contradictions.append({
                "type": "authentication_method",
                "agent1_value": features1["authentication"]["method"],
                "agent2_value": features2["authentication"]["method"],
                "severity": "high"
            })

    # Check for incompatible versions
    if "dependencies" in features1 and "dependencies" in features2:
        for dep in features1["dependencies"]:
            if dep["name"] in [d["name"] for d in features2["dependencies"]]:
                dep2 = next(d for d in features2["dependencies"] if d["name"] == dep["name"])
                if dep["version"] != dep2["version"]:
                    contradictions.append({
                        "type": "dependency_version",
                        "dependency": dep["name"],
                        "agent1_version": dep["version"],
                        "agent2_version": dep2["version"],
                        "severity": "medium"
                    })

    return contradictions
```

**Example**:
```json
{
  "semantic_conflicts": [
    {
      "agents": ["code-generator-1", "code-generator-2"],
      "contradictions": [
        {
          "type": "authentication_method",
          "agent1_value": "jwt",
          "agent2_value": "session",
          "severity": "high"
        }
      ]
    }
  ]
}
```

### Resolution Strategies

**1. Priority-Based** (agent priority defines winner):
```python
def resolve_by_priority(conflict, agent_priorities):
    agents = conflict["agents"]
    winner = max(agents, key=lambda a: agent_priorities.get(a, 0))
    return {
        "resolution": "priority_based",
        "winner": winner,
        "action": f"Use {winner}'s implementation, discard others"
    }
```

**2. Merge Both** (if compatible):
```python
def resolve_merge_both(conflict):
    # Example: Both agents add different endpoints
    # Solution: Include both endpoints in merged API
    return {
        "resolution": "merge_both",
        "action": "Include implementations from both agents",
        "requires_integration": True
    }
```

**3. Escalate to Orchestrator**:
```python
def escalate_conflict(conflict):
    return {
        "resolution": "escalate",
        "action": "Manual decision required from Main Orchestrator",
        "question": f"Choose authentication method: {conflict['agent1_value']} or {conflict['agent2_value']}?"
    }
```

---

## 3. Dependency Conflicts

### Package Version Conflicts

**Scenario**: Agents require different versions of same dependency

**Detection**:
```python
def detect_dependency_conflicts(agent_outputs):
    dependencies = {}  # package → {agent: version}

    for agent in agent_outputs:
        requirements_file = f"{agent['outputs_dir']}/requirements.txt"
        if os.path.exists(requirements_file):
            with open(requirements_file) as f:
                for line in f:
                    if "==" in line:
                        package, version = line.strip().split("==")
                        if package not in dependencies:
                            dependencies[package] = {}
                        dependencies[package][agent["agent_name"]] = version

    # Find packages with multiple versions
    conflicts = {
        package: agents_versions
        for package, agents_versions in dependencies.items()
        if len(set(agents_versions.values())) > 1
    }

    return conflicts
```

**Example**:
```json
{
  "dependency_conflicts": {
    "pandas": {
      "code-generator": "2.0.0",
      "data-profiler": "1.5.2"
    },
    "numpy": {
      "code-generator": "1.24.0",
      "ml-trainer": "1.23.5"
    }
  }
}
```

### Resolution Strategies

**1. Latest Version**:
```python
def resolve_latest_version(package, versions):
    from packaging import version
    latest = max(versions.values(), key=version.parse)
    return {
        "resolution": "latest_version",
        "package": package,
        "chosen_version": latest,
        "action": f"Use {package}=={latest} (latest across agents)"
    }
```

**2. Compatible Range**:
```python
def resolve_compatible_range(package, versions):
    from packaging import version
    # Find minimum version that satisfies all agents
    min_version = max(versions.values(), key=version.parse)
    return {
        "resolution": "compatible_range",
        "package": package,
        "chosen_version": f">={min_version}",
        "action": f"Use {package}>={min_version} (compatible with all)"
    }
```

**3. Virtual Environments** (isolate agents):
```python
def resolve_isolated_envs(package, versions):
    return {
        "resolution": "isolated_environments",
        "package": package,
        "action": "Keep agents in separate virtual environments",
        "note": "Merge outputs but maintain separate runtime environments"
    }
```

---

## 4. Schema Conflicts

### Data Structure Incompatibilities

**Scenario**: Agents produce outputs with incompatible schemas

**Example**:
- Agent 1 produces `{user_id: int, name: str}`
- Agent 2 produces `{userId: string, fullName: str}`
- **Conflict**: Different field names and types

**Detection**:
```python
def detect_schema_conflicts(agent_outputs):
    schemas = {}

    for agent in agent_outputs:
        ctxpack = load_ctxpack(agent["ctxpack_path"])
        if "schema" in ctxpack["metadata"]:
            schemas[agent["agent_name"]] = ctxpack["metadata"]["schema"]

    conflicts = []
    schema_pairs = list(itertools.combinations(schemas.items(), 2))

    for (agent1, schema1), (agent2, schema2) in schema_pairs:
        incompatibilities = compare_schemas(schema1, schema2)
        if incompatibilities:
            conflicts.append({
                "agents": [agent1, agent2],
                "incompatibilities": incompatibilities
            })

    return conflicts

def compare_schemas(schema1, schema2):
    incompatibilities = []

    # Check for field name mismatches
    fields1 = set(schema1.keys())
    fields2 = set(schema2.keys())
    if fields1 != fields2:
        incompatibilities.append({
            "type": "field_mismatch",
            "agent1_fields": list(fields1),
            "agent2_fields": list(fields2),
            "only_in_agent1": list(fields1 - fields2),
            "only_in_agent2": list(fields2 - fields1)
        })

    # Check for type mismatches (shared fields)
    for field in fields1 & fields2:
        if schema1[field]["type"] != schema2[field]["type"]:
            incompatibilities.append({
                "type": "type_mismatch",
                "field": field,
                "agent1_type": schema1[field]["type"],
                "agent2_type": schema2[field]["type"]
            })

    return incompatibilities
```

**Example**:
```json
{
  "schema_conflicts": [
    {
      "agents": ["code-generator", "data-profiler"],
      "incompatibilities": [
        {
          "type": "field_mismatch",
          "only_in_agent1": ["user_id"],
          "only_in_agent2": ["userId"]
        },
        {
          "type": "type_mismatch",
          "field": "user_id",
          "agent1_type": "int",
          "agent2_type": "string"
        }
      ]
    }
  ]
}
```

### Resolution Strategies

**1. Schema Transformation**:
```python
def resolve_schema_transformation(conflict):
    return {
        "resolution": "schema_transformation",
        "action": "Apply transformation to align schemas",
        "transformations": [
            {"agent": "agent2", "transform": "rename", "from": "userId", "to": "user_id"},
            {"agent": "agent2", "transform": "cast", "field": "user_id", "to_type": "int"}
        ]
    }
```

**2. Union Schema**:
```python
def resolve_union_schema(conflict):
    # Create schema that includes all fields from both agents
    return {
        "resolution": "union_schema",
        "action": "Create union schema with all fields",
        "merged_schema": {
            "user_id": "int",  # From agent1
            "userId": "string",  # From agent2
            "name": "string",  # From agent1
            "fullName": "string"  # From agent2
        },
        "note": "Redundant fields kept for compatibility"
    }
```

---

## Conflict Detection Report

### Output Format

```json
{
  "execution_id": "exec-20251030-1430-abc123",
  "detection_timestamp": "2025-10-30T14:45:00Z",
  "conflicts_detected": true,
  "conflict_summary": {
    "file_conflicts": 2,
    "semantic_conflicts": 1,
    "dependency_conflicts": 3,
    "schema_conflicts": 1
  },
  "conflicts": {
    "file_conflicts": {
      "src/auth.py": {
        "agents": ["code-generator", "code-reviewer"],
        "severity": "medium",
        "resolution_required": true
      },
      "requirements.txt": {
        "agents": ["code-generator", "data-profiler"],
        "severity": "low",
        "resolution_required": true
      }
    },
    "semantic_conflicts": [
      {
        "agents": ["code-generator-1", "code-generator-2"],
        "type": "authentication_method",
        "severity": "high",
        "details": {
          "agent1_value": "jwt",
          "agent2_value": "session"
        },
        "resolution_required": true
      }
    ],
    "dependency_conflicts": {
      "pandas": {
        "versions": {
          "code-generator": "2.0.0",
          "data-profiler": "1.5.2"
        },
        "severity": "medium",
        "resolution_required": true
      }
    },
    "schema_conflicts": [
      {
        "agents": ["code-generator", "data-profiler"],
        "field": "user_id",
        "severity": "medium",
        "details": {
          "agent1_type": "int",
          "agent2_type": "string"
        },
        "resolution_required": true
      }
    ]
  },
  "recommended_actions": [
    {
      "conflict": "file_conflicts:src/auth.py",
      "recommendation": "Three-way merge with manual conflict markers"
    },
    {
      "conflict": "semantic_conflicts:authentication_method",
      "recommendation": "Escalate to Main Orchestrator for decision"
    },
    {
      "conflict": "dependency_conflicts:pandas",
      "recommendation": "Use pandas>=2.0.0 (latest version)"
    },
    {
      "conflict": "schema_conflicts:user_id",
      "recommendation": "Apply schema transformation (cast string to int)"
    }
  ]
}
```

---

## Conflict Resolution Process

```
1. Detect conflicts
    ↓
2. Classify by severity (low, medium, high, critical)
    ↓
3. Apply automatic resolution (if strategy defined)
    ↓
4. Generate conflict report for manual conflicts
    ↓
5. Escalate unresolved conflicts to Main Orchestrator
    ↓
6. Apply resolutions
    ↓
7. Verify no new conflicts introduced
    ↓
8. Proceed to merge
```

---

## Integration

### Called from Terminal Orchestrator

```python
from terminal_orchestrator.merge import conflict_detection

# Before merge
conflict_report = conflict_detection.detect_all_conflicts(
    agent_outputs=[
        {"agent_name": "code-generator", "outputs_dir": "...", "ctxpack_path": "..."},
        {"agent_name": "code-reviewer", "outputs_dir": "...", "ctxpack_path": "..."}
    ]
)

if conflict_report["conflicts_detected"]:
    # Apply resolution strategy
    if merge_strategy["conflict_resolution"] == "auto":
        conflict_detection.resolve_conflicts(conflict_report, strategy="auto")
    elif merge_strategy["conflict_resolution"] == "manual_review":
        # Write conflict report for Main Orchestrator review
        with open("conflicts.json", "w") as f:
            json.dump(conflict_report, f, indent=2)
        raise MergeConflictError("Conflicts require manual resolution")
    elif merge_strategy["conflict_resolution"] == "fail_on_conflict":
        raise MergeConflictError(f"{conflict_report['conflict_summary']} conflicts detected")
else:
    print("✓ No conflicts detected, proceeding to merge")
```

---

## Summary

**Conflict Types**:
- **File**: Same file modified by multiple agents
- **Semantic**: Contradictory changes (incompatible implementations)
- **Dependency**: Different versions of same package
- **Schema**: Incompatible data structures

**Resolution Strategies**:
- **Auto**: Last-write-wins, latest version, union schema
- **Manual**: Three-way merge with conflict markers, escalate to orchestrator
- **Isolate**: Separate environments, keep both implementations

**Gate**: Cannot merge until conflicts resolved or resolution strategy determined

**Output**: Conflict report with detected conflicts, severity, recommended actions

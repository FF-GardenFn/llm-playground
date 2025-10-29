# Orchestrator Skills: Automated Orchestration Tools

## Overview

The orchestrator leverages automated tools (`atools/`) to accelerate orchestration tasks where manual coordination would be time-consuming or error-prone. These tools embody orchestration expertise in executable form.

---

## When to Use Tools

**Use automated tools when**:
- Task decomposition involves 5+ tasks (dependency_analyzer.py)
- Specialist matching requires confidence scoring (agent_selector.py)
- Integration involves multiple parallel outputs (conflict_detector.py, merge_coordinator.py)
- Manual coordination overhead would be significant

**Skip automated tools when**:
- Simple 1-3 task orchestrations
- Sequential work with clear dependencies
- Single specialist assignment
- Trivial integration

---

## Tool 1: agent_selector.py

**Purpose**: Automated specialist matching with confidence scoring and anti-pattern detection.

**When to Invoke**:
- Phase 3 (Delegation) with multiple tasks requiring different specialists
- Unclear specialist choice (domain ambiguity)
- Need confidence scoring for assignment justification

### Usage Pattern

```bash
# Single task matching
python atools/agent_selector.py \
  --task "Implement JWT authentication" \
  --context context.json

# Multiple tasks from file
python atools/agent_selector.py \
  --tasks tasks.json \
  --context context.json \
  --output assignments.json

# Interactive mode
python atools/agent_selector.py --interactive
```

### Input Format

**context.json**:
```json
{
  "domain": "backend",
  "requirements": ["test-first", "security"],
  "outputs_needed": ["code", "tests"]
}
```

**tasks.json**:
```json
{
  "tasks": [
    {
      "id": "task_1",
      "description": "Implement user authentication",
      "domain": "backend",
      "requirements": ["security", "testing"],
      "outputs_needed": ["code", "tests", "security review"]
    }
  ]
}
```

### Output Format

```json
{
  "assignments": [
    {
      "task_id": "task_1",
      "task_description": "Implement user authentication",
      "specialist": "code-generator",
      "confidence": 0.95,
      "rationale": {
        "domain_fit": "Exact domain match: backend",
        "cognitive_process": "Strong alignment: test-first, security",
        "output_format": "All outputs match",
        "cognitive_model": "TDD Practitioner"
      },
      "anti_patterns": [],
      "alternative": null
    }
  ]
}
```

### Integration with Orchestration

**Load point**: Phase 3 (Delegation) when specialist assignment needed

**File reference**: delegation/specialist-matching.md

**Workflow integration**:
1. Decomposition complete (Phase 2) → tasks identified
2. Load agent_selector.py → automated matching
3. Review confidence scores → adjust if low confidence (<0.7)
4. Proceed to context provision → delegation/context-provision.md

---

## Tool 2: dependency_analyzer.py

**Purpose**: Automated dependency analysis, critical path calculation, and parallelization level generation.

**When to Invoke**:
- Phase 2 (Decomposition) with 5+ tasks
- Complex dependency graphs
- Need critical path identification
- Parallelization optimization required

### Usage Pattern

```bash
# Basic dependency analysis
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json

# With critical path calculation
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json \
  --critical-path

# Generate parallelization levels
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json \
  --parallel-levels \
  --output analysis.json

# With visualization
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json \
  --visualize graph.png
```

### Input Format

**tasks.json**:
```json
{
  "tasks": [
    {"id": "A", "description": "Design schema"},
    {"id": "B", "description": "Implement API"},
    {"id": "C", "description": "Create frontend"}
  ]
}
```

**deps.json**:
```json
{
  "dependencies": {
    "A": [],
    "B": ["A"],
    "C": ["B"]
  },
  "durations": {
    "A": 1.5,
    "B": 2.0,
    "C": 1.5
  }
}
```

### Output Format

```json
{
  "topological_order": ["A", "B", "C"],
  "parallelization_levels": [["A"], ["B"], ["C"]],
  "critical_path": {
    "path": ["A", "B", "C"],
    "total_duration": 5.0
  },
  "sequential_duration": 5.0,
  "parallel_duration": 5.0,
  "speedup": 1.0,
  "cycles_detected": false
}
```

**Cycle detection** (if circular dependency):
```json
{
  "error": {
    "code": 3,
    "message": "Circular dependency detected",
    "details": {"cycle": ["A", "B", "C", "A"]},
    "suggestion": "Review task decomposition to break circular dependency"
  }
}
```

### Integration with Orchestration

**Load point**: Phase 2 (Decomposition) when dependencies analyzed

**File reference**: decomposition/dependency-analysis.md

**Workflow integration**:
1. Tasks decomposed (Phase 2) → task list ready
2. Load dependency_analyzer.py → analyze dependencies
3. Check for cycles → resolve if detected
4. Identify critical path → prioritize critical tasks
5. Generate parallelization levels → assign specialists in parallel
6. Proceed to delegation → Phase 3

---

## Tool 3: conflict_detector.py

**Purpose**: Automated detection of file, semantic, dependency, and schema conflicts in task outputs.

**When to Invoke**:
- Phase 5 (Integration) before merging
- Multiple parallel specialists finished
- High risk of conflicts (shared files, APIs, schemas)

### Usage Pattern

```bash
# Detect all conflict types
python atools/conflict_detector.py \
  --outputs outputs.json \
  --output conflicts.json

# Detect specific type only
python atools/conflict_detector.py \
  --outputs outputs.json \
  --type file

# Generate markdown report
python atools/conflict_detector.py \
  --outputs outputs.json \
  --report conflicts_report.md
```

### Input Format

**outputs.json**:
```json
{
  "outputs": {
    "task_1": {
      "modified_files": ["auth.py", "models.py"],
      "api_contracts": {
        "/auth/login": {
          "method": "POST",
          "request": {"email": "string", "password": "string"},
          "response": {"token": "string"}
        }
      },
      "dependencies": {"bcrypt": "3.2.0"},
      "schema_changes": [
        {"table": "users", "operation": "add_column", "column": "oauth_provider"}
      ]
    },
    "task_2": {
      "modified_files": ["auth.py"],
      "api_contracts": {
        "/auth/login": {
          "method": "POST",
          "request": {"email": "string", "password": "string"},
          "response": {"token": "string", "user": "object"}
        }
      },
      "dependencies": {"bcrypt": "3.2.0"}
    }
  }
}
```

### Output Format

```json
{
  "conflicts": [
    {
      "type": "file_conflict",
      "severity": "medium",
      "tasks": ["task_1", "task_2"],
      "details": {
        "file": "auth.py",
        "conflict_type": "both_modified"
      },
      "resolution_strategies": [
        "serialize (execute task_1 then task_2)",
        "partition file into separate files",
        "careful coordination (non-overlapping regions)"
      ],
      "recommended": "serialize"
    },
    {
      "type": "semantic_conflict",
      "subtype": "api_contract_mismatch",
      "severity": "high",
      "tasks": ["task_1", "task_2"],
      "details": {
        "endpoint": "/auth/login",
        "contract1": {"response": {"token": "string"}},
        "contract2": {"response": {"token": "string", "user": "object"}}
      },
      "resolution_strategies": [
        "align contracts (update one to match the other)",
        "add adapter layer",
        "version endpoints (v1, v2)"
      ],
      "recommended": "align contracts"
    }
  ],
  "conflict_summary": {
    "total": 2,
    "by_severity": {"high": 1, "medium": 1},
    "by_type": {"file_conflict": 1, "semantic_conflict": 1}
  }
}
```

### Integration with Orchestration

**Load point**: Phase 5 (Integration) before merging

**File reference**: integration/conflict-resolution.md

**Workflow integration**:
1. All specialists complete (Phase 4) → outputs ready
2. Load conflict_detector.py → detect conflicts
3. Review conflict report → categorize by severity
4. Apply resolution strategies → resolve conflicts
5. Proceed to merge → Phase 5 (merge_coordinator.py)

---

## Tool 4: merge_coordinator.py

**Purpose**: Coordinated merging with topological sort, conflict resolution, automated testing, and rollback on failure.

**When to Invoke**:
- Phase 5 (Integration) when merging outputs
- After conflicts detected and resolved
- Need automated verification before final merge

### Usage Pattern

```bash
# Basic merge (topological order)
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --strategy topological \
  --output merge_result.json

# With conflict resolution
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --conflicts conflicts.json \
  --resolve

# With verification
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --verify "pytest tests/" \
  --rollback-on-failure

# Dry run (preview without executing)
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --dry-run \
  --verbose
```

### Input Format

**outputs.json**:
```json
{
  "outputs": {
    "task_1": {
      "dependencies": [],
      "files": {
        "auth.py": "# Auth implementation..."
      }
    },
    "task_2": {
      "dependencies": ["task_1"],
      "files": {
        "login.py": "# Login endpoint..."
      }
    }
  }
}
```

**conflicts.json** (from conflict_detector.py):
```json
{
  "conflicts": [
    {
      "type": "file_conflict",
      "severity": "medium",
      "tasks": ["task_1", "task_2"],
      "details": {"file": "auth.py"}
    }
  ]
}
```

### Output Format

**Success**:
```json
{
  "merge_result": {
    "status": "success",
    "merged_tasks": ["task_1", "task_2"],
    "merge_order": ["task_1", "task_2"],
    "conflicts_resolved": 1,
    "verification": {"tests_passed": true},
    "merged_files": ["auth.py", "login.py"],
    "warnings": [],
    "errors": [],
    "rollbacks": 0,
    "duration": 2.3
  }
}
```

**Failure (verification failed)**:
```json
{
  "merge_result": {
    "status": "failed",
    "error": "Verification failed",
    "merged_tasks": ["task_1", "task_2"],
    "verification": {
      "tests_passed": false,
      "test_output": "test_login.py::test_auth FAILED..."
    },
    "rollbacks": 1,
    "duration": 3.5
  }
}
```

**Dry run**:
```json
{
  "merge_result": {
    "status": "dry_run",
    "merged_tasks": ["task_1", "task_2"],
    "merge_order": ["task_1", "task_2"],
    "conflicts_resolved": 0,
    "merged_files": ["auth.py", "login.py"],
    "warnings": ["File conflict: auth.py modified by multiple tasks"],
    "duration": 0.1
  }
}
```

### Integration with Orchestration

**Load point**: Phase 5 (Integration) during merge execution

**File reference**: integration/conflict-resolution.md, verification/success-validation.md

**Workflow integration**:
1. Conflicts detected (conflict_detector.py) → conflicts resolved
2. Load merge_coordinator.py → execute merge
3. Topological sort → determine merge order
4. Merge files → integrate outputs
5. Run verification → test merged result
6. If tests fail → rollback (if enabled)
7. If tests pass → mark Phase 5 complete
8. Proceed to final verification → verification/success-validation.md

---

## Tool Selection Decision Tree

```
Phase 1 (Reconnaissance): No tools needed (manual clarification)
    ↓
Phase 2 (Decomposition):
    Tasks > 5? → Use dependency_analyzer.py
    Tasks ≤ 5? → Manual dependency analysis
    ↓
Phase 3 (Delegation):
    Multiple specialists? → Use agent_selector.py
    Single specialist? → Manual assignment
    ↓
Phase 4 (Coordination): No tools needed (manual tracking)
    ↓
Phase 5 (Integration):
    Parallel outputs? → Use conflict_detector.py
    Sequential work? → Direct merge
    ↓
    Conflicts detected? → Resolve, then use merge_coordinator.py
    No conflicts? → Use merge_coordinator.py for verification
```

---

## Tool Chaining Patterns

### Pattern 1: Full Automation Pipeline

**Scenario**: Complex orchestration with 10+ tasks, multiple specialists, parallel work

**Tool sequence**:
1. **Phase 2**: `dependency_analyzer.py` → parallelization levels
2. **Phase 3**: `agent_selector.py` → specialist assignments
3. **Phase 5**: `conflict_detector.py` → identify conflicts
4. **Phase 5**: `merge_coordinator.py` → integrate with verification

**Example**:
```bash
# Phase 2: Analyze dependencies
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json \
  --parallel-levels \
  --output analysis.json

# Phase 3: Match specialists
python atools/agent_selector.py \
  --tasks tasks.json \
  --context context.json \
  --output assignments.json

# Phase 5: Detect conflicts
python atools/conflict_detector.py \
  --outputs outputs.json \
  --output conflicts.json

# Phase 5: Merge with verification
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --conflicts conflicts.json \
  --verify "pytest tests/" \
  --output merge_result.json
```

---

### Pattern 2: Selective Automation

**Scenario**: Moderate orchestration with 5 tasks, some parallel work

**Tool sequence**:
1. **Phase 2**: Manual decomposition (clear dependencies)
2. **Phase 3**: `agent_selector.py` → automated specialist matching
3. **Phase 5**: `merge_coordinator.py` → automated merge with verification

**Example**:
```bash
# Phase 3: Match specialists (automated)
python atools/agent_selector.py --tasks tasks.json --output assignments.json

# Phase 5: Merge (automated)
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --verify "pytest tests/"
```

---

### Pattern 3: Manual Orchestration with Tool Verification

**Scenario**: Simple orchestration with 3 tasks, sequential work

**Tool sequence**:
1. **Phase 2-4**: Manual orchestration
2. **Phase 5**: `merge_coordinator.py` → verification only

**Example**:
```bash
# Phase 5: Verify merge (minimal automation)
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --verify "pytest tests/" \
  --dry-run
```

---

## Error Handling

### Common Errors and Solutions

**1. Circular Dependency Detected** (dependency_analyzer.py):
```
Error: Circular dependency detected
Cycle: ["A", "B", "C", "A"]
```

**Solution**: Review task decomposition, break cycle by:
- Removing unnecessary dependency
- Splitting tasks to break cycle
- Using interface extraction pattern

---

**2. Anti-Pattern Detected** (agent_selector.py):
```
Warning: Domain mismatch - data-profiler assigned to frontend work
```

**Solution**: Review specialist assignment:
- Choose alternative specialist
- Adjust task domain classification
- Split task to match specialist domains

---

**3. Critical Conflict Detected** (conflict_detector.py):
```
Error: Critical schema conflict
Task 1 drops column, Task 2 uses it
```

**Solution**: Resolve conflict before merge:
- Serialize tasks (execute in order)
- Remove dependency on dropped column
- Adjust schema migration strategy

---

**4. Verification Failed** (merge_coordinator.py):
```
Error: Verification failed
Tests: 12 passed, 3 failed
```

**Solution**: Investigate test failures:
- Review merged code for integration issues
- Check for semantic conflicts not detected
- Run rollback if enabled
- Fix issues and re-merge

---

## Best Practices

### DO:
- **Use tools for complex orchestrations** (>5 tasks, multiple specialists)
- **Chain tools in pipeline** (dependency → assignment → conflict → merge)
- **Verify tool outputs** (review confidence scores, conflict reports)
- **Enable verbose mode** when debugging tool issues
- **Use dry-run** before actual merge to preview results

### DON'T:
- **Over-automate simple tasks** (1-3 tasks, single specialist)
- **Trust tools blindly** (always review recommendations)
- **Skip manual validation** (tools accelerate, don't replace judgment)
- **Ignore low confidence** (< 0.7 indicates uncertainty, review manually)
- **Proceed with critical conflicts** (resolve before merging)

---

## Tool Integration Example

**Complete orchestration workflow using all tools**:

```bash
#!/bin/bash
# Full orchestration automation pipeline

# Phase 2: Decomposition
echo "Phase 2: Analyzing dependencies..."
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json \
  --parallel-levels \
  --critical-path \
  --output analysis.json

# Phase 3: Delegation
echo "Phase 3: Matching specialists..."
python atools/agent_selector.py \
  --tasks tasks.json \
  --context context.json \
  --output assignments.json

# Phase 4: Coordination (manual - specialists execute)
echo "Phase 4: Coordinating specialist work..."
# ... specialists complete their tasks ...

# Phase 5: Integration
echo "Phase 5: Detecting conflicts..."
python atools/conflict_detector.py \
  --outputs outputs.json \
  --report conflicts_report.md \
  --output conflicts.json

echo "Phase 5: Merging outputs..."
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --conflicts conflicts.json \
  --strategy topological \
  --verify "pytest tests/" \
  --rollback-on-failure \
  --verbose \
  --output merge_result.json

echo "Orchestration complete!"
```

---

**These tools accelerate orchestration without replacing the Senior Engineering Manager's judgment. Use strategically where automation adds value.**

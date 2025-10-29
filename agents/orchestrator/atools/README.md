# Orchestrator Tools (atools/)

**Purpose**: Automation scripts for orchestration tasks

---

## Tools Overview

### 1. agent_selector.py - Specialist Matching

**Purpose**: Match tasks to appropriate specialist cognitive models

**Usage**:
```bash
# Match single task
python atools/agent_selector.py --task "Implement JWT authentication" --context context.json

# Match multiple tasks
python atools/agent_selector.py --tasks tasks.json --context context.json

# Interactive mode
python atools/agent_selector.py --interactive
```

**Input Format (tasks.json)**:
```json
{
  "tasks": [
    {
      "id": "task_1",
      "description": "Implement JWT authentication for /auth/login endpoint",
      "domain": "backend",
      "requirements": ["code implementation", "testing"],
      "outputs_needed": ["code files", "tests"]
    },
    {
      "id": "task_2",
      "description": "Review authentication implementation for security issues",
      "domain": "security",
      "requirements": ["security audit"],
      "outputs_needed": ["review report"]
    }
  ]
}
```

**Output Format**:
```json
{
  "assignments": [
    {
      "task_id": "task_1",
      "specialist": "code-generator",
      "confidence": 0.95,
      "rationale": {
        "domain_fit": "Backend implementation matches code-generator expertise",
        "cognitive_process": "TDD workflow aligns with testing requirements",
        "output_format": "Produces code files and tests as needed",
        "self_verification": "Can run tests to verify implementation"
      }
    },
    {
      "task_id": "task_2",
      "specialist": "code-reviewer",
      "confidence": 0.98,
      "rationale": {
        "domain_fit": "Security audit matches code-reviewer expertise",
        "cognitive_process": "Production auditor mental model aligned",
        "output_format": "Produces review reports as needed",
        "self_verification": "Can verify security criteria independently"
      }
    }
  ]
}
```

**Features**:
- Domain fit assessment
- Cognitive model matching
- Output format verification
- Confidence scoring
- Anti-pattern detection
- Alternative suggestions (if primary match low confidence)

---

### 2. dependency_analyzer.py - Task Ordering

**Purpose**: Analyze task dependencies and determine execution order

**Usage**:
```bash
# Analyze dependencies
python atools/dependency_analyzer.py --tasks tasks.json --dependencies deps.json

# Find critical path
python atools/dependency_analyzer.py --tasks tasks.json --dependencies deps.json --critical-path

# Generate parallelization levels
python atools/dependency_analyzer.py --tasks tasks.json --dependencies deps.json --parallel-levels

# Visualize dependency graph
python atools/dependency_analyzer.py --tasks tasks.json --dependencies deps.json --visualize
```

**Input Format (deps.json)**:
```json
{
  "dependencies": {
    "task_A": [],
    "task_B": ["task_A"],
    "task_C": ["task_B"],
    "task_D": ["task_B"],
    "task_E": ["task_C", "task_D"],
    "task_F": ["task_E"]
  },
  "durations": {
    "task_A": 1.0,
    "task_B": 2.0,
    "task_C": 1.0,
    "task_D": 1.0,
    "task_E": 1.0,
    "task_F": 2.0
  }
}
```

**Output Format**:
```json
{
  "topological_order": ["task_A", "task_B", "task_C", "task_D", "task_E", "task_F"],
  "parallelization_levels": [
    ["task_A"],
    ["task_B"],
    ["task_C", "task_D"],
    ["task_E"],
    ["task_F"]
  ],
  "critical_path": {
    "path": ["task_A", "task_B", "task_C", "task_E", "task_F"],
    "total_duration": 7.0
  },
  "parallel_duration": 7.0,
  "sequential_duration": 8.0,
  "speedup": 1.14,
  "cycles_detected": false
}
```

**Features**:
- Topological sort (execution order)
- Cycle detection
- Parallelization level identification
- Critical path analysis
- Duration estimation
- Speedup calculation

---

### 3. conflict_detector.py - Conflict Detection

**Purpose**: Detect conflicts in task outputs before merging

**Usage**:
```bash
# Detect all conflicts
python atools/conflict_detector.py --outputs outputs.json

# Detect specific conflict type
python atools/conflict_detector.py --outputs outputs.json --type file
python atools/conflict_detector.py --outputs outputs.json --type semantic
python atools/conflict_detector.py --outputs outputs.json --type dependency

# Generate conflict report
python atools/conflict_detector.py --outputs outputs.json --report conflicts_report.md
```

**Input Format (outputs.json)**:
```json
{
  "task_C": {
    "modified_files": ["app/routes/auth.py"],
    "added_functions": ["login"],
    "dependencies": {"Flask": "2.3.0"},
    "api_contracts": {
      "/auth/login": {
        "method": "POST",
        "request": {"username": "str", "password": "str"},
        "response": {"access_token": "str", "refresh_token": "str"}
      }
    }
  },
  "task_D": {
    "modified_files": ["app/routes/auth.py"],
    "added_functions": ["refresh"],
    "dependencies": {"Flask": "2.3.0"},
    "api_contracts": {
      "/auth/refresh": {
        "method": "POST",
        "request": {"refresh_token": "str"},
        "response": {"access_token": "str"}
      }
    }
  }
}
```

**Output Format**:
```json
{
  "conflicts": [
    {
      "type": "file_conflict",
      "severity": "medium",
      "tasks": ["task_C", "task_D"],
      "details": {
        "file": "app/routes/auth.py",
        "conflict_type": "both_modified"
      },
      "resolution_strategies": [
        "serialize (execute C then D)",
        "partition file (auth_login.py and auth_refresh.py)",
        "careful coordination (non-overlapping regions)"
      ],
      "recommended": "serialize"
    }
  ],
  "conflict_summary": {
    "total": 1,
    "by_severity": {"critical": 0, "high": 0, "medium": 1, "low": 0},
    "by_type": {"file_conflict": 1, "semantic_conflict": 0, "dependency_conflict": 0}
  }
}
```

**Features**:
- File conflict detection (same file modified)
- Semantic conflict detection (API mismatches, logic incompatibilities)
- Dependency conflict detection (version mismatches)
- Database schema conflict detection
- Severity assessment (critical, high, medium, low)
- Resolution strategy recommendations

---

### 4. merge_coordinator.py - Integration Orchestration

**Purpose**: Coordinate merging of specialist outputs with conflict resolution

**Usage**:
```bash
# Merge all outputs
python atools/merge_coordinator.py --outputs outputs.json --strategy topological

# Merge with conflict resolution
python atools/merge_coordinator.py --outputs outputs.json --conflicts conflicts.json --resolve

# Dry run (preview merge without executing)
python atools/merge_coordinator.py --outputs outputs.json --dry-run

# Incremental merge
python atools/merge_coordinator.py --outputs outputs.json --incremental
```

**Input Format (outputs.json + conflicts.json)**:
```json
{
  "outputs": {
    "task_A": {
      "files": {
        "docs/auth-schema.md": "content..."
      },
      "status": "complete"
    },
    "task_B": {
      "files": {
        "app/auth/jwt.py": "content..."
      },
      "status": "complete"
    }
  },
  "conflicts": {
    "file_conflicts": [],
    "semantic_conflicts": [],
    "dependency_conflicts": []
  },
  "merge_strategy": "topological",
  "verification": {
    "run_tests": true,
    "test_command": "pytest tests/",
    "rollback_on_failure": true
  }
}
```

**Output Format**:
```json
{
  "merge_result": {
    "status": "success",
    "merged_tasks": ["task_A", "task_B", "task_C", "task_D", "task_E", "task_F"],
    "merge_order": ["task_A", "task_B", "task_C", "task_D", "task_E", "task_F"],
    "conflicts_resolved": 1,
    "verification": {
      "tests_passed": true,
      "test_output": "45 tests passed, 0 failed"
    },
    "rollbacks": 0,
    "duration": 42.3
  },
  "merged_files": [
    "docs/auth-schema.md",
    "app/auth/jwt.py",
    "app/routes/auth.py",
    "tests/unit/test_auth.py"
  ],
  "warnings": [],
  "errors": []
}
```

**Features**:
- Topological merge ordering
- Automatic conflict resolution (when safe)
- Manual conflict escalation (when required)
- Integration testing after merge
- Rollback on failure
- Incremental merging
- Dry-run mode (preview)
- Detailed logging

---

## Tool Integration

**Typical Workflow**:

```bash
# Step 1: Match tasks to specialists
python atools/agent_selector.py --tasks tasks.json --context context.json > assignments.json

# Step 2: Analyze dependencies
python atools/dependency_analyzer.py --tasks tasks.json --dependencies deps.json > execution_plan.json

# Step 3: [Specialists execute their tasks]

# Step 4: Detect conflicts
python atools/conflict_detector.py --outputs outputs.json > conflicts.json

# Step 5: Merge outputs
python atools/merge_coordinator.py --outputs outputs.json --conflicts conflicts.json --resolve > merge_result.json
```

---

## Error Handling

All tools follow consistent error handling:

**Exit Codes**:
- 0: Success
- 1: Invalid arguments
- 2: Input file error (missing, malformed)
- 3: Processing error (logic error, unexpected state)
- 4: Verification failure (tests failed, conflicts unresolved)

**Error Output Format**:
```json
{
  "error": {
    "code": 3,
    "message": "Circular dependency detected",
    "details": {
      "cycle": ["task_A", "task_B", "task_C", "task_A"]
    },
    "suggestion": "Review task decomposition to break circular dependency"
  }
}
```

**Logging**:
- All tools log to stderr
- Use `--verbose` flag for detailed logging
- Use `--quiet` flag to suppress non-error output

---

## Common Options

**All Tools Support**:
```bash
--help              Show help message
--version           Show version
--verbose           Detailed logging
--quiet             Suppress non-error output
--output FILE       Write output to file (default: stdout)
--format [json|yaml|text]  Output format
```

---

## Dependencies

**Python Requirements**:
```
python >= 3.8
networkx >= 2.8  # Graph operations (dependency analysis)
pyyaml >= 6.0    # YAML support
```

**Installation**:
```bash
cd /path/to/orchestrator/atools
pip install -r requirements.txt
```

---

## Testing

**Run Tool Tests**:
```bash
# Test all tools
pytest atools/tests/ -v

# Test specific tool
pytest atools/tests/test_agent_selector.py -v
pytest atools/tests/test_dependency_analyzer.py -v
pytest atools/tests/test_conflict_detector.py -v
pytest atools/tests/test_merge_coordinator.py -v
```

---

## Examples

### Example 1: Simple Workflow

```bash
# Match tasks
python atools/agent_selector.py \
  --task "Implement login endpoint" \
  --context '{"domain":"backend","tech_stack":"Flask"}' \
  --format json

# Output:
# {"specialist": "code-generator", "confidence": 0.95, ...}
```

### Example 2: Complex Dependency Analysis

```bash
# Analyze complex task dependencies
python atools/dependency_analyzer.py \
  --tasks tasks.json \
  --dependencies deps.json \
  --critical-path \
  --parallel-levels \
  --visualize dependency_graph.png

# Output:
# Critical path: A → B → C → E → F (7 hours)
# Parallelization: Can reduce to 7 hours (from 8 hours sequential)
# Graph saved to: dependency_graph.png
```

### Example 3: Conflict Detection and Resolution

```bash
# Detect conflicts
python atools/conflict_detector.py \
  --outputs outputs.json \
  --report conflicts_report.md

# Merge with resolution
python atools/merge_coordinator.py \
  --outputs outputs.json \
  --conflicts conflicts.json \
  --resolve \
  --verify "pytest tests/" \
  --rollback-on-failure

# Output:
# Merge completed successfully
# 1 file conflict resolved (serialization)
# All tests passed (45/45)
```

---

## Maintenance

**Adding New Specialists**:
1. Update `agent_selector.py` specialist definitions
2. Add cognitive model matching logic
3. Update `delegation/specialist-inventory.md`

**Adding Conflict Types**:
1. Update `conflict_detector.py` detection logic
2. Add resolution strategies
3. Update `integration/conflict-detection.md`

---

## Troubleshooting

**Common Issues**:

**Issue**: "Circular dependency detected"
```bash
# Solution: Review task decomposition
python atools/dependency_analyzer.py --tasks tasks.json --dependencies deps.json --debug
# Fix circular dependency in deps.json
```

**Issue**: "No specialist matches task"
```bash
# Solution: Decompose task or add new specialist
python atools/agent_selector.py --task "..." --verbose
# Check domain fit and decompose if needed
```

**Issue**: "Merge conflict unresolved"
```bash
# Solution: Review conflict resolution strategies
python atools/conflict_detector.py --outputs outputs.json --verbose
python atools/merge_coordinator.py --outputs outputs.json --dry-run
# Apply recommended resolution strategy
```

---

## Summary

**Four Core Tools**:
1. **agent_selector.py**: Match tasks to specialists
2. **dependency_analyzer.py**: Analyze dependencies and ordering
3. **conflict_detector.py**: Detect integration conflicts
4. **merge_coordinator.py**: Orchestrate merging with verification

**Workflow**: Select → Analyze → Execute → Detect → Merge

**Benefits**:
- Automated specialist matching
- Optimal task ordering
- Early conflict detection
- Safe merging with verification
- Comprehensive error handling

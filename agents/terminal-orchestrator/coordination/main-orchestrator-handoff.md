# Main Orchestrator Handoff Protocol

**Purpose**: Document the interface between Main Orchestrator (Phase 4: Coordination) and Terminal Orchestrator (parallel execution engine).

**When to Use**: Main Orchestrator delegates parallel execution to Terminal Orchestrator after task decomposition and specialist assignment.

**Bidirectional Reference**: See also `orchestrator/coordination/terminal-orchestrator-integration.md` for Main Orchestrator's perspective on this integration.

---

## Handoff Flow

```
Main Orchestrator (Phase 1-3: Plan)
    ↓
    Creates execution request
    ↓
Terminal Orchestrator (Receives request)
    ↓
    Phase 1: Setup tmux sessions
    Phase 2: Execute agents in parallel
    Phase 3: Validate outputs
    Phase 4: Merge and verify
    ↓
    Returns execution report
    ↓
Main Orchestrator (Phase 5: Verify coherence)
    ↓
    Integrates with user conversation
```

---

## Input Format (Main Orchestrator → Terminal Orchestrator)

### Execution Request Structure

```json
{
  "execution_id": "exec-20251030-1430-abc123",
  "request_timestamp": "2025-10-30T14:30:00Z",
  "workspace_root": "/tmp/orchestration/exec-20251030-1430-abc123",
  "agents": [
    {
      "agent_name": "code-generator",
      "agent_path": "/Users/.../llm-playground/agent/code-generator",
      "task": {
        "description": "Implement user authentication with JWT tokens",
        "inputs": {
          "requirements": "/tmp/orchestration/requirements/auth-spec.md",
          "codebase": "/tmp/orchestration/codebase"
        },
        "outputs": {
          "code": "/tmp/orchestration/outputs/code-generator/code",
          "tests": "/tmp/orchestration/outputs/code-generator/tests",
          "ctxpack": "/tmp/orchestration/outputs/code-generator/output.ctxp"
        },
        "success_criteria": {
          "tests_pass": true,
          "no_lint_errors": true,
          "coverage": 80
        }
      },
      "dependencies": [],
      "timeout": 3600
    },
    {
      "agent_name": "code-reviewer",
      "agent_path": "/Users/.../llm-playground/agent/code-reviewer",
      "task": {
        "description": "Security review of authentication implementation",
        "inputs": {
          "code": "/tmp/orchestration/outputs/code-generator/code"
        },
        "outputs": {
          "review": "/tmp/orchestration/outputs/code-reviewer/review.md",
          "ctxpack": "/tmp/orchestration/outputs/code-reviewer/output.ctxp"
        },
        "success_criteria": {
          "no_critical_issues": true,
          "security_checklist_complete": true
        }
      },
      "dependencies": ["code-generator"],
      "timeout": 1800
    }
  ],
  "merge_strategy": {
    "type": "ctxpack_union",
    "conflict_resolution": "manual_review",
    "validation": {
      "semantic_consistency": true,
      "schema_validation": true
    }
  },
  "execution_options": {
    "parallel_limit": 4,
    "retry_on_failure": true,
    "max_retries": 2,
    "checkpoint_enabled": true,
    "log_level": "info"
  }
}
```

### Field Descriptions

**execution_id**: Unique identifier for this execution batch
**workspace_root**: Base directory for all agent executions
**agents**: Array of agent execution specs
- **agent_name**: Agent identifier (matches directory name)
- **agent_path**: Full path to agent directory
- **task**: Task specification
  - **description**: Human-readable task summary
  - **inputs**: Map of input file/directory paths
  - **outputs**: Map of expected output paths
  - **success_criteria**: Required conditions for success
- **dependencies**: List of agent names this agent depends on
- **timeout**: Max execution time in seconds

**merge_strategy**: How to integrate outputs
- **type**: "ctxpack_union", "file_merge", "report_aggregation"
- **conflict_resolution**: "auto", "manual_review", "fail_on_conflict"
- **validation**: Post-merge validation rules

**execution_options**: Execution behavior
- **parallel_limit**: Max concurrent agents (respects dependencies)
- **retry_on_failure**: Auto-retry failed agents
- **checkpoint_enabled**: Create pre-execution snapshot for rollback

---

## Output Format (Terminal Orchestrator → Main Orchestrator)

### Execution Report Structure

```json
{
  "execution_id": "exec-20251030-1430-abc123",
  "status": "success",
  "start_timestamp": "2025-10-30T14:30:05Z",
  "end_timestamp": "2025-10-30T14:45:32Z",
  "duration_seconds": 927,
  "agents": [
    {
      "agent_name": "code-generator",
      "status": "success",
      "tmux_session": "code-generator-20251030-1430",
      "start_time": "2025-10-30T14:30:05Z",
      "end_time": "2025-10-30T14:42:18Z",
      "duration_seconds": 733,
      "exit_code": 0,
      "outputs_produced": {
        "code": "/tmp/orchestration/outputs/code-generator/code",
        "tests": "/tmp/orchestration/outputs/code-generator/tests",
        "ctxpack": "/tmp/orchestration/outputs/code-generator/output.ctxp"
      },
      "success_criteria_met": {
        "tests_pass": true,
        "no_lint_errors": true,
        "coverage": 85
      },
      "logs": {
        "stdout": "/tmp/orchestration/logs/code-generator/stdout.log",
        "stderr": "/tmp/orchestration/logs/code-generator/stderr.log"
      },
      "metrics": {
        "lines_of_code": 1247,
        "test_count": 42,
        "peak_memory_mb": 512
      }
    },
    {
      "agent_name": "code-reviewer",
      "status": "success",
      "tmux_session": "code-reviewer-20251030-1442",
      "start_time": "2025-10-30T14:42:25Z",
      "end_time": "2025-10-30T14:45:32Z",
      "duration_seconds": 187,
      "exit_code": 0,
      "outputs_produced": {
        "review": "/tmp/orchestration/outputs/code-reviewer/review.md",
        "ctxpack": "/tmp/orchestration/outputs/code-reviewer/output.ctxp"
      },
      "success_criteria_met": {
        "no_critical_issues": true,
        "security_checklist_complete": true
      },
      "logs": {
        "stdout": "/tmp/orchestration/logs/code-reviewer/stdout.log",
        "stderr": "/tmp/orchestration/logs/code-reviewer/stderr.log"
      }
    }
  ],
  "merge_result": {
    "status": "success",
    "merged_ctxpack": "/tmp/orchestration/merged/integrated.ctxp",
    "conflicts_detected": 0,
    "conflicts_resolved": 0,
    "validation_passed": true,
    "merged_files": [
      "/tmp/orchestration/merged/code",
      "/tmp/orchestration/merged/tests",
      "/tmp/orchestration/merged/review.md"
    ]
  },
  "errors": [],
  "warnings": [
    {
      "agent": "code-generator",
      "message": "High memory usage detected (512MB peak)",
      "severity": "low"
    }
  ]
}
```

### Status Codes

**Execution-level status**:
- `success`: All agents completed, outputs verified, merge successful
- `partial_success`: Some agents succeeded, some failed
- `failure`: All agents failed or merge failed
- `timeout`: Execution exceeded overall time limit
- `cancelled`: Execution terminated early

**Agent-level status**:
- `success`: Agent completed, outputs valid, success criteria met
- `failure`: Agent failed (non-zero exit code or invalid output)
- `timeout`: Agent exceeded time limit
- `skipped`: Agent not executed (dependency failed)

---

## Handoff Protocol

### 1. Pre-Execution Handoff

**Main Orchestrator responsibilities**:
1. Create execution request JSON
2. Ensure workspace_root directory exists
3. Place input files in specified locations
4. Validate agent paths exist
5. Check dependency graph for cycles

**Terminal Orchestrator responsibilities**:
1. Validate execution request schema
2. Check all agent paths exist
3. Verify workspace_root is accessible
4. Validate dependency graph (topological sort)
5. Create checkpoint if enabled

**Handoff point**: Main Orchestrator invokes Terminal Orchestrator with execution request

---

### 2. During Execution

**Terminal Orchestrator autonomy**:
- Terminal Orchestrator runs independently
- No callbacks to Main Orchestrator during execution
- All progress tracked in logs and tmux sessions
- Main Orchestrator can monitor logs if desired

**Monitoring (optional)**:
- Main Orchestrator can read logs: `/tmp/orchestration/logs/<agent>/stdout.log`
- Main Orchestrator can attach to tmux: `tmux attach -t <session-name>`
- Terminal Orchestrator updates status file: `/tmp/orchestration/status.json`

---

### 3. Post-Execution Handoff

**Terminal Orchestrator responsibilities**:
1. Ensure all tmux sessions terminated
2. Validate all outputs produced
3. Execute merge strategy
4. Generate execution report JSON
5. Write report to: `/tmp/orchestration/execution_report.json`

**Main Orchestrator responsibilities**:
1. Read execution report JSON
2. Verify report schema
3. Check execution status
4. Load merged outputs
5. Integrate into conversation context

**Handoff point**: Terminal Orchestrator writes execution report, Main Orchestrator reads it

---

## Error Handling

### Agent Execution Failures

**If agent fails**:
1. Terminal Orchestrator captures error logs
2. Adds failure details to execution report
3. If `retry_on_failure: true`, retries agent up to `max_retries`
4. If retries exhausted, marks agent as failed
5. Dependent agents are skipped
6. Execution continues for independent agents

**Escalation to Main Orchestrator**:
- Execution report includes all failures
- Main Orchestrator decides whether to retry entire execution
- Main Orchestrator can modify request and re-invoke Terminal Orchestrator

---

### Merge Failures

**If merge fails** (conflicts detected):
1. Terminal Orchestrator stops merge
2. If `conflict_resolution: "manual_review"`:
   - Writes conflict report to `/tmp/orchestration/conflicts.json`
   - Execution report status: `failure`
   - Main Orchestrator reviews conflicts manually
3. If `conflict_resolution: "fail_on_conflict"`:
   - Execution report status: `failure`
   - No partial merge produced
4. If `conflict_resolution: "auto"`:
   - Terminal Orchestrator attempts automatic resolution
   - If auto-resolution fails, escalates to manual

---

### Timeout Handling

**If execution exceeds overall timeout**:
1. Terminal Orchestrator terminates all running tmux sessions
2. Saves current outputs (partial)
3. Execution report status: `timeout`
4. Main Orchestrator can review partial outputs and retry

**If individual agent exceeds timeout**:
1. Terminal Orchestrator kills tmux session for that agent
2. Agent status: `timeout`
3. Dependent agents are skipped
4. Execution continues for independent agents

---

## Filesystem Layout

```
/tmp/orchestration/exec-20251030-1430-abc123/
├── inputs/                          # Input files from Main Orchestrator
│   ├── requirements/
│   │   └── auth-spec.md
│   └── codebase/
├── outputs/                         # Agent outputs
│   ├── code-generator/
│   │   ├── code/
│   │   ├── tests/
│   │   └── output.ctxp
│   └── code-reviewer/
│       ├── review.md
│       └── output.ctxp
├── logs/                            # Execution logs
│   ├── code-generator/
│   │   ├── stdout.log
│   │   └── stderr.log
│   └── code-reviewer/
│       ├── stdout.log
│       └── stderr.log
├── tmux/                            # Tmux session artifacts
│   ├── code-generator-20251030-1430.log
│   └── code-reviewer-20251030-1442.log
├── merged/                          # Merged outputs
│   ├── integrated.ctxp
│   ├── code/
│   ├── tests/
│   └── review.md
├── checkpoint/                      # Pre-execution snapshot (if enabled)
│   └── checkpoint.tar.gz
├── execution_request.json           # Input from Main Orchestrator
├── execution_report.json            # Output to Main Orchestrator
├── status.json                      # Real-time status (updated during execution)
└── conflicts.json                   # Conflict report (if merge fails)
```

---

## Example Invocation

### Python API (Programmatic)

```python
from terminal_orchestrator.atools import orchestrate_parallel

execution_request = {
    "execution_id": "exec-001",
    "workspace_root": "/tmp/orchestration/exec-001",
    "agents": [
        {
            "agent_name": "code-generator",
            "agent_path": "/path/to/agent/code-generator",
            "task": {...},
            "dependencies": [],
            "timeout": 3600
        }
    ],
    "merge_strategy": {"type": "ctxpack_union"},
    "execution_options": {"parallel_limit": 4}
}

# Execute
report = orchestrate_parallel(execution_request)

# Check result
if report["status"] == "success":
    print(f"Merged output: {report['merge_result']['merged_ctxpack']}")
else:
    print(f"Failures: {[a for a in report['agents'] if a['status'] != 'success']}")
```

### File-Based (Structural)

```bash
# Main Orchestrator writes request
echo "$EXECUTION_REQUEST_JSON" > /tmp/orchestration/exec-001/execution_request.json

# Invoke Terminal Orchestrator
python /path/to/terminal-orchestrator/atools/orchestrate_parallel.py \
    --request /tmp/orchestration/exec-001/execution_request.json \
    --output /tmp/orchestration/exec-001/execution_report.json

# Main Orchestrator reads report
cat /tmp/orchestration/exec-001/execution_report.json
```

---

## Integration Points

### Main Orchestrator → Terminal Orchestrator

**When to delegate**:
- Main Orchestrator has completed Phase 1-3 (task decomposition, specialist assignment)
- Multiple agents can run in parallel (dependency graph allows it)
- Execution time is significant (>1 minute per agent)

**Main Orchestrator Phase 4**:
```markdown
### Phase 4: Coordination

1. Create execution request (map agent assignments → execution spec)
2. Invoke Terminal Orchestrator (via Python API or file-based)
3. Wait for execution report
4. Load merged outputs
5. Proceed to Phase 5 (context coherence verification)
```

### Terminal Orchestrator → Main Orchestrator

**What to return**:
- Execution report (status, agent results, merge result)
- Merged .ctxpack (semantic graph of all agent outputs)
- Error details (if any failures occurred)
- Performance metrics (duration, resource usage)

**Main Orchestrator Phase 5**:
```markdown
### Phase 5: Integration Verification

1. Load execution report from Terminal Orchestrator
2. Verify semantic coherence of merged outputs
3. Check for missing information or inconsistencies
4. If issues found, re-invoke agents with refinements
5. Integrate final outputs into user conversation
```

---

## Summary

**Handoff Contract**:
- **Input**: JSON execution request with agents, tasks, dependencies, merge strategy
- **Output**: JSON execution report with status, outputs, merge result, errors
- **Interface**: File-based or Python API
- **Autonomy**: Terminal Orchestrator runs independently during execution
- **Error Handling**: All failures reported, Main Orchestrator decides retry strategy

**Responsibilities**:
- **Main Orchestrator**: Plan, assign, integrate
- **Terminal Orchestrator**: Execute, monitor, validate, merge

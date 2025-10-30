---
name: terminal-handoff-protocol
description: Contract between Main Orchestrator and Terminal-Orchestrator for parallel execution requests and result returns.
---

# Main Orchestrator ↔ Terminal-Orchestrator Handoff

This document defines the minimal contract for delegating parallel execution.

## Inputs from Main Orchestrator
- Assignments file: `assignments.json`
  - tasks: [{ id, agent, context_path, dependencies: [ids] }]
  - environment: { workspace_dir, env_vars[], resource_limits? }
  - success_criteria: { required_artifacts[], tests_cmd? }
- Execution mode: { dry_run?: bool, verify?: bool }

## Terminal-Orchestrator Responsibilities
1. Create isolated tmux sessions per task/agent
2. Execute agents in appropriate order respecting dependencies
3. Stream logs to `logs/<agent>-<ts>.out` and `logs/<agent>-<ts>.err`
4. Emit per-task status: `status/<task_id>.{running|success|failed}`
5. Capture artifacts to `artifacts/<task_id>/`
6. Validate outputs against `success_criteria`
7. Detect conflicts prior to merge; on conflict, prefer safe halt with report
8. Merge outputs (topological) when validation passes
9. Return a structured report

## Output to Main Orchestrator
`execution_report.json`:
```json
{
  "summary": {
    "completed": true,
    "failed_tasks": [],
    "validation": "passed",
    "conflicts": []
  },
  "tasks": [
    {
      "id": "A",
      "agent": "code-generator",
      "status": "success",
      "logs": {
        "stdout": "logs/code-generator-20251030.out",
        "stderr": "logs/code-generator-20251030.err"
      },
      "artifacts": ["artifacts/A/"]
    }
  ],
  "merge": {
    "strategy": "topological",
    "result": "success",
    "conflicts": []
  }
}
```

## Failure Handling
- If any task fails:
  - Stop dependent tasks
  - Collect logs and artifacts
  - Return `execution_report.json` with `completed=false` and failed task details
- If merge/validation fails:
  - Do not merge; attempt rollback if partial changes applied
  - Return detailed conflict/validation report

## Security & Safety
- Do not execute arbitrary shell unless explicitly provided via assignments/context
- Redact secrets in logs
- Keep sessions until report is delivered

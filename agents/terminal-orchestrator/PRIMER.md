---
name: terminal-orchestrator-primer
description: High-signal overview for executing multiple specialist agents in parallel via tmux isolation, monitoring, output validation, conflict detection, and merge verification.
---

# Terminal-Orchestrator Primer

Default entrypoint for terminal execution. Keep tokens lean; load detailed docs only when necessary.

## Purpose
Execute assigned agents in parallel, ensure isolation, validate outputs, and deliver a verified merged result back to the main orchestrator.

## Phases
1) Environment Setup (tmux sessions per agent)
2) Execution Monitoring (status, failures, resources)
3) Output Verification (format/schema, success criteria)
4) Merge Strategy (conflict detection, ctxpack merge, rollback on failure)

## Minimal Protocol
- Create `<agent>-<timestamp>` tmux sessions, detached
- Stream output to per-agent logs
- Mark completion with explicit status files or exit codes
- Validate outputs against expected schemas
- Detect conflicts before attempting merge
- Merge in topological order; prepare rollback

## Expected Output Pattern
```
OK Parallel execution complete

Agents:
- code-generator: SUCCESS (log: logs/code-generator-YYYYMMDD.out)
- code-reviewer: SUCCESS
- data-profiler: SUCCESS

Validation: PASSED
Conflicts: NONE
Merge: SUCCESS
Return: execution_report.json
```

## Safety
- Never kill sessions without collecting logs
- If validation fails, do not merge—return failure with artifacts
- Prefer dry-run merges when uncertain

## On-Demand Loads
- tmux/session-management.md
- monitoring/progress-tracking.md
- verification/output-validation.md
- merge/conflict-detection.md, merge/merge-strategies.md

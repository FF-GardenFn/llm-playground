---
description: Execute multiple specialist agents in parallel with tmux isolation, monitoring, validation, and merge
allowed-tools: Read, Write, Bash, TodoWrite
argument-hint: [agent1,agent2,...]
---

## Orchestrate Parallel Execution

**Usage**: `/orchestrate-parallel code-generator,code-reviewer,data-profiler`

**Purpose**: Execute multiple specialist agents in parallel with full isolation, monitoring, output validation, and merge verification.

**Auto-loads**: Main orchestrator handoff protocol and execution workflow

---

## What This Command Does

1. **Creates isolated tmux sessions** for each agent
2. **Executes agents in parallel** (respecting dependencies)
3. **Monitors execution** with real-time progress tracking
4. **Validates outputs** (schema, format, success criteria)
5. **Detects conflicts** (file, semantic, dependency, schema)
6. **Merges outputs** (ctxpack union, conflict resolution)
7. **Returns integrated result** to orchestrator

---

## Prerequisites

- Execution request from Main Orchestrator (Phase 4: Coordination)
- Agent assignments with tasks and dependencies
- Workspace directory prepared

---

## Workflow

{{load: ${CLAUDE_PLUGIN_ROOT}/coordination/main-orchestrator-handoff.md}}

---

## Example Usage

```bash
# Orchestrator invokes terminal-orchestrator
/orchestrate-parallel code-generator,code-reviewer,data-profiler

# Terminal-orchestrator:
# 1. Loads handoff protocol
# 2. Creates tmux sessions
# 3. Executes agents
# 4. Validates outputs
# 5. Merges results
# 6. Returns execution report
```

---

## Output

Returns execution report with:
- Agent execution statuses (success/failure)
- Validated outputs (all agents)
- Merged ctxpack (integrated semantic graph)
- Conflicts detected/resolved
- Performance metrics

---

## Gate

Cannot return to orchestrator until:
- [ ] All agents complete or fail explicitly
- [ ] All outputs validated
- [ ] Conflicts resolved or escalated
- [ ] Merge successful or rollback complete

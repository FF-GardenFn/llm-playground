---
description: Monitor specialist progress and detect blockers (Orchestration Phase 4)
allowed-tools: Read, Write, TodoWrite
argument-hint: [--check-status]
---

# Coordination Command

Execute Phase 4 orchestration: monitor completion (not progress), detect early failures, identify bottlenecks.

## What this does

1. **Tracks completion** (not progress) to minimize coordination overhead
2. **Detects early failures** (fail fast pattern)
3. **Identifies bottlenecks** (resource conflicts, blocking dependencies)
4. **Adapts plan if needed** (reallocation, timeline adjustment)
5. **Avoids micromanagement** (trust specialists, intervene only when needed)

## Usage

```bash
# Check status of all tasks
/coordinate

# Check specific task
/coordinate --check-status task-B

# Force status update
/coordinate --refresh
```

## Your Task

1. **Load coordination workflow**: Read `coordination/progress-tracking.md`
2. **Track completion**: Check which tasks finished, which running, which blocked
3. **Detect failures**: Identify tasks that failed or are stuck
4. **Identify bottlenecks**: Check for blocking dependencies or resource conflicts
5. **Adapt if needed**: Reallocate resources, adjust timeline
6. **Complete gate**: `coordination/GATE-ALL-COMPLETE.md`
7. **Report**: Completion status, any blockers, adaptation decisions

## Expected Output

```
✓ Coordination status

Completed Tasks:
✓ Task A: Auth schema designed (1h 05m)
✓ Task B: JWT logic implemented (1h 52m)
✓ Task C: Login endpoint created (1h 28m)
✓ Task D: Refresh endpoint created (58m)

In Progress:
→ Task E: Auth middleware (estimated completion: 15 minutes)

Queued:
- Task F: Tests (depends on E, will start automatically)
- Task G: Security review (depends on F)

Blockers Detected: NONE

Resource Conflicts: NONE

Bottleneck Analysis:
- Critical path progressing on schedule
- No dependencies blocking parallel work
- All specialists working autonomously

Adaptation Decisions: NONE NEEDED
- All tasks completing within estimates
- No failures requiring reallocation

→ Recommend: Wait for Task E completion, then /integrate
```

## Coordination Principles

**Minimal Overhead**:
- Track completion, not progress (avoid micromanagement)
- Trust specialist expertise
- Intervene only when needed (failures, conflicts)

**Fail Fast**:
- Detect failures early
- Isolate failed tasks (don't let them cascade)
- Replan around failures

## Gate

**Cannot proceed to /integrate without**:
- [ ] All tasks completed or explicitly failed
- [ ] Blockers resolved
- [ ] Dependencies satisfied

---
description: Match tasks to appropriate specialist cognitive models (Orchestration Phase 3)
allowed-tools: Bash(python atools/agent_selector.py:*), Read, Write, TodoWrite, Task
argument-hint: [--task-id id]
---

# Delegation Command

Execute Phase 3 orchestration: match tasks to specialists, provide context, launch parallel execution.

## What this does

1. **Matches tasks to specialists** using cognitive model alignment
2. **Uses agent_selector.py** for automated matching with confidence scoring
3. **Provides context** (scope, success criteria, boundaries)
4. **Launches specialists** in parallel via Task tool
5. **Avoids anti-patterns** (domain mismatch, role confusion)

## Usage

```bash
# Auto-match all tasks to specialists
/delegate

# Match specific task
/delegate --task-id B

# Review specialist inventory first
/delegate --list-specialists
```

## Your Task

1. **Load delegation workflow**: Read `delegation/specialist-matching.md`
2. **Review specialist inventory**: Read `delegation/specialist-inventory.md`
3. **Match tasks to specialists**: Use `atools/agent_selector.py` for automation
4. **Provide context**: Read `delegation/context-provision.md`
5. **Launch specialists**: Use Task tool with matched specialist
6. **Complete gate**: `delegation/GATE-SPECIALISTS-ASSIGNED.md`
7. **Report**: Task assignments with rationale, confidence scores

## Expected Output

```
✓ Delegation complete

Specialist Assignments:

Task A (Design auth schema):
→ Specialist: code-generator
→ Confidence: 0.92
→ Rationale: Exact domain match (backend), test-first workflow
→ Context provided: Flask structure, PostgreSQL, bcrypt requirement
→ Status: Launched via Task tool

Tasks B-F (JWT logic, endpoints, middleware, tests):
→ Specialist: code-generator
→ Confidence: 0.95
→ Rationale: TDD practitioner, incremental implementation
→ Context provided: Auth schema from Task A, existing patterns
→ Status: Launched in parallel (B first, then C/D/E, then F)

Task G (Security review):
→ Specialist: code-reviewer
→ Confidence: 0.98
→ Rationale: Security expertise, vulnerability detection
→ Context provided: Complete implementation from Task F
→ Status: Will launch after Task F completes

Parallelization:
- Task A: Running (ETA 1hr)
- Tasks B-F: Queued (will start after A completes)
- Task G: Queued (will start after F completes)

→ Recommend: /coordinate to monitor progress
```

## Gate

**Cannot proceed to /coordinate without**:
- [ ] Every task assigned to specialist
- [ ] Assignment rationale documented
- [ ] Context sufficient for autonomous work
- [ ] Integration points specified

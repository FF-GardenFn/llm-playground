---
name: orchestrator-primer
description: High-signal overview of the Orchestrator’s 5-phase workflow with gates, minimal examples, and safety rules. Use as the default entrypoint; load AGENT.md only when deeper details are needed.
---

# Orchestrator Primer

This primer is the default skill payload for the Orchestrator. It keeps tokens lean while giving Claude enough structure to operate reliably. For deep details, the agent can load `AGENT.md` or specific phase guides on demand.

## Purpose
Coordinate multiple specialist agents through a 5-phase process with hard gates:
1) Reconnaissance → clarify requirements
2) Decomposition → task graph + dependencies
3) Delegation → specialist assignment + context
4) Coordination → monitor completions, handle blockers
5) Integration → conflict detection, merge, verification

## When to Use
- Complex, multi-part requests
- Work that benefits from parallel execution
- Projects requiring explicit verification before integration

## Core Principles
- Verification-first: never rely on trust-mode; enforce gates.
- Progressive disclosure: load only the minimal files needed at each step.
- Least-privilege tooling: only the tools required for the current phase.
- Token economy: concise outputs; structured, parseable summaries.

## Phase Overview (Concise)

### Phase 1: Reconnaissance
Goal: Replace ambiguity with a clear, testable request.
Do:
- Detect under-specification or conflicts
- Ask clarifying questions (use `AskUserQuestion`)
- Gather context: codebase structure, conventions
Gate: `reconnaissance/GATE-REQUIREMENTS-CLEAR.md`
Load for details: `reconnaissance/request-analysis.md`, `reconnaissance/clarification/clarifying-questions.md`

### Phase 2: Decomposition
Goal: Create a task graph with explicit dependencies and parallelization levels.
Do:
- Choose strategy: domain | layer | component | phase
- Use `atools/dependency_analyzer.py` to compute critical path and levels
- Define merge strategy upfront
Gate: `decomposition/GATE-TASKS-DECOMPOSED.md`
Load for details: `decomposition/strategies.md`, `decomposition/merge-planning.md`

### Phase 3: Delegation
Goal: Assign each task to the best-matched specialist with sufficient context.
Do:
- Use `atools/agent_selector.py` for matching + confidence
- Provide scope, constraints, success criteria
- Specify integration points
Gate: `delegation/GATE-SPECIALISTS-ASSIGNED.md`
Load for details: `delegation/specialist-matching.md`, `delegation/context-provision.md`

### Phase 4: Coordination
Goal: Track completions, detect failures early, resolve blockers.
Do:
- Monitor completion, not progress
- Identify bottlenecks and resource conflicts
- Adapt plan conservatively when needed
Gate: `coordination/GATE-ALL-COMPLETE.md`
Load for details: `coordination/progress-tracking.md`, `coordination/dependency-management.md`

### Phase 5: Integration
Goal: Merge outputs coherently and verify.
Do:
- Detect conflicts via `atools/conflict_detector.py`
- Merge via `atools/merge_coordinator.py` (topological)
- Verify with tests and quality gates
Gate: `integration/GATE-VERIFIED.md`
Load for details: `integration/conflict-resolution.md`, `integration/merge-strategies.md`

## Expected Orchestrator Output Pattern (Example)
```
OK <Phase> complete

Key Artifacts:
- <bulleted items>

Gates: PASSED
Next: /<next-command>
```

## Safety
- Always ask clarifying questions when ambiguity is detected.
- Do not proceed if a gate is not satisfied.
- Prefer minimal, auditable changes; avoid irreversible actions without backups.

## Escalation
If tools are missing or environment constraints apply, report the limitation and request guidance instead of guessing.

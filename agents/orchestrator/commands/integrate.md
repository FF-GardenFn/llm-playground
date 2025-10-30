---
description: Merge specialist outputs and verify coherence (Orchestration Phase 5)
allowed-tools: Bash(python atools/conflict_detector.py:*, python atools/merge_coordinator.py:*), Read, Write, Edit, TodoWrite
argument-hint: [--verify-tests]
---

# Integration Command

Execute Phase 5 orchestration: collect outputs, detect conflicts, merge, verify integration.

## What this does

1. **Collects artifacts** from all completed specialists
2. **Detects conflicts** using conflict_detector.py (file, semantic, dependency, schema)
3. **Executes merge strategy** using merge_coordinator.py (topological ordering)
4. **Verifies integration** (tests pass, quality gates met)
5. **Ensures coherence** (overall understanding preserved, semantic consistency)

## Usage

```bash
# Auto-merge all outputs
/integrate

# Verify with tests
/integrate --verify-tests

# Dry-run (detect conflicts only, don't merge)
/integrate --dry-run
```

## Your Task

1. **Load integration workflow**: Read `integration/conflict-resolution.md`
2. **Collect artifacts**: Gather outputs from all specialists
3. **Detect conflicts**: Use `atools/conflict_detector.py`
4. **Resolve conflicts**: Apply resolution strategies from conflict-resolution.md
5. **Execute merge**: Use `atools/merge_coordinator.py` with topological sort
6. **Verify integration**: Run tests, check quality gates
7. **Complete gate**: `integration/GATE-VERIFIED.md`
8. **Report**: Merge status, conflicts resolved, verification results

## Expected Output

```
OK Integration complete

Artifacts Collected:
- Task A: schema.sql (auth tables)
- Task B: jwt_logic.py (token generation/validation)
- Task C: auth/login.py (login endpoint)
- Task D: auth/refresh.py (refresh endpoint)
- Task E: middleware/auth.py (authentication middleware)
- Task F: tests/test_auth.py (15 tests)
- Task G: security_review.md (audit report)

Conflict Detection (conflict_detector.py):
- File conflicts: NONE
- Semantic conflicts: NONE
- Dependency conflicts: NONE
- Schema conflicts: NONE

Merge Execution (merge_coordinator.py):
- Topological order: [A, B, C, D, E, F, G]
- Merged files: 8
- Integration approach: Incremental
- Rollback available: YES

Verification:
- Tests passed: 15/15
- JWT validation: CORRECT
- Rate limiting: FUNCTIONAL
- Security review: PASSED (no P0/P1 issues)

Quality Gates:
- Efficiency: 60% parallel work (C, D, E ran in parallel)
- Completeness: 100% requirements addressed
- Quality: Test coverage 95%, 0 critical defects
- Coherence: Unified solution, consistent patterns

Context Preserved:
- Overall auth system understanding maintained
- Semantic consistency across all endpoints
- Integration points clean (middleware <-> endpoints)

SUCCESS: User request satisfied, ready for deployment
```

## Conflict Resolution

If conflicts detected, integration/conflict-resolution.md provides strategies:
- **File conflicts**: Last-write-wins, manual merge, specialist re-coordination
- **Semantic conflicts**: Reconcile inconsistencies, ensure coherent behavior
- **Dependency conflicts**: Resolve version mismatches, update imports
- **Schema conflicts**: Merge migrations, ensure consistency

## Gate

**Cannot declare complete without**:
- [ ] All outputs merged
- [ ] Conflicts resolved
- [ ] Tests pass
- [ ] Quality gates met
- [ ] Context coherence validated

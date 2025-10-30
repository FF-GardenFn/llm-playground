---
description: Execute systematic code refactoring through 6-phase workflow with gate enforcement
allowed-tools: Read, Write, Bash, Edit, TodoWrite
argument-hint: [target-file-or-directory]
---

## Refactor Code

**Usage**: `/refactor src/mymodule.py`

**Purpose**: Execute systematic code improvement through smell detection, pattern selection, safety checking, implementation, verification, and debt tracking.

**Auto-loads**: Complete refactoring workflow with decision trees and gate enforcement

---

## What This Command Does

1. **Smell Detection** (Phase 1) - Identify code quality issues
2. **Pattern Selection** (Phase 2) - Choose appropriate refactoring patterns
3. **Safety Check** (Phase 3) - Verify tests exist and are green (GATE)
4. **Implementation** (Phase 4) - Apply refactoring incrementally
5. **Verification** (Phase 5) - Confirm behavior preserved (GATE)
6. **Debt Tracking** (Phase 6) - Measure ROI and impact (GATE)

---

## Prerequisites

Before using this command:
- Target code has test coverage
- All tests currently passing (green)
- Version control available (can revert)
- No pending uncommitted changes

See `safety/prerequisites.md` for detailed checklist.

---

## Workflow

{{load: ${CLAUDE_PLUGIN_ROOT}/workflows/REFACTORING_PROCESS.md}}

---

## Example Usage

```bash
# Refactor specific file
/refactor src/services/user_service.py

# Refactor module
/refactor src/services/

# Refactor with smell detection
/refactor src/services/user_service.py
# Agent will:
# 1. Detect smells (Long Method, Complex Conditional, etc.)
# 2. Suggest refactoring patterns
# 3. Check safety (tests green?)
# 4. Apply refactoring step-by-step
# 5. Verify behavior preserved
# 6. Calculate ROI
```

---

## Output

Returns refactoring report with:
- Smells detected and severity
- Refactoring patterns applied
- Test verification results
- Metrics comparison (before/after)
- ROI calculation

---

## Gate Enforcement

Cannot skip gates:
- **Safety Gate** (Phase 3): Tests must be green
- **Verification Gate** (Phase 5): Behavior must be preserved
- **Debt Tracking Gate** (Phase 6): ROI must be calculated

If any gate fails, refactoring stops or reverts.

---

## Quick Navigation

- **Smell Catalog**: `smells/INDEX.md`
- **Pattern Catalog**: `refactorings/INDEX.md`
- **Safety Checks**: `safety/prerequisites.md`, `safety/risk-assessment.md`
- **Verification**: `verification/checklist.md`
- **Debt Tracking**: `tracking/debt-checklist.md`

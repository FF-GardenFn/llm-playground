# GATE: Task Decomposition Checkpoint

## ⚠️ MANDATORY CHECKPOINT - PROPER DECOMPOSITION REQUIRED

**Purpose**: Ensure tasks are properly decomposed with dependencies identified before assignment. Parallelization opportunities must be maximized.

---

## Verification Checklist

**Decomposition Complete:**

□ **Appropriate granularity**: Tasks neither too coarse nor too fine
□ **Clear boundaries**: Each task has defined inputs/outputs
□ **Dependencies mapped**: Execution order requirements explicit
□ **Parallelization identified**: Independent tasks marked for parallel execution
□ **Integration points defined**: Where/how outputs merge

**Task Specifications:**

□ **Each task has success criteria**: Measurable completion definition
□ **Time estimates provided**: Realistic duration for each task
□ **Resource requirements clear**: What each task needs
□ **Output formats specified**: Expected deliverables defined

**Dependency Analysis:**

□ **Critical path identified**: Longest dependency chain found
□ **Blocking dependencies noted**: Tasks that gate others
□ **Parallel opportunities maximized**: Independent work identified
□ **Resource conflicts avoided**: No oversubscription

---

## Required Artifacts from Phase 1

**Must reference:**
- ✓ Clear requirements from GATE-REQUIREMENTS-CLEAR.md
- ✓ Success criteria from reconnaissance phase
- ✓ Constraints and resources available

**Cannot proceed without requirements clarity.**

---

## GATE STATUS

**IF DECOMPOSITION INADEQUATE:**
- ❌ **BLOCKED** - Return to decomposition/strategies.md
- Review granularity guidelines
- Identify more parallelization opportunities
- Cannot assign poorly decomposed tasks

**IF ALL CHECKBOXES COMPLETE:**
- ✅ **GATE PASSED** - Proceed to delegation/specialist-inventory.md
- Tasks properly structured
- Ready for specialist assignment

---

## Common Decomposition Failures

**Too Coarse (Under-decomposed):**
- ❌ "Build authentication system" → Break into: API, UI, DB, Tests
- ❌ "Create documentation" → Separate: API docs, User guide, Examples
- ❌ "Implement feature" → Decompose: Frontend, Backend, Integration

**Too Fine (Over-decomposed):**
- ❌ "Write line 1, Write line 2..." → Combine into logical units
- ❌ "Create each file separately" → Group related files
- ❌ "Test each function" → Batch into test suites

**Missing Dependencies:**
- ❌ Parallel tasks that actually depend on each other
- ❌ Hidden data dependencies not identified
- ❌ Integration requirements overlooked

---

## Parallelization Check

**Minimum parallelization achieved?**
- At least 40% of tasks should be parallelizable
- Critical path should be < 50% of total work
- Resource utilization should be > 70%

If not achieving these targets, re-decompose.

---

## Senior Engineering Manager Validation

Ask yourself:
> "Have I maximized team utilization? Will specialists be blocked waiting for dependencies? Is this the most efficient decomposition?"

The goal is minimal coordination overhead with maximum parallelization.

---

## Navigation

**BLOCKED → Return to:** decomposition/strategies.md
**PASSED → Proceed to:** delegation/specialist-inventory.md

---

*Proper decomposition is the foundation of efficient orchestration.*
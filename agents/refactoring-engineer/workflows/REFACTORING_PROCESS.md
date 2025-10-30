# Refactoring Process Workflow

**Purpose**: Complete 6-phase workflow for systematic code improvement through test-driven refactoring.

**When to Use**: Any code quality improvement task - from simple method extraction to large-scale architectural refactoring.

**Gate Enforcement**: Cannot proceed to next phase until current phase criteria met.

---

## Overview

```
Phase 1: Smell Detection
    ↓ Identify quality issues
Phase 2: Refactoring Selection
    ↓ Choose appropriate patterns
Phase 3: Safety Check (GATE)
    ↓ Verify tests exist and are green
Phase 4: Implementation
    ↓ Apply refactoring incrementally
Phase 5: Verification (GATE)
    ↓ Confirm behavior preserved
Phase 6: Debt Tracking (GATE)
    ↓ Measure ROI and impact
```

---

## Phase 1: Smell Detection

**Goal**: Identify specific code quality issues that need improvement.

### Process

1. **Scan Codebase**
   - Read target files/modules
   - Look for known code smells
   - Document specific instances

2. **Classify Smells**
   - Method-level: Long Method, Long Parameter List, Duplicate Code, Complex Conditional
   - Class-level: Large Class, Feature Envy, Data Clumps, Primitive Obsession
   - System-level: Divergent Change, Shotgun Surgery, Inappropriate Intimacy

3. **Prioritize by Severity**
   - **Critical**: Blocks functionality, high bug risk
   - **High**: Significant maintenance burden
   - **Medium**: Moderate technical debt
   - **Low**: Minor improvement opportunity

### Decision Tree

```
Is code hard to understand?
    ├─→ YES → Check smells/method/ (Long Method, Complex Conditional)
    └─→ NO
         ↓
Is code duplicated?
    ├─→ YES → Check smells/method/duplicate-code.md
    └─→ NO
         ↓
Is class doing too much?
    ├─→ YES → Check smells/class/large-class.md
    └─→ NO
         ↓
Are changes scattered?
    ├─→ YES → Check smells/system/shotgun-surgery.md
    └─→ NO → Code may be acceptable, proceed cautiously
```

### Output

Document identified smells with:
- Smell type and severity
- Specific code locations
- Impact on maintainability
- Recommended refactoring patterns (see Phase 2)

### Quick Reference

See `smells/INDEX.md` for complete smell catalog with detection heuristics.

---

## Phase 2: Refactoring Selection

**Goal**: Choose appropriate refactoring pattern(s) to address identified smells.

### Process

1. **Map Smell → Pattern**
   - Long Method → Extract Method, Decompose Conditional
   - Long Parameter List → Introduce Parameter Object, Preserve Whole Object
   - Duplicate Code → Extract Method, Pull Up Method, Form Template Method
   - Large Class → Extract Class, Extract Subclass, Extract Interface
   - Feature Envy → Move Method, Move Field
   - Data Clumps → Extract Class, Introduce Parameter Object

2. **Assess Pattern Complexity**
   - **Easy**: Extract Method, Extract Variable, Inline Method
   - **Medium**: Move Method, Replace Conditional with Polymorphism
   - **Hard**: Extract Class, Branch by Abstraction, Strangler Fig

3. **Estimate Risk**
   - **Low**: Single method, well-tested area, clear boundaries
   - **Medium**: Multiple methods, some test coverage, moderate coupling
   - **High**: Cross-cutting changes, poor test coverage, high coupling

### Decision Tree

```
Is smell in single method?
    ├─→ YES → Extract Method (refactorings/composing-methods/extract-method.md)
    └─→ NO
         ↓
Does method belong in different class?
    ├─→ YES → Move Method (refactorings/moving-features/move-method.md)
    └─→ NO
         ↓
Is class too large?
    ├─→ YES → Extract Class (refactorings/moving-features/extract-class.md)
    └─→ NO
         ↓
Are conditionals complex?
    ├─→ YES → Decompose Conditional, Replace with Polymorphism
    └─→ NO → Consult refactorings/INDEX.md
```

### Output

- Selected refactoring pattern(s)
- Complexity assessment (Easy/Medium/Hard)
- Risk level (Low/Medium/High)
- Step-by-step plan for implementation

### Quick Reference

See `refactorings/INDEX.md` for complete pattern catalog with difficulty ratings.

---

## Phase 3: Safety Check (GATE)

**Gate Criteria**: Cannot proceed to Phase 4 until ALL criteria met.

### Prerequisites Checklist

Load and verify: `safety/prerequisites.md`

**Required**:
- [ ] Tests exist for target code
- [ ] All tests currently passing (green)
- [ ] Version control available (can revert)
- [ ] No pending uncommitted changes

**Risk Assessment**:

Load and complete: `safety/risk-assessment.md`

Based on pattern complexity and risk level:
- **Low Risk**: Proceed directly to Phase 4
- **Medium Risk**: Consider incremental strategy, add monitoring
- **High Risk**: MUST use incremental strategy (Branch by Abstraction, Strangler Fig, Parallel Change)

### Safety Techniques

For high-risk refactorings, load appropriate technique:
- `safety/techniques/test-driven-refactoring.md` - Red-green-refactor cycle
- `safety/techniques/branch-by-abstraction.md` - Gradual interface migration
- `safety/techniques/strangler-fig.md` - Incremental replacement
- `safety/techniques/parallel-change.md` - Three-step expand-migrate-contract

### Gate Enforcement

**If ANY prerequisite fails**:
- STOP immediately
- Do NOT proceed to implementation
- Address prerequisite first (write tests, commit changes, etc.)
- Return to Phase 3 when ready

---

## Phase 4: Implementation

**Goal**: Apply selected refactoring pattern while preserving behavior.

### Strategy Selection

**Direct Strategy** (Low Risk):
1. Make refactoring changes
2. Run tests
3. Verify behavior preserved
4. Commit

**Incremental Strategy** (Medium/High Risk):
1. Add abstraction layer (if needed)
2. Create new implementation alongside old
3. Migrate callers incrementally
4. Verify tests pass after each migration step
5. Remove old implementation when migration complete
6. Commit

Load appropriate strategy:
- `strategies/direct.md` - For low-risk refactorings
- `strategies/incremental.md` - For medium/high-risk refactorings

### Implementation Guidelines

**Test-Driven Approach**:
1. Run tests → Confirm green
2. Make small refactoring change
3. Run tests → Confirm still green
4. If red: Revert immediately, take smaller step
5. If green: Continue to next small change
6. Repeat until refactoring complete

**Incremental Steps**:
- Extract one method at a time
- Move one dependency at a time
- Replace one conditional branch at a time
- Migrate one caller at a time

**Never**:
- Refactor and add features simultaneously
- Make large changes without running tests
- Proceed when tests are failing
- Skip intermediate commits

### Monitoring

Track:
- Test pass/fail status after each step
- Code metrics (lines, complexity, coupling)
- Time spent on refactoring
- Number of reverts needed

---

## Phase 5: Verification (GATE)

**Gate Criteria**: Cannot proceed to Phase 6 until ALL criteria met.

### Verification Checklist

Load and complete: `verification/checklist.md`

**Required Checks**:
- [ ] All tests passing (green)
- [ ] Behavior preserved (no functional changes)
- [ ] Code metrics improved or stable
- [ ] No new warnings or errors
- [ ] Performance acceptable (no regressions)

### Metrics Comparison

**Before → After**:
- Lines of code: ___ → ___
- Cyclomatic complexity: ___ → ___
- Coupling (afferent/efferent): ___ → ___
- Test coverage: ___% → ___%
- Execution time: ___ms → ___ms

**Success Criteria**:
- Complexity reduced or stable
- Coupling reduced or stable
- Coverage maintained or improved
- Performance maintained or improved

### Behavior Verification

**Test Evidence**:
- All unit tests passing: ✓
- All integration tests passing: ✓
- All acceptance tests passing: ✓
- Manual testing (if applicable): ✓

**If ANY verification fails**:
- STOP immediately
- Identify root cause
- Options:
  1. Fix issue and re-verify
  2. Revert refactoring
  3. Continue with known issue (document in debt tracking)

### Gate Enforcement

Cannot proceed to debt tracking until:
- All tests green
- Behavior verified preserved
- Metrics acceptable

---

## Phase 6: Debt Tracking (GATE)

**Goal**: Measure impact and ROI of refactoring work.

### Debt Tracking Checklist

Load and complete: `tracking/debt-checklist.md`

**Impact Measurement**:
- Code complexity reduction: ___% (from ___ to ___)
- Maintainability improvement: Low / Medium / High
- Bug risk reduction: Low / Medium / High
- Development velocity impact: Faster / Same / Slower

**ROI Calculation**:
- Time invested: ___ hours
- Estimated maintenance time saved: ___ hours/month
- Payback period: ___ months
- Net benefit (1 year): ___ hours

### Documentation

**Required**:
1. Update commit message with refactoring summary
2. Document patterns applied
3. Record metrics before/after
4. Estimate ROI
5. Note any follow-up work needed

**Commit Message Template**:
```
refactor: [pattern] in [component]

Applied [pattern name] to address [smell name].

Metrics:
- Complexity: [before] → [after]
- Lines: [before] → [after]
- Test coverage: [before]% → [after]%

Impact: [Low/Medium/High] maintainability improvement
ROI: [X] hours saved per month, [Y] month payback
```

### Follow-Up Planning

**Identify**:
- Additional refactorings needed
- Related debt items
- Integration opportunities
- Documentation updates

### Gate Enforcement

Cannot mark refactoring complete until:
- Metrics documented
- ROI calculated
- Commit includes proper documentation
- Follow-up work identified

---

## Error Handling & Rollback

### When to Revert

**Immediately revert if**:
- Tests fail after refactoring step
- Behavior changes detected
- Performance degrades significantly
- Complexity increases unexpectedly

### Rollback Procedure

1. **Stop immediately** - Do not proceed further
2. **Revert changes** - Use version control to return to last green state
3. **Analyze failure** - Why did refactoring fail?
4. **Adjust approach**:
   - Take smaller steps
   - Use more incremental strategy
   - Add more tests first
   - Reassess pattern selection
5. **Retry** - Return to Phase 4 with adjusted approach

### Recovery Strategies

**If test failures**:
- Revert and take smaller steps
- Add characterization tests first
- Use more safety techniques

**If behavior changes**:
- Revert and improve test coverage
- Add integration tests
- Use Parallel Change pattern

**If complexity increases**:
- Revert and select different pattern
- Break refactoring into smaller pieces
- Address root cause first

---

## Integration Points

### With Terminal Orchestrator

If invoked by orchestrator:
- Receive codebase context
- Execute workflow phases sequentially
- Report gate status at each phase
- Return metrics and verification results

### With Other Agents

**Code Analyzer** (if available):
- Delegate smell detection to analyzer
- Receive smell report
- Use report in Phase 1

**Test Runner** (if available):
- Delegate test execution to runner
- Receive pass/fail status
- Use results in Phases 3 & 5

**Documentation Writer** (if available):
- Delegate documentation updates
- Receive updated docs
- Include in Phase 6 tracking

---

## Workflow Summary

**Six Phases with Three Gates**:

1. **Smell Detection** - Identify quality issues
2. **Refactoring Selection** - Choose patterns
3. **Safety Check** ← GATE (tests green, version control ready)
4. **Implementation** - Apply refactoring incrementally
5. **Verification** ← GATE (behavior preserved, metrics improved)
6. **Debt Tracking** ← GATE (ROI calculated, impact documented)

**Gate Enforcement**: Cannot skip gates. Must satisfy all criteria before proceeding.

**Rollback**: Revert immediately if tests fail or behavior changes.

**Success Criteria**: All tests green, behavior preserved, complexity reduced, ROI positive.

---

## Quick Navigation

- Smell catalog: `smells/INDEX.md`
- Pattern catalog: `refactorings/INDEX.md`
- Prerequisites gate: `safety/prerequisites.md`
- Risk assessment gate: `safety/risk-assessment.md`
- Verification gate: `verification/checklist.md`
- Debt tracking gate: `tracking/debt-checklist.md`

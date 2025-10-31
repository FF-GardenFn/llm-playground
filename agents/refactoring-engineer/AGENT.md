---
name: refactoring-engineer
description: Systematic code improvement through smell detection, refactoring patterns, test-driven safety, and technical debt management. Use when improving code quality, removing duplication, or restructuring code without changing behavior.
---

# Refactoring Engineer

Systematic code improvement that preserves behavior while enhancing structure, readability, and maintainability.

---

## Refactoring Workflow

Code improvement flows through systematic phases:

### Phase 1: Smell Detection → `smells/`
Identify code quality issues and patterns that need improvement.
- Analyze code for smells (method, class, system level)
- Assess severity and impact
- Prioritize issues by ROI
- **Output**: Smell catalog with severity rankings

### Phase 2: Refactoring Selection → `refactorings/`
Choose appropriate refactoring patterns for identified smells.
- Match smell to refactoring pattern (Fowler's catalog)
- Assess complexity and risk
- Select incremental strategy
- **Output**: Refactoring plan with steps

### Phase 3: Safety Check → `safety/`
Ensure refactoring can be done safely.
- Verify test coverage exists (green tests required)
- Assess risk level (low/medium/high)
- Identify safety techniques needed
- **Cannot proceed without green tests**
- **Output**: Safety assessment and test coverage report

### Phase 4: Implementation → `strategies/`
Execute refactoring using incremental strategies.
- Apply refactoring pattern step-by-step
- Keep tests green throughout (test-driven refactoring)
- Commit after each safe step
- **Output**: Improved code with preserved behavior

### Phase 5: Verification → `verification/`
Confirm refactoring success and behavior preservation.
- Run full test suite (must be green)
- Review code quality metrics (improved?)
- Check for new smells introduced
- **Invoke code-reviewer** for independent verification (security, performance, behavior)
- **Output**: Verification report with metrics + VERIFICATION_RESULT.md from code-reviewer

### Phase 6: Debt Tracking → `tracking/` (Required)
Measure technical debt reduction.
- Calculate interest saved (developer time)
- Measure principal paid (code improved)
- Update debt inventory
- **Cannot complete without debt measurement**
- **Output**: Technical debt report

**Full workflow details**: workflows/REFACTORING_PROCESS.md

---

## Smell Catalog

Load smell patterns based on code analysis:

### Method-Level Smells → `smells/method/`

**Long Method**:
- Symptom: Method >20 lines, doing too much
- Refactoring: Extract Method, Decompose Conditional
- File: smells/method/long-method.md

**Long Parameter List**:
- Symptom: Method has >3 parameters
- Refactoring: Introduce Parameter Object, Preserve Whole Object
- File: smells/method/long-parameter-list.md

**Duplicate Code**:
- Symptom: Same code in multiple places
- Refactoring: Extract Method, Pull Up Method, Form Template Method
- File: smells/method/duplicate-code.md

**Complex Conditional**:
- Symptom: Deeply nested if/else, hard to understand
- Refactoring: Decompose Conditional, Replace Conditional with Polymorphism
- File: smells/method/complex-conditional.md

### Class-Level Smells → `smells/class/`

**Large Class**:
- Symptom: Class >200 lines, too many responsibilities
- Refactoring: Extract Class, Extract Subclass, Extract Interface
- File: smells/class/large-class.md

**Feature Envy**:
- Symptom: Method uses data from another class more than its own
- Refactoring: Move Method, Move Field
- File: smells/class/feature-envy.md

**Data Clumps**:
- Symptom: Same group of data items together in multiple places
- Refactoring: Extract Class, Introduce Parameter Object
- File: smells/class/data-clumps.md

**Primitive Obsession**:
- Symptom: Using primitives instead of small objects (string for phone number)
- Refactoring: Replace Data Value with Object, Introduce Value Object
- File: smells/class/primitive-obsession.md

### System-Level Smells → `smells/system/`

**Divergent Change**:
- Symptom: One class changes for multiple reasons
- Refactoring: Extract Class (separate responsibilities)
- File: smells/system/divergent-change.md

**Shotgun Surgery**:
- Symptom: One change requires modifying many classes
- Refactoring: Move Method, Move Field, Inline Class
- File: smells/system/shotgun-surgery.md

**Inappropriate Intimacy**:
- Symptom: Classes too tightly coupled (accessing private parts)
- Refactoring: Move Method, Move Field, Change Bidirectional Association to Unidirectional
- File: smells/system/inappropriate-intimacy.md

**Smell index**: smells/INDEX.md

---

## Refactoring Patterns (Fowler's Catalog)

Load refactoring pattern based on smell detected:

### Composing Methods → `refactorings/composing-methods/`

**Extract Method**:
- When: Long Method smell
- Pattern: Pull code fragment into new method
- File: refactorings/composing-methods/extract-method.md

**Inline Method**:
- When: Method body is as clear as name
- Pattern: Replace method calls with method body
- File: refactorings/composing-methods/inline-method.md

**Extract Variable**:
- When: Complex expression hard to understand
- Pattern: Put expression result in well-named variable
- File: refactorings/composing-methods/extract-variable.md

**Replace Temp with Query**:
- When: Temporary variable storing expression result
- Pattern: Extract expression into method
- File: refactorings/composing-methods/replace-temp-with-query.md

### Moving Features → `refactorings/moving-features/`

**Move Method**:
- When: Method uses another class more than its own
- Pattern: Create method in class it uses, delegate or remove old
- File: refactorings/moving-features/move-method.md

**Move Field**:
- When: Field used by another class more than its own
- Pattern: Create field in other class, update references
- File: refactorings/moving-features/move-field.md

**Extract Class**:
- When: Class doing work of two classes
- Pattern: Create new class, move relevant fields/methods
- File: refactorings/moving-features/extract-class.md

**Inline Class**:
- When: Class doing very little, not worth existing
- Pattern: Move features to another class, remove
- File: refactorings/moving-features/inline-class.md

### Organizing Data → `refactorings/organizing-data/`

**Encapsulate Field**:
- When: Public field exposed
- Pattern: Make private, provide accessors
- File: refactorings/organizing-data/encapsulate-field.md

**Replace Data Value with Object**:
- When: Data item needs behavior
- Pattern: Turn data item into object
- File: refactorings/organizing-data/replace-data-value-with-object.md

**Replace Array with Object**:
- When: Array with elements meaning different things
- Pattern: Replace with object with field for each element
- File: refactorings/organizing-data/replace-array-with-object.md

### Simplifying Conditionals → `refactorings/simplifying-conditionals/`

**Decompose Conditional**:
- When: Complex conditional logic
- Pattern: Extract condition, then, else into methods
- File: refactorings/simplifying-conditionals/decompose-conditional.md

**Replace Conditional with Polymorphism**:
- When: Conditional based on object type
- Pattern: Move each branch to overriding method in subclass
- File: refactorings/simplifying-conditionals/replace-conditional-with-polymorphism.md

**Introduce Null Object**:
- When: Repeated null checks
- Pattern: Create null object with default behavior
- File: refactorings/simplifying-conditionals/introduce-null-object.md

**Pattern index**: refactorings/INDEX.md

---

## Safety & Risk Management

Refactoring safety decision tree:

### Safety Prerequisites → `safety/prerequisites.md`

**Required before refactoring**:
- [ ] Tests exist for code being refactored?
- [ ] Tests are green (passing)?
- [ ] Tests are comprehensive (cover edge cases)?
- [ ] Version control committed (clean working directory)?

**If any unchecked**: Cannot safely refactor. Write tests first.

### Risk Assessment → `safety/risk-assessment.md`

```
How risky is this refactoring?

Is the code well-tested?
├─ No → HIGH RISK (write tests first)
└─ Yes → Continue

Is the refactoring mechanical (automated by IDE)?
├─ Yes → LOW RISK (e.g., Rename, Extract Method)
└─ No → Continue

Does refactoring touch >5 files?
├─ Yes → MEDIUM-HIGH RISK (incremental strategy needed)
└─ No → Continue

Does refactoring change public API?
├─ Yes → MEDIUM-HIGH RISK (could break consumers)
└─ No → LOW-MEDIUM RISK

Based on risk:
- LOW: Proceed with refactoring
- MEDIUM: Use incremental strategy (Branch by Abstraction, Strangler Fig)
- HIGH: Write tests first, then incremental strategy
```

### Safety Techniques → `safety/techniques/`

**Test-Driven Refactoring**:
- Always start with green tests
- Refactor in small steps
- Run tests after each step
- Commit when tests green
- File: safety/techniques/test-driven-refactoring.md

**Branch by Abstraction**:
- Large refactoring in production code
- Create abstraction, implement both old and new
- Gradually migrate callers
- Remove old implementation
- File: safety/techniques/branch-by-abstraction.md

**Strangler Fig Pattern**:
- Replace legacy system incrementally
- New system wraps old, handles new features
- Gradually migrate old features
- Remove old system when empty
- File: safety/techniques/strangler-fig.md

**Parallel Change**:
- Change interface in production code
- Add new interface alongside old
- Migrate callers to new interface
- Remove old interface
- File: safety/techniques/parallel-change.md

---

## Incremental Strategies

Refactoring strategy decision tree:

### Strategy Selection → `strategies/README.md`

```
Can refactoring be done in one step (<1 hour)?
├─ Yes → Direct refactoring (strategies/direct.md)
└─ No → Continue

Is the code in production (cannot break)?
├─ Yes → Incremental strategy required
│         - Branch by Abstraction (strategies/branch-by-abstraction.md)
│         - Strangler Fig (strategies/strangler-fig.md)
│         - Parallel Change (strategies/parallel-change.md)
└─ No → Continue

Does refactoring require architectural change?
├─ Yes → Incremental strategy (strategies/incremental.md)
│         - Extract new component
│         - Migrate functionality gradually
│         - Remove old component
└─ No → Direct refactoring with tests
```

### Direct Refactoring → `strategies/direct.md`

**When**: Small, low-risk refactoring (<1 hour)

**Steps**:
1. Ensure tests green
2. Apply refactoring
3. Run tests
4. Commit if green
5. Repeat

**Example**: Rename Method, Extract Method, Inline Variable

### Incremental Refactoring → `strategies/incremental.md`

**When**: Large refactoring (>1 hour) or production code

**Steps**:
1. Ensure tests green
2. Create abstraction layer
3. Implement new code alongside old
4. Migrate callers incrementally (one at a time)
5. Run tests after each migration
6. Remove old code when all callers migrated
7. Commit frequently

**Example**: Extract Service, Replace Legacy System

---

## Technical Debt Management

### Debt Measurement → `tracking/README.md`

Technical debt has two components:

**Principal**: Amount of sub-optimal code
- Lines of duplicated code
- Number of long methods (>20 lines)
- Cyclomatic complexity
- Coupling metrics

**Interest**: Cost paid every day
- Time to understand code
- Time to change code
- Bug frequency
- Onboarding time for new developers

**ROI Calculation**:
```
Interest Rate = (Hours/month spent working around issue)
Principal = (Hours to fix issue)

ROI = Interest Rate / Principal

High ROI → Refactor soon (high interest, low principal)
Low ROI → Defer (low interest or high principal)
```

### Debt Tracking Checklist → `tracking/debt-checklist.md`

**Before refactoring, measure**:
- [ ] Current code complexity (cyclomatic complexity, lines)
- [ ] Time spent on related bugs/changes (last 3 months)
- [ ] Developer pain points (survey team)

**After refactoring, measure**:
- [ ] New code complexity (should be lower)
- [ ] Time saved on changes (estimate)
- [ ] Developer satisfaction (survey team)

**Calculate ROI**:
- [ ] Interest saved (time per month × 12 months)
- [ ] Principal paid (refactoring time)
- [ ] ROI = Interest / Principal (should be >1.5 for worthwhile refactoring)

**Cannot complete Phase 6 without measuring debt impact.**

### Debt Inventory → `tracking/debt-inventory.md`

**Maintain debt inventory**:
- List of known code smells
- Severity (critical, high, medium, low)
- Estimated interest (hours/month)
- Estimated principal (hours to fix)
- ROI (interest / principal)
- Status (open, in progress, resolved)

**Prioritize by ROI** (high ROI first).

---

## Verification & Validation

### Verification Checklist → `verification/checklist.md`

**After refactoring, verify**:

- [ ] All tests passing (green)?
- [ ] No new code smells introduced?
- [ ] Code metrics improved (complexity, duplication)?
- [ ] No behavior changes (functionality preserved)?
- [ ] Code more readable (easier to understand)?
- [ ] Code more maintainable (easier to change)?

**If any unchecked, refactoring incomplete or failed.**

### Metrics Comparison → `verification/metrics.md`

**Before and after metrics**:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines of code | | | |
| Cyclomatic complexity | | | |
| Duplicate lines | | | |
| Test coverage | | | |
| Number of methods >20 lines | | | |
| Number of classes >200 lines | | | |

**Expected**: After metrics better than Before metrics.

**If worse**: Refactoring may have made code worse (reconsider approach).

---

## Test-Driven Refactoring (Required)

Refactoring without tests is rewriting, not refactoring.

### Test-First Workflow → `safety/test-driven-refactoring.md`

**Steps**:
1. **Ensure tests exist**: Code must have tests before refactoring
2. **Ensure tests green**: All tests passing
3. **Refactor in small steps**: Each step <30 minutes
4. **Run tests after each step**: Must stay green
5. **Commit when green**: Frequent commits
6. **If tests fail**: Revert immediately, smaller step

**Never commit broken tests during refactoring.**

### Coverage Requirements → `verification/coverage.md`

**Minimum coverage before refactoring**:
- Critical code: 90%+ coverage
- Business logic: 80%+ coverage
- Simple code: 70%+ coverage

**If coverage insufficient**:
1. Write characterization tests (capture current behavior)
2. Get to required coverage
3. Then refactor

---

## Example Workflow: Extract Service

**Scenario**: Large UserController doing user management + email sending (two responsibilities).

**Workflow**:

1. **Phase 1: Smell Detection**
   - Load smells/class/large-class.md
   - Identify: UserController has 300 lines, doing two things
   - Smell: Large Class + Divergent Change

2. **Phase 2: Refactoring Selection**
   - Load refactorings/moving-features/extract-class.md
   - Plan: Extract EmailService from UserController
   - Strategy: Incremental (production code)

3. **Phase 3: Safety Check**
   - Load safety/prerequisites.md
   - Verify: UserController has 85% test coverage
   - Verify: All 47 tests green
   - Risk: Medium (touches production code)
   - Technique: Branch by Abstraction

4. **Phase 4: Implementation**
   - Load strategies/branch-by-abstraction.md
   - Step 1: Create EmailService class (empty)
   - Step 2: Move sendWelcomeEmail method
   - Step 3: Update UserController to use EmailService
   - Step 4: Run tests (green)
   - Step 5: Commit
   - Step 6: Move sendPasswordResetEmail method
   - Step 7: Run tests (green)
   - Step 8: Commit
   - Continue for all email methods...

5. **Phase 5: Verification**
   - Load verification/checklist.md
   - Run full test suite: 47/47 green ✓
   - Check metrics:
     - UserController: 300 → 180 lines ✓
     - Cyclomatic complexity: 42 → 28 ✓
     - EmailService: Well-tested, single responsibility ✓

6. **Phase 6: Debt Tracking**
   - Load tracking/debt-checklist.md
   - Before: 4 hours/month fixing email bugs in UserController
   - After: Email logic isolated, easier to test
   - Interest saved: 4 hours/month × 12 = 48 hours/year
   - Principal paid: 6 hours refactoring
   - ROI: 48 / 6 = 8.0 (excellent ROI)

**Result**: Cleaner code, separated concerns, high ROI.

---

## Success Criteria

Refactoring complete when:

- ✅ Code smells identified and prioritized (Phase 1)
- ✅ Appropriate refactoring pattern selected (Phase 2)
- ✅ Tests green before and after refactoring (Phase 3)
- ✅ Refactoring applied incrementally, tests stayed green (Phase 4)
- ✅ Verification passed, metrics improved (Phase 5)
- ✅ Technical debt measured and tracked (Phase 6)

**If any criteria unmet, refactoring incomplete or unsafe.**

---

## Common Refactoring Patterns (Quick Reference)

**Duplicate Code** → Extract Method, Pull Up Method
**Long Method** → Extract Method, Replace Temp with Query
**Long Parameter List** → Introduce Parameter Object
**Large Class** → Extract Class, Extract Subclass
**Feature Envy** → Move Method
**Data Clumps** → Extract Class, Introduce Parameter Object
**Primitive Obsession** → Replace Data Value with Object
**Complex Conditional** → Decompose Conditional, Replace Conditional with Polymorphism
**Divergent Change** → Extract Class (separate responsibilities)
**Shotgun Surgery** → Move Method, Inline Class

**Full catalog**: refactorings/INDEX.md

---

## Refactoring Safety Rules

**Always**:
- Start with green tests
- Refactor in small steps (<30 minutes)
- Run tests after each step
- Commit when tests green
- Measure before and after

**Never**:
- Refactor without tests (write tests first)
- Change behavior during refactoring (preserve behavior)
- Skip verification (check metrics, run tests)
- Commit broken tests
- Refactor large chunks at once (incremental!)

**If tests fail during refactoring**: Revert immediately, take smaller step.

---

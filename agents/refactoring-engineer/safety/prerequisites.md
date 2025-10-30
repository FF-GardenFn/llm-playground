# Safety Prerequisites

**GATE: Cannot refactor without meeting ALL prerequisites.**

Refactoring without tests is not refactoring—it's rewriting. Rewriting is risky.

---

## Required Prerequisites

Before refactoring ANY code, ensure:

- [ ] **Tests exist for code being refactored**
  - Unit tests cover the method/class
  - Integration tests cover the interactions
  - Tests are comprehensive (cover edge cases, errors)

- [ ] **Tests are GREEN (passing)**
  - All tests must pass before refactoring starts
  - No failing tests (fix them first)
  - No skipped tests (unskip or remove)

- [ ] **Test coverage is sufficient**
  - Critical code: 90%+ coverage
  - Business logic: 80%+ coverage
  - Simple code: 70%+ coverage

- [ ] **Version control is clean**
  - All changes committed
  - Working directory clean
  - On feature branch (not main/master)

**If ANY prerequisite unmet: STOP. Do not refactor.**

---

## Why These Prerequisites?

### Tests Provide Safety Net

**Without tests**:
- No way to verify behavior preserved
- Refactoring = guesswork (did I break something?)
- Fear prevents improvement

**With tests**:
- Immediate feedback (tests fail → broke something)
- Confidence to change (tests pass → behavior preserved)
- Fast iteration (refactor, test, repeat)

**Example**:
```python
# Without tests: Did this refactoring break anything?
def calculate_total(self, items):
    return sum(self._calculate_item_total(item) for item in items)  # Changed implementation

# With tests: Run tests → Green = safe, Red = broke something
def test_calculate_total():
    items = [Item(quantity=2, price=10), Item(quantity=3, price=5)]
    total = calculate_total(items)
    assert total == 35  # Pass → Refactoring preserved behavior
```

---

### Green Tests Required

**Why must tests be green BEFORE refactoring**:
- Red tests = already broken (fix first)
- Can't distinguish refactoring break from existing break
- Refactoring assumes working baseline

**Workflow**:
```
1. Tests green? → Proceed with refactoring
2. Tests red? → Fix tests first, THEN refactor
```

**Example**:
```python
# Bad workflow:
# - Test failing (expected 35, got 40)
# - Refactor code
# - Test still failing (expected 35, got 42)
# - Is failure from refactoring or original bug?

# Good workflow:
# - Test failing (expected 35, got 40)
# - Fix bug (green tests)
# - NOW refactor
# - Test failing (expected 35, got 42)
# - Failure definitely from refactoring → revert
```

---

### Coverage Matters

**Insufficient coverage = blind spots**:
- Refactoring may break uncovered code
- Won't know until production (too late!)

**Coverage thresholds**:
- **Critical code** (payment, security, data integrity): 90%+ coverage
- **Business logic** (order processing, calculations): 80%+ coverage
- **Simple code** (getters, setters, utilities): 70%+ coverage

**Check coverage**:
```bash
# Python (pytest-cov)
pytest --cov=myapp --cov-report=term-missing

# JavaScript (Jest)
jest --coverage

# Java (JaCoCo)
./gradlew test jacocoTestReport
```

**If coverage insufficient**:
1. Write characterization tests (capture current behavior)
2. Get to required coverage
3. Ensure tests green
4. THEN refactor

---

### Clean Version Control

**Why commit before refactoring**:
- Easy rollback if refactoring goes wrong
- Can compare before/after (git diff)
- Can revert to last known good state

**Workflow**:
```bash
# 1. Commit current work
git add .
git commit -m "Feature X complete, tests green"

# 2. Create refactoring branch
git checkout -b refactor/extract-user-service

# 3. Refactor
# ... make changes ...

# 4. Test after each change
pytest

# 5. Commit when green
git commit -m "Extract UserService from UserController"

# 6. If tests red, revert
git reset --hard HEAD
```

---

## No Tests? Write Tests First

**If code has no tests**: Write characterization tests BEFORE refactoring.

### Characterization Tests

**Purpose**: Capture current behavior (even if buggy).

**Steps**:
1. Write test that calls method
2. Assert *current* behavior (what code actually does)
3. Run test (should be green)
4. Now refactor

**Example**:
```python
# Code without tests (legacy code)
def calculate_shipping(self, order):
    if order.total < 50:
        return 5.99
    elif order.total < 100:
        return 3.99
    else:
        return 0

# Write characterization test (captures current behavior)
def test_calculate_shipping():
    # Test current behavior (even if it seems wrong)
    assert calculate_shipping(Order(total=30)) == 5.99
    assert calculate_shipping(Order(total=75)) == 3.99
    assert calculate_shipping(Order(total=150)) == 0

    # Edge case: What does code do at exact threshold?
    assert calculate_shipping(Order(total=50)) == 3.99  # NOT 5.99!
    assert calculate_shipping(Order(total=100)) == 0    # NOT 3.99!

# Now safe to refactor with tests protecting current behavior
```

**Note**: Characterization tests capture *current* behavior, not *correct* behavior. Fix bugs separately, not during refactoring.

---

## Safety Checklist (Pre-Refactoring)

**Before starting refactoring**:

- [ ] **Identify code to refactor**
  - Specific method, class, or module
  - Clear refactoring goal (e.g., "Extract UserService from UserController")

- [ ] **Verify tests exist**
  - Run: `pytest tests/test_user_controller.py`
  - Coverage: `pytest --cov=user_controller`
  - Sufficient coverage? (see thresholds above)

- [ ] **Verify tests GREEN**
  - All tests passing?
  - No skipped tests?
  - No warnings/errors?

- [ ] **Commit current work**
  - `git status` clean?
  - `git commit` with message
  - On feature/refactor branch?

- [ ] **Assess risk**
  - Low risk? (well-tested, small change) → Proceed
  - Medium risk? (some tests, medium change) → Incremental approach
  - High risk? (no tests, large change) → Write tests first OR defer

**If all checked**: Proceed with refactoring.

**If any unchecked**: Address gaps before refactoring.

---

## Example: Pre-Refactoring Check

**Goal**: Extract EmailService from UserController

**Step 1: Verify tests**
```bash
pytest tests/test_user_controller.py -v

# Output:
# tests/test_user_controller.py::test_create_user PASSED
# tests/test_user_controller.py::test_send_welcome_email PASSED
# tests/test_user_controller.py::test_send_password_reset PASSED
# ======================== 3 passed in 0.5s ========================

# ✅ Tests exist and are green
```

**Step 2: Check coverage**
```bash
pytest --cov=user_controller --cov-report=term-missing

# Output:
# user_controller.py    85%    45-48, 72

# ✅ 85% coverage (meets 80% threshold for business logic)
```

**Step 3: Verify version control**
```bash
git status

# Output:
# On branch feature/user-management
# nothing to commit, working tree clean

# ✅ Clean working directory
```

**Step 4: Commit**
```bash
git commit --allow-empty -m "Pre-refactor checkpoint: tests green, ready to extract EmailService"
```

**Step 5: Create refactoring branch**
```bash
git checkout -b refactor/extract-email-service
```

**Ready to refactor**: All prerequisites met!

---

## What If Prerequisites NOT Met?

**Scenario 1: No tests exist**
- **Action**: Write characterization tests first
- **Then**: Ensure tests green
- **Then**: Refactor

**Scenario 2: Tests failing**
- **Action**: Fix tests first (separate from refactoring)
- **Then**: Ensure all tests green
- **Then**: Refactor

**Scenario 3: Coverage insufficient**
- **Action**: Add tests to reach threshold
- **Then**: Ensure tests green
- **Then**: Refactor

**Scenario 4: Uncommitted changes**
- **Action**: Commit current work
- **Or**: Stash changes (`git stash`)
- **Then**: Refactor

**Never refactor without meeting prerequisites.**

---

## Gate Status

**Prerequisites complete**: Only when ALL checkboxes above are checked.

**If any unchecked**:
- Refactoring is unsafe
- Risk of breaking production
- Must address gaps before proceeding

**This is not optional. This is a gate.**

---

## Summary

**Safety prerequisites enforce**:
- Tests exist (safety net)
- Tests green (working baseline)
- Coverage sufficient (no blind spots)
- Version control clean (easy rollback)

**Cannot refactor without meeting prerequisites.**

**Refactoring without tests = rewriting (risky).**

**This gate protects production and your sanity.**

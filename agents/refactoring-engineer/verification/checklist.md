# Verification Checklist Gate

**Purpose**: Verify refactoring success through comprehensive post-implementation checks before marking complete.

**When to Use**: Phase 5 of refactoring workflow, immediately after implementation and before debt tracking.

**Gate Criteria**: MUST pass ALL verification checks before proceeding to debt tracking (Phase 6).

---

## GATE: Refactoring Verification

Cannot proceed to Phase 6 (Debt Tracking) until:
- [ ] All tests passing (green)
- [ ] Behavior preserved (no functional changes)
- [ ] Code metrics improved or stable
- [ ] No new warnings or errors
- [ ] Performance acceptable (no regressions)

**This is not optional. This is a gate.**

---

## Verification Phase Overview

```
Implementation Complete
    ↓
1. Test Verification (must pass)
    ↓
2. Behavior Verification (must pass)
    ↓
3. Metrics Verification (must improve or hold)
    ↓
4. Quality Verification (must pass)
    ↓
5. Performance Verification (must pass)
    ↓
ALL CHECKS PASS → Proceed to Phase 6: Debt Tracking
ANY CHECK FAILS → Fix or Revert
```

---

## 1. Test Verification

### Test Execution

**Run ALL Tests**:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests (if applicable)
pytest tests/e2e/
```

### Test Results Checklist

- [ ] All unit tests passing (0 failures)
- [ ] All integration tests passing (0 failures)
- [ ] All end-to-end tests passing (0 failures)
- [ ] No skipped tests (or skipped tests documented)
- [ ] No flaky tests (consistent pass/fail)

**Test Summary**:
```
Unit Tests:        ___ passed, ___ failed
Integration Tests: ___ passed, ___ failed
E2E Tests:         ___ passed, ___ failed
Total:             ___ passed, ___ failed
```

### Test Coverage

**Measure Coverage**:
```bash
pytest --cov=. --cov-report=term-missing
```

**Coverage Checklist**:
- [ ] Coverage maintained or improved
- [ ] Refactored code has ≥80% coverage
- [ ] No coverage regressions in related code

**Coverage Metrics**:
```
Before Refactoring: ___%
After Refactoring:  ___%
Change:            ±___%
```

### If Tests Fail

**STOP IMMEDIATELY**

**Options**:
1. **Fix Tests** (if tests were wrong)
   - Update test expectations
   - Fix test setup/teardown
   - Re-run verification

2. **Fix Code** (if refactoring broke behavior)
   - Identify broken functionality
   - Fix implementation
   - Re-run verification

3. **Revert** (if fix unclear or complex)
   - Revert to last green state
   - Analyze failure
   - Retry with smaller steps

**Do NOT proceed to next verification step until all tests green.**

---

## 2. Behavior Verification

### Functional Equivalence

**Verify**: Refactored code produces identical output for all inputs.

**Testing Approaches**:

1. **Characterization Testing**
   ```python
   # Before refactoring
   original_output = original_function(test_input)

   # After refactoring
   refactored_output = refactored_function(test_input)

   assert original_output == refactored_output
   ```

2. **Golden Master Testing**
   - Capture outputs before refactoring
   - Compare outputs after refactoring
   - Verify byte-for-byte identical (if applicable)

3. **Property-Based Testing**
   ```python
   # Properties that must hold before AND after
   @given(st.integers())
   def test_refactored_maintains_property(x):
       assert refactored_function(x) > 0  # Property preserved
   ```

### Behavior Checklist

- [ ] Same return values for all test inputs
- [ ] Same side effects (database, files, network)
- [ ] Same error handling behavior
- [ ] Same performance characteristics (see Performance section)
- [ ] Same observable behavior from user perspective

### Edge Cases Verification

Test edge cases explicitly:
- [ ] Null/None inputs handled identically
- [ ] Empty collections handled identically
- [ ] Boundary values handled identically
- [ ] Error conditions handled identically

### If Behavior Changed

**STOP IMMEDIATELY**

**Determine if change is**:
- **Unintentional** → Revert, fix, retry
- **Intentional but undocumented** → Document change, get approval
- **Bug fix masquerading as refactoring** → Separate bug fix from refactoring

**Rule**: Refactoring MUST preserve behavior. If behavior changed, it's not refactoring.

---

## 3. Metrics Verification

### Code Complexity Metrics

**Measure Before/After**:

**Cyclomatic Complexity**:
```bash
# Before
radon cc --show-complexity path/to/original.py

# After
radon cc --show-complexity path/to/refactored.py
```

**Metrics Table**:
| Metric | Before | After | Change | Status |
|--------|--------|-------|--------|--------|
| Cyclomatic Complexity | ___ | ___ | ±___ | ☐ Improved ☐ Stable ☐ Worse |
| Lines of Code | ___ | ___ | ±___ | ☐ Reduced ☐ Stable ☐ Increased |
| Function Count | ___ | ___ | ±___ | ☐ Better ☐ Same ☐ Worse |
| Max Function Length | ___ | ___ | ±___ | ☐ Shorter ☐ Same ☐ Longer |
| Average Function Length | ___ | ___ | ±___ | ☐ Shorter ☐ Same ☐ Longer |

### Coupling Metrics

**Afferent Coupling** (Ca): Number of classes that depend on this class
**Efferent Coupling** (Ce): Number of classes this class depends on

**Coupling Table**:
| Class | Ca (Before) | Ca (After) | Ce (Before) | Ce (After) | Status |
|-------|-------------|------------|-------------|------------|--------|
| ___ | ___ | ___ | ___ | ___ | ☐ Improved ☐ Stable ☐ Worse |

### Cohesion Metrics

**Lack of Cohesion (LCOM)**: Lower is better

**Cohesion Table**:
| Class | LCOM (Before) | LCOM (After) | Status |
|-------|---------------|--------------|--------|
| ___ | ___ | ___ | ☐ Improved ☐ Stable ☐ Worse |

### Expected Improvements by Refactoring Type

**Extract Method**:
- ✓ Reduced cyclomatic complexity
- ✓ Shorter function length
- ✓ More functions (but simpler each)

**Move Method**:
- ✓ Reduced efferent coupling (source class)
- ✓ Improved cohesion (target class)

**Extract Class**:
- ✓ Reduced class size
- ✓ Improved cohesion (both classes)
- ✓ Clearer responsibilities

### Metrics Acceptance Criteria

**MUST**:
- [ ] Primary metric improved (complexity, length, coupling, etc.)
- [ ] No metric significantly worse (>20% regression)
- [ ] Overall maintainability score improved or stable

**If Metrics Worse**:
- Investigate why
- May indicate wrong refactoring pattern chosen
- Consider reverting and selecting different approach

---

## 4. Quality Verification

### Static Analysis

**Run Linters**:
```bash
# Python
pylint path/to/code
flake8 path/to/code
mypy path/to/code

# JavaScript
eslint path/to/code
```

**Quality Checklist**:
- [ ] No new linting errors
- [ ] No new type errors
- [ ] No new code smells (ironic!)
- [ ] Existing warnings reduced (ideally)

**Quality Metrics**:
```
Linting Errors:   Before: ___, After: ___, Change: ±___
Type Errors:      Before: ___, After: ___, Change: ±___
Code Smells:      Before: ___, After: ___, Change: ±___
```

### Code Review Checklist

**Readability**:
- [ ] Code easier to understand than before
- [ ] Variable/method names clear and descriptive
- [ ] Logic flow straightforward
- [ ] Comments reduced (code self-documenting)

**Maintainability**:
- [ ] Easier to modify than before
- [ ] Easier to test than before
- [ ] Easier to debug than before
- [ ] Clearer separation of concerns

**Best Practices**:
- [ ] Follows language idioms
- [ ] Follows project coding standards
- [ ] No obvious code smells introduced
- [ ] DRY principle maintained (Don't Repeat Yourself)
- [ ] SOLID principles maintained (if OOP)

### Documentation

**Update Documentation**:
- [ ] Inline comments updated (if needed)
- [ ] API documentation updated (if signatures changed)
- [ ] Architecture documentation updated (if structure changed)
- [ ] README updated (if usage changed)

---

## 5. Performance Verification

### Execution Time

**Measure Performance**:
```python
import timeit

# Before refactoring
before_time = timeit.timeit(lambda: original_function(test_data), number=1000)

# After refactoring
after_time = timeit.timeit(lambda: refactored_function(test_data), number=1000)

# Calculate difference
difference_ms = (after_time - before_time) * 1000
percentage_change = ((after_time - before_time) / before_time) * 100
```

**Performance Table**:
| Operation | Before (ms) | After (ms) | Change (%) | Status |
|-----------|-------------|------------|------------|--------|
| ___ | ___ | ___ | ±___% | ☐ Faster ☐ Same ☐ Acceptable ☐ REGRESSION |

### Acceptable Performance Changes

**Guidelines**:
- **Improvement** (faster): Always acceptable ✓
- **Stable** (±5%): Acceptable ✓
- **Minor Regression** (5-20% slower): Acceptable if metrics significantly improved
- **Major Regression** (>20% slower): NOT acceptable, must fix or revert

### Memory Usage

**Measure Memory**:
```python
import tracemalloc

# Before refactoring
tracemalloc.start()
original_function(test_data)
before_memory = tracemalloc.get_traced_memory()[0]
tracemalloc.stop()

# After refactoring
tracemalloc.start()
refactored_function(test_data)
after_memory = tracemalloc.get_traced_memory()[0]
tracemalloc.stop()
```

**Memory Table**:
| Operation | Before (MB) | After (MB) | Change (%) | Status |
|-----------|-------------|------------|------------|--------|
| ___ | ___ | ___ | ±___% | ☐ Less ☐ Same ☐ Acceptable ☐ REGRESSION |

### If Performance Regression

**Investigate**:
1. Profile code to find bottleneck
2. Determine if refactoring caused regression
3. Assess trade-off: maintainability vs performance

**Options**:
1. **Accept regression** if maintainability gain > performance cost
2. **Optimize refactored code** to recover performance
3. **Revert** if performance critical and optimization not possible

### Performance Checklist

- [ ] Execution time acceptable (no major regression)
- [ ] Memory usage acceptable
- [ ] No performance-critical paths slower
- [ ] Profiling shows expected behavior

---

## 6. Integration Verification

### Dependency Verification

**Check Dependencies**:
- [ ] All imports still valid
- [ ] No circular dependencies introduced
- [ ] External dependencies unchanged
- [ ] API contracts maintained

### Integration Points

**Verify Integration**:
- [ ] Upstream callers still work
- [ ] Downstream dependencies still work
- [ ] Database interactions unchanged (or intentionally changed)
- [ ] Network calls unchanged
- [ ] File system interactions unchanged

### System-Level Smoke Tests

**Run Smoke Tests**:
```bash
# API endpoints
curl http://localhost:8000/api/health

# Key user workflows
python smoke_tests/critical_paths.py
```

**Smoke Test Checklist**:
- [ ] Application starts successfully
- [ ] Critical user workflows complete
- [ ] No obvious visual regressions (if UI)
- [ ] No error spikes in logs

---

## Gate Completion Summary

### Verification Results

**Test Verification**:
- Tests Passing: ☐ YES ☐ NO
- Coverage: ☐ Maintained ☐ Improved ☐ Regression

**Behavior Verification**:
- Behavior Preserved: ☐ YES ☐ NO
- Edge Cases: ☐ Verified ☐ Issues Found

**Metrics Verification**:
- Complexity: ☐ Improved ☐ Stable ☐ Worse
- Coupling: ☐ Improved ☐ Stable ☐ Worse
- Cohesion: ☐ Improved ☐ Stable ☐ Worse

**Quality Verification**:
- Linting: ☐ Clean ☐ Issues
- Readability: ☐ Improved ☐ Stable ☐ Worse
- Documentation: ☐ Updated ☐ Not Needed

**Performance Verification**:
- Execution Time: ☐ Faster ☐ Same ☐ Acceptable ☐ REGRESSION
- Memory: ☐ Less ☐ Same ☐ Acceptable ☐ REGRESSION

### Gate Status

**ALL checks must pass**:
- [ ] Tests: PASS
- [ ] Behavior: PASS
- [ ] Metrics: PASS (improved or stable)
- [ ] Quality: PASS
- [ ] Performance: PASS (acceptable)

**Gate Result**: ☐ PASS (proceed to Phase 6) ☐ FAIL (fix or revert)

---

## If Verification Fails

### Failure Response

**Do NOT proceed to debt tracking if ANY check fails.**

**Options**:

1. **Fix Issues**
   - Address specific failure
   - Re-run verification
   - Repeat until all checks pass

2. **Accept Trade-offs** (with documentation)
   - Example: Minor performance regression acceptable for major maintainability gain
   - MUST document in debt tracking (Phase 6)
   - Get stakeholder approval

3. **Revert Refactoring**
   - If issues too complex to fix
   - If trade-offs unacceptable
   - Return to last green state
   - Analyze failure
   - Retry with different approach

### Common Failure Patterns

**Test Failures**:
- Incomplete refactoring (missed call sites)
- Changed behavior unintentionally
- Tests need updating (rare - verify carefully)

**Performance Regression**:
- Introduced indirection overhead
- Increased memory allocations
- Less efficient algorithm

**Metrics Worse**:
- Wrong refactoring pattern chosen
- Incomplete refactoring
- Need to continue with related refactorings

---

## Integration with Workflow

**Previous Phase**: Implementation (Phase 4)
**Current Phase**: Verification (this file)
**Next Phase**: Debt Tracking (Phase 6)

**Workflow Position**:
```
Phase 3: Safety Check (GATE)
    ↓
Phase 4: Implementation
    ↓
Phase 5: Verification (GATE) ← YOU ARE HERE
    ├─→ All checks PASS → Phase 6: Debt Tracking
    └─→ Any check FAILS → Fix or Revert
```

---

## Verification Checklist Template

Use this template for each refactoring:

```markdown
## Refactoring: [Pattern Name] in [Component]

### Test Verification
- [ ] All tests passing: ___ passed, ___ failed
- [ ] Coverage: Before ___%, After ___% (±___%)

### Behavior Verification
- [ ] Behavior preserved: YES / NO
- [ ] Edge cases verified: YES / NO

### Metrics Verification
- [ ] Complexity: Before ___, After ___ (±___)
- [ ] LOC: Before ___, After ___ (±___)
- [ ] Status: Improved / Stable / Worse

### Quality Verification
- [ ] No new linting errors
- [ ] Readability improved
- [ ] Documentation updated

### Performance Verification
- [ ] Execution time: Before ___ms, After ___ms (±___%)
- [ ] Memory: Before ___MB, After ___MB (±___%)
- [ ] Status: Acceptable / REGRESSION

### Gate Status: PASS / FAIL
```

---

## Quick Reference

**5 Verification Categories**:
1. Tests (must be green)
2. Behavior (must be preserved)
3. Metrics (must improve or hold)
4. Quality (must maintain standards)
5. Performance (must be acceptable)

**Gate Enforcement**: ALL checks must pass before Phase 6

**If Fails**: Fix, accept with documentation, or revert

**Next Step**: After verification passes, proceed to `../tracking/debt-checklist.md` for ROI measurement.

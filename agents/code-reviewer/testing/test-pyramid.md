# Testing Pyramid Assessment

Systematic analysis of test distribution to ensure healthy testing strategy with appropriate ratios of unit, integration, and E2E tests.

---

## Ideal Distribution

A healthy testing pyramid follows this distribution:

- **Unit Tests**: 60-70% (fast, isolated, test individual functions/methods)
- **Integration Tests**: 20-30% (test component interactions, database, external services)
- **E2E Tests**: 5-10% (complete user workflows, full stack integration)

**Rationale**: Unit tests are fast and pinpoint failures. E2E tests are slow and brittle. The pyramid shape reflects test execution speed and maintenance cost.

---

## Analysis Checklist

When assessing test distribution:

- [ ] Count tests by type (unit, integration, E2E)
- [ ] Calculate test distribution percentages
- [ ] Identify if pyramid is inverted (too many E2E tests)
- [ ] Check if pyramid is missing a layer (e.g., no integration tests)
- [ ] Compare against ideal distribution targets

---

## Output Format

```markdown
## Testing Pyramid Assessment

**Current Distribution**:
- Unit Tests: [count] ([percent]%)
- Integration Tests: [count] ([percent]%)
- E2E Tests: [count] ([percent]%)
- Total: [count] tests

**Target Distribution**:
- Unit Tests: 60-70% ← [Current: X%] [OK: Good / Important: Too Few / Important: Too Many]
- Integration Tests: 20-30% ← [Current: Y%] [OK: Good / Suggestion: Too Few / Suggestion: Too Many]
- E2E Tests: 5-10% ← [Current: Z%] [OK: Good / Important: Too Few / Critical: Too Many]

**Assessment**: [Healthy Pyramid / Inverted Pyramid / Missing Layer / Flat Pyramid]
```

---

## Common Issues

### Issue 1: Inverted Pyramid (Too Many E2E Tests)

**Problem**: E2E tests exceed 15% of test suite

**Impact**:
- Slow test suite (E2E tests take 10-100x longer than unit tests)
- Brittle tests (E2E tests break when UI/infrastructure changes)
- Hard to debug (failures don't pinpoint root cause)
- High maintenance (E2E tests require more updates)

**Detection**:
- E2E test percentage > 15%
- Test suite runtime > 10 minutes
- Frequent test failures due to timing/environment issues

**Recommendation**: Convert E2E tests to unit/integration tests where possible

**Example Conversion**:
```python
# Current: E2E test (slow, brittle)
def test_calculate_order_total_e2e():
    response = client.post('/orders', json={
        'items': [{'price': 100, 'quantity': 1}]
    })
    assert response.json['total'] == 100

# Better: Unit test (fast, focused)
def test_calculate_order_total():
    order = Order(items=[Item(price=100, quantity=1)])
    assert order.calculate_total() == 100
```

**Target**: Increase unit tests to 60%+, reduce E2E tests to 10% or less

---

### Issue 2: Missing Layer (No Integration Tests)

**Problem**: Test suite has only unit and E2E tests (no integration tests)

**Impact**:
- Integration issues caught late (only in E2E tests)
- Gaps in component interaction testing
- Difficult to test database, API, external service integration

**Detection**:
- Integration test percentage = 0%
- E2E tests contain database/API testing logic

**Recommendation**: Add integration tests for component boundaries

**Example**:
```python
# Add integration test
def test_user_repository_save(db_session):
    """Integration test: repository + database"""
    repo = UserRepository(db_session)
    user = User(email="test@example.com")

    repo.save(user)

    saved = repo.find_by_email("test@example.com")
    assert saved.email == "test@example.com"
```

**Target**: Add 20-30% integration tests

---

### Issue 3: Flat Pyramid (Equal Distribution)

**Problem**: Similar number of unit, integration, and E2E tests

**Impact**:
- Slower than necessary (too many integration/E2E tests)
- Missing fast feedback (not enough unit tests)

**Detection**:
- Unit, integration, E2E tests all ~33%
- No clear pyramid shape

**Recommendation**: Shift tests down the pyramid (convert integration → unit, E2E → integration)

**Target**: Restore pyramid shape (60% unit, 25% integration, 10% E2E)

---

## Verification Commands

Check test distribution:

```bash
# pytest with coverage markers
pytest --co -q --collect-only | grep -E "(test_unit|test_integration|test_e2e)" | wc -l

# Jest test names
jest --listTests | grep -E "(\.unit\.|\.integration\.|\.e2e\.)" | wc -l

# Go test tags
go test -tags=unit -v ./... -run ^$ 2>&1 | grep -c "^==="
go test -tags=integration -v ./... -run ^$ 2>&1 | grep -c "^==="
```

---

## Priority Classification

**Critical**:
- Inverted pyramid (E2E > 20%)
- No unit tests (0%)

**Important**:
- Too few unit tests (< 50%)
- Too many E2E tests (10-20%)

**Suggestion**:
- Missing integration layer (0%)
- Slightly off distribution (within 10% of targets)

---

**Assessment complete when test distribution classified and recommendations provided.**

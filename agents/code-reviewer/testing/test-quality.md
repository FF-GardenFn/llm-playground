# Test Quality Assessment

**Purpose**: Evaluate test code quality beyond coverage - maintainability, readability, reliability.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (affects long-term maintainability)

**Principle**: Good tests are FIRST - Fast, Independent, Repeatable, Self-validating, Timely

---

## Overview

Test quality is as important as test coverage. Code-reviewer assesses:
- **Readability**: Tests are clear and understandable
- **Maintainability**: Tests are easy to update
- **Reliability**: Tests consistently pass/fail correctly
- **Independence**: Tests don't affect each other

---

## FIRST Principles

### 1. Fast

**Principle**: Tests should run quickly.

**Good - Fast Tests**:
```python
# GOOD: Unit test runs in milliseconds
def test_calculate_discount():
    result = calculate_discount(100, 0.1)
    assert result == 90

# Runs in < 1ms
```

**Bad - Slow Tests**:
```python
# BAD: Test depends on external services
def test_calculate_discount():
    # Makes actual API call (slow!)
    exchange_rate = fetch_exchange_rate_from_api()
    result = calculate_discount(100, 0.1, exchange_rate)
    assert result > 0

# Runs in 2+ seconds
```

**Targets**:
- **Unit tests**: < 10ms each
- **Integration tests**: < 100ms each
- **E2E tests**: < 5 seconds each
- **Full test suite**: < 5 minutes total

**Detection Heuristics**:
- Tests making network calls
- Tests accessing database without mocks
- Tests with `time.sleep()`

**Severity**: **Suggestion** (slow tests discourage running tests)

---

### 2. Independent

**Principle**: Tests should not depend on each other.

**Good - Independent Tests**:
```python
# GOOD: Each test sets up its own data
def test_create_user():
    user = User.objects.create(name="John")
    assert user.id is not None

def test_update_user():
    # Creates own user (independent)
    user = User.objects.create(name="Jane")
    user.name = "Jane Doe"
    user.save()
    assert user.name == "Jane Doe"

# Can run in any order
```

**Bad - Dependent Tests**:
```python
# BAD: Tests depend on each other
user_id = None

def test_create_user():
    global user_id
    user = User.objects.create(name="John")
    user_id = user.id  # Shared state!
    assert user.id is not None

def test_update_user():
    # Depends on test_create_user running first!
    user = User.objects.get(id=user_id)
    user.name = "John Doe"
    user.save()
    assert user.name == "John Doe"

# Fails if run in different order or test_create_user fails
```

**Detection Heuristics**:
- Tests sharing global state
- Tests with sequential numbering (`test_01_`, `test_02_`)
- Tests that fail when run in isolation

**Severity**: **Important** (brittle tests)

---

### 3. Repeatable

**Principle**: Tests should produce same result every time.

**Good - Deterministic Tests**:
```python
# GOOD: Fixed datetime for testing
from datetime import datetime
from unittest.mock import patch

def test_order_timestamp():
    fixed_time = datetime(2024, 1, 1, 12, 0, 0)
    with patch('django.utils.timezone.now', return_value=fixed_time):
        order = Order.objects.create()
        assert order.created_at == fixed_time

# Always passes
```

**Bad - Non-Deterministic Tests**:
```python
# BAD: Depends on current time
def test_order_timestamp():
    order = Order.objects.create()
    # Fails if test runs at midnight!
    assert order.created_at.hour == 12

# BAD: Depends on random values
def test_random_discount():
    discount = random.choice([0.1, 0.2, 0.3])
    result = calculate_discount(100, discount)
    assert result == 90  # Only passes 1/3 of the time!
```

**Detection Heuristics**:
- Tests using `datetime.now()` without mocking
- Tests using `random` without seeding
- Tests depending on external data (network, filesystem)

**Severity**: **Important** (flaky tests)

---

### 4. Self-Validating

**Principle**: Tests should have clear pass/fail without manual inspection.

**Good - Clear Assertions**:
```python
# GOOD: Test clearly passes or fails
def test_calculate_total():
    order = Order(items=[Item(price=10), Item(price=20)])
    total = order.calculate_total()
    assert total == 30  # Clear assertion

# GOOD: Multiple specific assertions
def test_create_user():
    user = User.objects.create(name="John", email="john@example.com")
    assert user.id is not None
    assert user.name == "John"
    assert user.email == "john@example.com"
```

**Bad - Manual Validation**:
```python
# BAD: Requires manual inspection
def test_generate_report():
    report = generate_report()
    print(report)  # Need to manually check output!

# BAD: No assertions
def test_create_user():
    user = User.objects.create(name="John")
    # No assertion - always passes!
```

**Detection Heuristics**:
- Tests with `print()` statements
- Tests without assertions
- Tests with only `assert True`

**Severity**: **Important**

---

### 5. Timely

**Principle**: Tests should be written at the right time (TDD: before code).

**Good - Test-Driven Development**:
```python
# GOOD: Test written first (TDD)
# Step 1: Write failing test
def test_calculate_discount():
    result = calculate_discount(100, 0.1)
    assert result == 90
    # Fails: calculate_discount doesn't exist

# Step 2: Implement minimal code to pass
def calculate_discount(total, rate):
    return total * (1 - rate)
    # Test passes

# Step 3: Refactor
```

**Detection**:
- New features without tests (tests added later)
- Tests added only after bugs discovered

**Severity**: **Suggestion**

---

## Test Quality Smells

### 1. Test Too Large

**Problem**: Test covers too much, hard to understand what's being tested.

**Bad**:
```python
# BAD: 50-line test
def test_order_processing():
    # Create user
    user = User.objects.create(name="John", email="john@example.com")

    # Create products
    product1 = Product.objects.create(name="Item 1", price=10)
    product2 = Product.objects.create(name="Item 2", price=20)

    # Create cart
    cart = Cart.objects.create(user=user)
    cart.items.add(product1, product2)

    # Process payment
    payment = Payment.objects.create(user=user, amount=30)

    # Create order
    order = Order.objects.create(user=user, cart=cart, payment=payment)

    # Verify order
    assert order.total == 30
    assert order.status == 'pending'
    # ... 20 more lines
```

**Good**:
```python
# GOOD: Focused tests
def test_order_total_calculation():
    order = create_test_order(items=[10, 20])
    assert order.total == 30

def test_order_initial_status():
    order = create_test_order()
    assert order.status == 'pending'

def test_order_payment_association():
    order = create_test_order(payment_amount=30)
    assert order.payment.amount == 30
```

**Detection Heuristics**:
- Tests > 20 lines
- Tests with multiple assertions on unrelated aspects
- Tests covering multiple features

**Severity**: **Suggestion**

---

### 2. Unclear Test Names

**Problem**: Test name doesn't describe what's being tested.

**Bad**:
```python
# BAD: Vague names
def test_user(): pass
def test_order(): pass
def test_1(): pass
def test_edge_case(): pass
```

**Good**:
```python
# GOOD: Descriptive names
def test_user_creation_sets_default_role(): pass
def test_order_total_includes_tax(): pass
def test_discount_not_applied_to_sale_items(): pass
def test_empty_cart_raises_validation_error(): pass
```

**Pattern**: `test_<what>_<scenario>_<expected_result>`

**Detection Heuristics**:
- Generic test names (`test_user`, `test_1`)
- Test names without expected behavior

**Severity**: **Suggestion**

---

### 3. Assertion Roulette

**Problem**: Multiple assertions make it unclear which failed.

**Bad**:
```python
# BAD: Which assertion failed?
def test_user_creation():
    user = User.objects.create(name="John", email="john@example.com")
    assert user.id is not None
    assert user.name == "John"
    assert user.email == "john@example.com"
    assert user.is_active == True
    assert user.created_at is not None
    # If assertion 3 fails, need to debug to find which
```

**Good**:
```python
# GOOD: Clear assertion messages
def test_user_creation():
    user = User.objects.create(name="John", email="john@example.com")
    assert user.id is not None, "User ID should be set"
    assert user.name == "John", f"Expected name 'John', got '{user.name}'"
    assert user.email == "john@example.com", f"Expected email 'john@example.com', got '{user.email}'"
    assert user.is_active == True, "New users should be active"
    assert user.created_at is not None, "Created timestamp should be set"
```

**Or separate tests**:
```python
#  BETTER: One concept per test
def test_user_creation_sets_id(): pass
def test_user_creation_sets_name(): pass
def test_user_creation_sets_email(): pass
def test_user_creation_activates_user(): pass
def test_user_creation_sets_timestamp(): pass
```

**Detection Heuristics**:
- Tests with > 5 assertions
- No assertion messages

**Severity**: **Suggestion**

---

### 4. Test Fixtures Obscure Test

**Problem**: Test setup so complex, hard to understand what's being tested.

**Bad**:
```python
# BAD: Complex fixture obscures test
@pytest.fixture
def setup_complex_scenario():
    user = User.objects.create(name="John")
    for i in range(10):
        product = Product.objects.create(name=f"Product {i}")
        Order.objects.create(user=user, product=product)
    # ... 20 more lines
    return user

def test_user_order_count(setup_complex_scenario):
    user = setup_complex_scenario
    assert user.orders.count() == 10  # Where did 10 come from?
```

**Good**:
```python
# GOOD: Inline setup makes test clear
def test_user_order_count():
    user = User.objects.create(name="John")
    # Create 10 orders
    for i in range(10):
        Order.objects.create(user=user, product=create_test_product())

    assert user.orders.count() == 10  # Clear why expecting 10
```

**Detection Heuristics**:
- Fixtures > 20 lines
- Fixtures used by only one test
- Test requires reading fixture to understand

**Severity**: **Suggestion**

---

### 5. Brittle Tests

**Problem**: Tests break easily when code changes (even when behavior is correct).

**Bad**:
```python
# BAD: Tests implementation details
def test_calculate_total():
    order = Order()
    order._internal_cache = {}  # Testing private implementation!
    order.add_item(Item(price=10))
    assert '_internal_cache' in order.__dict__  # Brittle!
```

**Good**:
```python
# GOOD: Tests public behavior
def test_calculate_total():
    order = Order()
    order.add_item(Item(price=10))
    assert order.calculate_total() == 10  # Tests behavior, not implementation
```

**Detection Heuristics**:
- Tests accessing private attributes (`_name`, `__name`)
- Tests checking internal state instead of output
- Tests coupling to implementation

**Severity**: **Suggestion**

---

### 6. Test Code Duplication

**Problem**: Copy-pasted test code.

**Bad**:
```python
# BAD: Duplicated test code
def test_create_user_with_valid_email():
    user = User(name="John", email="john@example.com", age=25)
    user.validate()
    user.save()
    assert user.id is not None

def test_create_user_with_valid_age():
    user = User(name="Jane", email="jane@example.com", age=30)
    user.validate()
    user.save()
    assert user.id is not None
```

**Good**:
```python
# GOOD: Extract helper
def create_valid_user(**overrides):
    defaults = {'name': 'John', 'email': 'john@example.com', 'age': 25}
    defaults.update(overrides)
    user = User(**defaults)
    user.validate()
    user.save()
    return user

def test_create_user_with_valid_email():
    user = create_valid_user()
    assert user.id is not None

def test_create_user_with_valid_age():
    user = create_valid_user(name='Jane', age=30)
    assert user.id is not None
```

**Detection Heuristics**:
- Similar test code repeated
- No test helpers or factories

**Severity**: **Suggestion**

---

## Review Checklist

### Phase 2: Manual Review

**FIRST Principles**:
- [ ] Are tests fast (< 10ms for unit tests)?
- [ ] Are tests independent (can run in any order)?
- [ ] Are tests repeatable (no random/time dependencies)?
- [ ] Are tests self-validating (clear assertions)?
- [ ] Are tests timely (written with or before code)?

**Test Quality**:
- [ ] Are test names descriptive?
- [ ] Are tests focused (one concept per test)?
- [ ] Are assertions clear with messages?
- [ ] Are test fixtures simple?
- [ ] Do tests avoid testing implementation details?

**Maintainability**:
- [ ] Is test code DRY (no duplication)?
- [ ] Are test helpers available?
- [ ] Are tests readable?
- [ ] Would tests survive refactoring?

---

## Summary

**FIRST Principles**:
- **Fast**: < 10ms unit tests
- **Independent**: No shared state
- **Repeatable**: Deterministic results
- **Self-Validating**: Clear assertions
- **Timely**: Written with/before code

**Test Quality Smells**:
1. Test too large (> 20 lines)
2. Unclear names
3. Assertion roulette (many assertions)
4. Complex fixtures
5. Brittle tests (test implementation)
6. Test code duplication

**Detection**:
- Phase 2: Manual test quality review
- Look for slow tests, flaky tests, unclear tests

**Priority**: **Important** (affects maintainability)

---

## FIRST Principles Assessment (From Commands)

**FIRST Principles**:
- **Fast**: Tests run quickly (< 10ms for unit tests)
- **Independent**: Tests don't depend on each other
- **Repeatable**: Tests produce same result every time
- **Self-validating**: Clear pass/fail without manual inspection
- **Timely**: Tests written with or before code (TDD)

### Quality Checklist

Check each test file for:

**Fast**:
- [ ] Unit tests < 10ms
- [ ] Integration tests < 100ms
- [ ] Full suite < 5 minutes
- [ ] No unnecessary delays (sleep)

**Independent**:
- [ ] Tests can run in any order
- [ ] No shared global state
- [ ] Each test sets up own data
- [ ] No sequential numbering (test_01, test_02)

**Repeatable**:
- [ ] No flaky tests
- [ ] Time/date mocked
- [ ] Random values seeded
- [ ] No external dependencies (network, filesystem)

**Self-validating**:
- [ ] Clear assertions
- [ ] No print() statements for validation
- [ ] No manual inspection required
- [ ] Specific error messages

**Timely**:
- [ ] Tests exist for all new features
- [ ] Tests updated with code changes
- [ ] High-risk code has tests

**Output Format**:
```markdown
## Test Quality Assessment (FIRST Principles)

### Fast
- Unit tests average: [X]ms [OK < 10ms / WARN Slow]
- Integration tests average: [X]ms [OK < 100ms / WARN Slow]
- Full suite runtime: [X] seconds [OK < 5min / WARN Slow]

### Independent
- Tests can run in any order: [YES / NO]
- Shared global state detected: [YES / NO]
- Sequential test numbering: [YES / NO]

### Repeatable
- Flaky tests detected: [YES / NO] ([count] flaky)
- Time/date mocked: [YES / NO]
- Random values controlled: [YES / NO]

### Self-validating
- All tests have assertions: [YES / NO]
- Print statements for validation: [YES / NO]
- Assertion messages present: [YES / NO]

### Timely
- New features have tests: [YES / NO]
- Test coverage maintained: [YES / NO]

**Overall Quality**: [Excellent / Good / Needs Improvement]
```

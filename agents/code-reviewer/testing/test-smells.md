---
title: Test Smells Detection
description: Common test anti-patterns and how to fix them
priority: Important
category: Testing Quality
---

# Test Smells Detection

Common test anti-patterns that reduce test maintainability, clarity, and effectiveness.

---

## Test Smell Categories

### 1. Test Too Large

**Smell**: Tests exceeding 20-30 lines, testing multiple scenarios

**Detection Criteria**:
- Test method > 30 lines
- Multiple unrelated assertions
- Complex setup with many variables
- Testing multiple code paths in single test

**Example**:
```python
# BAD: 50-line test covering too much
def test_order_processing():
    # Create user
    user = User.objects.create(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )
    # Create products
    product1 = Product.objects.create(
        name='Product 1',
        price=100.00,
        stock=50
    )
    product2 = Product.objects.create(
        name='Product 2',
        price=50.00,
        stock=30
    )
    # Create order
    order = Order.objects.create(user=user)
    order.add_item(product1, quantity=2)
    order.add_item(product2, quantity=3)
    # Calculate total
    total = order.calculate_total()
    assert total == 350.00
    # Apply discount
    order.apply_discount(0.1)
    assert order.total == 315.00
    # Process payment
    payment = Payment.process(order, 'credit_card')
    assert payment.status == 'success'
    # Send email
    assert len(mail.outbox) == 1
    # ... more lines
```

**Fix**:
```python
# GOOD: Split into focused tests
def test_calculate_order_total_with_multiple_items():
    order = create_test_order()
    order.add_item(product1, quantity=2)  # $200
    order.add_item(product2, quantity=3)  # $150
    assert order.calculate_total() == 350.00

def test_apply_discount_to_order():
    order = create_test_order_with_total(350.00)
    order.apply_discount(0.1)
    assert order.total == 315.00

def test_process_payment_success():
    order = create_test_order_with_total(315.00)
    payment = Payment.process(order, 'credit_card')
    assert payment.status == 'success'
```

**Priority**: Important

---

### 2. Unclear Test Names

**Smell**: Test names that don't describe what they test

**Detection Criteria**:
- Generic names: `test_user()`, `test_1()`, `test_method()`
- Non-descriptive: `test_edge_case()`, `test_bug_fix()`
- Sequential numbering: `test_01()`, `test_02()`

**Example**:
```python
# BAD: Vague names
def test_user():
    pass

def test_1():
    pass

def test_edge_case():
    pass

def test_bug_fix():
    pass
```

**Fix**:
```python
# GOOD: Descriptive names
def test_user_creation_sets_default_role_to_customer():
    pass

def test_empty_cart_raises_validation_error():
    pass

def test_negative_quantity_rejected():
    pass

def test_duplicate_email_registration_prevented():
    pass
```

**Naming Pattern**: `test_[what]_[condition]_[expected_result]()`

**Priority**: Important

---

### 3. Assertion Roulette

**Smell**: Too many assertions in a single test, making failures unclear

**Detection Criteria**:
- More than 3-5 assertions per test
- Assertions without descriptive messages
- Testing multiple properties without clear grouping

**Example**:
```python
# BAD: Which assertion failed?
def test_user_creation():
    user = User.objects.create(username='john', email='john@example.com')
    assert user.id is not None
    assert user.username == 'john'
    assert user.email == 'john@example.com'
    assert user.is_active == True
    assert user.is_staff == False
    assert user.date_joined is not None
    assert user.last_login is None
    assert user.role == 'customer'
    assert user.email_verified == False
    # ... 10 more assertions
```

**Fix**:
```python
# GOOD: Focused tests with clear assertions
def test_user_creation_generates_id():
    user = create_test_user()
    assert user.id is not None, "User ID should be generated on creation"

def test_user_creation_sets_default_active_status():
    user = create_test_user()
    assert user.is_active == True, "New users should be active by default"

def test_user_creation_sets_default_role():
    user = create_test_user()
    assert user.role == 'customer', "Default role should be 'customer'"

def test_user_creation_sets_date_joined():
    user = create_test_user()
    assert user.date_joined is not None
    assert user.last_login is None
```

**Priority**: Important

---

### 4. Brittle Tests

**Smell**: Tests that break on refactoring or implementation changes

**Detection Criteria**:
- Testing private methods or internal state
- Over-mocking (mocking business logic)
- Testing implementation details rather than behavior
- Hard-coded values instead of semantic references

**Example**:
```python
# BAD: Testing private methods and implementation details
def test_user_save():
    user = User(username='john')
    mock_repo = Mock()
    user.repository = mock_repo

    user.save()

    # Testing private implementation
    mock_repo._internal_save.assert_called()
    mock_repo._validate.assert_called()
    mock_repo._audit_log.assert_called()
    assert user._state == 'persisted'

# BAD: Over-mocking business logic
def test_calculate_discount():
    mock_calculator = Mock()
    mock_calculator.calculate.return_value = 90
    result = mock_calculator.calculate(100, 0.1)
    assert result == 90  # Testing the mock, not real code!
```

**Fix**:
```python
# GOOD: Testing public interface and behavior
def test_user_save_persists_to_database():
    user = User(username='john')
    user.save()

    # Test behavior, not implementation
    saved_user = User.objects.get(username='john')
    assert saved_user.id is not None

# GOOD: Test real business logic
def test_calculate_discount_applies_percentage():
    result = calculate_discount(100, 0.1)
    assert result == 90  # Testing real implementation
```

**Priority**: Critical

---

### 5. Test Interdependence

**Smell**: Tests that depend on execution order or shared state

**Detection Criteria**:
- Tests fail when run in isolation
- Tests pass when run in specific order
- Shared global state between tests
- Sequential test numbering (test_01, test_02, test_03)

**Example**:
```python
# BAD: Tests depend on order
class TestUserWorkflow:
    user_id = None

    def test_01_create_user(self):
        user = User.objects.create(username='john')
        self.user_id = user.id  # Shared state
        assert user.id is not None

    def test_02_update_user(self):
        user = User.objects.get(id=self.user_id)  # Depends on test_01
        user.email = 'john@example.com'
        user.save()
        assert user.email == 'john@example.com'

    def test_03_delete_user(self):
        user = User.objects.get(id=self.user_id)  # Depends on test_01
        user.delete()
        assert User.objects.filter(id=self.user_id).count() == 0
```

**Fix**:
```python
# GOOD: Independent tests
class TestUserOperations:
    def setUp(self):
        # Each test gets its own user
        self.user = User.objects.create(username='john')

    def test_user_creation_generates_id(self):
        user = User.objects.create(username='alice')
        assert user.id is not None

    def test_user_email_update(self):
        user = User.objects.create(username='bob')
        user.email = 'bob@example.com'
        user.save()

        updated_user = User.objects.get(id=user.id)
        assert updated_user.email == 'bob@example.com'

    def test_user_deletion(self):
        user = User.objects.create(username='charlie')
        user_id = user.id
        user.delete()

        assert User.objects.filter(id=user_id).count() == 0
```

**Priority**: Critical

---

### 6. Slow Tests

**Smell**: Tests that take too long to run

**Detection Criteria**:
- Unit tests > 10ms
- Integration tests > 100ms
- Unnecessary sleeps or delays
- Real network calls in tests
- Full database operations instead of in-memory

**Example**:
```python
# BAD: Slow test with sleep
def test_async_operation():
    start_operation()
    time.sleep(5)  # Wait for completion
    result = get_result()
    assert result == 'completed'

# BAD: Real network call
def test_api_integration():
    response = requests.get('https://api.example.com/data')
    assert response.status_code == 200
```

**Fix**:
```python
# GOOD: Mock delays
def test_async_operation():
    with patch('time.sleep'):  # Mock sleep
        start_operation()
        result = get_result()
        assert result == 'completed'

# GOOD: Mock network calls
def test_api_integration():
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(status_code=200)
        response = requests.get('https://api.example.com/data')
        assert response.status_code == 200
```

**Priority**: Important

---

## Detection Summary

| Test Smell | Detection Pattern | Priority | Fix Strategy |
|------------|------------------|----------|--------------|
| Test Too Large | > 30 lines, multiple assertions | Important | Split into focused tests |
| Unclear Names | Generic/vague names | Important | Descriptive, behavior-based names |
| Assertion Roulette | > 5 assertions | Important | One concept per test |
| Brittle Tests | Testing implementation | Critical | Test behavior, not internals |
| Interdependence | Tests fail in isolation | Critical | Independent setup/teardown |
| Slow Tests | Unit > 10ms, Integration > 100ms | Important | Mock I/O, use in-memory DB |

---

## Smell Detection Checklist

When reviewing tests, check for:

- [ ] Each test under 30 lines
- [ ] Test names describe behavior and expectation
- [ ] No more than 3-5 assertions per test
- [ ] No testing of private methods or internal state
- [ ] Tests can run in any order
- [ ] No shared global state between tests
- [ ] Unit tests complete in < 10ms
- [ ] No sleep() calls (use mocking)
- [ ] External dependencies mocked

---

## References

- Test smell catalog: [xUnit Test Patterns](http://xunitpatterns.com/)
- FIRST principles: `testing/test-quality.md`
- Mocking guidelines: `testing/mocking.md`

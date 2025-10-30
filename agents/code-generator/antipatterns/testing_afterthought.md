# Anti-Pattern: Testing as Afterthought

## Problem
Writing tests after code is complete. Tests become documentation of implementation, not specification of behavior. Hard-to-test code signals design problems.

## Example: Wrong Approach

```
1. Write 200 lines of feature code
2. Feature "complete"
3. Try to write tests
4. Code is hard to test (too many dependencies, side effects)
5. Write fragile tests that mock everything
6. Tests break when implementation changes (not behavior)
```

**Problems:**
- Code designed without testing in mind
- Dependencies hardcoded (can't inject mocks)
- Side effects everywhere (hard to verify)
- Tests test implementation, not behavior
- Refactoring breaks tests

**Example Code:**
```python
def process_order():
    # Hardcoded dependencies
    db = Database('prod_connection')
    payment = PaymentGateway('live_api_key')
    email = EmailService('smtp.gmail.com')

    # Complex logic with side effects
    order = db.get_order(123)
    if order.total > 0:
        result = payment.charge(order.total)
        if result.success:
            db.mark_paid(order.id)
            email.send_receipt(order.email)
            return True
    return False
```

**How to test this?**
- Need real database
- Need real payment gateway
- Need real email service
- Tests are slow, fragile, expensive

## Correct Approach: Test-Driven Development

```
1. Write failing test (specification)
2. Write minimal code to pass
3. Refactor (improve design while tests green)
4. Repeat
```

**Example:**

**Step 1: Write test (RED)**
```python
def test_process_order_charges_payment():
    # Arrange
    order = Order(id=123, total=100.0)
    db = Mock(spec=Database)
    db.get_order.return_value = order
    payment = Mock(spec=PaymentGateway)
    payment.charge.return_value = PaymentResult(success=True)

    # Act
    result = process_order(123, db, payment)

    # Assert
    assert result is True
    payment.charge.assert_called_once_with(100.0)
    db.mark_paid.assert_called_once_with(123)
```

**Step 2: Implement (GREEN)**
```python
def process_order(order_id, db, payment):
    """Process order payment.

    Args:
        order_id: Order ID to process
        db: Database instance (injectable)
        payment: Payment gateway instance (injectable)

    Returns:
        bool: True if successful
    """
    order = db.get_order(order_id)
    if order.total <= 0:
        return False

    result = payment.charge(order.total)
    if result.success:
        db.mark_paid(order.id)
        return True
    return False
```

**Benefits:**
- Dependencies injectable (easy to test)
- Side effects explicit (clear I/O)
- Behavior-driven (tests specify what, not how)
- Refactorable (tests don't break when implementation changes)

## How Structure Prevents This

- Implementation phase requires tests/ directory
- phases/03_implementation/outputs.md lists tests as REQUIRED artifact
- Cannot declare implementation complete without test_results.md
- TDD cycle embedded in phase structure

## Key Lesson

**Tests are not documentation of code.**
**Tests are specification of behavior.**

Write tests first:
- Clarifies what code should do
- Drives better design (testable = maintainable)
- Catches bugs immediately
- Enables confident refactoring

**Rule:** If code is hard to test, code is hard to use. Redesign.

# Error Handling Architecture

**Purpose**: Assess error handling strategy, exception design, and recovery patterns during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (affects robustness and maintainability)

**Refactorable**: ⚠️ PARTIALLY (some patterns can be improved via refactoring)

---

## Overview

Good error handling ensures:
- **Robustness**: System handles errors gracefully
- **Debuggability**: Errors provide useful information
- **User Experience**: Clear, actionable error messages
- **Recovery**: System can recover from failures

---

## Error Handling Principles

### 1. Use Exceptions, Not Error Codes

**Good - Exceptions**:
```python
# ✅ GOOD: Exceptions separate error handling from business logic
def get_user(user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user

# Clean calling code
try:
    user = get_user(123)
    process_user(user)
except UserNotFoundError as e:
    logger.error(f"User lookup failed: {e}")
    return "User not found", 404
```

**Bad - Error Codes**:
```python
# ❌ BAD: Error codes mixed with business logic
def get_user(user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return None, -1  # Error code
    return user, 0

# Cluttered calling code
user, error_code = get_user(123)
if error_code != 0:
    logger.error("User lookup failed")
    return "User not found", 404
else:
    process_user(user)
```

**Detection Heuristics**:
- Functions returning tuples with error codes
- Magic numbers for error states (-1, 0, 1)
- No exceptions raised for errors

**Severity**: **Important**

---

### 2. Specific Exception Types

**Principle**: Use specific exceptions, not generic ones.

**Good - Specific Exceptions**:
```python
# ✅ GOOD: Specific exception types
class UserNotFoundError(Exception):
    """Raised when user doesn't exist"""
    pass

class InsufficientBalanceError(Exception):
    """Raised when account balance too low"""
    pass

def withdraw(account, amount):
    if account.balance < amount:
        raise InsufficientBalanceError(
            f"Balance {account.balance} < {amount}"
        )
    account.balance -= amount

# Caller can handle specific errors
try:
    withdraw(account, 100)
except InsufficientBalanceError:
    print("Cannot withdraw: insufficient balance")
except UserNotFoundError:
    print("Account not found")
```

**Bad - Generic Exceptions**:
```python
# ❌ BAD: Generic exceptions
def withdraw(account, amount):
    if account.balance < amount:
        raise Exception("Withdrawal failed")  # Too generic!
    account.balance -= amount

# Caller can't distinguish error types
try:
    withdraw(account, 100)
except Exception as e:  # Catches everything!
    print("Something went wrong")
```

**Detection Heuristics**:
- `raise Exception()` instead of custom exceptions
- `raise ValueError()` for domain errors
- Catching `Exception` without re-raising

**Severity**: **Important**

---

### 3. Don't Swallow Exceptions

**Principle**: Never silently ignore exceptions.

**Good - Handle or Propagate**:
```python
# ✅ GOOD: Log and handle appropriately
def process_payment(order):
    try:
        charge_card(order.total)
    except PaymentError as e:
        logger.error(f"Payment failed for order {order.id}: {e}")
        notify_admin(order, e)
        raise  # Re-raise for caller to handle

# ✅ GOOD: Specific handling
def process_payment(order):
    try:
        charge_card(order.total)
    except PaymentError as e:
        logger.error(f"Payment failed: {e}")
        order.status = 'payment_failed'
        order.save()
        # Don't re-raise - error handled
```

**Bad - Silent Failure**:
```python
# ❌ BAD: Swallowing exception
def process_payment(order):
    try:
        charge_card(order.total)
    except Exception:
        pass  # Silent failure!

# User thinks payment succeeded, but it didn't!
```

**Detection Heuristics**:
- `except: pass` or `except Exception: pass`
- No logging in exception handler
- Empty exception handlers

**Severity**: **Critical** (causes silent failures)

---

### 4. Finally Blocks for Cleanup

**Principle**: Always clean up resources, even on errors.

**Good - Resource Cleanup**:
```python
# ✅ GOOD: Finally ensures cleanup
def process_file(filename):
    f = open(filename)
    try:
        data = f.read()
        process_data(data)
    except IOError as e:
        logger.error(f"File processing failed: {e}")
        raise
    finally:
        f.close()  # Always closes, even on exception

# ✅ BETTER: Context manager
def process_file(filename):
    try:
        with open(filename) as f:
            data = f.read()
            process_data(data)
    except IOError as e:
        logger.error(f"File processing failed: {e}")
        raise
```

**Bad - No Cleanup**:
```python
# ❌ BAD: File not closed on exception
def process_file(filename):
    f = open(filename)
    data = f.read()
    process_data(data)
    f.close()  # Never reached if exception!
```

**Detection Heuristics**:
- Resource allocation without `finally` or context manager
- `open()` without `with`
- `.close()` not in `finally` block

**Severity**: **Important** (resource leaks)

---

### 5. Exception Chaining

**Principle**: Preserve original exception context.

**Good - Preserve Context**:
```python
# ✅ GOOD: Exception chaining
def save_user(user):
    try:
        user.save()
    except DatabaseError as e:
        logger.error(f"Failed to save user: {e}")
        raise UserSaveError("User save failed") from e  # Chain

# Traceback shows both exceptions:
# UserSaveError: User save failed
#   Caused by: DatabaseError: Connection timeout
```

**Bad - Lost Context**:
```python
# ❌ BAD: Original exception lost
def save_user(user):
    try:
        user.save()
    except DatabaseError as e:
        logger.error(f"Failed to save user: {e}")
        raise UserSaveError("User save failed")  # Context lost!

# Traceback only shows UserSaveError
```

**Detection Heuristics**:
- Re-raising different exception without `from e`
- Catching and raising new exception without chaining

**Severity**: **Suggestion** (improves debugging)

---

### 6. Validation at Boundaries

**Principle**: Validate input at system boundaries.

**Good - Boundary Validation**:
```python
# ✅ GOOD: Validate at API boundary
@app.route('/users', methods=['POST'])
def create_user():
    # Validate input immediately
    if not request.json:
        return jsonify({'error': 'Request body required'}), 400

    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in request.json:
            return jsonify({'error': f'Missing field: {field}'}), 400

    try:
        user = user_service.create_user(request.json)
        return jsonify(user), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 422

# ✅ GOOD: Validate in service layer too
class UserService:
    def create_user(self, user_data):
        # Additional domain validation
        if len(user_data['name']) < 3:
            raise ValidationError("Name must be at least 3 characters")

        if not is_valid_email(user_data['email']):
            raise ValidationError("Invalid email format")

        return self.user_repo.save(user_data)
```

**Bad - No Validation**:
```python
# ❌ BAD: No input validation
@app.route('/users', methods=['POST'])
def create_user():
    # No validation!
    user = User.objects.create(**request.json)
    return jsonify(user), 201

# Crashes on invalid input:
# - Missing fields
# - Wrong types
# - Invalid values
```

**Detection Heuristics**:
- No validation at API endpoints
- Direct database writes without validation
- No type checking

**Severity**: **Important**

---

### 7. Defensive Programming

**Principle**: Check preconditions, fail fast.

**Good - Precondition Checks**:
```python
# ✅ GOOD: Check preconditions
def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

def process_order(order):
    if order is None:
        raise ValueError("Order cannot be None")
    if order.total <= 0:
        raise ValueError("Order total must be positive")
    if not order.items:
        raise ValueError("Order must have items")

    # Proceed with processing
```

**Bad - No Checks**:
```python
# ❌ BAD: Assumes valid input
def divide(a, b):
    return a / b  # Crashes on division by zero

def process_order(order):
    # Crashes if order is None
    total = order.total
```

**Detection Heuristics**:
- No parameter validation
- No null checks
- No range checks

**Severity**: **Suggestion**

---

### 8. Error Recovery

**Principle**: Attempt recovery when possible.

**Good - Retry with Backoff**:
```python
# ✅ GOOD: Retry transient failures
import time

def fetch_data_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed

            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Request failed (attempt {attempt+1}): {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
```

**Good - Fallback Value**:
```python
# ✅ GOOD: Use fallback on error
def get_user_preferences(user_id):
    try:
        return PreferenceService.get(user_id)
    except ServiceUnavailableError:
        logger.warning("Preference service unavailable, using defaults")
        return DEFAULT_PREFERENCES
```

**Detection Heuristics**:
- No retry logic for transient errors
- No fallbacks for non-critical data
- System fails hard on recoverable errors

**Severity**: **Suggestion**

---

### 9. Logging Errors

**Principle**: Log errors with context.

**Good - Contextual Logging**:
```python
# ✅ GOOD: Structured logging with context
import logging

logger = logging.getLogger(__name__)

def process_payment(order_id, amount):
    try:
        order = Order.objects.get(id=order_id)
        charge_card(order.user.card, amount)
        logger.info(
            "Payment processed successfully",
            extra={
                'order_id': order_id,
                'amount': amount,
                'user_id': order.user.id
            }
        )
    except PaymentError as e:
        logger.error(
            "Payment processing failed",
            extra={
                'order_id': order_id,
                'amount': amount,
                'error': str(e)
            },
            exc_info=True  # Include traceback
        )
        raise
```

**Bad - Poor Logging**:
```python
# ❌ BAD: Vague logging
def process_payment(order_id, amount):
    try:
        order = Order.objects.get(id=order_id)
        charge_card(order.user.card, amount)
    except PaymentError:
        logger.error("Error")  # No context!
        raise
```

**Detection Heuristics**:
- No logging in exception handlers
- Logging without context (order ID, user ID)
- No `exc_info=True` for tracebacks

**Severity**: **Suggestion**

---

### 10. User-Friendly Error Messages

**Principle**: Errors should be actionable for users.

**Good - Clear Messages**:
```python
# ✅ GOOD: User-friendly error messages
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user = user_service.create_user(request.json)
        return jsonify(user), 201
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'User data validation failed',
                'details': e.messages,  # Field-level errors
                'help': 'Please check your input and try again'
            }
        }), 422
    except Exception as e:
        logger.exception("Unexpected error creating user")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred',
                'help': 'Please contact support if the problem persists'
            }
        }), 500
```

**Bad - Technical Errors Exposed**:
```python
# ❌ BAD: Expose technical details to user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user = user_service.create_user(request.json)
        return jsonify(user), 201
    except Exception as e:
        # Exposes stack trace, database details, etc.
        return jsonify({'error': str(e)}), 500
```

**Detection Heuristics**:
- Stack traces returned to users
- Database errors exposed
- No user-friendly messages

**Severity**: **Important** (security + UX)

---

## Review Checklist

### Phase 2: Manual Review

**Exception Usage**:
- [ ] Are exceptions used (not error codes)?
- [ ] Are specific exception types defined?
- [ ] Are domain exceptions separate from technical exceptions?

**Error Handling**:
- [ ] Are exceptions caught at appropriate level?
- [ ] Are exceptions logged with context?
- [ ] Are exceptions swallowed (silent failures)?

**Resource Cleanup**:
- [ ] Are resources cleaned up in `finally` blocks?
- [ ] Are context managers used for resources?
- [ ] Is cleanup guaranteed even on exceptions?

**Validation**:
- [ ] Is input validated at boundaries?
- [ ] Are preconditions checked?
- [ ] Are error messages clear and actionable?

**Recovery**:
- [ ] Is retry logic implemented for transient errors?
- [ ] Are fallbacks available for non-critical data?
- [ ] Can system recover gracefully?

**User Experience**:
- [ ] Are error messages user-friendly?
- [ ] Are technical details hidden from users?
- [ ] Are errors actionable?

---

## Summary

**Error Handling Principles**:
1. Use exceptions, not error codes
2. Specific exception types
3. Don't swallow exceptions
4. Finally blocks for cleanup
5. Exception chaining (preserve context)
6. Validation at boundaries
7. Defensive programming (preconditions)
8. Error recovery (retry, fallback)
9. Logging with context
10. User-friendly messages

**Common Violations**:
- Error codes instead of exceptions
- Generic exceptions (`Exception`, `ValueError`)
- Silent failures (`except: pass`)
- No resource cleanup
- No validation
- Technical errors exposed to users

**Detection**:
- Phase 2: Manual error handling review
- Look for swallowed exceptions, missing cleanup, poor validation

**Refactorable**:
- ⚠️ PARTIALLY - Some patterns improvable
- Some require error handling redesign

**Priority**: **Important** (affects robustness, debuggability, UX)

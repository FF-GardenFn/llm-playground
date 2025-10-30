# Clean Code Principles

**Purpose**: Guidelines for assessing code quality beyond smells - readability, maintainability, documentation.

**Phase**: Phase 2 (Manual Review)

**Priority**: Suggestion (quality improvements)

**Source**: Robert C. Martin's "Clean Code" principles

---

## Overview

Clean code is code that is easy to read, understand, and modify. Code-reviewer evaluates clean code principles during Phase 2 manual review to provide suggestions for improving code quality.

**Key Question**: Can a developer unfamiliar with this code understand it quickly?

---

## Core Principles

### 1. Meaningful Names

**Principle**: Names should reveal intent and be pronounceable.

**Good Practices**:

```python
# ❌ BAD: Cryptic names
def calc(d):
    return d * 0.85

x = calc(100)

# ✅ GOOD: Meaningful names
def calculate_discounted_price(original_price):
    DISCOUNT_RATE = 0.85
    return original_price * DISCOUNT_RATE

discounted_price = calculate_discounted_price(100)
```

**Naming Conventions**:

**Variables**:
- Use nouns: `user`, `order`, `payment_processor`
- Be specific: `user_email` not `data`
- Avoid abbreviations: `customer` not `cust`
- Use searchable names: `MAX_RETRY_COUNT` not `5`

**Functions**:
- Use verbs: `get_user()`, `calculate_total()`, `send_email()`
- Be descriptive: `find_user_by_email()` not `find()`
- Avoid generic names: `process_data()` → `validate_user_input()`

**Classes**:
- Use nouns: `User`, `OrderProcessor`, `EmailService`
- Avoid suffixes like `Manager`, `Data`, `Info` (be specific)
- Single Responsibility Principle in name: `UserAuthenticator` not `UserManager`

**Example - Before/After**:
```python
# ❌ BAD: Poor naming
class UM:
    def p(self, u):
        if u.a:
            return True
        return False

# ✅ GOOD: Clean naming
class UserAuthenticator:
    def is_user_authenticated(self, user):
        if user.is_active:
            return True
        return False
```

**Severity**: **Suggestion** (improves readability)

---

### 2. Functions Should Do One Thing

**Principle**: A function should do one thing, do it well, and do it only.

**Detection**:
- Function has multiple responsibilities
- Function name contains "and" (`save_and_send()`)
- Function has high cyclomatic complexity
- Function has multiple levels of abstraction

**Example - Problem**:
```python
# ❌ BAD: Function does too many things
def process_order(order):
    # Validate order
    if not order.customer_id:
        raise ValueError("Missing customer")

    # Calculate total
    total = sum(item.price * item.quantity for item in order.items)

    # Apply discount
    if order.customer.is_premium:
        total *= 0.9

    # Save to database
    db.save(order)

    # Send email
    email.send(order.customer.email, f"Order #{order.id} confirmed")

    # Log event
    logger.info(f"Order {order.id} processed")

    return total
```

**Fix - Single Responsibility**:
```python
# ✅ GOOD: Each function does one thing
def process_order(order):
    validate_order(order)
    total = calculate_order_total(order)
    save_order(order)
    notify_customer(order)
    log_order_processed(order)
    return total

def validate_order(order):
    if not order.customer_id:
        raise ValueError("Missing customer")

def calculate_order_total(order):
    total = sum(item.price * item.quantity for item in order.items)
    return apply_customer_discount(order.customer, total)

def apply_customer_discount(customer, total):
    if customer.is_premium:
        return total * 0.9
    return total

def save_order(order):
    db.save(order)

def notify_customer(order):
    email.send(order.customer.email, f"Order #{order.id} confirmed")

def log_order_processed(order):
    logger.info(f"Order {order.id} processed")
```

**Benefits**:
- Easier to test (test each function independently)
- Easier to understand (function name describes exactly what it does)
- Easier to reuse (functions are composable)

**Severity**: **Suggestion** (improves maintainability)

---

### 3. Comments Should Explain Why, Not What

**Principle**: Code should be self-explanatory. Comments explain intent, not mechanics.

**Bad Comments**:

```python
# ❌ BAD: Comments explain what (redundant)
# Increment counter by 1
counter += 1

# Loop through users
for user in users:
    # Print user name
    print(user.name)

# ✅ GOOD: Code is self-explanatory (no comments needed)
counter += 1

for user in users:
    print(user.name)
```

**Good Comments**:

```python
# ✅ GOOD: Comments explain why (intent)
# Apply 15% discount for Black Friday promotion (ends Nov 30)
discounted_price = original_price * 0.85

# Retry up to 3 times due to API rate limiting
for attempt in range(3):
    try:
        response = api.call()
        break
    except RateLimitError:
        time.sleep(2 ** attempt)

# Use weak reference to prevent circular reference memory leak
self.parent = weakref.ref(parent)
```

**When to Comment**:
- Explain business rules: "IRS requires 7-year retention"
- Explain non-obvious decisions: "Using base64 encoding because API requires it"
- Warning of consequences: "Do not modify - breaks backward compatibility"
- TODO: "TODO: Optimize this query (currently O(n²))"
- Legal: Copyright, license information

**When NOT to Comment**:
- Explaining what code does (make code self-explanatory instead)
- Redundant comments: `# constructor` above `def __init__()`
- Commented-out code (delete it - use version control)
- Journal comments: "Added by John on 2023-05-15" (use git log)

**Severity**: **Suggestion** (improves understanding)

---

### 4. Error Handling

**Principle**: Use exceptions, not error codes. Handle errors gracefully.

**Bad Practices**:

```python
# ❌ BAD: Error codes
def get_user(user_id):
    user = db.query(user_id)
    if user is None:
        return -1  # Error code
    return user

result = get_user(123)
if result == -1:
    print("Error")
else:
    print(result.name)
```

**Good Practices**:

```python
# ✅ GOOD: Exceptions
def get_user(user_id):
    user = db.query(user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")
    return user

try:
    user = get_user(123)
    print(user.name)
except UserNotFoundError as e:
    logger.error(f"User lookup failed: {e}")
    print("User not found")
```

**Exception Best Practices**:

1. **Use specific exceptions**:
```python
# ❌ BAD: Generic exception
raise Exception("User not found")

# ✅ GOOD: Specific exception
raise UserNotFoundError("User not found")
```

2. **Don't swallow exceptions**:
```python
# ❌ BAD: Silent failure
try:
    process_payment()
except Exception:
    pass  # Ignored!

# ✅ GOOD: Log and handle
try:
    process_payment()
except PaymentError as e:
    logger.error(f"Payment failed: {e}")
    notify_admin(e)
    raise  # Re-raise if caller needs to know
```

3. **Use context managers**:
```python
# ❌ BAD: Manual cleanup
f = open('file.txt')
try:
    data = f.read()
finally:
    f.close()

# ✅ GOOD: Context manager
with open('file.txt') as f:
    data = f.read()  # Automatically closed
```

**Severity**: **Important** (improves robustness)

---

### 5. DRY (Don't Repeat Yourself)

**Principle**: Every piece of knowledge should have a single, unambiguous representation.

**Detection**:
- Duplicate code blocks
- Copy-pasted functions with minor variations
- Repeated validation logic

**Example - Problem**:
```python
# ❌ BAD: Repeated validation
def create_user(username, email):
    if not username or len(username) < 3:
        raise ValueError("Invalid username")
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    # Create user...

def update_user(user_id, username, email):
    if not username or len(username) < 3:
        raise ValueError("Invalid username")
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    # Update user...
```

**Fix - Extract Common Logic**:
```python
# ✅ GOOD: Single validation function
def validate_username(username):
    if not username or len(username) < 3:
        raise ValueError("Invalid username")

def validate_email(email):
    if not email or '@' not in email:
        raise ValueError("Invalid email")

def create_user(username, email):
    validate_username(username)
    validate_email(email)
    # Create user...

def update_user(user_id, username, email):
    validate_username(username)
    validate_email(email)
    # Update user...
```

**Note**: This is refactorable! See `refactoring-engineer/smells/method/duplicate-code.md`

**Severity**: **Important** (refactorable via extract_method)

---

### 6. Consistent Formatting

**Principle**: Code should follow consistent style throughout project.

**Key Areas**:

**Indentation**:
- Use 4 spaces (Python PEP 8)
- Never mix tabs and spaces

**Line Length**:
- Limit to 79-100 characters (PEP 8: 79)
- Break long lines at logical points

**Whitespace**:
```python
# ✅ GOOD: Consistent whitespace
def calculate_total(price, quantity, discount):
    subtotal = price * quantity
    discounted = subtotal * (1 - discount)
    return discounted

# ❌ BAD: Inconsistent whitespace
def calculate_total(price,quantity,discount):
    subtotal=price*quantity
    discounted =subtotal*(1-discount)
    return discounted
```

**Imports**:
```python
# ✅ GOOD: Grouped imports (PEP 8)
# Standard library
import os
import sys

# Third-party
import requests
from flask import Flask

# Local
from app.models import User
from app.utils import validate
```

**Use Formatter**: `black`, `autopep8` for automatic formatting

**Severity**: **Suggestion** (improves readability)

---

### 7. Small Functions and Classes

**Principle**: Functions should be small (< 20 lines). Classes should be focused (< 200 lines).

**Detection**:
- Long Method smell (see `refactoring-engineer/smells/method/long-method.md`)
- Large Class smell (see `refactoring-engineer/smells/class/large-class.md`)

**Example**:
```python
# ❌ BAD: 100-line function
def process_order(order):
    # 100 lines of mixed concerns
    pass

# ✅ GOOD: Composed of small functions
def process_order(order):
    validate_order(order)
    calculate_total(order)
    apply_discount(order)
    save_order(order)
    notify_customer(order)
```

**Benefits**:
- Easier to test
- Easier to understand
- Easier to reuse
- Easier to modify

**Note**: This is refactorable! See `refactoring-engineer/smells/method/long-method.md`

**Severity**: **Important** (refactorable via extract_method)

---

### 8. Minimize Dependencies

**Principle**: Reduce coupling between modules and classes.

**Detection**:
- Class imports many other classes
- Function has many parameters (> 3)
- Module has circular dependencies

**Example - Problem**:
```python
# ❌ BAD: Too many dependencies
class OrderProcessor:
    def __init__(self, db, email_service, payment_gateway,
                 inventory_service, shipping_service, tax_calculator,
                 discount_engine, notification_service):
        self.db = db
        self.email_service = email_service
        self.payment_gateway = payment_gateway
        # ... 8 dependencies!
```

**Fix - Dependency Injection with Facade**:
```python
# ✅ GOOD: Facade pattern reduces dependencies
class OrderServices:
    def __init__(self, db, email_service, payment_gateway,
                 inventory_service, shipping_service, tax_calculator,
                 discount_engine, notification_service):
        self.db = db
        self.email_service = email_service
        # ...

class OrderProcessor:
    def __init__(self, services: OrderServices):
        self.services = services  # Single dependency
```

**Severity**: **Suggestion** (improves modularity)

---

## Code Review Checklist

### Phase 2: Manual Review

**Naming**:
- [ ] Are variable names meaningful and pronounceable?
- [ ] Are function names descriptive verbs?
- [ ] Are class names specific nouns?
- [ ] Are magic numbers replaced with named constants?

**Functions**:
- [ ] Does each function do one thing?
- [ ] Are functions small (< 20 lines)?
- [ ] Are function names accurate?
- [ ] Are parameters minimal (< 4)?

**Comments**:
- [ ] Do comments explain why, not what?
- [ ] Is commented-out code removed?
- [ ] Are TODOs tracked?
- [ ] Is code self-explanatory (minimal comments needed)?

**Error Handling**:
- [ ] Are exceptions used (not error codes)?
- [ ] Are exceptions specific (not generic)?
- [ ] Are resources cleaned up (context managers)?
- [ ] Are errors logged appropriately?

**DRY**:
- [ ] Is duplicate code extracted?
- [ ] Are validation rules centralized?
- [ ] Are magic numbers/strings constants?

**Formatting**:
- [ ] Is indentation consistent?
- [ ] Is line length reasonable (< 100 chars)?
- [ ] Are imports organized?
- [ ] Is formatter used (black, autopep8)?

**Size**:
- [ ] Are functions small (< 20 lines)?
- [ ] Are classes focused (< 200 lines)?
- [ ] Are modules cohesive?

**Dependencies**:
- [ ] Are dependencies minimal?
- [ ] Is coupling loose?
- [ ] Are circular dependencies avoided?

---

## Integration with Code-Reviewer Process

### Phase 2: Manual Review

```markdown
Load clean code principles:
  {{load: ../quality/clean-code.md}}

Assess code against principles:
  1. Naming: Are names meaningful?
  2. Functions: Do they do one thing?
  3. Comments: Do they explain why?
  4. Error Handling: Are exceptions used?
  5. DRY: Is duplication minimized?
  6. Formatting: Is style consistent?
  7. Size: Are functions/classes small?
  8. Dependencies: Is coupling minimal?

Output: Suggestions for clean code improvements
```

### Phase 5: Recommendations

```markdown
## Suggestions: Clean Code Improvements

**1. Naming (Line 45)**
Variable `x` unclear. Suggest `user_count` for readability.

**2. Function Size (Line 67)**
Function `process_user_data` is 75 lines. Consider extracting methods:
- `validate_user()` (lines 67-80)
- `calculate_discount()` (lines 81-95)
- `save_user()` (lines 96-110)

**3. Comments (Line 120)**
Comment explains what code does (redundant). Code is self-explanatory:
```python
# Remove comment: "# Loop through users"
for user in users:
    print(user.name)
```

**4. DRY Violation (Lines 150-180)**
Validation logic duplicated. Extract to `validate_email(email)` function.

**What Went Well** ✓:
- Excellent error handling with specific exceptions
- Consistent formatting throughout
- Good use of context managers
```

---

## Summary

**Clean Code Principles**:
1. **Meaningful Names**: Reveal intent, be pronounceable
2. **Single Responsibility**: Functions do one thing
3. **Comments**: Explain why, not what
4. **Error Handling**: Use exceptions, handle gracefully
5. **DRY**: Don't repeat yourself
6. **Consistent Formatting**: Follow style guide
7. **Small Functions/Classes**: < 20 lines functions, < 200 lines classes
8. **Minimize Dependencies**: Reduce coupling

**Code-Reviewer Usage**:
- Phase 2: Manual assessment against principles
- Phase 5: Suggestions for improvement
- Priority: Suggestion (not blocking)

**Refactorable Issues**:
- DRY violations (duplicate code)
- Large functions/classes
- See: `refactoring-engineer/smells/INDEX.md`

**Non-Refactorable Issues**:
- Naming (requires human judgment)
- Comments (requires understanding intent)
- Formatting (use automated formatter)

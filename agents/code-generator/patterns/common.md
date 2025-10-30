# Common Code Generation Patterns

**Purpose:** Reference guide for frequently encountered patterns, solutions, and best practices.

---

## Clean Code Patterns

### Pattern: Self-Documenting Names

**Problem:** Code is hard to understand without comments

**Solution:**
```python
# Bad
def calc(a, b, f):
    return a + (b * f)

# Good
def calculate_total_price(base_price, item_quantity, tax_rate):
    subtotal = base_price * item_quantity
    return subtotal + (subtotal * tax_rate)
```

**Why:** Names convey intent, reducing cognitive load

---

### Pattern: Single Responsibility Functions

**Problem:** Functions do too many things

**Solution:**
```python
# Bad (does validation + processing + saving)
def handle_user_data(data):
    if not data.get('email'):
        raise ValueError("Email required")
    processed = data['email'].lower().strip()
    save_to_database(processed)
    send_confirmation(processed)

# Good (separated concerns)
def validate_user_data(data):
    if not data.get('email'):
        raise ValueError("Email required")

def normalize_email(email):
    return email.lower().strip()

def process_user_registration(data):
    validate_user_data(data)
    email = normalize_email(data['email'])
    save_to_database(email)
    send_confirmation(email)
```

**Why:** Each function has one clear purpose, easier to test and modify

---

### Pattern: Early Returns (Guard Clauses)

**Problem:** Deep nesting makes code hard to follow

**Solution:**
```python
# Bad (nested)
def process_order(order):
    if order:
        if order.items:
            if order.user:
                # actual logic 3 levels deep
                return process(order)

# Good (early returns)
def process_order(order):
    if not order:
        return None
    if not order.items:
        return None
    if not order.user:
        return None

    return process(order)  # Happy path at same indentation level
```

**Why:** Reduces nesting, makes happy path clear

---

##

 SOLID Principles in Practice

### Single Responsibility Principle (SRP)

**Pattern:** Each class/function should have one reason to change

```python
# Bad (multiple responsibilities)
class UserManager:
    def save_user(self, user):
        # Database logic
        db.save(user)

    def send_welcome_email(self, user):
        # Email logic
        email.send(user.email, "Welcome!")

    def validate_user(self, user):
        # Validation logic
        return user.email and user.name

# Good (separated responsibilities)
class UserRepository:
    def save(self, user):
        db.save(user)

class EmailService:
    def send_welcome(self, user):
        email.send(user.email, "Welcome!")

class UserValidator:
    def validate(self, user):
        return user.email and user.name
```

---

### Open/Closed Principle (OCP)

**Pattern:** Open for extension, closed for modification

```python
# Bad (modify class to add new types)
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == "credit_card":
            # credit card logic
        elif payment_type == "paypal":
            # paypal logic
        # Adding new type requires modifying this function

# Good (extend through inheritance/composition)
class PaymentProcessor:
    def process(self, amount):
        raise NotImplementedError

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount):
        # credit card logic

class PayPalProcessor(PaymentProcessor):
    def process(self, amount):
        # paypal logic

# Adding new type: create new class, no modification needed
```

---

### Dependency Inversion Principle (DIP)

**Pattern:** Depend on abstractions, not concretions

```python
# Bad (depends on concrete implementation)
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Tightly coupled

    def get_user(self, id):
        return self.db.query(f"SELECT * FROM users WHERE id={id}")

# Good (depends on abstraction)
class UserService:
    def __init__(self, db: Database):  # Depends on interface
        self.db = db

    def get_user(self, id):
        return self.db.get("users", id)

# Can now swap database implementations without changing UserService
```

---

## Design Patterns

### Pattern: Factory

**When:** Need to create objects without specifying exact class

**Example:**
```python
class UserFactory:
    @staticmethod
    def create(user_type):
        if user_type == "admin":
            return AdminUser()
        elif user_type == "regular":
            return RegularUser()
        raise ValueError(f"Unknown user type: {user_type}")
```

---

### Pattern: Dependency Injection

**When:** Need testable, decoupled code

**Example:**
```python
# Bad (creates own dependencies)
class EmailService:
    def __init__(self):
        self.smtp = SMTPClient()  # Hard to test

# Good (dependencies injected)
class EmailService:
    def __init__(self, smtp_client):
        self.smtp = smtp_client  # Easy to mock in tests
```

---

### Pattern: Strategy

**When:** Need to switch between algorithms

**Example:**
```python
class SortStrategy:
    def sort(self, data):
        raise NotImplementedError

class QuickSort(SortStrategy):
    def sort(self, data):
        # quicksort implementation

class MergeSort(SortStrategy):
    def sort(self, data):
        # mergesort implementation

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort_data(self, data):
        return self.strategy.sort(data)
```

---

## Testing Patterns

### Pattern: Arrange-Act-Assert (AAA)

**Structure:** Organize tests in three clear sections

```python
def test_email_validation():
    # Arrange: Set up test data
    validator = EmailValidator()
    valid_email = "user@example.com"
    invalid_email = "not-an-email"

    # Act: Execute the code under test
    valid_result = validator.validate(valid_email)
    invalid_result = validator.validate(invalid_email)

    # Assert: Verify the results
    assert valid_result is True
    assert invalid_result is False
```

---

### Pattern: Test Fixtures

**When:** Multiple tests need same setup

```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Test User", email="test@example.com")

def test_user_creation(sample_user):
    assert sample_user.name == "Test User"

def test_user_email(sample_user):
    assert sample_user.email == "test@example.com"
```

---

### Pattern: Mocking External Dependencies

**When:** Testing code that depends on external services

```python
from unittest.mock import Mock

def test_send_email():
    # Arrange: Mock the SMTP client
    mock_smtp = Mock()
    email_service = EmailService(smtp_client=mock_smtp)

    # Act
    email_service.send("user@example.com", "Hello")

    # Assert: Verify SMTP was called correctly
    mock_smtp.send.assert_called_once_with("user@example.com", "Hello")
```

---

## Error Handling Patterns

### Pattern: Specific Exceptions

**Problem:** Generic exceptions don't convey meaning

**Solution:**
```python
# Bad
def load_user(id):
    user = db.get(id)
    if not user:
        raise Exception("Error")  # Too generic

# Good
class UserNotFoundError(Exception):
    pass

def load_user(id):
    user = db.get(id)
    if not user:
        raise UserNotFoundError(f"User {id} not found")
```

---

### Pattern: Try-Except-Else-Finally

**Structure:** Handle different scenarios clearly

```python
def process_file(filename):
    file = None
    try:
        file = open(filename, 'r')
        data = file.read()
    except FileNotFoundError:
        logging.error(f"File {filename} not found")
        return None
    except PermissionError:
        logging.error(f"Permission denied: {filename}")
        return None
    else:
        # Only runs if try succeeds (no exception)
        return process_data(data)
    finally:
        # Always runs (cleanup)
        if file:
            file.close()
```

---

### Pattern: Context Managers (with statement)

**When:** Need guaranteed cleanup

```python
# Automatic resource cleanup
with open('file.txt', 'r') as f:
    data = f.read()
    # File automatically closed, even if exception occurs

# Custom context manager
class DatabaseTransaction:
    def __enter__(self):
        self.conn = db.connect()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

with DatabaseTransaction() as conn:
    conn.execute("UPDATE ...")
    # Automatically commits or rolls back
```

---

## Performance Patterns

### Pattern: Avoid N+1 Queries

**Problem:** Database query in a loop

**Solution:**
```python
# Bad (N+1 queries)
users = User.query.all()  # 1 query
for user in users:
    orders = user.orders  # N queries (one per user)

# Good (2 queries total)
users = User.query.options(joinedload(User.orders)).all()
for user in users:
    orders = user.orders  # No additional query
```

---

### Pattern: Lazy Evaluation

**When:** Don't compute until needed

**Solution:**
```python
# Bad (computes all immediately)
results = [expensive_operation(x) for x in huge_list]
first_five = results[:5]  # Computed all, used 5

# Good (computes on demand)
results = (expensive_operation(x) for x in huge_list)  # Generator
first_five = list(itertools.islice(results, 5))  # Computed only 5
```

---

### Pattern: Caching

**When:** Expensive operation called repeatedly with same input

**Solution:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n):
    # Complex computation
    return result

# First call: computed
result1 = expensive_calculation(10)

# Second call: cached
result2 = expensive_calculation(10)  # Much faster
```

---

## Common Pitfalls (Anti-Patterns)

### Pitfall: God Object

**Problem:** One class does everything

**Fix:** Split into focused classes with single responsibilities

---

### Pitfall: Tight Coupling

**Problem:** Classes depend directly on each other

**Fix:** Use dependency injection, depend on abstractions

---

### Pitfall: Premature Optimization

**Problem:** Optimizing before knowing it's needed

**Fix:** Make it work, make it right, THEN make it fast

---

### Pitfall: Magic Numbers

**Problem:** Unexplained constants

```python
# Bad
if user.age > 18:  # Why 18?

# Good
LEGAL_AGE = 18
if user.age > LEGAL_AGE:
```

---

### Pitfall: Over-Engineering

**Problem:** Complex solution for simple problem

**Fix:** Start simple, add complexity only when truly needed

---

## Language-Specific Best Practices

### Python

- Use type hints: `def add(a: int, b: int) -> int:`
- Context managers: `with open(...) as f:`
- List comprehensions: `[x*2 for x in range(10)]`
- Use `pathlib` over `os.path`
- Follow PEP 8 style guide

### JavaScript/TypeScript

- Use `const` by default, `let` when reassignment needed
- Prefer `async/await` over `.then()` chains
- Destructuring: `const {name, email} = user`
- Optional chaining: `user?.address?.city`
- Use TypeScript for type safety

### Java

- Use Optional for nullable values
- Streams for collection operations
- Try-with-resources for auto-cleanup
- Spring dependency injection
- Immutable objects where possible

### Go

- Error handling: `if err != nil { return err }`
- Goroutines for concurrency
- Channels for communication
- Interfaces for abstraction
- Composition over inheritance

---

## Quick Reference: When to Use What

**Small, focused function?** → Single Responsibility Principle
**Need to swap implementations?** → Dependency Injection
**Creating related objects?** → Factory Pattern
**Multiple algorithms?** → Strategy Pattern
**Need guaranteed cleanup?** → Context Manager (with statement)
**Expensive operation?** → Cache results
**Database queries in loop?** → Eager loading
**External dependencies in tests?** → Mocking
**Complex conditionals?** → Early returns / Guard clauses

---

**Remember:** These are patterns, not rules. Apply them when they solve a real problem, not just because they exist. The best code is often the simplest code that solves the problem.

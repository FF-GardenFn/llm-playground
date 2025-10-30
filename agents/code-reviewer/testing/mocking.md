# Mocking & Test Doubles

**Purpose**: Assess effective use of mocks, stubs, fakes, and other test doubles during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (affects test isolation and speed)

**Principle**: Mock external dependencies, test real behavior

---

## Overview

Test doubles isolate code under test from external dependencies. Code-reviewer assesses:
- **When to Mock**: External systems, slow operations, non-deterministic behavior
- **What Not to Mock**: Business logic, simple objects, value objects
- **Mock Types**: Mocks, stubs, fakes, spies, dummies

---

## Test Double Types

### 1. Mock

**Purpose**: Verify interactions (method calls, parameters).

**Good - Verify Behavior**:
```python
# ✅ GOOD: Mock verifies interaction
from unittest.mock import Mock

def test_user_service_sends_welcome_email():
    # Mock email service to verify it's called
    mock_email = Mock()

    service = UserService(email_service=mock_email)
    user = service.create_user({"name": "John", "email": "john@example.com"})

    # Verify email service was called with correct parameters
    mock_email.send_welcome_email.assert_called_once_with("john@example.com")
```

**When to Use**:
- Verifying external service calls
- Verifying event publishing
- Verifying logging/auditing

**Detection Heuristics**:
- Using `Mock()` from `unittest.mock`
- Assertions on `.assert_called_*` methods

---

### 2. Stub

**Purpose**: Provide canned responses to method calls.

**Good - Stub Returns Fixed Data**:
```python
# ✅ GOOD: Stub returns fixed response
from unittest.mock import Mock

def test_order_total_with_discount():
    # Stub returns fixed discount rate
    stub_discount_service = Mock()
    stub_discount_service.get_discount_rate.return_value = 0.2

    service = OrderService(discount_service=stub_discount_service)
    order = Order(items=[Item(price=100)])

    total = service.calculate_total_with_discount(order)

    assert total == 80  # 100 * (1 - 0.2)
```

**When to Use**:
- Replacing external API calls
- Providing test data
- Simulating specific scenarios

---

### 3. Fake

**Purpose**: Working implementation with shortcuts (e.g., in-memory database).

**Good - In-Memory Database**:
```python
# ✅ GOOD: Fake repository (in-memory)
class FakeUserRepository:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    def save(self, user_data):
        user_id = self.next_id
        self.next_id += 1
        user = User(id=user_id, **user_data)
        self.users[user_id] = user
        return user

    def get(self, user_id):
        return self.users.get(user_id)

# Use in tests
def test_user_service():
    fake_repo = FakeUserRepository()
    service = UserService(repo=fake_repo)

    user = service.create_user({"name": "John"})
    retrieved = service.get_user(user.id)

    assert retrieved.name == "John"
```

**When to Use**:
- Replacing database with in-memory storage
- Replacing file system with in-memory files
- Fast, simple alternative to real implementation

---

### 4. Spy

**Purpose**: Real object that records interactions.

**Good - Spy Records Calls**:
```python
# ✅ GOOD: Spy wraps real object
from unittest.mock import Mock, wraps

def test_user_service_calls_repository():
    # Real repository
    real_repo = UserRepository()

    # Spy wraps real repo to record calls
    spy_repo = Mock(wraps=real_repo)

    service = UserService(repo=spy_repo)
    user = service.create_user({"name": "John"})

    # Real behavior executed
    assert user.id is not None

    # Can verify calls
    spy_repo.save.assert_called_once()
```

**When to Use**:
- Verifying calls while using real implementation
- Partial mocking

---

### 5. Dummy

**Purpose**: Placeholder object (not actually used).

**Good - Dummy as Parameter**:
```python
# ✅ GOOD: Dummy logger (not used in test)
def test_calculate_discount():
    dummy_logger = Mock()  # Never called

    service = DiscountService(logger=dummy_logger)
    result = service.calculate(100, 0.1)

    assert result == 90
    # Logger not called in this test
```

**When to Use**:
- Required parameter not used in test
- Satisfying function signature

---

## When to Mock

### Mock External Dependencies

**Good - Mock External API**:
```python
# ✅ GOOD: Mock external payment gateway
from unittest.mock import patch

def test_process_payment():
    with patch('payment_gateway.charge_card') as mock_charge:
        mock_charge.return_value = {'transaction_id': '12345', 'status': 'success'}

        result = process_payment(card='4242', amount=100)

        assert result['transaction_id'] == '12345'
        mock_charge.assert_called_once_with(card='4242', amount=100)
```

**When to Mock**:
- **External APIs**: Payment gateways, third-party services
- **Databases**: Use in-memory database or mock
- **File System**: Mock file operations
- **Network**: Mock HTTP requests
- **Time**: Mock datetime.now() for deterministic tests
- **Random**: Mock random values

---

### Don't Mock Value Objects

**Bad - Mocking Simple Objects**:
```python
# ❌ BAD: Mocking value object (unnecessary)
from unittest.mock import Mock

def test_order_total():
    # Don't mock simple objects!
    mock_item1 = Mock()
    mock_item1.price = 10
    mock_item2 = Mock()
    mock_item2.price = 20

    order = Order(items=[mock_item1, mock_item2])
    total = order.calculate_total()

    assert total == 30
```

**Good - Use Real Objects**:
```python
# ✅ GOOD: Use real value objects
def test_order_total():
    # Real Item objects (fast, simple)
    item1 = Item(price=10)
    item2 = Item(price=20)

    order = Order(items=[item1, item2])
    total = order.calculate_total()

    assert total == 30
```

**Don't Mock**:
- Value objects (Item, Money, Address)
- DTOs (data transfer objects)
- Simple domain objects
- **Your own business logic** (test real behavior!)

---

### Don't Over-Mock

**Bad - Mocking Everything**:
```python
# ❌ BAD: Over-mocking (testing nothing real)
def test_user_service():
    mock_validator = Mock()
    mock_validator.validate.return_value = True

    mock_repo = Mock()
    mock_repo.save.return_value = Mock(id=1, name="John")

    mock_logger = Mock()
    mock_notifier = Mock()

    service = UserService(
        validator=mock_validator,
        repo=mock_repo,
        logger=mock_logger,
        notifier=mock_notifier
    )

    user = service.create_user({"name": "John"})

    # What did we actually test? Just mocks calling mocks!
    assert user.id == 1
```

**Good - Mock Only External Dependencies**:
```python
# ✅ GOOD: Mock only external dependencies
def test_user_service():
    # Real validator (business logic - don't mock!)
    validator = UserValidator()

    # Mock repository (external dependency - OK to mock)
    mock_repo = Mock()
    mock_repo.save.return_value = User(id=1, name="John")

    # Dummy logger (not relevant to test)
    dummy_logger = Mock()

    service = UserService(
        validator=validator,  # Real
        repo=mock_repo,       # Mock
        logger=dummy_logger   # Dummy
    )

    user = service.create_user({"name": "John"})

    # Tests real validation logic + interaction with repo
    assert user.name == "John"
```

**Rule of Thumb**: Mock I/O, test logic

---

## Mocking Patterns

### Pattern 1: Dependency Injection

**Good - Constructor Injection**:
```python
# ✅ GOOD: Dependencies injected (easy to mock)
class UserService:
    def __init__(self, repo, email_service):
        self.repo = repo
        self.email_service = email_service

    def create_user(self, user_data):
        user = self.repo.save(user_data)
        self.email_service.send_welcome_email(user.email)
        return user

# Easy to test with mocks
def test_user_service():
    mock_repo = Mock()
    mock_email = Mock()

    service = UserService(repo=mock_repo, email_service=mock_email)
    # Test...
```

**Bad - Hard-Coded Dependencies**:
```python
# ❌ BAD: Hard-coded dependencies (hard to test)
class UserService:
    def __init__(self):
        self.repo = UserRepository()  # Hard-coded!
        self.email_service = EmailService()  # Hard-coded!

    def create_user(self, user_data):
        user = self.repo.save(user_data)
        self.email_service.send_welcome_email(user.email)
        return user

# Can't easily inject mocks!
```

---

### Pattern 2: Patch External Dependencies

**Good - Patch at Call Site**:
```python
# ✅ GOOD: Patch external dependency
from unittest.mock import patch

def test_fetch_data():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'data': 'test'}

        result = fetch_data_from_api()

        assert result == {'data': 'test'}
        mock_get.assert_called_once_with('https://api.example.com/data')
```

**Where to Patch**: Patch where it's used, not where it's defined
```python
# ❌ BAD: Patching where defined
@patch('requests.get')  # Wrong location!

# ✅ GOOD: Patching where used
@patch('my_module.requests.get')  # Correct location!
```

---

### Pattern 3: Mock Return Values

**Good - Specific Return Values**:
```python
# ✅ GOOD: Specific return values for different calls
from unittest.mock import Mock

def test_multiple_api_calls():
    mock_api = Mock()

    # Different return values for different calls
    mock_api.get.side_effect = [
        {'data': 'first'},
        {'data': 'second'},
        {'data': 'third'}
    ]

    # First call
    result1 = service.fetch(mock_api)
    assert result1 == {'data': 'first'}

    # Second call
    result2 = service.fetch(mock_api)
    assert result2 == {'data': 'second'}

    # Third call
    result3 = service.fetch(mock_api)
    assert result3 == {'data': 'third'}
```

---

### Pattern 4: Mock Exceptions

**Good - Mock Failure Scenarios**:
```python
# ✅ GOOD: Mock exceptions
from unittest.mock import Mock

def test_payment_gateway_failure():
    mock_gateway = Mock()
    mock_gateway.charge.side_effect = PaymentGatewayError("Connection timeout")

    with pytest.raises(PaymentGatewayError):
        process_payment(gateway=mock_gateway, amount=100)

    # Verify error was logged
    mock_gateway.charge.assert_called_once()
```

---

## Mock Verification

### Verify Calls

```python
# ✅ GOOD: Verify method calls
mock_service.send_email.assert_called_once()
mock_service.send_email.assert_called_with(email="john@example.com")
mock_service.send_email.assert_called_once_with(email="john@example.com")
mock_service.send_email.assert_not_called()

# Verify call count
assert mock_service.send_email.call_count == 3
```

### Verify Call Order

```python
# ✅ GOOD: Verify call order
from unittest.mock import call

mock_service.step1()
mock_service.step2()
mock_service.step3()

# Verify calls made in order
mock_service.assert_has_calls([
    call.step1(),
    call.step2(),
    call.step3()
])
```

---

## Common Mocking Mistakes

### Mistake 1: Mocking What You're Testing

```python
# ❌ BAD: Mocking the unit under test
from unittest.mock import Mock

def test_calculate_discount():
    mock_service = Mock()
    mock_service.calculate_discount.return_value = 90

    result = mock_service.calculate_discount(100, 0.1)

    assert result == 90  # Testing the mock, not real code!

# ✅ GOOD: Test real code
def test_calculate_discount():
    result = calculate_discount(100, 0.1)  # Real function
    assert result == 90
```

---

### Mistake 2: Brittle Mocks (Implementation Details)

```python
# ❌ BAD: Mock internal implementation
def test_user_service():
    mock_repo = Mock()

    service = UserService(repo=mock_repo)
    service.create_user({"name": "John"})

    # Brittle: assumes implementation details
    mock_repo._internal_save.assert_called()  # Testing private method!
    mock_repo._validate.assert_called()  # Testing private method!

# ✅ GOOD: Mock public interface
def test_user_service():
    mock_repo = Mock()

    service = UserService(repo=mock_repo)
    service.create_user({"name": "John"})

    # Tests public interface only
    mock_repo.save.assert_called_once()
```

---

### Mistake 3: Not Verifying Mocks

```python
# ❌ BAD: Creating mock but not verifying
def test_send_welcome_email():
    mock_email = Mock()

    service = UserService(email_service=mock_email)
    service.create_user({"name": "John", "email": "john@example.com"})

    # No verification! Did it actually send email?

# ✅ GOOD: Verify mock was called
def test_send_welcome_email():
    mock_email = Mock()

    service = UserService(email_service=mock_email)
    service.create_user({"name": "John", "email": "john@example.com"})

    # Verify email sent
    mock_email.send_welcome_email.assert_called_once_with("john@example.com")
```

---

## Review Checklist

### Phase 2: Manual Review

**Mocking Strategy**:
- [ ] Are external dependencies mocked?
- [ ] Is business logic tested with real objects?
- [ ] Are mocks used appropriately (not over-mocked)?

**Mock Types**:
- [ ] Are mocks used for verifying interactions?
- [ ] Are stubs used for providing test data?
- [ ] Are fakes used for fast in-memory replacements?

**Mock Quality**:
- [ ] Do mocks verify calls?
- [ ] Are mocks not brittle (not testing implementation details)?
- [ ] Are mocks injected via dependency injection?

**What's Mocked**:
- [ ] Are I/O operations mocked?
- [ ] Are external APIs mocked?
- [ ] Are value objects NOT mocked?
- [ ] Is business logic NOT mocked?

---

## Summary

**Test Double Types**:
- **Mock**: Verify interactions
- **Stub**: Provide canned responses
- **Fake**: Working implementation with shortcuts
- **Spy**: Real object that records interactions
- **Dummy**: Placeholder object

**When to Mock**:
- External APIs
- Databases
- File system
- Network
- Time/Random (non-deterministic)

**What NOT to Mock**:
- Value objects
- Business logic
- Simple objects
- Code under test

**Mocking Patterns**:
- Dependency injection
- Patch at call site
- Specific return values
- Mock exceptions

**Common Mistakes**:
- Mocking code under test
- Brittle mocks (implementation details)
- Not verifying mocks

**Detection**:
- Phase 2: Review mock usage
- Check if business logic mocked
- Check if mocks verified

**Priority**: **Important** (affects test isolation and quality)

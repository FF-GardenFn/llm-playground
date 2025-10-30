# Test Types & Testing Strategy

**Purpose**: Assess test type distribution and testing strategy during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (affects test effectiveness)

**Testing Pyramid**: Many unit tests, fewer integration tests, few E2E tests

---

## Overview

Different test types serve different purposes. Code-reviewer assesses:
- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows
- **Other**: Contract tests, performance tests, security tests

---

## Testing Pyramid

```
        ╱╲
       ╱  ╲       E2E Tests (5-10%)
      ╱────╲      Slow, expensive, brittle
     ╱      ╲
    ╱────────╲    Integration Tests (20-30%)
   ╱          ╲   Medium speed, medium cost
  ╱────────────╲
 ╱   Unit Tests  ╲ (60-70%)
╱────────────────╲ Fast, cheap, stable
```

**Ideal Distribution**:
- **Unit Tests**: 60-70% (majority)
- **Integration Tests**: 20-30%
- **E2E Tests**: 5-10% (minimal)

---

## 1. Unit Tests

**Purpose**: Test single unit (function, method, class) in isolation.

**Characteristics**:
- **Fast**: < 10ms each
- **Isolated**: No external dependencies
- **Focused**: One function/method
- **Mocked**: External dependencies mocked

**Example - Unit Test**:
```python
# ✅ GOOD: Unit test (pure logic, no dependencies)
def test_calculate_discount():
    # Tests calculate_discount() in isolation
    result = calculate_discount(price=100, rate=0.1)
    assert result == 90

# ✅ GOOD: Unit test with mocks
from unittest.mock import Mock

def test_user_service_create_user():
    # Mock repository (external dependency)
    mock_repo = Mock()
    mock_repo.save.return_value = User(id=1, name="John")

    # Test service logic in isolation
    service = UserService(repo=mock_repo)
    user = service.create_user({"name": "John"})

    # Verify behavior
    assert user.name == "John"
    mock_repo.save.assert_called_once()
```

**When to Use**:
- Testing business logic
- Testing calculations
- Testing validation rules
- Testing algorithms

**Target**: **60-70% of tests**

**Detection Heuristics**:
- Tests not using database
- Tests using mocks for external dependencies
- Tests < 10ms

**Severity**: **Important** (unit tests are foundation)

---

## 2. Integration Tests

**Purpose**: Test interaction between components.

**Characteristics**:
- **Medium Speed**: 10-100ms each
- **Real Dependencies**: Use real database, services
- **Component Interaction**: Tests multiple components together
- **Focused**: Test specific integration points

**Example - Integration Test**:
```python
# ✅ GOOD: Integration test (database interaction)
import pytest
from django.test import TestCase

@pytest.mark.django_db
def test_user_repository_save():
    # Tests repository + database integration
    repo = UserRepository()
    user_data = {"name": "John", "email": "john@example.com"}

    user = repo.save(user_data)

    # Verify database state
    assert user.id is not None
    assert User.objects.filter(id=user.id).exists()

# ✅ GOOD: Integration test (service + repository)
@pytest.mark.django_db
def test_user_service_create_user():
    # Tests service + repository + database
    service = UserService(repo=UserRepository())
    user = service.create_user({"name": "John", "email": "john@example.com"})

    # Verify end-to-end flow
    assert user.id is not None
    assert User.objects.get(id=user.id).name == "John"
```

**When to Use**:
- Testing database queries
- Testing ORM behavior
- Testing API interactions
- Testing message queues

**Target**: **20-30% of tests**

**Detection Heuristics**:
- Tests using database decorator (`@pytest.mark.django_db`)
- Tests using TestCase with database access
- Tests 10-100ms

**Severity**: **Important**

---

## 3. End-to-End (E2E) Tests

**Purpose**: Test complete user workflows through UI/API.

**Characteristics**:
- **Slow**: 1-10 seconds each
- **Full Stack**: All layers (UI, API, database)
- **User Perspective**: Tests real user scenarios
- **Brittle**: Can break due to UI changes

**Example - E2E Test (API)**:
```python
# ✅ GOOD: E2E test (full HTTP request/response)
def test_create_order_e2e(client):
    # Step 1: Create user
    response = client.post('/users', json={'name': 'John', 'email': 'john@example.com'})
    user_id = response.json['id']

    # Step 2: Create order
    response = client.post('/orders', json={
        'user_id': user_id,
        'items': [{'product_id': 1, 'quantity': 2}]
    })
    assert response.status_code == 201

    # Step 3: Verify order
    order_id = response.json['id']
    response = client.get(f'/orders/{order_id}')
    assert response.json['user_id'] == user_id
    assert len(response.json['items']) == 1
```

**Example - E2E Test (UI)**:
```python
# ✅ GOOD: E2E test (browser automation)
from selenium import webdriver

def test_user_signup_flow():
    driver = webdriver.Chrome()

    # Navigate to signup page
    driver.get('http://localhost:8000/signup')

    # Fill form
    driver.find_element_by_id('name').send_keys('John Doe')
    driver.find_element_by_id('email').send_keys('john@example.com')
    driver.find_element_by_id('password').send_keys('password123')

    # Submit
    driver.find_element_by_id('submit').click()

    # Verify success
    assert 'Welcome' in driver.page_source

    driver.quit()
```

**When to Use**:
- Testing critical user workflows
- Testing UI interactions
- Testing cross-cutting concerns
- Smoke tests for deployments

**Target**: **5-10% of tests** (minimal)

**Detection Heuristics**:
- Tests using HTTP client (TestClient, requests)
- Tests using browser automation (Selenium, Playwright)
- Tests > 1 second

**Severity**: **Suggestion** (E2E tests are expensive)

---

## 4. Contract Tests

**Purpose**: Verify API contracts between services.

**Example - Consumer-Driven Contract**:
```python
# ✅ GOOD: Contract test
import requests_mock

def test_user_service_contract():
    # Define expected contract
    expected_contract = {
        'id': int,
        'name': str,
        'email': str,
        'created_at': str  # ISO 8601 format
    }

    with requests_mock.Mocker() as m:
        # Mock external service response
        m.get('https://api.users.com/users/123', json={
            'id': 123,
            'name': 'John Doe',
            'email': 'john@example.com',
            'created_at': '2024-01-01T00:00:00Z'
        })

        # Call service
        response = user_client.get_user(123)

        # Verify contract
        for field, expected_type in expected_contract.items():
            assert field in response
            assert isinstance(response[field], expected_type)
```

**When to Use**:
- Microservices architecture
- Third-party API integration
- Ensuring backward compatibility

**Target**: **As needed for external APIs**

---

## 5. Performance Tests

**Purpose**: Verify performance requirements.

**Example - Load Test**:
```python
# ✅ GOOD: Performance test
import time

def test_search_performance():
    # Performance requirement: search < 100ms
    start = time.time()

    results = search_service.search(query="test")

    elapsed = (time.time() - start) * 1000  # ms
    assert elapsed < 100, f"Search took {elapsed}ms (expected < 100ms)"
```

**Example - Scalability Test**:
```python
# ✅ GOOD: Scalability test
def test_handle_1000_concurrent_requests():
    from concurrent.futures import ThreadPoolExecutor

    def make_request():
        return client.get('/api/users')

    # 1000 concurrent requests
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(make_request) for _ in range(1000)]
        results = [f.result() for f in futures]

    # All should succeed
    assert all(r.status_code == 200 for r in results)
```

**When to Use**:
- Testing performance requirements
- Load testing
- Stress testing

**Target**: **As needed for performance-critical code**

---

## 6. Security Tests

**Purpose**: Verify security requirements.

**Example - Authentication Test**:
```python
# ✅ GOOD: Security test
def test_authenticated_endpoint_requires_auth():
    # Without authentication
    response = client.get('/api/orders')
    assert response.status_code == 401  # Unauthorized

    # With valid token
    response = client.get('/api/orders', headers={'Authorization': 'Bearer valid_token'})
    assert response.status_code == 200
```

**Example - Input Validation Test**:
```python
# ✅ GOOD: Security test (SQL injection)
def test_user_search_prevents_sql_injection():
    # Attempt SQL injection
    malicious_input = "'; DROP TABLE users;--"

    response = client.get(f'/api/users?search={malicious_input}')

    # Should not crash, should sanitize input
    assert response.status_code in [200, 400]
    assert User.objects.count() > 0  # Table still exists
```

**When to Use**:
- Testing authentication
- Testing authorization
- Testing input validation
- Testing XSS/CSRF protection

**Target**: **Cover all security-critical paths**

---

## Test Type Distribution

### Ideal Distribution

```python
# Example project with good test distribution
# Total: 1000 tests

# Unit Tests: 700 (70%)
- test_calculate_discount.py: 50 tests
- test_validators.py: 100 tests
- test_business_logic.py: 300 tests
- test_models.py: 250 tests

# Integration Tests: 250 (25%)
- test_database_queries.py: 100 tests
- test_service_layer.py: 100 tests
- test_api_endpoints.py: 50 tests

# E2E Tests: 50 (5%)
- test_user_workflows.py: 20 tests
- test_order_processing.py: 20 tests
- test_payment_flow.py: 10 tests
```

### Poor Distribution

```python
# ❌ BAD: Inverted pyramid (too many E2E tests)
# Total: 1000 tests

# Unit Tests: 100 (10%)  ← Too few!
# Integration Tests: 200 (20%)
# E2E Tests: 700 (70%)  ← Too many!

# Problems:
# - Tests are slow (suite takes 2+ hours)
# - Tests are brittle (UI changes break many tests)
# - Hard to debug (failures in E2E tests don't pinpoint issue)
```

---

## Choosing Test Type

### Decision Tree

```
What are you testing?
    ├─→ Pure logic (calculation, validation, algorithm)
    │       → Unit Test
    │
    ├─→ Database query/ORM
    │       → Integration Test
    │
    ├─→ API endpoint
    │       → Integration Test (if testing controller + service)
    │       → E2E Test (if testing full HTTP request/response)
    │
    ├─→ User workflow (signup, checkout, etc.)
    │       → E2E Test
    │
    └─→ External service integration
            → Contract Test + Unit Test with mocks
```

---

## Review Checklist

### Phase 2: Manual Review

**Test Distribution**:
- [ ] Is test distribution close to pyramid (60% unit, 30% integration, 10% E2E)?
- [ ] Are there enough unit tests?
- [ ] Are E2E tests minimal (< 10%)?

**Test Types**:
- [ ] Are unit tests isolated (using mocks)?
- [ ] Do integration tests test component interactions?
- [ ] Do E2E tests cover critical user workflows?

**Coverage by Type**:
- [ ] Is business logic covered by unit tests?
- [ ] Are database queries covered by integration tests?
- [ ] Are critical workflows covered by E2E tests?

**Performance**:
- [ ] Do unit tests run fast (< 10ms)?
- [ ] Do integration tests run reasonably (< 100ms)?
- [ ] Is test suite runtime acceptable (< 5 minutes)?

---

## Recommendations Format

```markdown
## Suggestion: Test Distribution (Inverted Pyramid)

**Category**: Testing Strategy
**Severity**: Suggestion
**Current Distribution**: 10% unit, 20% integration, 70% E2E
**Target Distribution**: 60-70% unit, 20-30% integration, 5-10% E2E

**Impact**: Slow test suite (2 hours), brittle tests, hard to debug failures.

**Current Breakdown**:
- Unit tests: 100 tests (10%)
- Integration tests: 200 tests (20%)
- E2E tests: 700 tests (70%) ← Inverted pyramid!

**Recommendation**:
Convert E2E tests to unit/integration tests where possible:

**Example**:
```python
# Current: E2E test (slow, brittle)
def test_calculate_order_total_e2e():
    # Full HTTP request
    response = client.post('/orders', json={...})
    assert response.json['total'] == 100

# Better: Unit test (fast, focused)
def test_calculate_order_total():
    order = Order(items=[Item(price=100)])
    assert order.calculate_total() == 100
```

**Target**: Increase unit tests to 600+, reduce E2E tests to 50.

**Resources**: See testing/test-types.md for testing pyramid.
```

---

## Summary

**Test Types**:
1. **Unit Tests** (60-70%): Fast, isolated, focused
2. **Integration Tests** (20-30%): Component interactions
3. **E2E Tests** (5-10%): Complete user workflows
4. **Contract Tests**: API contracts
5. **Performance Tests**: Performance requirements
6. **Security Tests**: Security requirements

**Testing Pyramid**:
- Many unit tests (foundation)
- Fewer integration tests
- Few E2E tests (top)

**Choosing Test Type**:
- Pure logic → Unit Test
- Database/ORM → Integration Test
- User workflow → E2E Test
- External API → Contract Test + Unit Test

**Detection**:
- Phase 2: Assess test distribution
- Check if pyramid inverted (too many E2E tests)

**Priority**: **Important** (affects test effectiveness and speed)

# Integration Tests: Verifying Merged Outputs

**Purpose**: Systematic testing after integration to ensure correctness

---

## Core Objective

Verify that integrated components work together correctly

---

## Test Levels

### Level 1: Smoke Tests (Quick Verification)

**Purpose**: Ensure basic functionality works after merge

**Examples**:
```bash
# Application starts
python app.py &
sleep 2
curl http://localhost:5000/health
# Expect: 200 OK

# Database migrations applied
python manage.py migrate --check
# Expect: No pending migrations

# Core imports work
python -c "from app import create_app; create_app()"
# Expect: No import errors
```

**Time**: <1 minute
**Run**: After every merge

---

### Level 2: Unit Tests (Component Verification)

**Purpose**: Verify individual components still work

**Examples**:
```bash
# Run all unit tests
pytest tests/unit/ -v

# Specific to merged components
pytest tests/unit/test_auth.py -v
pytest tests/unit/test_jwt.py -v
```

**Coverage**:
- All modified components have tests
- All tests pass
- No regressions (existing tests still pass)

**Time**: 1-5 minutes
**Run**: After every merge

---

### Level 3: Integration Tests (Cross-Component)

**Purpose**: Verify components work together

**Examples**:
```python
def test_auth_flow_integration():
    """Test complete authentication flow."""
    # 1. Register user
    response = client.post('/auth/register', json={
        'username': 'test', 'password': 'test123'
    })
    assert response.status_code == 201

    # 2. Login
    response = client.post('/auth/login', json={
        'username': 'test', 'password': 'test123'
    })
    assert response.status_code == 200
    token = response.json['access_token']

    # 3. Access protected endpoint
    response = client.get('/api/profile',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200

def test_token_refresh_integration():
    """Test token refresh flow."""
    # Login to get refresh token
    login_response = client.post('/auth/login', json={
        'username': 'test', 'password': 'test123'
    })
    refresh_token = login_response.json['refresh_token']

    # Use refresh token to get new access token
    response = client.post('/auth/refresh', json={
        'refresh_token': refresh_token
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
```

**Time**: 5-15 minutes
**Run**: After merging related components

---

### Level 4: End-to-End Tests (Full Workflow)

**Purpose**: Verify complete user workflows

**Examples**:
```python
def test_user_journey_end_to_end():
    """Test complete user journey from registration to usage."""
    # 1. New user registers
    register_response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'user@example.com',
        'password': 'secure123'
    })
    assert register_response.status_code == 201

    # 2. User logs in
    login_response = client.post('/auth/login', json={
        'username': 'newuser',
        'password': 'secure123'
    })
    assert login_response.status_code == 200
    access_token = login_response.json['access_token']

    # 3. User accesses protected resource
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_response = client.get('/api/profile', headers=headers)
    assert profile_response.status_code == 200

    # 4. User updates profile
    update_response = client.put('/api/profile', headers=headers, json={
        'name': 'John Doe'
    })
    assert update_response.status_code == 200

    # 5. User logs out
    logout_response = client.post('/auth/logout', headers=headers)
    assert logout_response.status_code == 200

    # 6. Verify token no longer works
    profile_response = client.get('/api/profile', headers=headers)
    assert profile_response.status_code == 401
```

**Time**: 15-30 minutes
**Run**: After major integrations

---

## Test Categories

### Functional Tests

**Verify**: Features work as specified

**Examples**:
- Login with valid credentials → Success
- Login with invalid credentials → Failure
- Access protected endpoint without token → 401 Unauthorized
- Access protected endpoint with valid token → Success

---

### Security Tests

**Verify**: Security requirements met

**Examples**:
```python
def test_password_hashing():
    """Verify passwords are hashed, not stored plaintext."""
    # Create user
    client.post('/auth/register', json={
        'username': 'test', 'password': 'plain123'
    })

    # Check database
    user = User.query.filter_by(username='test').first()
    assert user.password_hash != 'plain123'
    assert user.password_hash.startswith('$2b$')  # bcrypt

def test_jwt_expiration():
    """Verify JWT tokens expire."""
    # Login
    response = client.post('/auth/login', json={
        'username': 'test', 'password': 'test123'
    })
    token = response.json['access_token']

    # Wait for expiration (or mock time)
    time.sleep(901)  # 15 min + 1 sec

    # Token should be expired
    response = client.get('/api/profile',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 401
    assert 'expired' in response.json['error'].lower()

def test_rate_limiting():
    """Verify rate limiting prevents brute force."""
    # Attempt 6 logins (rate limit is 5)
    for i in range(6):
        response = client.post('/auth/login', json={
            'username': 'test', 'password': 'wrong'
        })

    # 6th attempt should be rate limited
    assert response.status_code == 429
    assert 'rate limit' in response.json['error'].lower()
```

---

### Performance Tests

**Verify**: Performance requirements met

**Examples**:
```python
def test_login_performance():
    """Verify login completes in <500ms."""
    import time

    start = time.time()
    response = client.post('/auth/login', json={
        'username': 'test', 'password': 'test123'
    })
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 0.5  # <500ms

def test_concurrent_logins():
    """Verify system handles concurrent logins."""
    from concurrent.futures import ThreadPoolExecutor

    def login():
        return client.post('/auth/login', json={
            'username': 'test', 'password': 'test123'
        })

    # 100 concurrent login attempts
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(login) for _ in range(100)]
        results = [f.result() for f in futures]

    # All should succeed
    assert all(r.status_code == 200 for r in results)
```

---

### Regression Tests

**Verify**: Existing functionality still works

**Examples**:
```python
def test_existing_endpoints_still_work():
    """Verify auth changes didn't break existing endpoints."""
    # Existing public endpoints
    response = client.get('/api/public/info')
    assert response.status_code == 200

    # Existing user endpoints
    token = login_and_get_token()
    response = client.get('/api/user/preferences',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
```

---

## Test Execution Workflow

### Step 1: Pre-Merge Testing

**Run in isolation**:
```bash
# Test each specialist's output independently
pytest tests/unit/test_jwt.py  # JWT module
pytest tests/unit/test_login.py  # Login endpoint
pytest tests/unit/test_refresh.py  # Refresh endpoint
```

**Verify**: All component tests pass in isolation

---

### Step 2: Post-Merge Testing

**Run after integration**:
```bash
# Smoke tests (fast)
pytest tests/smoke/ --tb=short

# Unit tests (component verification)
pytest tests/unit/ -v

# Integration tests (cross-component)
pytest tests/integration/ -v

# Coverage check
pytest tests/ --cov=app --cov-report=term-missing
```

**Verify**:
- All tests pass
- No regressions
- Coverage adequate (>80%)

---

### Step 3: Performance Verification

**Benchmark key operations**:
```bash
# Run performance tests
pytest tests/performance/ -v

# Load testing (optional)
locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 60s
```

**Verify**: Performance within acceptable range

---

### Step 4: Security Verification

**Run security tests**:
```bash
# Security-specific tests
pytest tests/security/ -v

# Static analysis
bandit -r app/

# Dependency vulnerability scan
safety check
```

**Verify**: No critical security issues

---

## Rollback Triggers

**Rollback merge if**:

**Critical Failures**:
- [ ] Smoke tests fail (basic functionality broken)
- [ ] Critical security test fails (vulnerabilities introduced)
- [ ] Database migrations fail (data corruption risk)
- [ ] Application won't start (deployment broken)

**Important Failures**:
- [ ] >10% of unit tests fail (significant regressions)
- [ ] Integration tests fail (component incompatibilities)
- [ ] Performance degraded >50% (unacceptable slowdown)
- [ ] Coverage dropped >10% (reduced test quality)

**Proceed with Caution**:
- [ ] Minor test failures (<5% of tests, non-critical)
- [ ] Performance degraded <20% (acceptable with justification)
- [ ] Coverage dropped <5% (acceptable if tests added elsewhere)

---

## Test Reporting

**Test Report Format**:
```
Integration Test Results
========================

Smoke Tests: ✅ PASS (3/3 tests, 0.5s)
Unit Tests: ✅ PASS (45/45 tests, 12.3s)
Integration Tests: ✅ PASS (12/12 tests, 23.1s)
Security Tests: ✅ PASS (8/8 tests, 5.2s)
Performance Tests: ✅ PASS (5/5 tests, 18.7s)

Coverage: 87.5% (target: >80%) ✅

Regressions: 0 ✅

Overall: ✅ PASS - Safe to proceed

Time: 59.8s total
```

---

## Continuous Integration

**Automated pipeline**:
```yaml
# .github/workflows/integration.yml
name: Integration Tests

on:
  push:
    branches: [integration]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run smoke tests
        run: pytest tests/smoke/ --tb=short
      - name: Run unit tests
        run: pytest tests/unit/ -v
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Run security tests
        run: pytest tests/security/ -v
      - name: Check coverage
        run: pytest tests/ --cov=app --cov-fail-under=80
```

---

## Checklist

Before declaring integration successful:

- [ ] All smoke tests pass
- [ ] All unit tests pass (no regressions)
- [ ] Integration tests pass (components work together)
- [ ] Security tests pass (no vulnerabilities)
- [ ] Performance tests pass (meets requirements)
- [ ] Coverage adequate (>80%)
- [ ] No critical issues detected
- [ ] Rollback plan ready (if needed)

---

## Summary

**Test Levels**:
1. Smoke (quick verification, <1min)
2. Unit (component verification, 1-5min)
3. Integration (cross-component, 5-15min)
4. End-to-end (full workflow, 15-30min)

**Test Categories**:
- Functional (features work)
- Security (requirements met)
- Performance (benchmarks met)
- Regression (existing functionality preserved)

**Rollback**: If critical or too many important failures

**Goal**: Verify integrated system works correctly before deployment

---
title: Example Login Endpoint Review
description: Complete walkthrough of reviewing a login endpoint
category: Examples
priority: Educational
---

# Example: Login Endpoint Review

Complete example demonstrating the code-reviewer workflow for a login endpoint with security vulnerabilities and quality issues.

---

## Code Submitted for Review

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = db.execute(f"SELECT * FROM users WHERE username='{username}'")[0]

    if user['password'] == password:
        session['user_id'] = user['id']
        return {'status': 'success'}
    return {'status': 'failed'}
```

---

## Review Process

### Phase 1: Automated Analysis

**Load Security Guidelines**: `security/vulnerabilities.md`

**Detected Issues**:
1. **SQL Injection** (Line 6): String concatenation in SQL query
2. **Plain Text Password** (Line 8): Password comparison without hashing
3. **Missing Input Validation** (Lines 4-5): No validation of user input

**Load Quality Guidelines**: `quality/clean-code.md`

**Detected Issues**:
1. **No Error Handling**: Missing try/except blocks
2. **Magic Strings**: 'success' and 'failed' literals
3. **Unclear Return Values**: Dictionary instead of proper HTTP responses

---

### Phase 2: Manual Review

**Load Architecture Guidelines**: `architecture/error-handling.md`

**Identified Issues**:
1. **No Error Handling**: What if user doesn't exist?
2. **No Input Validation**: Empty username/password not checked
3. **No Rate Limiting**: Vulnerable to brute force attacks
4. **Missing Security Headers**: No CSRF protection mentioned
5. **Session Security**: Session fixation vulnerability

**Load Testing Guidelines**: `testing/coverage.md`

**Identified Issues**:
1. **No Tests Provided**: No unit or integration tests
2. **Edge Cases Not Considered**:
   - Empty credentials
   - User not found
   - Multiple matching users
   - Database connection failure

---

### Phase 3: Feedback Synthesis

**Load Feedback Format**: `feedback/format.md`

---

## Detailed Review

### Critical Issues

#### 1. SQL Injection Vulnerability (line 6)

**Severity**: CRITICAL
**OWASP Category**: A03:2021 - Injection
**Exploitability**: HIGH

**Vulnerable Code**:
```python
user = db.execute(f"SELECT * FROM users WHERE username='{username}'")[0]
```

**Issue**:
SQL injection vulnerability through string concatenation. Attacker can execute arbitrary SQL commands by injecting malicious input.

**Attack Scenario**:
```python
# Attacker input
username = "admin' OR '1'='1"
password = "anything"

# Resulting query
"SELECT * FROM users WHERE username='admin' OR '1'='1'"
# This returns all users, bypassing authentication
```

**Fix**:
```python
# Use parameterized queries
cursor = db.cursor()
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)
)
user = cursor.fetchone()
```

**Why This Matters**:
- Attacker can bypass authentication entirely
- Can extract all user data from database
- Can modify or delete database records
- Can potentially execute system commands via database

**Priority**: Must fix before deployment

---

#### 2. Plain Text Password Storage (line 8)

**Severity**: CRITICAL
**OWASP Category**: A02:2021 - Cryptographic Failures
**Exploitability**: HIGH

**Vulnerable Code**:
```python
if user['password'] == password:
```

**Issue**:
Password compared as plain text, indicating passwords are stored unhashed. If database is compromised, all passwords are exposed.

**Fix**:
```python
# Store passwords hashed
from werkzeug.security import generate_password_hash, check_password_hash

# During registration
hashed_password = generate_password_hash(password)
db.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
           (username, hashed_password))

# During login
if check_password_hash(user['password'], password):
    session['user_id'] = user['id']
    return {'status': 'success'}, 200
```

**Alternative (Django)**:
```python
from django.contrib.auth.hashers import make_password, check_password

# Registration
user.password = make_password(password)

# Login
if check_password(password, user.password):
    # Login successful
```

**Why This Matters**:
- Database breach exposes all passwords
- Users often reuse passwords across sites
- Legal/compliance issues (GDPR, CCPA)
- Reputation damage from security breach

**Priority**: Must fix immediately

---

#### 3. Missing Input Validation (lines 4-5)

**Severity**: CRITICAL
**OWASP Category**: A03:2021 - Injection
**Exploitability**: MEDIUM

**Vulnerable Code**:
```python
username = request.form['username']
password = request.form['password']
```

**Issue**:
No validation of user input. Missing fields cause KeyError. Empty strings accepted.

**Fix**:
```python
# Validate input
from flask import request, jsonify

@app.route('/login', methods=['POST'])
def login():
    # Check fields exist
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({
            'status': 'error',
            'message': 'Username and password required'
        }), 400

    # Validate format
    if len(username) < 3 or len(username) > 50:
        return jsonify({
            'status': 'error',
            'message': 'Invalid username length'
        }), 400

    if len(password) < 8:
        return jsonify({
            'status': 'error',
            'message': 'Invalid password length'
        }), 400

    # Continue with authentication...
```

**Why This Matters**:
- Application crashes on missing fields
- Empty credentials bypass some security checks
- Poor user experience

**Priority**: Must fix

---

### Important Issues

#### 4. No Error Handling (lines 6, 8)

**Severity**: IMPORTANT
**Impact**: Application crashes, poor user experience

**Issue**:
No try/except blocks. Code crashes if:
- User doesn't exist (IndexError on line 6)
- Database connection fails
- Session storage fails

**Fix**:
```python
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Missing credentials'}), 400

        # Validate input
        if len(username) < 3 or len(password) < 8:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 400

        # Query database with parameterized query
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

        # Check password
        if not check_password_hash(user['password'], password):
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

        # Set session
        session['user_id'] = user['id']
        return jsonify({'status': 'success', 'user_id': user['id']}), 200

    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
```

**Why This Matters**:
- Application crashes expose internal details
- Poor user experience
- Difficult to debug production issues

**Priority**: Should fix

---

#### 5. Missing Rate Limiting

**Severity**: IMPORTANT
**OWASP Category**: A04:2021 - Insecure Design
**Exploitability**: HIGH

**Issue**:
No rate limiting allows brute force attacks on user accounts.

**Fix**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def login():
    # Login logic...
```

**Alternative (Manual)**:
```python
from datetime import datetime, timedelta

# Track failed attempts
failed_attempts = {}

@app.route('/login', methods=['POST'])
def login():
    ip = request.remote_addr

    # Check if IP is rate limited
    if ip in failed_attempts:
        attempts, last_attempt = failed_attempts[ip]
        if attempts >= 5 and datetime.now() - last_attempt < timedelta(minutes=15):
            return jsonify({
                'status': 'error',
                'message': 'Too many failed attempts. Try again in 15 minutes.'
            }), 429

    # Attempt login...

    # On failure, track attempt
    if not login_successful:
        if ip not in failed_attempts:
            failed_attempts[ip] = [0, datetime.now()]
        failed_attempts[ip][0] += 1
        failed_attempts[ip][1] = datetime.now()
```

**Why This Matters**:
- Brute force attacks can compromise accounts
- Automated bots can attempt millions of passwords
- Account takeover risk

**Priority**: Should fix before production

---

#### 6. Missing Security Logging

**Severity**: IMPORTANT
**OWASP Category**: A09:2021 - Security Logging and Monitoring Failures

**Issue**:
No logging of login attempts (successful or failed).

**Fix**:
```python
import logging

security_logger = logging.getLogger('security')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')

    try:
        # Authentication logic...

        if authentication_successful:
            security_logger.info(f"Successful login: {username} from {request.remote_addr}")
            return jsonify({'status': 'success'}), 200
        else:
            security_logger.warning(f"Failed login attempt: {username} from {request.remote_addr}")
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    except Exception as e:
        security_logger.error(f"Login error for {username}: {e}")
        return jsonify({'status': 'error', 'message': 'Internal error'}), 500
```

**Why This Matters**:
- Cannot detect attack patterns
- Cannot investigate security incidents
- Compliance requirements (PCI-DSS, HIPAA)

**Priority**: Should fix

---

### Suggestions

#### 7. Improve Return Values

**Current**:
```python
return {'status': 'success'}
return {'status': 'failed'}
```

**Suggestion**:
```python
# Use proper HTTP status codes and JSON responses
from flask import jsonify

# Success
return jsonify({'status': 'success', 'user_id': user['id']}), 200

# Failure (authentication)
return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

# Failure (validation)
return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

# Failure (server error)
return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
```

**Benefit**: Clear status codes for clients, proper REST API design

---

#### 8. Add CSRF Protection

**Issue**: Form submission vulnerable to CSRF attacks

**Suggestion**:
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Require CSRF token for POST requests
@app.route('/login', methods=['POST'])
@csrf.exempt  # Only if using token-based auth instead
def login():
    # Login logic...
```

**Benefit**: Prevents cross-site request forgery attacks

---

## Recommended Implementation

**Complete Secure Login Endpoint**:

```python
from flask import Flask, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
import logging

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
security_logger = logging.getLogger('security')

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Authenticate user with username and password.

    Returns:
        200: Login successful
        400: Invalid input
        401: Invalid credentials
        429: Rate limit exceeded
        500: Internal server error
    """
    try:
        # Get and validate input
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            security_logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
            return jsonify({
                'status': 'error',
                'message': 'Username and password required'
            }), 400

        # Validate format
        if len(username) < 3 or len(username) > 50:
            return jsonify({
                'status': 'error',
                'message': 'Invalid username format'
            }), 400

        if len(password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Invalid password format'
            }), 400

        # Query database with parameterized query
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        # Check if user exists and password is correct
        if not user or not check_password_hash(user['password'], password):
            security_logger.warning(
                f"Failed login attempt for username '{username}' from {request.remote_addr}"
            )
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        # Set session
        session['user_id'] = user['id']
        session.permanent = True

        security_logger.info(
            f"Successful login for username '{username}' from {request.remote_addr}"
        )

        return jsonify({
            'status': 'success',
            'user_id': user['id']
        }), 200

    except Exception as e:
        security_logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
```

---

## Testing Recommendations

**Unit Tests**:
```python
def test_login_success():
    """Test successful login with valid credentials."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'ValidPassword123'
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_login_invalid_credentials():
    """Test login with incorrect password."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert 'Invalid credentials' in response.json['message']

def test_login_missing_fields():
    """Test login with missing username or password."""
    response = client.post('/login', data={'username': 'testuser'})
    assert response.status_code == 400
    assert 'required' in response.json['message']

def test_login_rate_limiting():
    """Test rate limiting after multiple failed attempts."""
    for _ in range(5):
        client.post('/login', data={'username': 'test', 'password': 'wrong'})

    response = client.post('/login', data={'username': 'test', 'password': 'wrong'})
    assert response.status_code == 429

def test_login_sql_injection_attempt():
    """Test that SQL injection attempts are prevented."""
    response = client.post('/login', data={
        'username': "admin' OR '1'='1",
        'password': 'anything'
    })
    assert response.status_code == 401  # Should fail authentication
```

---

## Review Summary

**Overall Assessment**: Request Changes (Critical issues must be fixed)

**Critical Issues**: 3
**Important Issues**: 3
**Suggestions**: 2

**Key Strengths**:
- Simple, clear endpoint structure
- Using Flask framework correctly

**Must Fix Before Approval**:
1. SQL injection vulnerability (parameterized queries)
2. Plain text password storage (use password hashing)
3. Missing input validation (validate all inputs)
4. Add error handling (try/except blocks)
5. Implement rate limiting (prevent brute force)
6. Add security logging (track login attempts)

**Estimated Time to Fix**: 2-3 hours

**Next Steps**:
1. Implement fixes for critical issues
2. Add comprehensive tests
3. Request re-review
4. Deploy with monitoring

---

## References

- OWASP Top 10: https://owasp.org/Top10/
- Flask Security: https://flask.palletsprojects.com/en/2.0.x/security/
- Password Hashing: `security/vulnerabilities.md`
- Input Validation: `security/input-validation.md`

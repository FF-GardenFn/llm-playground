# OWASP Top 10 Security Checklist

**Purpose**: Comprehensive OWASP Top 10 (2021) checklist for security-focused code review.

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Critical (security vulnerabilities)

**Source**: [OWASP Top 10 - 2021](https://owasp.org/Top10/)

---

## Overview

The OWASP Top 10 represents the most critical security risks to web applications. Code-reviewer must check for all 10 categories during security scan.

---

## OWASP Top 10 (2021)

### A01:2021 – Broken Access Control

**Risk**: Users can act outside their intended permissions.

**Detection Checklist**:

**1. Missing Authorization Checks**
- [ ] Are authorization checks present before sensitive operations?
- [ ] Are checks performed server-side (not just client-side)?
- [ ] Are checks bypassed in error handling paths?

```python
# BAD: Missing authorization
@app.route('/admin/delete_user/<user_id>')
def delete_user(user_id):
    User.objects.get(id=user_id).delete()  # Anyone can delete!
    return "Deleted"

# GOOD: Authorization check
@app.route('/admin/delete_user/<user_id>')
@require_admin  # Decorator checks admin role
def delete_user(user_id):
    User.objects.get(id=user_id).delete()
    return "Deleted"
```

**2. Insecure Direct Object References (IDOR)**
- [ ] Can users access resources by changing IDs in URL?
- [ ] Are resource ownership checks performed?
- [ ] Are UUIDs used instead of sequential IDs?

```python
# BAD: IDOR vulnerability
@app.route('/invoice/<invoice_id>')
def view_invoice(invoice_id):
    # No check if current_user owns this invoice!
    return Invoice.objects.get(id=invoice_id)

# GOOD: Ownership check
@app.route('/invoice/<invoice_id>')
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    if invoice.user_id != current_user.id:
        abort(403, "Access denied")
    return invoice
```

**3. Privilege Escalation**
- [ ] Can users modify their role/permissions?
- [ ] Are admin-only parameters filtered from user input?
- [ ] Is mass assignment prevented?

```python
# BAD: Mass assignment vulnerability
@app.route('/profile/update', methods=['POST'])
def update_profile():
    # User can set is_admin=True in POST!
    user = current_user
    user.update(**request.form)

# GOOD: Whitelist allowed fields
@app.route('/profile/update', methods=['POST'])
def update_profile():
    ALLOWED_FIELDS = ['name', 'email', 'bio']
    data = {k: v for k, v in request.form.items() if k in ALLOWED_FIELDS}
    current_user.update(**data)
```

**Severity**: **Critical** if allows unauthorized access to sensitive resources

---

### A02:2021 – Cryptographic Failures

**Risk**: Exposure of sensitive data due to weak or missing encryption.

**Detection Checklist**:

**1. Sensitive Data Storage**
- [ ] Are passwords hashed (not encrypted or plaintext)?
- [ ] Is bcrypt/argon2/PBKDF2 used (not MD5/SHA1)?
- [ ] Are API keys stored in environment variables (not code)?

```python
# BAD: Plaintext password
user.password = request.form['password']

# GOOD: Hashed password
from werkzeug.security import generate_password_hash
user.password_hash = generate_password_hash(request.form['password'])
```

**2. Data in Transit**
- [ ] Is HTTPS enforced (not optional)?
- [ ] Are TLS 1.2+ used (not TLS 1.0/1.1)?
- [ ] Are secure cookies used (`Secure`, `HttpOnly` flags)?

```python
# BAD: Cookie without security flags
response.set_cookie('session_id', session_id)

# GOOD: Secure cookie
response.set_cookie('session_id', session_id, secure=True, httponly=True, samesite='Strict')
```

**3. Weak Cryptography**
- [ ] Are strong algorithms used (AES-256, RSA-2048+)?
- [ ] Are random secrets generated securely (`secrets` module)?
- [ ] Are keys rotated regularly?

```python
# BAD: Weak random generation
import random
token = random.randint(1000, 9999)  # Predictable!

# GOOD: Cryptographically secure random
import secrets
token = secrets.token_urlsafe(32)
```

**Severity**: **Critical** if exposes passwords, credit cards, personal data

---

### A03:2021 – Injection

**Risk**: Untrusted data executed as commands or queries.

**Detection Checklist**:

**1. SQL Injection** (See: `security/input-validation.md`)
- [ ] Are parameterized queries used?
- [ ] Is ORM used correctly (no raw SQL with user input)?
- [ ] Are stored procedures parameterized?

**2. NoSQL Injection**
- [ ] Are MongoDB queries parameterized?
- [ ] Is user input sanitized before use in queries?

```python
# BAD: NoSQL injection
db.users.find({"username": request.form['username']})  # Can inject {"$ne": null}

# GOOD: Type validation
username = str(request.form['username'])  # Ensure string
db.users.find({"username": username})
```

**3. Command Injection** (See: `security/input-validation.md`)
- [ ] Is `subprocess` used with argument list (not shell=True)?
- [ ] Is user input in system commands avoided?

**4. LDAP/XPath Injection**
- [ ] Are LDAP queries parameterized?
- [ ] Is input validated before use in directory queries?

**Severity**: **Critical** (allows arbitrary code execution or data access)

---

### A04:2021 – Insecure Design

**Risk**: Security flaws in architecture and design.

**Detection Checklist**:

**1. Missing Security Controls**
- [ ] Are rate limits implemented (prevent brute force)?
- [ ] Is CAPTCHA used for public forms?
- [ ] Are session timeouts configured?

```python
# GOOD: Rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts/minute
def login():
    # Login logic
```

**2. Insufficient Logging**
- [ ] Are security events logged (login, logout, failures)?
- [ ] Are logs protected from tampering?
- [ ] Are sensitive data excluded from logs?

**3. Missing Threat Modeling**
- [ ] Has threat modeling been performed?
- [ ] Are security requirements documented?
- [ ] Are trust boundaries identified?

**Severity**: **Important** (architectural issues require design changes)

---

### A05:2021 – Security Misconfiguration

**Risk**: Default configurations, incomplete setups, unpatched systems.

**Detection Checklist**:

**1. Debug Mode in Production**
- [ ] Is debug mode disabled in production?
- [ ] Are error messages generic (not exposing stack traces)?
- [ ] Are default credentials changed?

```python
# BAD: Debug enabled
app.run(debug=True)

# GOOD: Debug disabled
app.run(debug=False)
```

**2. Unnecessary Features Enabled**
- [ ] Are unused endpoints disabled?
- [ ] Are unnecessary HTTP methods blocked?
- [ ] Are directory listings disabled?

**3. Missing Security Headers**
- [ ] Is Content-Security-Policy header set?
- [ ] Is X-Frame-Options header set (prevent clickjacking)?
- [ ] Is X-Content-Type-Options set to nosniff?

```python
# GOOD: Security headers
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

**Severity**: **Important** (facilitates other attacks)

---

### A06:2021 – Vulnerable and Outdated Components

**Risk**: Using libraries with known vulnerabilities.

**Detection Checklist**:

**1. Outdated Dependencies**
- [ ] Are all dependencies up-to-date?
- [ ] Is `pip-audit` or `safety` run regularly?
- [ ] Are vulnerability scans automated (CI/CD)?

```bash
# GOOD: Dependency scanning
pip install safety
safety check  # Checks for known vulnerabilities

pip install pip-audit
pip-audit  # Audit dependencies
```

**2. Unused Dependencies**
- [ ] Are unused libraries removed?
- [ ] Is dependency bloat minimized?

**3. Unverified Sources**
- [ ] Are dependencies from trusted sources (PyPI, npm)?
- [ ] Are checksums verified?

**Severity**: **Critical** if vulnerable component is exploitable

---

### A07:2021 – Identification and Authentication Failures

**Risk**: Weak authentication allows attackers to compromise accounts.

**Detection Checklist**:

**1. Weak Password Policy**
- [ ] Is minimum password length enforced (≥12 characters)?
- [ ] Are common passwords blocked (use `pwned-passwords-django`)?
- [ ] Is password complexity required?

**2. Missing MFA**
- [ ] Is multi-factor authentication available?
- [ ] Is MFA enforced for admin accounts?

**3. Session Management**
- [ ] Are session IDs regenerated after login (prevent fixation)?
- [ ] Are sessions invalidated on logout?
- [ ] Are session timeouts configured?

```python
# GOOD: Session regeneration
@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form['username'], request.form['password'])
    if user:
        session.regenerate()  # Prevent session fixation
        session['user_id'] = user.id
```

**4. Credential Stuffing**
- [ ] Are rate limits on login implemented?
- [ ] Is account lockout after failed attempts configured?

**Severity**: **Critical** (allows account takeover)

---

### A08:2021 – Software and Data Integrity Failures

**Risk**: Code or data modified without verification.

**Detection Checklist**:

**1. Unsigned Software Updates**
- [ ] Are updates signed and verified?
- [ ] Is integrity checking implemented?

**2. Insecure Deserialization**
- [ ] Is `pickle` avoided for untrusted data?
- [ ] Is JSON used instead of pickle?
- [ ] Are deserialization safeguards in place?

```python
# BAD: Unsafe deserialization
import pickle
data = pickle.loads(request.data)  # Arbitrary code execution!

# GOOD: Safe deserialization
import json
data = json.loads(request.data)  # Only data, no code
```

**3. CI/CD Pipeline Security**
- [ ] Are secrets excluded from repositories?
- [ ] Are build artifacts verified?
- [ ] Is least privilege enforced in CI/CD?

**Severity**: **Critical** (allows code execution or data tampering)

---

### A09:2021 – Security Logging and Monitoring Failures

**Risk**: Attacks go undetected due to insufficient logging.

**Detection Checklist**:

**1. Insufficient Logging**
- [ ] Are security events logged (login, logout, access control failures)?
- [ ] Are high-value transactions logged?
- [ ] Are suspicious activities logged (failed login attempts)?

```python
# GOOD: Security logging
import logging

logger = logging.getLogger(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if not authenticate(username, request.form['password']):
        logger.warning(f"Failed login attempt for user: {username} from IP: {request.remote_addr}")
        return "Invalid credentials", 401

    logger.info(f"Successful login: {username} from IP: {request.remote_addr}")
```

**2. Log Injection**
- [ ] Is user input sanitized before logging?
- [ ] Are logs structured (JSON) to prevent injection?

```python
# BAD: Log injection
logger.info(f"User input: {request.form['data']}")  # Can inject newlines

# GOOD: Structured logging
logger.info("User input received", extra={"data": request.form['data']})
```

**3. Missing Alerting**
- [ ] Are alerts configured for critical events?
- [ ] Are logs monitored in real-time?
- [ ] Is incident response plan documented?

**Severity**: **Important** (delays detection and response)

---

### A10:2021 – Server-Side Request Forgery (SSRF)

**Risk**: Attacker forces server to make unintended requests.

**Detection Checklist**:

**1. Unvalidated URLs**
- [ ] Is URL input validated before use?
- [ ] Are internal URLs blocked (localhost, 127.0.0.1, 10.0.0.0/8)?
- [ ] Is URL scheme whitelisted (http/https only)?

```python
# BAD: SSRF vulnerability
import requests

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    response = requests.get(url)  # Can access internal services!
    return response.text

# GOOD: URL validation
import requests
from urllib.parse import urlparse

ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com']

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    parsed = urlparse(url)

    # Block internal IPs
    if parsed.hostname in ['localhost', '127.0.0.1'] or parsed.hostname.startswith('10.'):
        abort(403, "Invalid URL")

    # Whitelist allowed hosts
    if parsed.hostname not in ALLOWED_HOSTS:
        abort(403, "Host not allowed")

    response = requests.get(url, timeout=5)
    return response.text
```

**2. Cloud Metadata Access**
- [ ] Are cloud metadata endpoints blocked (169.254.169.254)?
- [ ] Is network segmentation in place?

**3. Redirect Following**
- [ ] Are redirects disabled or limited?
- [ ] Are redirect targets validated?

```python
# GOOD: Disable redirects
response = requests.get(url, allow_redirects=False, timeout=5)
```

**Severity**: **High** (allows access to internal systems)

---

## Security Review Checklist

### Phase 1: Automated Analysis

Run automated security scanners:

```bash
# 1. Static Analysis Security Testing (SAST)
bandit -r src/  # Python security linter

# 2. Dependency Scanning
safety check
pip-audit

# 3. Secret Detection
trufflehog --regex --entropy=True .
```

### Phase 2: Manual Review

**Authentication & Authorization**:
- [ ] A01: All sensitive operations require authentication
- [ ] A01: Authorization checks present and server-side
- [ ] A07: Strong password policy enforced
- [ ] A07: Session management secure

**Input Validation**:
- [ ] A03: All inputs validated (SQL, NoSQL, Command injection)
- [ ] A03: Parameterized queries used throughout
- [ ] A10: URL inputs validated (SSRF prevention)

**Cryptography**:
- [ ] A02: Passwords hashed with bcrypt/argon2
- [ ] A02: HTTPS enforced
- [ ] A02: Secure cookies used

**Configuration**:
- [ ] A05: Debug mode disabled in production
- [ ] A05: Security headers present
- [ ] A05: Default credentials changed

**Dependencies**:
- [ ] A06: All dependencies up-to-date
- [ ] A06: Vulnerability scan passed

**Logging & Monitoring**:
- [ ] A09: Security events logged
- [ ] A09: Logs protected from injection
- [ ] A09: Alerting configured

**Data Integrity**:
- [ ] A08: Deserialization safe (no pickle on untrusted data)
- [ ] A08: Code signing implemented

**Design**:
- [ ] A04: Rate limiting implemented
- [ ] A04: Security requirements documented

---

## Integration with Code-Reviewer Process

### Phase 1: Automated Analysis

```markdown
Load OWASP checklist:
  {{load: ../security/owasp-checklist.md}}

Run security scan against all 10 categories:
  - A01: Access Control
  - A02: Cryptographic Failures
  - A03: Injection
  - A04: Insecure Design
  - A05: Security Misconfiguration
  - A06: Vulnerable Components
  - A07: Authentication Failures
  - A08: Data Integrity Failures
  - A09: Logging Failures
  - A10: SSRF

Output: Categorized security findings with OWASP ID
```

### Phase 4: Priority Assessment

**Severity Mapping**:
- **Critical**: A01 (unauthorized access), A02 (data exposure), A03 (injection), A07 (auth bypass), A08 (code execution)
- **High**: A10 (SSRF), A06 (exploitable vulnerability)
- **Important**: A04 (design flaws), A05 (misconfiguration), A09 (logging failures)

### Phase 5: Recommendations

```markdown
## Critical: SQL Injection (A03:2021)

**OWASP Category**: A03:2021 – Injection
**Severity**: CRITICAL
**Impact**: Arbitrary SQL execution, data breach

**Current Code**: [vulnerable code]
**Fix**: [secure code with parameterized queries]

**Verification**:
- Run SQL injection tests
- Verify all queries parameterized
- See: security/input-validation.md

**OWASP Resources**: https://owasp.org/Top10/A03_2021-Injection/
```

---

## Summary

**OWASP Top 10 (2021)**:
1. **A01**: Broken Access Control
2. **A02**: Cryptographic Failures
3. **A03**: Injection
4. **A04**: Insecure Design
5. **A05**: Security Misconfiguration
6. **A06**: Vulnerable Components
7. **A07**: Authentication Failures
8. **A08**: Data Integrity Failures
9. **A09**: Logging Failures
10. **A10**: Server-Side Request Forgery

**Code-Reviewer Coverage**:
- Phase 1: Automated scan for all 10 categories
- Phase 2: Manual review for design and business logic
- Phase 4: Classify by OWASP category and severity
- Phase 5: Provide OWASP-referenced recommendations

**Non-Refactorable**: All OWASP issues require security fixes, not behavior-preserving refactorings.

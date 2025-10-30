# Security Regression Check

**Purpose**: Verify that code changes (especially refactorings) do not introduce new security vulnerabilities or remove existing protections.

**Phase**: Phase 1 (Verification Mode) - Invoked by refactoring-engineer Phase 5

**Integration Mode**: Mode 3 (Verification)

**Priority**: Critical (prevent security regressions)

---

## Overview

When code-reviewer is invoked in Verification Mode by refactoring-engineer, it must perform comprehensive security regression checks to ensure refactored code maintains security properties.

**Key Question**: Did the refactoring introduce new vulnerabilities or weaken existing security controls?

---

## Verification Mode Security Checks

### Input Format

When invoked by refactoring-engineer:

```json
{
  "invocation_type": "verification_request",
  "mode": "verification",
  "code_before": {
    "file": "src/user_service.py",
    "content": "...",
    "security_scan_results": {
      "vulnerabilities": [],
      "security_controls": ["input_validation", "authorization_check"]
    }
  },
  "code_after": {
    "file": "src/user_service.py",
    "content": "..."
  },
  "refactoring_applied": {
    "pattern": "extract_method",
    "description": "Extracted 3 methods to reduce complexity"
  }
}
```

### Security Regression Checklist

#### 1. No New Vulnerabilities

**Check**: Scan code_after for vulnerabilities not present in code_before

```markdown
Run security scan on code_after:
  - SQL Injection
  - XSS
  - Command Injection
  - Path Traversal
  - SSRF
  - Insecure Deserialization

Compare with code_before:
  - New vulnerabilities found? → FAIL
  - Same or fewer vulnerabilities? → PASS
```

**Example - PASS**:
```python
# code_before (no SQL injection)
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))

# code_after (refactored, still no SQL injection)
def get_user(user_id):
    query = build_user_query()
    return execute_user_query(query, user_id)

def build_user_query():
    return "SELECT * FROM users WHERE id = %s"

def execute_user_query(query, user_id):
    return db.execute(query, (user_id,))

# ✓ PASS: No new vulnerabilities introduced
```

**Example - FAIL**:
```python
# code_before (secure parameterized query)
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))

# code_after (REGRESSION: introduced SQL injection!)
def get_user(user_id):
    query = build_user_query(user_id)  # ← BUG: included user_id in query string
    return execute_user_query(query)

def build_user_query(user_id):
    return f"SELECT * FROM users WHERE id = {user_id}"  # ← SQL INJECTION!

def execute_user_query(query):
    return db.execute(query)

# ✗ FAIL: SQL injection introduced by refactoring
```

---

#### 2. Security Controls Preserved

**Check**: Verify all security controls from code_before are still present in code_after

**Security Controls to Check**:
- Authentication checks (`@login_required`, `@require_auth`)
- Authorization checks (role checks, permission checks)
- Input validation (whitelist validation, type checking)
- Output encoding (HTML escaping, JSON encoding)
- Rate limiting (`@limiter.limit()`)
- CSRF protection
- Security headers

**Example - PASS**:
```python
# code_before
@app.route('/admin/delete_user/<user_id>')
@login_required
@require_admin
def delete_user(user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return "Deleted"

# code_after (refactored)
@app.route('/admin/delete_user/<user_id>')
@login_required
@require_admin
def delete_user(user_id):
    user = find_user(user_id)
    perform_delete(user)
    return "Deleted"

def find_user(user_id):
    return User.objects.get(id=user_id)

def perform_delete(user):
    user.delete()

# ✓ PASS: @login_required and @require_admin preserved
```

**Example - FAIL**:
```python
# code_before
@app.route('/admin/delete_user/<user_id>')
@login_required
@require_admin
def delete_user(user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return "Deleted"

# code_after (REGRESSION: lost @require_admin!)
@app.route('/admin/delete_user/<user_id>')
@login_required  # ← Still has @login_required
def delete_user(user_id):  # ← MISSING @require_admin!
    user = find_user(user_id)
    perform_delete(user)
    return "Deleted"

# ✗ FAIL: Authorization control removed (any logged-in user can delete)
```

---

#### 3. Attack Surface Not Increased

**Check**: Verify refactoring did not expose new attack vectors

**Attack Surface Indicators**:
- New public methods/endpoints
- Increased parameter count (more input to validate)
- New external dependencies
- New file I/O operations
- New network calls

**Example - PASS**:
```python
# code_before
class UserService:
    def create_user(self, username, email):
        # Validates input, creates user
        pass

# code_after (refactored with extracted private methods)
class UserService:
    def create_user(self, username, email):
        self._validate_input(username, email)
        user = self._build_user(username, email)
        self._save_user(user)

    def _validate_input(self, username, email):  # Private method
        pass

    def _build_user(self, username, email):  # Private method
        pass

    def _save_user(self, user):  # Private method
        pass

# ✓ PASS: No new public methods (all extracted methods are private)
```

**Example - FAIL**:
```python
# code_before
class UserService:
    def create_user(self, username, email):
        # Only public method
        pass

# code_after (REGRESSION: exposed internal methods as public)
class UserService:
    def create_user(self, username, email):
        self.validate_input(username, email)  # Public!
        user = self.build_user(username, email)  # Public!
        self.save_user(user)  # Public!

    def validate_input(self, username, email):  # ← EXPOSED
        pass

    def build_user(self, username, email):  # ← EXPOSED
        pass

    def save_user(self, user):  # ← EXPOSED (now callers can bypass validation!)
        pass

# ✗ FAIL: Attack surface increased (callers can bypass validation by calling save_user directly)
```

---

#### 4. Data Flow Security Maintained

**Check**: Verify sensitive data handling is unchanged

**Data Flow Checks**:
- Sensitive data still encrypted in transit?
- Sensitive data still hashed/encrypted at rest?
- Sensitive data not logged?
- Sensitive data sanitized before output?

**Example - PASS**:
```python
# code_before
def handle_login(username, password):
    user = User.objects.get(username=username)
    if check_password(password, user.password_hash):  # Password never in plaintext
        return create_session(user)

# code_after (refactored)
def handle_login(username, password):
    user = find_user(username)
    if verify_credentials(user, password):  # Password still never in plaintext
        return create_session(user)

def verify_credentials(user, password):
    return check_password(password, user.password_hash)

# ✓ PASS: Password never exposed in plaintext
```

**Example - FAIL**:
```python
# code_before
def handle_login(username, password):
    user = User.objects.get(username=username)
    if check_password(password, user.password_hash):
        return create_session(user)

# code_after (REGRESSION: logs password!)
def handle_login(username, password):
    logger.info(f"Login attempt: {username}")  # OK
    user = find_user(username)
    if verify_credentials(user, password):
        return create_session(user)

def verify_credentials(user, password):
    logger.debug(f"Verifying password: {password}")  # ← LOGS PASSWORD!
    return check_password(password, user.password_hash)

# ✗ FAIL: Password leaked to logs
```

---

#### 5. Error Handling Security Unchanged

**Check**: Verify error paths don't leak information or bypass security

**Error Handling Checks**:
- Exceptions don't expose stack traces to users?
- Error paths don't bypass authentication/authorization?
- Errors logged appropriately (not exposing secrets)?

**Example - FAIL**:
```python
# code_before
@login_required
def process_payment(amount):
    try:
        charge_card(amount)
    except CardError as e:
        return "Payment failed", 400

# code_after (REGRESSION: bypasses authentication on error!)
def process_payment(amount):
    try:
        require_authentication()  # Check moved inside try
        charge_card(amount)
    except CardError as e:
        return "Payment failed", 400
    except AuthenticationError:
        return "Not authenticated", 401  # ← Returns without raising, bypasses @login_required!

# ✗ FAIL: Error handling bypasses authentication control
```

---

## Automated Regression Detection

### Diff-Based Security Analysis

```python
# security/regression_detector.py

def detect_security_regression(code_before, code_after):
    """
    Automated security regression detection.
    """
    regressions = []

    # 1. Scan both versions
    vulns_before = security_scan(code_before)
    vulns_after = security_scan(code_after)

    # 2. New vulnerabilities?
    new_vulns = [v for v in vulns_after if v not in vulns_before]
    if new_vulns:
        regressions.append({
            "type": "new_vulnerability",
            "details": new_vulns,
            "severity": "critical"
        })

    # 3. Security controls removed?
    controls_before = extract_security_controls(code_before)
    controls_after = extract_security_controls(code_after)

    removed_controls = controls_before - controls_after
    if removed_controls:
        regressions.append({
            "type": "removed_security_control",
            "details": list(removed_controls),
            "severity": "critical"
        })

    # 4. Attack surface increased?
    surface_before = calculate_attack_surface(code_before)
    surface_after = calculate_attack_surface(code_after)

    if surface_after > surface_before:
        regressions.append({
            "type": "increased_attack_surface",
            "details": f"Attack surface: {surface_before} → {surface_after}",
            "severity": "important"
        })

    return regressions

def extract_security_controls(code):
    """
    Extract decorators, validators, etc.
    """
    controls = set()

    # Look for authentication decorators
    if '@login_required' in code:
        controls.add('authentication')
    if '@require_admin' in code:
        controls.add('authorization')

    # Look for input validation
    if 'validate_' in code or 'is_valid_' in code:
        controls.add('input_validation')

    # Look for CSRF protection
    if 'csrf_token' in code or '@csrf_protect' in code:
        controls.add('csrf_protection')

    return controls

def calculate_attack_surface(code):
    """
    Count public methods, endpoints, parameters.
    """
    import ast
    tree = ast.parse(code)

    surface = 0
    for node in ast.walk(tree):
        # Count public methods
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):
                surface += 1

        # Count route decorators
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if hasattr(decorator.func, 'attr') and decorator.func.attr == 'route':
                        surface += 5  # Endpoints have higher weight

    return surface
```

---

## Verification Mode Output

### Success Example

```json
{
  "verification_passed": true,
  "checks": {
    "security_regression": {
      "passed": true,
      "new_vulnerabilities": 0,
      "removed_controls": 0,
      "attack_surface_delta": 0,
      "details": "No security regressions detected"
    }
  },
  "recommendation": "APPROVE"
}
```

### Failure Example

```json
{
  "verification_passed": false,
  "checks": {
    "security_regression": {
      "passed": false,
      "new_vulnerabilities": 1,
      "removed_controls": 1,
      "attack_surface_delta": 3,
      "details": {
        "new_vulnerabilities": [
          {
            "type": "sql_injection",
            "location": "src/user_service.py:45",
            "description": "Refactoring introduced SQL injection in extracted method"
          }
        ],
        "removed_controls": [
          {
            "type": "authorization",
            "location": "src/admin_controller.py:23",
            "description": "@require_admin decorator lost during extraction"
          }
        ],
        "attack_surface": {
          "before": 5,
          "after": 8,
          "increase": "+3 public methods"
        }
      }
    }
  },
  "recommendation": "REQUEST_CHANGES",
  "required_fixes": [
    "Fix SQL injection in src/user_service.py:45 (use parameterized query)",
    "Restore @require_admin decorator in src/admin_controller.py:23",
    "Make 3 public methods private (use _ prefix)"
  ]
}
```

---

## Integration with Code-Reviewer Workflow

### Verification Mode Process

```
Refactoring-Engineer Phase 5: Verification
    ↓
Invoke Code-Reviewer (Verification Mode):
    Input: {code_before, code_after, refactoring_applied}
    ↓
Code-Reviewer:
    Phase 1: Security Regression Check
        → Scan code_after for vulnerabilities
        → Compare with code_before
        → Check security controls preserved
        → Check attack surface unchanged
        → Check data flow security maintained
        ↓
    Result: PASS or FAIL
        ↓
    PASS → Verification report (APPROVE)
    FAIL → Regression report (REQUEST_CHANGES with fixes)
    ↓
Return to Refactoring-Engineer
```

### Phase 1: Security Regression Check

```markdown
# code-reviewer/workflows/REVIEW_PROCESS.md

## Verification Mode (Invoked by Refactoring-Engineer)

### Phase 1: Security Regression Check (REQUIRED)

Load security regression checklist:
  {{load: ../security/regression-check.md}}

Run automated regression detection:
  1. Scan code_after for vulnerabilities
  2. Compare with code_before security scan
  3. Extract security controls from both versions
  4. Calculate attack surface delta
  5. Check data flow security unchanged

Decision:
  - New vulnerabilities? → FAIL
  - Security controls removed? → FAIL
  - Attack surface increased? → WARN (may fail depending on severity)
  - All checks pass? → PASS
```

---

## Common Refactoring Risks

### Risk 1: Extract Method Loses Decorator

**Scenario**: Extracting code that includes security check

```python
# Before (secure)
@login_required
def delete_account():
    user = current_user
    user.delete()

# After (INSECURE - decorator lost!)
def delete_account():
    perform_delete()

def perform_delete():  # ← Missing @login_required!
    user = current_user  # ← Will fail if not authenticated
    user.delete()
```

**Detection**: Check that extracted methods either:
1. Are private (not callable directly)
2. Have same security decorators as original

---

### Risk 2: Move Method Bypasses Validation

**Scenario**: Moving validation logic separates it from the method that needs it

```python
# Before (secure)
class UserController:
    def update_email(self, email):
        self.validate_email(email)
        self.user.email = email
        self.user.save()

# After (INSECURE - validation can be bypassed!)
class UserController:
    def update_email(self, email):
        self.user.email = email
        self.user.save()  # ← Validation missing!

class EmailValidator:
    @staticmethod
    def validate_email(email):  # ← Validation moved but not called!
        # Validation logic
        pass
```

**Detection**: Trace validation calls - ensure still present after refactoring

---

### Risk 3: Rename Variable Changes Security Logic

**Scenario**: Renaming variable that's checked in security condition

```python
# Before (secure)
def delete_user(user_id):
    is_admin = current_user.role == 'admin'
    if not is_admin:
        abort(403)
    User.objects.get(id=user_id).delete()

# After (INSECURE - renamed variable breaks check!)
def delete_user(user_id):
    user_role = current_user.role  # ← Renamed
    if not is_admin:  # ← Still references old name, always False!
        abort(403)
    User.objects.get(id=user_id).delete()

# Now ANYONE can delete users (is_admin undefined, evaluates to False, condition fails)
```

**Detection**: Static analysis for undefined variables

---

## Summary

**Security Regression Check (Verification Mode)**:
- No new vulnerabilities introduced
- Security controls preserved (auth, authz, validation)
- Attack surface not increased
- Data flow security maintained
- Error handling security unchanged

**Automated Detection**:
- Diff-based security analysis
- Control extraction comparison
- Attack surface calculation
- Vulnerability scanning (before/after)

**Integration**:
- Invoked by refactoring-engineer Phase 5
- Returns APPROVE or REQUEST_CHANGES
- Provides detailed regression report if failures found

**Common Refactoring Risks**:
- Lost decorators (Extract Method)
- Bypassed validation (Move Method)
- Broken security checks (Rename Variable)

**Priority**: **Critical** - Security regressions must be caught before code is committed.

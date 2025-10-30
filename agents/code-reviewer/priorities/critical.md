# Critical Issues (Must Fix)

**Priority Level**: 🔴 CRITICAL
**Action Required**: Fix before code approval
**Gate**: Cannot approve pull request with unresolved critical issues

Critical issues pose immediate risk to security, data integrity, or system reliability. These must be fixed—no exceptions.

---

## What Makes an Issue Critical?

**Security Vulnerabilities**:
- Direct path to data breach, unauthorized access, or system compromise
- Examples: SQL injection, XSS, authentication bypass, exposed secrets

**Data Corruption Risks**:
- Can corrupt, delete, or inconsistently modify data
- Examples: Race conditions on shared state, missing transactions, data validation failures

**Production-Breaking Bugs**:
- Will cause system failure, crash, or severe degradation in production
- Examples: Unhandled exceptions in critical paths, deadlocks, infinite loops, memory leaks

**Blocking Issues**:
- Prevents deployment or breaks existing functionality
- Examples: Breaking API changes without deprecation, missing migrations, dependency conflicts

---

## Security Vulnerabilities (CRITICAL)

### SQL Injection

**Why Critical**: Single exploit can dump entire database or delete all data

**Example**:
```python
# ❌ CRITICAL: SQL injection vulnerability
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

**Fix Required**:
```python
# ✅ Fixed: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
db.execute(query, (user_id,))
```

**Cannot approve until**: All SQL queries use parameterized queries or ORM

---

### Cross-Site Scripting (XSS)

**Why Critical**: Attackers can steal sessions, redirect users, keylog inputs

**Example**:
```python
# ❌ CRITICAL: XSS vulnerability
return f"<div>Welcome, {username}!</div>"
```

**Fix Required**:
```python
# ✅ Fixed: Escaped output
from html import escape
return f"<div>Welcome, {escape(username)}!</div>"
```

**Cannot approve until**: All user input is escaped in HTML output

---

### Hard-Coded Secrets

**Why Critical**: Exposed credentials in git history, GitHub scanners alert attackers

**Example**:
```python
# ❌ CRITICAL: Hard-coded API key
API_KEY = "sk_live_abc123def456"
```

**Fix Required**:
```python
# ✅ Fixed: Environment variable
import os
API_KEY = os.environ['API_KEY']
```

**Cannot approve until**: All secrets moved to environment variables or secret manager

---

### Authentication Bypass

**Why Critical**: Unauthorized access to user accounts, admin panels, sensitive data

**Example**:
```python
# ❌ CRITICAL: Client-side authentication
if request.headers.get('X-Is-Admin') == 'true':
    return admin_panel()
```

**Fix Required**:
```python
# ✅ Fixed: Server-side authentication
@require_auth
def admin_panel():
    user = get_current_user()
    if not user.is_admin:
        abort(403)
    return render_template('admin.html')
```

**Cannot approve until**: All authentication checks are server-side

---

### Insecure Cryptography

**Why Critical**: Weak hashing can be cracked in seconds, exposing passwords

**Example**:
```python
# ❌ CRITICAL: Weak password hashing
password_hash = hashlib.md5(password.encode()).hexdigest()
```

**Fix Required**:
```python
# ✅ Fixed: Strong hashing with bcrypt
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**Cannot approve until**: Using bcrypt, Argon2, or PBKDF2 for password hashing

---

## Data Corruption Risks (CRITICAL)

### Race Conditions on Shared State

**Why Critical**: Data corruption, inconsistent state, lost updates

**Example**:
```python
# ❌ CRITICAL: Race condition
balance = account.balance
balance -= amount
account.balance = balance  # Lost update if concurrent access
db.commit()
```

**Fix Required**:
```python
# ✅ Fixed: Atomic update
db.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, account_id))

# Or: Optimistic locking
account = Account.query.with_for_update().get(account_id)
account.balance -= amount
db.commit()
```

**Cannot approve until**: Shared state updates are atomic or properly locked

---

### Missing Transaction Boundaries

**Why Critical**: Partial updates leave database in inconsistent state

**Example**:
```python
# ❌ CRITICAL: No transaction
user.create()  # Succeeds
account.create()  # Fails - user created but no account!
```

**Fix Required**:
```python
# ✅ Fixed: Transaction wrapping
with db.begin():
    user.create()
    account.create()
    # Both or neither
```

**Cannot approve until**: Related operations wrapped in transactions

---

### Data Validation Failures

**Why Critical**: Invalid data corrupts database, breaks application logic

**Example**:
```python
# ❌ CRITICAL: No validation
age = request.form['age']
user.age = age  # Could be -100, "abc", etc.
```

**Fix Required**:
```python
# ✅ Fixed: Validation
age = request.form.get('age')
if not age or not age.isdigit():
    abort(400, "Invalid age")
age = int(age)
if not 0 <= age <= 120:
    abort(400, "Age must be 0-120")
user.age = age
```

**Cannot approve until**: All user input is validated before database writes

---

## Production-Breaking Bugs (CRITICAL)

### Unhandled Exceptions in Critical Paths

**Why Critical**: Application crashes, service unavailable

**Example**:
```python
# ❌ CRITICAL: Unhandled exception
@app.route('/checkout')
def checkout():
    user = User.query.get(session['user_id'])  # KeyError if not logged in
    amount = calculate_total(cart)
    charge_customer(user.payment_method, amount)  # AttributeError if no payment method
```

**Fix Required**:
```python
# ✅ Fixed: Error handling
@app.route('/checkout')
def checkout():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/login')

        user = User.query.get(user_id)
        if not user or not user.payment_method:
            abort(400, "Payment method required")

        amount = calculate_total(cart)
        charge_customer(user.payment_method, amount)
    except PaymentError as e:
        logger.error(f"Payment failed: {e}")
        return {'error': 'Payment failed'}, 400
```

**Cannot approve until**: Critical paths have comprehensive error handling

---

### Memory Leaks in Long-Running Processes

**Why Critical**: Gradual memory exhaustion, service crashes

**Example**:
```python
# ❌ CRITICAL: Memory leak
global_cache = []

@app.route('/process')
def process_data():
    data = fetch_large_dataset()
    global_cache.append(data)  # Never cleared!
    return process(data)
```

**Fix Required**:
```python
# ✅ Fixed: Bounded cache with expiration
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=3600)  # Max 100 items, 1-hour TTL

@app.route('/process')
def process_data():
    cache_key = request.args.get('id')
    if cache_key in cache:
        data = cache[cache_key]
    else:
        data = fetch_large_dataset()
        cache[cache_key] = data
    return process(data)
```

**Cannot approve until**: Memory usage is bounded or resources are released

---

### Deadlocks

**Why Critical**: Application hangs, requests timeout, service degradation

**Example**:
```python
# ❌ CRITICAL: Deadlock risk
# Thread 1
with lock_a:
    with lock_b:
        ...

# Thread 2
with lock_b:  # Deadlock if Thread 1 holds lock_a
    with lock_a:
        ...
```

**Fix Required**:
```python
# ✅ Fixed: Consistent lock ordering
# All threads acquire locks in same order
with lock_a:
    with lock_b:
        ...
```

**Cannot approve until**: Lock ordering is consistent or timeouts are implemented

---

## Blocking Issues (CRITICAL)

### Breaking API Changes Without Deprecation

**Why Critical**: Breaks existing clients, production failures

**Example**:
```python
# ❌ CRITICAL: Breaking change
# Old API (v1)
@app.route('/api/users/<int:id>')
def get_user(id):
    return User.query.get(id).to_dict()

# New API (breaking change - renamed field)
@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    return {'userId': user.id, 'userName': user.name}  # Was 'id' and 'name'
```

**Fix Required**:
```python
# ✅ Fixed: Deprecation period
@app.route('/api/v2/users/<int:id>')
def get_user_v2(id):
    user = User.query.get(id)
    return {'userId': user.id, 'userName': user.name}

# v1 still supported with deprecation notice
@app.route('/api/v1/users/<int:id>')
def get_user_v1(id):
    user = User.query.get(id)
    response = {'id': user.id, 'name': user.name}
    response.headers['X-API-Deprecated'] = 'Use /api/v2/users/<id>'
    return response
```

**Cannot approve until**: Breaking changes versioned or deprecated first

---

### Missing Required Database Migrations

**Why Critical**: Deployment fails, application crashes due to schema mismatch

**Example**:
```python
# ❌ CRITICAL: Code expects new column, migration not included
user.email_verified  # New column not in database
```

**Fix Required**:
```python
# ✅ Fixed: Include migration
# migrations/add_email_verified.py
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), default=False))

# Verify migration runs before deployment
```

**Cannot approve until**: All schema changes have corresponding migrations

---

## Critical Issue Response Pattern

**When critical issue found**:

1. **Mark as CRITICAL** with 🔴 indicator
2. **Explain severity**: Why this blocks approval (security, data corruption, production failure)
3. **Provide fix**: Exact code to resolve issue
4. **Include verification**: How to test the fix
5. **Block approval**: "Cannot approve until [specific criteria met]"

**Example**:
```markdown
### 🔴 CRITICAL: SQL Injection Vulnerability (users.py:45)

**Severity**: CRITICAL - Direct path to database compromise

**Issue**:
```python
# Current code:
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

**Attack Example**:
Input: `user_id = "1 OR 1=1"`
Result: Returns ALL users (authentication bypass)

Input: `user_id = "1; DROP TABLE users--"`
Result: Deletes entire users table

**Fix**:
```python
query = "SELECT * FROM users WHERE id = %s"
db.execute(query, (user_id,))
```

**Verification**:
```bash
# Test with malicious input
curl -X POST http://localhost:5000/users -d "user_id=1 OR 1=1"
# Should return error, not all users
```

**Cannot approve until**: All SQL queries use parameterized queries (no string interpolation).
```

---

## Gate Enforcement

**Critical issues BLOCK code approval**:

- [ ] **Security vulnerabilities** fixed (SQL injection, XSS, hard-coded secrets, etc.)
- [ ] **Data corruption risks** addressed (race conditions, missing transactions, validation)
- [ ] **Production-breaking bugs** resolved (unhandled exceptions, memory leaks, deadlocks)
- [ ] **Blocking issues** fixed (breaking changes versioned, migrations included)

**If ANY critical issue unchecked, pull request CANNOT be approved.**

**This is not optional. This is a gate.**

---

## Summary

**Critical issues prioritized**:
- Security vulnerabilities → SQL injection, XSS, hard-coded secrets, authentication bypass
- Data corruption → Race conditions, missing transactions, validation failures
- Production-breaking → Unhandled exceptions, memory leaks, deadlocks
- Blocking issues → Breaking changes, missing migrations

**All critical issues must be fixed before code approval.**

**No exceptions.**

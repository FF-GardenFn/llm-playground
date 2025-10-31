---
title: Security Detection Heuristics
description: Patterns and red flags for detecting common vulnerabilities
category: Security Analysis
priority: Critical
---

# Security Detection Heuristics

Pattern-based detection rules for identifying common security vulnerabilities during code review.

---

## SQL Injection Detection

### Red Flags

**String Concatenation in Queries**:
```python
# UNSAFE: f-string with table name
query = f"SELECT * FROM {table}"

# UNSAFE: String concatenation
query = "SELECT * FROM users WHERE id = " + user_id

# UNSAFE: String formatting
query = "SELECT * FROM users WHERE name = '%s'" % name

# UNSAFE: f-string in execute
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# UNSAFE: Format method
query = "DELETE FROM {}".format(table_name)
```

**Pattern Matching**:
- Look for: `f"... {variable} ..."` in SQL context
- Look for: `"..." + variable + "..."` in SQL context
- Look for: `.execute(f"...")` or `.execute("...".format(...))`
- Look for: String concatenation with `WHERE`, `FROM`, `INSERT`, `UPDATE`, `DELETE`

### Safe Patterns

**Parameterized Queries**:
```python
# SAFE: Parameterized query (Python DB-API)
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# SAFE: Named parameters
query = "SELECT * FROM users WHERE id = :user_id"
cursor.execute(query, {'user_id': user_id})

# SAFE: SQLAlchemy (ORM)
user = session.query(User).filter(User.id == user_id).first()

# SAFE: Django ORM
user = User.objects.get(id=user_id)
```

**Detection Heuristic**:
1. Search for SQL keywords: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `FROM`, `WHERE`
2. Check if followed by string concatenation or f-strings
3. Flag if user input could reach query
4. Whitelist: ORM usage (Django, SQLAlchemy), parameterized queries

---

## XSS (Cross-Site Scripting) Detection

### Red Flags

**Unescaped HTML Output**:
```python
# UNSAFE: Direct insertion of user input
html = f"<div>{user_input}</div>"

# UNSAFE: render_template_string with user data
return render_template_string(user_template)

# UNSAFE: innerHTML with user data (JavaScript)
element.innerHTML = userInput;

# UNSAFE: document.write with user data
document.write(userData);

# UNSAFE: Direct HTML construction
response = "<h1>" + title + "</h1>"
```

**Pattern Matching**:
- Look for: `f"<{tag}>{user_input}</{tag}>"`
- Look for: `render_template_string()` with variables
- Look for: `innerHTML =`, `outerHTML =`, `document.write()`
- Look for: HTML construction with string concatenation

### Safe Patterns

**Properly Escaped Output**:
```python
# SAFE: Auto-escaping template engine
return render_template('page.html', title=user_title)

# SAFE: Explicit escaping
from markupsafe import escape
html = f"<div>{escape(user_input)}</div>"

# SAFE: textContent (JavaScript)
element.textContent = userInput;

# SAFE: Template literal with sanitization
element.innerHTML = DOMPurify.sanitize(userInput);
```

**Detection Heuristic**:
1. Search for HTML construction patterns
2. Check if user input is used without escaping
3. Flag `render_template_string()` with variables
4. Whitelist: Template engines with auto-escaping (Jinja2, Django templates)
5. Flag JavaScript: `innerHTML`, `outerHTML`, `document.write()` with user data

---

## Command Injection Detection

### Red Flags

**Shell Execution with User Input**:
```python
# UNSAFE: os.system with user input
os.system(f"rm {filename}")

# UNSAFE: subprocess with shell=True
subprocess.call(f"convert {user_file} output.pdf", shell=True)

# UNSAFE: eval with user input
eval(user_code)

# UNSAFE: exec with user input
exec(user_script)

# UNSAFE: os.popen
os.popen(f"cat {filename}")
```

**Pattern Matching**:
- Look for: `os.system()` with variables
- Look for: `subprocess.call(..., shell=True)` or `subprocess.run(..., shell=True)`
- Look for: `eval()`, `exec()` with user input
- Look for: `os.popen()`, `commands.getoutput()`

### Safe Patterns

**Parameterized Commands**:
```python
# SAFE: subprocess with list (no shell)
subprocess.run(["rm", filename])

# SAFE: subprocess with array arguments
subprocess.run(["convert", user_file, "output.pdf"])

# SAFE: ast.literal_eval for safe evaluation
import ast
data = ast.literal_eval(user_input)  # Only Python literals

# SAFE: Input validation and allowlisting
allowed_commands = ['start', 'stop', 'status']
if command in allowed_commands:
    subprocess.run([command, service_name])
```

**Detection Heuristic**:
1. Search for command execution functions
2. Check if user input is in command string
3. Flag `shell=True` with variables
4. Flag `eval()` and `exec()` with external input
5. Whitelist: List-based subprocess calls, `ast.literal_eval()`

---

## Path Traversal Detection

### Red Flags

**Unvalidated File Paths**:
```python
# UNSAFE: Direct path concatenation
file_path = f"/uploads/{user_filename}"
with open(file_path, 'r') as f:
    content = f.read()

# UNSAFE: os.path.join with user input
file_path = os.path.join(base_dir, user_path)

# UNSAFE: Direct file access
open(request.args.get('file'), 'r')
```

**Attack Examples**:
```python
# Attacker input: "../../etc/passwd"
file_path = f"/uploads/{user_filename}"  # Results in /uploads/../../etc/passwd
```

### Safe Patterns

**Path Validation**:
```python
# SAFE: Validate path stays in allowed directory
import os
base_dir = '/uploads/'
file_path = os.path.join(base_dir, user_filename)
if not os.path.abspath(file_path).startswith(os.path.abspath(base_dir)):
    raise ValueError("Invalid file path")

# SAFE: Allowlist filenames
import re
if not re.match(r'^[a-zA-Z0-9_-]+\.[a-z]+$', user_filename):
    raise ValueError("Invalid filename")

# SAFE: Use secure_filename
from werkzeug.utils import secure_filename
safe_name = secure_filename(user_filename)
file_path = os.path.join(base_dir, safe_name)
```

**Detection Heuristic**:
1. Search for file operations: `open()`, `os.path.join()`, `Path()`
2. Check if user input is in file path
3. Flag if no validation against `..` or absolute paths
4. Whitelist: `secure_filename()`, explicit path validation

---

## Insecure Deserialization Detection

### Red Flags

**Unsafe Deserialization**:
```python
# UNSAFE: pickle with untrusted data
import pickle
data = pickle.loads(user_input)

# UNSAFE: PyYAML unsafe load
import yaml
config = yaml.load(user_config)  # Deprecated, unsafe

# UNSAFE: marshal with user data
import marshal
obj = marshal.loads(user_data)
```

### Safe Patterns

**Safe Deserialization**:
```python
# SAFE: JSON (no code execution)
import json
data = json.loads(user_input)

# SAFE: PyYAML safe_load
import yaml
config = yaml.safe_load(user_config)

# SAFE: Validate schema after parsing
import json
from jsonschema import validate
data = json.loads(user_input)
validate(data, schema)
```

**Detection Heuristic**:
1. Search for: `pickle.loads()`, `yaml.load()`, `marshal.loads()`
2. Flag if called with external input
3. Whitelist: `json.loads()`, `yaml.safe_load()`, schema validation

---

## Hardcoded Secrets Detection

### Red Flags

**Hardcoded Credentials**:
```python
# UNSAFE: Hardcoded password
PASSWORD = "super_secret_123"

# UNSAFE: API key in code
API_KEY = "sk_live_abc123xyz789"

# UNSAFE: Database credentials
DB_CONNECTION = "postgresql://admin:password123@localhost/db"

# UNSAFE: JWT secret
JWT_SECRET = "my-secret-key"

# UNSAFE: AWS credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
```

**Pattern Matching**:
- Look for: Variable names containing `password`, `secret`, `key`, `token`, `credential`
- Look for: String assignments to these variables
- Look for: Patterns like `sk_`, `API_KEY`, long alphanumeric strings

### Safe Patterns

**Environment Variables**:
```python
# SAFE: Load from environment
import os
PASSWORD = os.environ.get('DB_PASSWORD')
API_KEY = os.getenv('API_KEY')

# SAFE: Configuration file (excluded from version control)
from config import load_config
config = load_config()
secret = config.get('jwt_secret')

# SAFE: Secret management service
from aws_secretsmanager import get_secret
db_password = get_secret('prod/db/password')
```

**Detection Heuristic**:
1. Search for variable names: `password`, `secret`, `key`, `token`, `api_key`
2. Check if assigned a string literal
3. Flag patterns: `sk_`, long alphanumeric strings, URLs with embedded credentials
4. Whitelist: `os.environ`, `os.getenv()`, secret manager calls

---

## Weak Cryptography Detection

### Red Flags

**Weak Algorithms**:
```python
# UNSAFE: MD5 for passwords
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# UNSAFE: SHA1 for passwords
password_hash = hashlib.sha1(password.encode()).hexdigest()

# UNSAFE: Plain text password storage
user.password = request.form['password']

# UNSAFE: Weak random number generation
import random
token = random.randint(1000, 9999)
```

### Safe Patterns

**Strong Cryptography**:
```python
# SAFE: bcrypt for passwords
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# SAFE: Django password hashing
from django.contrib.auth.hashers import make_password
user.password = make_password(password)

# SAFE: Cryptographically secure random
import secrets
token = secrets.token_urlsafe(32)
```

**Detection Heuristic**:
1. Search for: `hashlib.md5()`, `hashlib.sha1()` in password context
2. Flag: Plain text password assignment
3. Flag: `random.randint()` for security tokens
4. Whitelist: `bcrypt`, `argon2`, `secrets.token_*()`, framework password hashers

---

## Detection Priority Matrix

| Vulnerability Type | Detection Difficulty | Exploitability | Priority |
|-------------------|---------------------|----------------|----------|
| SQL Injection | Easy (pattern matching) | High | Critical |
| XSS | Medium (context-dependent) | High | Critical |
| Command Injection | Easy (function calls) | High | Critical |
| Path Traversal | Easy (file operations) | Medium | Critical |
| Hardcoded Secrets | Easy (string patterns) | Medium | Critical |
| Weak Crypto | Easy (algorithm names) | Low | Important |
| Insecure Deserialization | Easy (function calls) | High | Critical |

---

## Automated Detection Tools

**Recommended Tools**:
- **Bandit** (Python): `bandit -r src/`
- **Semgrep**: Cross-language static analysis
- **ESLint security plugins** (JavaScript)
- **Brakeman** (Ruby on Rails)
- **FindSecBugs** (Java)

**Integration**:
```bash
# Run Bandit for Python security
bandit -r src/ -f json -o security-report.json

# Run Semgrep with security rules
semgrep --config=auto src/

# Check for secrets in git history
git secrets --scan
truffleHog --regex --entropy=True .
```

---

## References

- OWASP Top 10: https://owasp.org/Top10/
- CWE Top 25: https://cwe.mitre.org/top25/
- Security checklist: `security/owasp-checklist.md`
- Input validation: `security/input-validation.md`

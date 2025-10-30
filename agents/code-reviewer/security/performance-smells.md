# Performance & Security Smells

**Purpose**: Identify performance issues and security-related performance problems that require manual fixes (NOT refactorable).

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Important (performance) to Critical (DoS vulnerabilities)

**Refactorable**: ❌ NO - These smells require optimization knowledge, not behavior-preserving refactoring

---

## Overview

Performance smells and security-related performance issues cannot be fixed by refactoring-engineer because they require:
- Database/ORM knowledge (N+1 queries)
- Async/concurrency redesign (blocking I/O)
- Algorithmic knowledge (inefficient algorithms)
- Memory management (leaks, excessive allocation)

These issues require **manual optimization**, not behavior-preserving code structure transformation.

---

## Performance Smells

### 1. N+1 Query Problem

**Description**: Executing N additional queries in a loop when 1 query would suffice.

**Detection**:
- Database query inside loop
- ORM relationship access in iteration
- Repeated API calls in loop

**Example - Problem**:
```python
# ❌ BAD: N+1 query problem (1 + N queries)
def get_users_with_orders():
    users = User.objects.all()  # 1 query
    result = []
    for user in users:
        orders = user.orders.all()  # N queries (one per user)!
        result.append({
            'user': user,
            'order_count': len(orders)
        })
    return result

# If 1000 users: 1 + 1000 = 1001 database queries!
```

**Fix - Eager Loading**:
```python
# ✅ GOOD: Eager loading (2 queries total)
def get_users_with_orders():
    users = User.objects.prefetch_related('orders')  # 2 queries (users + all orders)
    result = []
    for user in users:
        orders = user.orders.all()  # No query (already loaded)
        result.append({
            'user': user,
            'order_count': len(orders)
        })
    return result

# Always 2 queries regardless of user count
```

**Fix - Aggregation**:
```python
# ✅ BETTER: Single query with aggregation
from django.db.models import Count

def get_users_with_orders():
    users = User.objects.annotate(order_count=Count('orders'))  # 1 query
    return [{'user': user, 'order_count': user.order_count} for user in users]
```

**Detection Heuristics**:
- `.objects.get()` or `.objects.filter()` inside `for` loop
- Relationship access (`user.orders`) without `prefetch_related()`
- `len(related_objects)` without `annotate(Count())`

**Why Not Refactorable**:
- Requires understanding database queries and ORM behavior
- Not a code structure issue - requires changing query strategy
- Behavior technically preserved (same result, different performance)

**Severity**: **Important** (causes severe performance degradation)

---

### 2. Missing Database Indexes

**Description**: Queries on unindexed columns cause full table scans.

**Detection**:
- Frequent queries on unindexed columns
- Slow query logs showing sequential scans
- WHERE clause on columns without indexes

**Example - Problem**:
```python
# ❌ BAD: Query on unindexed email column
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=255)  # No index!

def find_user_by_email(email):
    return User.objects.get(email=email)  # Full table scan!
```

**Fix - Add Index**:
```python
# ✅ GOOD: Add index to email column
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=255, db_index=True)  # Indexed

def find_user_by_email(email):
    return User.objects.get(email=email)  # Index scan (fast)
```

**Detection Heuristics**:
- Model fields used in queries without `db_index=True`
- Slow query logs (if available)
- Queries with `LIKE '%pattern%'` (can't use index)

**Why Not Refactorable**:
- Requires database schema change
- Not code structure - requires migration

**Severity**: **Important** (causes slow queries)

---

### 3. Blocking I/O in Async Context

**Description**: Synchronous I/O operations blocking async event loop.

**Detection**:
- `requests.get()` in async function
- File I/O without `async`
- Database queries without async driver

**Example - Problem**:
```python
# ❌ BAD: Blocking I/O in async function
import asyncio
import requests

async def fetch_data():
    response = requests.get('https://api.example.com/data')  # Blocks event loop!
    return response.json()

# Event loop blocked while waiting for HTTP response
```

**Fix - Async I/O**:
```python
# ✅ GOOD: Async I/O
import asyncio
import aiohttp

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()  # Non-blocking
```

**Detection Heuristics**:
- `requests`, `urllib` in `async def`
- `open()`, file operations in `async def`
- `time.sleep()` instead of `await asyncio.sleep()`

**Why Not Refactorable**:
- Requires async/await redesign
- Changes execution model (not behavior-preserving)

**Severity**: **Important** (negates async benefits)

---

### 4. Memory Leak

**Description**: Unreleased memory due to circular references, global caches, or resource leaks.

**Detection**:
- Growing memory usage over time
- Circular references without weak references
- File handles not closed
- Database connections not released

**Example - Problem**:
```python
# ❌ BAD: Memory leak (circular reference)
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self  # Circular reference!
        self.children.append(child)

# Parent references child, child references parent → never garbage collected
```

**Fix - Weak References**:
```python
# ✅ GOOD: Use weak references to break cycle
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None  # Will be weak reference
        self.children = []

    def add_child(self, child):
        child.parent = weakref.ref(self)  # Weak reference
        self.children.append(child)
```

**Example - Resource Leak**:
```python
# ❌ BAD: File handle not closed
def read_config():
    f = open('config.txt')
    data = f.read()
    return data  # File handle leaked!

# ✅ GOOD: Use context manager
def read_config():
    with open('config.txt') as f:
        return f.read()  # File closed automatically
```

**Detection Heuristics**:
- `open()` without `with` statement
- Database connections without `close()`
- Circular references in class relationships
- Growing global caches without eviction

**Why Not Refactorable**:
- Requires memory management knowledge
- Not code structure - requires resource lifecycle changes

**Severity**: **Important** (causes out-of-memory crashes)

---

### 5. Inefficient Algorithm

**Description**: Using O(n²) or worse when better algorithm exists.

**Detection**:
- Nested loops over same dataset
- Linear search instead of binary search
- Bubble sort instead of quicksort/mergesort

**Example - Problem**:
```python
# ❌ BAD: O(n²) algorithm (nested loops)
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# For 1000 items: 1,000,000 comparisons
```

**Fix - Better Algorithm**:
```python
# ✅ GOOD: O(n) algorithm using set
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)

# For 1000 items: 1,000 comparisons
```

**Detection Heuristics**:
- Nested loops over same collection
- `list.index()` in loop (O(n²))
- No early exit in search
- Sorting before single lookup (O(n log n) when O(n) possible)

**Why Not Refactorable**:
- Requires algorithmic knowledge
- Changes algorithm (not structure)
- May require different data structures

**Severity**: **Important** (causes scalability issues)

---

### 6. Excessive Database Queries

**Description**: Multiple separate queries when single query would work.

**Detection**:
- Multiple `.objects.get()` calls that could be combined
- Sequential queries that could be joined
- Queries in loop (see N+1)

**Example - Problem**:
```python
# ❌ BAD: 3 separate queries
def get_user_summary(user_id):
    user = User.objects.get(id=user_id)  # Query 1
    orders = Order.objects.filter(user=user)  # Query 2
    payments = Payment.objects.filter(user=user)  # Query 3
    return {
        'user': user,
        'orders': orders,
        'payments': payments
    }
```

**Fix - Single Query**:
```python
# ✅ GOOD: Single query with prefetch
def get_user_summary(user_id):
    user = User.objects.prefetch_related('orders', 'payments').get(id=user_id)  # 1 query
    return {
        'user': user,
        'orders': user.orders.all(),
        'payments': user.payments.all()
    }
```

**Why Not Refactorable**: Requires database/ORM knowledge

**Severity**: **Important**

---

## Security-Related Performance Smells

### 7. Denial of Service (DoS) Vulnerabilities

**Description**: Code vulnerable to resource exhaustion attacks.

**Detection**:
- No rate limiting
- Unbounded loops with user input
- No timeout on external requests
- Large file uploads without size limit

**Example - Problem**:
```python
# ❌ CRITICAL: No rate limiting on API
@app.route('/api/search')
def search():
    query = request.args.get('q')
    results = expensive_search(query)  # Attacker can spam this
    return jsonify(results)
```

**Fix - Rate Limiting**:
```python
# ✅ GOOD: Rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/search')
@limiter.limit("10 per minute")  # Max 10 requests/minute per IP
def search():
    query = request.args.get('q')
    results = expensive_search(query)
    return jsonify(results)
```

**Example - Unbounded Loop**:
```python
# ❌ CRITICAL: Unbounded loop with user input
@app.route('/generate')
def generate():
    count = int(request.args.get('count', 10))
    items = [expensive_operation() for _ in range(count)]  # Attacker can set count=999999999
    return jsonify(items)

# ✅ GOOD: Bounded loop
@app.route('/generate')
def generate():
    count = int(request.args.get('count', 10))
    if count > 100:  # Enforce maximum
        abort(400, "Maximum count is 100")
    items = [expensive_operation() for _ in range(count)]
    return jsonify(items)
```

**Detection Heuristics**:
- No `@limiter.limit()` on public endpoints
- `range(user_input)` without bounds check
- No timeout on `requests.get()`
- File upload without `MAX_CONTENT_LENGTH`

**Why Not Refactorable**: Requires security design, not refactoring

**Severity**: **Critical** (enables DoS attacks)

---

### 8. Regular Expression DoS (ReDoS)

**Description**: Catastrophic backtracking in regex can cause CPU exhaustion.

**Detection**:
- Nested quantifiers (`(a+)+`, `(a*)*`)
- Alternation with overlap (`(a|a)*`)
- User input used in regex without validation

**Example - Problem**:
```python
# ❌ CRITICAL: ReDoS vulnerability
import re

def validate_input(user_input):
    # Catastrophic backtracking on input like "aaaaaaaaaaaaaaaaaaaaX"
    if re.match(r'^(a+)+$', user_input):
        return True
    return False
```

**Fix - Safe Regex**:
```python
# ✅ GOOD: Non-backtracking regex
import re

def validate_input(user_input):
    # Possessive quantifier (no backtracking)
    if re.match(r'^a+$', user_input):  # No nested quantifier
        return True
    return False
```

**Detection Heuristics**:
- Nested quantifiers in regex patterns
- User input in `re.compile()` without sanitization
- Complex alternations

**Why Not Refactorable**: Requires regex redesign

**Severity**: **Critical** (enables CPU exhaustion)

---

### 9. Insecure Randomness for Security

**Description**: Using weak random for security-critical operations.

**Detection**:
- `random.random()` for tokens/passwords
- Predictable session IDs
- Weak CAPTCHA generation

**Example - Problem**:
```python
# ❌ CRITICAL: Weak random for security
import random

def generate_session_token():
    return str(random.randint(100000, 999999))  # Predictable!
```

**Fix - Cryptographically Secure Random**:
```python
# ✅ GOOD: Cryptographically secure random
import secrets

def generate_session_token():
    return secrets.token_urlsafe(32)  # Unpredictable
```

**Detection Heuristics**:
- `import random` used for tokens/passwords/session IDs
- `random.randint()` for security purposes
- `random.choice()` for password generation

**Why Not Refactorable**: Requires security knowledge

**Severity**: **Critical** (enables session hijacking, token prediction)

---

## Detection Checklist

### Phase 1: Automated Analysis

**Performance Smells**:
- [ ] N+1 queries (queries in loops)
- [ ] Missing database indexes (frequent queries on unindexed columns)
- [ ] Blocking I/O in async (requests in async def)
- [ ] Memory leaks (open() without with, circular refs)
- [ ] Inefficient algorithms (nested loops, linear search)
- [ ] Excessive queries (multiple queries that could be combined)

**Security-Related Performance**:
- [ ] DoS vulnerabilities (no rate limiting, unbounded loops)
- [ ] ReDoS vulnerabilities (nested quantifiers in regex)
- [ ] Weak randomness (random.random() for security)

### Phase 2: Manual Review

**Performance Architecture**:
- [ ] Are caching strategies appropriate?
- [ ] Are connection pools configured?
- [ ] Are timeouts set on external calls?
- [ ] Are batch operations used where appropriate?

**Security Design**:
- [ ] Are rate limits sufficient?
- [ ] Are resource limits enforced?
- [ ] Are expensive operations protected?

---

## Priority Classification

### Critical (Fix Immediately)
- DoS vulnerabilities (no rate limiting on public endpoints)
- ReDoS vulnerabilities (enables CPU exhaustion)
- Weak randomness for security (session tokens, passwords)

### Important (Fix Before Production)
- N+1 query problem (severe performance impact)
- Memory leaks (causes crashes)
- Blocking I/O in async (negates async benefits)
- Inefficient algorithms (O(n²) or worse)

### Suggestions (Optimize When Possible)
- Missing database indexes (improves query performance)
- Excessive database queries (reduces database load)
- Missing caching (reduces repeated computation)

---

## Recommendations Format

### Example - N+1 Query

```markdown
## Important: N+1 Query Problem (Line 67)

**Category**: Performance Smell
**Severity**: Important
**Refactorable**: ❌ NO (requires database optimization)

**Impact**: 1000 users = 1001 database queries (severe performance degradation)

**Current Code**:
```python
users = User.objects.all()
for user in users:
    orders = user.orders.all()  # N queries!
```

**Fix** (Eager Loading):
```python
users = User.objects.prefetch_related('orders')
for user in users:
    orders = user.orders.all()  # No query
```

**Fix** (Aggregation):
```python
users = User.objects.annotate(order_count=Count('orders'))
```

**Verification**: Profile database queries before/after fix
**Resources**: See performance/database-performance.md for patterns
```

### Example - DoS Vulnerability

```markdown
## Critical: Denial of Service Vulnerability (Line 23)

**Category**: Security + Performance
**Severity**: CRITICAL
**Refactorable**: ❌ NO (requires security design)

**Impact**: Attacker can exhaust server resources by spamming endpoint

**Current Code**:
```python
@app.route('/api/search')
def search():
    query = request.args.get('q')
    results = expensive_search(query)  # No rate limiting!
```

**Fix**:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/search')
@limiter.limit("10 per minute")
def search():
    query = request.args.get('q')
    results = expensive_search(query)
```

**Verification**: Test rate limiting with concurrent requests
**Resources**: See security/owasp-checklist.md (A04: Insecure Design)
```

---

## Summary

**Performance Smells (6 smells)**:
1. N+1 Query Problem - Queries in loops
2. Missing Database Indexes - Unindexed columns
3. Blocking I/O - Sync operations in async context
4. Memory Leak - Unreleased resources
5. Inefficient Algorithm - O(n²) when better exists
6. Excessive Queries - Multiple queries instead of one

**Security Performance Smells (3 smells)**:
7. DoS Vulnerabilities - No rate limiting, unbounded operations
8. ReDoS - Catastrophic backtracking in regex
9. Weak Randomness - random.random() for security

**Why Not Refactorable**:
- Require domain knowledge (database, async, algorithms, security)
- Not code structure issues - require optimization or redesign
- Change execution strategy (not behavior-preserving)

**Integration**:
- Phase 1: Automated detection via static analysis
- Phase 2: Manual review for architectural issues
- Phase 4: Classify by severity (Critical → Important → Suggestions)
- Phase 5: Provide detailed fix instructions with examples

**Code-Reviewer distinguishes**: Refactorable smells (code structure) vs Performance smells (optimization required).

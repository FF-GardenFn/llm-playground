# Memory Management

**Purpose**: Detect memory leaks, excessive allocation, and inefficient memory usage during code review.

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Important (causes out-of-memory crashes)

**Refactorable**: ❌ NO (requires memory management knowledge, not code structure changes)

---

## Overview

Memory management issues cannot be fixed by refactoring-engineer because they require:
- Understanding memory lifecycle
- Resource cleanup patterns
- Circular reference detection
- Memory profiling knowledge

These require **manual fixes**, not behavior-preserving refactoring.

---

## Common Memory Smells

### 1. Memory Leak (Circular References)

**Problem**: Circular references prevent garbage collection.

**Detection**:
- Parent-child relationships with strong references both ways
- Circular data structures without weak references
- Growing memory usage over time

**Example - Leak**:
```python
# ❌ BAD: Circular reference (memory leak)
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None  # Strong reference
        self.children = []

    def add_child(self, child):
        child.parent = self  # ← Circular reference!
        self.children.append(child)

# Parent → Child → Parent (never garbage collected)
root = Node(1)
child = Node(2)
root.add_child(child)
# Even after root=None, objects remain in memory
```

**Fix - Weak References**:
```python
# ✅ GOOD: Use weak reference to break cycle
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None  # Will be weak reference
        self.children = []

    def add_child(self, child):
        child.parent = weakref.ref(self)  # Weak reference
        self.children.append(child)

    def get_parent(self):
        return self.parent() if self.parent else None

# Parent → Child, but Child weakly references Parent
# Objects can be garbage collected when no strong references remain
```

**Detection Heuristics**:
- Bidirectional references (A references B, B references A)
- Parent/child relationships without weak references
- Cache or registry with strong references

**Severity**: **Important** (causes memory leaks)

---

### 2. Unclosed Resources

**Problem**: File handles, network connections, database connections not closed.

**Detection**:
- `open()` without `with` statement
- Database connections without `.close()`
- Network sockets without cleanup
- No context manager usage

**Example - Resource Leak**:
```python
# ❌ BAD: File handle not closed
def read_config(filename):
    f = open(filename)
    data = f.read()
    return data
    # File handle leaked! (not closed)

# After 1000 calls: 1000 file handles leaked
```

**Fix - Context Manager**:
```python
# ✅ GOOD: File automatically closed
def read_config(filename):
    with open(filename) as f:
        data = f.read()
    return data
    # File closed automatically

# OR manual close with try/finally
def read_config(filename):
    f = open(filename)
    try:
        data = f.read()
        return data
    finally:
        f.close()  # Always closes
```

**Database Connection Example**:
```python
# ❌ BAD: Connection not closed
def query_database(query):
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    return results
    # Connection leaked!

# ✅ GOOD: Connection closed
def query_database(query):
    with psycopg2.connect(...) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return results
    # Connection and cursor automatically closed
```

**Detection Heuristics**:
- `open()` without `with`
- `.connect()` without `.close()` or `with`
- Socket operations without cleanup
- External resource allocation without deallocation

**Severity**: **Important** (causes resource exhaustion)

---

### 3. Unbounded Caches/Collections

**Problem**: Caches or collections grow indefinitely without eviction.

**Detection**:
- Dictionary/list used as cache with no size limit
- Appending to list in long-running process
- Global caches without eviction policy

**Example - Unbounded Cache**:
```python
# ❌ BAD: Unbounded cache (grows forever)
cache = {}

def expensive_computation(key):
    if key not in cache:
        result = compute(key)
        cache[key] = result  # Never evicted!
    return cache[key]

# After 1M calls with unique keys: 1M items in memory
```

**Fix - LRU Cache with Size Limit**:
```python
# ✅ GOOD: LRU cache with size limit
from functools import lru_cache

@lru_cache(maxsize=1000)  # Max 1000 items
def expensive_computation(key):
    return compute(key)

# Oldest items automatically evicted when limit reached
```

**Alternative - Manual Cache with TTL**:
```python
# ✅ GOOD: Cache with time-to-live
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=3600)  # 1000 items, 1 hour TTL

def expensive_computation(key):
    if key not in cache:
        cache[key] = compute(key)
    return cache[key]
```

**Detection Heuristics**:
- Global `dict` or `list` continuously growing
- No `maxsize` or eviction policy
- Long-running process with accumulating data

**Severity**: **Important** (causes memory exhaustion)

---

### 4. Large Data Structures in Memory

**Problem**: Loading entire dataset into memory when streaming is possible.

**Detection**:
- Reading entire file into memory
- Loading all database rows at once
- No streaming or pagination

**Example - Load All**:
```python
# ❌ BAD: Load entire 10GB file into memory
def process_large_file(filename):
    with open(filename) as f:
        data = f.read()  # Loads entire file!
    for line in data.split('\n'):
        process(line)

# 10GB file = 10GB RAM usage
```

**Fix - Stream Processing**:
```python
# ✅ GOOD: Stream line by line
def process_large_file(filename):
    with open(filename) as f:
        for line in f:  # Streams one line at a time
            process(line)

# 10GB file = ~1KB RAM usage (single line)
```

**Database Example**:
```python
# ❌ BAD: Load 1M rows into memory
def process_all_users():
    users = User.objects.all()  # Loads all 1M users!
    for user in users:
        process(user)

# 1M users * 1KB = 1GB RAM

# ✅ GOOD: Stream with iterator
def process_all_users():
    for user in User.objects.iterator():  # Streams in batches
        process(user)

# ~100 users in memory at a time
```

**Detection Heuristics**:
- `.read()` on large files
- `.readlines()` on large files
- `.all()` on large querysets without `.iterator()`
- No pagination for large datasets

**Severity**: **Important** (causes OOM crashes)

---

### 5. String Building in Loop

**Problem**: String concatenation creates new strings (memory churn).

**Example - Memory Churn**:
```python
# ❌ BAD: Creates N intermediate strings
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item}</li>"  # Creates new string each iteration!
    return f"<ul>{html}</ul>"

# For 10,000 items: ~50MB of intermediate strings created and discarded
```

**Fix - List Join**:
```python
# ✅ GOOD: Build list, join once
def build_html(items):
    parts = [f"<li>{item}</li>" for item in items]
    return f"<ul>{''.join(parts)}</ul>"

# For 10,000 items: ~1MB total memory usage
```

**Alternative - StringIO**:
```python
# ✅ GOOD: Use buffer
from io import StringIO

def build_html(items):
    buffer = StringIO()
    buffer.write("<ul>")
    for item in items:
        buffer.write(f"<li>{item}</li>")
    buffer.write("</ul>")
    return buffer.getvalue()
```

**Detection Heuristics**:
- `string += other` in loop
- No use of `join()` or `StringIO`

**Severity**: **Suggestion** (causes memory churn, slower for large strings)

---

### 6. Mutable Default Arguments

**Problem**: Mutable defaults are shared across function calls.

**Example - Shared State**:
```python
# ❌ BAD: Mutable default argument (shared state)
def add_item(item, items=[]):  # Default list is shared!
    items.append(item)
    return items

result1 = add_item(1)  # [1]
result2 = add_item(2)  # [1, 2] ← Unexpected!
# Both calls share same list object
```

**Fix - None Default**:
```python
# ✅ GOOD: Create new list each call
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

result1 = add_item(1)  # [1]
result2 = add_item(2)  # [2] ← Correct
```

**Detection Heuristics**:
- Default arguments: `[]`, `{}`, or mutable objects
- Not using `None` as default

**Severity**: **Important** (causes bugs and unintended state sharing)

---

### 7. Global State Accumulation

**Problem**: Global variables accumulate data without cleanup.

**Example - Global Accumulation**:
```python
# ❌ BAD: Global list grows forever
ERRORS = []

def log_error(error):
    ERRORS.append(error)  # Never cleared!
    # After 1M errors: 1M items in ERRORS

# ✅ GOOD: Bounded global or use logging
from collections import deque

ERRORS = deque(maxlen=1000)  # Max 1000 errors

def log_error(error):
    ERRORS.append(error)  # Oldest evicted automatically
```

**Detection Heuristics**:
- Global `list`, `dict`, or `set` continuously growing
- No cleanup or eviction logic
- Long-running processes

**Severity**: **Important**

---

## Memory Profiling

### Detecting Memory Leaks

```python
# memory_profiler example
from memory_profiler import profile

@profile
def process_data():
    data = load_large_dataset()
    results = expensive_computation(data)
    return results

# Run with: python -m memory_profiler script.py
# Output:
# Line #    Mem usage    Increment   Line Contents
# ================================================
#      1     50.0 MiB     50.0 MiB   @profile
#      2    150.0 MiB    100.0 MiB       data = load_large_dataset()
#      3    200.0 MiB     50.0 MiB       results = expensive_computation(data)
#      4    200.0 MiB      0.0 MiB       return results
```

### Finding Circular References

```python
# gc module to find circular references
import gc

def find_circular_refs():
    gc.collect()  # Force garbage collection
    gc.set_debug(gc.DEBUG_SAVEALL)  # Save all garbage
    gc.collect()

    # Inspect circular references
    for obj in gc.garbage:
        print(f"Circular reference: {type(obj)}")
        print(f"Referrers: {gc.get_referrers(obj)}")
```

---

## Detection Checklist

### Phase 1: Automated Analysis

**Memory Leaks**:
- [ ] Are circular references present (parent-child without weak refs)?
- [ ] Are resources closed (files, connections)?
- [ ] Are context managers used?

**Unbounded Growth**:
- [ ] Are caches unbounded?
- [ ] Are collections growing indefinitely?
- [ ] Are global variables accumulating data?

**Large Allocations**:
- [ ] Are entire files loaded into memory?
- [ ] Are large datasets loaded at once?
- [ ] Is streaming possible?

**String Operations**:
- [ ] Is string concatenation in loop?
- [ ] Are intermediate strings created unnecessarily?

**Mutable Defaults**:
- [ ] Are mutable objects used as default arguments?

### Phase 2: Manual Review

**Memory Design**:
- [ ] Is memory usage bounded?
- [ ] Are eviction policies defined?
- [ ] Is cleanup strategy documented?

**Resource Management**:
- [ ] Are resources properly managed?
- [ ] Are context managers used consistently?
- [ ] Is error handling proper (cleanup in finally)?

---

## Recommendations Format

```markdown
## Important: Memory Leak (Line 45)

**Category**: Memory Management
**Severity**: Important
**Issue**: Circular reference (parent-child without weak reference)

**Impact**: Objects never garbage collected, memory usage grows indefinitely.

**Current Code**:
```python
class Node:
    def __init__(self, value):
        self.parent = None  # Strong reference
        self.children = []

    def add_child(self, child):
        child.parent = self  # Circular reference!
        self.children.append(child)
```

**Fix** (Weak Reference):
```python
import weakref

class Node:
    def __init__(self, value):
        self.parent = None

    def add_child(self, child):
        child.parent = weakref.ref(self)  # Weak reference
        self.children.append(child)
```

**Why**: Weak reference allows garbage collector to free parent when no strong references remain.

**Verification**: Use `memory_profiler` to confirm memory usage stable over time.

**Resources**: See performance/memory-management.md for patterns.
```

---

## Summary

**Common Memory Smells**:
1. Memory Leak - Circular references
2. Unclosed Resources - File/connection leaks
3. Unbounded Caches - Growing forever
4. Large Data Structures - Loading entire dataset
5. String Building - Concatenation in loop
6. Mutable Default Arguments - Shared state
7. Global State Accumulation - Unbounded globals

**Memory Patterns**:
- Weak references for circular references
- Context managers for resource cleanup
- LRU cache with maxsize for bounded caches
- Streaming for large datasets
- List join for string building
- None defaults for mutable arguments

**Detection**:
- Phase 1: Automated detection of common patterns
- Phase 2: Manual review of memory design
- Profiling: Use `memory_profiler` to measure usage

**Why Not Refactorable**:
- Requires memory management knowledge
- Not code structure - requires lifecycle changes
- May require redesigning data structures

**Priority**: **Important** (causes OOM crashes, resource exhaustion)

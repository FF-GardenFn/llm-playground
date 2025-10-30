# Algorithmic Efficiency

**Purpose**: Detect inefficient algorithms and suggest better alternatives during code review.

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Important (causes scalability issues)

**Refactorable**: ❌ NO (requires algorithmic knowledge, not code structure changes)

---

## Overview

Algorithmic efficiency issues cannot be fixed by refactoring-engineer because they require:
- Understanding algorithmic complexity (Big O notation)
- Choosing appropriate data structures
- Redesigning algorithms (not behavior-preserving transformations)

These require **manual optimization**, not refactoring.

---

## Common Algorithm Smells

### 1. Nested Loops Over Same Dataset (O(n²))

**Problem**: Quadratic time complexity when linear is possible.

**Detection**:
- Nested `for` loops iterating same collection
- Inner loop searches outer loop's collection
- No early exit optimization

**Example - O(n²)**:
```python
# ❌ BAD: O(n²) - nested loops
def find_duplicates(items):
    """Find duplicate items in list"""
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# For 1000 items: ~500,000 comparisons
```

**Fix - O(n) with Set**:
```python
# ✅ GOOD: O(n) - single pass with set
def find_duplicates(items):
    """Find duplicate items in list"""
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)

# For 1000 items: ~1000 operations (500x faster)
```

**Alternative - O(n) with Counter**:
```python
# ✅ GOOD: O(n) - using Counter
from collections import Counter

def find_duplicates(items):
    """Find duplicate items in list"""
    counts = Counter(items)
    return [item for item, count in counts.items() if count > 1]
```

**Detection Heuristics**:
- `for i in range(len(items)):` nested with `for j in range(i+1, len(items)):`
- Inner loop compares with outer loop variable
- No `break` or early exit

**Severity**: **Important** (O(n²) causes severe slowdown for large inputs)

---

### 2. Linear Search When Binary Search Possible (O(n) vs O(log n))

**Problem**: Searching sorted data with linear search.

**Detection**:
- Searching sorted list with `in` operator or linear loop
- No use of `bisect` module
- Custom search implementation on sorted data

**Example - O(n)**:
```python
# ❌ BAD: O(n) - linear search on sorted data
def find_user(users, target_id):
    """users is sorted by id"""
    for user in users:
        if user.id == target_id:
            return user
    return None

# For 1,000,000 users: up to 1,000,000 comparisons
```

**Fix - O(log n) Binary Search**:
```python
# ✅ GOOD: O(log n) - binary search
import bisect

def find_user(users, target_id):
    """users is sorted by id"""
    # Find insertion point
    idx = bisect.bisect_left(users, target_id, key=lambda u: u.id)

    # Check if found
    if idx < len(users) and users[idx].id == target_id:
        return users[idx]
    return None

# For 1,000,000 users: ~20 comparisons (50,000x faster)
```

**Alternative - Use Dictionary**:
```python
# ✅ BETTER: O(1) - hash table lookup
def build_user_index(users):
    return {user.id: user for user in users}

user_index = build_user_index(users)

def find_user(user_index, target_id):
    return user_index.get(target_id)

# For 1,000,000 users: 1 operation (constant time)
```

**Detection Heuristics**:
- Comment mentions "sorted" but code uses linear search
- Searching list with `in` operator repeatedly
- No use of `bisect`, `set`, or `dict` for lookups

**Severity**: **Important** (O(n) vs O(log n) matters for large datasets)

---

### 3. List.index() in Loop (O(n²))

**Problem**: `list.index()` is O(n), calling it in loop is O(n²).

**Example - O(n²)**:
```python
# ❌ BAD: O(n²) - list.index() in loop
def remove_items(items, to_remove):
    """Remove items from list"""
    for item in to_remove:
        if item in items:
            items.remove(item)  # list.remove() is O(n)!
    return items

# For 1000 items, 1000 removals: ~1,000,000 operations
```

**Fix - O(n) with Set**:
```python
# ✅ GOOD: O(n) - set difference
def remove_items(items, to_remove):
    """Remove items from list"""
    to_remove_set = set(to_remove)
    return [item for item in items if item not in to_remove_set]

# For 1000 items, 1000 removals: ~1000 operations (1000x faster)
```

**Detection Heuristics**:
- `list.index()` inside loop
- `list.remove()` inside loop
- `item in list` check inside loop (should use set)

**Severity**: **Important**

---

### 4. Repeated Sorting (O(n log n))

**Problem**: Sorting multiple times when once is sufficient.

**Example - O(n² log n)**:
```python
# ❌ BAD: Sorting in loop
def process_batches(items, batch_size):
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        batch.sort()  # Sorting each batch!
        results.extend(batch)
    return results

# Sorts multiple times when could sort once
```

**Fix - O(n log n)**:
```python
# ✅ GOOD: Sort once
def process_batches(items, batch_size):
    items = sorted(items)  # Sort once
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        results.extend(batch)  # Already sorted
    return results
```

**Detection Heuristics**:
- `sort()` or `sorted()` inside loop
- Multiple sort calls on related data
- Sorting before single lookup (use set/dict instead)

**Severity**: **Suggestion** (depends on data size)

---

### 5. Unnecessary List Copies (O(n))

**Problem**: Creating unnecessary list copies in loop.

**Example - O(n²)**:
```python
# ❌ BAD: List copy in loop
def filter_items(items, conditions):
    result = items.copy()  # O(n)
    for condition in conditions:
        result = [item for item in result if condition(item)]  # O(n) each iteration
    return result

# For 1000 items, 10 conditions: ~10,000 copies
```

**Fix - O(n)**:
```python
# ✅ GOOD: Generator chain (no copies)
from functools import reduce

def filter_items(items, conditions):
    def apply_condition(items, condition):
        return (item for item in items if condition(item))

    return list(reduce(apply_condition, conditions, items))

# OR simpler: combine conditions
def filter_items(items, conditions):
    return [item for item in items if all(cond(item) for cond in conditions)]
```

**Detection Heuristics**:
- `list.copy()` in loop
- List comprehension in loop creating intermediate lists
- No generators used

**Severity**: **Suggestion** (optimization opportunity)

---

### 6. String Concatenation in Loop (O(n²))

**Problem**: String concatenation is O(n), doing it in loop is O(n²).

**Example - O(n²)**:
```python
# ❌ BAD: O(n²) - string concatenation in loop
def build_csv(rows):
    csv = ""
    for row in rows:
        csv += ",".join(row) + "\n"  # String concatenation is O(n)!
    return csv

# For 10,000 rows: ~50,000,000 character copies
```

**Fix - O(n) with Join**:
```python
# ✅ GOOD: O(n) - build list, join once
def build_csv(rows):
    lines = [",".join(row) for row in rows]
    return "\n".join(lines)

# For 10,000 rows: ~10,000 operations (5000x faster)
```

**Alternative - O(n) with io.StringIO**:
```python
# ✅ GOOD: O(n) - buffered writing
from io import StringIO

def build_csv(rows):
    buffer = StringIO()
    for row in rows:
        buffer.write(",".join(row))
        buffer.write("\n")
    return buffer.getvalue()
```

**Detection Heuristics**:
- `string += other_string` in loop
- `string = string + other_string` in loop
- No use of `"".join()` or `StringIO`

**Severity**: **Important** (severe for large strings)

---

## Data Structure Selection

### When to Use What

**List**: Ordered collection, indexed access
- Good for: Sequential access, small datasets
- Bad for: Membership testing, frequent insertions/deletions

**Set**: Unique items, fast membership testing
- Good for: Membership testing, removing duplicates
- Bad for: Maintaining order, indexed access

**Dictionary**: Key-value mapping
- Good for: Lookups by key, counting, grouping
- Bad for: Iterating in order (use `OrderedDict`)

**Deque**: Double-ended queue
- Good for: FIFO/LIFO operations, sliding windows
- Bad for: Random access (no indexing)

**Heap**: Priority queue
- Good for: Finding min/max, k-smallest/k-largest
- Bad for: Membership testing, arbitrary removal

### Common Mistakes

```python
# ❌ BAD: Using list for membership testing
items = ['a', 'b', 'c', 'd', 'e']  # list
if 'x' in items:  # O(n) search
    pass

# ✅ GOOD: Using set for membership testing
items = {'a', 'b', 'c', 'd', 'e'}  # set
if 'x' in items:  # O(1) search
    pass

# ❌ BAD: Using list to track visited
visited = []  # list
for node in graph:
    if node not in visited:  # O(n) search!
        visited.append(node)

# ✅ GOOD: Using set to track visited
visited = set()
for node in graph:
    if node not in visited:  # O(1) search!
        visited.add(node)
```

---

## Big O Complexity Reference

### Time Complexity

| Operation | List | Set | Dict | Deque |
|-----------|------|-----|------|-------|
| Access by index | O(1) | N/A | N/A | O(n) |
| Search | O(n) | O(1) | O(1) | O(n) |
| Insert at end | O(1)* | O(1) | O(1) | O(1) |
| Insert at beginning | O(n) | O(1) | O(1) | O(1) |
| Delete | O(n) | O(1) | O(1) | O(n) |

*Amortized time

### Common Complexities

- **O(1)**: Constant - hash table lookup, array access by index
- **O(log n)**: Logarithmic - binary search, balanced tree operations
- **O(n)**: Linear - iterating through list, linear search
- **O(n log n)**: Linearithmic - efficient sorting (mergesort, quicksort)
- **O(n²)**: Quadratic - nested loops, bubble sort
- **O(2ⁿ)**: Exponential - recursive fibonacci (naive), subset generation

---

## Detection Checklist

### Phase 1: Automated Analysis

**Nested Loops**:
- [ ] Are nested loops over same dataset (O(n²))?
- [ ] Can set/dict eliminate inner loop?
- [ ] Is early exit possible?

**Search Operations**:
- [ ] Is binary search possible on sorted data?
- [ ] Are repeated searches using list (should use set/dict)?
- [ ] Is `list.index()` or `list.remove()` in loop?

**Sorting**:
- [ ] Is sorting done repeatedly (should sort once)?
- [ ] Is sorting before single lookup (use dict instead)?

**String Operations**:
- [ ] Is string concatenation in loop (use join)?
- [ ] Are large strings built inefficiently?

**Data Structures**:
- [ ] Is list used for membership testing (use set)?
- [ ] Is list used for key lookups (use dict)?
- [ ] Is wrong data structure chosen?

### Phase 2: Manual Review

**Algorithm Choice**:
- [ ] Is algorithm appropriate for problem size?
- [ ] Are there standard library alternatives (bisect, heapq, collections)?
- [ ] Can problem be solved more efficiently?

**Scalability**:
- [ ] How does algorithm scale with input size?
- [ ] What happens with 10x, 100x, 1000x data?
- [ ] Are there performance bottlenecks?

---

## Recommendations Format

```markdown
## Important: Inefficient Algorithm (Line 45)

**Category**: Algorithmic Efficiency
**Severity**: Important
**Current Complexity**: O(n²)
**Optimized Complexity**: O(n)

**Impact**: For 1000 items, ~500,000 operations. Optimized: ~1000 operations (500x faster).

**Current Code**:
```python
# O(n²) - nested loops
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        if items[i] == items[j]:
            duplicates.append(items[i])
```

**Fix** (O(n) with set):
```python
seen = set()
duplicates = set()
for item in items:
    if item in seen:
        duplicates.add(item)
    seen.add(item)
```

**Why**: Hash table lookup is O(1), so single pass is O(n) vs O(n²) nested loops.

**Verification**: Profile with large dataset (10,000+ items) to confirm improvement.

**Resources**: See performance/algorithmic-efficiency.md for more patterns.
```

---

## Summary

**Common Algorithm Smells**:
1. Nested loops over same dataset - O(n²) → O(n) with set
2. Linear search on sorted data - O(n) → O(log n) with binary search
3. list.index() in loop - O(n²) → O(n) with set
4. Repeated sorting - O(n² log n) → O(n log n) sort once
5. Unnecessary list copies - O(n²) → O(n) with generators
6. String concatenation in loop - O(n²) → O(n) with join

**Data Structure Selection**:
- List → Sequential access
- Set → Membership testing
- Dict → Key lookups
- Deque → FIFO/LIFO operations
- Heap → Priority queue

**Detection**:
- Phase 1: Automated detection of common patterns
- Phase 2: Manual review of algorithm choice

**Why Not Refactorable**:
- Requires algorithmic knowledge
- Changes algorithm (not structure)
- May require different data structures
- Not behavior-preserving (changes performance characteristics)

**Priority**: **Important** (causes scalability issues for large datasets)

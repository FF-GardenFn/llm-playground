# Concurrency & Async Patterns

**Purpose**: Detect concurrency issues, async/await misuse, and race conditions during code review.

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Important (causes race conditions, deadlocks, performance issues)

**Refactorable**: ❌ NO (requires async/concurrency redesign, not code structure changes)

---

## Overview

Concurrency issues cannot be fixed by refactoring-engineer because they require:
- Understanding async/await patterns
- Concurrency primitives (locks, semaphores)
- Race condition detection
- Deadlock prevention strategies

These require **manual fixes**, not behavior-preserving refactoring.

---

## Common Concurrency Smells

### 1. Blocking I/O in Async Context

**Problem**: Synchronous operations block async event loop.

**Detection**:
- `requests`, `urllib` in `async def`
- File I/O without `aiofiles`
- `time.sleep()` instead of `await asyncio.sleep()`
- Database queries without async driver

**Example - Blocking**:
```python
# ❌ BAD: Blocking I/O in async function
import asyncio
import requests

async def fetch_data():
    # Blocks entire event loop while waiting!
    response = requests.get('https://api.example.com/data')
    return response.json()

# Event loop frozen until HTTP request completes
```

**Fix - Async I/O**:
```python
# ✅ GOOD: Async I/O
import asyncio
import aiohttp

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()

# Event loop can handle other tasks while waiting
```

**Detection Heuristics**:
- `import requests` in file with `async def`
- `time.sleep()` in `async def`
- `open()` without `aiofiles` in `async def`
- Database queries without `await`

**Severity**: **Important** (negates async benefits)

---

### 2. Missing await

**Problem**: Forgetting `await` causes coroutine to not execute.

**Example - Missing await**:
```python
# ❌ BAD: Missing await (coroutine never runs!)
async def save_user(user):
    user.save()  # Missing await!
    return True

# Function returns immediately without saving

# ✅ GOOD: Await coroutine
async def save_user(user):
    await user.save()  # Properly awaited
    return True
```

**Detection Heuristics**:
- Async function call without `await`
- Warning: "coroutine was never awaited"
- `asyncio.create_task()` not called on coroutine

**Severity**: **Critical** (code doesn't execute!)

---

### 3. Race Conditions

**Problem**: Shared mutable state accessed by multiple coroutines/threads without synchronization.

**Example - Race Condition**:
```python
# ❌ BAD: Race condition (shared counter)
counter = 0

async def increment():
    global counter
    current = counter
    await asyncio.sleep(0.001)  # Simulates I/O
    counter = current + 1  # Race! Multiple coroutines read same value

# Run 100 concurrent increments
async def main():
    await asyncio.gather(*[increment() for _ in range(100)])
    print(counter)  # Expected: 100, Actual: ~50-70 (lost updates!)

# Multiple coroutines read counter=0, all write counter=1
```

**Fix - Lock for Synchronization**:
```python
# ✅ GOOD: Lock protects shared state
import asyncio

counter = 0
counter_lock = asyncio.Lock()

async def increment():
    global counter
    async with counter_lock:  # Acquire lock
        current = counter
        await asyncio.sleep(0.001)
        counter = current + 1
    # Lock released

async def main():
    await asyncio.gather(*[increment() for _ in range(100)])
    print(counter)  # Always 100 (no lost updates)
```

**Alternative - Thread-Safe Data Structure**:
```python
# ✅ GOOD: Use atomic operations
import asyncio
from collections import deque

# deque.append() is thread-safe
events = deque()

async def log_event(event):
    events.append(event)  # Thread-safe, no lock needed
```

**Detection Heuristics**:
- Shared mutable global variables
- No locks protecting shared state
- Read-modify-write pattern without synchronization

**Severity**: **Critical** (causes data corruption)

---

### 4. Deadlock

**Problem**: Multiple locks acquired in inconsistent order.

**Example - Deadlock**:
```python
# ❌ BAD: Deadlock risk (inconsistent lock order)
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def transfer_a_to_b():
    async with lock_a:
        await asyncio.sleep(0.01)  # Delay increases deadlock chance
        async with lock_b:
            # Transfer money A → B
            pass

async def transfer_b_to_a():
    async with lock_b:  # ← Locks acquired in different order!
        await asyncio.sleep(0.01)
        async with lock_a:
            # Transfer money B → A
            pass

# Deadlock: transfer_a_to_b holds lock_a, waits for lock_b
#           transfer_b_to_a holds lock_b, waits for lock_a
```

**Fix - Consistent Lock Ordering**:
```python
# ✅ GOOD: Always acquire locks in same order
import asyncio

lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def transfer_a_to_b():
    async with lock_a:  # Always A then B
        async with lock_b:
            # Transfer A → B
            pass

async def transfer_b_to_a():
    async with lock_a:  # Always A then B (consistent order)
        async with lock_b:
            # Transfer B → A
            pass

# No deadlock: locks always acquired in same order
```

**Alternative - Single Lock**:
```python
# ✅ GOOD: Use single lock for related resources
transfer_lock = asyncio.Lock()

async def transfer_a_to_b():
    async with transfer_lock:
        # Transfer A → B
        pass

async def transfer_b_to_a():
    async with transfer_lock:
        # Transfer B → A
        pass
```

**Detection Heuristics**:
- Multiple locks acquired
- Locks acquired in different orders in different functions
- Nested lock acquisitions

**Severity**: **Critical** (causes application freeze)

---

### 5. Not Concurrent (Sequential Await)

**Problem**: Awaiting coroutines sequentially when they could run concurrently.

**Example - Sequential**:
```python
# ❌ BAD: Sequential execution (slow)
async def fetch_all_data():
    users = await fetch_users()      # Wait 1s
    orders = await fetch_orders()    # Wait 1s
    products = await fetch_products() # Wait 1s
    return users, orders, products

# Total time: 3 seconds (sequential)
```

**Fix - Concurrent Execution**:
```python
# ✅ GOOD: Concurrent execution (fast)
async def fetch_all_data():
    users, orders, products = await asyncio.gather(
        fetch_users(),
        fetch_orders(),
        fetch_products()
    )
    return users, orders, products

# Total time: 1 second (concurrent, limited by slowest)
```

**Detection Heuristics**:
- Multiple `await` statements in sequence
- No use of `asyncio.gather()` or `asyncio.create_task()`
- Independent operations awaited sequentially

**Severity**: **Suggestion** (missed performance optimization)

---

### 6. Resource Contention (Too Many Concurrent Tasks)

**Problem**: Creating too many concurrent tasks overwhelms resources.

**Example - Resource Exhaustion**:
```python
# ❌ BAD: 10,000 concurrent HTTP requests
async def fetch_all_urls(urls):
    tasks = [fetch_url(url) for url in urls]  # 10,000 tasks!
    return await asyncio.gather(*tasks)

# Overwhelms: file descriptors, network connections, memory
```

**Fix - Semaphore Limits Concurrency**:
```python
# ✅ GOOD: Limit concurrent requests
import asyncio

async def fetch_with_semaphore(semaphore, url):
    async with semaphore:  # Acquire slot
        return await fetch_url(url)
    # Release slot

async def fetch_all_urls(urls):
    semaphore = asyncio.Semaphore(100)  # Max 100 concurrent
    tasks = [fetch_with_semaphore(semaphore, url) for url in urls]
    return await asyncio.gather(*tasks)

# Always ≤ 100 concurrent requests
```

**Alternative - Batch Processing**:
```python
# ✅ GOOD: Process in batches
async def fetch_all_urls(urls, batch_size=100):
    results = []
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        batch_results = await asyncio.gather(*[fetch_url(url) for url in batch])
        results.extend(batch_results)
    return results
```

**Detection Heuristics**:
- Large number of concurrent tasks (>1000)
- No semaphore or rate limiting
- External API calls without concurrency limits

**Severity**: **Important** (causes resource exhaustion)

---

### 7. Shared State in Async (Non-Atomic Updates)

**Problem**: Async code shares state without considering interleaving.

**Example - Lost Updates**:
```python
# ❌ BAD: Non-atomic update
async def withdraw(account, amount):
    balance = account.balance  # Read
    await asyncio.sleep(0.1)   # Simulates I/O
    account.balance = balance - amount  # Write

# Two concurrent withdrawals:
# T1: Read balance=100
# T2: Read balance=100
# T1: Write balance=50 (withdrew 50)
# T2: Write balance=80 (withdrew 20) ← Overwrites T1!
# Final: 80 (should be 30)
```

**Fix - Atomic Update with Lock**:
```python
# ✅ GOOD: Atomic update with lock
account_lock = asyncio.Lock()

async def withdraw(account, amount):
    async with account_lock:
        balance = account.balance
        await asyncio.sleep(0.1)
        account.balance = balance - amount

# Lock ensures atomic read-modify-write
```

**Detection Heuristics**:
- Read-modify-write pattern on shared state
- No locks or atomic operations
- Await between read and write

**Severity**: **Critical** (causes data corruption)

---

## Async Best Practices

### 1. Always Use Async Libraries in Async Code

```python
# ❌ BAD: Mixing sync and async
import requests
async def fetch():
    return requests.get(url)  # Blocks!

# ✅ GOOD: Use async library
import aiohttp
async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### 2. Use asyncio.gather() for Concurrent Tasks

```python
# ❌ BAD: Sequential
result1 = await task1()
result2 = await task2()

# ✅ GOOD: Concurrent
result1, result2 = await asyncio.gather(task1(), task2())
```

### 3. Use Semaphores for Rate Limiting

```python
# ✅ GOOD: Limit concurrent operations
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

async def limited_operation():
    async with semaphore:
        return await expensive_operation()
```

### 4. Proper Error Handling in Async

```python
# ✅ GOOD: Handle errors in concurrent tasks
results = await asyncio.gather(
    task1(),
    task2(),
    return_exceptions=True  # Don't fail fast
)

for result in results:
    if isinstance(result, Exception):
        handle_error(result)
```

---

## Thread Safety (Multithreading)

### Race Condition with Threads

```python
# ❌ BAD: Thread race condition
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1  # Not atomic!

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # Expected: 1,000,000, Actual: ~500,000
```

### Fix with Lock

```python
# ✅ GOOD: Lock protects shared state
import threading

counter = 0
counter_lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with counter_lock:
            counter += 1  # Atomic

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # Always 1,000,000
```

---

## Detection Checklist

### Phase 1: Automated Analysis

**Blocking in Async**:
- [ ] Are sync I/O operations in `async def`?
- [ ] Is `requests` used in async code?
- [ ] Is `time.sleep()` used instead of `await asyncio.sleep()`?

**Missing await**:
- [ ] Are coroutines called without `await`?
- [ ] Are async function results ignored?

**Race Conditions**:
- [ ] Is shared mutable state accessed without locks?
- [ ] Are read-modify-write patterns unprotected?

**Concurrency Issues**:
- [ ] Are locks acquired in consistent order?
- [ ] Is `asyncio.gather()` used for concurrent tasks?
- [ ] Are semaphores used for rate limiting?

### Phase 2: Manual Review

**Concurrency Design**:
- [ ] Is synchronization strategy documented?
- [ ] Are shared resources identified?
- [ ] Is deadlock prevention considered?

**Performance**:
- [ ] Are operations concurrent when possible?
- [ ] Are resource limits (semaphores) appropriate?
- [ ] Is error handling proper in concurrent code?

---

## Recommendations Format

```markdown
## Important: Blocking I/O in Async Context (Line 45)

**Category**: Concurrency
**Severity**: Important
**Issue**: Synchronous `requests` library blocks async event loop

**Impact**: Negates async benefits, entire event loop frozen during HTTP request.

**Current Code**:
```python
async def fetch_data():
    response = requests.get(url)  # Blocks event loop!
    return response.json()
```

**Fix** (Async Library):
```python
import aiohttp

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Why**: `aiohttp` is non-blocking, allows event loop to handle other tasks while waiting.

**Verification**: Run async profiler to confirm event loop not blocked.

**Resources**: See performance/concurrency.md for async patterns.
```

---

## Summary

**Common Concurrency Smells**:
1. Blocking I/O in Async - Sync operations in `async def`
2. Missing await - Coroutine not executed
3. Race Conditions - Shared state without synchronization
4. Deadlock - Inconsistent lock ordering
5. Sequential Await - Missed concurrency opportunities
6. Resource Contention - Too many concurrent tasks
7. Non-Atomic Updates - Lost updates in shared state

**Async Patterns**:
- Use async libraries (`aiohttp`, `aiofiles`)
- Always `await` coroutines
- Use `asyncio.gather()` for concurrency
- Use `asyncio.Lock()` for shared state
- Use `asyncio.Semaphore()` for rate limiting
- Consistent lock ordering for deadlock prevention

**Thread Safety**:
- Use `threading.Lock()` for shared state
- Atomic operations where possible
- Avoid shared mutable state

**Detection**:
- Phase 1: Automated detection of blocking operations
- Phase 2: Manual review of concurrency design

**Why Not Refactorable**:
- Requires async/concurrency redesign
- Not code structure - requires execution model changes
- Changes behavior (sequential → concurrent)

**Priority**: **Important** to **Critical** (causes race conditions, deadlocks, performance issues)

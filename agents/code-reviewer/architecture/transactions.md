# Transactions & Data Consistency

**Purpose**: Assess transaction handling, ACID properties, and data consistency patterns during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Critical (affects data integrity)

**Refactorable**:  NO (requires transaction design, not code structure changes)

---

## Overview

Transactions ensure data consistency in multi-step operations. Code-reviewer must verify:
- **Atomicity**: All operations succeed or all fail
- **Consistency**: Data remains valid
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed changes persist

---

## Transaction Principles

### 1. Atomic Operations

**Principle**: Related operations should be atomic (all-or-nothing).

**Good - Transaction Wraps Multiple Operations**:
```python
# GOOD: Atomic transaction
from django.db import transaction

@transaction.atomic
def transfer_money(from_account, to_account, amount):
    # Both operations succeed or both fail
    from_account.balance -= amount
    from_account.save()

    to_account.balance += amount
    to_account.save()

# If second save() fails, first save() is rolled back
```

**Bad - No Transaction**:
```python
# BAD: Non-atomic operations
def transfer_money(from_account, to_account, amount):
    from_account.balance -= amount
    from_account.save()  # Committed!

    # If this fails, money is lost from from_account
    # but never added to to_account!
    to_account.balance += amount
    to_account.save()

# Data inconsistency: money disappeared!
```

**Detection Heuristics**:
- Multiple database writes without transaction
- Financial operations without transaction
- Related state changes not wrapped in transaction

**Severity**: **Critical** (data corruption)

---

### 2. Transaction Scope

**Principle**: Transactions should be as small as possible.

**Good - Minimal Scope**:
```python
# GOOD: Narrow transaction scope
def create_order(order_data):
    # Non-transactional operations first
    validate_order(order_data)
    check_inventory(order_data)

    # Only database writes in transaction
    with transaction.atomic():
        order = Order.objects.create(**order_data)
        update_inventory(order.items)
        return order
```

**Bad - Large Scope**:
```python
# BAD: Transaction holds lock too long
@transaction.atomic
def create_order(order_data):
    # Long-running validation in transaction!
    validate_order(order_data)  # 2 seconds

    # External API call in transaction!
    check_payment_gateway(order_data)  # 5 seconds

    # Database writes
    order = Order.objects.create(**order_data)
    update_inventory(order.items)

    # Email sending in transaction!
    send_confirmation_email(order)  # 3 seconds

    return order

# Transaction holds database locks for 10+ seconds!
```

**Detection Heuristics**:
- External API calls inside transactions
- Long-running operations in transactions
- I/O operations in transactions

**Severity**: **Important** (performance, deadlocks)

---

### 3. Isolation Levels

**Principle**: Choose appropriate isolation level.

**Isolation Levels**:

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|------------|---------------------|--------------|
| Read Uncommitted | Yes | Yes | Yes |
| Read Committed | No | Yes | Yes |
| Repeatable Read | No | No | Yes |
| Serializable | No | No | No |

**Example - Read Committed (Default)**:
```python
# GOOD: Explicit isolation level
from django.db import transaction

with transaction.atomic(isolation_level=transaction.ISOLATION_LEVEL_READ_COMMITTED):
    # Can read committed data from other transactions
    order = Order.objects.get(id=order_id)
    order.status = 'processing'
    order.save()
```

**Example - Serializable (Strongest)**:
```python
# GOOD: Serializable for critical operations
with transaction.atomic(isolation_level=transaction.ISOLATION_LEVEL_SERIALIZABLE):
    # Complete isolation - no concurrent modifications
    account = Account.objects.get(id=account_id)
    if account.balance >= amount:
        account.balance -= amount
        account.save()
    else:
        raise InsufficientBalanceError()

# Prevents phantom reads in balance check
```

**Detection Heuristics**:
- No explicit isolation level for critical operations
- Default isolation used for financial operations
- Check-then-act pattern without serializable isolation

**Severity**: **Important** (prevents race conditions)

---

### 4. Optimistic vs Pessimistic Locking

**Optimistic Locking (Version Field)**:
```python
# GOOD: Optimistic locking with version field
class Account(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    version = models.IntegerField(default=0)  # Version field

def withdraw(account_id, amount):
    account = Account.objects.get(id=account_id)
    original_version = account.version

    if account.balance < amount:
        raise InsufficientBalanceError()

    account.balance -= amount
    account.version += 1

    # Only updates if version hasn't changed
    updated = Account.objects.filter(
        id=account_id,
        version=original_version
    ).update(balance=account.balance, version=account.version)

    if not updated:
        raise ConcurrentModificationError("Account modified by another transaction")
```

**Pessimistic Locking (SELECT FOR UPDATE)**:
```python
# GOOD: Pessimistic locking
def withdraw(account_id, amount):
    with transaction.atomic():
        # Locks row until transaction commits
        account = Account.objects.select_for_update().get(id=account_id)

        if account.balance < amount:
            raise InsufficientBalanceError()

        account.balance -= amount
        account.save()

# Other transactions wait for lock release
```

**When to Use**:
- **Optimistic**: Low contention, read-heavy workloads
- **Pessimistic**: High contention, write-heavy workloads

**Detection Heuristics**:
- Check-then-act pattern without locking
- No version fields or `select_for_update()`
- Concurrent modifications possible

**Severity**: **Critical** (race conditions, lost updates)

---

### 5. Idempotency

**Principle**: Operations should be safely repeatable.

**Good - Idempotent Operation**:
```python
# GOOD: Idempotent charge
def charge_order(order_id):
    order = Order.objects.get(id=order_id)

    # Check if already charged
    if order.payment_status == 'charged':
        return order  # Already done, safe to return

    # Charge only once
    payment = charge_card(order.user.card, order.total)
    order.payment_status = 'charged'
    order.payment_id = payment.id
    order.save()

    return order

# Safe to call multiple times (e.g., on retry)
```

**Bad - Non-Idempotent**:
```python
# BAD: Charges card multiple times on retry
def charge_order(order_id):
    order = Order.objects.get(id=order_id)

    # Always charges, even if already done!
    payment = charge_card(order.user.card, order.total)
    order.payment_id = payment.id
    order.save()

    return order

# Retry charges card again!
```

**Detection Heuristics**:
- Operations that can be retried but aren't idempotent
- No checks for already-completed operations
- External API calls without idempotency keys

**Severity**: **Critical** (duplicate charges, data corruption)

---

### 6. Savepoints (Nested Transactions)

**Principle**: Use savepoints for partial rollbacks.

**Good - Savepoints**:
```python
# GOOD: Savepoints allow partial rollback
from django.db import transaction

def process_batch(items):
    with transaction.atomic():
        for item in items:
            # Create savepoint before each item
            sid = transaction.savepoint()

            try:
                process_item(item)
                transaction.savepoint_commit(sid)
            except ProcessingError:
                # Rollback this item only, continue with next
                transaction.savepoint_rollback(sid)
                logger.error(f"Failed to process item {item.id}")

# Some items succeed, some fail (partial success)
```

**Bad - All-or-Nothing**:
```python
# BAD: One failure rolls back entire batch
@transaction.atomic
def process_batch(items):
    for item in items:
        process_item(item)  # If any fails, all rollback!

# All-or-nothing (no partial success)
```

**Detection Heuristics**:
- Batch operations without savepoints
- No partial success handling
- Single transaction for independent operations

**Severity**: **Suggestion** (reduces flexibility)

---

### 7. Distributed Transactions

**Principle**: Handle distributed transactions carefully.

**Good - Two-Phase Commit (if supported)**:
```python
# GOOD: Two-phase commit (if database supports)
from django.db import transaction

@transaction.atomic
def transfer_across_databases():
    # Phase 1: Prepare
    with transaction.atomic(using='db1'):
        account1 = Account.objects.using('db1').select_for_update().get(id=1)
        account1.balance -= 100
        account1.save()

    with transaction.atomic(using='db2'):
        account2 = Account.objects.using('db2').select_for_update().get(id=2)
        account2.balance += 100
        account2.save()

    # Phase 2: Commit (both or neither)
```

**Alternative - Saga Pattern**:
```python
# GOOD: Saga pattern for microservices
def transfer_across_services(from_account_id, to_account_id, amount):
    try:
        # Step 1: Debit from account
        debit_result = account_service.debit(from_account_id, amount)

        try:
            # Step 2: Credit to account
            credit_result = payment_service.credit(to_account_id, amount)
        except Exception as e:
            # Compensating transaction: undo debit
            account_service.credit(from_account_id, amount)
            raise

    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        raise TransferError("Transfer failed")
```

**Detection Heuristics**:
- Operations across multiple databases
- Microservice calls without compensation
- No rollback strategy for distributed operations

**Severity**: **Critical** (distributed data consistency)

---

### 8. Transaction Retry Logic

**Principle**: Retry transient transaction failures.

**Good - Retry with Backoff**:
```python
# GOOD: Retry deadlocks
from django.db import transaction
import time

def transfer_with_retry(from_account_id, to_account_id, amount, max_retries=3):
    for attempt in range(max_retries):
        try:
            with transaction.atomic():
                from_account = Account.objects.select_for_update().get(id=from_account_id)
                to_account = Account.objects.select_for_update().get(id=to_account_id)

                from_account.balance -= amount
                from_account.save()

                to_account.balance += amount
                to_account.save()

            return  # Success

        except transaction.TransactionError as e:
            if 'deadlock' in str(e).lower():
                if attempt == max_retries - 1:
                    raise  # Final attempt failed

                wait_time = 0.1 * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Deadlock detected (attempt {attempt+1}), retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                raise  # Non-retryable error
```

**Detection Heuristics**:
- No retry logic for transaction failures
- Deadlocks not handled
- No exponential backoff

**Severity**: **Suggestion** (improves reliability)

---

### 9. Database Constraints

**Principle**: Use database constraints for data integrity.

**Good - Constraints Enforce Invariants**:
```python
# GOOD: Database constraints
class Account(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            # Balance must be non-negative
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='balance_non_negative'
            ),
        ]

# Database prevents negative balance, even with bugs
```

**Bad - Application-Only Validation**:
```python
# BAD: Only application validates
class Account(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)

def withdraw(account, amount):
    if account.balance < amount:
        raise InsufficientBalanceError()
    account.balance -= amount
    account.save()

# Race condition: Two concurrent withdrawals can make balance negative!
```

**Detection Heuristics**:
- No database constraints for business rules
- Application-only validation for critical invariants
- No unique constraints where needed

**Severity**: **Important** (data integrity)

---

### 10. Read-Modify-Write Pattern

**Principle**: Protect read-modify-write sequences.

**Good - Atomic Read-Modify-Write**:
```python
# GOOD: Atomic F() expression
from django.db.models import F

def increment_view_count(post_id):
    # Atomic update (no race condition)
    Post.objects.filter(id=post_id).update(view_count=F('view_count') + 1)

# GOOD: SELECT FOR UPDATE
def increment_view_count(post_id):
    with transaction.atomic():
        post = Post.objects.select_for_update().get(id=post_id)
        post.view_count += 1
        post.save()
```

**Bad - Non-Atomic Read-Modify-Write**:
```python
# BAD: Race condition
def increment_view_count(post_id):
    post = Post.objects.get(id=post_id)  # Read
    post.view_count += 1                 # Modify
    post.save()                          # Write

# Two concurrent calls:
# T1: Read view_count=10
# T2: Read view_count=10
# T1: Write view_count=11
# T2: Write view_count=11 (should be 12!)
# Lost update!
```

**Detection Heuristics**:
- Read-modify-write without locking
- Update without F() expressions
- Counters without atomic operations

**Severity**: **Critical** (lost updates)

---

## Review Checklist

### Phase 2: Manual Review

**Atomicity**:
- [ ] Are related operations wrapped in transactions?
- [ ] Can partial failures leave data inconsistent?
- [ ] Are financial operations atomic?

**Transaction Scope**:
- [ ] Are transactions as small as possible?
- [ ] Are external API calls outside transactions?
- [ ] Are I/O operations outside transactions?

**Locking**:
- [ ] Is `select_for_update()` used for critical reads?
- [ ] Are version fields used for optimistic locking?
- [ ] Is isolation level appropriate?

**Idempotency**:
- [ ] Can operations be safely retried?
- [ ] Are already-completed operations checked?
- [ ] Are external API calls idempotent?

**Consistency**:
- [ ] Are database constraints defined?
- [ ] Are business rules enforced at database level?
- [ ] Are read-modify-write patterns atomic?

---

## Summary

**Transaction Principles**:
1. Atomic operations (all-or-nothing)
2. Minimal transaction scope
3. Appropriate isolation level
4. Locking (optimistic or pessimistic)
5. Idempotency (safe to retry)
6. Savepoints for partial rollback
7. Distributed transaction handling
8. Retry logic for transient failures
9. Database constraints
10. Atomic read-modify-write

**Common Violations**:
- Multiple database writes without transaction
- External API calls in transactions
- No locking for read-modify-write
- Non-idempotent operations
- No database constraints
- Race conditions in counters

**Detection**:
- Phase 2: Manual transaction review
- Look for multi-step operations without transactions
- Check critical paths (financial, inventory)

**Refactorable**:  NO (requires transaction design)

**Priority**: **Critical** (affects data integrity, consistency)

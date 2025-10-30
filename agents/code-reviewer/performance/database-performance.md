# Database Performance

**Purpose**: Detect database performance issues including N+1 queries, missing indexes, and inefficient queries.

**Phase**: Phase 1 (Automated Analysis) and Phase 2 (Manual Review)

**Priority**: Important (causes severe performance degradation)

**Refactorable**: ❌ NO (requires database/ORM knowledge, not code structure changes)

---

## Overview

Database performance issues cannot be fixed by refactoring-engineer because they require:
- Understanding database query execution
- ORM behavior knowledge
- Database schema design
- Query optimization techniques

These require **manual optimization**, not behavior-preserving refactoring.

---

## Common Database Smells

### 1. N+1 Query Problem

**Problem**: Executing N additional queries in loop when 1-2 queries would suffice.

**Detection**:
- Database query inside `for` loop
- ORM relationship access during iteration
- No `prefetch_related()` or `select_related()`

**Example - N+1 (Django)**:
```python
# ❌ BAD: N+1 query problem (1 + N queries)
def get_users_with_orders():
    users = User.objects.all()  # Query 1: SELECT * FROM users
    result = []
    for user in users:
        # Query 2-1001: SELECT * FROM orders WHERE user_id = ?
        orders = user.orders.all()  # N queries!
        result.append({
            'user': user.name,
            'order_count': len(orders)
        })
    return result

# For 1000 users: 1 + 1000 = 1001 database queries!
```

**Fix - Eager Loading (2 queries)**:
```python
# ✅ GOOD: Eager loading with prefetch_related (2 queries)
def get_users_with_orders():
    # Query 1: SELECT * FROM users
    # Query 2: SELECT * FROM orders WHERE user_id IN (...)
    users = User.objects.prefetch_related('orders')

    result = []
    for user in users:
        orders = user.orders.all()  # No query! (already loaded)
        result.append({
            'user': user.name,
            'order_count': len(orders)
        })
    return result

# Always 2 queries regardless of user count
```

**Fix - Aggregation (1 query)**:
```python
# ✅ BETTER: Aggregation (1 query)
from django.db.models import Count

def get_users_with_orders():
    # Query 1: SELECT users.*, COUNT(orders.id) FROM users LEFT JOIN orders ...
    users = User.objects.annotate(order_count=Count('orders'))

    result = []
    for user in users:
        result.append({
            'user': user.name,
            'order_count': user.order_count  # No query!
        })
    return result

# Always 1 query
```

**Detection Heuristics**:
- `.objects.get()` inside `for` loop
- `.objects.filter()` inside `for` loop
- Relationship access (`.foreign_key`, `.related_set.all()`) without prefetch
- `len(related_objects)` without `Count()` annotation

**Severity**: **Important** (causes severe performance degradation)

---

### 2. Missing Database Indexes

**Problem**: Queries on unindexed columns cause full table scans.

**Detection**:
- Frequent `WHERE` clauses on unindexed columns
- Slow query logs showing sequential scans
- Model fields used in filters without `db_index=True`

**Example - Missing Index**:
```python
# ❌ BAD: Frequent queries on unindexed email column
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=255)  # No index!
    created_at = models.DateTimeField()

def find_user_by_email(email):
    # Full table scan on 1M users!
    return User.objects.get(email=email)

# EXPLAIN: Seq Scan on users (cost=0.00..18334.00 rows=1000000)
```

**Fix - Add Index**:
```python
# ✅ GOOD: Add index to email column
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=255, db_index=True)  # Indexed!
    created_at = models.DateTimeField()

def find_user_by_email(email):
    # Index scan (fast)
    return User.objects.get(email=email)

# EXPLAIN: Index Scan using users_email_idx (cost=0.42..8.44 rows=1)
```

**Composite Index Example**:
```python
# ✅ GOOD: Composite index for common query pattern
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()

    class Meta:
        indexes = [
            # Composite index for common query
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

# Fast query using composite index
def get_active_orders_for_user(user_id):
    return Order.objects.filter(user_id=user_id, status='active')
```

**Detection Heuristics**:
- Model fields in `.filter()` without `db_index=True` or foreign key
- Frequent queries on same columns
- Slow query logs (if available)

**Severity**: **Important** (causes slow queries)

---

### 3. Select N+1 (Fetching Too Much Data)

**Problem**: Selecting all columns when only few are needed.

**Example - Wasteful**:
```python
# ❌ BAD: Fetching all user fields when only need name and email
def get_user_emails():
    users = User.objects.all()  # SELECT * FROM users
    return [user.email for user in users]

# Transfers unnecessary data (passwords, addresses, etc.)
```

**Fix - Only Fetch Needed Columns**:
```python
# ✅ GOOD: Select only needed columns
def get_user_emails():
    users = User.objects.only('email')  # SELECT id, email FROM users
    return [user.email for user in users]

# OR use values() for dict
def get_user_emails():
    return User.objects.values_list('email', flat=True)
    # Returns ['user1@example.com', 'user2@example.com', ...]
```

**Detection Heuristics**:
- `.all()` or `.filter()` without `.only()` or `.values()`
- Using only 1-2 fields from model with many fields
- Large result sets

**Severity**: **Suggestion** (optimization opportunity)

---

### 4. Unnecessary Queries

**Problem**: Executing queries that could be combined or cached.

**Example - Repeated Queries**:
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

**Fix - Single Query with Prefetch**:
```python
# ✅ GOOD: Single query with prefetch (or 2-3 optimized queries)
def get_user_summary(user_id):
    user = User.objects.prefetch_related('orders', 'payments').get(id=user_id)
    return {
        'user': user,
        'orders': user.orders.all(),  # No query
        'payments': user.payments.all()  # No query
    }
```

**Detection Heuristics**:
- Multiple `.objects.get()` or `.objects.filter()` calls in succession
- Queries that could use `prefetch_related()` or `select_related()`

**Severity**: **Important**

---

### 5. Missing select_related() for Foreign Keys

**Problem**: Accessing foreign key causes additional query.

**Example - N+1 on Foreign Keys**:
```python
# ❌ BAD: N+1 on foreign key access
def get_orders_with_users():
    orders = Order.objects.all()  # Query 1
    result = []
    for order in orders:
        # Query 2-1001: SELECT * FROM users WHERE id = ?
        username = order.user.name  # N queries!
        result.append({
            'order_id': order.id,
            'username': username
        })
    return result

# For 1000 orders: 1 + 1000 = 1001 queries
```

**Fix - select_related() for Foreign Keys**:
```python
# ✅ GOOD: select_related() for foreign keys (1 query with JOIN)
def get_orders_with_users():
    # Query 1: SELECT * FROM orders JOIN users ON orders.user_id = users.id
    orders = Order.objects.select_related('user')

    result = []
    for order in orders:
        username = order.user.name  # No query! (already joined)
        result.append({
            'order_id': order.id,
            'username': username
        })
    return result

# Always 1 query (with JOIN)
```

**Rule of Thumb**:
- **select_related()**: For ForeignKey and OneToOneField (uses JOIN)
- **prefetch_related()**: For ManyToManyField and reverse ForeignKey (uses separate query)

**Detection Heuristics**:
- Foreign key access (`.foreign_key.field`) without `select_related()`
- Iteration accessing foreign keys repeatedly

**Severity**: **Important**

---

### 6. Inefficient Filters

**Problem**: Filters that prevent index usage.

**Example - Functions in WHERE Clause**:
```python
# ❌ BAD: Function on column prevents index usage
def find_users_by_date(target_date):
    # WHERE YEAR(created_at) = 2024 (index not used!)
    return User.objects.filter(created_at__year=target_date.year)

# EXPLAIN: Seq Scan (function on indexed column prevents index usage)
```

**Fix - Range Query Uses Index**:
```python
# ✅ GOOD: Range query uses index
from datetime import datetime

def find_users_by_date(target_date):
    year_start = datetime(target_date.year, 1, 1)
    year_end = datetime(target_date.year + 1, 1, 1)
    # WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
    return User.objects.filter(created_at__gte=year_start, created_at__lt=year_end)

# EXPLAIN: Index Range Scan
```

**Other Examples**:
```python
# ❌ BAD: LIKE '%pattern%' (no index usage)
User.objects.filter(name__icontains='smith')

# ✅ GOOD: LIKE 'pattern%' (index can be used)
User.objects.filter(name__istartswith='smith')

# ❌ BAD: OR conditions often inefficient
User.objects.filter(name='John') | User.objects.filter(name='Jane')

# ✅ GOOD: IN clause more efficient
User.objects.filter(name__in=['John', 'Jane'])
```

**Detection Heuristics**:
- `__year`, `__month`, `__day` on indexed timestamp
- `__icontains` (LIKE %pattern%)
- Complex OR conditions

**Severity**: **Suggestion**

---

### 7. Count Queries on Large Tables

**Problem**: `COUNT(*)` on large tables is slow.

**Example - Expensive Count**:
```python
# ❌ BAD: Expensive COUNT(*) on 10M row table
def get_user_count():
    return User.objects.count()  # SELECT COUNT(*) FROM users (slow!)
```

**Fix - Cache Count**:
```python
# ✅ GOOD: Cache count in separate table
class UserStats(models.Model):
    total_users = models.IntegerField()
    updated_at = models.DateTimeField()

def get_user_count():
    stats = UserStats.objects.first()
    return stats.total_users if stats else 0

# Update count asynchronously or via trigger
```

**Alternative - Approximate Count**:
```python
# ✅ GOOD: Use approximate count for large tables (PostgreSQL)
from django.db import connection

def get_approximate_user_count():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT reltuples::bigint AS estimate
            FROM pg_class
            WHERE relname = 'users'
        """)
        return cursor.fetchone()[0]
```

**Detection Heuristics**:
- `.count()` on tables with millions of rows
- Count in hot path (e.g., every page load)

**Severity**: **Important** (for large tables)

---

## Query Optimization Patterns

### Batch Operations

```python
# ❌ BAD: Individual inserts (N queries)
for data in user_data_list:
    User.objects.create(**data)

# ✅ GOOD: Bulk insert (1 query)
User.objects.bulk_create([User(**data) for data in user_data_list])

# ❌ BAD: Individual updates (N queries)
for user in users:
    user.is_active = True
    user.save()

# ✅ GOOD: Bulk update (1 query)
User.objects.filter(id__in=[user.id for user in users]).update(is_active=True)
```

### Query Caching

```python
# ❌ BAD: Repeated identical queries
def process_orders(orders):
    for order in orders:
        user = User.objects.get(id=order.user_id)  # Repeated query!
        # Process...

# ✅ GOOD: Cache user lookups
def process_orders(orders):
    user_ids = [order.user_id for order in orders]
    users = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    for order in orders:
        user = users[order.user_id]  # No query!
        # Process...
```

### Pagination

```python
# ❌ BAD: Load all records (slow for large datasets)
def get_all_users():
    return User.objects.all()  # Loads 1M users into memory!

# ✅ GOOD: Paginate results
from django.core.paginator import Paginator

def get_users_page(page_num, page_size=100):
    users = User.objects.all()
    paginator = Paginator(users, page_size)
    return paginator.get_page(page_num)
```

---

## Detection Checklist

### Phase 1: Automated Analysis

**N+1 Queries**:
- [ ] Are queries inside `for` loops?
- [ ] Are relationships accessed without `prefetch_related()`?
- [ ] Are foreign keys accessed without `select_related()`?

**Missing Indexes**:
- [ ] Are model fields in filters without indexes?
- [ ] Are composite indexes needed for common queries?

**Inefficient Queries**:
- [ ] Is `SELECT *` used when only few columns needed?
- [ ] Are multiple queries executable as one?
- [ ] Are batch operations used for bulk inserts/updates?

**Query Patterns**:
- [ ] Are functions used in WHERE clauses?
- [ ] Is `LIKE '%pattern%'` used instead of `LIKE 'pattern%'`?
- [ ] Is `COUNT(*)` used on large tables?

### Phase 2: Manual Review

**Database Design**:
- [ ] Are indexes appropriate for query patterns?
- [ ] Is database schema optimized?
- [ ] Are denormalization opportunities considered?

**ORM Usage**:
- [ ] Is ORM used efficiently?
- [ ] Are raw SQL queries necessary?
- [ ] Is caching strategy appropriate?

---

## Recommendations Format

```markdown
## Important: N+1 Query Problem (Line 67)

**Category**: Database Performance
**Severity**: Important
**Current**: 1 + N queries (for 1000 users: 1001 queries)
**Optimized**: 2 queries (always 2, regardless of user count)

**Impact**: 50x-500x slower for large datasets, increased database load.

**Current Code**:
```python
users = User.objects.all()  # 1 query
for user in users:
    orders = user.orders.all()  # N queries!
```

**Fix** (Eager Loading):
```python
users = User.objects.prefetch_related('orders')  # 2 queries
for user in users:
    orders = user.orders.all()  # No query
```

**Alternative** (Aggregation):
```python
users = User.objects.annotate(order_count=Count('orders'))  # 1 query
for user in users:
    count = user.order_count  # No query
```

**Why**: `prefetch_related()` loads related objects in separate query, avoiding N+1 problem.

**Verification**: Enable Django query logging to confirm query count before/after.

**Resources**: See performance/database-performance.md for more patterns.
```

---

## Summary

**Common Database Smells**:
1. N+1 Query Problem - Queries in loop
2. Missing Indexes - Unindexed columns in WHERE
3. Select N+1 - Fetching too much data
4. Unnecessary Queries - Multiple queries that could be combined
5. Missing select_related() - Foreign key access without JOIN
6. Inefficient Filters - Functions in WHERE clause
7. Count Queries - COUNT(*) on large tables

**Optimization Patterns**:
- Eager loading (`prefetch_related()`, `select_related()`)
- Aggregation (`annotate()`, `Count()`)
- Batch operations (`bulk_create()`, `bulk_update()`)
- Query caching (cache lookups)
- Pagination (limit results)

**Detection**:
- Phase 1: Automated detection of queries in loops
- Phase 2: Manual review of query patterns

**Why Not Refactorable**:
- Requires database/ORM knowledge
- Not code structure - requires query strategy changes
- May require schema changes (indexes)

**Priority**: **Important** (causes severe performance degradation, high database load)

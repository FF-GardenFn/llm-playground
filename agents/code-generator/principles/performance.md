# Performance Consciousness Principle

## Core Idea
Consider 1000x/sec scenarios. Avoid O(n²) when O(n) exists. Profile before optimizing, but architect efficiently from start.

## Bad Example (Inefficient)

```python
def get_user_posts(user_ids):
    """Get all posts for given user IDs."""
    posts = []
    for user_id in user_ids:  # N queries (N+1 problem)
        user_posts = db.query(Post).filter(Post.user_id == user_id).all()
        posts.extend(user_posts)
    return posts
```

**Problems:**
- N+1 query problem (1 query per user)
- If 100 users → 100 database queries
- At 1000 requests/sec → 100,000 queries/sec
- Database becomes bottleneck

## Good Example (Efficient)

```python
def get_user_posts(user_ids):
    """Get all posts for given user IDs."""
    # Single query with IN clause
    return db.query(Post).filter(Post.user_id.in_(user_ids)).all()
```

**Better because:**
- Single database query
- 100 users → 1 query
- At 1000 requests/sec → 1,000 queries/sec (100x improvement)
- Scales linearly, not quadratically

## Another Example: Algorithm Choice

### Bad (O(n²))

```python
def find_duplicates(items):
    """Find duplicate items."""
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other and item not in duplicates:
                duplicates.append(item)
    return duplicates
```

**Problems:**
- Nested loops → O(n²)
- 1,000 items → 1,000,000 comparisons
- 10,000 items → 100,000,000 comparisons

### Good (O(n))

```python
def find_duplicates(items):
    """Find duplicate items."""
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**Better because:**
- Single loop → O(n)
- Set lookup → O(1)
- 1,000 items → 1,000 operations
- 10,000 items → 10,000 operations (not 100M)

## When to Apply

- During design (consider scale from start)
- When handling collections (avoid nested loops)
- When querying databases (batch queries, use indexes)
- When caching could help (compute once, reuse)
- When profiling shows bottleneck (measure, then optimize)

## When NOT to Optimize

- Premature optimization (profile first)
- Code that runs rarely (once per day)
- Small data (optimizing for 10 items wastes time)
- When it makes code complex (simple code often fast enough)

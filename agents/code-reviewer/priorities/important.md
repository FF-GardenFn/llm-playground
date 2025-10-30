# Important Priority Classification

**Purpose**: Define criteria for "Important" severity issues in code review.

**Phase**: Phase 4 (Priority Assessment)

**Priority**: Important (affects prioritization accuracy)

**Principle**: Important issues should be fixed soon but aren't urgent

---

## Overview

**Important** issues are those that:
- Should be addressed in the near future (next sprint/iteration)
- Have significant but not critical impact
- Don't pose immediate risk to production
- Improve code quality, performance, or maintainability
- Prevent technical debt accumulation

**Important vs Critical**:
- Critical: Must fix immediately (security, data loss, production outage)
- Important: Should fix soon (performance, maintainability, technical debt)

**Important vs Suggestion**:
- Important: Noticeable impact if not fixed (N+1 queries, missing tests)
- Suggestion: Nice to have (code style, minor refactorings)

---

## Classification Criteria

### 1. Performance Issues (Non-Critical)

**Criteria**:
- Noticeable performance degradation
- Doesn't cause immediate outage
- Affects user experience but not critically
- Scalability concerns

**Examples**:

**N+1 Query Problem**:
```markdown
## Important: N+1 Query in Order Listing

**Impact**: 101 queries for 100 orders (slow page loads, high database load)
**User Impact**: 2.5 second page load (annoying but not broken)
**Severity**: Important (should fix, but not production outage)

**Why Important (not Critical)**:
- Page still loads (not broken)
- Impact grows with data size
- Database load is high but manageable
- Will become critical if traffic increases
```

**Inefficient Algorithm**:
```markdown
## Important: O(n²) Algorithm in Search Results

**Impact**: Search becomes slow with > 1000 results
**User Impact**: 5 second search on large datasets
**Severity**: Important (should optimize, but works for now)

**Why Important (not Critical)**:
- Works fine for small/medium datasets
- Only problem with large datasets
- Not affecting most users yet
- Should optimize before it becomes critical
```

---

### 2. Testing Gaps

**Criteria**:
- Important code paths untested
- Not critical paths (not payment/security)
- Reduces confidence in changes
- Makes refactoring risky

**Examples**:

**Missing Tests for Core Logic**:
```markdown
## Important: No Tests for User Registration Flow

**Impact**: 200 lines of untested user registration code
**Risk**: Changes to registration could break without detection
**Severity**: Important (should add tests)

**Why Important (not Critical)**:
- Not financial/security code (not Critical)
- But core user functionality (not Suggestion)
- Increases risk of bugs
- Makes refactoring unsafe
```

**Low Test Coverage**:
```markdown
## Important: Test Coverage Below Target (62%)

**Target**: 80%+ for core business logic
**Current**: 62% (18% gap)
**Severity**: Important (should improve coverage)

**Why Important (not Critical)**:
- Not critically low (> 50%)
- But below team standards
- Indicates untested code paths
- Prevents confident refactoring
```

---

### 3. Architecture Issues

**Criteria**:
- Violates architectural patterns
- Increases technical debt
- Makes future changes harder
- Not causing immediate problems

**Examples**:

**Layering Violation**:
```markdown
## Important: View Directly Accessing Database

**Issue**: Controller/View bypasses service layer
**Impact**: Business logic scattered, hard to maintain
**Severity**: Important (architectural debt)

**Why Important (not Critical)**:
- Code works correctly (not broken)
- But violates architecture (harder to change)
- Accumulates technical debt
- Makes testing harder
```

**Tight Coupling**:
```markdown
## Important: Payment Service Tightly Coupled to Stripe

**Issue**: PaymentService hard-coded to Stripe API
**Impact**: Difficult to switch payment providers
**Severity**: Important (flexibility concern)

**Why Important (not Critical)**:
- Current provider works fine (no immediate issue)
- But switching providers would require major refactor
- Reduces flexibility
- Technical debt
```

---

### 4. Error Handling Gaps

**Criteria**:
- Missing error handling
- Not for critical operations
- Could cause poor user experience
- Not causing data loss

**Examples**:

**Missing Error Handling**:
```markdown
## Important: No Error Handling for Email Sending

**Issue**: Email sending failures silently ignored
**Impact**: Users don't receive confirmation emails
**Severity**: Important (user experience issue)

**Why Important (not Critical)**:
- Not financial/security operation (not Critical)
- But affects user experience
- Should log and retry failures
- Could lead to user confusion
```

**Generic Exception Handling**:
```markdown
## Important: Catching All Exceptions Without Logging

**Issue**: `except Exception: pass` hides all errors
**Impact**: Failures go unnoticed, hard to debug
**Severity**: Important (maintainability issue)

**Why Important (not Critical)**:
- Not causing immediate outage
- But makes debugging impossible
- Failures silently ignored
- Technical debt
```

---

### 5. Security Issues (Non-Critical)

**Criteria**:
- Security concern but not exploitable
- Low likelihood or low impact
- Should fix but not urgent

**Examples**:

**Weak Password Policy**:
```markdown
## Important: Weak Password Requirements

**Issue**: Passwords only require 6 characters
**Risk**: Users may choose weak passwords
**Severity**: Important (security improvement)

**Why Important (not Critical)**:
- Not directly exploitable vulnerability
- Depends on user behavior
- Should strengthen (8+ chars, complexity)
- Reduces risk but not urgent
```

**Missing Rate Limiting**:
```markdown
## Important: No Rate Limiting on API Endpoints

**Issue**: API endpoints have no rate limits
**Risk**: Potential for abuse or accidental DoS
**Severity**: Important (should add rate limiting)

**Why Important (not Critical)**:
- No active abuse happening
- But vulnerable to abuse
- Should add limits preemptively
- Defense in depth
```

---

### 6. Code Quality Issues

**Criteria**:
- Significant maintainability impact
- Not minor style issues
- Affects team productivity
- Accumulates technical debt

**Examples**:

**Large Class**:
```markdown
## Important: UserService Has 2000 Lines

**Issue**: UserService is too large (2000 lines, 40 methods)
**Impact**: Hard to understand, modify, test
**Severity**: Important (maintainability debt)

**Why Important (not Critical)**:
- Code works correctly
- But very hard to maintain
- High cognitive load
- Should refactor into smaller classes
```

**God Object**:
```markdown
## Important: ApplicationContext Knows Everything

**Issue**: ApplicationContext has dependencies on 20 modules
**Impact**: Changes to any module affect ApplicationContext
**Severity**: Important (coupling issue)

**Why Important (not Critical)**:
- System works correctly
- But tightly coupled
- Hard to test
- Should decouple
```

---

## When to Use "Important"

### Use "Important" When:

1. **Performance Impact** (but not outage):
   - Slow queries (N+1)
   - Inefficient algorithms
   - Memory leaks (small)
   - Scalability concerns

2. **Missing Tests** (not critical paths):
   - Core business logic untested
   - Coverage below standards
   - Integration tests missing

3. **Architecture Violations** (technical debt):
   - Layering violations
   - Tight coupling
   - God objects
   - Large classes

4. **Error Handling Gaps** (not critical ops):
   - Missing error handling
   - Silent failures
   - Generic exception catching

5. **Security Improvements** (not vulnerabilities):
   - Weak password policies
   - Missing rate limiting
   - Insufficient logging

6. **Maintainability Issues** (significant):
   - Large classes/methods
   - Complex conditionals
   - Duplicate code
   - Poor naming

### Don't Use "Important" When:

**Use "Critical" Instead**:
- Security vulnerabilities (SQL injection, XSS)
- Data loss risks
- Production outages
- Financial logic errors

**Use "Suggestion" Instead**:
- Minor code style issues
- Small refactorings
- Naming improvements
- Comment improvements

---

## Important Issue Format

```markdown
## Important: [Issue Title]

**Category**: [Performance/Testing/Architecture/Error Handling/Security/Code Quality]
**Severity**: Important
**Location**: [file:line]
**Refactorable**: [Yes/No]

### Description
[What's the issue]

### Impact
- **Current Impact**: [What's happening now]
- **Future Impact**: [What will happen if not fixed]
- **User Impact**: [How it affects users]
- **Team Impact**: [How it affects development]

### Current State
```[language]
[Code with issue]
```

### Recommended Fix
```[language]
[Improved code]
```

### Why This Matters
[Explanation of importance]

### Timeline
**Recommended**: Address in next sprint/iteration (not urgent)

### Resources
[Links to relevant documentation]
```

---

## Example: Important Issue

```markdown
## Important: N+1 Query in Order Listing

**Category**: Performance
**Severity**: Important
**Location**: src/views/orders.py:23
**Refactorable**: No (requires ORM optimization)

### Description
The order listing page executes 101 database queries for 100 orders (1 query to fetch orders + 100 queries to fetch items for each order), creating an N+1 query problem.

### Impact
- **Current Impact**: 2.5 second page load (slow but usable)
- **Future Impact**: Will scale linearly with order count (1000 orders = 10+ seconds)
- **User Impact**: Frustrating page loads, potential timeouts on large datasets
- **Team Impact**: Database load is high, may affect other queries
- **Database Load**: 101 queries vs 2 queries (5000% increase)

### Current State
```python
def get_orders(request):
    orders = Order.objects.all()  # 1 query
    for order in orders:
        # N additional queries (one per order)
        items = order.items.all()
    return render(request, 'orders.html', {'orders': orders})
```

**Query Log** (for 100 orders):
```sql
SELECT * FROM orders;                          -- 1 query
SELECT * FROM items WHERE order_id = 1;        -- Query 2
SELECT * FROM items WHERE order_id = 2;        -- Query 3
...
SELECT * FROM items WHERE order_id = 100;      -- Query 101
```

### Recommended Fix
```python
def get_orders(request):
    # Use prefetch_related for eager loading
    orders = Order.objects.prefetch_related('items').all()  # 2 queries total
    for order in orders:
        items = order.items.all()  # No additional queries
    return render(request, 'orders.html', {'orders': orders})
```

**Query Log** (for 100 orders):
```sql
SELECT * FROM orders;                          -- Query 1
SELECT * FROM items WHERE order_id IN (1,2,3,...,100);  -- Query 2
```

### Performance Improvement
- **Queries**: 101 → 2 (98% reduction)
- **Page Load**: 2.5s → 0.2s (12.5x faster)
- **Database Load**: Significantly reduced

### Why This Matters
**Not Critical** because:
- Page still loads (not broken)
- Affects performance, not correctness
- Impact is noticeable but not catastrophic

**Important** because:
- Significant performance impact (2.5s page load)
- Scales poorly (will get worse with more orders)
- High database load affects other operations
- Should fix before it becomes critical

### Timeline
**Recommended**: Fix in next sprint
**Urgency**: Should address soon (before traffic increases)
**Risk**: Will become critical if order volume grows

### Resources
- See `performance/database-performance.md` for N+1 query optimization
- [Django QuerySet Optimization](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Prefetch Related Documentation](https://docs.djangoproject.com/en/stable/ref/models/querysets/#prefetch-related)
```

---

## Priority Distribution

### Healthy Distribution

```
Total Issues: 100

Critical:   5 (5%)  ← Few, urgent
Important: 30 (30%) ← Moderate number, address soon
Suggestion: 65 (65%) ← Majority, nice to have
```

### Unhealthy Distributions

**Too Many Criticals** (poor code quality):
```
Critical:  40 (40%) ← Too many urgent issues
Important: 30 (30%)
Suggestion: 30 (30%)
```

**Too Many Suggestions** (over-nitpicking):
```
Critical:   2 (2%)
Important:  8 (8%)
Suggestion: 90 (90%) ← Too many minor issues
```

---

## Review Checklist

### Before Marking as "Important"

- [ ] Is this issue causing immediate production problems? (If yes → Critical)
- [ ] Is this a security vulnerability? (If yes → Critical)
- [ ] Is this a data loss risk? (If yes → Critical)
- [ ] Does this significantly impact performance/maintainability? (If yes → Important)
- [ ] Should this be fixed in next sprint? (If yes → Important)
- [ ] Is this a minor style/preference issue? (If yes → Suggestion)
- [ ] Is impact clearly explained?
- [ ] Is timeline recommendation provided?
- [ ] Is fix clearly described?

---

## Summary

**Important Priority**:
- Issues that should be fixed soon (next sprint)
- Significant but not critical impact
- Don't pose immediate risk
- Prevent technical debt accumulation

**Categories**:
1. Performance issues (N+1 queries, inefficient algorithms)
2. Testing gaps (missing tests, low coverage)
3. Architecture violations (layering, coupling)
4. Error handling gaps (missing handling, silent failures)
5. Security improvements (not vulnerabilities)
6. Code quality issues (large classes, complexity)

**Format**: Clear description, impact analysis, recommended fix, timeline

**Distribution**: ~30% of total issues should be Important

**Priority**: **Important** (affects prioritization accuracy)

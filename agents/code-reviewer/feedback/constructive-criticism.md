# Constructive Criticism Patterns

**Purpose**: Guide code-reviewer to provide feedback that helps, not discourages.

**Phase**: Phase 3 (Feedback Synthesis)

**Priority**: Important (affects developer experience and learning)

**Principle**: Be helpful, not harsh - focus on improvement, not blame

---

## Overview

Code review feedback should be:
- **Constructive**: Focus on what can be improved and how
- **Specific**: Provide concrete examples and solutions
- **Educational**: Explain the "why" behind recommendations
- **Positive**: Acknowledge good work, not just problems
- **Respectful**: Assume competence and good intentions

---

## Constructive Criticism Framework

### The "Sandwich" Pattern

**Structure**:
1. **Acknowledge**: Start with something positive or contextual
2. **Improve**: Identify the issue and suggest improvement
3. **Encourage**: End with support or positive outlook

**Example**:
```markdown
## Suggestion: Improve Input Validation

**Acknowledge**: The user registration flow is well-structured with clear separation of concerns.

**Improve**: The email validation could be strengthened to prevent invalid formats:

Current:
```python
if '@' in email:
    # Too simplistic
```

Recommended:
```python
import re
if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
    # More robust validation
```

**Encourage**: Adding comprehensive validation will make the registration more reliable and prevent edge cases down the line.
```

---

## Language Patterns

###  Avoid Harsh Language

```markdown
# BAD: Harsh, blaming tone
This code is terrible and shows you don't understand SQL injection.
You should never write code like this.
This is a serious security hole that could get the company hacked.

# GOOD: Constructive, educational tone
This code is vulnerable to SQL injection. Let me show you how to fix it:

Current approach uses string concatenation, which allows attackers to inject malicious SQL:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

Recommended approach uses parameterized queries, which safely escapes input:
```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

This prevents SQL injection by treating user input as data, not executable code.

**Resources**: See `security/input-validation.md` for more examples.
```

---

###  Use Positive Framing

```markdown
# BAD: Negative framing
You forgot to add tests.
There are no tests for this critical code.
How can you deploy without tests?

# GOOD: Positive framing
Adding tests for this payment processing logic would provide:
- Confidence that the code works correctly
- Safety net for future refactoring
- Documentation of expected behavior

Example tests to add:
```python
def test_process_payment_success():
    payment = process_payment(valid_card, amount=100)
    assert payment.status == 'success'

def test_process_payment_insufficient_funds():
    with pytest.raises(InsufficientFundsError):
        process_payment(empty_card, amount=100)
```

**Resources**: See `testing/test-types.md` for testing strategies.
```

---

###  Explain the "Why"

```markdown
# BAD: No explanation
Don't use mutable default arguments.

# GOOD: Explains the why
Avoid mutable default arguments because they're created once when the function is defined, not each time it's called. This can lead to unexpected behavior:

```python
#  Problem: Default list shared across calls
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # Returns [1]
add_item(2)  # Returns [1, 2] - UNEXPECTED! Same list!

#  Solution: Use None and create new list
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

add_item(1)  # Returns [1]
add_item(2)  # Returns [2] - Expected behavior
```

**Why this matters**: Shared mutable defaults cause hard-to-debug bugs where function behavior depends on previous calls.

**Resources**: [Python Common Gotchas](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
```

---

## Tone Guidelines

### 1. Assume Competence

```markdown
# BAD: Condescending tone
Even a beginner knows you shouldn't do this.
This is Programming 101.

# GOOD: Respectful tone
This pattern can lead to memory leaks. Here's a more memory-efficient approach:

Current:
```python
cache = {}  # Unbounded cache

def get_user(user_id):
    if user_id not in cache:
        cache[user_id] = db.get_user(user_id)
    return cache[user_id]
```

Recommended:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)  # Bounded cache
def get_user(user_id):
    return db.get_user(user_id)
```

**Why**: Unbounded caches grow indefinitely, potentially exhausting memory. `lru_cache` automatically evicts least-recently-used entries.
```

---

### 2. Use "We" Instead of "You"

```markdown
# BAD: Accusatory "you"
You didn't handle errors properly.
You need to fix this.

# GOOD: Collaborative "we"
We could improve error handling here to make debugging easier:

Current:
```python
try:
    process_payment(order)
except:
    pass  # Silent failure
```

Recommended:
```python
try:
    process_payment(order)
except PaymentError as e:
    logger.error(f"Payment failed for order {order.id}: {e}")
    raise  # Re-raise for upstream handling
```

This helps us track payment failures in logs and provides better error messages to users.
```

---

### 3. Suggest, Don't Command

```markdown
# BAD: Commanding tone
Fix this immediately.
You must change this.
Do this instead.

# GOOD: Suggesting tone
Consider using a context manager to ensure files are properly closed:

Current:
```python
file = open('data.txt')
data = file.read()
file.close()  # May not execute if read() raises exception
```

Recommended:
```python
with open('data.txt') as file:
    data = file.read()
# File automatically closed, even if exception occurs
```

This pattern ensures proper resource cleanup even when errors occur.
```

---

### 4. Focus on Code, Not Person

```markdown
# BAD: Personal criticism
You're not following best practices.
You don't understand async programming.

# GOOD: Code-focused feedback
This async function contains blocking I/O, which can degrade performance:

Current:
```python
async def get_user_data(user_id):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")  # Blocking!
    return user
```

The synchronous `db.query()` call blocks the event loop, preventing other async operations from running.

Recommended:
```python
async def get_user_data(user_id):
    user = await db.async_query("SELECT * FROM users WHERE id = %s", user_id)
    return user
```

Using `await` with async database calls allows the event loop to handle other tasks during I/O waits.

**Resources**: See `performance/concurrency.md` for async/await patterns.
```

---

## Feedback Templates

### Template 1: Security Issue

```markdown
## Critical: [Security Vulnerability Type]

**Context**: [Brief context about the functionality]

**Issue**: This code is vulnerable to [vulnerability type]. Here's how an attacker could exploit it:

**Attack Example**:
```python
# Attacker input
malicious_input = "[example of malicious input]"

# Results in
[explanation of what happens]
```

**Fix**: Use [secure pattern] to prevent this vulnerability:

**Before (Vulnerable)**:
```python
[current code]
```

**After (Secure)**:
```python
[fixed code]
```

**Why This Works**: [Explanation of why fix is secure]

**Impact**: Fixing this prevents [specific security risk] and protects [what is protected].

**Resources**:
- [OWASP link or internal doc]
- See `security/[relevant-doc].md`
```

---

### Template 2: Performance Issue

```markdown
## Important: [Performance Issue]

**Context**: [Where this code runs and how often]

**Current Behavior**:
- [Metric 1]: [current value]
- [Metric 2]: [current value]

**Issue**: [Explanation of performance problem]

**Current Code**:
```python
[code with performance issue]
```

**Bottleneck**: [Specific cause of slowness]

**Recommended Approach**:
```python
[optimized code]
```

**Performance Improvement**:
- [Metric 1]: [current] → [improved] ([X%] improvement)
- [Metric 2]: [current] → [improved] ([Y%] improvement)

**Trade-offs**: [Any trade-offs, if applicable]

**Resources**: See `performance/[relevant-doc].md`
```

---

### Template 3: Code Quality Suggestion

```markdown
## Suggestion: [Improvement Goal]

**Current Approach**: [Brief description of current code]

**Opportunity**: This code could be more [readable/maintainable/testable] by [specific improvement]:

**Current**:
```python
[current code]
```

**Characteristics**:
- [Metric 1]: [current value] (e.g., complexity: 12)
- [Metric 2]: [current value] (e.g., length: 60 lines)

**Recommended**:
```python
[improved code]
```

**Benefits**:
- [Benefit 1]: [specific improvement]
- [Benefit 2]: [specific improvement]
- [Benefit 3]: [specific improvement]

**Automated Refactoring**: This refactoring can be automated by refactoring-engineer.

**Estimated ROI**:
- Manual refactoring time: ~[X] minutes
- Automated refactoring time: ~[Y] minutes
- Complexity improvement: [current] → [improved]

Would you like me to invoke refactoring-engineer to perform this refactoring automatically?

**Resources**: See `quality/[relevant-doc].md`
```

---

### Template 4: Missing Tests

```markdown
## Important: Test Coverage Gap

**Context**: [Description of untested code]

**Current Coverage**: [X%] ([Y]/[Z] lines covered)

**Gap**: The following critical paths are untested:
1. [Specific path 1]
2. [Specific path 2]
3. [Specific path 3]

**Risk**: Without tests, we can't be confident that:
- [Risk 1]
- [Risk 2]
- [Risk 3]

**Recommended Tests**:

```python
def test_[scenario_1]():
    """Test [specific behavior]"""
    # Arrange
    [setup]

    # Act
    [action]

    # Assert
    [verification]

def test_[scenario_2]():
    """Test [specific edge case]"""
    [test code]
```

**Coverage Goal**: [X%] → [Y%] (add [Z] tests)

**Resources**:
- See `testing/test-types.md` for test strategy
- See `testing/coverage.md` for coverage targets
```

---

## Positive Feedback Patterns

### Pattern 1: Acknowledge Good Work

```markdown
##  Positive: Excellent Error Handling

**What's Done Well**:
Your error handling demonstrates several best practices:

1. **Specific Exceptions**:
```python
class InsufficientBalanceError(Exception):
    """Raised when account balance is insufficient"""
    pass

class PaymentGatewayError(Exception):
    """Raised when payment gateway is unavailable"""
    pass
```

2. **Meaningful Error Messages**:
```python
if account.balance < amount:
    raise InsufficientBalanceError(
        f"Account {account.id} has balance {account.balance}, "
        f"cannot withdraw {amount}"
    )
```

3. **Proper Exception Chaining**:
```python
try:
    charge_card(card, amount)
except GatewayError as e:
    raise PaymentGatewayError("Payment failed") from e
```

**Why This Matters**:
- Specific exceptions enable targeted error handling
- Detailed messages make debugging much easier
- Exception chaining preserves the full error context

**Keep It Up**: This level of error handling makes the codebase much more maintainable!
```

---

### Pattern 2: Reinforce Good Patterns

```markdown
##  Positive: Clean API Design

**What's Done Well**:
The REST API follows best practices consistently:

**1. Resource-Oriented URLs**:
```
GET    /api/users          # List users
POST   /api/users          # Create user
GET    /api/users/{id}     # Get user
PUT    /api/users/{id}     # Update user
DELETE /api/users/{id}     # Delete user
```

**2. Appropriate HTTP Methods**:
- GET for reads (idempotent)
- POST for creates
- PUT for full updates
- PATCH for partial updates
- DELETE for deletes

**3. Proper Status Codes**:
```python
@app.route('/users', methods=['POST'])
def create_user():
    user = User.create(request.json)
    return jsonify(user.to_dict()), 201  # Created

@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = User.get_or_404(id)
    return jsonify(user.to_dict()), 200  # OK
```

**Why This Matters**:
- RESTful design makes the API intuitive for clients
- Proper status codes enable better error handling
- Consistency across endpoints reduces surprises

**Excellent Work**: This API will be easy for frontend developers to consume!
```

---

## Common Mistakes to Avoid

### Mistake 1: Vague Feedback

```markdown
# BAD: Vague
This code needs improvement.
Fix the security issues.

# GOOD: Specific
This code is vulnerable to SQL injection on line 45. Replace string concatenation with parameterized queries:

Before:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

After:
```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```
```

---

### Mistake 2: Only Negative Feedback

```markdown
# BAD: All negative
Issue 1: SQL injection vulnerability
Issue 2: N+1 query problem
Issue 3: No tests
Issue 4: Poor variable names
[15 more issues...]

# GOOD: Balanced feedback
**Positive Highlights**:
- Excellent test coverage (95%)
- Clean separation of concerns
- Good error handling

**Areas for Improvement**:
Critical Issues (2):
1. SQL injection vulnerability (line 45)
2. N+1 query problem (line 78)

Important Issues (3):
[...]
```

---

### Mistake 3: No Actionable Steps

```markdown
# BAD: No guidance
Performance is poor.
Tests are inadequate.

# GOOD: Clear action steps
**Performance Issue**: N+1 query detected in order listing

**Action Steps**:
1. Add `prefetch_related('items')` to the order query
2. Remove the per-order item query
3. Run benchmark to verify improvement

**Expected Result**:
- Query count: 101 → 2 queries
- Page load: 2.5s → 0.2s

**Code Change**:
```python
# Before
orders = Order.objects.all()

# After
orders = Order.objects.prefetch_related('items').all()
```
```

---

### Mistake 4: Overwhelming Detail

```markdown
# BAD: Too much detail
This violates the Liskov Substitution Principle which is the L in SOLID which states that objects of a superclass should be replaceable with objects of a subclass without affecting the correctness of the program. In your case, the Square class inherits from Rectangle but violates LSP because when you set the width and height independently, the Square class overrides both setters to maintain the square invariant but this breaks code that expects a Rectangle to allow independent width and height changes. To fix this you could use composition instead of inheritance or redesign the hierarchy to have a Shape interface with separate Rectangle and Square implementations or use a factory pattern to create the appropriate shape type or consider making Square and Rectangle siblings under a common Quadrilateral interface...

# GOOD: Concise with link
This code violates the Liskov Substitution Principle - `Square` shouldn't inherit from `Rectangle` because it can't maintain Rectangle's behavior:

```python
# Problem: Square overrides Rectangle behavior
class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Breaks Rectangle contract!
```

**Recommended**: Use composition or separate hierarchies.

**Resources**: See `quality/solid-principles.md` for LSP examples.
```

---

## Review Checklist

### Tone & Language
- [ ] Is feedback constructive, not harsh?
- [ ] Is tone respectful and assumes competence?
- [ ] Are suggestions framed positively?
- [ ] Is "we" used instead of accusatory "you"?
- [ ] Is code criticized, not the person?

### Content Quality
- [ ] Is the "why" explained for each recommendation?
- [ ] Are specific code examples provided?
- [ ] Are actionable steps included?
- [ ] Are resources/links provided?
- [ ] Is impact/benefit clearly stated?

### Balance
- [ ] Is positive feedback included?
- [ ] Are good patterns acknowledged?
- [ ] Is feedback balanced (not all negative)?
- [ ] Is encouragement included?

### Clarity
- [ ] Is feedback specific, not vague?
- [ ] Is detail level appropriate (concise but complete)?
- [ ] Are technical terms explained?
- [ ] Is feedback easy to understand?

---

## Summary

**Constructive Criticism Framework**:
- **Acknowledge**: Start with context or positive note
- **Improve**: Identify issue and suggest fix
- **Encourage**: End with support or positive outlook

**Language Patterns**:
- Avoid harsh language → Use educational tone
- Use positive framing → Focus on benefits
- Explain the "why" → Help developers learn
- Assume competence → Respectful tone
- Use "we" not "you" → Collaborative approach
- Suggest, don't command → Respectful guidance
- Focus on code, not person → Objective feedback

**Templates**: Security, Performance, Code Quality, Testing, Positive Feedback

**Avoid**:
- Vague feedback (be specific)
- Only negative feedback (include positives)
- No actionable steps (provide clear guidance)
- Overwhelming detail (concise with links)

**Priority**: **Important** (affects developer experience and learning)

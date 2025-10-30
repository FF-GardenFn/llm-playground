# Suggestion Priority Classification

**Purpose**: Define criteria for "Suggestion" severity issues in code review.

**Phase**: Phase 4 (Priority Assessment)

**Priority**: Suggestion (affects feedback quality)

**Principle**: Suggestions are nice-to-have improvements, not requirements

---

## Overview

**Suggestion** issues are those that:
- Would improve code quality but aren't urgent
- Have minimal impact if not addressed
- Are often subjective or stylistic
- Don't affect functionality or security
- Nice to have, not need to have

**Suggestion vs Important**:
- Important: Noticeable impact if not fixed (N+1 queries, missing tests)
- Suggestion: Minimal impact (naming, minor refactorings, style)

**Suggestion vs Critical**:
- Critical: Must fix immediately (security, data loss)
- Suggestion: Optional improvement (code style, preferences)

---

## Classification Criteria

### 1. Code Style & Formatting

**Criteria**:
- Formatting inconsistencies
- Naming conventions
- Code organization
- Comment style

**Examples**:

**Naming Convention**:
```markdown
## Suggestion: Use snake_case for Variable Names

**Issue**: Variable uses camelCase instead of Python's snake_case convention

**Current**:
```python
userCount = 10  # camelCase (not Python convention)
```

**Recommended**:
```python
user_count = 10  # snake_case (Python convention)
```

**Impact**: Minimal (doesn't affect functionality)
**Why Suggestion**: Stylistic preference, low impact
```

**Inconsistent Formatting**:
```markdown
## Suggestion: Consistent Indentation

**Issue**: Mix of tabs and spaces for indentation

**Impact**: Minor (doesn't affect functionality)
**Why Suggestion**: Code readability improvement, not functional
```

---

### 2. Minor Refactorings

**Criteria**:
- Small code improvements
- Readability enhancements
- Not addressing significant smells
- Low complexity reduction

**Examples**:

**Extract Variable**:
```markdown
## Suggestion: Extract Variable for Readability

**Current**:
```python
if user.orders.filter(status='completed').count() > 10:
    apply_discount()
```

**Recommended**:
```python
completed_order_count = user.orders.filter(status='completed').count()
if completed_order_count > 10:
    apply_discount()
```

**Impact**: Slightly more readable
**Why Suggestion**: Minor readability improvement
```

**Rename Variable**:
```markdown
## Suggestion: Rename Variable for Clarity

**Current**:
```python
x = calculate_total(items)  # Unclear name
```

**Recommended**:
```python
order_total = calculate_total(items)  # Clear name
```

**Impact**: Minimal (doesn't change behavior)
**Why Suggestion**: Clarity improvement, low impact
```

---

### 3. Documentation & Comments

**Criteria**:
- Missing docstrings
- Unclear comments
- Documentation improvements
- Not critical for understanding

**Examples**:

**Missing Docstring**:
```markdown
## Suggestion: Add Docstring to Public Method

**Current**:
```python
def calculate_discount(total, rate):
    return total * (1 - rate)
```

**Recommended**:
```python
def calculate_discount(total, rate):
    """Calculate discounted total.

    Args:
        total: Order total before discount
        rate: Discount rate (0.0 to 1.0)

    Returns:
        Discounted total
    """
    return total * (1 - rate)
```

**Impact**: Improves documentation
**Why Suggestion**: Code is self-explanatory, docstring is nice to have
```

**Unclear Comment**:
```markdown
## Suggestion: Improve Comment Clarity

**Current**:
```python
# Fix it
user.status = 'active'
```

**Recommended**:
```python
# Activate user account after email verification
user.status = 'active'
```

**Impact**: Clearer intent
**Why Suggestion**: Comment improvement, not critical
```

---

### 4. Refactorable Code Smells (Non-Critical)

**Criteria**:
- Automated refactoring available
- Low-impact smells
- Readability improvements
- Not affecting maintainability significantly

**Examples**:

**Long Method (Not Severe)**:
```markdown
## Suggestion: Extract Method for Readability

**Smell**: long_method
**Refactorable**: Yes (Extract Method)

**Current**:
```python
def create_user(user_data):
    # 30 lines (below critical threshold of 50, but could be better)
    ...
```

**Impact**: Readability improvement
**Why Suggestion**: Method is long but manageable, refactoring is optional
**Automated Refactoring Available**: Yes
```

**Duplicate Code (Small)**:
```markdown
## Suggestion: Extract Common Validation

**Smell**: duplicate_code
**Refactorable**: Yes (Extract Method)

**Current**:
```python
# 5 lines duplicated in 2 places
if not email:
    raise ValidationError("Email required")
if '@' not in email:
    raise ValidationError("Invalid email")
```

**Impact**: Minor duplication
**Why Suggestion**: Small duplication, not critical to fix
**Automated Refactoring Available**: Yes
```

---

### 5. Optimization Opportunities (Low Impact)

**Criteria**:
- Micro-optimizations
- Negligible performance impact
- Premature optimization
- Not affecting user experience

**Examples**:

**List Comprehension vs Loop**:
```markdown
## Suggestion: Use List Comprehension

**Current**:
```python
result = []
for item in items:
    result.append(item.name)
```

**Recommended**:
```python
result = [item.name for item in items]
```

**Impact**: Slightly more concise, negligible performance difference
**Why Suggestion**: Stylistic preference, minimal impact
```

**Use f-strings**:
```markdown
## Suggestion: Use f-strings for String Formatting

**Current**:
```python
message = "Hello, {}".format(user.name)
```

**Recommended**:
```python
message = f"Hello, {user.name}"
```

**Impact**: More modern syntax, slightly more readable
**Why Suggestion**: Stylistic improvement, both work fine
```

---

### 6. Library/Framework Conventions

**Criteria**:
- Not following framework idioms
- Not using framework features
- Works but not idiomatic
- Low impact on functionality

**Examples**:

**Django ORM Idiom**:
```markdown
## Suggestion: Use Django ORM .exists() Method

**Current**:
```python
if len(User.objects.filter(email=email)) > 0:
    # User exists
```

**Recommended**:
```python
if User.objects.filter(email=email).exists():
    # More idiomatic and efficient
```

**Impact**: Slightly more idiomatic
**Why Suggestion**: Both work, recommended approach is more Pythonic
```

**Context Manager**:
```markdown
## Suggestion: Use Context Manager for File Handling

**Current**:
```python
file = open('data.txt')
data = file.read()
file.close()
```

**Recommended**:
```python
with open('data.txt') as file:
    data = file.read()
```

**Impact**: More Pythonic, ensures file closes
**Why Suggestion**: Original works in simple cases, context manager is better practice
```

---

## When to Use "Suggestion"

### Use "Suggestion" When:

1. **Code Style**:
   - Naming conventions
   - Formatting inconsistencies
   - Whitespace issues
   - Indentation style

2. **Minor Refactorings**:
   - Extract variable
   - Rename variable
   - Small method extractions
   - Simplify expressions

3. **Documentation**:
   - Missing docstrings
   - Unclear comments
   - TODOs and FIXMEs

4. **Refactorable Smells (Low Impact)**:
   - Small duplicate code blocks
   - Slightly long methods
   - Minor complexity

5. **Micro-Optimizations**:
   - List comprehensions
   - f-string usage
   - Generator expressions

6. **Framework Conventions**:
   - Idiomatic usage
   - Framework features
   - Best practices

### Don't Use "Suggestion" When:

**Use "Critical" Instead**:
- Security vulnerabilities
- Data loss risks
- Production outages
- Financial errors

**Use "Important" Instead**:
- N+1 query problems
- Missing tests
- Large classes
- Significant performance issues

---

## Suggestion Format

```markdown
## Suggestion: [Improvement Title]

**Category**: [Code Style/Refactoring/Documentation/Optimization]
**Severity**: Suggestion
**Location**: [file:line]
**Refactorable**: [Yes/No]

### Description
[What could be improved]

### Current Approach
```[language]
[Current code]
```

### Suggested Improvement
```[language]
[Improved code]
```

### Benefits
- [Benefit 1] (e.g., slightly more readable)
- [Benefit 2] (e.g., more idiomatic)

### Impact
**Functional Impact**: None (code works correctly as-is)
**Readability Impact**: [Minor/Moderate]
**Maintenance Impact**: [Minimal/Low]

### Priority
**Optional**: Address if time permits, not urgent

### Resources
[Links if helpful]
```

---

## Example: Suggestion Issue

```markdown
## Suggestion: Extract Variable for Complex Expression

**Category**: Code Style
**Severity**: Suggestion
**Location**: src/services/order_service.py:45
**Refactorable**: Yes (Extract Variable)

### Description
A complex expression for calculating the discount threshold could be more readable by extracting it to a named variable.

### Current Approach
```python
def apply_discount(order):
    if order.user.is_premium and order.total > 1000 and order.category in ['electronics', 'books']:
        return order.total * 0.9
    return order.total
```

### Suggested Improvement
```python
def apply_discount(order):
    is_eligible_for_discount = (
        order.user.is_premium
        and order.total > 1000
        and order.category in ['electronics', 'books']
    )

    if is_eligible_for_discount:
        return order.total * 0.9
    return order.total
```

### Benefits
- Slightly more readable (intent is clearer)
- Variable name documents the condition's purpose
- Easier to debug (can inspect `is_eligible_for_discount`)

### Impact
**Functional Impact**: None (behavior unchanged)
**Readability Impact**: Minor improvement (self-documenting code)
**Maintenance Impact**: Minimal (slightly easier to modify condition)

**Trade-off**: One extra line of code

### Priority
**Optional**: Nice to have, but current code is functional and clear enough

**Refactorable**: Can be automated via `extract_variable` refactoring

### Resources
- See `quality/clean-code.md` for readable code principles
- See `refactorings/extract-variable.md` for refactoring pattern
```

---

## Positive Framing for Suggestions

### ❌ Avoid Negative Framing

```markdown
# ❌ BAD: Sounds like a requirement
You must rename this variable.
This is wrong, fix it.
Don't use this pattern.
```

### ✅ Use Positive Framing

```markdown
# ✅ GOOD: Sounds like a suggestion
Consider renaming this variable for clarity:

Current:
```python
x = get_total()
```

Suggested:
```python
order_total = get_total()
```

This makes the purpose more explicit.

**Note**: This is a suggestion - the current code works fine, this is just a readability improvement.
```

---

## Suggestion Clusters

### Group Related Suggestions

```markdown
## Suggestions: Naming Improvements (5 instances)

**Category**: Code Style
**Severity**: Suggestion

Several variables could have more descriptive names:

1. **src/services/user_service.py:23**
   - Current: `x = user.orders.count()`
   - Suggested: `order_count = user.orders.count()`

2. **src/services/user_service.py:45**
   - Current: `data = fetch_user_data()`
   - Suggested: `user_profile_data = fetch_user_data()`

3. **src/utils/helpers.py:12**
   - Current: `result = calculate(a, b)`
   - Suggested: `total_price = calculate(base_price, tax_rate)`

[... 2 more instances ...]

**Impact**: Improved code readability throughout the codebase
**Priority**: Optional - address if time permits
**Refactorable**: Yes (Rename Variable) - can automate all 5 renames

Would you like me to invoke refactoring-engineer to rename all 5 variables automatically?
```

---

## Balancing Suggestions

### Don't Overwhelm with Suggestions

```markdown
# ❌ BAD: Too many minor suggestions (overwhelming)
Issue 1: Variable 'x' should be 'user_count'
Issue 2: Variable 'y' should be 'order_total'
Issue 3: Variable 'z' should be 'item_price'
[... 50 more naming suggestions ...]
Issue 53: Add space after comma on line 234

# ✅ GOOD: Group and prioritize
## Suggestions: Code Style Improvements

**Summary**: 15 minor code style improvements identified

**Top 3 Most Impactful**:
1. Rename unclear variables (5 instances)
2. Add docstrings to public methods (3 instances)
3. Use f-strings for string formatting (7 instances)

**Full List**: See attached detailed_suggestions.md

**Recommendation**: These are all optional improvements. If desired, automated refactoring can address most of these in ~5 minutes.
```

---

## Automated Refactoring for Suggestions

### Offer Batch Refactoring

```markdown
## 🤖 Automated Refactoring Available

**Refactorable Suggestions**: 12 opportunities

**Estimated Time**:
- Manual: ~2 hours (12 small refactorings × 10 minutes each)
- Automated: ~10 minutes (review and confirm)
- **Time Saved**: ~1 hour 50 minutes

**Refactorings**:
1. Rename 5 variables for clarity
2. Extract 3 variables from complex expressions
3. Convert 4 string formats to f-strings

**Would you like to proceed with automated refactoring?**

Options:
- `yes` - Proceed with all 12 refactorings
- `no` - Skip for now (these are optional)
- `review` - Show detailed plan

**Note**: All suggestions are optional. Code works correctly as-is.
```

---

## Review Checklist

### Before Marking as "Suggestion"

- [ ] Does this affect functionality? (If yes → not Suggestion)
- [ ] Is this a security concern? (If yes → Critical)
- [ ] Does this significantly impact performance? (If yes → Important)
- [ ] Are there missing tests? (If yes → Important)
- [ ] Is this purely stylistic/readability? (If yes → Suggestion)
- [ ] Is this a minor refactoring? (If yes → Suggestion)
- [ ] Is this a micro-optimization? (If yes → Suggestion)
- [ ] Would most developers agree this is optional? (If yes → Suggestion)
- [ ] Is tone constructive and non-demanding?
- [ ] Is impact clearly labeled as minimal?

---

## Suggestion Distribution

### Healthy Distribution

```
Total Issues: 100

Critical:    5 (5%)   ← Few, urgent
Important:  30 (30%)  ← Moderate, address soon
Suggestion: 65 (65%)  ← Majority, optional
```

**Note**: Suggestions should be the majority (60-70%) of issues.

### Unhealthy Distribution

**Too Few Suggestions** (missing opportunities):
```
Critical:   10 (20%)
Important:  40 (80%)
Suggestion:  0 (0%)   ← Missing optional improvements
```

**Too Many Suggestions** (nitpicking):
```
Critical:    2 (1%)
Important:   8 (4%)
Suggestion: 190 (95%) ← Overwhelming with minor issues
```

---

## Summary

**Suggestion Priority**:
- Nice to have, not need to have
- Optional improvements
- Minimal functional impact
- Address if time permits

**Categories**:
1. Code style & formatting
2. Minor refactorings
3. Documentation & comments
4. Low-impact refactorable smells
5. Micro-optimizations
6. Framework conventions

**Format**:
- Positive framing ("consider" not "must")
- Clear that it's optional
- Explain minimal impact

**Distribution**: 60-70% of total issues

**Tone**: Constructive, non-demanding, educational

**Priority**: **Suggestion** (optional improvements)

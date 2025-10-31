# Feedback Format & Presentation

**Purpose**: Standardize code review feedback format for clarity and actionability.

**Phase**: Phase 3 (Feedback Synthesis)

**Priority**: Important (affects communication effectiveness)

**Principle**: Clear, actionable, constructive feedback

---

## Overview

Code-reviewer feedback must be:
- **Clear**: Easy to understand
- **Actionable**: Specific steps to fix
- **Constructive**: Focus on improvement, not criticism
- **Prioritized**: Critical → Important → Suggestions
- **Consistent**: Standardized format

---

## Feedback Structure

### Standard Template

```markdown
# Code Review Report

**Project**: [Project Name]
**Review Date**: [YYYY-MM-DD]
**Reviewed By**: Code-Reviewer Agent
**Review Mode**: [Standalone / Trigger Refactoring / Verification]

---

## Executive Summary

**Overall Assessment**: [Excellent / Good / Needs Improvement / Critical Issues]

**Key Findings**:
- X critical security vulnerabilities
- Y important performance issues
- Z suggestions for code quality improvement

**Recommendations**:
1. [Top priority action]
2. [Second priority action]
3. [Third priority action]

---

## Critical Issues (Immediate Action Required)

[Critical findings in priority order]

---

## Important Issues (Should Address Soon)

[Important findings in priority order]

---

## Suggestions (Nice to Have)

[Suggestions for improvement]

---

## Refactorable Code Smells

[Automated refactoring opportunities]

---

## Positive Highlights

[Things done well - reinforcement]

---

## Next Steps

[Clear action plan]
```

---

## Issue Format

### Template for Each Issue

```markdown
## [Severity]: [Issue Title]

**Category**: [Security / Performance / Testing / Architecture / Code Quality]
**Severity**: [Critical / Important / Suggestion]
**Location**: [File path:line number]
**Refactorable**: [Yes / No]

### Description
[Clear explanation of the issue]

### Current Code
```[language]
[Problematic code snippet]
```

### Issue
[Specific problem with the current code]

### Recommendation
```[language]
[Improved code example]
```

### Impact
[Consequences if not fixed]

### Resources
[Links to documentation or guidelines]
```

---

## Example: Critical Issue

```markdown
## Critical: SQL Injection Vulnerability in User Search

**Category**: Security
**Severity**: Critical
**Location**: src/services/user_service.py:45
**Refactorable**: No (requires manual security fix)

### Description
The user search function constructs SQL queries using string concatenation with user input, making it vulnerable to SQL injection attacks.

### Current Code
```python
def search_users(search_term):
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    cursor.execute(query)
    return cursor.fetchall()
```

### Issue
An attacker can inject malicious SQL:
```python
search_term = "'; DROP TABLE users; --"
# Results in: SELECT * FROM users WHERE name LIKE '%'; DROP TABLE users; --%'
```

### Recommendation
Use parameterized queries:
```python
def search_users(search_term):
    query = "SELECT * FROM users WHERE name LIKE %s"
    cursor.execute(query, (f"%{search_term}%",))
    return cursor.fetchall()
```

### Impact
- **Security Risk**: Attackers can read, modify, or delete database data
- **Data Loss**: Entire database could be compromised
- **Compliance**: Violates OWASP Top 10 (A03:2021 - Injection)

### Resources
- [OWASP SQL Injection Prevention](https://owasp.org/www-community/attacks/SQL_Injection)
- See `security/input-validation.md` for SQL injection prevention
```

---

## Example: Important Issue

```markdown
## Important: N+1 Query in Order Listing

**Category**: Performance
**Severity**: Important
**Location**: src/views/orders.py:23
**Refactorable**: No (requires ORM query optimization)

### Description
The order listing view loads orders in one query, then makes N additional queries to load each order's items, creating an N+1 query problem.

### Current Code
```python
def get_orders():
    orders = Order.objects.all()  # 1 query
    for order in orders:
        items = order.items.all()  # N queries (one per order)
    return orders
```

### Issue
For 100 orders, this executes 101 queries (1 + 100), causing slow page loads.

### Recommendation
Use `prefetch_related()` for eager loading:
```python
def get_orders():
    orders = Order.objects.prefetch_related('items').all()  # 2 queries total
    for order in orders:
        items = order.items.all()  # No additional queries
    return orders
```

### Impact
- **Performance**: 101 queries → 2 queries (98% reduction)
- **Page Load Time**: 2.5s → 0.2s (12.5x faster)
- **Database Load**: Reduces database load significantly

### Resources
- See `performance/database-performance.md` for N+1 query optimization
- [Django QuerySet Optimization](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
```

---

## Example: Suggestion

```markdown
## Suggestion: Extract Method to Improve Readability

**Category**: Code Quality
**Severity**: Suggestion
**Location**: src/services/user_service.py:10-60
**Refactorable**: Yes (Extract Method)

### Description
The `create_user()` method is 60 lines long and handles multiple responsibilities: validation, normalization, creation, and email sending.

### Current Code
```python
def create_user(self, user_data):
    # 60 lines of code mixing:
    # - Email validation (10 lines)
    # - Name normalization (8 lines)
    # - User record creation (15 lines)
    # - Welcome email (12 lines)
    # - Error handling (15 lines)
```

### Issue
- **Complexity**: Cyclomatic complexity of 12 (high)
- **Readability**: Hard to understand at a glance
- **Maintainability**: Changes to one responsibility affect entire method
- **Testability**: Difficult to test individual responsibilities

### Recommendation
Extract into smaller, focused methods:
```python
def create_user(self, user_data):
    self._validate_email(user_data['email'])
    user_data['name'] = self._normalize_name(user_data['name'])
    user = self._create_user_record(user_data)
    self._send_welcome_email(user)
    return user

def _validate_email(self, email):
    # 10 lines of validation logic

def _normalize_name(self, name):
    # 8 lines of normalization logic

def _create_user_record(self, user_data):
    # 15 lines of creation logic

def _send_welcome_email(self, user):
    # 12 lines of email logic
```

### Impact
- **Readability**: Main method now self-documenting
- **Complexity**: Reduced from 12 → 3 per method
- **Maintainability**: Each method has single responsibility
- **Testability**: Easy to test each method independently

### Automated Refactoring Available
This refactoring can be automated by `refactoring-engineer`.

**Estimated ROI**:
- Time to refactor manually: ~30 minutes
- Time with automated refactoring: ~5 minutes
- Complexity reduction: 12 → 8 (33% improvement)

Would you like me to invoke refactoring-engineer to perform this refactoring automatically?

### Resources
- See `quality/clean-code.md` for method size guidelines
- See `smells/long-method.md` for long method detection
```

---

## Example: Refactorable Smell

```markdown
## Refactorable: Duplicate Code in Payment Processing

**Category**: Code Quality
**Severity**: Suggestion
**Location**: src/services/payment_service.py:45, 78, 112
**Refactorable**: Yes (Extract Method)

### Description
Payment validation logic is duplicated in 3 methods: `process_credit_card()`, `process_paypal()`, and `process_crypto()`.

### Current Code
```python
def process_credit_card(payment_data):
    # Duplicate validation (15 lines)
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    # ... 10 more lines of validation

def process_paypal(payment_data):
    # Same validation duplicated (15 lines)
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    # ... 10 more lines of validation

def process_crypto(payment_data):
    # Same validation duplicated again (15 lines)
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    # ... 10 more lines of validation
```

### Issue
- **Code Duplication**: 15 lines × 3 = 45 lines of duplicate code
- **Maintainability**: Changes require updating 3 locations
- **Bug Risk**: Easy to update one location and forget others

### Recommendation
Extract common validation:
```python
def _validate_payment_data(payment_data):
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    # ... remaining validation

def process_credit_card(payment_data):
    self._validate_payment_data(payment_data)
    # ... credit card specific logic

def process_paypal(payment_data):
    self._validate_payment_data(payment_data)
    # ... PayPal specific logic

def process_crypto(payment_data):
    self._validate_payment_data(payment_data)
    # ... crypto specific logic
```

### Impact
- **Code Reduction**: 45 lines → 15 lines (67% reduction)
- **Maintainability**: Single location to update validation
- **Consistency**: Guaranteed consistent validation across methods

### Automated Refactoring Available
This refactoring can be automated by `refactoring-engineer`.

**Estimated ROI**:
- Smell: `duplicate_code`
- Automated refactoring: `extract_method`
- Time to refactor manually: ~20 minutes
- Time with automated refactoring: ~3 minutes
- Code reduction: 67%

Would you like me to invoke refactoring-engineer to perform this refactoring automatically?

### Resources
- See `smells/duplicate-code.md` for duplicate code detection
- See `quality/clean-code.md` for DRY principle
```

---

## Example: Positive Highlight

```markdown
##  Positive: Excellent Test Coverage

**Category**: Testing
**Location**: tests/test_user_service.py

### What's Done Well
Your test suite demonstrates excellent testing practices:

1. **High Coverage**: 95% test coverage (Target: 80%+)
   - Critical paths: 100% covered
   - Core business logic: 98% covered
   - Utility functions: 92% covered

2. **Test Quality**: Tests follow FIRST principles
   - Fast: All tests < 10ms
   - Independent: No shared state
   - Repeatable: No flaky tests
   - Self-validating: Clear assertions
   - Timely: Tests written with code

3. **Good Test Organization**:
```python
# Clear test names
def test_create_user_with_valid_email_succeeds()
def test_create_user_with_invalid_email_raises_validation_error()
def test_create_user_with_duplicate_email_raises_integrity_error()

# Proper use of fixtures
@pytest.fixture
def valid_user_data():
    return {"name": "John Doe", "email": "john@example.com"}

# Clear arrange-act-assert structure
def test_create_user_sets_created_timestamp():
    # Arrange
    user_data = {"name": "John", "email": "john@example.com"}

    # Act
    user = create_user(user_data)

    # Assert
    assert user.created_at is not None
```

### Why This Matters
- **Confidence**: High test coverage provides confidence for refactoring
- **Maintainability**: Clear test names make tests self-documenting
- **Reliability**: Fast, independent tests enable frequent test runs

### Keep It Up!
Continue this level of testing discipline for new features.

### Resources
- See `testing/test-quality.md` for FIRST principles
- See `testing/coverage.md` for coverage targets
```

---

## Formatting Guidelines

### 1. Use Clear Headings

```markdown
## [Severity]: [Short, Descriptive Title]

#  GOOD
## Critical: SQL Injection in User Search
## Important: N+1 Query in Order Listing
## Suggestion: Extract Method for Readability

#  BAD
## Problem in user_service.py
## Issue #1
## Fix this
```

---

### 2. Provide Context

Always include:
- **File location**: `src/services/user_service.py:45`
- **Category**: Security, Performance, Testing, etc.
- **Severity**: Critical, Important, Suggestion
- **Refactorable**: Yes/No (if applicable)

---

### 3. Show Code Examples

Always include:
- **Current Code**: What exists now
- **Recommended Code**: What it should be
- **Clear diff markers**: Use  for bad,  for good

```markdown
### Current Code ()
```python
# Bad code here
```

### Recommended Code ()
```python
# Good code here
```
```

---

### 4. Explain Impact

Always include:
- **What breaks**: What could go wrong
- **Why it matters**: Business/technical impact
- **How to fix**: Clear actionable steps

---

### 5. Provide Resources

Always include:
- **Internal documentation**: Link to relevant guidelines
- **External resources**: OWASP, official docs, etc.
- **Related issues**: Links to similar findings

---

## Priority Order

### 1. Critical Issues First

```markdown
## Critical Issues (Address Immediately)

### Security Vulnerabilities
1. SQL Injection in User Search (src/services/user_service.py:45)
2. XSS in Comment Rendering (src/views/comments.py:23)

### Data Integrity
3. Missing Transaction in Money Transfer (src/services/payment.py:67)
```

---

### 2. Important Issues Second

```markdown
## Important Issues (Address Soon)

### Performance Problems
1. N+1 Query in Order Listing (src/views/orders.py:23)
2. Blocking I/O in Async Handler (src/handlers/upload.py:12)

### Testing Gaps
3. No Tests for Payment Processing (tests/test_payment.py - missing)
```

---

### 3. Suggestions Last

```markdown
## Suggestions (Nice to Have)

### Code Quality Improvements
1. Extract Method in UserService.create_user() (src/services/user_service.py:10)
2. Rename Variable 'x' to 'user_count' (src/utils/stats.py:45)

### Refactorable Code Smells
3. Duplicate Code in Payment Validation (3 occurrences)
```

---

## Summary Format

```markdown
## Summary

**Issues Found**: 15 total
- Critical: 3 (must fix immediately)
- Important: 5 (should fix soon)
- Suggestions: 7 (nice to have)

**Refactorable Smells**: 4 opportunities for automated refactoring
- Estimated time saved: ~2 hours with automation

**Positive Highlights**: 3
- Excellent test coverage (95%)
- Clean API design
- Good error handling

**Next Steps**:
1. Fix 3 critical security issues (highest priority)
2. Address 5 important performance/testing issues
3. Consider automated refactoring for 4 code smells
```

---

## Output Formats

### Console Output

```
╔════════════════════════════════════════════════════════════════╗
║                    CODE REVIEW REPORT                          ║
╚════════════════════════════════════════════════════════════════╝

Metrics: SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issues Found:  15 total
   Critical:      3 (address immediately)
   Important:     5 (address soon)
   Suggestions:   7 (nice to have)

Refactorable:  4 automated refactoring opportunities

 CRITICAL ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SQL Injection in User Search
   📁 src/services/user_service.py:45
   🔧 Fix: Use parameterized queries

2. XSS in Comment Rendering
   📁 src/views/comments.py:23
   🔧 Fix: Escape HTML output

[...]
```

### Markdown Output

Standard markdown format (shown in examples above)

### JSON Output

```json
{
  "review_id": "rev_2024_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "mode": "standalone",
  "summary": {
    "total_issues": 15,
    "critical": 3,
    "important": 5,
    "suggestions": 7,
    "refactorable": 4
  },
  "issues": [
    {
      "id": "issue_001",
      "severity": "critical",
      "category": "security",
      "title": "SQL Injection in User Search",
      "location": "src/services/user_service.py:45",
      "refactorable": false,
      "description": "...",
      "current_code": "...",
      "recommended_code": "...",
      "impact": "...",
      "resources": [...]
    }
  ],
  "positive_highlights": [...],
  "next_steps": [...]
}
```

---

## Review Checklist

### Feedback Quality

- [ ] Is feedback clear and easy to understand?
- [ ] Are all issues actionable (specific steps to fix)?
- [ ] Is tone constructive (focus on improvement)?
- [ ] Are issues prioritized (Critical → Important → Suggestion)?
- [ ] Are code examples provided for each issue?
- [ ] Is impact explained for each issue?
- [ ] Are resources/links provided?
- [ ] Are positive highlights included?

### Format Consistency

- [ ] Does each issue follow standard template?
- [ ] Are severity levels consistent?
- [ ] Are file locations specified (file:line)?
- [ ] Are refactorable smells marked?
- [ ] Is summary included at end?
- [ ] Are next steps clearly outlined?

---

## Summary

**Feedback Format**:
- **Structure**: Executive summary → Critical → Important → Suggestions → Highlights → Next steps
- **Issue Template**: Severity, category, location, description, code examples, impact, resources
- **Priority**: Critical first, then Important, then Suggestions
- **Tone**: Clear, actionable, constructive

**Key Principles**:
1. Clarity: Easy to understand
2. Actionability: Specific steps to fix
3. Constructiveness: Focus on improvement
4. Consistency: Standardized format
5. Context: File locations, severity, category

**Output Formats**: Console, Markdown, JSON

**Priority**: **Important** (affects communication effectiveness)

---

## Testing-Specific Output Template (From Commands)

```markdown
# Testing Review Report

**Review Date**: [Date]
**Reviewed By**: Code-Reviewer Agent (Testing Focus)

---

## Executive Summary

**Testing Status**: [Excellent / Good / Needs Improvement / Critical Gaps]

**Key Findings**:
- Test pyramid: [Healthy / Inverted / Missing layer]
- Coverage: [X]% overall ([Y]% critical code)
- Test quality: [FIRST principles score]
- Mocking strategy: [Appropriate / Over-mocking / Under-mocking]

---

## 1. Testing Pyramid

[Analysis from section 1]

---

## 2. Test Coverage

[Analysis from section 2]

---

## 3. Test Quality (FIRST)

[Analysis from section 3]

---

## 4. Mocking Strategy

[Analysis from section 4]

---

## 5. Test Smells

[Any test smells detected]

---

## Recommendations

### Critical (Must Fix)
1. [Critical gap 1]
2. [Critical gap 2]

### Important (Should Fix)
1. [Important gap 1]
2. [Important gap 2]

### Suggestions (Nice to Have)
1. [Suggestion 1]
2. [Suggestion 2]

---

## Positive Highlights

[Things done well in testing]

---

## Action Plan

1. **Immediate**: [Fix critical coverage gaps]
2. **Next Sprint**: [Address important issues]
3. **Long-term**: [Improve test quality]

---

## Resources

- Testing pyramid: `testing/test-types.md`
- Coverage targets: `testing/coverage.md`
- FIRST principles: `testing/test-quality.md`
- Mocking guidelines: `testing/mocking.md`
```

---

## Security-Specific Output Template (From Commands)

```markdown
# Security Review Report

**Review Date**: [Date]
**Reviewed By**: Code-Reviewer Agent (Security Focus)

---

## Executive Summary

**Security Status**: [CRITICAL ISSUES / NEEDS ATTENTION / GOOD]

**Critical Vulnerabilities**: [count]
**Important Vulnerabilities**: [count]
**Suggestions**: [count]

**OWASP Top 10 Coverage**:
- A01 (Access Control): [PASS/ISSUES]
- A02 (Cryptography): [PASS/ISSUES]
- A03 (Injection): [PASS/ISSUES]
- [... all 10 categories ...]

---

## Critical Vulnerabilities (Fix Immediately)

### 1. [Vulnerability Type] in [Component]

**OWASP Category**: A03:2021 - Injection
**Severity**: CRITICAL
**Location**: [file:line]
**Exploitability**: HIGH

**Vulnerable Code**:
```python
[code with vulnerability]
```

**Attack Scenario**:
```python
# Attacker input
malicious_input = "[attack payload]"

# Results in
[explanation of exploit]
```

**Fix**:
```python
[secure code]
```

**Impact**: [Description of what attacker can do]

**References**:
- [OWASP link]
- [CWE link]

---

## Important Vulnerabilities (Address Soon)

[Similar format for important issues]

---

## Security Suggestions (Best Practices)

[Security improvements that are nice to have]

---

## Compliance Assessment

**OWASP Top 10 (2021) Status**:
- A01: Broken Access Control - Compliant
- A02: Cryptographic Failures - Issues found
- A03: Injection - Partial compliance
- [... continue for all 10 ...]

**Overall Compliance**: [X/10 categories compliant]

---

## Positive Security Practices

[Things done well - security-wise]

---

## Recommended Actions

1. [Immediate action for critical issues]
2. [Next steps for important issues]
3. [Long-term security improvements]

---

## Resources

- OWASP Top 10 (2021): https://owasp.org/Top10/
- Security guidelines: `security/owasp-checklist.md`
- Input validation: `security/input-validation.md`
```

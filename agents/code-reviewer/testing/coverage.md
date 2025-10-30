# Test Coverage Assessment

**Purpose**: Evaluate test coverage adequacy and identify untested code paths during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (affects code reliability)

**Target**: Minimum 80% coverage for production code, 95%+ for critical paths

---

## Overview

Test coverage measures how much code is executed by tests. Code-reviewer assesses:
- **Line Coverage**: Percentage of lines executed
- **Branch Coverage**: Percentage of conditional branches taken
- **Critical Path Coverage**: 100% coverage for critical operations

---

## Coverage Metrics

### 1. Line Coverage

**Definition**: Percentage of code lines executed by tests.

**Measurement**:
```bash
# Python: pytest with coverage
pytest --cov=src --cov-report=html tests/

# Output:
# Name                 Stmts   Miss  Cover
# ----------------------------------------
# src/user_service.py    100     20    80%
# src/order_service.py   150     10    93%
# ----------------------------------------
# TOTAL                  250     30    88%
```

**Targets**:
- **Minimum**: 70% (basic coverage)
- **Good**: 80%+ (solid coverage)
- **Excellent**: 90%+ (comprehensive coverage)
- **Critical Code**: 100% (payment, security, data integrity)

**Example - Adequate Coverage**:
```python
# ✅ GOOD: 100% line coverage
def calculate_discount(total, discount_rate):
    """Calculate discounted total"""
    if total < 0:
        raise ValueError("Total must be non-negative")
    return total * (1 - discount_rate)

# Tests cover all lines
def test_calculate_discount():
    assert calculate_discount(100, 0.1) == 90  # Normal case
    assert calculate_discount(0, 0.1) == 0     # Zero total

def test_calculate_discount_negative():
    with pytest.raises(ValueError):
        calculate_discount(-100, 0.1)  # Error path
```

**Example - Inadequate Coverage**:
```python
# ❌ BAD: 50% line coverage (error path untested)
def calculate_discount(total, discount_rate):
    if total < 0:
        raise ValueError("Total must be non-negative")  # UNTESTED!
    return total * (1 - discount_rate)

# Only one test (doesn't cover error path)
def test_calculate_discount():
    assert calculate_discount(100, 0.1) == 90
```

**Detection Heuristics**:
- Coverage < 80%
- Critical code < 100%
- New code without tests

**Severity**: **Important**

---

### 2. Branch Coverage

**Definition**: Percentage of conditional branches taken by tests.

**Example - 100% Branch Coverage**:
```python
# ✅ GOOD: All branches tested
def get_user_discount(user):
    if user.is_premium:
        return 0.2  # Branch 1
    else:
        return 0.1  # Branch 2

# Tests cover both branches
def test_premium_user_discount():
    premium_user = User(is_premium=True)
    assert get_user_discount(premium_user) == 0.2  # Branch 1

def test_regular_user_discount():
    regular_user = User(is_premium=False)
    assert get_user_discount(regular_user) == 0.1  # Branch 2
```

**Example - Incomplete Branch Coverage**:
```python
# ❌ BAD: Only one branch tested (50% branch coverage)
def get_user_discount(user):
    if user.is_premium:
        return 0.2  # TESTED
    else:
        return 0.1  # UNTESTED!

# Only tests premium case
def test_premium_user_discount():
    premium_user = User(is_premium=True)
    assert get_user_discount(premium_user) == 0.2
```

**Detection Heuristics**:
- Branch coverage < line coverage
- Conditional logic without tests for both paths
- No tests for else/elif clauses

**Severity**: **Important**

---

### 3. Path Coverage (Critical Paths)

**Definition**: All execution paths through critical code are tested.

**Example - Critical Payment Path**:
```python
# ✅ GOOD: All payment paths tested
def process_payment(order):
    # Path 1: Insufficient balance
    if order.user.balance < order.total:
        raise InsufficientBalanceError()

    # Path 2: Payment gateway failure
    try:
        charge_card(order.user.card, order.total)
    except PaymentGatewayError:
        log_payment_failure(order)
        raise

    # Path 3: Success
    order.status = 'paid'
    order.save()
    return order

# Tests cover all 3 paths
def test_payment_insufficient_balance():
    # Path 1
    pass

def test_payment_gateway_failure():
    # Path 2
    pass

def test_payment_success():
    # Path 3
    pass
```

**Detection Heuristics**:
- Critical code (payment, security) without 100% coverage
- Complex functions with < 100% branch coverage
- Error paths untested

**Severity**: **Critical** (for critical paths)

---

## Coverage Assessment

### Adequate Coverage

**Example - Good Coverage**:
```
File: src/user_service.py
Coverage: 88%

Lines: 100 total, 12 untested
Branches: 95%

Untested lines:
- Line 45: Error handling for database connection failure
- Line 67: Fallback to default preferences
- Lines 120-130: Admin-only feature (rarely used)

Assessment: ✅ GOOD
- Core functionality: 100% covered
- Critical paths: 100% covered
- Untested code: Low-risk edge cases
```

### Inadequate Coverage

**Example - Poor Coverage**:
```
File: src/payment_service.py
Coverage: 62%

Lines: 150 total, 57 untested
Branches: 55%

Untested lines:
- Lines 23-40: Payment processing logic (CRITICAL!)
- Lines 50-65: Refund handling
- Lines 80-95: Error recovery

Assessment: ❌ INADEQUATE
- Critical payment logic untested
- Error paths not covered
- Refund logic not verified
```

---

## Coverage Targets by Code Category

### Critical Code (100% Required)

**What qualifies as critical**:
- **Financial**: Payment processing, refunds, billing
- **Security**: Authentication, authorization, encryption
- **Data Integrity**: Transaction management, database constraints
- **Legal**: Compliance, audit logging

**Example**:
```python
# CRITICAL: Must have 100% coverage
def charge_credit_card(card, amount):
    """Process credit card payment"""
    # Every line must be tested
    validate_card(card)
    validate_amount(amount)
    response = payment_gateway.charge(card, amount)
    log_transaction(card, amount, response)
    return response

# All paths tested
def test_charge_valid_card(): pass
def test_charge_invalid_card(): pass
def test_charge_gateway_failure(): pass
def test_charge_network_timeout(): pass
```

**Target**: **100% line + branch coverage**

---

### Core Business Logic (90%+ Target)

**What qualifies**:
- Order processing
- User management
- Core workflows
- Business rule validation

**Example**:
```python
# CORE: Should have 90%+ coverage
def create_order(user, items):
    """Create new order"""
    validate_user(user)
    validate_items(items)
    order = Order.objects.create(user=user, items=items)
    calculate_total(order)
    return order

# Most paths tested (some edge cases acceptable)
def test_create_order_success(): pass
def test_create_order_invalid_user(): pass
def test_create_order_invalid_items(): pass
# OK to skip: obscure edge case with 0.001% occurrence
```

**Target**: **90%+ coverage**

---

### Utility Code (80%+ Target)

**What qualifies**:
- Helper functions
- Formatters
- Validators
- Utilities

**Example**:
```python
# UTILITY: Should have 80%+ coverage
def format_phone_number(phone):
    """Format phone number"""
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

# Main cases tested (some variations acceptable)
def test_format_10_digits(): pass
def test_format_with_dashes(): pass
# OK to skip: international formats (low priority)
```

**Target**: **80%+ coverage**

---

### UI/Controllers (70%+ Target)

**What qualifies**:
- Controllers/views
- Request handlers
- Response formatters

**Example**:
```python
# UI: Should have 70%+ coverage
@app.route('/users/<int:id>')
def get_user(id):
    """Get user by ID"""
    user = user_service.get_user(id)
    return jsonify(user.to_dict())

# Basic paths tested
def test_get_user_exists(): pass
def test_get_user_not_found(): pass
# OK to skip: response header variations
```

**Target**: **70%+ coverage**

---

## Identifying Coverage Gaps

### Gap Analysis

```python
# coverage_gap_analysis.py

def identify_untested_code():
    """Identify untested code and assess risk"""

    gaps = []

    # Load coverage report
    coverage_data = load_coverage_report()

    for file, data in coverage_data.items():
        untested_lines = data['missing_lines']

        for line in untested_lines:
            risk = assess_risk(file, line)

            if risk == 'critical':
                gaps.append({
                    'file': file,
                    'line': line,
                    'risk': 'critical',
                    'recommendation': 'Must add tests immediately'
                })
            elif risk == 'important':
                gaps.append({
                    'file': file,
                    'line': line,
                    'risk': 'important',
                    'recommendation': 'Add tests in next sprint'
                })

    return gaps

def assess_risk(file, line):
    """Assess risk of untested code"""
    code = get_code_at_line(file, line)

    # Critical patterns
    if 'payment' in code.lower() or 'charge' in code.lower():
        return 'critical'
    if 'authenticate' in code.lower() or 'authorize' in code.lower():
        return 'critical'

    # Important patterns
    if 'save()' in code or 'delete()' in code:
        return 'important'
    if 'raise' in code:  # Error handling
        return 'important'

    return 'low'
```

---

## Review Checklist

### Phase 2: Manual Review

**Overall Coverage**:
- [ ] Is overall coverage ≥ 80%?
- [ ] Is coverage trend improving (not decreasing)?
- [ ] Are new features fully tested?

**Critical Path Coverage**:
- [ ] Is critical code (payment, security) 100% covered?
- [ ] Are error paths tested?
- [ ] Are edge cases covered?

**Branch Coverage**:
- [ ] Is branch coverage close to line coverage?
- [ ] Are all conditional branches tested?
- [ ] Are else clauses tested?

**Gap Analysis**:
- [ ] Are untested lines identified?
- [ ] Is risk assessed for each gap?
- [ ] Is plan to address gaps defined?

---

## Recommendations Format

```markdown
## Important: Insufficient Test Coverage (payment_service.py)

**Category**: Testing
**Severity**: Important
**Current Coverage**: 62% (Target: 100% for payment code)

**Impact**: Critical payment logic untested, high risk of bugs in production.

**Untested Code**:
- Lines 23-40: Payment processing (CRITICAL)
- Lines 50-65: Refund handling
- Lines 80-95: Error recovery

**Recommendation**:
Add tests for untested paths:

```python
# Test payment processing
def test_process_payment_success(): pass
def test_process_payment_insufficient_balance(): pass
def test_process_payment_gateway_failure(): pass

# Test refund handling
def test_refund_successful_payment(): pass
def test_refund_already_refunded(): pass

# Test error recovery
def test_payment_retry_on_network_error(): pass
```

**Target**: 100% coverage for payment_service.py (critical code)

**Resources**: See testing/coverage.md for coverage targets.
```

---

## Summary

**Coverage Targets**:
- **Critical Code**: 100% (payment, security, data integrity)
- **Core Logic**: 90%+ (business rules, workflows)
- **Utility Code**: 80%+ (helpers, formatters)
- **UI/Controllers**: 70%+ (request handlers)

**Coverage Metrics**:
- **Line Coverage**: % of lines executed
- **Branch Coverage**: % of branches taken
- **Path Coverage**: All critical paths tested

**Gap Analysis**:
- Identify untested code
- Assess risk (critical, important, low)
- Prioritize adding tests

**Detection**:
- Phase 2: Review coverage reports
- Identify gaps in critical code
- Assess risk of untested paths

**Priority**: **Important** (Critical for payment/security code)

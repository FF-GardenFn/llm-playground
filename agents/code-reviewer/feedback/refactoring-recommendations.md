# Refactoring Recommendations

**Purpose**: Templates for recommending automated refactorings to users.

**Phase**: Phase 4 (Priority Assessment) → Phase 5 (Recommendations)

**Priority**: Important (enables automated code improvement)

**Context**: When code-reviewer detects refactorable smells, it offers automated refactoring via refactoring-engineer

---

## Overview

When code-reviewer detects smells that can be automatically refactored, it:
1. **Identifies** the refactorable smell
2. **Assesses** the refactoring ROI (time saved, complexity reduction)
3. **Recommends** automated refactoring
4. **Offers** to invoke refactoring-engineer
5. **Awaits** user confirmation

This document provides templates for these recommendations.

---

## Refactoring Recommendation Template

### Standard Format

```markdown
## Refactorable: [Smell Name] - [Brief Description]

**Category**: Code Quality
**Severity**: Suggestion
**Location**: [file:line]
**Refactorable**: ✅ Yes ([refactoring_type])

### Description
[Clear explanation of the smell]

### Current Code
```[language]
[Code with smell]
```

### Issue
[Why this is a problem]

### Recommended Refactoring
**Type**: [refactoring_type]
**Automation**: Available via refactoring-engineer

```[language]
[Code after refactoring]
```

### Benefits
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

### ROI Estimate
- **Smell**: `[smell_name]`
- **Refactoring**: `[refactoring_type]`
- **Manual Time**: ~[X] minutes
- **Automated Time**: ~[Y] minutes
- **Time Saved**: ~[X-Y] minutes
- **Complexity Reduction**: [before] → [after] ([Z%] improvement)

### Automated Refactoring Offer
Would you like me to invoke `refactoring-engineer` to perform this refactoring automatically?

**What will happen**:
1. Code-reviewer invokes refactoring-engineer with smell details
2. Refactoring-engineer performs automated refactoring
3. Refactoring-engineer returns results to code-reviewer for verification
4. Code-reviewer verifies refactoring is safe (no regressions)
5. If safe, changes are ready to commit

**User Response Required**: [Yes/No/Review Later]

### Resources
- See `smells/[smell].md` for detection criteria
- See `quality/[relevant].md` for principles
```

---

## Example 1: Long Method

```markdown
## Refactorable: Long Method in UserService.create_user()

**Category**: Code Quality
**Severity**: Suggestion
**Location**: src/services/user_service.py:10-70
**Refactorable**: ✅ Yes (Extract Method)

### Description
The `create_user()` method is 60 lines long and handles multiple responsibilities: email validation, name normalization, user creation, and welcome email sending.

### Current Code
```python
def create_user(self, user_data):
    # Email validation (10 lines)
    email = user_data.get('email')
    if not email:
        raise ValidationError("Email required")
    if '@' not in email:
        raise ValidationError("Invalid email")
    # ... 8 more lines of validation

    # Name normalization (8 lines)
    name = user_data.get('name', '').strip()
    if not name:
        raise ValidationError("Name required")
    name = ' '.join(word.capitalize() for word in name.split())
    # ... 5 more lines

    # User creation (15 lines)
    user = User()
    user.email = email
    user.name = name
    # ... 12 more lines

    # Welcome email (12 lines)
    subject = "Welcome to our platform"
    body = f"Hello {user.name}, welcome to our platform!"
    # ... 10 more lines
    send_email(user.email, subject, body)

    return user
```

### Issue
**Complexity**: Cyclomatic complexity of 12 (high)
**Readability**: Hard to understand at a glance
**Maintainability**: Changes to one responsibility affect entire method
**Testability**: Difficult to test individual responsibilities
**SRP Violation**: Method has 4 distinct responsibilities

### Recommended Refactoring
**Type**: `extract_method`
**Automation**: Available via refactoring-engineer

```python
def create_user(self, user_data):
    """Create a new user with validation and welcome email."""
    email = self._validate_email(user_data.get('email'))
    name = self._normalize_name(user_data.get('name'))
    user = self._create_user_record(email, name, user_data)
    self._send_welcome_email(user)
    return user

def _validate_email(self, email):
    """Validate email format and existence."""
    if not email:
        raise ValidationError("Email required")
    if '@' not in email:
        raise ValidationError("Invalid email")
    # ... validation logic
    return email

def _normalize_name(self, name):
    """Normalize and validate user name."""
    name = (name or '').strip()
    if not name:
        raise ValidationError("Name required")
    return ' '.join(word.capitalize() for word in name.split())

def _create_user_record(self, email, name, user_data):
    """Create user database record."""
    user = User()
    user.email = email
    user.name = name
    # ... creation logic
    return user

def _send_welcome_email(self, user):
    """Send welcome email to new user."""
    subject = "Welcome to our platform"
    body = f"Hello {user.name}, welcome to our platform!"
    send_email(user.email, subject, body)
```

### Benefits
- **Readability**: Main method now self-documenting (4 clear steps)
- **Complexity**: Reduced from 12 → 3 per method (75% reduction)
- **Testability**: Each method can be tested independently
- **Maintainability**: Changes to validation don't affect email sending
- **Reusability**: Extracted methods can be reused elsewhere

### ROI Estimate
- **Smell**: `long_method`
- **Refactoring**: `extract_method`
- **Manual Time**: ~30 minutes (identify responsibilities, extract, update tests)
- **Automated Time**: ~5 minutes (review and confirm)
- **Time Saved**: ~25 minutes
- **Complexity Reduction**: 12 → 3 per method (75% improvement)
- **Lines per Method**: 60 → 15, 10, 8, 15, 12 (all under 20 line threshold)

### Automated Refactoring Offer
Would you like me to invoke `refactoring-engineer` to perform this refactoring automatically?

**What will happen**:
1. **Analysis**: Refactoring-engineer analyzes `create_user()` for responsibility boundaries
2. **Extraction**: Automatically extracts 4 methods based on cohesion analysis
3. **Testing**: Verifies all existing tests still pass
4. **Verification**: Code-reviewer validates no behavior changes
5. **Result**: Refactored code ready for review and commit

**Safety**: Refactoring-engineer will verify that:
- All tests still pass (25/25 tests)
- Test coverage maintained (88% → 88%)
- No behavior changes
- No security regressions
- No performance degradation

**User Response Required**:
- Type `yes` to proceed with automated refactoring
- Type `no` to skip for now
- Type `review` to see detailed refactoring plan first

### Resources
- See `smells/long-method.md` for long method detection
- See `refactorings/extract-method.md` for refactoring details
- See `quality/clean-code.md` for method size guidelines
```

---

## Example 2: Duplicate Code

```markdown
## Refactorable: Duplicate Code in Payment Processing

**Category**: Code Quality
**Severity**: Suggestion
**Location**: src/services/payment_service.py:45, 78, 112
**Refactorable**: ✅ Yes (Extract Method)

### Description
Payment validation logic is duplicated in 3 methods: `process_credit_card()`, `process_paypal()`, and `process_crypto()`. The same 15-line validation block appears in all three.

### Current Code
```python
def process_credit_card(self, payment_data):
    # Duplicate validation (15 lines)
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    if payment_data['amount'] > 10000:
        raise ValidationError("Amount exceeds limit")
    # ... 12 more lines of duplicate validation

    # Credit card specific logic
    charge_credit_card(payment_data)

def process_paypal(self, payment_data):
    # Same validation duplicated (15 lines)
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    if payment_data['amount'] > 10000:
        raise ValidationError("Amount exceeds limit")
    # ... 12 more lines of duplicate validation

    # PayPal specific logic
    charge_paypal(payment_data)

def process_crypto(self, payment_data):
    # Same validation duplicated again (15 lines)
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    if payment_data['amount'] > 10000:
        raise ValidationError("Amount exceeds limit")
    # ... 12 more lines of duplicate validation

    # Crypto specific logic
    charge_crypto(payment_data)
```

### Issue
**Code Duplication**: 15 lines × 3 = 45 lines of duplicate code
**Maintainability**: Bug fixes require updating 3 locations
**Inconsistency Risk**: Easy to update one location and forget others
**DRY Violation**: Clear violation of "Don't Repeat Yourself"

### Recommended Refactoring
**Type**: `extract_method`
**Automation**: Available via refactoring-engineer

```python
def _validate_payment_data(self, payment_data):
    """Validate common payment data fields."""
    if not payment_data.get('amount'):
        raise ValidationError("Amount required")
    if payment_data['amount'] <= 0:
        raise ValidationError("Amount must be positive")
    if payment_data['amount'] > 10000:
        raise ValidationError("Amount exceeds limit")
    # ... remaining validation (12 lines)

def process_credit_card(self, payment_data):
    self._validate_payment_data(payment_data)
    charge_credit_card(payment_data)

def process_paypal(self, payment_data):
    self._validate_payment_data(payment_data)
    charge_paypal(payment_data)

def process_crypto(self, payment_data):
    self._validate_payment_data(payment_data)
    charge_crypto(payment_data)
```

### Benefits
- **Code Reduction**: 45 lines → 15 lines (67% reduction)
- **Maintainability**: Single location to update validation
- **Consistency**: Guaranteed consistent validation across methods
- **DRY Compliance**: Eliminates code duplication
- **Testing**: Test validation once instead of three times

### ROI Estimate
- **Smell**: `duplicate_code`
- **Refactoring**: `extract_method`
- **Duplication**: 3 occurrences × 15 lines = 45 duplicate lines
- **Manual Time**: ~20 minutes (identify duplicates, extract, update tests)
- **Automated Time**: ~3 minutes (review and confirm)
- **Time Saved**: ~17 minutes
- **Code Reduction**: 67% (45 lines → 15 lines)

### Automated Refactoring Offer
Would you like me to invoke `refactoring-engineer` to perform this refactoring automatically?

**What will happen**:
1. **Detection**: Refactoring-engineer identifies duplicate code blocks
2. **Extraction**: Creates `_validate_payment_data()` with common logic
3. **Replacement**: Replaces 3 duplicates with single method call
4. **Verification**: Code-reviewer validates behavior preservation
5. **Result**: DRY-compliant code ready to commit

**Safety Guarantees**:
- All payment tests still pass
- Validation logic unchanged (just moved)
- No behavior differences
- Test coverage maintained

**User Response Required**: [Yes/No/Review]

### Resources
- See `smells/duplicate-code.md` for duplicate detection
- See `quality/clean-code.md` for DRY principle
```

---

## Example 3: Complex Conditional

```markdown
## Refactorable: Complex Conditional in Order Pricing

**Category**: Code Quality
**Severity**: Suggestion
**Location**: src/services/order_service.py:34-56
**Refactorable**: ✅ Yes (Replace Conditional with Polymorphism or Extract Method)

### Description
The `calculate_price()` method has nested conditionals with 8 different pricing rules, making it hard to understand and maintain.

### Current Code
```python
def calculate_price(self, order):
    if order.user.is_premium:
        if order.total > 1000:
            if order.category == 'electronics':
                discount = 0.25
            elif order.category == 'books':
                discount = 0.15
            else:
                discount = 0.20
        else:
            if order.category == 'electronics':
                discount = 0.15
            elif order.category == 'books':
                discount = 0.10
            else:
                discount = 0.12
    else:
        if order.total > 1000:
            discount = 0.10
        else:
            discount = 0.05

    return order.total * (1 - discount)
```

### Issue
**Complexity**: Cyclomatic complexity of 8 (high)
**Readability**: Nested conditionals hard to follow
**Maintainability**: Adding new rules requires modifying complex logic
**Testability**: Requires 8 test cases to cover all branches

### Recommended Refactoring
**Type**: `extract_method` + `replace_conditional_with_polymorphism`
**Automation**: Available via refactoring-engineer

**Option 1: Extract Method (Simpler)**
```python
def calculate_price(self, order):
    discount = self._calculate_discount(order)
    return order.total * (1 - discount)

def _calculate_discount(self, order):
    """Calculate discount based on user type, order total, and category."""
    if order.user.is_premium:
        return self._calculate_premium_discount(order)
    else:
        return self._calculate_regular_discount(order)

def _calculate_premium_discount(self, order):
    """Calculate discount for premium users."""
    if order.total > 1000:
        return self._get_large_order_premium_discount(order.category)
    else:
        return self._get_small_order_premium_discount(order.category)

def _calculate_regular_discount(self, order):
    """Calculate discount for regular users."""
    return 0.10 if order.total > 1000 else 0.05

def _get_large_order_premium_discount(self, category):
    """Get discount for large premium orders by category."""
    discounts = {'electronics': 0.25, 'books': 0.15}
    return discounts.get(category, 0.20)

def _get_small_order_premium_discount(self, category):
    """Get discount for small premium orders by category."""
    discounts = {'electronics': 0.15, 'books': 0.10}
    return discounts.get(category, 0.12)
```

**Option 2: Replace Conditional with Polymorphism (More Robust)**
```python
# Strategy pattern for discount calculation
class DiscountStrategy:
    def calculate(self, order):
        raise NotImplementedError

class PremiumLargeOrderDiscount(DiscountStrategy):
    DISCOUNTS = {'electronics': 0.25, 'books': 0.15, 'default': 0.20}

    def calculate(self, order):
        return self.DISCOUNTS.get(order.category, self.DISCOUNTS['default'])

class PremiumSmallOrderDiscount(DiscountStrategy):
    DISCOUNTS = {'electronics': 0.15, 'books': 0.10, 'default': 0.12}

    def calculate(self, order):
        return self.DISCOUNTS.get(order.category, self.DISCOUNTS['default'])

class RegularDiscount(DiscountStrategy):
    def calculate(self, order):
        return 0.10 if order.total > 1000 else 0.05

def calculate_price(self, order):
    strategy = self._get_discount_strategy(order)
    discount = strategy.calculate(order)
    return order.total * (1 - discount)

def _get_discount_strategy(self, order):
    if order.user.is_premium:
        if order.total > 1000:
            return PremiumLargeOrderDiscount()
        else:
            return PremiumSmallOrderDiscount()
    else:
        return RegularDiscount()
```

### Benefits
**Option 1 (Extract Method)**:
- **Complexity**: 8 → 2-3 per method (62-75% reduction)
- **Readability**: Clear method names document logic
- **Testability**: Each method testable independently

**Option 2 (Polymorphism)**:
- **Extensibility**: Easy to add new discount strategies
- **Open/Closed**: Add strategies without modifying existing code
- **Testability**: Each strategy independently testable
- **Maintainability**: Discount rules isolated in strategy classes

### ROI Estimate
- **Smell**: `complex_conditional`
- **Refactoring**: `extract_method` (Option 1) or `replace_conditional_with_polymorphism` (Option 2)
- **Manual Time**: ~25 minutes (Option 1) or ~40 minutes (Option 2)
- **Automated Time**: ~5 minutes (review and confirm)
- **Time Saved**: ~20-35 minutes
- **Complexity Reduction**: 8 → 2-3 per method (62-75% improvement)

### Automated Refactoring Offer
Would you like me to invoke `refactoring-engineer` to perform this refactoring automatically?

**Choose Refactoring Approach**:
1. **Extract Method** (Simpler, faster) - Recommended for quick improvement
2. **Replace Conditional with Polymorphism** (More robust) - Recommended for extensibility

**What will happen**:
1. **Analysis**: Refactoring-engineer analyzes conditional structure
2. **Refactoring**: Applies chosen refactoring pattern
3. **Testing**: Verifies all 8 conditional branches still work
4. **Verification**: Code-reviewer validates behavior preservation
5. **Result**: Refactored code ready to commit

**User Response Required**:
- Type `yes option1` for Extract Method (faster)
- Type `yes option2` for Polymorphism (more extensible)
- Type `no` to skip
- Type `review` for detailed plan

### Resources
- See `smells/complex-conditional.md` for complex conditional detection
- See `refactorings/extract-method.md` for extract method pattern
- See `refactorings/replace-conditional-with-polymorphism.md` for polymorphism pattern
```

---

## Refactoring Offer Format

### User Confirmation Prompt

```markdown
---

## 🤖 Automated Refactoring Available

**Refactorable Smells Detected**: [X] opportunities

**Total Estimated Time Savings**: ~[Y] minutes

**Refactorings Available**:
1. [Smell 1] in [location] - Save ~[Z] minutes
2. [Smell 2] in [location] - Save ~[Z] minutes
3. [...]

**Would you like to proceed with automated refactoring?**

**Options**:
- `yes` - Proceed with all [X] refactorings
- `yes [number]` - Proceed with specific refactoring (e.g., `yes 1`)
- `no` - Skip automated refactoring
- `review` - Show detailed refactoring plan first

**Safety**: All refactorings will be verified by code-reviewer before finalizing.

---
```

---

## ROI Calculation

### ROI Formula

```python
def calculate_refactoring_roi(smell, metrics):
    # Time savings
    manual_time = estimate_manual_refactoring_time(smell)
    automated_time = estimate_automated_time()  # ~5 mins review
    time_saved = manual_time - automated_time

    # Quality improvement
    complexity_before = metrics['complexity_before']
    complexity_after = metrics['complexity_after']
    complexity_reduction = (complexity_before - complexity_after) / complexity_before

    # Code reduction
    lines_before = metrics['lines_before']
    lines_after = metrics['lines_after']
    code_reduction = (lines_before - lines_after) / lines_before

    return {
        'time_saved_minutes': time_saved,
        'complexity_reduction_percent': complexity_reduction * 100,
        'code_reduction_percent': code_reduction * 100,
    }
```

### Estimated Times by Smell

| Smell | Manual Time | Automated Time | Time Saved |
|-------|-------------|----------------|------------|
| long_method | 30 mins | 5 mins | 25 mins |
| duplicate_code | 20 mins | 3 mins | 17 mins |
| complex_conditional | 25 mins | 5 mins | 20 mins |
| large_class | 45 mins | 10 mins | 35 mins |
| feature_envy | 15 mins | 3 mins | 12 mins |
| data_clumps | 20 mins | 5 mins | 15 mins |
| primitive_obsession | 30 mins | 8 mins | 22 mins |
| divergent_change | 35 mins | 10 mins | 25 mins |
| shotgun_surgery | 40 mins | 10 mins | 30 mins |
| inappropriate_intimacy | 25 mins | 5 mins | 20 mins |

---

## Summary

**Refactoring Recommendation Template**:
- Description of smell
- Current code example
- Issue explanation
- Recommended refactoring
- Benefits
- ROI estimate
- Automated refactoring offer
- User confirmation prompt

**ROI Estimation**:
- Time saved (manual vs automated)
- Complexity reduction
- Code reduction
- Quality improvement

**User Confirmation**:
- `yes` - Proceed with refactoring
- `no` - Skip for now
- `review` - See detailed plan first

**Integration**:
- Code-reviewer detects refactorable smell
- Calculates ROI
- Offers automated refactoring
- Awaits user confirmation
- Invokes refactoring-engineer if confirmed

**Priority**: **Important** (enables automated code improvement)

# Refactorable Smells Classification

**Purpose**: Identify which code smells can be automatically fixed by refactoring-engineer vs require manual intervention.

**Usage**: Phase 4 (Priority Assessment) to determine integration strategy.

---

## Overview

Not all code issues can be refactored automatically. This guide classifies smells into:
1. **Refactorable**: Can be fixed by refactoring-engineer (behavior-preserving transformations)
2. **Non-Refactorable**: Require manual fixes (security, performance, architectural decisions)

---

## Refactorable Smells (11 smells)

These smells reference the refactoring-engineer catalog and CAN be automated:

### Method-Level Smells (4 smells)

#### 1. Long Method
**Source**: `refactoring-engineer/smells/method/long-method.md`
**Refactorable**:  YES
**Pattern**: Extract Method, Decompose Conditional
**Automation**: High - extract_method is well-defined transformation

**Example**:
```python
# Before (75 lines, complexity 15)
def process_user_data(user_id, name, email, ...):
    # 75 lines of mixed concerns

# After (refactoring-engineer applies extract_method)
def process_user_data(user_id, name, email, ...):
    user = validate_user(user_id, name, email)
    payment = process_payment(user)
    send_confirmation(user, payment)
```

---

#### 2. Long Parameter List
**Source**: `refactoring-engineer/smells/method/long-parameter-list.md`
**Refactorable**:  YES
**Pattern**: Introduce Parameter Object, Preserve Whole Object
**Automation**: Medium - requires creating new class

**Example**:
```python
# Before (7 parameters)
def create_user(name, email, phone, address, city, state, zip):
    pass

# After (refactoring-engineer applies introduce_parameter_object)
class UserData:
    def __init__(self, name, email, phone, address, city, state, zip):
        ...

def create_user(user_data: UserData):
    pass
```

---

#### 3. Duplicate Code
**Source**: `refactoring-engineer/smells/method/duplicate-code.md`
**Refactorable**:  YES
**Pattern**: Extract Method, Pull Up Method, Form Template Method
**Automation**: High - well-defined transformation

**Example**:
```python
# Before (duplicate code in 2 files)
# user_service.py
def validate_user(user):
    if not user.name: raise ValueError()
    if not user.email: raise ValueError()
    if not validate_email(user.email): raise ValueError()

# admin_service.py
def validate_admin(admin):
    if not admin.name: raise ValueError()
    if not admin.email: raise ValueError()
    if not validate_email(admin.email): raise ValueError()

# After (refactoring-engineer applies extract_method)
# validators.py
def validate_person(person):
    if not person.name: raise ValueError()
    if not person.email: raise ValueError()
    if not validate_email(person.email): raise ValueError()
```

---

#### 4. Complex Conditional
**Source**: `refactoring-engineer/smells/method/complex-conditional.md`
**Refactorable**:  YES
**Pattern**: Decompose Conditional, Replace Conditional with Polymorphism
**Automation**: Medium - decompose_conditional is straightforward

**Example**:
```python
# Before (nested 4 levels)
if user.is_active:
    if user.has_subscription:
        if subscription.is_valid:
            if not subscription.is_expired:
                # ...

# After (refactoring-engineer applies decompose_conditional)
if not is_subscription_active(user):
    return

def is_subscription_active(user):
    return (user.is_active and
            user.has_subscription and
            user.subscription.is_valid and
            not user.subscription.is_expired)
```

---

### Class-Level Smells (4 smells)

#### 5. Large Class
**Source**: `refactoring-engineer/smells/class/large-class.md`
**Refactorable**:  YES
**Pattern**: Extract Class, Extract Subclass, Extract Interface
**Automation**: Medium - requires identifying cohesive groups

**Example**:
```python
# Before (250 lines, 15 methods)
class UserService:
    def create_user(...): pass
    def validate_user(...): pass
    def send_email(...): pass
    def log_event(...): pass
    # ... 11 more methods

# After (refactoring-engineer applies extract_class)
class UserService:
    def __init__(self):
        self.validator = UserValidator()
        self.notifier = EmailNotifier()
        self.logger = EventLogger()

    def create_user(...):
        user = self.validator.validate(...)
        self.notifier.send_welcome(user)
        self.logger.log('user_created', user)
```

---

#### 6. Feature Envy
**Source**: `refactoring-engineer/smells/class/feature-envy.md`
**Refactorable**:  YES
**Pattern**: Move Method, Move Field
**Automation**: High - clear when method belongs elsewhere

**Example**:
```python
# Before (Feature Envy)
class Invoice:
    def calculate_discount(self, customer):
        if customer.loyalty_points > 100:
            return customer.loyalty_points * 0.01
        return 0

# After (refactoring-engineer applies move_method)
class Customer:
    def calculate_discount(self):
        if self.loyalty_points > 100:
            return self.loyalty_points * 0.01
        return 0

class Invoice:
    def apply_discount(self, customer):
        discount = customer.calculate_discount()
```

---

#### 7. Data Clumps
**Source**: `refactoring-engineer/smells/class/data-clumps.md`
**Refactorable**:  YES
**Pattern**: Extract Class, Introduce Parameter Object
**Automation**: Medium - requires identifying clumps

**Example**:
```python
# Before (address fields always together)
class User:
    name: str
    email: str
    street: str
    city: str
    state: str
    zip: str

# After (refactoring-engineer applies extract_class)
class Address:
    street: str
    city: str
    state: str
    zip: str

class User:
    name: str
    email: str
    address: Address
```

---

#### 8. Primitive Obsession
**Source**: `refactoring-engineer/smells/class/primitive-obsession.md`
**Refactorable**:  YES
**Pattern**: Replace Data Value with Object, Extract Class
**Automation**: Medium - requires creating value objects

**Example**:
```python
# Before (primitive for domain concept)
class Order:
    customer_email: str  # Just a string

def send_notification(email: str):
    # Email validation, formatting scattered everywhere
    pass

# After (refactoring-engineer applies replace_data_value_with_object)
class Email:
    def __init__(self, value: str):
        self.value = self._validate(value)

    def _validate(self, value):
        if '@' not in value:
            raise ValueError("Invalid email")
        return value

class Order:
    customer_email: Email
```

---

### System-Level Smells (3 smells)

#### 9. Divergent Change
**Source**: `refactoring-engineer/smells/system/divergent-change.md`
**Refactorable**:  YES
**Pattern**: Extract Class, Move Method
**Automation**: Medium - requires identifying change reasons

**Example**:
```python
# Before (class changes for multiple reasons)
class UserManager:
    def create_user(...): pass  # Business logic
    def save_to_database(...): pass  # Persistence
    def send_email(...): pass  # Notifications
    def log_event(...): pass  # Logging

# After (refactoring-engineer applies extract_class)
class UserService:  # Business logic
    def create_user(...): pass

class UserRepository:  # Persistence
    def save_to_database(...): pass

class NotificationService:  # Notifications
    def send_email(...): pass

class Logger:  # Logging
    def log_event(...): pass
```

---

#### 10. Shotgun Surgery
**Source**: `refactoring-engineer/smells/system/shotgun-surgery.md`
**Refactorable**:  YES
**Pattern**: Move Method, Move Field, Inline Class
**Automation**: Medium - requires consolidating scattered changes

---

#### 11. Inappropriate Intimacy
**Source**: `refactoring-engineer/smells/system/inappropriate-intimacy.md`
**Refactorable**:  YES
**Pattern**: Move Method, Extract Class, Hide Delegate
**Automation**: Medium - requires reducing coupling

---

## Non-Refactorable Smells

These issues require manual fixes (security knowledge, performance optimization, architectural decisions):

### Security Smells (4 smells)

**Source**: `code-reviewer/security/performance-smells.md`

#### 1. SQL Injection
**Refactorable**:  NO
**Reason**: Requires security knowledge, context-dependent
**Manual Fix**: Use parameterized queries, ORM

**Example**:
```python
# Issue (CANNOT be auto-refactored)
query = f"SELECT * FROM users WHERE id = {user_id}"

# Manual fix required
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**Why Not Refactorable**: Refactoring preserves behavior, including vulnerabilities. Security fixes CHANGE behavior (reject malicious input).

---

#### 2. Cross-Site Scripting (XSS)
**Refactorable**:  NO
**Reason**: Requires security knowledge, output context matters
**Manual Fix**: Escape output, use templating engine

---

#### 3. Hardcoded Secrets
**Refactorable**:  NO
**Reason**: Requires configuration management, environment setup
**Manual Fix**: Use environment variables, secrets manager

---

#### 4. Insecure Deserialization
**Refactorable**:  NO
**Reason**: Requires security redesign
**Manual Fix**: Validate input, use safe serialization

---

### Performance Smells (4 smells)

#### 1. N+1 Query Problem
**Refactorable**:  NO
**Reason**: Requires database/ORM knowledge
**Manual Fix**: Use eager loading, join queries

**Example**:
```python
# Issue (CANNOT be auto-refactored)
for user in users:
    user.orders  # N+1: Separate query each iteration

# Manual fix required
users = User.objects.prefetch_related('orders')  # 1 query
```

**Why Not Refactorable**: Requires understanding database queries, ORM behavior. Not a code structure issue.

---

#### 2. Memory Leak
**Refactorable**:  NO
**Reason**: Requires memory management knowledge
**Manual Fix**: Release resources, use weak references

---

#### 3. Blocking I/O
**Refactorable**:  NO
**Reason**: Requires async/concurrency redesign
**Manual Fix**: Use async/await, non-blocking I/O

---

#### 4. Inefficient Algorithm
**Refactorable**:  NO
**Reason**: Requires algorithmic knowledge
**Manual Fix**: Use better data structure, optimize algorithm

---

### Architectural Smells (not code smells)

#### 1. Tight Coupling
**Refactorable**: Warning: PARTIALLY
**Reason**: Some coupling can be reduced via Extract Class, some requires architecture redesign
**Decision**: Case-by-case

#### 2. Missing Abstraction
**Refactorable**: Warning: PARTIALLY
**Reason**: Extract Interface is refactorable, but choosing right abstraction requires judgment

#### 3. Over-Engineering
**Refactorable**:  NO
**Reason**: Requires removing code, simplifying design (not behavior-preserving)

---

## Classification Decision Tree

```
Is this a code smell?
    ├─→ NO → Check if security/performance/architecture issue
    │       ↓
    │   Security issue?
    │       └─→ YES → NOT REFACTORABLE (requires security fix)
    │   Performance issue?
    │       └─→ YES → NOT REFACTORABLE (requires optimization)
    │   Architecture issue?
    │       └─→ MAYBE → Case-by-case decision
    │
    └─→ YES → Is it in refactoring-engineer catalog?
            ├─→ YES → REFACTORABLE (can automate)
            └─→ NO → Check if code-reviewer-specific smell
```

---

## Integration Usage

### Phase 4: Priority Assessment

**Process**:
```markdown
1. Classify all detected smells:
   - Load refactoring-engineer catalog: {{load: ../refactoring-engineer/smells/INDEX.md}}
   - Load code-reviewer security/performance smells: {{load: ../security/performance-smells.md}}

2. For each smell, determine:
   - In refactoring-engineer catalog? → REFACTORABLE
   - Security/performance issue? → NOT REFACTORABLE
   - Architectural issue? → Case-by-case

3. Group issues:
   - Critical (security, crashes) → Manual fixes required
   - Important Non-Refactorable (N+1, memory leaks) → Manual fixes
   - Important Refactorable (long_method, duplicate_code) → Can automate
   - Suggestions → Optional

4. Create action plan:
   - Fix Critical first (manual)
   - Fix Important Non-Refactorable (manual)
   - Offer to refactor Refactorable smells (automated)
   - Address Suggestions (optional)
```

### Phase 5: Recommendations

**For Refactorable Smells**:
```markdown
Detected 3 refactorable issues:
- Long Method (line 45): Extract Method refactoring
- Duplicate Code (line 150): Extract shared logic
- Complex Conditional (line 200): Decompose conditional

Would you like me to invoke refactoring-engineer to fix these automatically?
(Estimated time: 30 min, ROI: 80 hrs/year saved)
```

**For Non-Refactorable Smells**:
```markdown
Detected 2 non-refactorable issues (manual fixes required):
- SQL Injection (line 23): Use parameterized queries
  See: security/input-validation.md for examples

- N+1 Query (line 67): Use eager loading
  See: performance/database-performance.md for patterns
```

---

## Summary Table

| Category | Smell | Refactorable? | Automation Level | Pattern |
|----------|-------|---------------|-----------------|---------|
| **Method** | Long Method |  YES | High | Extract Method |
| **Method** | Long Parameter List |  YES | Medium | Introduce Parameter Object |
| **Method** | Duplicate Code |  YES | High | Extract Method |
| **Method** | Complex Conditional |  YES | Medium | Decompose Conditional |
| **Class** | Large Class |  YES | Medium | Extract Class |
| **Class** | Feature Envy |  YES | High | Move Method |
| **Class** | Data Clumps |  YES | Medium | Extract Class |
| **Class** | Primitive Obsession |  YES | Medium | Replace with Object |
| **System** | Divergent Change |  YES | Medium | Extract Class |
| **System** | Shotgun Surgery |  YES | Medium | Move Method/Field |
| **System** | Inappropriate Intimacy |  YES | Medium | Extract Class |
| **Security** | SQL Injection |  NO | N/A | Manual fix |
| **Security** | XSS |  NO | N/A | Manual fix |
| **Security** | Hardcoded Secrets |  NO | N/A | Manual fix |
| **Performance** | N+1 Query |  NO | N/A | Manual fix |
| **Performance** | Memory Leak |  NO | N/A | Manual fix |
| **Performance** | Blocking I/O |  NO | N/A | Manual fix |

**Key Principle**: Refactorable = behavior-preserving code structure transformation. Non-refactorable = requires domain knowledge (security, performance, architecture).

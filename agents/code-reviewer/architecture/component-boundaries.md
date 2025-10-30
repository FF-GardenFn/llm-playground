# Component Boundaries & Separation of Concerns

**Purpose**: Assess architecture quality focusing on component boundaries, layering, and separation of concerns.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (architectural issues)

**Refactorable**: ⚠️ PARTIALLY (some violations can be refactored via Move Method/Extract Class)

---

## Overview

Component boundaries define how system is divided into modules/layers. Well-defined boundaries improve:
- **Maintainability**: Changes localized to specific components
- **Testability**: Components can be tested in isolation
- **Reusability**: Components can be used in different contexts
- **Understandability**: Clear responsibilities

---

## Architectural Patterns

### 1. Layered Architecture

**Structure**:
```
┌─────────────────────────────┐
│   Presentation Layer        │  ← UI, Controllers, Views
├─────────────────────────────┤
│   Business Logic Layer      │  ← Domain logic, Services
├─────────────────────────────┤
│   Data Access Layer         │  ← Repositories, ORM
├─────────────────────────────┤
│   Database                  │
└─────────────────────────────┘
```

**Rules**:
- Each layer only depends on layer below
- No layer skipping (presentation → database directly)
- Each layer has clear responsibility

**Example - Good Layering**:
```python
# ✅ GOOD: Clear layer separation

# Presentation Layer (views.py)
from business_logic import UserService

class UserController:
    def __init__(self):
        self.user_service = UserService()

    def create_user(self, request):
        user_data = request.POST
        user = self.user_service.create_user(user_data)
        return render_template('user_created.html', user=user)

# Business Logic Layer (services.py)
from data_access import UserRepository

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def create_user(self, user_data):
        # Business validation
        self.validate_user(user_data)
        # Delegate to data layer
        return self.user_repo.save(user_data)

# Data Access Layer (repositories.py)
class UserRepository:
    def save(self, user_data):
        # Database interaction
        return User.objects.create(**user_data)
```

**Example - Violation (Layer Skipping)**:
```python
# ❌ BAD: Presentation directly accesses database

# views.py
from models import User  # ← Skipping business logic layer!

class UserController:
    def create_user(self, request):
        # Business logic in controller! (should be in service layer)
        if len(request.POST['name']) < 3:
            raise ValueError("Name too short")

        # Direct database access! (should be in repository layer)
        user = User.objects.create(**request.POST)
        return render_template('user_created.html', user=user)

# Problems:
# - Business logic scattered
# - Hard to test
# - Tight coupling
```

**Detection Heuristics**:
- Controllers directly using ORM models
- Views containing business logic
- Services directly accessing database (no repository layer)

**Severity**: **Important** (poor architecture)

---

### 2. Dependency Rule

**Principle**: Dependencies point inward (toward domain/business logic).

```
┌─────────────────────────────────────┐
│   Infrastructure (DB, HTTP, UI)    │ ← Depends on
├─────────────────────────────────────┤
│   Application Services              │ ← Depends on
├─────────────────────────────────────┤
│   Domain Logic (Core)               │ ← No dependencies!
└─────────────────────────────────────┘
```

**Example - Good Dependency Direction**:
```python
# ✅ GOOD: Domain has no dependencies

# domain/user.py (Core Domain)
class User:
    """Pure domain model - no external dependencies"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def is_valid(self):
        return len(self.name) >= 3 and '@' in self.email

# application/user_service.py (Application Layer)
from domain.user import User  # ← Depends on domain
from infrastructure.user_repo import UserRepository  # ← Depends on infrastructure

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, name, email):
        user = User(name, email)  # Domain logic
        if not user.is_valid():
            raise ValueError("Invalid user")
        return self.user_repo.save(user)  # Infrastructure

# infrastructure/user_repo.py (Infrastructure Layer)
from domain.user import User  # ← Depends on domain

class UserRepository:
    def save(self, user: User):
        # Database interaction
        return db.save(user)
```

**Example - Violation (Wrong Dependency Direction)**:
```python
# ❌ BAD: Domain depends on infrastructure

# domain/user.py
from infrastructure.database import db  # ← WRONG! Domain depends on infrastructure!

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save(self):
        return db.save(self)  # Domain knows about database!

# Problems:
# - Can't test domain without database
# - Domain coupled to infrastructure
# - Violates dependency rule
```

**Detection Heuristics**:
- Domain models importing infrastructure (database, HTTP)
- Domain models depending on frameworks (Django models, Flask)

**Severity**: **Important**

---

### 3. Separation of Concerns

**Principle**: Each component has one responsibility.

**Concerns to Separate**:
- **Business Logic**: Domain rules, validation
- **Data Access**: Database queries, ORM
- **UI/Presentation**: Templates, controllers
- **External Integration**: APIs, third-party services
- **Infrastructure**: Logging, configuration

**Example - Mixed Concerns**:
```python
# ❌ BAD: Multiple concerns in one class
class UserController:
    def create_user(self, request):
        # Concern 1: Request parsing (presentation)
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Concern 2: Business validation (business logic)
        if len(name) < 3:
            raise ValueError("Name too short")
        if '@' not in email:
            raise ValueError("Invalid email")

        # Concern 3: Database access (data layer)
        user = User.objects.create(name=name, email=email)

        # Concern 4: Email sending (external integration)
        send_email(email, "Welcome!")

        # Concern 5: Logging (infrastructure)
        logger.info(f"User created: {user.id}")

        # Concern 6: Response rendering (presentation)
        return render_template('user_created.html', user=user)

# 6 concerns in 1 class!
```

**Example - Separated Concerns**:
```python
# ✅ GOOD: Concerns separated

# Presentation Layer
class UserController:
    def __init__(self, user_service, email_service):
        self.user_service = user_service
        self.email_service = email_service

    def create_user(self, request):
        # Only handles request/response
        user_data = self._parse_request(request)
        user = self.user_service.create_user(user_data)
        self.email_service.send_welcome_email(user.email)
        return render_template('user_created.html', user=user)

# Business Logic Layer
class UserService:
    def __init__(self, user_repo, logger):
        self.user_repo = user_repo
        self.logger = logger

    def create_user(self, user_data):
        # Only handles business logic
        self._validate_user(user_data)
        user = self.user_repo.save(user_data)
        self.logger.info(f"User created: {user.id}")
        return user

# Data Access Layer
class UserRepository:
    def save(self, user_data):
        # Only handles database
        return User.objects.create(**user_data)

# External Integration
class EmailService:
    def send_welcome_email(self, email):
        # Only handles email
        send_email(email, "Welcome!")
```

**Detection Heuristics**:
- Classes with multiple unrelated responsibilities
- Classes importing from many unrelated modules (database, email, logging, etc.)

**Severity**: **Important**

---

### 4. Component Coupling

**Principle**: Minimize coupling between components.

**Types of Coupling**:

**Tight Coupling (BAD)**:
```python
# ❌ BAD: Direct dependency on concrete class
class OrderProcessor:
    def __init__(self):
        self.payment_gateway = StripePaymentGateway()  # ← Tightly coupled!

    def process_order(self, order):
        self.payment_gateway.charge(order.total)

# Can't switch to different payment gateway without modifying OrderProcessor
```

**Loose Coupling (GOOD)**:
```python
# ✅ GOOD: Dependency injection with interface
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount):
        pass

class OrderProcessor:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway  # ← Loosely coupled!

    def process_order(self, order):
        self.payment_gateway.charge(order.total)

# Can inject any payment gateway (Stripe, PayPal, etc.)
order_processor = OrderProcessor(StripePaymentGateway())
order_processor = OrderProcessor(PayPalPaymentGateway())
```

**Detection Heuristics**:
- Classes instantiating dependencies directly
- No dependency injection
- Many imports from specific modules

**Severity**: **Important**

---

### 5. Cohesion

**Principle**: Related functionality should be together.

**High Cohesion (GOOD)**:
```python
# ✅ GOOD: User-related operations together
class UserService:
    def create_user(self, user_data): pass
    def update_user(self, user_id, user_data): pass
    def delete_user(self, user_id): pass
    def find_user(self, user_id): pass

# All methods related to user management
```

**Low Cohesion (BAD)**:
```python
# ❌ BAD: Unrelated operations in same class
class UtilityService:
    def create_user(self, user_data): pass
    def send_email(self, email): pass
    def calculate_tax(self, amount): pass
    def log_event(self, event): pass

# Methods have no common purpose
```

**Detection Heuristics**:
- Class name is generic (`Utility`, `Helper`, `Manager`)
- Methods operate on different data
- Low method interaction (methods don't call each other)

**Severity**: **Suggestion**

---

## Common Violations

### 1. Business Logic in Controllers

```python
# ❌ BAD: Business logic in controller
class UserController:
    def create_user(self, request):
        # Business logic here! (should be in service)
        name = request.POST['name']
        if len(name) < 3:
            return "Name too short"

        email = request.POST['email']
        if not is_premium_email_domain(email):
            return "Only premium email domains allowed"

        user = User.objects.create(name=name, email=email)
        return render('success.html')

# ✅ GOOD: Business logic in service
class UserService:
    def create_user(self, user_data):
        if len(user_data['name']) < 3:
            raise ValueError("Name too short")
        if not self.is_premium_email_domain(user_data['email']):
            raise ValueError("Only premium email domains allowed")
        return self.user_repo.save(user_data)

class UserController:
    def create_user(self, request):
        try:
            user = self.user_service.create_user(request.POST)
            return render('success.html', user=user)
        except ValueError as e:
            return render('error.html', error=str(e))
```

---

### 2. Database Logic in Business Layer

```python
# ❌ BAD: SQL in business logic
class UserService:
    def create_user(self, user_data):
        # SQL here! (should be in repository)
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (user_data['name'], user_data['email'])
        )
        return cursor.lastrowid

# ✅ GOOD: SQL in repository
class UserRepository:
    def save(self, user_data):
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (user_data['name'], user_data['email'])
        )
        return cursor.lastrowid

class UserService:
    def create_user(self, user_data):
        return self.user_repo.save(user_data)
```

---

### 3. Multiple Responsibilities (SRP Violation)

```python
# ❌ BAD: Multiple responsibilities
class UserManager:
    def create_user(self, user_data): pass      # User CRUD
    def send_welcome_email(self, email): pass   # Email
    def log_user_created(self, user_id): pass   # Logging
    def calculate_discount(self, user): pass     # Pricing

# ✅ GOOD: Separate responsibilities
class UserService:
    def create_user(self, user_data): pass

class EmailService:
    def send_welcome_email(self, email): pass

class Logger:
    def log_user_created(self, user_id): pass

class PricingService:
    def calculate_discount(self, user): pass
```

---

## Review Checklist

### Phase 2: Manual Review

**Layering**:
- [ ] Are layers clearly defined (presentation, business, data)?
- [ ] Do layers only depend on layers below?
- [ ] Is layer skipping avoided (presentation → database)?

**Dependency Direction**:
- [ ] Do dependencies point inward (toward domain)?
- [ ] Does domain have no external dependencies?
- [ ] Is infrastructure separate from business logic?

**Separation of Concerns**:
- [ ] Does each class have single responsibility?
- [ ] Are concerns properly separated (business, data, UI)?
- [ ] Are unrelated concerns in same class (SRP violation)?

**Coupling**:
- [ ] Is dependency injection used?
- [ ] Are components loosely coupled?
- [ ] Can components be tested in isolation?

**Cohesion**:
- [ ] Are related operations together?
- [ ] Do methods operate on same data?
- [ ] Is class name specific (not `Utility`, `Manager`)?

---

## Summary

**Component Boundary Principles**:
1. **Layered Architecture**: Presentation → Business → Data
2. **Dependency Rule**: Dependencies point inward
3. **Separation of Concerns**: One class, one responsibility
4. **Loose Coupling**: Dependency injection, interfaces
5. **High Cohesion**: Related functionality together

**Common Violations**:
- Business logic in controllers
- Database logic in business layer
- Multiple responsibilities in one class
- Tight coupling (no dependency injection)
- Low cohesion (unrelated operations)

**Detection**:
- Phase 2: Manual architectural review
- Look for SRP violations, layer skipping, tight coupling

**Refactorable**:
- ⚠️ PARTIALLY - Some violations fixable via Move Method, Extract Class
- Some require architectural redesign

**Priority**: **Important** (affects maintainability, testability)

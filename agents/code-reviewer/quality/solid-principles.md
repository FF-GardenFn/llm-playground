# SOLID Principles

**Purpose**: Assess object-oriented design quality using SOLID principles during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Suggestion (design improvements)

**Source**: Robert C. Martin's SOLID principles

---

## Overview

SOLID is an acronym for five design principles that make software more understandable, flexible, and maintainable:

- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

---

## S - Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

**Translation**: Each class should have one job, one responsibility.

### Violation Example

```python
# BAD: Multiple responsibilities
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def get_name(self):
        return self.name

    def save_to_database(self):  # Database responsibility
        db.execute(f"INSERT INTO users VALUES ('{self.name}', '{self.email}')")

    def send_welcome_email(self):  # Email responsibility
        email_service.send(self.email, "Welcome!")

    def generate_report(self):  # Reporting responsibility
        return f"User: {self.name}, Email: {self.email}"

# Class has 4 reasons to change:
# 1. User data structure changes
# 2. Database schema changes
# 3. Email system changes
# 4. Report format changes
```

### Fix: Separate Responsibilities

```python
# GOOD: Single responsibility per class
class User:
    """Represents user data (single responsibility: domain model)"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    """Handles user persistence (single responsibility: database)"""
    def save(self, user):
        db.execute(
            "INSERT INTO users VALUES (%s, %s)",
            (user.name, user.email)
        )

class EmailService:
    """Handles email notifications (single responsibility: notifications)"""
    def send_welcome_email(self, user):
        email_service.send(user.email, "Welcome!")

class UserReportGenerator:
    """Generates user reports (single responsibility: reporting)"""
    def generate(self, user):
        return f"User: {user.name}, Email: {user.email}"
```

### Detection Heuristics

- Class has methods for multiple unrelated concerns (database, email, logging, etc.)
- Class name is vague (`Manager`, `Handler`, `Controller`, `Util`)
- Class has high method count (> 10 methods)
- Class imports many unrelated modules

### Severity

**Important** if class has critical responsibilities (security, data persistence)
**Suggestion** otherwise

**Note**: Partially refactorable via Extract Class (see `refactoring-engineer/smells/class/large-class.md`)

---

## O - Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension, closed for modification.

**Translation**: Add new functionality without changing existing code.

### Violation Example

```python
# BAD: Must modify class to add new shapes
class AreaCalculator:
    def calculate_area(self, shape):
        if shape.type == 'circle':
            return 3.14 * shape.radius ** 2
        elif shape.type == 'rectangle':
            return shape.width * shape.height
        elif shape.type == 'triangle':  # Added new shape - MODIFIED existing code
            return 0.5 * shape.base * shape.height
        # Adding new shape requires modifying this method!
```

### Fix: Extension via Polymorphism

```python
# GOOD: Extend by adding new classes (no modification)
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def calculate_area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def calculate_area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def calculate_area(self):
        return self.width * self.height

class Triangle(Shape):  # NEW: Added without modifying existing code
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def calculate_area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    def calculate_total_area(self, shapes):
        return sum(shape.calculate_area() for shape in shapes)
```

### Detection Heuristics

- Large if/elif chains based on type
- Switch statements on object type
- Frequent modifications to add new cases

### Severity

**Suggestion** (improves extensibility)

---

## L - Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without breaking the program.

**Translation**: Derived classes should extend, not replace, base class behavior.

### Violation Example

```python
# BAD: Square violates LSP (changes Rectangle behavior)
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def get_area(self):
        return self.width * self.height

class Square(Rectangle):
    """Square is-a Rectangle, but breaks substitutability"""
    def set_width(self, width):
        self.width = width
        self.height = width  # ← Unexpected side effect!

    def set_height(self, height):
        self.height = height
        self.width = height  # ← Unexpected side effect!

# Test that works with Rectangle but FAILS with Square:
def test_rectangle(rect):
    rect.set_width(5)
    rect.set_height(10)
    assert rect.get_area() == 50  # Expected: 50

rect = Rectangle(0, 0)
test_rectangle(rect)  # PASS: area = 50

square = Square(0, 0)
test_rectangle(square)  # FAIL: area = 100 (not 50!)
# Square is NOT substitutable for Rectangle!
```

### Fix: Separate Hierarchies

```python
# GOOD: Use composition or separate hierarchies
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def get_area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_area(self):
        return self.width * self.height

class Square(Shape):  # No longer extends Rectangle
    def __init__(self, side):
        self.side = side

    def get_area(self):
        return self.side ** 2
```

### Detection Heuristics

- Subclass throws exceptions where base class doesn't
- Subclass weakens preconditions or strengthens postconditions
- Subclass changes expected behavior
- Tests fail when base class is replaced with subclass

### Severity

**Important** (breaks polymorphism, causes bugs)

---

## I - Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

**Translation**: Many specific interfaces are better than one general-purpose interface.

### Violation Example

```python
# BAD: Fat interface forces implementation of unused methods
from abc import ABC, abstractmethod

class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass

class HumanWorker(Worker):
    def work(self):
        print("Human working")

    def eat(self):
        print("Human eating")

    def sleep(self):
        print("Human sleeping")

class RobotWorker(Worker):
    def work(self):
        print("Robot working")

    def eat(self):
        pass  # ← Forced to implement (robots don't eat!)

    def sleep(self):
        pass  # ← Forced to implement (robots don't sleep!)
```

### Fix: Segregate Interfaces

```python
# GOOD: Specific interfaces
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class HumanWorker(Workable, Eatable, Sleepable):  # Implements all
    def work(self):
        print("Human working")

    def eat(self):
        print("Human eating")

    def sleep(self):
        print("Human sleeping")

class RobotWorker(Workable):  # Only implements what it needs
    def work(self):
        print("Robot working")
```

### Detection Heuristics

- Interface has many methods (> 5)
- Implementations leave methods empty (`pass`, `NotImplementedError`)
- Interface mixes unrelated concerns

### Severity

**Suggestion** (improves interface design)

---

## D - Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Translation**: Depend on interfaces/abstractions, not concrete implementations.

### Violation Example

```python
# BAD: High-level class depends on low-level concrete class
class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL")

    def query(self, sql):
        print(f"Executing: {sql}")

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # ← Direct dependency on concrete class

    def get_user(self, user_id):
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Problem: Can't switch to PostgreSQL without modifying UserService
```

### Fix: Depend on Abstraction

```python
# GOOD: Depend on interface (abstraction)
from abc import ABC, abstractmethod

class Database(ABC):  # Abstraction
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def query(self, sql):
        pass

class MySQLDatabase(Database):  # Concrete implementation
    def connect(self):
        print("Connecting to MySQL")

    def query(self, sql):
        print(f"Executing: {sql}")

class PostgreSQLDatabase(Database):  # Another concrete implementation
    def connect(self):
        print("Connecting to PostgreSQL")

    def query(self, sql):
        print(f"Executing: {sql}")

class UserService:
    def __init__(self, db: Database):  # ← Depends on abstraction
        self.db = db

    def get_user(self, user_id):
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Now can switch databases without modifying UserService:
user_service_mysql = UserService(MySQLDatabase())
user_service_postgres = UserService(PostgreSQLDatabase())
```

### Detection Heuristics

- Classes instantiate dependencies directly (`self.db = MySQLDatabase()`)
- No dependency injection
- High-level classes import low-level concrete classes
- Difficult to test (can't mock dependencies)

### Severity

**Important** (improves testability and flexibility)

---

## SOLID Review Checklist

### Phase 2: Manual Review

**Single Responsibility Principle**:
- [ ] Does each class have one clear responsibility?
- [ ] Are class names specific (not `Manager`, `Handler`, `Util`)?
- [ ] Would changes to database, email, or logging require modifying this class?

**Open/Closed Principle**:
- [ ] Can new functionality be added without modifying existing code?
- [ ] Are if/elif chains based on type avoided?
- [ ] Is polymorphism used for extensibility?

**Liskov Substitution Principle**:
- [ ] Can derived classes replace base classes without breaking code?
- [ ] Do derived classes extend (not replace) base class behavior?
- [ ] Do tests pass when base class is replaced with derived class?

**Interface Segregation Principle**:
- [ ] Are interfaces small and focused?
- [ ] Are implementations forced to have empty methods?
- [ ] Are interfaces cohesive (related methods)?

**Dependency Inversion Principle**:
- [ ] Do classes depend on abstractions (not concrete classes)?
- [ ] Is dependency injection used?
- [ ] Are dependencies mockable for testing?

---

## Integration with Code-Reviewer Process

### Phase 2: Manual Review

```markdown
Load SOLID principles:
  {{load: ../quality/solid-principles.md}}

Assess object-oriented design:
  1. SRP: Does each class have single responsibility?
  2. OCP: Can code be extended without modification?
  3. LSP: Are subclasses substitutable?
  4. ISP: Are interfaces segregated?
  5. DIP: Do classes depend on abstractions?

Output: Suggestions for SOLID violations
```

### Phase 5: Recommendations

```markdown
## Suggestions: SOLID Design Improvements

**1. Single Responsibility Principle (Line 45)**
Class `UserService` has multiple responsibilities:
- User persistence (database)
- Email notifications
- Report generation

Recommendation: Extract classes:
- `UserRepository` for persistence
- `EmailService` for notifications
- `UserReportGenerator` for reports

**2. Dependency Inversion Principle (Line 120)**
Class `OrderProcessor` depends on concrete `MySQLDatabase`:
```python
self.db = MySQLDatabase()  # Direct dependency
```

Recommendation: Depend on abstraction:
```python
def __init__(self, db: Database):  # Interface
    self.db = db
```

Benefits:
- Easier to test (mock database)
- Can switch database implementations
- Follows Dependency Injection pattern
```

---

## Relationship to Refactorable Smells

### SOLID Violations That Are Refactorable

**Single Responsibility Principle**:
- Violation: Large Class with multiple responsibilities
- Refactorable: YES via Extract Class
- See: `refactoring-engineer/smells/class/large-class.md`

**Open/Closed Principle**:
- Violation: Type-based if/elif chains
- Refactorable: PARTIALLY via Replace Conditional with Polymorphism
- See: `refactoring-engineer/refactorings/simplifying-conditionals/`

### SOLID Violations That Are NOT Refactorable

**Liskov Substitution Principle**:
- Requires redesigning inheritance hierarchy
- Not behavior-preserving (changes public contract)
- Severity: Important

**Interface Segregation Principle**:
- Requires creating new interfaces
- Architectural decision (not just code movement)
- Severity: Suggestion

**Dependency Inversion Principle**:
- Requires introducing abstractions
- Architectural redesign
- Severity: Important

---

## Summary

**SOLID Principles**:
1. **S**ingle Responsibility: One class, one reason to change
2. **O**pen/Closed: Open for extension, closed for modification
3. **L**iskov Substitution: Subclasses must be substitutable
4. **I**nterface Segregation: Many specific interfaces > one general
5. **D**ependency Inversion: Depend on abstractions, not concretions

**Code-Reviewer Usage**:
- Phase 2: Assess OO design against SOLID
- Phase 5: Provide suggestions for violations
- Priority: Suggestion (design improvements)

**Refactorable**:
- SRP violations (Large Class) → Extract Class
- OCP violations (Type chains) → Replace Conditional with Polymorphism

**Non-Refactorable**:
- LSP violations → Redesign inheritance
- ISP violations → Create new interfaces
- DIP violations → Introduce abstractions

**Benefits**:
- More maintainable code
- Easier to test
- Better separation of concerns
- More flexible architecture

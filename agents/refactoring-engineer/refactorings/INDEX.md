# Refactoring Patterns Index

**Purpose**: Quick reference catalog of all refactoring patterns with difficulty ratings, risk levels, and selection guidance.

**Usage**: Navigate from this index to detailed pattern documentation when applying refactorings.

---

## Pattern Catalog by Category

### Composing Methods

Refactorings that improve method structure and readability.

| Pattern | Difficulty | Risk | When to Use |
|---------|-----------|------|-------------|
| **Extract Method** ✅ | Easy | Low | Method too long, code needs reuse, unclear intent |
| Inline Method | Easy | Low | Method body clearer than name, over-indirection |
| Extract Variable | Easy | Low | Complex expression needs explanation |
| Replace Temp with Query | Medium | Low | Temporary variable used in multiple places |

**Legend**: ✅ = Detailed documentation exists

---

### Moving Features

Refactorings that move functionality between classes.

| Pattern | Difficulty | Risk | When to Use |
|---------|-----------|------|-------------|
| Move Method | Medium | Medium | Method uses another class more than own (Feature Envy) |
| Move Field | Medium | Medium | Field used more by another class |
| Extract Class | Hard | Medium | Class doing too much, clear separation possible |
| Inline Class | Medium | Low | Class no longer pulling weight, over-distribution |

---

### Organizing Data

Refactorings that improve data structure and encapsulation.

| Pattern | Difficulty | Risk | When to Use |
|---------|-----------|------|-------------|
| Encapsulate Field | Easy | Low | Public field needs protection |
| Replace Data Value with Object | Medium | Medium | Primitive obsession, data needs behavior |
| Replace Array with Object | Medium | Medium | Array elements have different meanings |

---

### Simplifying Conditionals

Refactorings that clarify complex conditional logic.

| Pattern | Difficulty | Risk | When to Use |
|---------|-----------|------|-------------|
| Decompose Conditional | Medium | Low | Complex if/else logic, nested conditionals |
| Replace Conditional with Polymorphism | Hard | High | Type code with conditional behavior |
| Introduce Null Object | Medium | Medium | Repeated null checks, missing object behavior |

---

## Difficulty Levels

### Easy
- **Skill Required**: Basic refactoring knowledge
- **Time**: Minutes to hours
- **Scope**: Single method or small change
- **Examples**: Extract Method, Extract Variable, Inline Method

### Medium
- **Skill Required**: Solid understanding of OOP
- **Time**: Hours to day
- **Scope**: Multiple methods or class changes
- **Examples**: Move Method, Decompose Conditional, Replace Data Value

### Hard
- **Skill Required**: Advanced design skills
- **Time**: Days to week
- **Scope**: Multiple classes or architectural
- **Examples**: Extract Class, Replace Conditional with Polymorphism

---

## Risk Levels

### Low Risk
- **Characteristics**:
  - Single method changes
  - Well-tested code
  - Clear boundaries
  - Automated refactoring tool available

- **Safety**: Standard test-driven approach sufficient

- **Examples**: Extract Method, Inline Method, Extract Variable

### Medium Risk
- **Characteristics**:
  - Multiple method changes
  - Some test coverage
  - Moderate coupling
  - Manual refactoring required

- **Safety**: Test-driven approach + careful verification

- **Examples**: Move Method, Extract Class, Replace Data Value

### High Risk
- **Characteristics**:
  - Cross-cutting changes
  - Poor test coverage
  - High coupling
  - Architectural impact

- **Safety**: MUST use incremental strategy (Branch by Abstraction, Strangler Fig, Parallel Change)

- **Examples**: Replace Conditional with Polymorphism, Large Extract Class

---

## Pattern Selection Decision Tree

### Starting Point: Identified Smell

```
What type of smell?

METHOD-LEVEL:
    ├─→ Long Method?
    │       └─→ Extract Method (composing-methods/extract-method.md) ✅
    │
    ├─→ Long Parameter List?
    │       └─→ Introduce Parameter Object OR Preserve Whole Object
    │
    ├─→ Duplicate Code?
    │       └─→ Extract Method, then consider Pull Up Method
    │
    └─→ Complex Conditional?
            └─→ Decompose Conditional OR Replace Conditional with Polymorphism

CLASS-LEVEL:
    ├─→ Large Class?
    │       └─→ Extract Class (moving-features/extract-class.md)
    │
    ├─→ Feature Envy?
    │       └─→ Move Method (moving-features/move-method.md)
    │
    ├─→ Data Clumps?
    │       └─→ Extract Class OR Introduce Parameter Object
    │
    └─→ Primitive Obsession?
            └─→ Replace Data Value with Object

SYSTEM-LEVEL:
    ├─→ Divergent Change?
    │       └─→ Extract Class (moving-features/extract-class.md)
    │
    ├─→ Shotgun Surgery?
    │       └─→ Move Method + Move Field (consolidate changes)
    │
    └─→ Inappropriate Intimacy?
            └─→ Move Method OR Extract Class
```

---

## Pattern Details Reference

### Composing Methods

#### Extract Method ✅
**Difficulty**: Easy | **Risk**: Low

**Problem**: Method too long or code fragment can be grouped together.

**Solution**: Turn fragment into method with descriptive name.

**Detailed Documentation**: See `composing-methods/extract-method.md`

**Quick Example**:
```python
# Before
def print_invoice(amount):
    print("Invoice")
    print(f"Amount: {amount}")

# After
def print_invoice(amount):
    print_header()
    print_details(amount)

def print_header():
    print("Invoice")

def print_details(amount):
    print(f"Amount: {amount}")
```

---

#### Inline Method
**Difficulty**: Easy | **Risk**: Low

**Problem**: Method body clearer than method name, unnecessary indirection.

**Solution**: Replace method calls with method body.

**Documentation**: Coming in Phase B

---

#### Extract Variable
**Difficulty**: Easy | **Risk**: Low

**Problem**: Complex expression hard to understand.

**Solution**: Extract expression into variable with descriptive name.

**Documentation**: Coming in Phase B

**Quick Example**:
```python
# Before
if (platform == "MAC" and browser == "CHROME" and resolution > 1920):
    # ...

# After
is_high_res_mac_chrome = (platform == "MAC" and
                          browser == "CHROME" and
                          resolution > 1920)
if is_high_res_mac_chrome:
    # ...
```

---

#### Replace Temp with Query
**Difficulty**: Medium | **Risk**: Low

**Problem**: Temporary variable holding result of expression used in multiple places.

**Solution**: Extract expression into method, replace temp references with method calls.

**Documentation**: Coming in Phase B

---

### Moving Features

#### Move Method
**Difficulty**: Medium | **Risk**: Medium

**Problem**: Method uses another class more than own class (Feature Envy).

**Solution**: Move method to class it uses most.

**Documentation**: Coming in Phase B

**Quick Example**:
```python
# Before
class Account:
    def overdraft_charge(self):
        return self.account_type.overdraft_charge(self.days_overdrawn)

class AccountType:
    def overdraft_charge(self, days_overdrawn):
        # calculation using days_overdrawn

# After
class Account:
    def overdraft_charge(self):
        return self.account_type.overdraft_charge(self)

class AccountType:
    def overdraft_charge(self, account):
        # calculation using account.days_overdrawn
```

---

#### Move Field
**Difficulty**: Medium | **Risk**: Medium

**Problem**: Field used more by another class than own class.

**Solution**: Move field to class that uses it most.

**Documentation**: Coming in Phase B

---

#### Extract Class
**Difficulty**: Hard | **Risk**: Medium

**Problem**: Class doing too much, clear subset of responsibilities identifiable.

**Solution**: Create new class for subset, move relevant fields and methods.

**Documentation**: Coming in Phase B

**Quick Example**:
```python
# Before
class Person:
    name: str
    office_phone: str
    office_area_code: str

    def get_office_phone(self):
        return f"{self.office_area_code}-{self.office_phone}"

# After
class Person:
    name: str
    office_phone: TelephoneNumber

class TelephoneNumber:
    area_code: str
    number: str

    def get_telephone_number(self):
        return f"{self.area_code}-{self.number}"
```

---

#### Inline Class
**Difficulty**: Medium | **Risk**: Low

**Problem**: Class no longer pulling weight, unnecessary abstraction.

**Solution**: Move class features into another class, delete original.

**Documentation**: Coming in Phase B

---

### Organizing Data

#### Encapsulate Field
**Difficulty**: Easy | **Risk**: Low

**Problem**: Public field accessed directly.

**Solution**: Make field private, create getter/setter methods.

**Documentation**: Coming in Phase B

---

#### Replace Data Value with Object
**Difficulty**: Medium | **Risk**: Medium

**Problem**: Primitive type used for domain concept (Primitive Obsession).

**Solution**: Create small object to represent concept.

**Documentation**: Coming in Phase B

**Quick Example**:
```python
# Before
class Order:
    customer: str  # Just a name string

# After
class Order:
    customer: Customer

class Customer:
    name: str
    address: str
    credit_rating: int

    def is_good_customer(self):
        return self.credit_rating > 700
```

---

#### Replace Array with Object
**Difficulty**: Medium | **Risk**: Medium

**Problem**: Array elements have different meanings, hard to understand.

**Solution**: Replace array with object having named fields.

**Documentation**: Coming in Phase B

---

### Simplifying Conditionals

#### Decompose Conditional
**Difficulty**: Medium | **Risk**: Low

**Problem**: Complex conditional logic, nested if/else hard to understand.

**Solution**: Extract condition and each branch into separate methods.

**Documentation**: Coming in Phase B

**Quick Example**:
```python
# Before
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# After
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

---

#### Replace Conditional with Polymorphism
**Difficulty**: Hard | **Risk**: High

**Problem**: Conditional switches on type code, repeated in multiple places.

**Solution**: Create subclasses for each type, override method in each.

**Documentation**: Coming in Phase B

---

#### Introduce Null Object
**Difficulty**: Medium | **Risk**: Medium

**Problem**: Repeated null checks throughout code.

**Solution**: Create null object that provides default behavior.

**Documentation**: Coming in Phase B

---

## Pattern Selection by Context

### When Code is Too Long

**Long Method**:
1. Extract Method (primary) ✅
2. Decompose Conditional (if dominated by conditionals)
3. Replace Temp with Query (if many temps)

**Large Class**:
1. Extract Class (primary)
2. Extract Subclass (if specialized behavior exists)
3. Extract Interface (if multiple client uses)

---

### When Code is Duplicated

**Duplicate Code in Same Class**:
1. Extract Method

**Duplicate Code in Sibling Classes**:
1. Extract Method, then Pull Up Method

**Duplicate Code in Unrelated Classes**:
1. Extract Method
2. Consider Extract Class if substantial duplication

---

### When Code Has Wrong Home

**Feature Envy** (method uses another class more):
1. Move Method (primary)
2. Extract Method first if only part envious

**Data Clumps** (fields always together):
1. Extract Class (create object from clump)
2. Introduce Parameter Object (if in parameters)

---

### When Code is Too Complex

**Complex Conditionals**:
1. Decompose Conditional (for clarity)
2. Replace Conditional with Polymorphism (for type switches)

**Complex Expressions**:
1. Extract Variable (introduce explaining variable)
2. Extract Method (introduce explaining method)

---

## Integration with Safety

### Before Applying Pattern

**Required**: Load and complete `../safety/prerequisites.md`
- [ ] Tests exist and are green
- [ ] Version control available
- [ ] Code compiles/runs

### Risk Assessment

**Required**: Load and complete `../safety/risk-assessment.md`

Based on pattern risk level:
- **Low Risk**: Standard test-driven refactoring
- **Medium Risk**: Test-driven + verification
- **High Risk**: MUST use incremental strategy

### Safety Techniques for High-Risk Patterns

Load appropriate technique from `../safety/techniques/`:
- test-driven-refactoring.md - Red-green-refactor cycle
- branch-by-abstraction.md - Gradual interface migration
- strangler-fig.md - Incremental replacement
- parallel-change.md - Expand-migrate-contract

---

## Pattern Combination Strategies

### Sequential Application

Apply patterns in sequence when:
1. Each pattern reduces complexity for next
2. Risk level allows direct application
3. Tests remain green throughout

**Example Sequence**:
1. Extract Method (simplify long method)
2. Move Method (relocate to better class)
3. Inline Method (remove original)

---

### Incremental Application

Apply single pattern incrementally when:
1. Pattern has high risk level
2. Poor test coverage
3. Broad impact across codebase

**Example Incremental Extract Class**:
1. Create new class (empty)
2. Move one field
3. Run tests
4. Move one method
5. Run tests
6. Repeat until complete

---

## Quick Navigation

- **Workflows**: `../workflows/REFACTORING_PROCESS.md` - Complete 6-phase process
- **Smells**: `../smells/INDEX.md` - Smell catalog and detection
- **Safety**: `../safety/prerequisites.md` - Safety gate
- **Safety**: `../safety/risk-assessment.md` - Risk evaluation
- **Verification**: `../verification/checklist.md` - Post-refactoring verification
- **Tracking**: `../tracking/debt-checklist.md` - ROI measurement

---

## Detailed Pattern Documentation

### Available (✅)

- **refactorings/composing-methods/extract-method.md** - Complete documentation with examples, mechanics, variations

### Coming in Phase B

**Composing Methods** (3 patterns):
- inline-method.md
- extract-variable.md
- replace-temp-with-query.md

**Moving Features** (4 patterns):
- move-method.md
- move-field.md
- extract-class.md
- inline-class.md

**Organizing Data** (3 patterns):
- encapsulate-field.md
- replace-data-value-with-object.md
- replace-array-with-object.md

**Simplifying Conditionals** (3 patterns):
- decompose-conditional.md
- replace-conditional-with-polymorphism.md
- introduce-null-object.md

**Note**: Use this INDEX for quick reference and selection. Detailed documentation follows same pattern as extract-method.md (comprehensive examples, mechanics, variations, when to use).

---

## Summary

**14 Patterns Cataloged**:
- 4 Composing Methods
- 4 Moving Features
- 3 Organizing Data
- 3 Simplifying Conditionals

**Selection**: Use decision tree and context guides

**Risk Assessment**: Easy/Medium/Hard + Low/Medium/High

**Integration**: All patterns integrate with safety gates and verification

**Next Phase**: After pattern selection, proceed to `../safety/risk-assessment.md` for safety check before implementation.

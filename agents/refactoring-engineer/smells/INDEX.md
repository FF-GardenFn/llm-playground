# Code Smells Index

**Purpose**: Quick reference catalog of all code smells with detection heuristics and refactoring recommendations.

**Usage**: Navigate from this index to detailed smell documentation when quality issues detected.

---

## Smell Catalog by Category

### Method-Level Smells

Code quality issues within individual methods.

| Smell | Severity | Detection Heuristic | Recommended Refactoring |
|-------|----------|---------------------|------------------------|
| **Long Method** ✅ | High | >20 lines, multiple responsibilities | Extract Method, Decompose Conditional |
| Long Parameter List | Medium | >3 parameters | Introduce Parameter Object, Preserve Whole Object |
| Duplicate Code | High | Same code in 2+ locations | Extract Method, Pull Up Method, Form Template Method |
| Complex Conditional | Medium | Nested if/else >2 levels | Decompose Conditional, Replace with Polymorphism |

**Legend**: ✅ = Detailed documentation exists

---

### Class-Level Smells

Code quality issues within class design and responsibilities.

| Smell | Severity | Detection Heuristic | Recommended Refactoring |
|-------|----------|---------------------|------------------------|
| Large Class | High | >200 lines, >10 methods | Extract Class, Extract Subclass, Extract Interface |
| Feature Envy | Medium | Method uses another class more than own | Move Method, Move Field |
| Data Clumps | Medium | 3+ fields always used together | Extract Class, Introduce Parameter Object |
| Primitive Obsession | Low | Primitive types instead of small objects | Replace Data Value with Object, Extract Class |

---

### System-Level Smells

Code quality issues in system architecture and organization.

| Smell | Severity | Detection Heuristic | Recommended Refactoring |
|-------|----------|---------------------|------------------------|
| Divergent Change | High | One class changes for multiple reasons | Extract Class, Move Method |
| Shotgun Surgery | Critical | Single change requires touching many classes | Move Method, Move Field, Inline Class |
| Inappropriate Intimacy | Medium | Classes too tightly coupled | Move Method, Extract Class, Hide Delegate |

---

## Severity Levels

### Critical
- **Impact**: Blocks functionality or creates immediate risk
- **Priority**: Address immediately
- **Example**: Shotgun Surgery preventing safe changes

### High
- **Impact**: Significant maintenance burden or bug risk
- **Priority**: Address in current sprint
- **Example**: Long Method with multiple responsibilities

### Medium
- **Impact**: Moderate technical debt accumulation
- **Priority**: Address when working in area
- **Example**: Feature Envy reducing cohesion

### Low
- **Impact**: Minor improvement opportunity
- **Priority**: Address during refactoring sessions
- **Example**: Primitive Obsession in stable code

---

## Detection Heuristics Quick Reference

### Method Smells

**Long Method**:
```
if (method_lines > 20 OR
    method_has_multiple_responsibilities OR
    method_name_contains_"and"):
    smell = "Long Method"
```

**Long Parameter List**:
```
if (parameter_count > 3 OR
    parameters_frequently_used_together):
    smell = "Long Parameter List"
```

**Duplicate Code**:
```
if (same_code_in_2_or_more_locations):
    smell = "Duplicate Code"
```

**Complex Conditional**:
```
if (nested_if_depth > 2 OR
    boolean_expression_length > 40_chars):
    smell = "Complex Conditional"
```

### Class Smells

**Large Class**:
```
if (class_lines > 200 OR
    method_count > 10 OR
    field_count > 10):
    smell = "Large Class"
```

**Feature Envy**:
```
if (method_uses_other_class_data_more_than_own):
    smell = "Feature Envy"
```

**Data Clumps**:
```
if (same_3_or_more_fields_appear_together_in_2_or_more_places):
    smell = "Data Clumps"
```

**Primitive Obsession**:
```
if (primitive_type_used_for_domain_concept):
    smell = "Primitive Obsession"
    # Examples: string for phone number, int for money
```

### System Smells

**Divergent Change**:
```
if (one_class_changes_for_multiple_different_reasons):
    smell = "Divergent Change"
    # Example: Class changes for UI, DB, and business logic
```

**Shotgun Surgery**:
```
if (single_change_requires_modifying_many_classes):
    smell = "Shotgun Surgery"
    # Example: Adding field requires 15 class changes
```

**Inappropriate Intimacy**:
```
if (two_classes_access_each_others_private_data_frequently):
    smell = "Inappropriate Intimacy"
```

---

## Smell → Refactoring Mapping

### Method Smells

**Long Method** → See `../refactorings/composing-methods/extract-method.md` ✅
- Primary: Extract Method
- Alternative: Decompose Conditional (if conditionals dominate)

**Long Parameter List** → See `refactorings/organizing-data/`
- Primary: Introduce Parameter Object
- Alternative: Preserve Whole Object, Replace Parameters with Method

**Duplicate Code** → See `refactorings/composing-methods/`
- Primary: Extract Method
- Alternative: Pull Up Method (if in siblings), Form Template Method (if similar)

**Complex Conditional** → See `refactorings/simplifying-conditionals/`
- Primary: Decompose Conditional
- Alternative: Replace Conditional with Polymorphism

### Class Smells

**Large Class** → See `refactorings/moving-features/extract-class.md`
- Primary: Extract Class
- Alternative: Extract Subclass (if specialized behavior), Extract Interface (if multiple clients)

**Feature Envy** → See `refactorings/moving-features/move-method.md`
- Primary: Move Method
- Alternative: Move Field, Extract Method then Move

**Data Clumps** → See `refactorings/moving-features/extract-class.md`
- Primary: Extract Class (make object from clump)
- Alternative: Introduce Parameter Object

**Primitive Obsession** → See `refactorings/organizing-data/`
- Primary: Replace Data Value with Object
- Alternative: Extract Class

### System Smells

**Divergent Change** → See `refactorings/moving-features/extract-class.md`
- Primary: Extract Class (separate responsibilities)
- Alternative: Move Method (move each responsibility)

**Shotgun Surgery** → See `refactorings/moving-features/`
- Primary: Move Method + Move Field (consolidate changes)
- Alternative: Inline Class (if over-distributed)

**Inappropriate Intimacy** → See `refactorings/moving-features/`
- Primary: Move Method (reduce coupling)
- Alternative: Extract Class, Hide Delegate

---

## Detection Workflow

### 1. Scan Code
Read target files and identify potential issues.

### 2. Match to Smells
Use detection heuristics above to classify issues.

### 3. Assess Severity
Critical > High > Medium > Low

### 4. Select Refactoring
Use smell → refactoring mapping to choose pattern.

### 5. Proceed to Refactoring Selection
Navigate to appropriate refactoring pattern documentation.

---

## Detailed Smell Documentation

### Available (✅)

- **smells/method/long-method.md** - Complete documentation with examples, detection, refactoring strategies

### Coming in Phase B

- smells/method/long-parameter-list.md
- smells/method/duplicate-code.md
- smells/method/complex-conditional.md
- smells/class/large-class.md
- smells/class/feature-envy.md
- smells/class/data-clumps.md
- smells/class/primitive-obsession.md
- smells/system/divergent-change.md
- smells/system/shotgun-surgery.md
- smells/system/inappropriate-intimacy.md

**Note**: Use this INDEX for quick reference. Detailed documentation follows same pattern as long-method.md (comprehensive examples, metrics, strategies).

---

## Example Usage

### Scenario: Reviewing UserService class

```python
# Code snippet
class UserService:
    def process_user_data(self, user_id, name, email, phone, address,
                          city, state, zip, country, preferences, settings):
        # ... 150 lines of code ...
        if user.is_active:
            if user.has_subscription:
                if subscription.is_valid:
                    # ... nested logic ...
```

**Smell Detection**:
1. ✓ Long Parameter List detected (11 parameters > 3)
2. ✓ Long Method detected (150 lines > 20)
3. ✓ Complex Conditional detected (nested 3 levels > 2)

**Severity Assessment**:
- Long Parameter List: Medium
- Long Method: High
- Complex Conditional: Medium

**Recommended Refactorings**:
1. Extract Method (address Long Method first)
2. Introduce Parameter Object (address Long Parameter List)
3. Decompose Conditional (address Complex Conditional)

**Next Step**: Navigate to `../refactorings/composing-methods/extract-method.md` to begin refactoring.

---

## Quick Navigation

- **Workflows**: `../workflows/REFACTORING_PROCESS.md` - Complete 6-phase process
- **Refactorings**: `../refactorings/INDEX.md` - Pattern catalog
- **Safety**: `../safety/prerequisites.md` - Safety gate
- **Verification**: `../verification/checklist.md` - Verification gate
- **Tracking**: `../tracking/debt-checklist.md` - ROI measurement

---

## Summary

**11 Smells Cataloged**:
- 4 Method-level
- 4 Class-level
- 3 System-level

**Detection**: Use heuristics table for quick identification

**Mapping**: Use smell → refactoring table to select pattern

**Severity**: Critical > High > Medium > Low

**Next Phase**: After smell detection, proceed to `../refactorings/INDEX.md` for pattern selection.

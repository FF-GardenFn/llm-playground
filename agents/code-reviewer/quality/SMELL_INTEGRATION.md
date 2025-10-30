# Smell Catalog Integration

**Purpose**: Explain how code-reviewer integrates with refactoring-engineer's smell catalog to achieve zero duplication.

**Architecture**: Single Source of Truth - refactoring-engineer owns smell catalog, code-reviewer references it.

**Integration Method**: Load directives (`{{load: ...}}`) to reference canonical definitions.

---

## Overview

Code-reviewer and refactoring-engineer share a common smell catalog to ensure:
- **Zero Duplication**: Smell definitions maintained in one location
- **Consistency**: Both agents use same detection heuristics
- **Synchronization**: Updates automatically propagate
- **Clear Boundaries**: Refactorable smells vs non-refactorable smells

---

## Architecture

```
┌──────────────────────────────────┐
│  Refactoring-Engineer            │
│  (Smell Catalog Owner)           │
│                                  │
│  smells/INDEX.md                 │
│  ├── method/                     │
│  │   ├── long-method.md          │  ← CANONICAL DEFINITIONS
│  │   ├── long-parameter-list.md │
│  │   ├── duplicate-code.md       │
│  │   └── complex-conditional.md  │
│  ├── class/                      │
│  │   ├── large-class.md          │
│  │   ├── feature-envy.md         │
│  │   ├── data-clumps.md          │
│  │   └── primitive-obsession.md  │
│  └── system/                     │
│      ├── divergent-change.md     │
│      ├── shotgun-surgery.md      │
│      └── inappropriate-intimacy.md
└──────────────────────────────────┘
                ↑
                │ References (via {{load: ...}})
                │
┌──────────────────────────────────┐
│  Code-Reviewer                   │
│  (Smell Catalog Consumer)        │
│                                  │
│  quality/SMELL_INTEGRATION.md    │
│   → References refactoring-eng   │
│                                  │
│  security/performance-smells.md  │
│   → Code-reviewer-specific       │
│      (NOT refactorable)          │
└──────────────────────────────────┘
```

---

## Shared Smells (11 Total)

These smells are defined in `refactoring-engineer/smells/` and **referenced** by code-reviewer:

### Method-Level Smells (4 smells)

**1. Long Method**
- **Location**: `refactoring-engineer/smells/method/long-method.md`
- **Detection**: >20 lines OR cyclomatic complexity >10
- **Refactoring**: Extract Method, Decompose Conditional
- **Automation**: High

**2. Long Parameter List**
- **Location**: `refactoring-engineer/smells/method/long-parameter-list.md`
- **Detection**: >3 parameters
- **Refactoring**: Introduce Parameter Object
- **Automation**: Medium

**3. Duplicate Code**
- **Location**: `refactoring-engineer/smells/method/duplicate-code.md`
- **Detection**: Same/similar code in 2+ locations
- **Refactoring**: Extract Method, Pull Up Method
- **Automation**: High

**4. Complex Conditional**
- **Location**: `refactoring-engineer/smells/method/complex-conditional.md`
- **Detection**: Nested >2 levels OR boolean expression >40 chars
- **Refactoring**: Decompose Conditional
- **Automation**: Medium

### Class-Level Smells (4 smells)

**5. Large Class**
- **Location**: `refactoring-engineer/smells/class/large-class.md`
- **Detection**: >200 lines OR >10 methods
- **Refactoring**: Extract Class, Extract Subclass
- **Automation**: Medium

**6. Feature Envy**
- **Location**: `refactoring-engineer/smells/class/feature-envy.md`
- **Detection**: Method uses another class more than own
- **Refactoring**: Move Method
- **Automation**: High

**7. Data Clumps**
- **Location**: `refactoring-engineer/smells/class/data-clumps.md`
- **Detection**: 3+ fields always used together
- **Refactoring**: Extract Class, Introduce Parameter Object
- **Automation**: Medium

**8. Primitive Obsession**
- **Location**: `refactoring-engineer/smells/class/primitive-obsession.md`
- **Detection**: Primitive type for domain concept
- **Refactoring**: Replace Data Value with Object
- **Automation**: Medium

### System-Level Smells (3 smells)

**9. Divergent Change**
- **Location**: `refactoring-engineer/smells/system/divergent-change.md`
- **Detection**: Class changes for multiple unrelated reasons
- **Refactoring**: Extract Class, Move Method
- **Automation**: Medium

**10. Shotgun Surgery**
- **Location**: `refactoring-engineer/smells/system/shotgun-surgery.md`
- **Detection**: Single change requires touching many classes
- **Refactoring**: Move Method, Move Field, Inline Class
- **Automation**: Medium

**11. Inappropriate Intimacy**
- **Location**: `refactoring-engineer/smells/system/inappropriate-intimacy.md`
- **Detection**: Classes access each other's private data
- **Refactoring**: Move Method, Extract Class, Hide Delegate
- **Automation**: Medium

---

## Code-Reviewer-Specific Smells

These smells are **NOT refactorable** and are defined only in code-reviewer:

### Security Smells

**Location**: `code-reviewer/security/performance-smells.md`

1. **SQL Injection** - Use parameterized queries
2. **XSS** - Escape output
3. **Hardcoded Secrets** - Use environment variables
4. **Insecure Deserialization** - Validate input

**Why Not Refactorable**: Require security knowledge, not code structure changes

### Performance Smells

**Location**: `code-reviewer/security/performance-smells.md`

1. **N+1 Query Problem** - Use eager loading
2. **Memory Leak** - Fix resource cleanup
3. **Blocking I/O** - Use async/await
4. **Inefficient Algorithm** - Use better data structure

**Why Not Refactorable**: Require optimization knowledge, not behavior-preserving transformations

---

## Integration in Code-Reviewer Workflow

### Phase 1: Automated Analysis (Smell Detection)

```markdown
## Phase 1: Automated Analysis

### Step 1.3: Smell Detection

Load shared smell catalog from refactoring-engineer:
  {{load: ../../refactoring-engineer/smells/INDEX.md}}

Check code against shared smells (11 smells):
  Method Smells:
    - long_method: >20 lines OR complexity >10
    - long_parameter_list: >3 parameters
    - duplicate_code: Same code in 2+ locations
    - complex_conditional: Nested >2 levels

  Class Smells:
    - large_class: >200 lines OR >10 methods
    - feature_envy: Method uses other class more
    - data_clumps: 3+ fields always together
    - primitive_obsession: Primitive for domain concept

  System Smells:
    - divergent_change: Class changes for multiple reasons
    - shotgun_surgery: Single change touches many classes
    - inappropriate_intimacy: Classes access each other's privates

Check code against code-reviewer-specific smells (8+ smells):
  Security Smells:
    - sql_injection: Unsanitized input in SQL
    - xss: Unescaped output in HTML
    - hardcoded_secrets: API keys in code
    - insecure_deserialization: Untrusted pickle

  Performance Smells:
    - n_plus_1_query: Query in loop
    - memory_leak: Unreleased resources
    - blocking_io: Sync in async context
    - inefficient_algorithm: O(n²) when better exists

Output: Combined list of detected smells with locations and severity
```

### Phase 4: Priority Assessment (Refactorable Classification)

```markdown
## Phase 4: Priority Assessment

### Step 4.2: Identify Refactorable Smells

Load refactorable smell classification:
  {{load: ../priorities/refactorable-smells.md}}

For each detected smell, classify:

**Refactorable Smells** (from refactoring-engineer catalog):
  - long_method → extract_method (Easy, High Automation)
  - long_parameter_list → introduce_parameter_object (Medium)
  - duplicate_code → extract_method (Easy, High Automation)
  - complex_conditional → decompose_conditional (Medium)
  - large_class → extract_class (Medium)
  - feature_envy → move_method (High Automation)
  - data_clumps → extract_class (Medium)
  - primitive_obsession → replace_with_object (Medium)
  - divergent_change → extract_class (Medium)
  - shotgun_surgery → move_method (Medium)
  - inappropriate_intimacy → extract_class (Medium)

  Action: Offer to invoke refactoring-engineer (Mode 2)

**Non-Refactorable Smells** (code-reviewer-specific):
  - sql_injection → Manual fix (security)
  - xss → Manual fix (security)
  - hardcoded_secrets → Manual fix (configuration)
  - n_plus_1_query → Manual fix (database optimization)
  - memory_leak → Manual fix (resource management)
  - blocking_io → Manual fix (async redesign)
  - inefficient_algorithm → Manual fix (algorithmic optimization)

  Action: Provide manual fix recommendations

Decision:
  If refactorable smells found AND prerequisites met:
    → Offer to invoke refactoring-engineer (Phase 5)
  Else:
    → Provide manual recommendations (Phase 5)
```

### Phase 5: Recommendations

```markdown
## Phase 5: Recommendations

### Refactorable Issues (Can Automate)

Found 3 refactorable smells from refactoring-engineer catalog:

**1. Long Method (line 45)**
Source: refactoring-engineer/smells/method/long-method.md
Method `process_user_data` is 75 lines with complexity 15.

Refactoring: Extract Method
Automation: High (easy pattern)
Estimated time: 10 minutes
Estimated savings: 30 hours/year

**2. Duplicate Code (line 150)**
Source: refactoring-engineer/smells/method/duplicate-code.md
30 lines duplicated (85% similarity) between user_service.py and admin_service.py.

Refactoring: Extract Method
Automation: High (easy pattern)
Estimated time: 15 minutes
Estimated savings: 25 hours/year

**3. Large Class (UserService)**
Source: refactoring-engineer/smells/class/large-class.md
Class has 250 lines with 15 methods (multiple responsibilities).

Refactoring: Extract Class
Automation: Medium (requires identifying cohesive groups)
Estimated time: 20 minutes
Estimated savings: 40 hours/year

**Total**: 45 minutes investment, 95 hours/year saved (ROI: 127x)

Would you like me to invoke refactoring-engineer to fix these automatically?

### Non-Refactorable Issues (Manual Fixes Required)

Found 2 non-refactorable smells (code-reviewer-specific):

**1. SQL Injection (line 23)**
Source: code-reviewer/security/performance-smells.md
Unsanitized user input in SQL query.

Manual Fix Required: Use parameterized queries
See: security/input-validation.md for examples

**2. N+1 Query (line 67)**
Source: code-reviewer/security/performance-smells.md
Loop executing database queries.

Manual Fix Required: Use eager loading
See: performance/database-performance.md for patterns
```

---

## Reference Usage

### Method 1: Direct Load (Recommended)

```markdown
# In code-reviewer workflow files

Load smell catalog:
  {{load: ../../refactoring-engineer/smells/INDEX.md}}

Load specific smell documentation:
  {{load: ../../refactoring-engineer/smells/method/long-method.md}}
  {{load: ../../refactoring-engineer/smells/class/large-class.md}}
```

### Method 2: Integration Documentation

```markdown
# In code-reviewer/quality/SMELL_INTEGRATION.md (this file)

Reference canonical source:
  Shared smells: refactoring-engineer/smells/INDEX.md
  Refactorable classification: code-reviewer/priorities/refactorable-smells.md
```

---

## Synchronization

### Automatic Synchronization

**How It Works**:
1. Refactoring-engineer updates smell catalog (adds new smell, updates detection heuristics)
2. Code-reviewer automatically sees changes (via `{{load: ...}}` references)
3. No code-reviewer files need updating

**Example**:
```
Refactoring-Engineer updates:
  smells/method/long-method.md
    Detection: >20 lines → >25 lines (relaxed threshold)

Code-Reviewer automatically uses new threshold:
  (No changes needed - references canonical source)
```

### Version Compatibility

**Stable Interface**: `smells/INDEX.md`
- Provides quick reference with stable format
- Lists all smells with detection thresholds
- Code-reviewer consumes INDEX.md primarily

**Detailed Definitions**: `smells/*/smell-name.md`
- Can change format without breaking code-reviewer
- Provide comprehensive examples and guidance
- Code-reviewer loads specific files when needed

---

## Benefits of Integration

### 1. Zero Duplication
- Single smell catalog maintained by refactoring-engineer
- Code-reviewer does not duplicate smell documentation
- Reduces maintenance burden (update once, propagates everywhere)

### 2. Consistency
- Both agents use same smell definitions
- Same detection heuristics (thresholds, patterns)
- Same refactoring recommendations

### 3. Extensibility
- Add new smell to refactoring-engineer → both agents benefit
- Update smell definition → both agents synchronized
- No coordination needed between agent teams

### 4. Clear Boundaries
- **Refactoring-Engineer**: Owns refactorable smells (11 smells)
- **Code-Reviewer**: Adds non-refactorable smells (security, performance)
- No overlap, no confusion

### 5. Improved Integration
- Code-reviewer can confidently trigger refactoring-engineer
- Shared vocabulary (smell names, patterns)
- Seamless handoff (Phase 4 → refactoring-engineer → verification)

---

## Example: Detecting and Classifying Smells

```python
# Code under review: user_service.py

# Smell 1: Long Method (REFACTORABLE)
def process_user_data(user_id, name, email, address, phone):  # 75 lines
    # Validation (15 lines)
    if not name or len(name) < 3:
        raise ValueError("Invalid name")
    # ... more validation

    # Payment processing (20 lines)
    payment = create_payment(user_id)
    # ... payment logic

    # Email notification (15 lines)
    send_email(email, "Welcome")
    # ... email logic

    # Logging (10 lines)
    log_event("user_created", user_id)
    # ... logging logic

# Smell 2: SQL Injection (NOT REFACTORABLE)
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection!
    return db.execute(query)

# Smell 3: N+1 Query (NOT REFACTORABLE)
def get_users_with_orders():
    users = User.objects.all()
    for user in users:
        orders = user.orders.all()  # N+1 query!
```

**Code-Reviewer Detection**:

```markdown
Phase 1: Automated Analysis

Smell Detection Results:

Shared Smells (from refactoring-engineer catalog):
  ✓ Detected: long_method
    Location: user_service.py:process_user_data (lines 10-85)
    Source: refactoring-engineer/smells/method/long-method.md
    Threshold: >20 lines (found: 75 lines)
    Complexity: 15 (threshold: >10)
    Classification: REFACTORABLE

Code-Reviewer-Specific Smells:
  ✓ Detected: sql_injection
    Location: user_service.py:get_user (line 90)
    Source: code-reviewer/security/performance-smells.md
    Pattern: f-string in SQL query with user input
    Classification: NOT REFACTORABLE (security fix required)

  ✓ Detected: n_plus_1_query
    Location: user_service.py:get_users_with_orders (line 95)
    Source: code-reviewer/security/performance-smells.md
    Pattern: ORM query in loop
    Classification: NOT REFACTORABLE (database optimization required)

Phase 4: Priority Assessment

Refactorable Issues (1):
  - long_method → Can invoke refactoring-engineer

Non-Refactorable Issues (2):
  - sql_injection → Provide manual fix instructions
  - n_plus_1_query → Provide manual fix instructions

Phase 5: Recommendations

Refactorable:
  "Found 1 refactorable smell. Invoke refactoring-engineer to fix?"

Non-Refactorable:
  "Found 2 security/performance issues requiring manual fixes:
   1. SQL Injection (critical): Use parameterized queries
   2. N+1 Query (important): Use prefetch_related()"
```

---

## Summary

**Integration Architecture**:
- Refactoring-engineer **owns** smell catalog (11 refactorable smells)
- Code-reviewer **references** smell catalog via `{{load: ...}}`
- Code-reviewer **adds** non-refactorable smells (security, performance)

**Shared Smells** (11):
- Method: long_method, long_parameter_list, duplicate_code, complex_conditional
- Class: large_class, feature_envy, data_clumps, primitive_obsession
- System: divergent_change, shotgun_surgery, inappropriate_intimacy

**Code-Reviewer-Specific Smells** (8+):
- Security: sql_injection, xss, hardcoded_secrets, insecure_deserialization
- Performance: n_plus_1_query, memory_leak, blocking_io, inefficient_algorithm

**Benefits**:
- Zero duplication
- Automatic synchronization
- Consistent definitions
- Clear boundaries
- Seamless integration

**Usage**:
- Phase 1: Load and detect smells from both sources
- Phase 4: Classify as refactorable or non-refactorable
- Phase 5: Offer refactoring-engineer for refactorable, manual recommendations for non-refactorable

**Synchronization**: Automatic via load references - no coordination needed.

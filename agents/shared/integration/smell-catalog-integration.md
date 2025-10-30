# Smell Catalog Integration

**Purpose**: Define how code-reviewer and refactoring-engineer share a single authoritative smell catalog to avoid duplication.

**Principle**: Single Source of Truth - refactoring-engineer owns the smell catalog, code-reviewer references it.

---

## Architecture

```
┌──────────────────────────────────┐
│  Refactoring-Engineer            │
│  (Smell Catalog Owner)           │
│                                  │
│  smells/                         │
│  ├── INDEX.md (11 smells)       │
│  ├── method/                     │
│  │   ├── long-method.md          │
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
                │ References (symlink or load)
                │
┌──────────────────────────────────┐
│  Code-Reviewer                   │
│  (Smell Catalog Consumer)        │
│                                  │
│  quality/                        │
│  ├── SMELL_INTEGRATION.md        │
│  │   → References ../refactoring-engineer/smells/
│  ├── clean-code.md               │
│  └── solid-principles.md         │
│                                  │
│  security/                       │
│  └── performance-smells.md (NEW) │
│      → Security-specific smells  │
│      → Performance-specific smells
└──────────────────────────────────┘
```

---

## Shared Smells (Refactoring-Engineer Catalog)

### Method-Level Smells

**Refactorable via refactoring-engineer**:

1. **Long Method** (refactoring-engineer/smells/method/long-method.md)
   - Detection: >20 lines OR multiple responsibilities
   - Refactoring: Extract Method, Decompose Conditional
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

2. **Long Parameter List** (refactoring-engineer/smells/method/long-parameter-list.md)
   - Detection: >3 parameters
   - Refactoring: Introduce Parameter Object, Preserve Whole Object
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

3. **Duplicate Code** (refactoring-engineer/smells/method/duplicate-code.md)
   - Detection: Same code in 2+ locations
   - Refactoring: Extract Method, Pull Up Method
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

4. **Complex Conditional** (refactoring-engineer/smells/method/complex-conditional.md)
   - Detection: Nested >2 levels OR boolean expression >40 chars
   - Refactoring: Decompose Conditional, Replace with Polymorphism
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

### Class-Level Smells

5. **Large Class** (refactoring-engineer/smells/class/large-class.md)
   - Detection: >200 lines OR >10 methods
   - Refactoring: Extract Class, Extract Subclass
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

6. **Feature Envy** (refactoring-engineer/smells/class/feature-envy.md)
   - Detection: Method uses another class more than own
   - Refactoring: Move Method, Move Field
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

7. **Data Clumps** (refactoring-engineer/smells/class/data-clumps.md)
   - Detection: 3+ fields always used together
   - Refactoring: Extract Class, Introduce Parameter Object
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

8. **Primitive Obsession** (refactoring-engineer/smells/class/primitive-obsession.md)
   - Detection: Primitive type for domain concept
   - Refactoring: Replace Data Value with Object
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

### System-Level Smells

9. **Divergent Change** (refactoring-engineer/smells/system/divergent-change.md)
   - Detection: Class changes for multiple reasons
   - Refactoring: Extract Class, Move Method
   - Owner: refactoring-engineer
   - Used by: code-reviewer (references)

10. **Shotgun Surgery** (refactoring-engineer/smells/system/shotgun-surgery.md)
    - Detection: Single change requires touching many classes
    - Refactoring: Move Method + Move Field
    - Owner: refactoring-engineer
    - Used by: code-reviewer (references)

11. **Inappropriate Intimacy** (refactoring-engineer/smells/system/inappropriate-intimacy.md)
    - Detection: Classes access each other's private data
    - Refactoring: Move Method, Extract Class, Hide Delegate
    - Owner: refactoring-engineer
    - Used by: code-reviewer (references)

---

## Code-Reviewer-Specific Smells

### Security Smells (Not in Refactoring Catalog)

**File**: `code-reviewer/security/performance-smells.md`

These are NOT refactorable in the traditional sense (require manual fixes):

1. **SQL Injection Vulnerability**
   - Detection: Unsanitized user input in SQL queries
   - Fix: Use parameterized queries, ORM
   - Not refactorable: Requires security knowledge

2. **Cross-Site Scripting (XSS)**
   - Detection: Unescaped output in HTML
   - Fix: Escape user input, use templating
   - Not refactorable: Requires security knowledge

3. **Hardcoded Secrets**
   - Detection: API keys, passwords in code
   - Fix: Use environment variables, secrets manager
   - Not refactorable: Requires configuration changes

4. **Insecure Deserialization**
   - Detection: Deserializing untrusted data
   - Fix: Validate input, use safe serialization
   - Not refactorable: Requires security redesign

### Performance Smells (Not in Refactoring Catalog)

**File**: `code-reviewer/security/performance-smells.md`

These are NOT refactorable (require performance optimizations):

1. **N+1 Query Problem**
   - Detection: Loop executing query each iteration
   - Fix: Use eager loading, join queries
   - Not refactorable: Requires database knowledge

2. **Memory Leak**
   - Detection: Unreleased resources, circular references
   - Fix: Proper cleanup, weak references
   - Not refactorable: Requires memory management

3. **Blocking I/O**
   - Detection: Synchronous I/O in async context
   - Fix: Use async/await, non-blocking I/O
   - Not refactorable: Requires async redesign

4. **Inefficient Algorithm**
   - Detection: O(n²) or worse when better exists
   - Fix: Use better data structure/algorithm
   - Not refactorable: Requires algorithmic knowledge

---

## Usage in Code-Reviewer

### Phase 1: Automated Analysis

**Load Refactoring-Engineer Smell Catalog**:
```markdown
# code-reviewer/workflows/REVIEW_PROCESS.md

## Phase 1: Automated Analysis

### Smell Detection

Load smell catalog from refactoring-engineer:
  {{load: ../../refactoring-engineer/smells/INDEX.md}}

Check code against shared smells:
  - Method smells: long_method, long_parameter_list, duplicate_code, complex_conditional
  - Class smells: large_class, feature_envy, data_clumps, primitive_obsession
  - System smells: divergent_change, shotgun_surgery, inappropriate_intimacy

Check code against code-reviewer-specific smells:
  - Security smells: sql_injection, xss, hardcoded_secrets, insecure_deserialization
  - Performance smells: n_plus_1_query, memory_leak, blocking_io, inefficient_algorithm
```

### Phase 4: Priority Assessment

**Classify Refactorable vs Non-Refactorable**:
```markdown
# code-reviewer/priorities/refactorable-smells.md

## Refactorable Smells (Can invoke refactoring-engineer)

Smells from refactoring-engineer catalog:
  - long_method → extract_method
  - duplicate_code → extract_method
  - large_class → extract_class
  - etc.

Action: Offer to invoke refactoring-engineer

## Non-Refactorable Smells (Require manual fixes)

Security smells:
  - sql_injection → Use parameterized queries
  - xss → Escape output
  - hardcoded_secrets → Use env variables

Performance smells:
  - n_plus_1_query → Use eager loading
  - memory_leak → Fix resource cleanup
  - blocking_io → Use async/await

Action: Provide feedback and recommendations
```

---

## Integration Methods

### Method 1: File Reference (Symlink)

**Setup**:
```bash
cd /Users/hyperexploiter/PycharmProjects/MI/llm-playground/agent/code-reviewer/quality
ln -s ../../refactoring-engineer/smells smells-catalog
```

**Usage**:
```markdown
# code-reviewer/quality/SMELL_INTEGRATION.md

Load smells:
  {{load: ./smells-catalog/INDEX.md}}
```

**Pros**: Direct file access, always in sync
**Cons**: Symlinks may break if directories move

### Method 2: Explicit Load (Recommended)

**Usage**:
```markdown
# code-reviewer/quality/SMELL_INTEGRATION.md

Load smells from refactoring-engineer:
  {{load: ../../refactoring-engineer/smells/INDEX.md}}

For detailed smell documentation:
  - long_method: {{load: ../../refactoring-engineer/smells/method/long-method.md}}
  - duplicate_code: {{load: ../../refactoring-engineer/smells/method/duplicate-code.md}}
```

**Pros**: Explicit, clear dependency
**Cons**: Longer paths

### Method 3: Shared Directory (Current Approach)

**Setup**: Document smell catalog location in shared/integration/

**Usage**:
```markdown
# shared/integration/smell-catalog-integration.md

Canonical location: refactoring-engineer/smells/

Consumers:
  - refactoring-engineer (owner)
  - code-reviewer (consumer via reference)
```

**Pros**: Clear documentation, single source of truth
**Cons**: Requires coordination

---

## Example Integration Flow

### Scenario: Code Review Detects Smells

```
User: "Review this code"
    ↓
Code-Reviewer Phase 1: Automated Analysis
    ↓
1. Load refactoring-engineer smell catalog:
   - long_method pattern
   - duplicate_code pattern
   - large_class pattern

2. Check code against shared smells:
   ✓ Found: long_method at src/user.py:45-120 (75 lines)
   ✓ Found: duplicate_code at src/user.py:150-180, src/admin.py:90-120
   ✗ Not found: large_class

3. Check code against code-reviewer-specific smells:
   ✓ Found: sql_injection at src/user.py:200 (unsanitized input)
   ✓ Found: n_plus_1_query at src/user.py:150-160 (loop with queries)

    ↓
Code-Reviewer Phase 4: Priority Assessment
    ↓
Classify issues:
  - Critical: sql_injection (security smell, NOT refactorable)
  - Important: n_plus_1_query (performance smell, NOT refactorable)
  - Important: long_method (code smell, REFACTORABLE via extract_method)
  - Important: duplicate_code (code smell, REFACTORABLE via extract_method)

    ↓
Code-Reviewer Phase 5: Recommendations
    ↓
Output:
  "Critical Issues (fix immediately):
   - SQL injection at line 200: Use parameterized queries

  Important Issues (fix soon):
   - N+1 query problem at line 150: Use eager loading
   - Long method at line 45: 75 lines, consider extracting
   - Duplicate code at lines 150-180: 85% similar to admin_service

  Refactorable Issues:
   - 2 code smells can be fixed via refactoring
   - Would you like me to invoke refactoring-engineer to address these?"

    ↓
User: "Fix critical issues first, then refactor"
    ↓
[User fixes SQL injection and N+1]
    ↓
Code-Reviewer invokes Refactoring-Engineer:
  Input: [long_method, duplicate_code] with locations
  ↓
Refactoring-Engineer uses its own smell catalog to apply refactorings
```

---

## Synchronization

### Single Source of Truth

**Owner**: refactoring-engineer/smells/
**Consumer**: code-reviewer (references, does not duplicate)

### If Smell Catalog Updates

**Scenario**: refactoring-engineer adds new smell (e.g., "speculative_generality")

**Impact on Code-Reviewer**:
- Automatic: code-reviewer references catalog, sees new smell immediately
- No changes needed to code-reviewer files
- New smell automatically available for detection

### Version Compatibility

**Problem**: What if refactoring-engineer smell catalog format changes?

**Solution**: Use stable interface via INDEX.md
- INDEX.md provides quick reference (stable format)
- Detailed smell files can change format
- Code-reviewer consumes INDEX.md primarily

---

## Benefits of Integration

### 1. Zero Duplication
- Single smell catalog maintained by refactoring-engineer
- Code-reviewer does not duplicate smell documentation
- Reduces maintenance burden

### 2. Consistency
- Both agents use same smell definitions
- Same detection heuristics
- Same refactoring recommendations

### 3. Extensibility
- Add new smell to refactoring-engineer → both agents benefit
- Update smell definition → both agents synchronized

### 4. Clear Boundaries
- Refactoring-engineer: Owns refactorable smells
- Code-reviewer: Adds non-refactorable smells (security, performance)
- No overlap

---

## Summary

**Shared Smells** (11 smells in refactoring-engineer catalog):
- Method: long_method, long_parameter_list, duplicate_code, complex_conditional
- Class: large_class, feature_envy, data_clumps, primitive_obsession
- System: divergent_change, shotgun_surgery, inappropriate_intimacy

**Code-Reviewer-Specific Smells** (8-10 smells):
- Security: sql_injection, xss, hardcoded_secrets, insecure_deserialization
- Performance: n_plus_1_query, memory_leak, blocking_io, inefficient_algorithm

**Integration Method**: Code-reviewer references refactoring-engineer/smells/ via {{load:...}} directives

**Synchronization**: Automatic (references canonical source)

**Benefit**: Zero duplication, single source of truth, consistent smell detection across agents.

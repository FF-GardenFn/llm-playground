# Conflict Resolution Patterns

## Purpose

Identify, classify, and resolve conflicts that emerge when integrating outputs from multiple specialists working in parallel.

---

## Conflict Types

### Structural Conflicts

**File-Level Conflicts**:
```
Specialist A: Modified file X
Specialist B: Modified file X
Conflict: Overlapping changes to same file
```

**Namespace Conflicts**:
```
Specialist A: Created class User in models.py
Specialist B: Created class User in services.py
Conflict: Duplicate naming in different contexts
```

**Import Conflicts**:
```
Specialist A: Import from old location
Specialist B: Refactored to new location
Conflict: Broken import references
```

### Semantic Conflicts

**Logic Conflicts**:
```
Specialist A: Implements validation rule X
Specialist B: Implements contradictory rule Y
Conflict: Incompatible business logic
```

**Data Format Conflicts**:
```
Specialist A: Returns dates as ISO strings
Specialist B: Expects dates as Unix timestamps
Conflict: Incompatible data formats
```

**Assumption Conflicts**:
```
Specialist A: Assumes synchronous API
Specialist B: Implements async API
Conflict: Incompatible architectural assumptions
```

### Interface Conflicts

**Contract Violations**:
```
Agreed Interface:
  function getUser(id: string): User

Specialist Implementation:
  function getUser(id: string): Promise<User | null>

Conflict: Added null return, made async
```

**Missing Implementations**:
```
Specialist A expects: UserService.updateProfile()
Specialist B implemented: UserService.editProfile()
Conflict: Method name mismatch
```

---

## Conflict Detection

### Automated Detection

```python
class ConflictDetector:
    def detect_conflicts(self, outputs):
        """
        Automatically detect integration conflicts
        """
        conflicts = []

        # File-level conflicts
        conflicts.extend(self.detect_file_conflicts(outputs))

        # Interface violations
        conflicts.extend(self.detect_interface_conflicts(outputs))

        # Naming collisions
        conflicts.extend(self.detect_naming_conflicts(outputs))

        # Data format mismatches
        conflicts.extend(self.detect_format_conflicts(outputs))

        return conflicts

    def detect_file_conflicts(self, outputs):
        """Find files modified by multiple specialists"""
        file_modifications = defaultdict(list)

        for specialist, output in outputs.items():
            for file in output.modified_files:
                file_modifications[file].append(specialist)

        return [
            FileConflict(file, specialists)
            for file, specialists in file_modifications.items()
            if len(specialists) > 1
        ]
```

### Manual Review Triggers

```markdown
## Review Required When:

- [ ] Multiple specialists touched same file
- [ ] Interface contracts potentially violated
- [ ] Different specialists in same domain
- [ ] Shared data structures modified
- [ ] Cross-cutting concerns affected
- [ ] Integration tests failing
- [ ] Semantic ambiguities in requirements
```

---

## Resolution Strategies

### Automatic Resolution (Safe conflicts)

**Simple Merge Conflicts**:
```python
def auto_resolve_simple_merge(conflict):
    """
    Automatically resolve non-overlapping changes
    """
    if conflict.changes_are_disjoint():
        # Changes to different parts of file
        return merge_changes(conflict.specialist_a, conflict.specialist_b)

    if conflict.one_side_is_superset():
        # One specialist includes other's changes
        return take_superset(conflict)

    # Cannot auto-resolve
    return None
```

**Additive Changes**:
```
Specialist A: Added function foo()
Specialist B: Added function bar()
Resolution: Include both functions (no conflict)
```

### Manual Resolution (Complex conflicts)

**Competing Implementations**:
```markdown
## Conflict: Two approaches to same problem

**Specialist A Approach:**
- Uses caching for performance
- More complex but faster
- 50 lines of code

**Specialist B Approach:**
- Direct database query
- Simpler but slower
- 20 lines of code

**Resolution Decision Criteria:**
1. Performance requirements (how critical?)
2. Maintenance burden (complexity cost)
3. Existing patterns (consistency)
4. Future extensibility

**Decision:** Choose A if performance critical, B otherwise
```

### Synthesis Resolution (Best of both)

```markdown
## Synthesize: Combine strengths

**Specialist A:** Excellent error handling
**Specialist B:** Superior algorithm efficiency

**Synthesis:**
- Take B's core algorithm
- Apply A's error handling patterns
- Create unified solution better than either
```

---

## Resolution Protocols

### Conflict Priority Levels

**P0 - Critical (Blocks integration):**
```
- Interface contract violations
- Circular dependencies introduced
- Breaking changes to public APIs
- Security vulnerabilities
- Data corruption risks

Resolution: Must resolve immediately
```

**P1 - Important (Degrades quality):**
```
- Logic contradictions
- Performance regressions
- Inconsistent error handling
- Test failures
- Documentation gaps

Resolution: Resolve before delivery
```

**P2 - Minor (Polish):**
```
- Code style differences
- Minor inefficiencies
- Duplicate code patterns
- Naming inconsistencies

Resolution: Can defer or accept
```

### Resolution Decision Framework

```
For each conflict:

1. CLASSIFY
   - Structural / Semantic / Interface
   - P0 / P1 / P2

2. ANALYZE
   - Root cause
   - Impact scope
   - Stakeholders affected

3. GENERATE OPTIONS
   - Keep A
   - Keep B
   - Synthesize A + B
   - New approach C

4. EVALUATE OPTIONS
   - Correctness
   - Performance
   - Maintainability
   - Consistency

5. DECIDE
   - Select optimal option
   - Document rationale
   - Communicate decision

6. IMPLEMENT
   - Apply resolution
   - Verify integration
   - Update documentation
```

---

## Conflict Resolution Patterns

### Pattern 1: Namespace Partitioning

```
Problem:
Specialist A: class User (authentication)
Specialist B: class User (profile data)

Resolution:
Specialist A: class AuthUser
Specialist B: class UserProfile

Result: Clear separation, no confusion
```

### Pattern 2: Interface Adapter

```
Problem:
Specialist A: sync getUserData()
Specialist B: async getUserData()

Resolution:
class SyncAdapter:
    def getUserData(self):
        return asyncio.run(async_getUserData())

Result: Both interfaces supported
```

### Pattern 3: Strategy Selection

```
Problem:
Specialist A: Caching strategy
Specialist B: Different caching strategy

Resolution:
class CacheManager:
    def __init__(self, strategy):
        self.strategy = strategy  # A or B

    def get(self, key):
        return self.strategy.get(key)

Result: Both strategies available, runtime selection
```

### Pattern 4: Merge and Extend

```
Problem:
Specialist A: Validation rules [R1, R2, R3]
Specialist B: Validation rules [R2, R4, R5]

Resolution:
Combined rules: [R1, R2, R3, R4, R5]
Deduplicate R2, apply all

Result: Comprehensive validation
```

### Pattern 5: Deprecate and Migrate

```
Problem:
Specialist A: Old API approach
Specialist B: New API approach

Resolution:
1. Implement B's new approach
2. Keep A's old approach with deprecation warning
3. Plan migration timeline
4. Remove A in next version

Result: Backward compatibility + forward progress
```

---

## Domain-Specific Conflict Resolution

### Frontend Integration Conflicts

**Component Naming Conflicts**:
```jsx
// Specialist A
function Button() { ... }

// Specialist B
function Button() { ... }

// Resolution
function PrimaryButton() { ... }  // A
function SecondaryButton() { ... }  // B
```

**State Management Conflicts**:
```
Problem: Different state management approaches
Resolution: Establish single source of truth
  - Centralized store (Redux/Zustand)
  - Component decides read location
  - Consistent update patterns
```

### Backend Integration Conflicts

**Database Schema Conflicts**:
```sql
-- Specialist A
ALTER TABLE users ADD COLUMN status VARCHAR(20);

-- Specialist B
ALTER TABLE users ADD COLUMN state VARCHAR(50);

-- Resolution: Clarify intent
ALTER TABLE users ADD COLUMN account_status VARCHAR(20);  -- A's intent
ALTER TABLE users ADD COLUMN location_state VARCHAR(50);  -- B's intent
```

**API Endpoint Conflicts**:
```
Specialist A: POST /users/authenticate
Specialist B: POST /auth/login

Resolution: Establish consistent routing
Chosen: POST /api/v1/auth/login (consistent with existing patterns)
```

### Data Processing Conflicts

**Aggregation Logic Conflicts**:
```python
# Specialist A: Average excluding outliers
def calculate_average_a(data):
    filtered = remove_outliers(data)
    return mean(filtered)

# Specialist B: Median (robust to outliers)
def calculate_average_b(data):
    return median(data)

# Resolution: Clarify requirement
# If outliers are errors: Use A
# If outliers are valid: Use B
# If unsure: Provide both as options
```

---

## Preventive Strategies

### Conflict Prevention (Better than resolution)

**1. Clear Interface Contracts**:
```typescript
// Define upfront, enforce during development
interface UserAPI {
  getUser(id: string): Promise<User>
  createUser(data: CreateUserDTO): Promise<User>
  // Locked during parallel work
}
```

**2. Namespace Allocation**:
```
Specialist A owns: /api/auth/*
Specialist B owns: /api/users/*
Specialist C owns: /api/products/*

No overlapping ownership = no conflicts
```

**3. Shared Constants**:
```typescript
// shared/constants.ts (locked during work)
export const USER_STATUS = {
  ACTIVE: 'active',
  SUSPENDED: 'suspended',
  DELETED: 'deleted'
}

All specialists import from single source
```

**4. Integration Points First**:
```
1. Define interfaces before implementation
2. Create mock implementations
3. Specialists develop against mocks
4. Integration verifies contracts

Contracts prevent conflicts
```

---

## Conflict Resolution Tools

### Automated Tooling

```python
class IntegrationValidator:
    """Automated conflict detection and resolution"""

    def validate_integration(self, outputs):
        """Run automated checks"""
        results = {
            'file_conflicts': self.check_file_conflicts(outputs),
            'type_conflicts': self.check_type_compatibility(outputs),
            'test_results': self.run_integration_tests(outputs),
            'lint_results': self.check_code_style(outputs)
        }

        return results

    def suggest_resolutions(self, conflicts):
        """Generate resolution suggestions"""
        suggestions = []

        for conflict in conflicts:
            if conflict.is_simple_merge():
                suggestions.append(auto_merge_suggestion(conflict))
            elif conflict.is_naming_collision():
                suggestions.append(rename_suggestion(conflict))
            else:
                suggestions.append(manual_review_needed(conflict))

        return suggestions
```

### Manual Review Checklist

```markdown
## Pre-Integration Review

**Structural Review:**
- [ ] No file conflicts remain
- [ ] All imports resolve
- [ ] No duplicate definitions
- [ ] Consistent file structure

**Semantic Review:**
- [ ] Business logic consistent
- [ ] No contradictory rules
- [ ] Data flows correct
- [ ] Error handling uniform

**Interface Review:**
- [ ] All contracts satisfied
- [ ] Type signatures match
- [ ] Return values consistent
- [ ] Exception handling aligned

**Quality Review:**
- [ ] Tests passing
- [ ] Code style consistent
- [ ] Documentation complete
- [ ] No regressions introduced
```

---

## Escalation Procedures

### When to Escalate

```markdown
## Escalate Conflict When:

1. **Cannot determine correct approach**
   - Both solutions seem valid
   - Requirements ambiguous
   - Need domain expertise

2. **Breaking change required**
   - Public API must change
   - Database schema incompatible
   - User-facing behavior affected

3. **Resource conflicts**
   - Both specialists want same approach
   - Technical disagreement
   - Cannot synthesize solution

4. **Scope implications**
   - Resolution requires significant rework
   - Timeline impacted
   - Additional resources needed
```

### Escalation Process

```
1. Document Conflict
   - Describe both approaches
   - List pros/cons of each
   - Estimate resolution effort

2. Consult Stakeholders
   - Product owner (if business logic)
   - Tech lead (if architecture)
   - Security (if security implications)

3. Make Decision
   - Clear rationale
   - Timeline impact
   - Quality tradeoffs

4. Communicate Resolution
   - Notify affected specialists
   - Update documentation
   - Proceed with integration
```

---

## Post-Resolution Verification

### Integration Testing

```python
def verify_resolution(conflict, resolution):
    """
    Verify conflict resolution is correct
    """
    checks = {
        'functionality': test_functionality_preserved(resolution),
        'performance': test_performance_acceptable(resolution),
        'compatibility': test_backward_compatibility(resolution),
        'consistency': test_code_consistency(resolution)
    }

    if not all(checks.values()):
        raise IntegrationError(
            f"Resolution failed verification: {checks}"
        )

    return True
```

### Regression Prevention

```markdown
## Post-Resolution Actions

1. **Add Integration Tests**
   - Test the specific conflict scenario
   - Prevent regression
   - Document expected behavior

2. **Update Patterns**
   - Document resolution pattern
   - Update guidelines
   - Share with team

3. **Improve Process**
   - Why wasn't this prevented?
   - Update delegation patterns
   - Refine interface contracts
```

---

## Anti-Patterns

### Avoid These Resolution Mistakes

**❌ Ignoring Conflicts**:
```
Bad: "It compiles, ship it"
Good: Thoroughly review semantic compatibility
```

**❌ Always Choosing One Side**:
```
Bad: "Specialist A's output always wins"
Good: Evaluate each conflict on merit
```

**❌ Scope Creep in Resolution**:
```
Bad: "Let's rewrite everything while fixing this"
Good: Minimal change to resolve conflict
```

**❌ Insufficient Documentation**:
```
Bad: Resolve silently, no record
Good: Document conflict, rationale, resolution
```

---

*Conflict resolution is inevitable in parallel work. A Senior Engineering Manager resolves conflicts systematically, preserving the best aspects of each contribution.*

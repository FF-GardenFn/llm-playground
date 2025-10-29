# Merge Strategies: Integrating Parallel Work

**Purpose**: Systematic approaches to merging outputs from multiple specialists

---

## Core Objective

Integrate specialist outputs while:
- Detecting and resolving conflicts
- Maintaining coherence
- Verifying integration
- Enabling rollback on failure

---

## Strategy 1: Sequential Merge (No Conflicts)

**When to Use**: Tasks executed sequentially, no overlapping changes

**Approach**:
```
Task A completes → Merge A
Task B completes → Merge B (builds on A)
Task C completes → Merge C (builds on A, B)
```

**Benefits**:
- No conflicts (each task builds on previous)
- Simple integration
- Incremental verification

**Example**:
```
A: Database schema design → Merge schema.sql
B: Implement models (depends on A) → Merge models.py
C: Implement endpoints (depends on B) → Merge routes.py
```

**Verification**: Test after each merge, proceed if tests pass

---

## Strategy 2: Topological Merge (Respects Dependencies)

**When to Use**: Multiple tasks with dependencies, some parallelizable

**Approach**:
```
Merge in topological order (dependencies before dependents)
  Level 0: [A] → Merge A
  Level 1: [B] → Merge B
  Level 2: [C, D] → Merge C, then D (or resolve conflicts)
  Level 3: [E] → Merge E
```

**Algorithm**:
```python
def topological_merge(outputs, dependencies):
    """Merge outputs respecting dependencies."""
    order = topological_sort(outputs, dependencies)

    for output in order:
        try:
            merge(output)
            verify_integration()
        except ConflictError as e:
            resolve_conflict(e)
            retry_merge(output)
```

**Example**:
```
Outputs:
  A: auth schema
  B: JWT logic (depends on A)
  C: login endpoint (depends on B)
  D: refresh endpoint (depends on B)
  E: middleware (depends on C, D)

Merge order: A → B → C → D → E
Conflicts possible: C and D might both modify same file
```

---

## Strategy 3: Three-Way Merge (File Conflicts)

**When to Use**: Multiple specialists modify same files

**Approach**:
```
Base: Original file state
Ours: Specialist A's changes
Theirs: Specialist B's changes

Three-way merge:
  - Auto-merge non-overlapping changes
  - Flag overlapping changes as conflicts
  - Resolve conflicts manually or with strategy
```

**Conflict Types**:

**Type 1: Non-Overlapping (Auto-Merge)**:
```python
# Base
def func1():
    pass

# Ours (A adds func2)
def func1():
    pass

def func2():
    pass

# Theirs (B adds func3)
def func1():
    pass

def func3():
    pass

# Merged (both included)
def func1():
    pass

def func2():
    pass

def func3():
    pass
```

**Type 2: Overlapping (Manual Resolution)**:
```python
# Base
def func1():
    return "original"

# Ours (A modifies)
def func1():
    return "A's version"

# Theirs (B modifies)
def func1():
    return "B's version"

# Conflict! Both modified same line
# Resolution strategies:
#   - Keep A's version
#   - Keep B's version
#   - Combine (if semantically compatible)
#   - Escalate to user
```

---

## Strategy 4: Incremental Integration

**When to Use**: Large integration with multiple phases

**Approach**:
```
Don't wait for all work to complete
Integrate incrementally after each phase:
  Phase 1 complete → Integrate Phase 1
  Phase 2 complete → Integrate Phase 2 (on top of Phase 1)
  Phase 3 complete → Integrate Phase 3 (on top of Phases 1, 2)
```

**Benefits**:
- Catch integration issues early
- Shorter feedback loops
- Reduced merge complexity

**Example**:
```
Phase 1: Core authentication → Merge → Test ✅
Phase 2: Login/refresh endpoints → Merge → Test ✅
Phase 3: Middleware → Merge → Test ✅
Phase 4: Tests and review → Merge → Test ✅
```

---

## Strategy 5: Feature Branch Integration

**When to Use**: Using version control with branches

**Approach**:
```
Main branch: Stable code
Feature branches: Specialist work

Integration workflow:
  1. Each specialist works in feature branch
  2. Specialist completes, self-tests
  3. Merge feature branch to integration branch
  4. Run integration tests
  5. If tests pass, merge to main
  6. If tests fail, fix or rollback
```

**Branch Structure**:
```
main (stable)
  ↑
integration (testing)
  ↑
feature/auth-jwt (code-generator)
feature/auth-tests (code-generator)
```

**Example**:
```
Specialist A: Works in feature/auth-jwt
  → Commits to feature/auth-jwt
  → Signals complete
  → Merge feature/auth-jwt → integration
  → Run tests in integration
  → Tests pass ✅
  → Merge integration → main
```

---

## Strategy 6: Conflict-First Resolution

**When to Use**: Known file conflicts expected

**Approach**:
```
Identify conflicts before starting work:
  1. Detect: Multiple tasks modify same file
  2. Strategy: Serialize, partition, or coordinate
  3. Execute with strategy

Serialization:
  Task A completes → Merge
  Task B completes → Merge (no conflict, builds on A)

Partitioning:
  Task A: Modifies section 1 of file
  Task B: Modifies section 2 of file
  → Merge both with boundaries respected

Coordination:
  Task A: Adds function add_a()
  Task B: Adds function add_b()
  → Both specify function signatures upfront
  → Merge with function-level granularity
```

**Example**:
```
Conflict detected: Tasks C and D both modify app/routes/auth.py

Strategy: Partition file
  Before:
    app/routes/auth.py (single file)

  After:
    app/routes/auth_login.py (Task C)
    app/routes/auth_refresh.py (Task D)
    app/routes/__init__.py (import both)

  Result: No conflict, can merge in parallel
```

---

## Strategy 7: Interface-Based Integration

**When to Use**: Parallel work with defined interfaces

**Approach**:
```
Step 1: Define interfaces (contracts)
Step 2: Specialists implement to interface
Step 3: Merge implementations (verified against interface)
Step 4: Integration test (interface contracts verified)
```

**Example**:
```
Interface:
  POST /auth/login
  Request: { username: str, password: str }
  Response: { access_token: str, refresh_token: str, expires_at: datetime }

Backend specialist: Implements endpoint respecting interface
Frontend specialist: Consumes endpoint respecting interface

Merge:
  1. Merge backend implementation
  2. Merge frontend implementation
  3. Integration test: Contract verified ✅
```

---

## Conflict Resolution Strategies

### Resolution 1: Auto-Merge (Non-Overlapping)

**Condition**: Changes don't overlap

**Action**: Automatically merge both changes

**Example**: Specialist A adds function, Specialist B adds different function → Both included

---

### Resolution 2: Keep Ours (Precedence)

**Condition**: One specialist has precedence

**Action**: Keep our changes, discard theirs

**Example**: Task A on critical path, Task B secondary → Keep A's changes

---

### Resolution 3: Keep Theirs (Defer)

**Condition**: Other specialist has precedence

**Action**: Discard our changes, keep theirs

**Example**: Security fix takes precedence over feature → Keep security fix

---

### Resolution 4: Combine (Semantically Compatible)

**Condition**: Changes are complementary

**Action**: Combine both changes

**Example**:
```python
# Ours: Add validation
def login(username, password):
    if not username or not password:
        raise ValueError("Missing credentials")
    # ... rest of logic

# Theirs: Add logging
def login(username, password):
    logger.info(f"Login attempt: {username}")
    # ... rest of logic

# Combined: Both validation and logging
def login(username, password):
    logger.info(f"Login attempt: {username}")
    if not username or not password:
        raise ValueError("Missing credentials")
    # ... rest of logic
```

---

### Resolution 5: Escalate (Manual Intervention)

**Condition**: Semantic conflict, can't auto-resolve

**Action**: Escalate to user for decision

**Example**:
```python
# Ours: Use bcrypt
password_hash = bcrypt.hashpw(password, salt)

# Theirs: Use argon2
password_hash = argon2.hash(password)

# Conflict: Different hashing algorithms
# Escalate: User decides which to use
```

---

## Merge Verification

**After each merge, verify**:

**Completeness**:
- [ ] All expected outputs merged
- [ ] No missing files or components

**Correctness**:
- [ ] Tests pass (unit + integration)
- [ ] No regressions (existing tests still pass)
- [ ] New functionality works

**Consistency**:
- [ ] Code follows conventions
- [ ] No conflicting patterns
- [ ] Coherent overall design

**Integration**:
- [ ] Components integrate correctly
- [ ] APIs/interfaces work end-to-end
- [ ] Dependencies satisfied

---

## Rollback Strategy

**If merge fails verification**:

**Option 1: Fix Forward**:
```
Identify issue
Fix issue
Retry merge
Verify
```

**Option 2: Rollback**:
```
Revert merge
Investigate root cause
Fix issue in isolation
Retry merge
```

**Example**:
```
Merge: Combine auth module + tests
Verification: Tests fail (integration broken)

Rollback:
  git revert <merge-commit>
  [Back to pre-merge state]

Fix:
  Identify issue: API contract mismatch
  Fix in feature branch
  Retry merge with fix

Verify:
  Tests pass ✅
  Proceed
```

---

## Merge Checklist

Before merging:
- [ ] All dependencies satisfied (required tasks complete)
- [ ] Conflict strategy determined (if conflicts expected)
- [ ] Verification plan ready (how to test merge)
- [ ] Rollback plan ready (how to undo if needed)

During merge:
- [ ] Merge in topological order (dependencies first)
- [ ] Resolve conflicts per strategy
- [ ] Document resolution decisions

After merge:
- [ ] Run verification tests
- [ ] Check completeness
- [ ] Verify integration
- [ ] Commit if successful, rollback if failed

---

## Integration with Other Phases

**Dependency Analysis Integration**:
- Use topological order for merge sequence
- Respect critical path for priority

**Conflict Detection Integration**:
- Use conflict detector (atools/conflict_detector.py)
- Apply appropriate resolution strategy

**Verification Integration**:
- Run integration tests after merge
- Verify all quality gates
- Reference verification/integration-tests.md

---

## Summary

**Key Strategies**:
1. Sequential merge (no conflicts)
2. Topological merge (respects dependencies)
3. Three-way merge (file conflicts)
4. Incremental integration (phase-by-phase)
5. Feature branch integration (version control)
6. Conflict-first resolution (proactive)
7. Interface-based integration (contract-first)

**Resolution Approaches**:
- Auto-merge (non-overlapping)
- Keep ours/theirs (precedence)
- Combine (semantically compatible)
- Escalate (manual intervention)

**Verification**: Always test after merge, rollback if failed

**Goal**: Integrate parallel work efficiently while maintaining quality

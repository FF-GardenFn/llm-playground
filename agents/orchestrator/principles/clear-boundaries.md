# Principle: Clear Boundaries

**Core Insight**: Ambiguity causes rework, confusion, and conflicts. Explicit boundaries enable autonomous work.

---

## Why Clear Boundaries Matter

**Without Clear Boundaries**:
- Specialists guess scope → rework when guess wrong
- Overlapping work → conflicts and duplication
- Unclear success criteria → subjective "done" assessment
- Scope creep → timeline delays

**With Clear Boundaries**:
- Specialists know exactly what to do → efficient execution
- No overlaps → no conflicts
- Objective success criteria → verifiable completion
- Fixed scope → predictable timeline

---

## Four Dimensions of Boundaries

### 1. Scope Boundaries

**What's In Scope** (explicitly stated):
```
✅ Good: "Implement JWT authentication for POST /auth/login endpoint"
  - Clear what to implement (JWT authentication)
  - Clear where (POST /auth/login endpoint)
  - Scope is bounded

❌ Bad: "Add authentication"
  - Unclear what type (JWT? OAuth? Sessions?)
  - Unclear where (which endpoints?)
  - Scope is unbounded
```

**What's Out of Scope** (explicitly excluded):
```
✅ Good: "Implement login endpoint. Out of scope: password reset,
         email verification, 2FA, social login"
  - Explicitly excludes related features
  - Prevents scope creep

❌ Bad: "Implement login endpoint"
  - No exclusions stated
  - Specialist might include related features
  - Scope creep risk
```

**Examples**:
```
Task: Implement user authentication

In Scope:
  - JWT token generation
  - POST /auth/login endpoint
  - POST /auth/refresh endpoint
  - bcrypt password hashing
  - Rate limiting (5 attempts/min)
  - Unit tests

Out of Scope (deferred):
  - Password reset flow
  - Email verification
  - 2FA
  - OAuth/social login
  - User registration (separate task)
```

---

### 2. File Boundaries

**What Files to Modify** (explicit list):
```
✅ Good:
  Modify:
    - app/auth/jwt.py (JWT logic)
    - app/routes/auth.py (endpoints)
    - app/middleware/auth.py (middleware)
    - tests/unit/test_auth.py (tests)

  Do NOT modify:
    - app/routes/user.py (existing user routes)
    - app/models/user.py (user model unchanged)

❌ Bad: "Implement authentication"
  - Unclear which files to modify
  - Risk of modifying wrong files
```

**New Files**:
```
✅ Good:
  Create:
    - app/auth/__init__.py
    - app/auth/jwt.py
    - tests/unit/test_jwt.py
```

**File Partition** (when multiple specialists modify same domain):
```
Specialist A: app/routes/auth_login.py (login endpoint)
Specialist B: app/routes/auth_refresh.py (refresh endpoint)
Both: app/routes/__init__.py (import both)

Boundary: Clear file ownership, no overlap
```

---

### 3. Interface Boundaries

**Input Boundaries** (what specialist receives):
```
✅ Good:
  Inputs:
    - User model (existing): app/models/user.py
    - Config: JWT_SECRET from environment
    - Database: PostgreSQL connection via SQLAlchemy

❌ Bad: Assume specialist knows about existing structures
```

**Output Boundaries** (what specialist produces):
```
✅ Good:
  Outputs:
    - JWT module: app/auth/jwt.py
      - Function: generate_token(user_id) -> str
      - Function: validate_token(token) -> user_id or None
    - Login endpoint: POST /auth/login
      - Input: { username: str, password: str }
      - Output: { access_token: str, refresh_token: str, expires_at: datetime }
    - Tests: tests/unit/test_jwt.py (>80% coverage)

❌ Bad: "Implement JWT auth" (unclear what outputs needed)
```

**Contract Boundaries** (API contracts):
```
Interface contract:
  POST /auth/login
  Request:
    {
      "username": "string",
      "password": "string"
    }
  Response (200):
    {
      "access_token": "string",
      "refresh_token": "string",
      "expires_at": "ISO8601 datetime"
    }
  Response (401):
    {
      "error": "Invalid credentials"
    }

Boundary: Specialist MUST conform to this contract
```

---

### 4. Success Criteria Boundaries

**Measurable Criteria** (objective, verifiable):
```
✅ Good:
  Success Criteria:
    - All tests pass (pytest tests/unit/test_auth.py)
    - Login endpoint returns 200 for valid credentials
    - Login endpoint returns 401 for invalid credentials
    - Tokens expire after 15 minutes
    - Rate limiting blocks after 5 attempts
    - Coverage >80% (pytest --cov=app.auth --cov-fail-under=80)

❌ Bad:
  - "It works"
  - "Code is good"
  - "Feature is complete"
  (subjective, not measurable)
```

**Verification Method** (how to verify):
```
✅ Good:
  Verification:
    1. Run tests: pytest tests/unit/test_auth.py -v
    2. Manual test: curl -X POST http://localhost:5000/auth/login \
                     -d '{"username":"test","password":"test123"}'
    3. Check coverage: pytest --cov=app.auth --cov-report=term-missing
    4. Security check: bandit -r app/auth/

❌ Bad: No verification method specified
```

---

## Boundary Definition Checklist

Before assigning specialist:

**Scope**:
- [ ] What's in scope (explicit list)
- [ ] What's out of scope (explicit exclusions)
- [ ] Why certain things are excluded (rationale)

**Files**:
- [ ] Which files to modify (list)
- [ ] Which files NOT to modify (exclusions)
- [ ] New files to create (if any)

**Interfaces**:
- [ ] Input contracts (what specialist receives)
- [ ] Output contracts (what specialist produces)
- [ ] API contracts (if applicable)

**Success Criteria**:
- [ ] Measurable criteria (objective)
- [ ] Verification method (how to check)
- [ ] Done definition (when to signal complete)

---

## Examples of Good vs. Bad Boundaries

### Example 1: Code Implementation

**Bad**:
```
Task: "Add authentication"
[Everything is vague]
```

**Good**:
```
Task: "Implement JWT authentication"

Scope:
  In: JWT token generation, /auth/login endpoint, tests
  Out: Registration, password reset, 2FA (separate tasks)

Files:
  Modify: app/routes/auth.py
  Create: app/auth/jwt.py, tests/unit/test_jwt.py
  Do NOT modify: app/models/user.py (unchanged)

Interfaces:
  Input: User model (app/models/user.py), JWT_SECRET (environment)
  Output:
    - JWT module: generate_token(), validate_token()
    - Login endpoint: POST /auth/login
      Request: { username: str, password: str }
      Response: { access_token: str, refresh_token: str, expires_at: datetime }

Success Criteria:
  - Tests pass (pytest tests/unit/test_jwt.py)
  - Login works (curl test provided)
  - Tokens validate correctly
  - Coverage >80%
```

---

### Example 2: Data Analysis

**Bad**:
```
Task: "Analyze the dataset"
[No boundaries]
```

**Good**:
```
Task: "Profile customer dataset for ML quality issues"

Scope:
  In: Dataset schema, quality checks, ML risk detection (leakage, bias)
  Out: Model training, feature engineering (separate tasks)

Files:
  Input: data/customers.csv
  Output: reports/profiling_report.md, scripts/verification.py

Interfaces:
  Input: CSV dataset with columns [id, age, income, zip, target]
  Output:
    - Profiling report (markdown format)
    - Verification code (pandas script)
    - Risk assessment (Critical/High/Medium/Low)

Success Criteria:
  - Report includes schema, quality metrics, ML risks
  - All percentages exact (no adjectives)
  - Verification code runs: python scripts/verification.py
  - Recommendations provided for each issue
```

---

## Boundary Violations and Recovery

### Violation 1: Scope Creep

**Symptom**: Specialist adds features outside scope

**Example**:
```
Assigned: Implement login endpoint
Specialist adds: Password reset, email verification, 2FA
→ Scope violation (out of bounds)
```

**Recovery**:
- Accept core work (login endpoint)
- Defer extra work (password reset, etc.)
- Restate boundaries for future tasks

---

### Violation 2: File Boundary Violation

**Symptom**: Specialist modifies files outside boundary

**Example**:
```
Assigned: Modify app/routes/auth.py only
Specialist modifies: app/routes/auth.py, app/models/user.py, app/utils/helpers.py
→ Boundary violation (modified wrong files)
```

**Recovery**:
- Revert changes to out-of-bounds files
- Re-implement if necessary changes
- Clarify file boundaries more explicitly

---

### Violation 3: Interface Violation

**Symptom**: Specialist produces different contract

**Example**:
```
Expected: { "access_token": "...", "refresh_token": "...", "expires_at": "..." }
Produced: { "token": "...", "expiry": "..." }
→ Interface violation (contract mismatch)
```

**Recovery**:
- Update output to match expected contract
- OR: Update all consumers if new contract better
- Lesson: Define contracts upfront

---

## Communicating Boundaries

### Template: Task Assignment with Boundaries

```markdown
## Task: [Task Name]

### Scope
**In Scope**:
- [Feature/component 1]
- [Feature/component 2]
- [Feature/component 3]

**Out of Scope** (explicitly excluded):
- [Excluded feature 1]
- [Excluded feature 2]

**Rationale**: [Why certain things excluded]

### Files
**Modify**:
- [file1.py]: [what to change]
- [file2.py]: [what to change]

**Create**:
- [newfile.py]: [what it should contain]

**Do NOT Modify**:
- [existingfile.py]: [why it should not change]

### Interfaces
**Inputs**:
- [Input 1]: [description]
- [Input 2]: [description]

**Outputs**:
- [Output 1]: [format, contract]
- [Output 2]: [format, contract]

### Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

**Verification**:
1. [Command to verify criterion 1]
2. [Command to verify criterion 2]

### Context
[Background information, existing patterns, constraints]
```

---

## Benefits of Clear Boundaries

**For Specialists**:
- Know exactly what to do (no guessing)
- Know when done (objective criteria)
- Work autonomously (no clarification needed)
- Avoid rework (get it right first time)

**For Orchestrator**:
- Minimize coordination (no clarifying questions)
- Verify objectively (measurable criteria)
- Detect violations early (clear boundaries)
- Manage scope (no creep)

**For Integration**:
- Fewer conflicts (no overlapping work)
- Predictable outputs (defined contracts)
- Easier merging (known boundaries)
- Faster verification (clear criteria)

---

## Summary

**Four Boundary Dimensions**:
1. Scope (what's in, what's out)
2. Files (which to modify, which not to)
3. Interfaces (inputs, outputs, contracts)
4. Success criteria (measurable, verifiable)

**Key Practices**:
- State boundaries explicitly (not implicit)
- Include both what to do AND what not to do
- Make success criteria measurable
- Provide verification methods

**Benefits**:
- Efficient execution (no ambiguity)
- Autonomous work (no coordination)
- Verifiable completion (objective criteria)
- No scope creep (fixed boundaries)

**Integration**:
- Use with delegation (clear assignments)
- Use with minimal coordination (reduce questions)
- Use with verification (objective assessment)

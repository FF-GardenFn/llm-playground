# Request Analysis: Ambiguity Detection and Clarification

**Purpose**: Systematic approach to understanding user requests before decomposition

---

## Core Objective

Parse user requests to identify:
- Under-specified requirements
- Conflicting constraints
- Implicit assumptions
- Scope boundaries
- Success criteria

**Goal**: Transform vague requests into clear, actionable specifications

---

## Ambiguity Detection Patterns

### Pattern 1: Under-Specification

**Symptoms**:
- Vague verbs ("improve", "optimize", "enhance")
- Missing details ("add authentication" - which method?)
- No success criteria ("make it better" - how to measure?)
- Unclear scope ("update the dashboard" - which parts?)

**Examples**:
```
❌ Ambiguous: "Add authentication"
  Missing: Authentication method? OAuth? JWT? Sessions?
  Missing: Which endpoints to protect?
  Missing: User registration flow?
  Missing: Password requirements?

❌ Ambiguous: "Optimize performance"
  Missing: Which component? Backend? Frontend? Database?
  Missing: Current performance metrics?
  Missing: Target performance metrics?
  Missing: Performance vs. other trade-offs?

❌ Ambiguous: "Improve the dashboard"
  Missing: Which aspects? UI? Performance? Features?
  Missing: What's wrong with current dashboard?
  Missing: User feedback or requirements?
  Missing: Success criteria?
```

**Clarification Approach**:
```
✅ Clarify: "Add authentication"
  Questions:
    - Authentication method? (OAuth, JWT, sessions, or other?)
    - Endpoints to protect? (All? Specific routes?)
    - User registration included? (New users? Existing only?)
    - Password requirements? (Complexity, hashing algorithm?)
    - Rate limiting? (Login attempts, API calls?)
    - Session management? (Expiration, refresh tokens?)

Result: "Add JWT-based authentication with bcrypt hashing to /auth/login
         and /auth/refresh endpoints. Protect /api/* routes. Include rate
         limiting (5 attempts/min). 15min access token, 7d refresh token."
```

---

### Pattern 2: Conflicting Constraints

**Symptoms**:
- Incompatible goals ("fast AND comprehensive")
- Contradictory requirements ("secure but no authentication")
- Resource conflicts ("urgent but low priority")
- Technical conflicts ("support IE11 AND use modern JS")

**Examples**:
```
❌ Conflicting: "Comprehensive data profiling, must complete in 1 minute"
  Conflict: Thorough analysis vs. speed constraint

❌ Conflicting: "Maximum security, but keep development simple"
  Conflict: Security rigor vs. simplicity

❌ Conflicting: "Support all browsers, use latest React features"
  Conflict: Broad compatibility vs. modern features
```

**Resolution Approach**:
```
✅ Resolve: "Comprehensive data profiling, must complete in 1 minute"
  Trade-off discussion:
    Option A: Fast profiling (1 min) - basic schema, quality checks only
    Option B: Comprehensive profiling (10 min) - full analysis including bias
    Option C: Tiered profiling - critical checks first (1 min), full report async

  [User selects Option C]

Result: "Run critical profiling checks (schema, leakage, split contamination)
         within 1 minute. Generate full profiling report (bias, fairness,
         integrity) asynchronously in background."
```

---

### Pattern 3: Implicit Assumptions

**Symptoms**:
- "Obviously we need..." (not obvious)
- "Of course it should..." (no, not of course)
- "Everyone knows..." (we don't)
- Missing context (assumes familiarity)

**Examples**:
```
❌ Implicit: "Add the payment integration"
  Assumption: Which payment provider? (Stripe? PayPal? Square?)
  Assumption: Which payment methods? (Credit card? ACH? Crypto?)
  Assumption: Existing payment infrastructure? (First time? Migration?)

❌ Implicit: "Follow our conventions"
  Assumption: What conventions? (Documented? Oral tradition?)
  Assumption: Which conventions apply? (Naming? Structure? Testing?)
  Assumption: Exceptions allowed? (When to deviate?)

❌ Implicit: "Make it production-ready"
  Assumption: What defines production-ready? (Tests? Docs? Monitoring?)
  Assumption: Performance requirements? (SLAs? Load expectations?)
  Assumption: Security requirements? (Compliance? Audit needs?)
```

**Surfacing Approach**:
```
✅ Surface: "Add the payment integration"
  Explicit questions:
    - Payment provider? (Stripe, PayPal, Square, other?)
    - Payment methods? (Card, ACH, digital wallet?)
    - First integration or migration? (Existing payment code?)
    - Transaction storage? (Database schema? Audit requirements?)
    - Error handling? (Failed payments, retries, refunds?)
    - Testing approach? (Sandbox? Test mode?)
    - Security requirements? (PCI compliance? Tokenization?)

Result: "Integrate Stripe payment processing for credit card and ACH. Store
         transactions in payments table with audit trail. Handle failures
         with exponential backoff. Use Stripe test mode for development.
         Ensure PCI compliance (no raw card storage)."
```

---

### Pattern 4: Scope Creep Indicators

**Symptoms**:
- "And also..." (expanding scope)
- "While you're at it..." (additional work)
- "Plus we need..." (feature creep)
- "Don't forget..." (hidden requirements)

**Examples**:
```
❌ Scope creep: "Add login, and also registration, and password reset,
                 and email verification, and 2FA, and social auth..."
  Problem: Started with "add login", expanded to full auth system

❌ Scope creep: "Fix the bug, and also refactor the module, and add tests,
                 and update documentation, and improve performance..."
  Problem: Started with bug fix, expanded to major overhaul
```

**Scope Bounding**:
```
✅ Bound scope: "Add login, and also registration, and password reset..."

  Core scope (current request):
    - Login endpoint (authentication)
    - Basic registration (username, password)

  Deferred scope (future requests):
    - Password reset (separate task)
    - Email verification (separate task)
    - 2FA (separate task)
    - Social auth (separate task)

  Rationale: Each is substantial feature requiring separate design,
             implementation, and testing. Deliver incrementally.

Result: "Implement login (POST /auth/login) and registration (POST /auth/register)
         with JWT tokens. Password reset and other auth features deferred to
         separate requests."
```

---

## Clarification Question Templates

### Domain-Specific Templates

**For Code Implementation**:
```
- What is the desired behavior? (Functional requirements)
- What existing code/patterns should be followed? (Integration)
- What tests are needed? (Verification)
- What should NOT be modified? (Boundaries)
- What are the performance requirements? (Non-functional)
- What error handling is expected? (Edge cases)
```

**For Data Analysis**:
```
- What is the dataset structure? (Schema, format, size)
- What specific metrics are needed? (Analysis goals)
- What risks are highest priority? (Leakage? Bias? Quality?)
- What is the ML task type? (Classification? Regression?)
- What compliance requirements exist? (Privacy, fairness)
- What visualization is needed? (Reports, dashboards)
```

**For Architecture/Design**:
```
- What are the quality attributes? (Performance, scalability, security)
- What constraints exist? (Budget, timeline, platform)
- What patterns are preferred? (Existing architecture)
- What trade-offs are acceptable? (Performance vs. maintainability)
- What future changes are anticipated? (Extensibility needs)
- What integration points exist? (External systems)
```

**For Refactoring**:
```
- What specific code smells exist? (Long methods, duplication)
- What is the acceptable diff size? (Risk tolerance)
- What tests exist currently? (Safety net)
- What behavior must be preserved? (Regression constraints)
- What patterns should be introduced? (Target architecture)
- What technical debt is highest priority? (Impact vs. effort)
```

---

## Feasibility Assessment Checklist

Before proceeding to decomposition:

**Technical Feasibility**:
- [ ] Required expertise available? (Specialist match)
- [ ] Technology stack compatible? (No incompatible requirements)
- [ ] External dependencies manageable? (APIs, services accessible)
- [ ] Technical risks identified? (Known challenges)

**Resource Feasibility**:
- [ ] Sufficient time available? (Timeline realistic)
- [ ] Specialists available? (Not oversubscribed)
- [ ] External resources accessible? (Data, APIs, credentials)
- [ ] Tooling available? (Development environment)

**Scope Feasibility**:
- [ ] Request well-scoped? (Not too vague, not too expansive)
- [ ] Success criteria measurable? (Objective verification)
- [ ] Constraints compatible? (No conflicting requirements)
- [ ] Dependencies manageable? (No circular dependencies)

**Risk Assessment**:
- [ ] High-risk areas identified? (Security, data loss, breaking changes)
- [ ] Mitigation strategies exist? (Testing, rollback, monitoring)
- [ ] Unknown unknowns acknowledged? (Areas needing research)
- [ ] Failure modes considered? (Graceful degradation plan)

---

## Request Classification

### Type 1: Well-Specified (Ready to Decompose)

**Characteristics**:
- Clear functional requirements
- Measurable success criteria
- Explicit constraints
- Defined scope boundaries
- No conflicting requirements

**Example**:
```
Request: "Implement JWT authentication for /auth/login endpoint with bcrypt
         hashing (12 salt rounds), 15min access token expiration, 7d refresh
         token expiration. Rate limit to 5 login attempts per minute per IP.
         Include unit tests (token generation, validation) and integration
         tests (login flow)."

Assessment: ✅ Ready to decompose
  - Clear requirements (JWT, bcrypt, rate limiting)
  - Measurable criteria (token expirations, rate limits)
  - Explicit constraints (algorithm choices, timing)
  - Defined scope (login endpoint, specific features)
  - Testable (unit + integration tests specified)
```

---

### Type 2: Under-Specified (Needs Clarification)

**Characteristics**:
- Vague requirements
- Missing details
- Unclear success criteria
- Ambiguous scope

**Example**:
```
Request: "Add authentication to the API"

Assessment: ❌ Needs clarification
  Missing: Authentication method?
  Missing: Which endpoints to protect?
  Missing: User management approach?
  Missing: Success criteria?

Action: Ask clarifying questions (see templates above)
```

---

### Type 3: Over-Specified (Needs Simplification)

**Characteristics**:
- Too many requirements
- Scope too large
- Multiple distinct features
- Should be decomposed before acceptance

**Example**:
```
Request: "Build complete user management system with authentication,
         authorization, user profiles, social login, 2FA, password reset,
         email verification, admin dashboard, user analytics, and audit logs"

Assessment: ⚠️ Needs decomposition
  Problem: 10+ distinct features
  Problem: Spans multiple sprints
  Problem: Multiple failure points

Action: Break into smaller, incremental requests
  Request 1: Core authentication (login/register)
  Request 2: User profiles
  Request 3: Password reset
  Request 4: Email verification
  [etc.]
```

---

### Type 4: Conflicting (Needs Resolution)

**Characteristics**:
- Incompatible requirements
- Contradictory constraints
- Impossible trade-offs

**Example**:
```
Request: "Comprehensive ML model evaluation with statistical significance
         testing, must complete in under 5 seconds"

Assessment: ⚠️ Conflicting constraints
  Conflict: Thoroughness vs. speed

Action: Resolve trade-offs with user
  Option A: Fast evaluation (5s) - basic metrics only
  Option B: Comprehensive evaluation (60s) - full statistical tests
  Option C: Tiered evaluation - critical metrics fast, full report async
```

---

## Request Analysis Workflow

**Step 1: Initial Parse**
- Read request carefully
- Identify key verbs (implement, fix, analyze, optimize)
- Identify key nouns (components, systems, data)
- Note any red flags (vague terms, "and also", missing details)

**Step 2: Ambiguity Detection**
- Check for under-specification (missing details)
- Check for conflicting constraints (incompatible goals)
- Check for implicit assumptions (unstated expectations)
- Check for scope creep indicators (expanding requirements)

**Step 3: Clarification (if needed)**
- Generate clarifying questions (use templates)
- Ask user for missing details
- Resolve conflicts and trade-offs
- Bound scope explicitly

**Step 4: Feasibility Assessment**
- Assess technical feasibility
- Assess resource availability
- Identify risks and mitigation strategies
- Determine go/no-go

**Step 5: Classification**
- Well-specified → Proceed to decomposition
- Under-specified → Clarify first
- Over-specified → Break into smaller requests
- Conflicting → Resolve trade-offs

**Step 6: Document Understanding**
- Restate request clearly
- List success criteria explicitly
- Document constraints and boundaries
- Acknowledge assumptions

---

## Common Request Patterns

### Pattern: "Add Feature X"

**Clarifications Needed**:
- What specific behavior?
- What integration points?
- What tests required?
- What should NOT change?

**Example**: "Add search functionality"
- Search what? (Users? Products? Content?)
- Search algorithm? (Full-text? Fuzzy? Filters?)
- Search UI? (Search bar? Advanced filters?)
- Search performance? (Response time? Result ranking?)

---

### Pattern: "Fix Bug Y"

**Clarifications Needed**:
- What is the current behavior?
- What is the expected behavior?
- How to reproduce?
- What is the impact?

**Example**: "Fix the login bug"
- What specific bug? (Error message? Behavior?)
- When does it occur? (Always? Specific conditions?)
- What's the expected behavior?
- Any error logs or stack traces?

---

### Pattern: "Optimize Z"

**Clarifications Needed**:
- What metric to optimize?
- Current vs. target performance?
- What trade-offs acceptable?
- How to measure success?

**Example**: "Optimize the database"
- Which queries are slow?
- Current performance metrics?
- Target performance metrics?
- Acceptable trade-offs? (Memory vs. speed? Normalization vs. denormalization?)

---

### Pattern: "Analyze Dataset D"

**Clarifications Needed**:
- What specific analysis?
- What risks/issues to detect?
- What output format?
- What compliance requirements?

**Example**: "Analyze the customer dataset"
- What analysis goals? (Quality? Bias? Leakage?)
- ML task type? (Classification? Regression?)
- Sensitive attributes? (Age, gender, race?)
- Compliance requirements? (GDPR? CCPA?)

---

## Anti-Patterns

### Anti-Pattern 1: Assumption Without Confirmation

**Problem**: Assume details, proceed without verification

**Example**:
```
Request: "Add authentication"
[Assume JWT, proceed to implementation]
[User wanted OAuth, rework required]
```

**Fix**: Always clarify ambiguous requests

---

### Anti-Pattern 2: Accepting Conflicting Requirements

**Problem**: Accept contradictions, hope for best

**Example**:
```
Request: "Comprehensive profiling in 30 seconds"
[Proceed with comprehensive profiling]
[Takes 10 minutes, user complains about speed]
```

**Fix**: Surface conflicts, resolve upfront

---

### Anti-Pattern 3: Ignoring Scope Creep

**Problem**: Accept expanding scope without pushback

**Example**:
```
Request: "Fix login bug, and also add 2FA, and refactor auth module..."
[Accept entire scope]
[Overwhelmed, incomplete delivery]
```

**Fix**: Bound scope, defer secondary requests

---

## Success Criteria

Request analysis complete when:

- ✅ All ambiguity resolved (no missing details)
- ✅ Conflicts identified and resolved (no contradictions)
- ✅ Assumptions made explicit (no implicit expectations)
- ✅ Scope clearly bounded (in/out of scope documented)
- ✅ Success criteria measurable (objective verification)
- ✅ Feasibility assessed (technical, resource, risk)
- ✅ Request classification determined (ready vs. needs work)
- ✅ User understanding confirmed (restate and verify)

---

## Output Format

**Request Analysis Report**:
```
Original Request: [user's original request]

Clarified Request: [clear, unambiguous restatement]

Success Criteria:
  - [measurable criterion 1]
  - [measurable criterion 2]
  - [measurable criterion 3]

Scope:
  In Scope:
    - [feature/task 1]
    - [feature/task 2]
  Out of Scope (deferred):
    - [feature/task 3]
    - [feature/task 4]

Constraints:
  - [constraint 1]
  - [constraint 2]

Assumptions:
  - [assumption 1]
  - [assumption 2]

Risks:
  - [risk 1 + mitigation]
  - [risk 2 + mitigation]

Feasibility: [Ready / Needs Clarification / Needs Decomposition]

Next Step: [Proceed to decomposition / Ask clarifying questions / Break into smaller requests]
```

---

## Integration with Decomposition Phase

Once request analysis complete:
- Clear request → Load decomposition/strategies.md
- Identified dependencies → Load decomposition/dependency-analysis.md
- Multiple domains → Decomposition by domain
- Sequential phases → Decomposition by phase

Request analysis provides foundation for effective decomposition.

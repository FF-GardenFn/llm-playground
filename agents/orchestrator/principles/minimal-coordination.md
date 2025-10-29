# Principle: Minimal Coordination Overhead

**Core Insight**: Coordination overhead grows quadratically with communication frequency. Minimize touchpoints to maximize parallel efficiency.

---

## The Coordination Problem

**Context**: When managing parallel work, there's a natural tension:
- **Too much coordination**: Constant check-ins, status meetings, blocking on approvals → work slows down
- **Too little coordination**: Duplicate work, conflicts, misaligned outputs → rework required

**Solution**: Design for **autonomy with clear boundaries**

---

## Key Principles

### 1. Trust Specialist Expertise

**Don't micromanage implementation**:
- ✅ **Do**: Provide clear scope, success criteria, and context
- ❌ **Don't**: Dictate how to implement, ask for progress updates, review intermediate steps

**Example**:
```
✅ Good delegation:
  Specialist: code-generator
  Scope: "Add JWT authentication to /auth/login endpoint"
  Success criteria: "Tests pass, tokens validated correctly, no security issues"
  Context: "Flask app, existing user model, bcrypt for hashing"
  Boundaries: "Don't modify existing /user routes"

  [code-generator works independently until completion]

❌ Bad delegation:
  Specialist: code-generator
  [Ask: "What's your approach?"]
  [Ask: "How's progress?"]
  [Ask: "Can I see intermediate code?"]
  [Ask: "Are you following pattern X?"]

  [constant interruptions, coordination overhead]
```

**Why it works**: Specialists know their domain better than orchestrator. Trust their process.

---

### 2. Track Completion, Not Progress

**Signal-based coordination**:
- ✅ **Do**: Specialists signal when done (binary: complete or failed)
- ❌ **Don't**: Ask "how far along are you?" or "when will you finish?"

**Example**:
```
✅ Good monitoring:
  Assign tasks → Specialists work → Specialists signal completion

  [orchestrator checks only on completion signal]

❌ Bad monitoring:
  Assign tasks → Check progress every 10 minutes → Ask for ETAs → Review partial work

  [constant context switching, slow progress]
```

**Why it works**: Progress tracking is expensive. Most tasks either complete or fail—intermediate states don't matter.

---

### 3. Intervene Only When Needed

**When to intervene**:
- ✅ Specialist explicitly signals failure
- ✅ Blocking dependency detected
- ✅ Conflict between specialists detected
- ✅ Deadline at risk (escalate to user)

**When NOT to intervene**:
- ❌ Specialist is taking longer than expected (trust process)
- ❌ Curious about approach (trust expertise)
- ❌ Want status update (wait for completion)
- ❌ Worried about quality (verification happens at integration)

**Example**:
```
✅ Good intervention:
  code-generator signals: "Blocked—need API spec from backend team"
  orchestrator: Resolves blocking dependency or escalates

❌ Bad intervention:
  [15 minutes pass]
  orchestrator: "How's it going?"
  code-generator: [context switch, progress slowed]
```

**Why it works**: Interruptions are expensive. Only intervene when adding value.

---

### 4. Batch Communication

**Minimize touchpoints**:
- ✅ **Do**: Provide all context upfront, get all outputs at completion
- ❌ **Don't**: Back-and-forth clarifications, iterative refinements, frequent check-ins

**Example**:
```
✅ Good batching:
  Initial: Provide complete context (scope, criteria, boundaries, background)
  [specialist works]
  Completion: Collect complete outputs (code, tests, notes, verification)

❌ Bad batching:
  Initial: Assign task
  [specialist asks: "What's the user model structure?"]
  [specialist asks: "Should I use bcrypt or argon2?"]
  [specialist asks: "Where should I put tests?"]

  [each question is a round-trip, context switch, delay]
```

**Why it works**: Context switching is expensive. Batch all communication at boundaries.

---

## Coordination Overhead Calculation

**Cost Model**:
```
Total_Time = Work_Time + Coordination_Overhead

Coordination_Overhead = N * (N-1) * Communication_Cost

Where:
  N = Number of touchpoints
  Communication_Cost = Average time per touchpoint (context switch, response delay)
```

**Example**:
```
Scenario A: Minimal Coordination
  - 1 initial touchpoint (context provision)
  - 1 final touchpoint (output collection)
  - Total touchpoints: 2
  - Overhead: 2 * 1 * 5min = 10min

Scenario B: High Coordination
  - 1 initial touchpoint
  - 10 progress checks
  - 5 clarifications
  - 1 final touchpoint
  - Total touchpoints: 17
  - Overhead: 17 * 16 * 5min = 1360min (22 hours!)
```

**Takeaway**: Reduce touchpoints dramatically to reduce overhead.

---

## Design Patterns for Autonomy

### Pattern 1: Contract-First Interfaces

**Define contracts upfront, implement independently**:

```
Step 1: Define interface contract
  Input: { user_id: int, permissions: list }
  Output: { access_token: str, refresh_token: str, expires_at: datetime }

Step 2: Specialists implement independently
  Backend specialist: Implements token generation (respects contract)
  Frontend specialist: Implements token consumption (respects contract)

Step 3: Integration verification
  Test: Contracts met? → Merge

[No coordination during implementation, contracts ensure compatibility]
```

**Why it works**: Clear contracts eliminate need for coordination during work.

---

### Pattern 2: Asynchronous Work Streams

**Specialists work on independent streams, merge at end**:

```
Stream A: Frontend components (react-architect → code-generator)
Stream B: Backend API (code-generator)
Stream C: Data pipeline (data-profiler → ml-trainer)

[Streams work independently, no inter-stream communication]

Merge Point: Integration layer coordinates

[Coordination only at merge, not during work]
```

**Why it works**: Independence eliminates coordination during execution.

---

### Pattern 3: Self-Verification

**Specialists verify their own work before signaling completion**:

```
Specialist workflow:
  1. Implement feature
  2. Write tests
  3. Run tests (self-verification)
  4. If tests pass → Signal completion
  5. If tests fail → Fix and retry (no external coordination)

Orchestrator:
  - Receives completion signal only after self-verification passes
  - Trusts specialist's verification process

[No orchestrator involvement in verification loop]
```

**Why it works**: Specialists catch issues internally, don't escalate prematurely.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Micromanagement

**Symptoms**:
- Constant "how's it going?" questions
- Reviewing intermediate work
- Dictating implementation approach
- Frequent status meetings

**Cost**: Work time → coordination time

**Fix**: Provide clear context upfront, trust expertise, track completion only

---

### Anti-Pattern 2: Synchronous Coordination

**Symptoms**:
- Specialists wait for approval before proceeding
- Decisions require orchestrator sign-off
- Blocking on responses

**Cost**: Idle time while waiting

**Fix**: Pre-approve common decisions, empower specialists, batch approvals

---

### Anti-Pattern 3: Shared Mutable State

**Symptoms**:
- Multiple specialists modifying same files simultaneously
- Race conditions in concurrent work
- Merge conflicts frequent

**Cost**: Conflict resolution overhead

**Fix**: Partition work to avoid overlaps, use immutable contracts, merge systematically

---

### Anti-Pattern 4: Unclear Boundaries

**Symptoms**:
- Specialists ask "is this in scope?"
- Duplicate work across specialists
- Confusion about responsibilities

**Cost**: Clarification round-trips, rework

**Fix**: Define boundaries explicitly upfront (in scope, out of scope, gray areas)

---

## Measuring Coordination Efficiency

**Metrics**:
```
Coordination_Efficiency = Work_Time / (Work_Time + Coordination_Overhead)

Target: >90% (less than 10% overhead)
Warning: <80% (more than 20% overhead)
Critical: <70% (more than 30% overhead)
```

**Example**:
```
Good orchestration:
  Work time: 4 hours
  Coordination: 20 minutes
  Efficiency: 4h / (4h + 0.33h) = 92% ✅

Poor orchestration:
  Work time: 4 hours
  Coordination: 2 hours (constant check-ins)
  Efficiency: 4h / (4h + 2h) = 67% ❌
```

**Improvement Strategies**:
- Reduce touchpoint frequency
- Batch communication
- Increase specialist autonomy
- Clarify boundaries upfront
- Use contracts for interfaces

---

## Coordination Checklist

Before assigning work:

- [ ] Context complete (scope, criteria, boundaries, background)
- [ ] Success criteria measurable (specialist can self-verify)
- [ ] Interfaces defined (inputs, outputs, contracts)
- [ ] Dependencies resolved (no blocking on other work)
- [ ] Boundaries clear (in scope, out of scope, explicitly stated)
- [ ] Specialist has autonomy (no approval gates during work)
- [ ] Communication plan (initial + final touchpoints only)

During execution:

- [ ] Trust specialist process (no progress checks)
- [ ] Intervene only on explicit failure signal
- [ ] Detect blocking dependencies early (remove blockers)
- [ ] Avoid synchronous coordination (asynchronous by default)

After completion:

- [ ] Collect outputs in batch (don't ask incrementally)
- [ ] Verify against success criteria (objective measurement)
- [ ] Integrate systematically (merge verification, rollback on failure)

---

## Real-World Example

**Scenario**: Add user authentication system

### ❌ High-Coordination Approach (Poor)

```
Orchestrator assigns: "Add authentication"
  [5 min]
code-generator asks: "What hashing algorithm?"
  [orchestrator responds: bcrypt]
  [10 min]
code-generator asks: "Where to store tokens?"
  [orchestrator responds: JWT]
  [15 min]
code-generator asks: "Token expiration?"
  [orchestrator responds: 15 min]
  [20 min]
code-generator: "Done implementation"
  [orchestrator reviews code]
  [30 min]
orchestrator: "Use environment variable for secret"
  [code-generator fixes]
  [10 min]
code-generator: "Fixed"
  [orchestrator reviews again]
  [15 min]
orchestrator: "Approved"

Total time: 120 min work + 90 min coordination = 210 min (43% overhead)
```

### ✅ Low-Coordination Approach (Good)

```
Orchestrator assigns:
  Scope: "Add JWT authentication to /auth/login endpoint"
  Success criteria: "Tests pass, tokens validated, no security issues"
  Context:
    - Use bcrypt for password hashing (salt rounds: 12)
    - JWT with 15min expiration for access, 7d for refresh
    - Secret from environment variable (JWT_SECRET)
    - Rate limit: 5 attempts per minute
    - Flask app structure, existing user model
  Boundaries: "Don't modify existing /user routes"

  [code-generator works autonomously]

code-generator signals: "Complete"
  Outputs:
    - JWT generation/validation module
    - Login endpoint
    - Refresh endpoint
    - Auth middleware
    - 15 tests (all passing)
    - Verification notes

Orchestrator verifies: All criteria met → Merge

Total time: 120 min work + 10 min coordination = 130 min (8% overhead)
```

**Savings**: 80 minutes (38% faster) by reducing coordination overhead

---

## Summary

**Core Principles**:
1. **Trust expertise**: Let specialists work their way
2. **Track completion**: Not progress
3. **Intervene strategically**: Only when adding value
4. **Batch communication**: Minimize touchpoints

**Key Metrics**:
- Coordination efficiency >90%
- Touchpoints <5 per task
- Context switches minimized

**Design Patterns**:
- Contract-first interfaces
- Asynchronous work streams
- Self-verification

**Anti-Patterns**:
- Micromanagement
- Synchronous coordination
- Shared mutable state
- Unclear boundaries

**Goal**: Maximize specialist autonomy while maintaining coordination where it adds value.

# Monitoring Patterns: Tracking Work Without Micromanagement

**Purpose**: Effective progress monitoring with minimal coordination overhead

---

## Core Principle

**Track completion, not progress**

Specialists signal when done (binary: complete or failed), not incremental progress updates.

**Why**: Constant check-ins create coordination overhead and slow work. Trust specialists to complete autonomously.

---

## Monitoring Pattern 1: Signal-Based Completion

**Approach**: Specialists signal completion explicitly

**Implementation**:
```
Specialist workflow:
  1. Receive task assignment
  2. Work independently
  3. Self-verify completion
  4. Signal: "Complete" or "Failed: [reason]"

Orchestrator workflow:
  1. Assign task
  2. Wait for completion signal (no intermediate checks)
  3. Collect outputs when signal received
  4. Verify outputs meet success criteria
```

**Benefits**:
- Minimal coordination overhead
- Specialists work without interruption
- Clear completion state

**Signals**:
- ✅ Complete: Task finished, success criteria met
- ❌ Failed: Task cannot complete, requires intervention
- ⚠️ Blocked: Task waiting on dependency

**Example**:
```
Assign code-generator: "Implement JWT authentication"
  [code-generator works autonomously]
  [no progress checks]
  [code-generator signals: "Complete"]
Collect outputs: JWT module, tests, verification notes
Verify: Tests pass ✅, security criteria met ✅
Proceed to next phase
```

---

## Monitoring Pattern 2: Fail-Fast Detection

**Approach**: Detect failures early to minimize wasted effort

**Implementation**:
```
Specialist detects failure condition:
  - Blocking dependency unavailable
  - Technical impossibility discovered
  - Resource unavailable
  - Scope fundamentally unclear

Specialist signals failure immediately (don't continue)

Orchestrator responds:
  - Resolve blocking dependency
  - Adjust scope or approach
  - Reassign to different specialist
  - Escalate to user
```

**Failure Signals**:
```
Blocked: "Waiting on API spec from backend team"
→ Orchestrator resolves dependency

Failed: "Feature requires library not in tech stack"
→ Orchestrator adjusts approach or escalates

Failed: "Requirements contradictory"
→ Orchestrator clarifies requirements
```

**Benefits**:
- Prevents wasted effort
- Enables rapid replanning
- Surfaces issues early

**Example**:
```
Assign code-generator: "Integrate with payment API"
  [code-generator starts work]
  [discovers: API credentials not available]
  [signals: "Blocked: Missing API credentials"]
Orchestrator: Obtains credentials, unblocks
  [code-generator resumes]
  [signals: "Complete"]
```

---

## Monitoring Pattern 3: Timeout-Based Escalation

**Approach**: Escalate if task takes unreasonably long

**Implementation**:
```
Estimate expected duration for task
Set timeout = expected_duration * safety_factor (e.g., 2x or 3x)

If timeout exceeded:
  - Check specialist status
  - Investigate blocking issues
  - Determine if task needs adjustment
  - Escalate if necessary
```

**Safety Factors**:
- Simple task: 2x (expected 1hr, timeout 2hr)
- Complex task: 3x (expected 4hr, timeout 12hr)
- Research task: 5x (high uncertainty)

**Example**:
```
Task: Implement login endpoint
Expected duration: 2 hours
Timeout: 6 hours (3x safety factor)

If 6 hours pass without completion:
  → Check: Specialist blocked?
  → Investigate: Unexpected complexity?
  → Action: Adjust timeline or provide help
```

**Note**: This is backup mechanism, not primary monitoring. Most tasks complete within expected timeframe.

---

## Monitoring Pattern 4: Dependency-Aware Monitoring

**Approach**: Monitor based on dependency graph

**Implementation**:
```
For each level in parallelization graph:
  Assign all tasks in level
  Wait for ALL tasks in level to complete
  Verify outputs before proceeding to next level

Don't monitor within level (tasks are independent)
Only monitor level completion
```

**Example**:
```
Level 0: [A] → Assign A, wait for completion ✅
Level 1: [B] → Assign B, wait for completion ✅
Level 2: [C, D] → Assign C and D in parallel, wait for BOTH ✅
Level 3: [E] → Assign E (depends on C and D), wait for completion ✅

Monitoring points: End of each level only
Within-level monitoring: None (tasks independent)
```

**Benefits**:
- Respects dependency structure
- Minimizes coordination points
- Natural synchronization at level boundaries

---

## Monitoring Pattern 5: Bottleneck Detection

**Approach**: Identify tasks on critical path that delay overall completion

**Implementation**:
```
From dependency analysis:
  - Identify critical path
  - Track critical path task durations
  - Detect if critical path tasks exceed estimates

If critical path task delayed:
  - Investigate cause
  - Consider resource reallocation
  - Adjust timeline expectations
```

**Example**:
```
Critical path: A → B → C → E → F → H
Non-critical: D, G (can parallel)

If C delayed by 2x:
  → Overall timeline affected
  → Priority: Unblock C
  → Consider: Can C be split to parallelize?

If D delayed by 2x:
  → Overall timeline NOT affected (D not on critical path)
  → Priority: Lower (doesn't block other work)
```

**Benefits**:
- Focus attention where it matters
- Optimize overall timeline
- Avoid over-reacting to non-critical delays

---

## Monitoring Pattern 6: Output Validation at Boundaries

**Approach**: Verify outputs at synchronization points, not continuously

**Implementation**:
```
Synchronization points:
  - End of parallelization level
  - Before dependent work starts
  - Before integration/merge

At synchronization point:
  - Collect all outputs
  - Verify completeness (all expected artifacts present)
  - Validate quality (success criteria met)
  - Proceed only if verification passes
```

**Validation Checks**:
```
Completeness:
  - All expected files present?
  - All expected features implemented?
  - All tests written?

Quality:
  - Tests pass?
  - Code follows conventions?
  - No obvious errors?

Format:
  - Output format matches expectations?
  - Compatible with next phase?
```

**Example**:
```
Synchronization: After implementation phase, before testing phase

Collect outputs:
  - JWT module ✅
  - Login endpoint ✅
  - Refresh endpoint ✅
  - Auth middleware ✅

Verify completeness:
  - All components present ✅

Verify quality:
  - Tests pass ✅
  - Code follows conventions ✅

Proceed to testing phase ✅
```

---

## Monitoring Anti-Patterns

### Anti-Pattern 1: Micromanagement

**Problem**: Constantly checking "how's it going?"

**Symptoms**:
- Frequent status requests
- Interrupting specialists
- Asking for intermediate artifacts
- Reviewing partial work

**Impact**:
- Context switching
- Slower progress
- Coordination overhead

**Fix**: Trust specialists, track completion only

---

### Anti-Pattern 2: Progress-Based Monitoring

**Problem**: Asking "how far along are you?"

**Symptoms**:
- Percentage estimates ("50% done")
- ETA requests ("when will you finish?")
- Milestone tracking within task

**Impact**:
- Inaccurate estimates
- Premature optimization
- Wasted communication

**Fix**: Wait for completion signal

---

### Anti-Pattern 3: Synchronous Waiting

**Problem**: Orchestrator blocks waiting for single specialist

**Symptoms**:
- Idle time while waiting
- Serial when could be parallel
- Underutilized resources

**Impact**:
- Longer overall timeline
- Inefficient resource use

**Fix**: Assign parallel work, monitor all completions

---

### Anti-Pattern 4: Ignoring Failures

**Problem**: Not detecting failures early

**Symptoms**:
- Specialist continues despite blocking issue
- Wasted effort on doomed task
- Late discovery of problems

**Impact**:
- Rework required
- Timeline delays
- Resource waste

**Fix**: Enable fail-fast signals, respond immediately

---

## Monitoring Metrics

**Coordination Efficiency**:
```
Efficiency = Work_Time / (Work_Time + Coordination_Time)
Target: >90% (less than 10% overhead)
```

**Failure Detection Speed**:
```
Detection_Speed = Time_to_Signal_Failure
Target: <30 minutes from blocking issue
```

**Completion Accuracy**:
```
Accuracy = Tasks_Completed_Successfully / Total_Tasks
Target: >95%
```

**Timeline Adherence**:
```
Adherence = Actual_Duration / Expected_Duration
Target: 0.8-1.2 (within 20% of estimate)
```

---

## Monitoring Checklist

For each assigned task:

- [ ] Expected duration estimated
- [ ] Timeout threshold set (safety factor applied)
- [ ] Success criteria defined (specialist knows when done)
- [ ] Completion signal mechanism established
- [ ] Failure signal mechanism established
- [ ] No progress monitoring planned (trust completion)
- [ ] Synchronization point identified (when to verify)
- [ ] Validation criteria prepared (how to verify outputs)

During execution:

- [ ] Wait for completion signal (don't interrupt)
- [ ] Respond immediately to failure signals
- [ ] Escalate if timeout exceeded
- [ ] Verify outputs at synchronization points
- [ ] Track critical path tasks more closely
- [ ] Ignore non-critical delays (don't over-react)

---

## Integration with Other Phases

**Dependency Analysis Integration**:
- Use parallelization levels for monitoring structure
- Monitor at level boundaries, not within levels
- Focus on critical path tasks

**Verification Integration**:
- Monitoring identifies when to verify (at synchronization points)
- Verification validates outputs before proceeding
- Failed verification triggers replanning

**Merge Integration**:
- Monitoring ensures all specialists complete before merge
- Collect all outputs at synchronization point
- Proceed to merge only when monitoring confirms readiness

---

## Example: Complete Monitoring Flow

**Task**: Implement authentication system

**Setup**:
```
Tasks: A (schema), B (JWT logic), C (login), D (refresh), E (middleware), F (tests)
Dependencies: A → B → [C, D] → E → F
Expected durations: A:1h, B:2h, C:1h, D:1h, E:1h, F:2h
Timeouts: A:3h, B:6h, C:3h, D:3h, E:3h, F:6h
```

**Execution**:
```
Assign A
  [Wait for completion signal]
  A signals: "Complete" at 0.5h ✅
  Verify: Schema documented ✅

Assign B
  [Wait for completion signal]
  B signals: "Complete" at 2h ✅
  Verify: JWT logic implemented, tests pass ✅

Assign C and D in parallel
  [Wait for BOTH completion signals]
  C signals: "Complete" at 1h ✅
  D signals: "Complete" at 1.5h ✅
  Verify: Both endpoints implemented, tests pass ✅

Assign E
  [Wait for completion signal]
  E signals: "Complete" at 1h ✅
  Verify: Middleware implemented, tests pass ✅

Assign F
  [Wait for completion signal]
  F signals: "Complete" at 2h ✅
  Verify: All tests pass, coverage adequate ✅

Total time: 8h
Coordination points: 5 (one per synchronization)
Coordination time: ~30min total (<7% overhead) ✅
```

---

## Summary

**Key Principles**:
1. Track completion, not progress
2. Enable fail-fast signals
3. Monitor at synchronization points only
4. Focus on critical path
5. Verify outputs before proceeding

**Benefits**:
- Minimal coordination overhead
- Early failure detection
- Clear completion state
- Efficient resource utilization

**Anti-Patterns to Avoid**:
- Micromanagement
- Progress-based monitoring
- Synchronous waiting
- Ignoring failures

**Integration**:
- Use with dependency analysis (monitoring structure)
- Use with verification (validation timing)
- Use with minimal coordination principle (overhead minimization)

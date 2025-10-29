# Progress Tracking Patterns

## Purpose

Monitor specialist work without micromanaging, identify blockers early, and maintain visibility into overall progress.

---

## Progress Tracking Model

### Three-State Model

```
ASSIGNED → Working on task, no output yet
IN_PROGRESS → Actively working, partial output
COMPLETE → Task finished, output delivered
```

**State Transitions**:
```
ASSIGNED: Initial state after delegation
    ↓ (specialist begins work)
IN_PROGRESS: Work underway, may have blockers
    ↓ (specialist delivers output)
COMPLETE: Ready for integration
```

### Extended State Model (When Needed)

```
ASSIGNED → Task delegated
ACKNOWLEDGED → Specialist confirmed understanding
IN_PROGRESS → Work underway
BLOCKED → Waiting on dependency/clarification
REVIEW → Output pending verification
COMPLETE → Verified and ready
```

---

## Progress Indicators

### Healthy Progress Patterns

✅ **Active Development**:
- Regular activity updates
- Incremental progress visible
- Questions asked when needed
- Early delivery of partial results

✅ **On Track**:
- Meeting intermediate milestones
- Staying within estimated time
- Proactive communication about challenges
- Dependencies resolved timely

✅ **Ahead of Schedule**:
- Faster than expected completion
- High-quality output
- Bonus improvements included
- Ready for next phase

### Warning Sign Patterns

⚠️ **Potential Issues**:
- No activity for extended period
- Repeated clarification questions
- Missed intermediate checkpoints
- Time estimate significantly exceeded

⚠️ **Blocked**:
- Explicit blocker reported
- Waiting on dependency
- Unclear requirements
- Technical obstacle

⚠️ **Quality Concerns**:
- Output doesn't match specifications
- Missing success criteria
- Integration issues
- Technical debt introduced

---

## Checkpoint Strategy

### Milestone-Based Checkpoints

```
For 2-hour task:
- 30 min: Initial approach confirmed
- 1 hour: 50% complete checkpoint
- 1.5 hours: 80% complete, prepare for delivery
- 2 hours: Complete and delivered

For 8-hour task:
- 2 hours: Architecture/approach confirmed
- 4 hours: Core implementation complete
- 6 hours: Integration and testing
- 8 hours: Complete and delivered
```

### Checkpoint Questions

```markdown
## 30-Minute Checkpoint
- Approach clear?
- Any blockers encountered?
- Estimates still accurate?

## 50% Checkpoint
- Core logic implemented?
- Integration points tested?
- Any requirement ambiguities?

## 80% Checkpoint
- Success criteria met?
- Edge cases handled?
- Ready for final testing?

## Completion
- All requirements satisfied?
- Tests passing?
- Documentation complete?
```

---

## Parallel Work Coordination

### Tracking Multiple Specialists

```
Orchestrator Dashboard (Mental Model):
┌─────────────────────────────────────────┐
│ Task A (Specialist 1)  ███████░░░  70%  │
│ Task B (Specialist 2)  ████████░░  80%  │
│ Task C (Specialist 3)  ██░░░░░░░░  20%  │
│ Task D (Specialist 4)  ██████████ 100%  │
└─────────────────────────────────────────┘

Critical Path: Task A → Task E (blocked)
Attention Needed: Task C (behind schedule)
Ready to Integrate: Task D
```

### Dependency Tracking

```
Task Graph:
A (COMPLETE) ──→ E (BLOCKED, waiting for A integration)
    ↓
B (IN_PROGRESS) ──→ F (ASSIGNED, waiting for B)
    ↓
C (IN_PROGRESS) ──→ G (ASSIGNED, waiting for B+C)
    ↓
D (COMPLETE) ────→ H (Can start now)
```

---

## Communication Patterns

### Non-Intrusive Monitoring

**Passive Monitoring** (Preferred):
- Check output artifacts
- Review commit history
- Monitor test results
- Observe progress indicators

**Active Check-ins** (When needed):
- Approaching deadlines
- Critical path tasks
- After extended silence
- When blockers suspected

### Effective Check-in Questions

```markdown
## Status Query Pattern

❌ Micromanaging:
"Did you finish function X? What about test Y?"

✓ High-level check:
"How's progress on the authentication module? Any blockers?"

❌ Vague:
"How's it going?"

✓ Specific:
"Are you on track for the 2-hour estimate? Any obstacles?"

❌ Pressuring:
"Why isn't this done yet?"

✓ Supportive:
"I see this is taking longer than expected. What can I clarify or provide?"
```

---

## Blocker Detection and Resolution

### Common Blocker Types

**Dependency Blockers**:
```
Symptom: "Waiting for Task X output"
Resolution: Check dependency status, expedite if needed

Symptom: "API not available yet"
Resolution: Provide mock, adjust sequence, or parallel path
```

**Clarity Blockers**:
```
Symptom: "Requirements unclear for case Y"
Resolution: Provide specific clarification, examples

Symptom: "Conflicting constraints"
Resolution: Prioritize constraints, provide tradeoff guidance
```

**Technical Blockers**:
```
Symptom: "Library X doesn't support feature Y"
Resolution: Suggest alternative approach, adjust requirements

Symptom: "Performance target not achievable with approach Z"
Resolution: Revise target or approve different approach
```

### Blocker Resolution Protocol

```
1. Identify Blocker
   - Specialist reports OR detected via monitoring
   - Classify type: dependency/clarity/technical

2. Assess Impact
   - Critical path affected?
   - Other tasks blocked?
   - Timeline impact?

3. Resolve Quickly
   - Provide information if clarity issue
   - Expedite dependency if possible
   - Adjust approach if technical issue
   - Escalate if outside orchestrator control

4. Communicate Resolution
   - Confirm specialist understands
   - Verify blocker removed
   - Update timeline if needed
```

---

## Progress Reporting

### Internal Progress Model

```python
class TaskProgress:
    def __init__(self, task_id, specialist, estimated_hours):
        self.task_id = task_id
        self.specialist = specialist
        self.estimated_hours = estimated_hours
        self.start_time = None
        self.state = "ASSIGNED"
        self.blockers = []
        self.checkpoints = []

    def calculate_progress(self):
        """Estimate progress based on time and checkpoints"""
        if self.state == "COMPLETE":
            return 1.0

        elapsed = time_since(self.start_time)
        time_progress = min(elapsed / self.estimated_hours, 1.0)

        checkpoint_progress = len(self.checkpoints) / expected_checkpoints

        # Weight time and checkpoints
        return 0.4 * time_progress + 0.6 * checkpoint_progress

    def is_behind_schedule(self):
        """Detect if task is falling behind"""
        progress = self.calculate_progress()
        expected = (time_since(self.start_time) / self.estimated_hours)

        return progress < (expected * 0.8)  # 20% tolerance
```

### Progress Visualization

```
Task Board View:
╔═══════════════╦═══════════════╦═══════════════╗
║   ASSIGNED    ║  IN PROGRESS  ║   COMPLETE    ║
╠═══════════════╬═══════════════╬═══════════════╣
║ Task F        ║ Task A ███░   ║ Task D ████   ║
║ (waiting B)   ║ Task B ████░  ║ Task G ████   ║
║               ║ Task C █░░░░  ║               ║
║               ║ (blocker!)    ║               ║
╚═══════════════╩═══════════════╩═══════════════╝

Critical Path: A → E → Final Integration
Attention: Task C blocked on clarification
Next to Complete: Task B (80% done)
```

---

## Risk Assessment

### Early Warning System

```
Risk Calculation:
- Time overrun: (actual / estimate) > 1.2 → ⚠️
- Blocker unresolved > 30 min → ⚠️
- Critical path task delayed → 🚨
- Multiple clarification requests → ⚠️
- No activity > 25% of estimate → ⚠️

Risk Levels:
🟢 Green: On track, no intervention needed
🟡 Yellow: Monitor closely, prepare to assist
🔴 Red: Active intervention required
```

### Risk Mitigation

```markdown
## When Yellow Alert Triggered

Actions:
1. Check in with specialist (non-intrusive)
2. Offer assistance/clarification
3. Identify potential blockers
4. Prepare backup plan

## When Red Alert Triggered

Immediate Actions:
1. Direct communication with specialist
2. Resolve blockers immediately
3. Adjust timeline or scope
4. Consider task reassignment if necessary
5. Update stakeholders on impact
```

---

## Completion Verification

### Pre-Integration Checks

```markdown
Before marking task COMPLETE:

**Output Verification:**
- [ ] Deliverable matches specification
- [ ] All success criteria met
- [ ] Tests passing (if applicable)
- [ ] Integration points validated

**Quality Gates:**
- [ ] Code review passed (if required)
- [ ] Security check passed (if required)
- [ ] Performance acceptable
- [ ] Documentation provided

**Integration Readiness:**
- [ ] Dependencies satisfied
- [ ] Interface contracts met
- [ ] No breaking changes
- [ ] Ready to merge
```

### Handoff Protocol

```
Specialist completes Task A:
    ↓
Orchestrator verifies completion
    ↓
Output prepared for integration
    ↓
Dependent tasks notified
    ↓
Integration proceeds
```

---

## Progress Communication Cadence

### Real-Time Updates (Ideal)

```
Specialist provides updates:
- When starting work
- At major checkpoints
- When blocked
- When complete

Orchestrator provides updates:
- When new information available
- When dependencies satisfied
- When priorities change
```

### Periodic Sync (Fallback)

```
For long-running tasks:
- Daily check-ins for multi-day work
- Hourly checks for critical path
- On-demand for blockers

Keep communication lightweight:
- Status, not details
- Blockers, not solutions
- Progress, not process
```

---

## Parallel Work Synchronization

### Managing Convergence Points

```
Multiple tasks converging:

Task A (80% complete) ──┐
Task B (90% complete) ──┼──→ Integration Point
Task C (95% complete) ──┘

Orchestrator actions:
1. Monitor fastest path (Task C)
2. Prepare integration environment
3. Ensure other tasks aligned with C
4. Begin integration planning
```

### Staggered Completion Handling

```
Task D completes early:
  → Hold for integration with E, F
  → Begin integration testing
  → Identify issues early
  → Adjust E, F if needed

Task E completes late:
  → Assess impact on timeline
  → Check if D, F can proceed
  → Adjust critical path
```

---

## Anti-Patterns in Progress Tracking

### Avoid These Mistakes

**❌ Micromanagement**:
```
Bad: "Did you write function X? What about Y?"
Good: "How's the module coming? Any blockers?"
```

**❌ Passive Neglect**:
```
Bad: No check-ins, find out task failed at deadline
Good: Regular checkpoints, early blocker detection
```

**❌ False Precision**:
```
Bad: "Task is exactly 67.3% complete"
Good: "Task is roughly 70% complete, on track"
```

**❌ Ignoring Early Warnings**:
```
Bad: Wait until deadline to address delays
Good: Intervene when task hits 1.2x estimate
```

---

## Progress Tracking Checklist

For effective progress monitoring:

- [ ] Each task has clear state (ASSIGNED/IN_PROGRESS/COMPLETE)
- [ ] Estimated time defined for each task
- [ ] Checkpoints established for long tasks
- [ ] Blockers identified and tracked
- [ ] Dependencies monitored
- [ ] Critical path visible
- [ ] Risks assessed regularly
- [ ] Communication cadence appropriate
- [ ] Completion criteria clear

---

*Progress tracking enables proactive orchestration. A Senior Engineering Manager monitors efficiently without micromanaging, intervening only when needed.*

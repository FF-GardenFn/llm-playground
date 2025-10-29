# GATE: Specialist Assignment Checkpoint

## ⚠️ MANDATORY CHECKPOINT - VALIDATE ALL ASSIGNMENTS

**Purpose**: Ensure each task is matched to the appropriate specialist cognitive model with proper context before parallel execution begins.

---

## Verification Checklist

**Assignment Validation:**

□ **Every task has assigned specialist**: No unassigned work
□ **Specialist-task fit validated**: Cognitive model matches task requirements
□ **No specialist overloaded**: Work distributed appropriately
□ **Context provided to each**: Success criteria, constraints, interfaces defined
□ **Output formats agreed**: Each specialist knows expected deliverable format

**Specialist Matching Criteria Met:**

□ **Domain expertise aligned**: Task domain matches specialist expertise
□ **Cognitive process fit**: Task type matches specialist's mental model
□ **Capability confirmed**: Specialist has required tools/access
□ **Availability verified**: Specialist not blocked/oversubscribed

**Context Provision Complete:**

□ **Scope clearly defined**: What's included/excluded specified
□ **Dependencies communicated**: What they need from others
□ **Integration requirements**: How their output fits the whole
□ **Success criteria provided**: How they know when done

---

## Required Artifacts from Previous Phases

**Must have:**
- ✓ Decomposed tasks from GATE-TASKS-DECOMPOSED.md
- ✓ Task specifications with clear boundaries
- ✓ Dependency map showing execution order
- ✓ Resource requirements per task

**These determine specialist selection.**

---

## GATE STATUS

**IF ASSIGNMENTS INADEQUATE:**
- ❌ **BLOCKED** - Return to delegation/specialist-inventory.md
- Review specialist capabilities
- Reconsider task-specialist matching
- Cannot proceed with poor assignments

**IF ALL CHECKBOXES COMPLETE:**
- ✅ **GATE PASSED** - Proceed to coordination/monitoring-patterns.md
- All specialists properly assigned
- Ready for parallel execution

---

## Assignment Anti-Patterns to Avoid

**Mismatched Expertise:**
- ❌ Frontend specialist → Database design
- ❌ Data analyst → UI implementation
- ❌ Security expert → Performance optimization

**Overloading Specialists:**
- ❌ One specialist assigned 60% of tasks
- ❌ Critical path entirely through one specialist
- ❌ No load balancing considered

**Insufficient Context:**
- ❌ "Just implement this" → Provide specifications
- ❌ "You know what to do" → Define success criteria
- ❌ "Figure it out" → Give constraints and requirements

---

## Specialist Utilization Check

**Optimal distribution achieved?**
```
Each specialist: 60-80% utilized
No specialist: >90% (overloaded) or <40% (underutilized)
Critical specialists: Have backup assignments
```

If not optimal, rebalance assignments.

---

## Communication Overhead Assessment

For each specialist, verify:
- Dependencies clearly communicated
- Integration points identified
- Coordination touchpoints < 3
- Can work independently 80% of time

**Goal**: Minimal coordination overhead (< 10% of work time)

---

## Senior Engineering Manager Validation

Ask yourself:
> "Have I set each specialist up for success? Do they have everything needed to work independently? Will they deliver what's needed for integration?"

Good delegation means specialists can work autonomously.

---

## Navigation

**BLOCKED → Return to:** delegation/specialist-inventory.md
**PASSED → Proceed to:** coordination/monitoring-patterns.md

---

*Proper specialist assignment enables parallel execution with minimal coordination.*
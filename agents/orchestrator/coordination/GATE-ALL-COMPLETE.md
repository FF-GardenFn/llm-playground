# GATE: Coordination Completion Checkpoint

## ⚠️ MANDATORY CHECKPOINT - VERIFY ALL WORK COMPLETE

**Purpose**: Ensure all parallel work has completed (successfully or with documented failure) before attempting integration.

---

## Verification Checklist

**Work Completion Status:**

□ **All tasks have reported status**: No work unaccounted for
□ **Success/failure explicitly documented**: Clear outcome for each task
□ **Outputs collected**: All deliverables retrieved
□ **Failures handled**: Failed tasks have mitigation or acceptance

**Parallel Execution Monitoring:**

□ **No deadlocks occurred**: Dependencies properly managed
□ **No resource conflicts**: Specialists didn't block each other
□ **Progress tracked throughout**: Monitoring was effective
□ **Bottlenecks addressed**: Slow tasks didn't gate everything

**Output Verification:**

□ **Expected formats received**: Outputs match specifications
□ **Quality checks passed**: Basic validation complete
□ **Integration interfaces present**: Can be merged
□ **No critical gaps**: All essential work complete

---

## Required Status from Each Specialist

For EVERY assigned task, must have:
- ✓ Completion status (success/failure/partial)
- ✓ Output artifact (or failure explanation)
- ✓ Integration readiness confirmation
- ✓ Any deviation from specifications noted

**Cannot proceed to integration with missing work.**

---

## GATE STATUS

**IF ANY WORK INCOMPLETE:**
- ❌ **BLOCKED** - Cannot integrate incomplete work
- Determine if work is truly blocked
- Consider partial integration if possible
- May need to reassign or modify approach

**IF CRITICAL FAILURES:**
- ❌ **BLOCKED** - Address failures first
- Evaluate if project can proceed
- Consider fallback strategies
- May need to loop back to earlier phase

**IF ALL COMPLETE (OR ACCEPTABLY PARTIAL):**
- ✅ **GATE PASSED** - Proceed to integration/verification.md
- All work accounted for
- Ready to merge outputs

---

## Handling Incomplete Work

**Acceptable Partial Completion:**
- ✓ Non-critical features incomplete but documented
- ✓ Graceful degradation implemented
- ✓ Core functionality works
- ✓ Integration still possible

**Unacceptable Gaps:**
- ❌ Critical path incomplete
- ❌ Integration blockers unresolved
- ❌ Security/safety requirements unmet
- ❌ Core success criteria missed

---

## Coordination Metrics Check

Evaluate coordination efficiency:
```
Coordination time / Total work time < 10% ✓
Specialists blocked < 5% of time ✓
Rework due to coordination < 5% ✓
```

If metrics exceeded, note for process improvement.

---

## Failure Recovery Decision Tree

```
If specialist failed:
  └─ Is task critical?
      ├─ Yes → Can another specialist complete?
      │   ├─ Yes → Reassign and wait
      │   └─ No → Escalate/Replan
      └─ No → Document and proceed
          └─ Note degraded functionality
```

---

## Senior Engineering Manager Assessment

Before integration, confirm:
> "Do I have everything needed for successful integration? Are the gaps acceptable? Will the integrated result meet success criteria?"

Integration with missing pieces often fails catastrophically.

---

## Navigation

**INCOMPLETE → Options:**
- Return to coordination/monitoring-patterns.md (wait)
- Return to delegation/ (reassign)
- Return to decomposition/ (replan)

**COMPLETE → Proceed to:** integration/verification.md

---

*Complete work is prerequisite for successful integration. This gate prevents integration failures.*
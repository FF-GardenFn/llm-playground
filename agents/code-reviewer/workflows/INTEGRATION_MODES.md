# Integration Modes

**Purpose**: Define the three operational modes for code-reviewer based on context and integration needs.

**Modes**: Standalone, Trigger Refactoring, Verification

---

## Mode Selection

```
User Request
    ↓
Is this verification request from refactoring-engineer?
    ├─→ YES → Mode 3: Verification
    └─→ NO
         ↓
     User wants code review?
         ├─→ YES → Mode 1 or 2 (depends on findings)
         └─→ NO → Not for code-reviewer
```

---

## Mode 1: Standalone Review

**When**: User requests standard code review, no refactoring integration needed.

**Triggers**:
- "Review this PR"
- "Check code quality"
- "Security audit"
- "Architecture review"

**Workflow**: Full 5-phase review process
```
Phase 1: Automated Analysis
Phase 2: Manual Review
Phase 3: Feedback Synthesis
Phase 4: Priority Assessment
Phase 5: Recommendations (no refactoring offer)
```

**Output**: Structured review report with findings and recommendations

**Integration**: None - completely standalone

**Example**:
```
User: "Quick PR review for security"
    ↓
Code-Reviewer (Standalone Mode):
    - Security scan: Found 1 SQL injection
    - Quality check: Found 2 code smells (noted but not acted on)
    - Output: Security-focused report
    - No refactoring-engineer invocation
```

---

## Mode 2: Trigger Refactoring

**When**: Code review finds refactorable smells AND user wants automated fixes.

**Triggers**:
- "Review and refactor"
- "Improve code quality"
- "Fix technical debt"
- User approves refactoring after review

**Workflow**: 5-phase review + refactoring integration
```
Phase 1-4: Standard review process
    ↓
Refactorable smells detected in Phase 4
    ↓
Phase 5: Offer to invoke refactoring-engineer
    ↓
User approves
    ↓
Invoke refactoring-engineer with smell list
    ↓
Receive refactoring results
    ↓
Return combined report (review + refactoring)
```

**Output**: Review report + refactoring results + ROI metrics

**Integration**: Code-Reviewer → Refactoring-Engineer (sequential)

**Example**:
```
User: "Review and improve this code"
    ↓
Code-Reviewer (Trigger Refactoring Mode):
    Phase 1-4: Detect 3 refactorable smells
    Phase 5: "Found 3 refactorable issues. Invoke refactoring-engineer?"
    ↓
User: "Yes, refactor"
    ↓
Code-Reviewer invokes Refactoring-Engineer:
    Input: [long_method, duplicate_code, complex_conditional]
    ↓
Refactoring-Engineer: Applies refactorings
    ↓
Code-Reviewer returns:
    - Review findings
    - Refactoring results (3 smells fixed)
    - Metrics: Complexity reduced 60%
    - ROI: 30 min invested, 80 hrs/year saved
```

---

## Mode 3: Verification

**When**: Refactoring-engineer requests comprehensive post-refactoring verification.

**Triggers**:
- Invoked by refactoring-engineer Phase 5
- Critical code refactored
- User explicitly requests verification

**Workflow**: Streamlined verification process
```
Input from Refactoring-Engineer:
    - code_before
    - code_after
    - refactoring_applied
    - tests_passed
    ↓
Verification Checks:
    1. Security Regression Check (REQUIRED)
    2. Performance Regression Check (REQUIRED)
    3. Architecture Integrity Check (REQUIRED)
    4. Quality Delta Assessment (REQUIRED)
    ↓
Output: APPROVE | REQUEST_CHANGES
```

**Output**: Verification report with pass/fail + recommendation

**Integration**: Refactoring-Engineer → Code-Reviewer (invoked)

**Example**:
```
Refactoring-Engineer Phase 5:
    "Refactored critical payment code, need comprehensive verification"
    ↓
Refactoring-Engineer invokes Code-Reviewer (Verification Mode):
    Input:
      - code_before: payment_service.py (complexity 15)
      - code_after: payment_service.py (complexity 6)
      - refactoring: extract_method
      - tests_passed: true
    ↓
Code-Reviewer (Verification Mode):
    Check 1: Security Regression
        → Scan code_after for new vulnerabilities
        → Result: No new issues ✓

    Check 2: Performance Regression
        → Profile execution time
        → Result: 2% faster ✓

    Check 3: Architecture Integrity
        → Verify boundaries maintained
        → Result: Intact ✓

    Check 4: Quality Delta
        → Complexity: 15 → 6 (60% improvement) ✓
        → Duplication: No increase ✓
    ↓
Output to Refactoring-Engineer:
    {
      "verification_passed": true,
      "recommendation": "APPROVE",
      "checks": {
        "security": "PASS",
        "performance": "PASS (2% faster)",
        "architecture": "PASS",
        "quality": "IMPROVED (60% complexity reduction)"
      }
    }
```

---

## Mode Comparison

| Aspect | Mode 1: Standalone | Mode 2: Trigger Refactoring | Mode 3: Verification |
|--------|-------------------|----------------------------|---------------------|
| **Trigger** | User review request | User wants improvement | Refactoring-engineer invocation |
| **Duration** | 2-5 minutes | 15-40 minutes | 2-5 minutes |
| **Phases** | All 5 phases | All 5 + refactoring | Streamlined 4 checks |
| **Integration** | None | CR → RE | RE → CR |
| **Output** | Review report | Review + refactoring | Verification report |
| **Refactoring** | Not offered | Offered/applied | Already applied |

---

## Mode Selection Logic

### Decision Tree

```
Is this a verification request?
    ├─→ YES (invocation_type: "verification_request")
    │       → Mode 3: Verification
    └─→ NO
         ↓
     Run Phases 1-4 (standard review)
         ↓
     Are refactorable smells found?
         ├─→ YES
         │    ↓
         │ User wants automated fixes?
         │    ├─→ YES → Mode 2: Trigger Refactoring
         │    └─→ NO → Mode 1: Standalone (note smells in report)
         │
         └─→ NO → Mode 1: Standalone
```

### Configuration

**File**: `code-reviewer/integration/config.json`
```json
{
  "default_mode": "auto",
  "auto_offer_refactoring": true,
  "verification_mode_enabled": true,
  "ask_before_invoking_refactoring": true
}
```

**Settings**:
- `default_mode: "auto"`: Automatically choose mode based on context
- `default_mode: "standalone"`: Never offer refactoring
- `auto_offer_refactoring: true`: Offer refactoring if smells found
- `ask_before_invoking_refactoring: true`: Require user confirmation

---

## Mode-Specific Behavior

### Mode 1: Standalone Review

**What to Include**:
- ✓ All security issues
- ✓ All performance issues
- ✓ All architecture issues
- ✓ All code smells (noted)
- ✓ Testing recommendations

**What to Exclude**:
- ✗ Refactoring offer
- ✗ Integration with refactoring-engineer

**When to Use**:
- Quick PR reviews
- Security-focused audits
- Architecture assessments
- User explicitly no refactoring

### Mode 2: Trigger Refactoring

**What to Include**:
- ✓ Everything from Mode 1
- ✓ Refactorable smell classification
- ✓ Refactoring offer with ROI estimate
- ✓ Refactoring results (if accepted)
- ✓ Combined metrics (before/after)

**What to Exclude**:
- ✗ Offering refactoring for non-refactorable issues

**When to Use**:
- "Improve code quality" requests
- Technical debt cleanup
- Comprehensive code improvement
- User open to automated fixes

**Prerequisites**:
- Tests must be passing
- Version control available
- Refactorable smells detected

### Mode 3: Verification

**What to Include**:
- ✓ Security regression check
- ✓ Performance regression check
- ✓ Architecture integrity check
- ✓ Quality delta (before/after metrics)
- ✓ APPROVE/REQUEST_CHANGES recommendation

**What to Exclude**:
- ✗ New smell detection (focus on regression only)
- ✗ Manual review (streamlined for speed)
- ✗ Offering new refactorings

**When to Use**:
- Invoked by refactoring-engineer Phase 5
- Post-refactoring verification
- Critical code changes

**Input Required**:
- code_before (with metrics)
- code_after (with metrics)
- refactoring_applied (pattern name)
- tests_passed (boolean)

---

## Integration Protocol

### Mode 1 → Mode 2 Transition

**Trigger**: User approves refactoring after seeing review

```
Code-Reviewer (Mode 1):
    Phase 1-4: Complete
    Phase 5: "Found 3 refactorable smells. Type 'refactor' to fix automatically."
    ↓
User: "refactor"
    ↓
Code-Reviewer switches to Mode 2:
    Load integration protocol:
      {{load: ../integration/REFACTORING_TRIGGER.md}}
    ↓
    Invoke refactoring-engineer with smell list
    ↓
    Return combined results
```

### Mode 3 Entry Point

**Invoked by Refactoring-Engineer**:

```json
{
  "invocation_type": "verification_request",
  "source_agent": "refactoring-engineer",
  "mode": "verification",
  "code_before": {...},
  "code_after": {...},
  "refactoring_applied": "extract_method"
}
```

**Code-Reviewer detects verification mode**:
```
Parse invocation JSON
    ↓
invocation_type == "verification_request"?
    ├─→ YES → Enter Mode 3: Verification
    │       Load verification workflow:
    │         {{load: ../integration/VERIFICATION_MODE.md}}
    │       Run streamlined checks
    │       Return verification report
    │
    └─→ NO → Normal review (Mode 1 or 2)
```

---

## Error Handling by Mode

### Mode 1 Errors

**Error**: Automated tools fail
**Handling**: Continue with manual review only, note tool unavailable

**Error**: Code unreadable/corrupted
**Handling**: Report error, request valid code

### Mode 2 Errors

**Error**: Refactoring-engineer unavailable
**Handling**: Fall back to Mode 1, provide manual refactoring recommendations

**Error**: Prerequisites not met (tests failing)
**Handling**: Report prerequisite failure, recommend fixing tests first

**Error**: Refactoring fails
**Handling**: Report failure, revert suggested, provide manual alternatives

### Mode 3 Errors

**Error**: code_before or code_after missing
**Handling**: Return verification failed, request complete input

**Error**: Verification finds regressions
**Handling**: Return REQUEST_CHANGES with detailed regression report

**Error**: Cannot access code
**Handling**: Return verification error, request valid code paths

---

## Performance Considerations

### Mode Duration Estimates

- **Mode 1 (Standalone)**: 2-5 minutes
  - Automated analysis: 30 seconds
  - Manual review: 1-4 minutes
  - Report generation: 30 seconds

- **Mode 2 (Trigger Refactoring)**: 15-40 minutes
  - Code review: 2-5 minutes
  - Refactoring-engineer invocation: 10-30 minutes
  - Combined report: 3-5 minutes

- **Mode 3 (Verification)**: 2-5 minutes
  - Regression checks: 1-2 minutes
  - Metrics comparison: 30 seconds
  - Report generation: 1 minute

### Optimization Strategies

**Mode 1**:
- Cache automated analysis results
- Parallelize security scan + static analysis

**Mode 2**:
- Don't rerun code-reviewer checks after refactoring
- Pass code-reviewer metrics to refactoring-engineer

**Mode 3**:
- Skip full review, focus on regression only
- Use diff analysis for targeted checks

---

## User Experience

### Mode 1 UX

```
User: "Review this PR"
    ↓
Code-Reviewer: "Reviewing... (2 minutes)"
    ↓
Output:
  "✓ Review complete

   Found 5 issues:
   - 1 Critical (security)
   - 3 Important (performance, testing)
   - 1 Suggestion (naming)

   See detailed report above."
```

### Mode 2 UX

```
User: "Review and improve"
    ↓
Code-Reviewer: "Reviewing... (2 minutes)"
    ↓
Output:
  "✓ Review complete

   Found 5 issues:
   - 1 Critical (security) - manual fix required
   - 2 Important (N+1 query) - manual fix required
   - 3 Refactorable (smells) - can automate

   Would you like me to fix the 3 refactorable issues automatically?
   (Estimated time: 30 min, ROI: 80 hrs/year saved)"
    ↓
User: "Yes"
    ↓
Code-Reviewer: "Invoking refactoring-engineer... (30 minutes)"
    ↓
Output:
  "✓ Refactoring complete

   Fixed 3 code smells:
   - Long method: Extracted 3 methods
   - Duplicate code: Created shared utility
   - Complex conditional: Simplified logic

   Metrics improved:
   - Complexity: 15 → 6 (60% reduction)
   - Tests: All passing ✓

   Remaining issues (manual):
   - 1 Critical (security)
   - 2 Important (N+1 query)"
```

### Mode 3 UX

```
[Refactoring-Engineer working...]
    ↓
Refactoring-Engineer Phase 5:
    "Invoking code-reviewer for verification... (2 minutes)"
    ↓
Code-Reviewer (Verification Mode):
    Running checks...
    ✓ Security: No regressions
    ✓ Performance: 2% faster
    ✓ Architecture: Intact
    ✓ Quality: 60% improvement
    ↓
Output to Refactoring-Engineer:
    "Verification: APPROVED"
    ↓
[Refactoring-Engineer continues to Phase 6...]
```

---

## Summary

**Three Modes**:
1. **Standalone**: Fast, focused review (no integration)
2. **Trigger Refactoring**: Review → detect smells → invoke refactoring (sequential integration)
3. **Verification**: Invoked by refactoring-engineer for post-refactoring checks (reverse integration)

**Mode Selection**: Automatic based on context and user intent

**Integration**: Bidirectional (Code-Reviewer ↔ Refactoring-Engineer)

**User Control**: Can configure default behavior, always asked before triggering refactoring

**Fallback**: Graceful degradation to standalone if integration unavailable

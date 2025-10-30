# Refactoring Trigger Protocol

**Purpose**: Define when and how code-reviewer Phase 4 invokes refactoring-engineer to automate code smell fixes.

**Integration Mode**: Mode 2 (Trigger Refactoring) - Sequential integration (Code-Reviewer → Refactoring-Engineer)

**Protocol Version**: 1.0

---

## Overview

```
Code-Reviewer Phase 4: Priority Assessment
    ↓
Refactorable smells detected?
    ├─→ NO → Phase 5: Recommendations only
    └─→ YES
         ↓
     User approval required?
         ├─→ YES → Ask user for confirmation
         │       ↓
         │   User approves?
         │       ├─→ YES → Invoke refactoring-engineer
         │       └─→ NO → Phase 5: Manual recommendations
         │
         └─→ NO (auto-refactoring enabled) → Invoke refactoring-engineer
```

---

## Trigger Conditions

### Required Conditions (ALL must be true)

1. **Refactorable Smells Detected**
   - At least 1 smell from refactoring-engineer catalog found
   - Smell classified as "refactorable" in Phase 4
   - Smell severity: Important or Critical (not just Suggestions)

2. **Prerequisites Met**
   - Tests are passing (prerequisite for safe refactoring)
   - Version control available (can revert if needed)
   - Code not in production-critical state

3. **User Approval** (unless auto-refactoring enabled)
   - User explicitly requests refactoring ("review and improve", "refactor")
   - OR user approves refactoring offer in Phase 5
   - OR configuration: `auto_offer_refactoring: true`

### Optional Conditions (Enhance Decision)

- **ROI Positive**: Estimated time savings > time investment
- **Risk Low**: All detected smells have low-risk refactoring patterns
- **Coverage High**: Test coverage ≥ 80% (safer refactoring)

---

## Invocation Protocol

### Step 1: Prepare Invocation Payload

**Format**: JSON (matches `shared/integration/PROTOCOL.md`)

```json
{
  "invocation_type": "refactoring_request",
  "source_agent": "code-reviewer",
  "timestamp": "2025-10-30T14:30:00Z",
  "detected_smells": [
    {
      "type": "long_method",
      "location": "src/user_service.py:45-120",
      "severity": "important",
      "description": "Method process_user_data is 75 lines with complexity 15",
      "suggested_refactoring": "extract_method",
      "metrics": {
        "lines": 75,
        "complexity": 15,
        "parameters": 3
      }
    },
    {
      "type": "duplicate_code",
      "location": "src/user_service.py:150-180",
      "duplicate_location": "src/admin_service.py:90-120",
      "severity": "important",
      "description": "30 lines duplicated (85% similarity)",
      "suggested_refactoring": "extract_method",
      "metrics": {
        "similarity_percentage": 85,
        "lines_duplicated": 30
      }
    },
    {
      "type": "complex_conditional",
      "location": "src/user_service.py:200-220",
      "severity": "important",
      "description": "Conditional nested 4 levels deep",
      "suggested_refactoring": "decompose_conditional",
      "metrics": {
        "nesting_depth": 4,
        "boolean_expression_length": 65
      }
    }
  ],
  "context": {
    "test_coverage": 85,
    "tests_passing": true,
    "version_control": "git",
    "criticality": "medium",
    "files_affected": [
      "src/user_service.py",
      "src/admin_service.py"
    ]
  },
  "request_parameters": {
    "comprehensive_verification": false,
    "risk_tolerance": "low",
    "user_approved": true
  }
}
```

### Step 2: User Confirmation Workflow

**If `ask_before_invoking_refactoring: true`** (default):

```
Code-Reviewer Phase 5 Output:
  "✓ Review complete

   Found 5 issues:
   - 1 Critical (security) - manual fix required
   - 2 Important (N+1 query) - manual fix required
   - 3 Refactorable (smells) - can automate

   Refactorable Issues:
   • Long Method (line 45): 75 lines, complexity 15
     → Refactoring: Extract Method (Easy, Low Risk)
     → Estimated time: 10 minutes
     → Estimated savings: 30 hours/year

   • Duplicate Code (line 150): 85% similar to admin_service.py:90
     → Refactoring: Extract Method (Easy, Low Risk)
     → Estimated time: 15 minutes
     → Estimated savings: 25 hours/year

   • Complex Conditional (line 200): Nested 4 levels
     → Refactoring: Decompose Conditional (Medium, Low Risk)
     → Estimated time: 10 minutes
     → Estimated savings: 20 hours/year

   Total estimated time: 35 minutes
   Total estimated savings: 75 hours/year
   ROI: Positive (129x return)

   Would you like me to invoke refactoring-engineer to fix these automatically?
   Type 'yes' to proceed, 'no' for manual recommendations."
    ↓
User: "yes"
    ↓
Code-Reviewer: "Invoking refactoring-engineer... (estimated 35 minutes)"
```

**If `ask_before_invoking_refactoring: false`**:
- Auto-invoke if conditions met
- Notify user of automatic invocation
- Provide option to cancel within 5 seconds

### Step 3: Invoke Refactoring-Engineer

**Method**: Agent-to-agent invocation via Task tool

```markdown
Load refactoring-engineer integration:
  {{load: ../../refactoring-engineer/workflows/REFACTORING_PROCESS.md}}

Invoke with prepared payload:
  {detected_smells: [...], context: {...}}

Wait for refactoring-engineer completion (Phase 1-6):
  - Phase 1: Smell Detection (uses provided list)
  - Phase 2: Refactoring Selection
  - Phase 3: Safety Check
  - Phase 4: Implementation
  - Phase 5: Verification
  - Phase 6: Debt Tracking
```

### Step 4: Receive Refactoring Results

**Expected Output Format**:

```json
{
  "status": "success",
  "refactorings_applied": [
    {
      "smell": "long_method",
      "location": "src/user_service.py:45-120",
      "pattern": "extract_method",
      "methods_extracted": [
        "validate_user",
        "process_payment",
        "send_confirmation"
      ],
      "metrics_before": {"complexity": 15, "lines": 75},
      "metrics_after": {"complexity": 6, "lines": 45}
    },
    {
      "smell": "duplicate_code",
      "location": "src/user_service.py:150-180",
      "pattern": "extract_method",
      "shared_method_created": "validate_person",
      "files_modified": ["src/user_service.py", "src/admin_service.py"],
      "metrics_before": {"duplication": 85},
      "metrics_after": {"duplication": 0}
    },
    {
      "smell": "complex_conditional",
      "location": "src/user_service.py:200-220",
      "pattern": "decompose_conditional",
      "guard_clauses_added": 3,
      "metrics_before": {"nesting_depth": 4},
      "metrics_after": {"nesting_depth": 1}
    }
  ],
  "overall_metrics": {
    "complexity_before": 15,
    "complexity_after": 6,
    "improvement_percentage": 60,
    "tests_passing": true,
    "files_modified": 2,
    "time_invested_minutes": 35
  },
  "verification": {
    "tests_passed": true,
    "behavior_preserved": true,
    "metrics_improved": true
  },
  "roi": {
    "time_invested": "35 minutes",
    "estimated_savings": "75 hours/year",
    "roi_multiplier": 129
  }
}
```

**Or Error Format**:

```json
{
  "status": "error",
  "error_type": "prerequisite_failure",
  "message": "Tests are failing, cannot proceed with refactoring",
  "details": {
    "failing_tests": 3,
    "test_output": "..."
  },
  "recommendation": "Fix failing tests before refactoring"
}
```

### Step 5: Incorporate Results into Review Report

**Code-Reviewer Final Output**:

```markdown
# Code Review Complete

## Executive Summary
- Overall Quality: B- → A (significant improvement)
- Issues Found: 6 (3 fixed via refactoring, 3 require manual fixes)
- Refactoring Applied: 3 code smells addressed

## Critical Issues (Manual Fix Required)
1. SQL Injection (line 23): Use parameterized queries
   See: security/input-validation.md

## Important Issues (Manual Fix Required)
2. N+1 Query (line 67): Use eager loading
   See: performance/database-performance.md

## Refactoring Results ✓

### Automated Fixes Applied by Refactoring-Engineer

**1. Long Method (line 45) - FIXED**
- Before: 75 lines, complexity 15
- After: 45 lines, complexity 6 (60% improvement)
- Pattern: Extract Method
- Methods extracted: validate_user, process_payment, send_confirmation
- Tests: All passing ✓

**2. Duplicate Code (line 150) - FIXED**
- Before: 85% duplication between user_service.py and admin_service.py
- After: 0% duplication (shared method validate_person created)
- Pattern: Extract Method
- Files modified: 2
- Tests: All passing ✓

**3. Complex Conditional (line 200) - FIXED**
- Before: Nested 4 levels deep
- After: Nested 1 level (guard clauses added)
- Pattern: Decompose Conditional
- Tests: All passing ✓

### Overall Improvement Metrics
- Complexity: 15 → 6 (60% reduction)
- Code Duplication: 85% → 0% (eliminated)
- Maintainability Index: C+ → A

### ROI
- Time invested: 35 minutes
- Estimated savings: 75 hours/year
- ROI multiplier: 129x

## Next Steps

1. **Immediate**: Fix Critical issues (SQL injection)
2. **This Sprint**: Fix N+1 query problem
3. **Done**: Code smells addressed via automated refactoring ✓

## Verification
- All tests passing: ✓
- Behavior preserved: ✓
- Code quality improved: ✓ (60% complexity reduction)
```

---

## Error Handling

### Scenario 1: Refactoring-Engineer Unavailable

**Error**: Cannot connect to refactoring-engineer agent

**Handling**:
```
Code-Reviewer (Graceful Fallback):
    Phase 5: Recommendations (without automated refactoring)
        → Provide detailed manual refactoring instructions
        → Reference refactoring pattern documentation
        → Include step-by-step DIY guide
    ↓
Output:
  "Found 3 refactorable smells:

   Note: refactoring-engineer not available for automated fixes.
   Manual refactoring instructions provided below.

   Long Method (line 45):
   • Current: 75 lines, complexity 15
   • Recommended: Extract Method refactoring
   • Steps:
     1. Identify cohesive groups of lines
     2. Extract validate_user() from lines 45-60
     3. Extract process_payment() from lines 61-85
     4. Extract send_confirmation() from lines 86-120
   • See: refactorings/composing-methods/extract-method.md

   [... additional manual instructions ...]"
```

### Scenario 2: Prerequisites Not Met

**Error**: Tests failing, version control unavailable, etc.

**Handling**:
```
Code-Reviewer:
    Detect prerequisite failure
        ↓
    Do NOT invoke refactoring-engineer
        ↓
    Phase 5: Report prerequisite issues
        ↓
Output:
  "Found 3 refactorable smells, but cannot automate refactoring:

   Prerequisites Not Met:
   ✗ Tests failing (3 tests failing)
   ✗ Version control not available

   Recommendation:
   1. Fix failing tests first
   2. Initialize git repository
   3. Re-run review with 'refactor' option

   Manual refactoring instructions available if needed."
```

### Scenario 3: Refactoring Fails

**Error**: Refactoring-engineer returns error status

**Handling**:
```
Code-Reviewer receives error response:
    {
      "status": "error",
      "error_type": "refactoring_failure",
      "message": "Extract method failed: naming conflict",
      "smells_fixed": 1,
      "smells_failed": 2
    }
    ↓
Code-Reviewer Output:
  "Refactoring partially completed:

   ✓ Fixed: Long method (complexity reduced 60%)
   ✗ Failed: Duplicate code (naming conflict)
   ✗ Failed: Complex conditional (tests broke)

   Refactoring-engineer has reverted failed changes.

   Manual fixes required for remaining 2 smells.
   See detailed error log for diagnosis."
```

### Scenario 4: User Cancels

**Error**: User interrupts refactoring process

**Handling**:
```
Code-Reviewer invokes refactoring-engineer
    ↓
User: "cancel"
    ↓
Code-Reviewer:
    Send cancellation signal to refactoring-engineer
    ↓
    Refactoring-engineer Phase 3: Safety Check detects cancellation
    ↓
    No changes applied (safe exit)
    ↓
Output:
  "Refactoring cancelled by user.
   No changes applied.
   Manual refactoring instructions available if needed."
```

---

## Configuration

### Integration Config

**File**: `code-reviewer/integration/config.json`

```json
{
  "refactoring_trigger": {
    "enabled": true,
    "ask_before_invoking": true,
    "auto_invoke_conditions": {
      "min_roi_multiplier": 50,
      "max_risk": "low",
      "min_test_coverage": 80
    },
    "timeout_seconds": 3600,
    "retry_on_failure": false
  },
  "prerequisites": {
    "require_tests_passing": true,
    "require_version_control": true,
    "min_test_coverage": 70
  },
  "refactorable_smells": {
    "min_severity": "important",
    "exclude_smells": [],
    "max_smells_per_invocation": 10
  }
}
```

### Settings Explanation

- `enabled`: Master switch for refactoring integration
- `ask_before_invoking`: Require user confirmation (default: true)
- `auto_invoke_conditions`: Criteria for automatic invocation (if ask_before_invoking: false)
- `timeout_seconds`: Maximum time to wait for refactoring-engineer
- `require_tests_passing`: Block refactoring if tests failing
- `min_severity`: Only trigger for "important" or "critical" smells (not "suggestions")
- `max_smells_per_invocation`: Limit smells per refactoring session (avoid overwhelming changes)

---

## User Experience Examples

### Example 1: Standard Trigger

```
User: "Review and improve user_service.py"
    ↓
Code-Reviewer Phase 1-4:
    → Detects 3 refactorable smells (long_method, duplicate_code, complex_conditional)
    → Prerequisites: Tests passing ✓, Version control ✓
    ↓
Code-Reviewer Phase 5:
    "Found 3 refactorable issues. Invoke refactoring-engineer? (35 min, 75 hrs/year savings)"
    ↓
User: "yes"
    ↓
Code-Reviewer invokes Refactoring-Engineer:
    [35 minutes later]
    ↓
Output:
    "Refactoring complete:
     ✓ Complexity reduced 60%
     ✓ Duplication eliminated
     ✓ All tests passing
     ROI: 129x"
```

### Example 2: Auto-Invoke (No Confirmation)

```
User: "Review and auto-improve" (with config: ask_before_invoking: false)
    ↓
Code-Reviewer Phase 1-4:
    → Detects 3 refactorable smells
    → ROI: 129x (> 50x threshold)
    → Risk: Low (all easy patterns)
    → Coverage: 85% (> 80% threshold)
    → Auto-invoke conditions met ✓
    ↓
Code-Reviewer:
    "Auto-invoking refactoring-engineer (3 smells detected, estimated 35 min)...
     Press Ctrl+C within 5 seconds to cancel."
    [5 second delay]
    ↓
    [Proceeds with refactoring automatically]
```

### Example 3: Prerequisites Fail

```
User: "Review and refactor"
    ↓
Code-Reviewer Phase 1-3:
    → Tests: 3 failing ✗
    ↓
Code-Reviewer Phase 4:
    → Prerequisite check: Tests failing
    → Do NOT offer refactoring
    ↓
Code-Reviewer Phase 5:
    "Found 3 refactorable issues, but cannot automate:
     ✗ Prerequisite not met: 3 tests failing

     Recommendation:
     1. Fix failing tests first
     2. Re-run review with 'refactor'

     Manual refactoring instructions available."
```

### Example 4: Mixed Issues

```
User: "Review payment_service.py"
    ↓
Code-Reviewer Phase 1-4:
    → Critical: 1 SQL injection (NOT refactorable)
    → Important: 1 N+1 query (NOT refactorable)
    → Important: 3 code smells (REFACTORABLE)
    ↓
Code-Reviewer Phase 5:
    "Found 5 issues:

     Critical (fix first):
     ✗ SQL injection (line 23): Manual fix required

     Important (fix soon):
     ✗ N+1 query (line 67): Manual fix required

     Refactorable (can automate):
     • 3 code smells detected

     Recommended workflow:
     1. Fix Critical (SQL injection) first
     2. Fix Important (N+1 query)
     3. Then refactor code smells

     Type 'refactor' when Critical/Important fixed."
    ↓
User fixes Critical and Important issues
    ↓
User: "refactor"
    ↓
Code-Reviewer invokes Refactoring-Engineer for code smells
```

---

## Decision Tree

```
Code-Reviewer Phase 4: Priority Assessment
    ↓
Are refactorable smells detected?
    ├─→ NO
    │    ↓
    │ Phase 5: Recommendations only (no refactoring offer)
    │
    └─→ YES (1+ refactorable smells found)
         ↓
     Are there Critical issues?
         ├─→ YES
         │    ↓
         │ Phase 5: Recommend fix Critical first, defer refactoring
         │ Output: "Fix Critical issues first, then type 'refactor'"
         │
         └─→ NO (no blocking Critical issues)
              ↓
          Prerequisites met?
              ├─→ NO (tests failing, no version control, etc.)
              │    ↓
              │ Phase 5: Report prerequisite failure
              │ Output: "Cannot automate refactoring (prerequisites not met)"
              │
              └─→ YES (prerequisites satisfied)
                   ↓
               ask_before_invoking == true?
                   ├─→ YES
                   │    ↓
                   │ Phase 5: Offer refactoring with ROI estimate
                   │ Output: "Would you like me to invoke refactoring-engineer?"
                   │    ↓
                   │ Wait for user response
                   │    ↓
                   │ User approves?
                   │    ├─→ YES → Invoke refactoring-engineer
                   │    └─→ NO → Provide manual recommendations
                   │
                   └─→ NO (auto-invoke enabled)
                        ↓
                    Auto-invoke conditions met?
                        ├─→ YES (ROI > 50x, Risk low, Coverage > 80%)
                        │    ↓
                        │ Notify user (5 second cancellation window)
                        │ Invoke refactoring-engineer
                        │
                        └─→ NO → Fall back to user confirmation
```

---

## Performance Considerations

### Latency Impact

**Refactoring Integration Adds**:
- User confirmation: +10-30 seconds (if enabled)
- Refactoring-engineer invocation: +10-40 minutes (depends on smell count)
- Result processing: +1-2 minutes

**Total Duration**:
- Code-Reviewer standalone: 2-5 minutes
- Code-Reviewer + Refactoring-Engineer: 15-50 minutes

### Optimization Strategies

1. **Parallel Execution**: Not possible (refactoring-engineer needs code-reviewer's smell list)
2. **Smell Batching**: Group smells to avoid multiple invocations
3. **Selective Refactoring**: Only trigger for high-ROI smells (config: min_roi_multiplier)
4. **Caching**: Cache refactoring-engineer results for repeated invocations on same code

---

## Summary

**Trigger Refactoring When**:
- Refactorable smells detected (Important or Critical severity)
- Prerequisites met (tests passing, version control available)
- User approves (or auto-invoke enabled with conditions met)
- No blocking Critical issues

**Invocation Protocol**:
- Prepare JSON payload with detected_smells + context
- Invoke refactoring-engineer via Task tool
- Wait for completion (Phase 1-6)
- Receive results (success or error)
- Incorporate into final review report

**Error Handling**:
- Graceful fallback to manual recommendations
- Clear communication of failures
- Prerequisite checking before invocation

**User Control**:
- Configuration: ask_before_invoking (default: true)
- Cancellation: 5-second window for auto-invoke
- Transparency: ROI estimates, time estimates, risk levels

**Integration Goal**: Seamless collaboration between code-reviewer (detection) and refactoring-engineer (automation) to maximize code quality improvement with minimal manual effort.

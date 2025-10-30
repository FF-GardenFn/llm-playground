# Agent Integration Protocol

**Purpose**: Define how code-reviewer and refactoring-engineer communicate and collaborate.

**Version**: 0.1.0
**Date**: 2025-10-21

---

## Overview

Code-reviewer and refactoring-engineer are independent specialist agents that can collaborate through a standardized integration protocol. This enables:

1. **Code-reviewer → Refactoring-engineer**: Review identifies refactorable smells, triggers refactoring
2. **Refactoring-engineer → Code-reviewer**: Refactoring verification invokes comprehensive code review
3. **Shared Resources**: Single smell catalog, unified quality metrics

---

## Integration Modes

### Mode 1: Standalone Operation (No Integration)

**Code-Reviewer Standalone**:
- User requests PR review
- Code-reviewer executes 5-phase review
- Returns structured feedback
- No refactoring-engineer invocation

**Refactoring-Engineer Standalone**:
- User requests code refactoring
- Refactoring-engineer executes 6-phase workflow
- Returns refactored code + metrics
- No code-reviewer invocation

### Mode 2: Sequential Integration (Code-Reviewer → Refactoring-Engineer)

**Trigger**: Code-reviewer Phase 4 (Priority Assessment) detects refactorable smells

**Flow**:
```
User: "Review this code"
    ↓
Code-Reviewer Phase 1-4:
    - Automated analysis
    - Manual review
    - Feedback synthesis
    - Priority assessment
        → Detects: 3 refactorable smells (long_method, duplicate_code)
    ↓
Code-Reviewer Output:
    "Found 3 refactorable issues. Would you like me to invoke refactoring-engineer?"
    ↓
User: "Yes, refactor"
    ↓
Code-Reviewer invokes Refactoring-Engineer:
    Input: smell list + code locations
    ↓
Refactoring-Engineer Phases 1-6:
    - Smell detection (uses provided smells)
    - Pattern selection
    - Safety check
    - Implementation
    - Verification
    - Debt tracking
    ↓
Return to Code-Reviewer:
    - Refactored code
    - Metrics comparison
    - ROI calculation
```

### Mode 3: Sequential Integration (Refactoring-Engineer → Code-Reviewer)

**Trigger**: Refactoring-engineer Phase 5 (Verification) needs comprehensive quality check

**Flow**:
```
User: "Refactor this code"
    ↓
Refactoring-Engineer Phases 1-4:
    - Smell detection
    - Pattern selection
    - Safety check
    - Implementation
    ↓
Refactoring-Engineer Phase 5 (Verification):
    - Basic verification (tests pass, metrics improved)
    - For critical code: Invoke code-reviewer for comprehensive verification
    ↓
Code-Reviewer Verification Mode:
    Input: code_before, code_after, tests_passed, metrics
    ↓
Code-Reviewer Checks:
    - Security regression check
    - Performance regression check
    - Quality metrics validation
    - Architecture integrity
    ↓
Return to Refactoring-Engineer:
    - Verification passed: true/false
    - Issues found: []
    - Recommendation: "APPROVE" | "REQUEST_CHANGES"
    ↓
Refactoring-Engineer Phase 6 (Debt Tracking):
    - Include code-reviewer verification in report
```

---

## Invocation Protocol

### Method 1: Code-Reviewer → Refactoring-Engineer

**When**: Code-reviewer detects refactorable smells in Phase 4

**Input Format**:
```json
{
  "invocation_type": "refactoring_request",
  "source_agent": "code-reviewer",
  "timestamp": "2025-10-30T14:30:00Z",
  "target_code": {
    "files": ["src/user_service.py"],
    "language": "python"
  },
  "detected_smells": [
    {
      "type": "long_method",
      "location": "src/user_service.py:45-120",
      "severity": "important",
      "complexity": 15,
      "suggested_refactoring": "extract_method"
    },
    {
      "type": "duplicate_code",
      "location": "src/user_service.py:150-180, src/admin_service.py:90-120",
      "severity": "important",
      "duplication_percentage": 85,
      "suggested_refactoring": "extract_method"
    }
  ],
  "context": {
    "test_coverage": 85,
    "tests_passing": true,
    "current_complexity": 15
  },
  "user_preferences": {
    "incremental": true,
    "max_time_minutes": 60
  }
}
```

**Expected Output**:
```json
{
  "invocation_type": "refactoring_response",
  "source_agent": "refactoring-engineer",
  "timestamp": "2025-10-30T15:00:00Z",
  "status": "success",
  "refactorings_applied": [
    {
      "smell": "long_method",
      "pattern": "extract_method",
      "files_modified": ["src/user_service.py"],
      "methods_extracted": ["validate_user", "process_payment", "send_confirmation"]
    }
  ],
  "metrics": {
    "complexity_before": 15,
    "complexity_after": 6,
    "improvement_percentage": 60
  },
  "verification": {
    "tests_passing": true,
    "behavior_preserved": true
  },
  "roi": {
    "time_invested_minutes": 45,
    "estimated_savings_hours_per_year": 120
  }
}
```

### Method 2: Refactoring-Engineer → Code-Reviewer

**When**: Refactoring-engineer Phase 5 needs comprehensive verification

**Input Format**:
```json
{
  "invocation_type": "verification_request",
  "source_agent": "refactoring-engineer",
  "timestamp": "2025-10-30T14:45:00Z",
  "mode": "verification",
  "code_before": {
    "file": "src/user_service.py",
    "content": "...",
    "metrics": {
      "complexity": 15,
      "loc": 250,
      "test_coverage": 85
    }
  },
  "code_after": {
    "file": "src/user_service.py",
    "content": "...",
    "metrics": {
      "complexity": 6,
      "loc": 245,
      "test_coverage": 87
    }
  },
  "refactoring_applied": {
    "pattern": "extract_method",
    "description": "Extracted 3 methods to reduce complexity"
  },
  "tests_passed": true,
  "verification_requirements": {
    "check_security_regression": true,
    "check_performance_regression": true,
    "check_architecture_integrity": true
  }
}
```

**Expected Output**:
```json
{
  "invocation_type": "verification_response",
  "source_agent": "code-reviewer",
  "timestamp": "2025-10-30T14:50:00Z",
  "verification_passed": true,
  "checks": {
    "security_regression": {
      "passed": true,
      "issues_found": 0,
      "message": "No new security vulnerabilities introduced"
    },
    "performance_regression": {
      "passed": true,
      "performance_delta_percent": -2,
      "message": "Performance improved by 2%"
    },
    "architecture_integrity": {
      "passed": true,
      "issues_found": 0,
      "message": "Component boundaries maintained"
    },
    "quality_improvement": {
      "complexity_reduction": 60,
      "maintainability_score": "A",
      "message": "Significant quality improvement"
    }
  },
  "new_issues": [],
  "recommendation": "APPROVE",
  "confidence": "high"
}
```

---

## Shared Resources

### Shared Smell Catalog

**Location**: `refactoring-engineer/smells/`

**Usage**:
- **Refactoring-Engineer**: Owns and maintains smell catalog (11 smells)
- **Code-Reviewer**: References refactoring-engineer smell catalog, does NOT duplicate
- **Integration**: Code-reviewer loads smells from `../refactoring-engineer/smells/INDEX.md`

**Example**:
```markdown
# code-reviewer Phase 1: Automated Analysis

Load smell catalog:
  {{load: ../../refactoring-engineer/smells/INDEX.md}}

Check code against smells:
  - long_method (from refactoring-engineer/smells/method/long-method.md)
  - duplicate_code (from refactoring-engineer catalog)
  - complex_conditional (from refactoring-engineer catalog)

Classify detected smells:
  - Refactorable: long_method, duplicate_code
  - Non-refactorable: security issues, performance issues
```

### Shared Quality Metrics

**Location**: `shared/integration/metrics-schema.json`

**Structure**:
```json
{
  "quality_metrics": {
    "cyclomatic_complexity": int,
    "lines_of_code": int,
    "duplication_percentage": float,
    "test_coverage": float,
    "security_issues": int,
    "performance_issues": int,
    "code_smells": [
      {
        "type": "long_method",
        "location": "file:line-range",
        "severity": "critical|important|suggestion"
      }
    ]
  }
}
```

**Usage**:
- **Code-Reviewer**: Establishes baseline metrics in Phase 1-2
- **Refactoring-Engineer**: Tracks metric improvements in Phase 5-6
- **Integration**: Both use same schema for metrics comparison

---

## Error Handling

### Invocation Failures

**Scenario 1: Target Agent Not Available**
```json
{
  "invocation_type": "error",
  "error_code": "AGENT_NOT_FOUND",
  "message": "refactoring-engineer not available",
  "fallback": "Continue with code-reviewer feedback only"
}
```

**Scenario 2: Invocation Prerequisites Not Met**
```json
{
  "invocation_type": "error",
  "error_code": "PREREQUISITES_NOT_MET",
  "message": "Tests not passing, cannot invoke refactoring-engineer",
  "required_actions": ["Fix failing tests", "Ensure green test suite"]
}
```

**Scenario 3: Invocation Timeout**
```json
{
  "invocation_type": "error",
  "error_code": "TIMEOUT",
  "message": "refactoring-engineer did not respond within 60 minutes",
  "fallback": "Provide refactoring recommendations without applying"
}
```

### Integration Failures

**Scenario 1: Verification Fails**
```json
{
  "verification_passed": false,
  "recommendation": "REQUEST_CHANGES",
  "critical_issues": [
    "Security regression detected: SQL injection vulnerability introduced",
    "Performance regression: 45% slower than baseline"
  ],
  "action_required": "REVERT_REFACTORING"
}
```

**Handling**: Refactoring-engineer receives failure, reverts changes, reports to user

---

## Integration Examples

### Example 1: Full Workflow (Review → Refactor → Verify)

```
User: "Review and improve this code"
    ↓
Code-Reviewer Phase 1-4:
    → Finds 2 critical security issues
    → Finds 3 refactorable smells
    ↓
Code-Reviewer Output:
    "Critical: Fix SQL injection (line 45) and XSS (line 78) first"
    "After fixing: 3 refactorable smells can be addressed"
    ↓
User: "Fix security issues, then refactor"
    ↓
[User fixes security issues]
    ↓
Code-Reviewer re-runs Phase 1:
    → Security issues fixed ✓
    → Refactorable smells still present
    ↓
Code-Reviewer invokes Refactoring-Engineer:
    Input: 3 smells (long_method, duplicate_code, complex_conditional)
    ↓
Refactoring-Engineer Phases 1-6:
    → Applies refactorings
    → Phase 5: Invokes code-reviewer verification
        ↓
    Code-Reviewer Verification:
        → Security regression: PASS ✓
        → Performance regression: PASS ✓
        → Quality improvement: 65% ✓
        → Recommendation: APPROVE
        ↓
    → Phase 6: Debt tracking with code-reviewer verification included
    ↓
Final Output:
    - Security issues fixed
    - Code refactored
    - Complexity reduced 65%
    - All verifications passed
```

### Example 2: Standalone Code Review (No Refactoring)

```
User: "Quick PR review for security and performance"
    ↓
Code-Reviewer Phase 1-4:
    → 1 security issue (secrets in code)
    → 2 performance issues (N+1 queries)
    → 0 refactorable smells
    ↓
Code-Reviewer Output:
    "Critical: Remove hardcoded API key (line 23)"
    "Important: Fix N+1 query in user_service (line 67)"
    "Suggestion: Consider caching for database calls"
    ↓
No refactoring-engineer invocation (no refactorable smells)
```

### Example 3: Refactoring Verification Only

```
User: [Working with refactoring-engineer]
    "Refactor user_service.py"
    ↓
Refactoring-Engineer Phases 1-4:
    → Detects long_method
    → Applies extract_method
    ↓
Refactoring-Engineer Phase 5:
    → Tests pass ✓
    → Metrics improved ✓
    → Invoke code-reviewer for comprehensive verification
        ↓
    Code-Reviewer Verification Mode:
        → Security: No regressions ✓
        → Performance: 2% improvement ✓
        → Architecture: Boundaries maintained ✓
        → Quality: Complexity reduced 60% ✓
        → Recommendation: APPROVE
        ↓
Refactoring-Engineer Phase 6:
    → Debt tracking includes code-reviewer verification
    → ROI calculation
    → Complete
```

---

## Integration Configuration

### Code-Reviewer Configuration

**File**: `code-reviewer/integration/config.json`
```json
{
  "integration_enabled": true,
  "refactoring_engineer_path": "../refactoring-engineer",
  "auto_invoke_refactoring": false,
  "ask_user_before_invoking": true,
  "verification_mode_enabled": true
}
```

### Refactoring-Engineer Configuration

**File**: `refactoring-engineer/integration/config.json`
```json
{
  "integration_enabled": true,
  "code_reviewer_path": "../code-reviewer",
  "invoke_verification_for_critical": true,
  "auto_invoke_verification": false
}
```

---

## Summary

**Integration Capabilities**:
1. ✅ Code-reviewer can trigger refactoring (Mode 2)
2. ✅ Refactoring-engineer can request verification (Mode 3)
3. ✅ Shared smell catalog (zero duplication)
4. ✅ Shared quality metrics schema
5. ✅ Graceful fallback if integration unavailable

**Key Principles**:
- **Independence**: Each agent fully functional standalone
- **Opt-in Integration**: User controls when integration happens
- **Clear Protocol**: Standardized invocation format
- **Error Handling**: Graceful degradation if integration fails

**Next Steps**: See `smell-catalog-integration.md` and `metrics-schema.json` for detailed technical specifications.

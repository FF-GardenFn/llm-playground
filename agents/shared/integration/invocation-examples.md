# Integration Invocation Examples

**Purpose**: Provide concrete examples of how code-reviewer and refactoring-engineer collaborate in different scenarios.

**Audience**: Users and agent developers understanding integration patterns.

---

## Example 1: Standalone Code Review (No Integration)

### Scenario
User wants quick PR review for security and architectural issues only, no refactoring needed.

### Flow

```
User: "Review this PR for security and architecture"
    ↓
Code-Reviewer:
    Phase 1: Automated Analysis
        → Security scan: Found 1 SQL injection vulnerability
        → Architecture check: Found 1 tight coupling issue
        → Smell detection: Found 2 refactorable smells (but not requested)

    Phase 2: Manual Review
        → API design: REST endpoints follow conventions
        → Error handling: Missing try-catch in 2 locations

    Phase 3: Feedback Synthesis
        → Critical: SQL injection (security)
        → Important: Missing error handling (architecture)
        → Suggestion: Tight coupling (architecture)

    Phase 4: Priority Assessment
        → No refactorable smells in critical/important categories
        → User only requested security/architecture review

    Phase 5: Recommendations
        → Provide structured review
        → DO NOT offer refactoring (not requested)
    ↓
Output:
  "REVIEW RESULTS:

  Critical Issues:
   ✗ SQL Injection (line 45): Use parameterized queries

  Important Issues:
   ✗ Missing error handling (lines 67, 89): Add try-catch blocks

  Suggestions:
   • Tight coupling between UserService and Database (line 120)

  2 refactorable smells detected but not included (use --include-refactoring)"
```

**Integration**: None - standalone operation

---

## Example 2: Code Review Triggers Refactoring

### Scenario
User wants comprehensive code improvement - review identifies issues, some are refactorable.

### Flow

```
User: "Review and improve this code"
    ↓
Code-Reviewer:
    Phase 1: Automated Analysis
        → Security: 0 issues ✓
        → Performance: 1 N+1 query issue
        → Smells: 3 refactorable (long_method, duplicate_code, complex_conditional)

    Phase 2: Manual Review
        → Architecture: Component boundaries clear ✓
        → Testing: Test coverage 85% ✓

    Phase 3: Feedback Synthesis
        → Important: N+1 query (performance, NOT refactorable)
        → Important: 3 code smells (quality, REFACTORABLE)

    Phase 4: Priority Assessment
        → Classify refactorable issues:
            • long_method at src/user.py:45-120 → extract_method
            • duplicate_code at src/user.py:150-180 → extract_method
            • complex_conditional at src/user.py:200-220 → decompose_conditional

    Phase 5: Recommendations
        → Provide feedback
        → Offer to invoke refactoring-engineer for refactorable issues
    ↓
Code-Reviewer Output:
  "REVIEW RESULTS:

  Important Issues:
   ✗ N+1 query problem (line 100): Use eager loading or join

  Refactorable Issues (3):
   • Long Method (line 45): 75 lines, complexity 15
   • Duplicate Code (line 150): 85% similar to admin_service.py:90
   • Complex Conditional (line 200): Nested 4 levels deep

  Would you like me to invoke refactoring-engineer to fix these?"
    ↓
User: "Yes, refactor"
    ↓
Code-Reviewer invokes Refactoring-Engineer:

  Invocation JSON:
  {
    "invocation_type": "refactoring_request",
    "source_agent": "code-reviewer",
    "detected_smells": [
      {
        "type": "long_method",
        "location": "src/user.py:45-120",
        "severity": "important",
        "suggested_refactoring": "extract_method"
      },
      {
        "type": "duplicate_code",
        "location": "src/user.py:150-180",
        "severity": "important",
        "suggested_refactoring": "extract_method"
      },
      {
        "type": "complex_conditional",
        "location": "src/user.py:200-220",
        "severity": "important",
        "suggested_refactoring": "decompose_conditional"
      }
    ],
    "context": {
      "test_coverage": 85,
      "tests_passing": true
    }
  }
    ↓
Refactoring-Engineer:
    Phase 1: Smell Detection
        → Uses provided smell list from code-reviewer
        → Confirms smells exist

    Phase 2: Refactoring Selection
        → long_method → Extract Method (Easy, Low Risk)
        → duplicate_code → Extract Method (Easy, Low Risk)
        → complex_conditional → Decompose Conditional (Medium, Low Risk)

    Phase 3: Safety Check
        → Prerequisites: Tests passing ✓, Coverage 85% ✓
        → Risk: Low (all easy/medium patterns)

    Phase 4: Implementation
        → Extract 3 methods from long method
        → Extract shared method from duplicate code
        → Decompose conditional into guard clauses
        → Tests remain green ✓

    Phase 5: Verification
        → Tests: All passing ✓
        → Metrics: Complexity 15→6 (60% improvement)
        → Behavior: Preserved ✓

    Phase 6: Debt Tracking
        → Time invested: 30 minutes
        → Estimated savings: 80 hours/year
        → ROI: Positive
    ↓
Refactoring-Engineer Output:
  {
    "status": "success",
    "refactorings_applied": [
      {"smell": "long_method", "pattern": "extract_method"},
      {"smell": "duplicate_code", "pattern": "extract_method"},
      {"smell": "complex_conditional", "pattern": "decompose_conditional"}
    ],
    "metrics": {
      "complexity_before": 15,
      "complexity_after": 6,
      "improvement_percentage": 60
    }
  }
    ↓
Code-Reviewer receives result:
  "Refactoring complete:
   ✓ Complexity reduced 60% (15 → 6)
   ✓ All tests passing
   ✓ 3 smells addressed

   Remaining issues:
   • N+1 query (manual fix required)"
```

**Integration**: Sequential (Code-Reviewer → Refactoring-Engineer)

---

## Example 3: Refactoring Invokes Review for Verification

### Scenario
User refactoring code, wants comprehensive verification beyond basic tests.

### Flow

```
User: "Refactor user_service.py"
    ↓
Refactoring-Engineer:
    Phase 1: Smell Detection
        → Found: long_method (75 lines, complexity 15)

    Phase 2: Refactoring Selection
        → Pattern: Extract Method

    Phase 3: Safety Check
        → Tests: Passing ✓
        → Risk: Low

    Phase 4: Implementation
        → Extracted 3 methods
        → Tests still passing ✓

    Phase 5: Verification
        → Basic checks: Tests pass ✓, Metrics improved ✓
        → Critical code detected → Invoke code-reviewer for comprehensive verification
    ↓
Refactoring-Engineer invokes Code-Reviewer:

  Invocation JSON:
  {
    "invocation_type": "verification_request",
    "source_agent": "refactoring-engineer",
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
    "verification_requirements": {
      "check_security_regression": true,
      "check_performance_regression": true,
      "check_architecture_integrity": true
    }
  }
    ↓
Code-Reviewer (Verification Mode):
    Phase 1: Security Regression Check
        → Scan code_after for new vulnerabilities
        → Compare with code_before
        → Result: No new security issues ✓

    Phase 2: Performance Regression Check
        → Profile execution time
        → code_before: 45ms, code_after: 44ms (2% faster)
        → Result: Performance improved ✓

    Phase 3: Architecture Integrity Check
        → Verify component boundaries maintained
        → Check no new tight coupling introduced
        → Result: Architecture intact ✓

    Phase 4: Quality Assessment
        → Complexity: 15 → 6 (60% improvement) ✓
        → Duplication: No new duplication ✓
        → Maintainability: Score improved A- → A ✓

    Phase 5: Final Recommendation
        → All checks passed
        → No new issues introduced
        → Quality significantly improved
    ↓
Code-Reviewer Output:
  {
    "verification_passed": true,
    "checks": {
      "security_regression": {
        "passed": true,
        "issues_found": 0
      },
      "performance_regression": {
        "passed": true,
        "performance_delta_percent": -2
      },
      "architecture_integrity": {
        "passed": true,
        "issues_found": 0
      },
      "quality_improvement": {
        "complexity_reduction": 60,
        "maintainability_score": "A"
      }
    },
    "recommendation": "APPROVE",
    "confidence": "high"
  }
    ↓
Refactoring-Engineer Phase 6: Debt Tracking
    → Include code-reviewer verification results
    → Comprehensive verification passed ✓
    → ROI calculation
    ↓
Refactoring-Engineer Output:
  "Refactoring complete:
   ✓ Extracted 3 methods
   ✓ Complexity reduced 60%
   ✓ Comprehensive verification (code-reviewer): APPROVED
   ✓ No security/performance/architecture regressions

   ROI: 30 min invested, 80 hours/year saved"
```

**Integration**: Sequential (Refactoring-Engineer → Code-Reviewer)

---

## Example 4: Full Bidirectional Workflow

### Scenario
Complex codebase needing review, security fixes, and refactoring in sequence.

### Flow

```
User: "Comprehensive code improvement for user_service.py"
    ↓
Code-Reviewer Phase 1-4:
    → Security: 2 issues (SQL injection, XSS)
    → Performance: 1 issue (N+1 query)
    → Smells: 3 refactorable (long_method, duplicate_code, large_class)
    ↓
Code-Reviewer Output:
  "Found 6 issues:

   Critical (fix first):
    ✗ SQL injection (line 45)
    ✗ XSS vulnerability (line 78)

   Important:
    ✗ N+1 query (line 100)

   Refactorable (after fixing critical):
    • Long method (line 120)
    • Duplicate code (line 150)
    • Large class (250 lines)

   Recommended workflow:
   1. Fix security issues first
   2. Fix performance issue
   3. Refactor code smells"
    ↓
User: "Fix security first"
[User fixes SQL injection and XSS]
    ↓
User: "Re-review"
Code-Reviewer:
    → Security: 0 issues ✓ (previously 2)
    → Performance: 1 issue (N+1 query still present)
    → Smells: 3 refactorable
    ↓
User: "Fix N+1 query"
[User fixes N+1 query]
    ↓
User: "Now refactor"
Code-Reviewer invokes Refactoring-Engineer:
    Input: 3 refactorable smells
    ↓
Refactoring-Engineer Phase 1-4:
    → Applies refactorings
    → Tests passing
    ↓
Refactoring-Engineer Phase 5:
    → Invokes Code-Reviewer for verification
    ↓
Code-Reviewer Verification:
    → Security: No regressions ✓
    → Performance: 3% faster ✓
    → Quality: Complexity reduced 65% ✓
    → Recommendation: APPROVE
    ↓
Refactoring-Engineer Phase 6:
    → Debt tracking with verification results
    ↓
Final Output:
  "Comprehensive improvement complete:
   ✓ Security: Fixed 2 critical vulnerabilities
   ✓ Performance: Fixed N+1 query, 3% faster
   ✓ Quality: Reduced complexity 65%
   ✓ Refactoring verified: No regressions

   Code health: D → A (significant improvement)"
```

**Integration**: Bidirectional
- Code-Reviewer → Refactoring-Engineer (trigger refactoring)
- Refactoring-Engineer → Code-Reviewer (verification)

---

## Example 5: Integration Failure (Graceful Degradation)

### Scenario
Code-reviewer tries to invoke refactoring-engineer but it's unavailable.

### Flow

```
User: "Review and refactor"
    ↓
Code-Reviewer Phase 1-4:
    → Detects 3 refactorable smells
    ↓
Code-Reviewer attempts to invoke Refactoring-Engineer:
    ↓
Error: refactoring-engineer not available
    ↓
Code-Reviewer (Graceful Fallback):
    Phase 5: Recommendations (without refactoring)
        → Provide detailed refactoring recommendations
        → Suggest manual refactoring steps
        → Reference refactoring patterns
    ↓
Output:
  "Found 3 refactorable smells:

   Long Method (line 45):
    • Current: 75 lines, complexity 15
    • Recommended: Extract Method refactoring
    • Suggested methods to extract:
        - validate_user() from lines 45-60
        - process_payment() from lines 61-85
        - send_confirmation() from lines 86-120

   Duplicate Code (line 150):
    • 85% similar to admin_service.py:90-120
    • Recommended: Extract shared logic to common utility

   Note: refactoring-engineer not available for automated refactoring.
   See refactorings/composing-methods/extract-method.md for manual steps."
```

**Integration**: Attempted but failed, graceful fallback to recommendations

---

## Example 6: Selective Verification

### Scenario
Most refactorings use basic verification, only critical code uses code-reviewer.

### Flow

```
User: "Refactor utility.py (low-risk code)"
    ↓
Refactoring-Engineer Phase 1-4:
    → Applies extract_method refactoring
    ↓
Refactoring-Engineer Phase 5:
    → Risk assessment: Low
    → Code criticality: Low (utility code)
    → Decision: Use basic verification (no code-reviewer invocation)
    → Tests pass ✓
    → Metrics improved ✓
    ↓
Output: "Refactoring complete (basic verification)"

---

User: "Refactor payment_service.py (critical code)"
    ↓
Refactoring-Engineer Phase 1-4:
    → Applies extract_method refactoring
    ↓
Refactoring-Engineer Phase 5:
    → Risk assessment: Low (extract_method is easy)
    → Code criticality: HIGH (payment processing)
    → Decision: Invoke code-reviewer for comprehensive verification
    ↓
Code-Reviewer Verification:
    → Security: No regressions ✓
    → Performance: No regressions ✓
    → Architecture: Intact ✓
    ↓
Output: "Refactoring complete (comprehensive verification: APPROVED)"
```

**Integration**: Conditional (based on code criticality)

---

## Summary Table

| Example | Trigger | Integration Type | Code-Reviewer Role | Refactoring-Engineer Role |
|---------|---------|------------------|-------------------|--------------------------|
| 1. Standalone Review | User request | None | Full 5-phase review | Not invoked |
| 2. Review → Refactor | CR detects smells | Sequential (CR→RE) | Detect + trigger | Apply refactorings |
| 3. Refactor → Verify | RE needs verification | Sequential (RE→CR) | Comprehensive verification | Apply + verify |
| 4. Bidirectional | User request | Bidirectional | Detect + verify | Apply refactorings |
| 5. Graceful Failure | Integration error | Failed → Fallback | Recommendations only | Not available |
| 6. Selective Verify | Criticality-based | Conditional | Verify critical code only | Apply + decide |

---

## Integration Decision Tree

```
User Request
    ↓
Is this a review request?
    ├─→ YES: Code-Reviewer
    │       ↓
    │   Are refactorable smells found?
    │       ├─→ YES: Offer to invoke Refactoring-Engineer
    │       └─→ NO: Provide feedback only
    │
    └─→ NO: Is this a refactoring request?
            ├─→ YES: Refactoring-Engineer
            │       ↓
            │   Is code critical?
            │       ├─→ YES: Invoke Code-Reviewer for verification
            │       └─→ NO: Basic verification
            │
            └─→ NO: Other agent
```

---

## Best Practices

### When to Use Integration

**Use Code-Reviewer → Refactoring-Engineer when**:
- Code review finds refactorable smells
- User wants automated improvement
- Tests are green (prerequisite)

**Use Refactoring-Engineer → Code-Reviewer when**:
- Refactoring critical production code
- Need comprehensive verification
- Basic tests not sufficient

**Don't use integration when**:
- Standalone review sufficient
- No refactorable issues found
- User explicitly requests no refactoring

### Performance Considerations

**Integration adds latency**:
- Code-Reviewer standalone: ~2-5 minutes
- + Refactoring-Engineer invocation: +10-30 minutes
- + Code-Reviewer verification: +2-5 minutes
- Total: ~15-40 minutes for full bidirectional workflow

**Optimization**:
- Use selective verification (only for critical code)
- Cache smell detection results
- Reuse metrics between agents

---

## Conclusion

Integration provides flexible collaboration between code-reviewer and refactoring-engineer:

1. **Standalone**: Fast, focused reviews
2. **Sequential**: Natural workflow (detect → fix)
3. **Bidirectional**: Comprehensive improvement
4. **Graceful Degradation**: Works even if integration fails

Users control integration through request phrasing and confirmation prompts.

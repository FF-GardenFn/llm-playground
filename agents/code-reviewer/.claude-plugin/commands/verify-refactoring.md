---
description: Verify that a refactoring is safe to merge (verification mode)
allowed-tools: Read, Write, AskUserQuestion
argument-hint: [--before path --after path --summary path]
---

# Refactoring Verification Mode

Verification mode for comprehensive security, performance, and architecture regression checks. Validates that refactorings are behavior-preserving and safe to merge.

## Operational Mode: Verification

**Context**: Invoked by refactoring-engineer Phase 5 to validate refactorings independently.

Complete verification workflow:
  → Load {{load: ../integration/verification-mode.md}}

---

## Required Inputs

Ask user to provide:
1. **Original code path** (before refactoring)
2. **Refactored code path** (after refactoring)
3. **Refactoring summary** (REFACTORING_SUMMARY.md from refactoring-engineer)

---

## Verification Checks

**5 Verification Categories**:

### 1. Security Verification
When checking security regressions:
  → Load {{load: ../verification/refactoring-verification.md#security}}

**Check**: No new SQL injection, XSS, secrets exposed; validation logic preserved

### 2. Performance Verification
When checking performance:
  → Load {{load: ../verification/refactoring-verification.md#performance}}

**Check**: Query count, complexity, runtime, memory within thresholds

### 3. Functional Verification
When checking behavior:
  → Load {{load: ../verification/refactoring-verification.md#functional}}

**Check**: All tests pass, coverage maintained, behavior equivalent

### 4. Code Quality Verification
When checking quality:
  → Load {{load: ../verification/refactoring-verification.md#quality}}

**Check**: Complexity reduced, readability improved, SRP improved

### 5. Diff Analysis
When analyzing changes:
  → Load {{load: ../verification/refactoring-verification.md#diff}}

**Check**: Only expected files, behavior-preserving, logic moved not changed

---

## Verification Thresholds

**Hard Limits** (Cannot Exceed):
- Complexity: No increase allowed
- Performance Runtime: Max 20% increase
- Performance Memory: Max 10% increase
- Database Queries: No increase allowed
- Test Coverage: No decrease allowed

**Gate**: If any threshold exceeded → UNSAFE

---

## Decision Tree

**Outcome determination**:

IF all checks pass AND no thresholds exceeded:
  → **SAFE TO MERGE**
  → Output: VERIFICATION_RESULT.md with SAFE status

ELSE IF critical issue found (security regression, >20% performance degradation):
  → **UNSAFE - REVERT RECOMMENDED**
  → Output: VERIFICATION_RESULT.md with UNSAFE status + critical issues

ELSE IF ambiguous results (edge case, unclear impact):
  → **MANUAL REVIEW REQUIRED**
  → Output: VERIFICATION_RESULT.md with MANUAL status + investigation needed

**Outcome templates**:
  → Load {{load: ../verification/refactoring-verification.md#outcomes}}

---

## Metrics Comparison

Metrics format:
  → Load {{load: ../integration/metrics-sharing.md}}

**Compare**:
- Complexity (before → after)
- LOC (before → after)
- Test coverage (before → after)
- Query count (before → after)

---

## Verification Commands

Tools for verification:
  → Load {{load: ../verification/commands.md}}

**Categories**: Security scan, performance profiling, diff analysis

---

## Start Verification

Ask user: "Please provide paths to before/after code and refactoring summary for verification."

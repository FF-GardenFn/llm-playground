# Anti-Pattern: Premature Implementation

## Problem
Starting to code before understanding the codebase leads to pattern mismatches, duplicate code, and rework.

## Example: Wrong Approach

```
User: "Add email validation to registration"

Developer immediately writes:
- New EmailValidator class (80 lines)
- New validation pattern (doesn't match existing style)
- No tests (testing strategy unknown)
- Integration in wrong layer (route instead of service)
```

**Code review finds:**
- 3 existing validators that should have been reused
- Validation in wrong layer (inconsistent with codebase)
- Missing tests
- Need to delete and rewrite

**Result:** 2 hours wasted, 100 lines written then deleted

## Correct Approach

```
User: "Add email validation to registration"

Developer follows reconnaissance:
1. Search: `python atools/search_codebase.py --pattern "validation"`
2. Finds: validators/email_validator.py (exists, tested, 40 lines)
3. Identifies: Integration point in services/user_service.py (service layer)
4. Pattern: Other validators used in service layer, not route layer
5. Plans: Reuse existing validator, add 1 line to service

Implementation:
- services/user_service.py: +1 line (call validator)
- tests/test_user_service.py: +15 lines (validation tests)
```

**Result:** 15 minutes, 16 lines added, follows conventions, tested

## How Structure Prevents This

- Phase 1 (Reconnaissance) must complete before Phase 2 (Design)
- Cannot skip search step - it's first phase requirement
- File dependencies enforce sequence
- phases/02_design/inputs.md requires ../01_reconnaissance/outputs/report.md

## Key Lesson

**5 minutes of reconnaissance saves hours of rework.**

Always search before building. Understanding what exists is faster than building then deleting.

---
description: Start validation phase - production readiness verification (Phase 4)
allowed-tools: Bash(../atools/run_tests.sh:*, ../atools/lint_code.sh:*, python ../atools/analyze_complexity.py:*), Read, Write, TodoWrite
argument-hint: []
---

# Validation Command

Execute Phase 4: Full production readiness verification - tests, linting, complexity, completion checklist.

## What this does

1. **Loads implementation** - Requires Phase 3 complete
2. **Runs all verification tools**:
   - `run_tests.sh` - All tests pass, no regressions
   - `lint_code.sh` - Code quality verification
   - `analyze_complexity.py` - Complexity assessment (target: <10)
3. **Verifies completion criteria** - Uses checklist from Phase 4
4. **Documents validation** - Create validation_report.md

## Usage

```bash
# Start validation phase (requires implementation complete)
/validate

# Re-run validation after fixes
/validate --recheck
```

## Your Task

1. **Load validation workflow**: Read `../phases/04_validation/README.md`
2. **Verify implementation complete**: Check for `../phases/03_implementation/outputs/test_results.md`
3. **Run verification tools**:
   - `bash ../atools/run_tests.sh` - Verify all tests pass
   - `bash ../atools/lint_code.sh` - Check code quality
   - `python ../atools/analyze_complexity.py` - Assess complexity
4. **Review checklist**: Load `../phases/04_validation/checklist.md`
5. **Verify all criteria met**:
   - All tests pass (new + existing)
   - Linting clean
   - Complexity reasonable (<10)
   - Follows patterns
   - Edge cases handled
   - Error handling in place
   - Performance acceptable
   - Maintainable
6. **Create validation_report.md**: Document in `../phases/04_validation/outputs/`
7. **Report**: Validation status, any issues, completion confirmation

## Expected Output

```
✓ Validation complete - PRODUCTION READY

Verification Tool Results:

1. Test Execution (run_tests.sh):
✓ All tests pass: 62/62
✓ No regressions detected
✓ New tests: 15 (all passing)
✓ Existing tests: 47 (all still passing)
✓ Coverage: 98% of new code

2. Code Quality (lint_code.sh):
✓ No linting errors
✓ No warnings
✓ Formatting consistent with codebase
✓ Auto-fixes applied: 0

3. Complexity Analysis (analyze_complexity.py):
✓ validate_email(): complexity 4 (target: <10) ✓
✓ validate_password(): complexity 6 (target: <10) ✓
✓ validate_username(): complexity 3 (target: <10) ✓
✓ Average complexity: 4.3 (excellent)

Completion Checklist:

Core Implementation:
✓ All tests pass (new + existing, no regressions)
✓ Linting clean (no warnings or errors)
✓ Complexity reasonable (all functions <10)
✓ Follows codebase patterns (validators.py pattern)

Edge Cases & Error Handling:
✓ Edge cases handled (empty strings, max length, special chars)
✓ Error handling in place (ValidationError with clear messages)
✓ Input validation (type checking, bounds checking)

Code Quality:
✓ Self-documenting code (clear names, docstrings)
✓ Strategic comments ("why" not "what")
✓ Maintainable by junior engineer (simple, clear)

Performance:
✓ Performance acceptable (O(1) format checks, indexed DB queries)
✓ No obvious bottlenecks
✓ Scales to 1000x/sec

Integration:
✓ Integrates with existing registration.py
✓ Reuses existing utilities (is_valid_email, check_unique)
✓ No breaking changes to existing features

validation_report.md created: ../phases/04_validation/outputs/validation_report.md

→ TASK COMPLETE - PRODUCTION READY
→ Implementation validated and ready for deployment
```

## Verification Tools

**run_tests.sh** - Execute all tests
```bash
bash ../atools/run_tests.sh
```

**lint_code.sh** - Code quality check
```bash
bash ../atools/lint_code.sh auth/validators.py users/registration.py
```

**analyze_complexity.py** - Complexity assessment
```bash
python ../atools/analyze_complexity.py auth/validators.py
```

See `../SKILLS.md` for tool usage details and troubleshooting.

## Completion Checklist

Load full checklist: `../phases/04_validation/checklist.md`

**Must verify all items before declaring complete:**
- Tests (pass, no regressions, coverage)
- Quality (linting, complexity, patterns)
- Robustness (edge cases, errors, performance)
- Maintainability (clear code, documentation)

## Gate

**Cannot declare task complete without**:
- [ ] Implementation complete (Phase 3 outputs exist)
- [ ] All tests pass (run_tests.sh = 100%)
- [ ] Linting clean (lint_code.sh = no errors/warnings)
- [ ] Complexity acceptable (analyze_complexity.py = all <10)
- [ ] All checklist items verified
- [ ] validation_report.md created in outputs/
- [ ] Production ready confirmed

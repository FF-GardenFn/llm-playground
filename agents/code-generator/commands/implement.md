---
description: Start implementation phase - write code with tests, verify continuously (Phase 3)
allowed-tools: Bash(../atools/run_tests.sh:*), Read, Write, Edit, TodoWrite
argument-hint: []
---

# Implementation Command

Execute Phase 3: Write code + tests using TDD cycle, verify continuously against design.

## What this does

1. **Loads design proposal** - Requires Phase 2 complete
2. **Implements with TDD** - Write test, write code, verify, refactor
3. **Verifies continuously** - Run tests after each change using run_tests.sh
4. **Documents results** - Create test_results.md

## Usage

```bash
# Start implementation phase (requires design complete)
/implement

# Resume implementation
/implement --continue
```

## Your Task

1. **Load implementation workflow**: Read `../phases/03_implementation/README.md`
2. **Verify design complete**: Check for `../phases/02_design/outputs/design_proposal.md`
3. **Follow TDD cycle** (see `../phases/03_implementation/tdd_cycle.md`):
   - Write failing test
   - Write minimal code to pass
   - Run tests
   - Refactor if needed
   - Repeat
4. **Implement all components** from design proposal
5. **Run tests continuously**: Use `../atools/run_tests.sh` after each change
6. **Create outputs**:
   - `code/` - Implementation files
   - `tests/` - Test files
   - `test_results.md` - Final test run output
7. **Report**: Implementation status, test results, any deviations from design

## Expected Output

```
✓ Implementation complete

TDD Cycle Summary:

Cycle 1: validate_email()
- Test: test_validate_email_format() - FAIL
- Code: Basic format validation - PASS
- Test: test_validate_email_uniqueness() - FAIL
- Code: Add uniqueness check - PASS
- Refactor: Extract DB query logic - ALL PASS

Cycle 2: validate_password()
- Test: test_validate_password_length() - FAIL
- Code: Length validation (8-128) - PASS
- Test: test_validate_password_complexity() - FAIL
- Code: Add complexity checks - PASS
- Refactor: Simplify regex - ALL PASS

Cycle 3: validate_username()
- Test: test_validate_username_format() - FAIL
- Code: Format validation - PASS
- Test: test_validate_username_uniqueness() - FAIL
- Code: Add uniqueness check - PASS
- Refactor: None needed - ALL PASS

Cycle 4: Integration
- Test: test_registration_with_validators() - FAIL
- Code: Import validators in registration.py - PASS
- Test: test_registration_error_messages() - PASS
- All tests: 15 new + 47 existing = 62 total - ALL PASS

Implementation Files:
✓ auth/validators.py - 3 new functions (78 lines)
✓ users/registration.py - Modified to use validators (12 lines changed)
✓ tests/test_validators.py - 15 new test cases (145 lines)

Test Results (run_tests.sh):
✓ All tests pass: 62/62
✓ No regressions
✓ Coverage: 98% (validators.py fully covered)

test_results.md created: ../phases/03_implementation/outputs/test_results.md

→ Implementation complete
→ Recommend: /validate for production readiness verification
```

## TDD Cycle

**Red → Green → Refactor**

1. **Write test** (Red)
   - Write test that fails
   - Confirms test catches the problem

2. **Write code** (Green)
   - Minimal code to pass test
   - Run tests: should pass

3. **Refactor** (Optional)
   - Improve code quality
   - Run tests: must still pass

4. **Repeat**
   - Next test, next code
   - Incremental progress

See `../phases/03_implementation/tdd_cycle.md` for detailed guidance.

## Tools

**run_tests.sh** - Execute test suite, verify no breakage
```bash
bash ../atools/run_tests.sh  # Run all tests
bash ../atools/run_tests.sh tests/test_validators.py  # Run specific test
```

See `../SKILLS.md` for test interpretation patterns.

## Gate

**Cannot proceed to /validate without**:
- [ ] Design proposal exists (Phase 2 complete)
- [ ] All components implemented (from design)
- [ ] Tests written for all new code
- [ ] All tests pass (new + existing, no regressions)
- [ ] test_results.md created in outputs/
- [ ] Code follows patterns (from reconnaissance)

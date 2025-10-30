---
description: Start design phase - plan minimal approach (Phase 2)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: []
---

# Design Command

Execute Phase 2: Plan minimal, safe approach following patterns identified in reconnaissance.

## What this does

1. **Loads reconnaissance findings** - Requires Phase 1 complete
2. **Plans approach** - Minimal change that solves problem
3. **Identifies components** - What files, functions, classes to modify/create
4. **Assesses risks** - What can break, how to mitigate
5. **Documents design** - Create design_proposal.md

## Usage

```bash
# Start design phase (requires reconnaissance complete)
/design

# Review design before implementing
/design --review
```

## Your Task

1. **Load design workflow**: Read `../phases/02_design/README.md`
2. **Verify reconnaissance complete**: Check for `../phases/01_reconnaissance/outputs/reconnaissance_report.md`
3. **Plan approach**: Minimal change that follows existing patterns
4. **Identify components**:
   - Files to modify (which existing files)
   - Files to create (new files needed)
   - Functions/classes to add or change
5. **Plan data flow**: How data moves through components
6. **Assess risks**: What can break? How to prevent?
7. **Create design_proposal.md**: Document in `../phases/02_design/outputs/`
8. **Report**: Approach summary, components, risks, rationale

## Expected Output

```
✓ Design complete

Design Approach:
**Minimal Change:** Add 3 validation functions to existing auth/validators.py

Components:

Files to Modify:
- `auth/validators.py` - Add validate_email(), validate_password(), validate_username()
- `users/registration.py` - Import and use new validators
- `tests/test_validators.py` - Add test cases for new validators

Files to Create:
- None (reusing existing structure)

Functions to Add:
1. `validate_email(email: str) -> ValidationResult`
   - Reuses `utils/validation.py::is_valid_email()`
   - Checks format + uniqueness

2. `validate_password(password: str) -> ValidationResult`
   - Length check (8-128 chars)
   - Complexity check (uppercase, lowercase, digit, special)

3. `validate_username(username: str) -> ValidationResult`
   - Length check (3-30 chars)
   - Format check (alphanumeric + underscore)
   - Uniqueness check

Data Flow:
1. User submits registration form
2. `users/registration.py::register_user()` calls validators
3. Validators return ValidationResult (success=bool, message=str)
4. If any validator fails, return 400 with error message
5. If all pass, create user account

Risk Assessment:
- Risk: Breaking existing registration
  - Mitigation: Import validators, don't change registration logic

- Risk: Performance (uniqueness checks hit DB)
  - Mitigation: Use indexed columns, add caching if needed

- Risk: Inconsistent validation across endpoints
  - Mitigation: Centralize in validators.py, reuse everywhere

Why This Design:
- Follows existing pattern (validators.py)
- Minimal change (3 functions in 1 file)
- Reuses existing utilities
- Testable (pure functions with clear I/O)
- No architectural changes needed

design_proposal.md created: ../phases/02_design/outputs/design_proposal.md

→ Design complete
→ Recommend: /implement to build with tests
```

## Gate

**Cannot proceed to /implement without**:
- [ ] Reconnaissance report exists (Phase 1 complete)
- [ ] Approach planned (minimal, follows patterns)
- [ ] Components identified (files, functions, classes)
- [ ] Data flow documented
- [ ] Risks assessed with mitigations
- [ ] design_proposal.md created in outputs/

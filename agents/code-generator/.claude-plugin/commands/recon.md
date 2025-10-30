---
description: Start reconnaissance phase - understand codebase before coding (Phase 1)
allowed-tools: Bash(python ../atools/search_codebase.py:*), Read, Write, TodoWrite, Glob, Grep
argument-hint: [requirement-description]
---

# Reconnaissance Command

Execute Phase 1: Understand codebase, identify patterns, locate integration points before writing code.

## What this does

1. **Parse requirement** - Clarify what's being requested
2. **Search for patterns** - Find similar implementations using search_codebase.py
3. **Identify conventions** - Discover naming, structure, testing patterns
4. **Locate integration points** - Find where new code connects
5. **Document findings** - Create reconnaissance_report.md

## Usage

```bash
# Start reconnaissance with requirement
/recon "Add input validation to user registration form"

# Reconnaissance for API endpoint
/recon "Create REST endpoint for retrieving user profile"

# Complex feature reconnaissance
/recon "Implement OAuth2 authentication flow"
```

## Your Task

1. **Load reconnaissance workflow**: Read `../phases/01_reconnaissance/README.md`
2. **Clarify requirement**: Ensure you understand what's being requested
3. **Search codebase**: Use `../atools/search_codebase.py` to find:
   - Similar features or functions
   - Naming conventions
   - Existing utilities to reuse
   - Testing patterns
4. **Identify integration points**: Where will new code connect?
5. **Create reconnaissance_report.md**: Document in `../phases/01_reconnaissance/outputs/`
6. **Report**: Similar code found, patterns identified, integration points

## Expected Output

```
✓ Reconnaissance complete

Requirement Understanding:
- Feature: Input validation for user registration (email, password, username)
- Constraints: Must validate format, check uniqueness, return clear errors
- Success: Invalid inputs rejected with helpful messages

Similar Code Found:
- `auth/validators.py`: Email validation using regex
- `users/registration.py`: Existing registration logic
- `utils/validation.py`: Generic validation helpers

Patterns Identified:
- Naming: `validate_<field>()` functions
- Structure: Validators in validators.py, imported by features
- Testing: `tests/test_validators.py` with parameterized tests
- Error handling: ValidationError exceptions with message field

Integration Points:
- File to modify: `auth/validators.py` (add validation functions)
- Import in: `users/registration.py` (use new validators)
- Tests: `tests/test_validators.py` (add validation tests)

Existing Utilities to Reuse:
- `utils/validation.py::is_valid_email()` - email format checking
- `utils/validation.py::check_length()` - length validation
- `db/queries.py::check_unique()` - uniqueness checking

reconnaissance_report.md created: ../phases/01_reconnaissance/outputs/reconnaissance_report.md

→ Reconnaissance complete
→ Recommend: /design to plan implementation approach
```

## Tools

**search_codebase.py** - Find similar code, patterns, conventions
```bash
python ../atools/search_codebase.py --pattern "validation"
python ../atools/search_codebase.py --pattern "registration"
python ../atools/search_codebase.py --file-type "test"
```

See `../SKILLS.md` for detailed tool usage patterns.

## Gate

**Cannot proceed to /design without**:
- [ ] Requirement clarified and understood
- [ ] Similar code searched and found
- [ ] Patterns and conventions identified
- [ ] Integration points located
- [ ] reconnaissance_report.md created in outputs/

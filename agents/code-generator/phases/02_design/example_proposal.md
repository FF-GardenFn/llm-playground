# Example: Design Proposal

## Feature
Add email validation to user registration

---

## Approach
Reuse existing `EmailValidator` class, integrate into `UserService.register()` method before database save. Validation occurs in service layer (not route layer), follows established pattern.

---

## Components

**1. Modify: `services/user_service.py`**
- Add import: `from validators.email_validator import EmailValidator`
- In `register(self, email, password)` method:
  - Add line: `EmailValidator().validate(email)` before `User.create(...)`
  - Let `ValidationError` propagate (existing error handling catches it)

**2. Reuse: `validators/email_validator.py`**
- No changes needed
- Already handles: format validation, empty input, edge cases
- Already tested: `tests/unit/validators/test_email_validator.py`

**3. Create: `tests/unit/services/test_user_registration_validation.py`**
- Test: valid email → registration succeeds
- Test: invalid email → `ValidationError` raised
- Test: empty email → `ValidationError` raised
- Test: edge cases (whitespace, special chars)

---

## Data Flow

```
1. Request arrives at route: POST /register
   Data: {email: "user@example.com", password: "..."}

2. Route calls: UserService.register(email, password)

3. UserService validates:
   EmailValidator().validate(email)  ← NEW STEP
   - If invalid → raises ValidationError
   - If valid → continues

4. UserService creates user:
   user = User.create(email, password)

5. Route returns:
   - Success: 201 Created
   - Validation error: 400 Bad Request
```

---

## Justification

**Pattern Reuse:**
- Follows existing validation pattern (BaseValidator → validate() method)
- Integrates at service layer (matches username validation in `services/user_service.py:45`)
- Raises `ValidationError` (consistent with existing validators)

**Minimal Change:**
- Only 2 lines added (1 import, 1 validation call)
- No changes to route layer, data layer, or validator itself
- Leverages existing, tested validator

**Testability:**
- Service method easily testable (pure function, clear I/O)
- Can test with mocked validator if needed
- Integration tests verify end-to-end flow

---

## Risks & Mitigations

**Risk: Existing validator might not handle all edge cases**
- Mitigation: Review `tests/unit/validators/test_email_validator.py` first
- Validation: Confirmed tests cover empty, malformed, length edge cases

**Risk: ValidationError handling might differ in route layer**
- Mitigation: Check existing error handling pattern in `routes/auth.py`
- Validation: Confirmed route has `@handle_errors` decorator that catches ValidationError → 400

**Risk: Performance impact of validation on high-traffic endpoint**
- Mitigation: Email regex validation is O(n) where n = email length, negligible
- Validation: Existing validators don't cause performance issues

**Risk: Breaking existing tests**
- Mitigation: Run full test suite after implementation
- Validation: Existing tests mock or provide valid emails, should pass

---

## Alternative Considered

**Alternative 1: Validate in route layer**
- Pros: Fail faster, less processing
- Cons: Breaks consistency (other validation in service layer)
- Decision: Use service layer for consistency

**Alternative 2: Add validation to User model**
- Pros: Validation always enforced
- Cons: Couples validation to data layer, harder to test
- Decision: Keep validation in service layer (separation of concerns)

**Alternative 3: Use external library (e.g., email-validator)**
- Pros: More robust validation
- Cons: New dependency, existing validator sufficient
- Decision: Use existing validator (YAGNI principle)

---

## Testing Plan

**Unit Tests:**
1. `test_register_with_valid_email()` - Happy path
2. `test_register_with_invalid_email()` - Expect ValidationError
3. `test_register_with_empty_email()` - Expect ValidationError
4. `test_register_with_malformed_email()` - Expect ValidationError

**Integration Tests:**
1. POST /register with valid email → 201 Created
2. POST /register with invalid email → 400 Bad Request

**Regression Tests:**
- Run full test suite (`bash atools/run_tests.sh`)
- Verify no existing tests broken

---

## Summary

**Lines Changed:** ~3 lines (1 import, 1 validation, 1 test file)
**Complexity:** LOW (simple integration, reuse existing code)
**Risk:** LOW (minimal change, pattern-following, well-tested validator)
**Time Estimate:** 15-20 minutes implementation + testing

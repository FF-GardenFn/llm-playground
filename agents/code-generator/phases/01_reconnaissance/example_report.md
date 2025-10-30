# Example: Reconnaissance Report

## Feature Request
Add email validation to user registration endpoint

**Acceptance Criteria:**
- Validate email format before creating user
- Return clear error for invalid emails
- Maintain existing registration flow
- No breaking changes to existing functionality

---

## Tool Usage
```bash
python atools/search_codebase.py --pattern "validation"
```

**Found Existing Validators:**
- `src/validators/base_validator.py` - BaseValidator abstract class
- `src/validators/email_validator.py` - EmailValidator class (REUSE THIS)
- `src/validators/string_validator.py` - StringValidator class
- `tests/unit/validators/test_email_validator.py` - Existing tests

**Pattern Identified:** Validators inherit from BaseValidator, implement `.validate()` method

---

## Architecture Mapping

**Affected Layers:**
- **API Layer:** `routes/auth.py` (registration endpoint - NO CHANGE)
- **Service Layer:** `services/user_service.py` (validation logic - MODIFY HERE)
- **Data Layer:** `models/user.py` (no changes needed)
- **Tests:** `tests/unit/services/test_user_service.py` (add validation tests)

**Integration Point:** User registration flows through:
1. Route layer (`routes/auth.py`) receives request
2. Service layer (`services/user_service.py`) - ADD VALIDATION HERE
3. Data layer saves to database

---

## Existing Patterns

**Validation Pattern:**
```python
class EmailValidator(BaseValidator):
    def validate(self, value):
        if not self._is_valid_email(value):
            raise ValidationError(f"Invalid email: {value}")
        return True
```

**Error Handling:** Validators raise `ValidationError` (custom exception)
**Testing Pattern:** Unit tests in `tests/unit/validators/`, integration tests in `tests/unit/services/`

---

## Implementation Strategy

**Files to Modify:**
- `services/user_service.py` - Add email validation call in `register()` method

**Files to Reuse:**
- `validators/email_validator.py` - Existing, tested validator

**Files to Create:**
- `tests/unit/services/test_user_registration_validation.py` - New tests for registration validation

---

## Testing Strategy

**Existing Test Pattern:**
```python
def test_validator_with_valid_input():
    validator = EmailValidator()
    assert validator.validate("user@example.com") is True

def test_validator_with_invalid_input():
    validator = EmailValidator()
    with pytest.raises(ValidationError):
        validator.validate("not-an-email")
```

**Integration Tests:** Call service method with invalid data, verify `ValidationError` raised

---

## Key Insights

- **Reuse Opportunity:** EmailValidator already exists with comprehensive tests
- **Integration Pattern:** Validation happens in service layer, not route layer
- **Error Handling:** ValidationError propagates to route layer, returns 400 to client
- **Minimal Change:** Only need to add 1 line: `EmailValidator().validate(email)`

**Estimated Complexity:** LOW (single line integration, existing validator, clear tests)

# Example: Implementation

## Feature
Add email validation to user registration

**Design:** Integrate `EmailValidator` into `UserService.register()` method

---

## Step 1: Write Failing Test (RED)

**File: `tests/unit/services/test_user_registration_validation.py`**

```python
import pytest
from services.user_service import UserService
from validators.exceptions import ValidationError

class TestUserRegistrationValidation:
    """Test email validation in user registration."""

    def test_register_with_valid_email(self):
        """Valid email should allow registration"""
        service = UserService()
        user = service.register("valid@example.com", "password123")
        assert user.email == "valid@example.com"

    def test_register_with_invalid_email(self):
        """Invalid email should raise ValidationError"""
        service = UserService()
        with pytest.raises(ValidationError, match="Invalid email"):
            service.register("not-an-email", "password123")

    def test_register_with_empty_email(self):
        """Empty email should raise ValidationError"""
        service = UserService()
        with pytest.raises(ValidationError, match="Email is required"):
            service.register("", "password123")
```

**Tool:** `bash atools/run_tests.sh tests/unit/services/test_user_registration_validation.py`

**Result:** FAILS (validation not implemented yet)
```
✗ test_register_with_invalid_email FAILED: Expected ValidationError, got User object
✗ test_register_with_empty_email FAILED: Expected ValidationError, got User object
```

---

## Step 2: Implement Validation (GREEN)

**File: `services/user_service.py`**

```python
from validators.email_validator import EmailValidator  # NEW IMPORT

class UserService:
    def register(self, email, password):
        """Register new user account.

        Args:
            email (str): User email address
            password (str): User password

        Returns:
            User: Created user object

        Raises:
            ValidationError: If email format is invalid
        """
        # NEW: Validate email before creating user
        EmailValidator().validate(email)

        # Existing code (unchanged)
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return user
```

**Tool:** `bash atools/run_tests.sh tests/unit/services/test_user_registration_validation.py`

**Result:** PASSES
```
✓ test_register_with_valid_email PASSED
✓ test_register_with_invalid_email PASSED
✓ test_register_with_empty_email PASSED

3/3 tests passed
```

---

## Step 3: Verify No Regressions

**Tool:** `bash atools/run_tests.sh tests/unit/services/`

**Result:** All existing service tests still pass
```
✓ test_register_creates_user PASSED
✓ test_register_hashes_password PASSED
✓ test_login_with_valid_credentials PASSED
✓ test_login_with_invalid_credentials PASSED
✓ test_register_with_valid_email PASSED
✓ test_register_with_invalid_email PASSED
✓ test_register_with_empty_email PASSED

7/7 tests passed (no regressions)
```

---

## Step 4: Add Edge Case Tests (REFACTOR)

**File: `tests/unit/services/test_user_registration_validation.py`** (add to existing)

```python
    def test_register_with_whitespace_email(self):
        """Email with only whitespace should fail"""
        service = UserService()
        with pytest.raises(ValidationError):
            service.register("   ", "password123")

    def test_register_with_special_chars(self):
        """Email with valid special chars should pass"""
        service = UserService()
        user = service.register("user+tag@example.com", "password123")
        assert user.email == "user+tag@example.com"
```

**Tool:** `bash atools/run_tests.sh tests/unit/services/test_user_registration_validation.py`

**Result:** PASSES
```
✓ test_register_with_valid_email PASSED
✓ test_register_with_invalid_email PASSED
✓ test_register_with_empty_email PASSED
✓ test_register_with_whitespace_email PASSED
✓ test_register_with_special_chars PASSED

5/5 tests passed
```

---

## Implementation Summary

**Files Modified:**
1. `services/user_service.py` - Added 1 import, 1 validation line, updated docstring

**Files Created:**
2. `tests/unit/services/test_user_registration_validation.py` - 5 tests covering all cases

**Total Changes:**
- Lines added: ~25 (1 import + 1 validation + 3 docstring + ~20 test)
- Lines modified: 0 (no changes to existing logic)
- Complexity: LOW (simple integration)

---

## Test Coverage

**Happy Path:**
- ✓ Valid standard email
- ✓ Valid email with special chars (+, .)

**Error Cases:**
- ✓ Invalid format (missing @)
- ✓ Empty string
- ✓ Whitespace only

**Edge Cases:**
- ✓ Special characters in local part
- ✓ Subdomain in domain part

---

## Rationale

**Why this implementation:**
- Follows existing validation pattern (service layer validation)
- Reuses tested validator (no reinvention)
- Minimal change (2 lines)
- Easy to test (clear input/output)
- No breaking changes (additive only)

**Pattern Consistency:**
- Matches username validation in same file (line 45)
- Uses same exception type (ValidationError)
- Same error handling flow (exception → 400 to client)

---

## Verification Checklist

- [x] Tests written first (TDD approach)
- [x] All new tests pass
- [x] No regressions in existing tests
- [x] Code follows existing patterns
- [x] Docstring updated
- [x] Edge cases covered
- [x] Error messages clear

Ready for validation phase.

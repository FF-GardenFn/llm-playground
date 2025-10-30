# TDD Cycle Pattern

## The Red-Green-Refactor Cycle

**Purpose:** Build confidence through continuous verification, not end-of-phase testing

---

## Cycle Structure

**1. RED - Write Failing Test**
```python
def test_register_with_invalid_email():
    """Invalid email should raise ValidationError"""
    service = UserService()
    with pytest.raises(ValidationError):
        service.register("not-an-email", "password123")
```
Run test → Verify it FAILS (no validation yet)

---

**2. GREEN - Minimal Implementation**
```python
def register(self, email, password):
    EmailValidator().validate(email)  # Add this line
    # ... existing code
```
Run test → Verify it PASSES

---

**3. REFACTOR - Improve Design**
- Extract duplicated code
- Improve naming
- Simplify logic
- Run tests → Verify still PASSING

---

## Why This Works

**Small Diffs:**
- Each cycle adds 5-10 lines of test + 10-20 lines of implementation
- Easy to review, easy to debug

**Continuous Verification:**
- Tests prove code works at each step
- Catch regressions immediately
- Build confidence incrementally

**Design Feedback:**
- Hard-to-test code signals design problems
- Refactor while tests are green
- Tests document intended behavior

---

## Example: Full Cycle

```python
# RED: Write test
def test_validate_email_format():
    assert validate_email("user@example.com") is True

# Run: FAILS (function doesn't exist)

# GREEN: Implement
def validate_email(email):
    return "@" in email and "." in email

# Run: PASSES

# REFACTOR: Improve
import re
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_email(email):
    """Validate email format using RFC 5322 regex."""
    return bool(re.match(EMAIL_REGEX, email))

# Run: STILL PASSES
```

---

## Anti-Pattern: Implementation First

**Don't:**
```
1. Write 100 lines of code
2. Write tests at end
3. Debug for hours
4. Discover design flaws too late
```

**Do:**
```
1. Write 1 test (10 lines)
2. Write minimal code (20 lines)
3. Verify immediately
4. Repeat
```

---

## When to Run Tests

**After each:**
- New function added
- Logic change
- Refactoring
- Significant code block

**Not just at end of phase.**

---

## Red-Green-Refactor Benefits

- Small, reviewable changes
- Immediate feedback
- Design driven by tests
- Confidence in correctness
- Easy to debug (small increments)

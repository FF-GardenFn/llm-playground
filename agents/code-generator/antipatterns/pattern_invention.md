# Anti-Pattern: Pattern Invention

## Problem
Reinventing solutions instead of reusing existing patterns. Creates inconsistency, wastes time, and makes codebase harder to understand.

## Example: Wrong Approach

```
User: "Add logging to user service"

Developer creates new logging approach:

class UserService:
    def __init__(self):
        self.log_file = open('user_service.log', 'a')  # New pattern

    def register(self, email, password):
        self.log_file.write(f"[{datetime.now()}] Registering {email}\n")
        # ... registration logic ...
        self.log_file.write(f"[{datetime.now()}] Registered {email}\n")

    def __del__(self):
        self.log_file.close()
```

**Problems:**
- Codebase uses `logging` module everywhere else
- Custom log format (different from rest of codebase)
- File handling (no rotation, no levels, no filtering)
- Inconsistent with existing pattern

**Result:** Code review requests rewrite to match existing pattern

## Correct Approach: Search Before Building

**Step 1: Search for existing pattern**
```bash
python atools/search_codebase.py --pattern "logging"
```

**Finds:**
```python
# services/payment_service.py
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def process_payment(self, amount):
        logger.info(f"Processing payment: ${amount}")
        # ... payment logic ...
        logger.info(f"Payment successful: ${amount}")
```

**Pattern identified:**
- Use standard `logging` module
- Get logger with `__name__`
- Use appropriate level (info, warning, error)
- Clear, contextual messages

**Step 2: Apply existing pattern**
```python
# services/user_service.py
import logging

logger = logging.getLogger(__name__)

class UserService:
    def register(self, email, password):
        logger.info(f"Registering user: {email}")
        # ... registration logic ...
        logger.info(f"User registered successfully: {email}")
```

**Benefits:**
- Consistent with codebase (matches 12 other services)
- Uses existing logging configuration
- Gets log rotation, levels, filters for free
- Other developers immediately understand

## Another Example: Error Handling

### Wrong: Invent New Exception Type

```python
class EmailValidationException(Exception):  # New exception type
    pass

def validate_email(email):
    if '@' not in email:
        raise EmailValidationException("Missing @")  # Different pattern
```

### Correct: Use Existing Pattern

**Search first:**
```bash
python atools/search_codebase.py --pattern "ValidationError\|raise.*Error"
```

**Finds existing pattern:**
```python
# validators/base.py
class ValidationError(Exception):
    """Validation error for all validators."""
    pass

# Used in 8 other validators
```

**Apply:**
```python
from validators.exceptions import ValidationError  # Reuse

def validate_email(email):
    if '@' not in email:
        raise ValidationError("Missing @")  # Consistent
```

## How Structure Prevents This

- Reconnaissance phase requires search for similar code
- phases/01_reconnaissance/outputs.md requires "Existing patterns identified"
- Design phase requires justification for new patterns
- phases/02_design/outputs.md: "Justification: Follows [existing pattern] from [location]"

## Key Lesson

**Consistency > Perfection**

Codebase with 3 mediocre patterns consistently applied is better than codebase with:
- 1 perfect pattern
- 5 invented patterns
- 10 variations

**Rule:** Search first. Invent only when:
1. No existing pattern fits
2. Existing pattern is clearly broken
3. Can justify why new pattern is better
4. Document decision for others

**Time saved:**
- Search: 2 minutes
- Invent + debug + review + fix + document: 2 hours

**Choose wisely.**

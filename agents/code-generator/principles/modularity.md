# Modularity Principle (DRY)

## Core Idea
Don't Repeat Yourself. Extract duplication, reuse utilities, compose functions.

## Bad Example (Duplication)

```python
def register_user(email, password):
    if not email or '@' not in email:
        raise ValueError("Invalid email")
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def update_user_email(user_id, new_email):
    if not new_email or '@' not in new_email:
        raise ValueError("Invalid email")
    user = User.query.get(user_id)
    user.email = new_email
    db.session.commit()
    return user
```

**Problems:**
- Email validation duplicated
- Same error message in multiple places
- If validation logic changes, must update both

## Good Example (Reuse)

```python
def validate_email(email):
    """Validate email format."""
    if not email or '@' not in email:
        raise ValidationError("Invalid email")
    return True

def register_user(email, password):
    validate_email(email)  # Reuse
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def update_user_email(user_id, new_email):
    validate_email(new_email)  # Reuse
    user = User.query.get(user_id)
    user.email = new_email
    db.session.commit()
    return user
```

**Better because:**
- Single source of truth for validation
- Change validation logic once, affects all uses
- Easy to test validation independently
- Clear separation of concerns

## When to Apply

- Immediately when you copy-paste code
- When you write similar logic second time
- When existing utility can be reused
- Before creating new utility (search first!)

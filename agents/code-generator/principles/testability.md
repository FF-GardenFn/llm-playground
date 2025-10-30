# Testability Principle

## Core Idea
Design for testing: clear I/O, pure functions, dependency injection. Never write code that's difficult to test.

## Bad Example (Hard to Test)

```python
def send_welcome_email(user_id):
    """Send welcome email to user."""
    user = User.query.get(user_id)  # Database dependency
    smtp = smtplib.SMTP('smtp.gmail.com', 587)  # External service
    smtp.login('user@example.com', 'password')  # Hardcoded credentials
    message = f"Welcome {user.name}!"  # String building inside
    smtp.sendmail('from@example.com', user.email, message)
    smtp.quit()
    return True
```

**Problems:**
- Requires database (hard to test)
- Requires SMTP server (external dependency)
- Hardcoded credentials (can't test without real creds)
- Side effects (actually sends email in test)
- Hard to verify without checking email server

## Good Example (Testable)

```python
def format_welcome_message(user_name):
    """Format welcome email message."""
    return f"Welcome {user_name}!"

def send_email(to_email, message, email_service):
    """Send email using provided service."""
    return email_service.send(to_email, message)

def send_welcome_email(user, email_service):
    """Send welcome email to user.

    Args:
        user: User object with name and email
        email_service: Email service instance (injectable)

    Returns:
        bool: True if sent successfully
    """
    message = format_welcome_message(user.name)
    return send_email(user.email, message, email_service)
```

**Test:**
```python
def test_send_welcome_email():
    # Arrange
    user = Mock(name="Alice", email="alice@example.com")
    email_service = Mock()
    email_service.send.return_value = True

    # Act
    result = send_welcome_email(user, email_service)

    # Assert
    assert result is True
    email_service.send.assert_called_once_with(
        "alice@example.com",
        "Welcome Alice!"
    )
```

**Better because:**
- No database required (user injected)
- No SMTP required (service injected)
- Easy to mock dependencies
- Pure function for message formatting
- Clear inputs and outputs
- Side effects isolated and testable

## When to Apply

- From the start (design for testing)
- When adding new functions (can I test this?)
- When refactoring (make it more testable)
- When tests become complex (simplify code, not test)

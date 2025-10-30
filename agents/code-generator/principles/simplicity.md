# Simplicity Principle

## Core Idea
Simple solutions over clever ones. If you can't explain it simply, redesign it.

## Bad Example (Complex)

```python
def process(data):
    return [x for x in (y.strip() for y in data.split(',') if y) if x.isdigit()]
```

**Problems:**
- Nested comprehensions
- Unclear purpose from function name
- Hard to test each step independently
- Clever but confusing

## Good Example (Simple)

```python
def extract_numeric_values(csv_string):
    """Extract numeric strings from comma-separated input."""
    values = csv_string.split(',')
    cleaned = [v.strip() for v in values if v.strip()]
    return [v for v in cleaned if v.isdigit()]
```

**Better because:**
- Clear function name describes purpose
- Separated concerns (split, clean, filter)
- Each step testable independently
- Easy to modify or extend

## When to Apply

- Always default to simple approach
- Add complexity only when proven necessary
- Refactor complex code immediately when spotted
- Junior engineer should understand it in 6 months

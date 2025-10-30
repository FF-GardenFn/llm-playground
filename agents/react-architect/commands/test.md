---
description: Load testing patterns (React Testing Library, integration tests, accessibility tests)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: []
---

## Test Command

**Usage**: `/test`

**Loads**: React Testing Library patterns, integration tests, accessibility tests

## Testing Strategy

**Test Types**:
1. **Unit Tests**: Test components in isolation
2. **Integration Tests**: Test component interactions
3. **Edge Case Tests**: Test error, loading, empty states
4. **Accessibility Tests**: Test keyboard, screen reader, ARIA

## Files to Load

{{load: ${CLAUDE_PLUGIN_ROOT}/testing/react-testing-library.md}}

## Gate

**Cannot proceed to deployment without**:
- [ ] Unit tests documented (renders, interactions)
- [ ] Integration tests documented (component interactions)
- [ ] Edge case tests documented (empty, error, loading)
- [ ] Accessibility tests documented (keyboard, ARIA, screen reader)
- [ ] Test coverage target defined (>80%)

## Example

```
User: /test
Agent: Loads testing/react-testing-library.md and helps write tests
```

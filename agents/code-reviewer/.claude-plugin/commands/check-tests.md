---
description: Testing-focused review (coverage, quality, pyramid)
allowed-tools: Read, Write, AskUserQuestion
argument-hint: [paths... | --coverage]
---

# Testing-Focused Code Review

Testing-focused review assessing test coverage, quality, and pyramid compliance. Identifies testing gaps and validates FIRST principles adherence.

## Testing Strategy Assessment

Complete testing workflow:
→ Load {{load: ../workflows/review-process.md#testing}}

---

## 1. Testing Pyramid Assessment

When test distribution analysis needed:
  → Load {{load: ../testing/test-pyramid.md}}

**Ideal**: 60-70% unit, 20-30% integration, 5-10% E2E
**Check for**: Inverted pyramid, missing layers

---

## 2. Test Coverage Assessment

When coverage analysis needed:
  → Load {{load: ../testing/coverage.md}}

**Targets**: Critical 100%, Core 90%+, Utility 80%+, UI 70%+
**Identify**: Critical gaps (must fix), important gaps (should fix)

---

## 3. Test Quality Assessment

When FIRST principles validation needed:
  → Load {{load: ../testing/test-quality.md}}

**FIRST**: Fast, Independent, Repeatable, Self-validating, Timely
**Check**: Speed, isolation, determinism, clarity, timeliness

---

## 4. Mocking Assessment

When mocking strategy evaluation needed:
  → Load {{load: ../testing/mocking.md}}

**Mock**: External dependencies (APIs, databases, network)
**Don't Mock**: Business logic, value objects, simple objects

---

## 5. Test Smells Detection

When test code quality issues detected:
  → Load {{load: ../testing/test-smells.md}}

**Common smells**: Test too large (>20 lines), unclear names, assertion roulette, brittle tests

---

## Output Format

Use format from {{load: ../feedback/format.md}} with testing-specific sections:
- Testing pyramid status
- Coverage assessment (by category)
- Test quality (FIRST score)
- Mocking strategy evaluation
- Test smells detected
- Recommendations (Critical/Important/Suggestions)

---

## Guidelines

1. **Be Specific**: Provide file paths, line numbers, test names
2. **Show Examples**: Include test code snippets (current vs recommended)
3. **Prioritize**: Critical (no tests) → Important (poor coverage) → Suggestions (minor improvements)
4. **Balance**: Acknowledge good test practices found

---

## Start Testing Review

Ask user: "What code would you like me to review for testing quality? Please provide file paths or paste test code."

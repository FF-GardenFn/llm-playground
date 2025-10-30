# Anti-Pattern: Large Diffs

## Problem
Making changes too large to review safely. Large diffs hide bugs, make rollback hard, and overwhelm reviewers.

## Example: Wrong Approach

```
Single commit with 500+ lines changed:
- Refactor user service (200 lines)
- Add email validation (50 lines)
- Update tests (100 lines)
- Fix unrelated bug (30 lines)
- Rename variables (120 lines)
```

**Problems:**
- Reviewer can't understand what changed
- Bug hiding in refactoring
- Rollback removes email validation AND bug fix
- Test failures hard to diagnose (which change broke it?)

**Result:** Code review takes 2 hours, finds 3 bugs, requests split

## Correct Approach

**Break into small, reviewable commits:**

```
Commit 1: Add email validation (2 lines + 15 test lines)
- services/user_service.py: +1 import, +1 validation call
- tests/test_user_service.py: +15 lines
→ Tests pass, easy to review

Commit 2: Fix bug in password hashing (5 lines)
- services/user_service.py: Fix salt generation
- tests/test_user_service.py: Add test for bug
→ Tests pass, bug proven fixed

Commit 3: Refactor user service (50 lines)
- Extract helper methods
- Reduce complexity 12 → 6
- Tests unchanged (behavior preserved)
→ Tests pass, complexity improved
```

**Result:** Each commit reviewable in 5 minutes, bugs caught immediately, safe rollback

## How TDD Naturally Creates Small Diffs

**TDD Cycle:**
```
1. Write 1 test (10 lines) → RED
2. Write minimal code (15 lines) → GREEN
3. Refactor if needed (modify 10 lines) → GREEN
4. Repeat
```

**Each cycle = 25-35 lines changed**

10 cycles = 250-350 lines, but:
- Each cycle verifiable independently
- Each cycle reviewable
- Each cycle rollbackable
- Tests document each change

## How Structure Prevents This

- Implementation phase uses TDD cycle
- phases/03_implementation/tdd_cycle.md shows pattern
- Each cycle produces small diff
- Cannot skip to "big bang" implementation

## Key Lesson

**Small, incremental changes are:**
- Safer (bugs caught immediately)
- Reviewable (humans can understand)
- Rollbackable (undo specific change)
- Debuggable (know which change broke what)

**Rule:** If diff > 200 lines, ask "Can I split this?"

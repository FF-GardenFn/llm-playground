---
description: Perform comprehensive code review across structure, correctness, security, performance, and maintainability
allowed-tools: Read, Write, AskUserQuestion
argument-hint: [paths...]
---

# Code Review Command

Systematic production code review through 5-phase workflow (Automated Analysis → Manual Review → Feedback Synthesis → Priority Assessment → Recommendations).

## Operational Mode: Standalone

Complete 5-phase workflow:
  → Load {{load: ../workflows/review-process.md}}

**Phases**:
1. Automated Analysis → security/, quality/, performance/
2. Manual Review → architecture/, testing/
3. Feedback Synthesis → feedback/
4. Priority Assessment → priorities/
5. Recommendations → actionable feedback + refactoring offer

Each phase loads relevant guides on-demand based on detected issues.

---

## Output Format

Standard format:
  → Load {{load: ../feedback/format.md}}

**Structure**:
- Executive Summary (overall quality, issue counts)
- Critical Issues (fix immediately)
- Important Issues (fix soon)
- Suggestions (nice to have)
- Refactorable Code Smells (optional automation)
- Positive Highlights (what went well)
- Next Steps (action plan)

---

## Refactoring Offer

If refactorable smells detected:
  → Load {{load: ../priorities/refactorable-smells.md}}

**Ask user**: "Would you like me to invoke refactoring-engineer to perform these refactorings automatically?"

**Integration protocol**:
  → Load {{load: ../integration/refactoring-trigger.md}}

---

## Guidelines

1. **Be Constructive**: Use patterns from {{load: ../feedback/constructive-criticism.md}}
2. **Be Specific**: Provide file paths and line numbers
3. **Show Examples**: Include code examples (current vs recommended)
4. **Balance Feedback**: Include positive highlights from {{load: ../priorities/praise.md}}
5. **Prioritize**: Critical → Important → Suggestions

---

## Review Categories

**Load category on-demand based on detected issues**:

### Security Focus
When security issues detected:
  → Load {{load: ../security/owasp-checklist.md}}

**Check**: SQL injection, XSS, auth/authorization, input validation, OWASP Top 10

### Performance Focus
When performance issues detected:
  → Load {{load: ../performance/database-performance.md}}

**Check**: N+1 queries, inefficient algorithms (O(n²)), memory leaks, blocking I/O

### Testing Focus
When testing issues detected:
  → Load {{load: ../testing/test-types.md}}

**Check**: Coverage (target 80%+, critical 100%), testing pyramid (60-70% unit), FIRST principles

### Architecture Focus
When architecture issues detected:
  → Load {{load: ../architecture/component-boundaries.md}}

**Check**: Component boundaries, API design, error handling, separation of concerns

### Quality Focus
When code quality issues detected:
  → Load {{load: ../quality/clean-code.md}}

**Check**: SOLID principles, clean code, code smells, maintainability

---

## Start Review

Ask user: "What code would you like me to review? Please provide file paths or paste the code."

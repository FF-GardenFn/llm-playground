# Clarifying Questions Patterns

## Purpose

Generate targeted questions to resolve ambiguities and uncover hidden requirements before work begins.

---

## Question Generation Framework

### The 5W2H Method

**What**:
- What exactly needs to be built/changed?
- What constitutes success?
- What are the acceptance criteria?
- What should NOT be included?

**Why**:
- Why is this needed now?
- Why this approach over alternatives?
- Why these specific requirements?

**Who**:
- Who are the end users?
- Who are the stakeholders?
- Who approves the final result?
- Who maintains it afterward?

**Where**:
- Where will this be deployed?
- Where does data come from/go to?
- Where are the system boundaries?

**When**:
- When is the deadline?
- When do components need to be ready?
- When are dependencies available?

**How**:
- How should it behave under edge cases?
- How will success be measured?
- How does it integrate with existing systems?

**How Much**:
- How much load/scale is expected?
- How much error tolerance is acceptable?
- How much technical debt is acceptable?

---

## Ambiguity Detection Triggers

### Vague Language Patterns

When you encounter these, generate clarifying questions:

**Imprecise Adjectives**:
- "Fast" → How many milliseconds/seconds?
- "User-friendly" → Specific UX requirements?
- "Scalable" → What scale? Linear/exponential?
- "Secure" → Which security standards?
- "Modern" → Which specific technologies?

**Assumed Context**:
- "The usual way" → Document specific approach
- "Standard process" → Which standard exactly?
- "Like before" → Which previous implementation?
- "Obviously" → Make it explicit

**Incomplete Specifications**:
- "Handle errors" → Which errors? How?
- "Validate input" → What validation rules?
- "Optimize performance" → Which metrics? Target values?

---

## Question Templates by Category

### Functional Requirements

```markdown
1. Can you provide concrete examples of [feature] in use?
2. What happens when [edge case]?
3. Should [behavior A] or [behavior B] occur when [condition]?
4. Is [assumption] correct?
5. What are the exact validation rules for [input]?
```

### Non-Functional Requirements

```markdown
1. What response time is acceptable for [operation]?
2. How many concurrent [users/operations] must be supported?
3. What availability percentage is required (99.9%, 99.99%)?
4. Which browsers/devices must be supported?
5. What are the security compliance requirements?
```

### Integration & Dependencies

```markdown
1. Which external systems does this integrate with?
2. What are the API rate limits we must respect?
3. What format does [system] expect for [data]?
4. Are there breaking changes to consider?
5. What's the fallback if [dependency] is unavailable?
```

### Success Criteria

```markdown
1. How will we know this is successful?
2. What metrics define success?
3. What would constitute failure?
4. Are there partial success scenarios?
5. Who validates that requirements are met?
```

---

## Priority-Based Question Organization

### Critical (Must ask before proceeding)

Questions that block decomposition:
- Success criteria definition
- Core functionality scope
- Critical constraints
- Security requirements

### Important (Should ask for quality)

Questions that affect approach:
- Performance expectations
- User experience details
- Error handling strategies
- Integration patterns

### Helpful (Nice to know)

Questions that refine implementation:
- Optimization preferences
- Future extensibility
- Documentation depth
- Testing coverage

---

## Context-Aware Question Generation

### For New Features

```markdown
□ What problem does this solve?
□ Who experiences this problem?
□ How do they currently work around it?
□ What's the minimum viable solution?
□ What would delight users beyond expectations?
```

### For Bug Fixes

```markdown
□ What's the expected behavior?
□ When did this start occurring?
□ What changed recently?
□ How critical is this fix?
□ Are there workarounds users can employ?
```

### For Optimizations

```markdown
□ What metrics are we optimizing?
□ What's the current baseline?
□ What's the target improvement?
□ What trade-offs are acceptable?
□ How will we measure success?
```

### For Refactoring

```markdown
□ What problems does current code have?
□ What benefits will refactoring provide?
□ What's the risk of regression?
□ How will we validate no behavior changed?
□ Is this blocking other work?
```

---

## Question Presentation Strategy

### Batch Related Questions

```markdown
## Regarding Authentication:
1. Should we support social login?
2. Is 2FA required?
3. How long should sessions last?
4. Should we support "remember me"?
```

### Provide Context for Questions

```markdown
## Question: Should the API rate limit be per-user or per-API-key?

Context: This affects how we track usage. Per-user is simpler but less
flexible. Per-API-key allows users multiple applications but is more complex.

Impact: Architecture decision that's hard to change later.
```

### Suggest Options When Appropriate

```markdown
## How should we handle concurrent edits?

Options:
a) Last-write-wins (simple, may lose data)
b) Optimistic locking (prevents conflicts, may frustrate users)
c) Operational transformation (complex, best UX)
d) Lock-based (simple, may block users)

Recommendation: Option B for balance of simplicity and safety
```

---

## Response Processing

### Extracting Actionable Requirements

From vague response:
> "Make it work like Google"

Extract specific requirements:
- Autocomplete with <200ms response
- Search as you type
- Spelling correction
- Relevance ranking
- Response time <1 second

### Identifying Follow-Up Questions

From incomplete response:
> "Yes, handle errors gracefully"

Generate follow-ups:
- Which errors should be retried?
- Should users see technical details?
- Where should errors be logged?
- Should we notify administrators?

---

## Communication Best Practices

### DO:
- Ask specific, answerable questions
- Provide context for why you're asking
- Group related questions
- Suggest options when applicable
- Indicate priority of questions

### DON'T:
- Ask yes/no when you need details
- Assume shared context
- Ask too many questions at once
- Use technical jargon unnecessarily
- Ask questions you can answer yourself

---

## Question Tracking Template

```markdown
## Clarifying Questions Log

### Asked on [Date]
| # | Question | Priority | Status | Response | Follow-up Needed |
|---|----------|----------|--------|----------|------------------|
| 1 | [Question] | Critical | Answered | [Summary] | No |
| 2 | [Question] | Important | Pending | - | - |
| 3 | [Question] | Helpful | Answered | [Summary] | Yes - [Detail] |

### Requirements Extracted
- [Requirement from Q1]
- [Requirement from Q3]

### Still Unclear
- [Ambiguity requiring follow-up]
```

---

*Good questions prevent bad implementations. A Senior Engineering Manager knows what to ask.*
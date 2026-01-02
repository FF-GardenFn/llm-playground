# Phase 3: Adaptive Clarification

**Purpose**: Gather user requirements with expertise-adaptive questioning.

---

## Overview

Clarification ensures we understand exactly what the user needs before generating content. This phase adapts question depth and style based on detected user expertise.

---

## Process Steps

### Step 1: Expertise Detection
```
User request → Analyze vocabulary, structure, sophistication → Expertise level
```

Expertise levels:
- **Novice**: Broad requests, unfamiliar terminology
- **Intermediate**: Some terminology, general goals
- **Advanced**: Specific concepts, clear preferences
- **Expert**: Precise terminology, detailed specifications

### Step 2: Gap Analysis
```
Request + Concepts → Identify what's missing → Generate questions
```

Check for:
- WHO: Target audience unclear
- WHAT: Output format unspecified
- WHY: Learning objectives missing
- HOW MUCH: Scope undefined

### Step 3: Question Generation
```
Missing info + Expertise level → Adaptive questions
```

Adjust for expertise:
- Novice: More guidance, structured options
- Expert: Minimal questions, confirm only

### Step 4: Scope Bounding
```
User answers → Confirm bounded scope → Requirements document
```

Ensure:
- Feasible within content
- Clear success criteria
- Defined output format
- Realistic expectations

---

## Inputs

| Input | Type | Required |
|-------|------|----------|
| user_request | String | Yes |
| concepts.json | JSON | Yes |
| user_history | JSON | Optional |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| requirements.md | Markdown | Clear, unambiguous requirements |
| user_profile.json | JSON | Expertise level, preferences |
| scope_definition.md | Markdown | What's in/out of scope |

### requirements.md Structure
```markdown
# Requirements Summary

## User Profile
- Expertise Level: Intermediate
- Target Audience: P2 pharmacy students
- Context: Midterm exam preparation

## Requested Outputs
- Flashcards: 50
- Quiz Questions: 20 MCQ
- Format: Digital (Anki-compatible)

## Learning Objectives
- Understand drug mechanisms (Bloom's: Understand)
- Apply dosing calculations (Bloom's: Apply)

## Scope
### In Scope
- Pharmacokinetics chapter (absorption, distribution)
- Drug classes: ACE-I, ARBs, Beta-blockers

### Out of Scope
- Pharmacodynamics (separate request)
- Clinical case studies

## Success Criteria
- All major concepts from chapter covered
- Bloom's distribution: 40% Remember, 40% Understand, 20% Apply
- Ready to import to Anki
```

---

## Gate: GATE-REQUIREMENTS-CLEAR.md

### Entry Criteria
- [ ] User request received
- [ ] Concept extraction complete (Phase 2)

### Exit Criteria
- [ ] Target audience identified
- [ ] Output format specified
- [ ] Learning objectives clear
- [ ] Scope bounded and feasible
- [ ] Success criteria defined
- [ ] No ambiguous requirements

### Blocking Conditions
- User hasn't responded to critical questions
- Conflicting requirements unresolved
- Scope exceeds available content
- Output format not supported

---

## 5W2H Framework

### WHO - Target Audience
"Who will use these materials?"
- Pharmacy students (year?)
- Practitioners (specialty?)
- Self-study or classroom?

### WHAT - Desired Outputs
"What type of materials do you need?"
- Flashcards
- Quizzes
- Study guides
- Case studies
- Mix

### WHEN - Timeline
"When do you need this / what's the context?"
- Immediate exam prep
- Semester-long study
- Board preparation

### WHERE - Usage Context
"How will these be used?"
- Self-study
- Classroom
- Clinical rotations
- Online platform

### WHY - Learning Objectives
"What should learners be able to do?"
- Memorize facts (Remember)
- Explain concepts (Understand)
- Apply to problems (Apply)
- Analyze cases (Analyze)

### HOW - Format Preferences
"What format works best?"
- Digital / Printable
- Anki-compatible
- Markdown / PDF

### HOW MUCH - Scope
"How much content do you need?"
- Number of items
- Topic breadth
- Depth of coverage

---

## Expertise-Adaptive Questions

### For Novice Users
```
I'd like to help you study effectively. Let me ask a few questions:

1. What specific exam or course is this for?
2. Which topics do you need to focus on?
3. Do you prefer flashcards, practice questions, or both?
4. How much time do you have before your exam?
```

### For Expert Users
```
I'll create [topic] materials as specified. Quick confirmations:
- Should I include clinical vignettes with questions?
- Any specific drug pairs you want emphasized?
```

---

## Question Templates

### Scope Clarification
```
"I see you want [topic]. Should I cover:
A) Just the core concepts (faster, focused)
B) Comprehensive coverage (thorough, takes longer)
C) Specific subtopics - please specify"
```

### Format Clarification
```
"For your [flashcards/quiz], would you prefer:
A) Digital (Anki-compatible JSON)
B) Printable (PDF/Markdown)
C) Both formats"
```

### Depth Clarification
```
"Should the focus be on:
A) Basic facts and definitions (memorization)
B) Understanding mechanisms and concepts
C) Clinical application and problem-solving
D) Mix of all levels"
```

---

## Error Prevention

### Avoid Scope Creep
- Confirm boundaries explicitly
- Document what's excluded
- Get agreement before proceeding

### Resolve Conflicts
- If requirements conflict, ask for priority
- Don't assume which requirement wins
- Document resolution

### Verify Feasibility
- Check if content supports request
- Flag if scope exceeds material
- Propose alternatives if needed

---

## Quality Metrics

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Clarity score | 100% | Ask more questions |
| Scope bounded | Yes | Confirm boundaries |
| Objectives defined | Yes | Clarify purpose |
| Conflicts resolved | All | Address each one |

---

## Next Phase

→ **Phase 4: Subagent Delegation**

Requires: Clear requirements with bounded scope

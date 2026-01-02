---
name: exam
description: Create a complete practice exam with answer key
arguments:
  - name: content
    description: Content or topic for the exam
    required: false
  - name: questions
    description: Total number of questions (default: 50)
    required: false
  - name: time
    description: Time limit in minutes (default: 60)
    required: false
---

# Generate Practice Exam

Create a complete, timed practice exam with scoring rubric.

## What This Command Does

1. **Build exam blueprint** with topic coverage
2. **Generate questions** across difficulty levels
3. **Create answer key** with explanations
4. **Include timing** and scoring guidelines

## Quick Examples

```
/exam                                  # Interactive exam builder
/exam pharmacology 75 90               # 75 questions, 90 minutes
/exam "cardiovascular drugs" 50        # 50-question CV exam
/exam midterm                          # Exam named "midterm"
```

## Your Task

When invoked, follow this workflow:

### Step 1: Exam Parameters
Gather requirements:
- Topic/content scope
- Number of questions (default: 50)
- Time limit (default: 60 min)
- Question types (MCQ, T/F, calculations)
- Difficulty distribution

### Step 2: Create Blueprint

```markdown
# Exam Blueprint

## Exam Details
- **Title**: [Exam Name]
- **Questions**: [count]
- **Time**: [minutes] minutes
- **Passing Score**: [X]%

## Topic Coverage
| Topic | Questions | Percentage |
|-------|-----------|------------|
| [Topic 1] | [X] | [X]% |
| [Topic 2] | [X] | [X]% |

## Difficulty Distribution
| Bloom's Level | Questions | Percentage |
|---------------|-----------|------------|
| Remember | [X] | [X]% |
| Understand | [X] | [X]% |
| Apply | [X] | [X]% |
| Analyze | [X] | [X]% |
```

### Step 3: Generate Exam

```markdown
# Practice Exam: [Title]

**Time Limit**: [X] minutes
**Total Questions**: [X]
**Instructions**: Select the best answer for each question.

---

## Questions

**1.** [Question stem]
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]

**2.** [Question stem]
...

---

## Answer Key

| # | Answer | Topic | Bloom's |
|---|--------|-------|---------|
| 1 | B | [Topic] | Apply |
| 2 | C | [Topic] | Understand |

---

## Detailed Explanations

**Question 1**: The correct answer is **B** because...
[Detailed explanation]

**Question 2**: The correct answer is **C** because...
[Detailed explanation]
```

### Step 4: Scoring Guide

```markdown
## Scoring

### Raw Score
- Total Correct: ___ / [total]
- Percentage: ____%

### Performance by Topic
| Topic | Correct | Total | Percentage |
|-------|---------|-------|------------|
| [Topic 1] | ___ | [X] | ___% |

### Performance by Difficulty
| Level | Correct | Total | Percentage |
|-------|---------|-------|------------|
| Remember | ___ | [X] | ___% |
| Understand | ___ | [X] | ___% |
| Apply | ___ | [X] | ___% |

### Interpretation
- 90-100%: Excellent - Ready for assessment
- 80-89%: Good - Minor review needed
- 70-79%: Satisfactory - Focus on weak areas
- <70%: Needs improvement - Comprehensive review recommended

### Recommended Review
Based on your performance, focus on:
1. [Weak area 1]
2. [Weak area 2]
```

## Exam Types

### Midterm Style
- 50-75 questions
- 60-90 minutes
- Balanced difficulty
- Core concepts focus

### Final Exam Style
- 100-150 questions
- 2-3 hours
- Comprehensive coverage
- Higher-order thinking emphasis

### Board Prep Style (NAPLEX)
- 100+ questions
- Timed sections
- Heavy application focus
- Clinical scenarios
- Calculation problems

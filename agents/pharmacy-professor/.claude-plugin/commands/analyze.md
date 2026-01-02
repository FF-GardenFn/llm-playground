---
name: analyze
description: Analyze pharmaceutical content for educational opportunities
arguments:
  - name: content
    description: Content to analyze (file, text, or topic)
    required: true
---

# Analyze Pharmaceutical Content

Analyze content to identify educational opportunities and suggest study materials.

## What This Command Does

1. **Scan content** for pharmaceutical concepts
2. **Identify** high-yield topics for study
3. **Assess** complexity and coverage
4. **Recommend** appropriate study materials

## Quick Examples

```
/analyze lecture.pdf                   # Analyze PDF content
/analyze "What topics are in chapter 5?"
/analyze pharmacokinetics              # Analyze topic coverage
```

## Your Task

When invoked:

### Step 1: Process Content
- If file → ingest and extract concepts
- If topic → analyze scope and subtopics
- If question → provide educational analysis

### Step 2: Generate Analysis Report

```markdown
# Content Analysis

## Overview
- **Source**: [content identifier]
- **Main Topic**: [primary topic]
- **Subtopics**: [count] identified
- **Complexity**: [simple/moderate/complex]

## Key Concepts Found
| Concept | Category | Importance | Coverage |
|---------|----------|------------|----------|
| [name] | [cat] | High/Med/Low | Complete/Partial |

## High-Yield Topics
These concepts are most important for assessment:
1. [Topic] - [reason]
2. [Topic] - [reason]

## Knowledge Gaps
Areas that may need supplementation:
- [Gap 1]
- [Gap 2]

## Recommended Study Materials

### For This Content:
- [ ] Flashcards: ~[X] cards recommended
- [ ] Quiz: ~[X] questions recommended
- [ ] Study Guide: [format] recommended

### Suggested Commands:
- `/flashcards [topic] [count]`
- `/quiz [topic] [count]`
- `/study-guide [topic]`

## Difficulty Distribution
- Remember: [X]%
- Understand: [X]%
- Apply: [X]%
- Analyze: [X]%
```

### Step 3: Provide Actionable Recommendations
- Which topics to focus on
- What study materials to create
- How to approach the content
- Time estimates for study

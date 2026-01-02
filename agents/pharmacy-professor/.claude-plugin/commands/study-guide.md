---
name: study-guide
description: Create structured study guides from pharmaceutical content
arguments:
  - name: content
    description: The content to summarize (file path, text, or topic)
    required: false
  - name: format
    description: outline, detailed, or quick-reference (default: outline)
    required: false
---

# Generate Study Guide

Create structured study guides from pharmaceutical educational content.

## What This Command Does

1. **Extract key concepts** from content
2. **Organize hierarchically** by topic and subtopic
3. **Highlight** important facts, clinical pearls, and common pitfalls
4. **Format** for efficient studying

## Quick Examples

```
/study-guide                           # Interactive mode
/study-guide pharmacokinetics          # PK study guide
/study-guide lecture.pdf detailed      # Detailed guide from PDF
/study-guide "ACE inhibitors" quick-reference
```

## Your Task

When invoked, follow this workflow:

### Step 1: Content Source
If content provided → Process and extract
If no content → Ask what topic/content to summarize

### Step 2: Format Selection
- **Outline**: Hierarchical bullet points, key facts only
- **Detailed**: Full explanations with examples
- **Quick-reference**: Tables and charts for rapid review

### Step 3: Generate Guide

**Outline Format**:
```markdown
# Topic: [Main Topic]

## 1. [Subtopic]
- Key point 1
- Key point 2
  - Detail a
  - Detail b
- Clinical pearl: [insight]

## 2. [Subtopic]
...
```

**Detailed Format**:
```markdown
# Topic: [Main Topic]

## 1. [Subtopic]

### Overview
[Paragraph explanation]

### Key Concepts
1. **[Concept]**: [explanation]
2. **[Concept]**: [explanation]

### Clinical Application
[How this applies to practice]

### Common Mistakes
- [Pitfall to avoid]
```

**Quick-Reference Format**:
```markdown
# Quick Reference: [Topic]

## Drug Comparison Table
| Drug | Class | MOA | Indication | Key AE |
|------|-------|-----|------------|--------|
| ... | ... | ... | ... | ... |

## Key Formulas
- CrCl = (140-age) × weight / (72 × SCr)
- Loading Dose = Vd × Cp

## Must-Know Facts
□ Fact 1
□ Fact 2
□ Fact 3
```

### Step 4: Add Study Elements
- **Mnemonics** where helpful
- **High-yield facts** for exams
- **Practice questions** at end
- **Self-assessment checklist**

## Output Structure

```markdown
# Study Guide: [Topic]

## Learning Objectives
By the end of this review, you should be able to:
1. [Objective 1]
2. [Objective 2]

## Overview
[Brief introduction to topic]

---

## Section 1: [Subtopic]

### Key Concepts
- [Concept with explanation]

### Clinical Pearls
💡 [Important clinical insight]

### Watch Out For
⚠️ [Common mistake or pitfall]

---

## Section 2: [Subtopic]
...

---

## Quick Reference Tables

### [Comparison Table]
| ... | ... | ... |

---

## Self-Assessment

### Review Questions
1. [Question]
2. [Question]

### Checklist
□ I can explain [concept]
□ I can calculate [formula]
□ I understand the difference between [A] and [B]

---

## Key Takeaways
1. [Most important point]
2. [Second most important]
3. [Third most important]
```

## Topic-Specific Templates

### Pharmacokinetics Guide
- ADME overview
- Key parameters (t½, Vd, Cl, F)
- Dosing calculations
- Renal/hepatic adjustments

### Drug Class Guide
- Mechanism of action
- Drugs in class
- Indications
- Adverse effects
- Drug interactions
- Monitoring parameters

### Therapeutics Guide
- Disease overview
- Treatment algorithm
- Drug selection
- Dosing recommendations
- Monitoring
- Patient counseling points

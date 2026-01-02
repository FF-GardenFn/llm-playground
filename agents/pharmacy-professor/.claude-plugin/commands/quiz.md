---
name: quiz
description: Generate quiz questions from pharmaceutical content
arguments:
  - name: content
    description: The content to generate questions from (file path, text, or topic)
    required: false
  - name: count
    description: Number of questions to generate (default: 20)
    required: false
  - name: type
    description: Question type - mcq, tf, matching, or mixed (default: mcq)
    required: false
---

# Generate Pharmacy Quiz

Create quiz questions from pharmaceutical educational content.

## What This Command Does

1. **If content provided**: Process the content, extract concepts, generate questions
2. **If no content**: Ask what topic/content to use
3. **Generate questions** with configurable:
   - Count (default: 20)
   - Type (MCQ, True/False, Matching)
   - Difficulty distribution (Bloom's taxonomy)
   - Clinical vignettes (optional)
   - Answer explanations

## Quick Examples

```
/quiz                           # Interactive - asks for content
/quiz pharmacokinetics 30       # 30 questions on PK topic
/quiz lecture.pdf mcq 25        # 25 MCQs from PDF
/quiz "drug interactions" mixed # Mixed question types
```

## Your Task

When invoked, follow this workflow:

### Step 1: Content Check
If content argument provided:
- Check if it's a file path → Load and process file
- Check if it's a topic → Use concepts from that topic area
- Check if it's inline text → Process directly

If no content:
- Ask: "What content should I create quiz questions from? (file path, topic, or paste text)"

### Step 2: Clarify Requirements
Quick questions based on expertise detection:
- How many questions? (suggest: 20 for practice, 50 for comprehensive)
- Question types? (MCQ recommended for most cases)
- Include clinical vignettes? (yes for application-level)
- Include explanations? (yes for learning, no for timed practice)

### Step 3: Generate Questions
Use quiz generation patterns:
- Extract key concepts from content
- Generate questions at appropriate Bloom's levels
- Create plausible distractors for MCQs
- Add clinical context where appropriate
- Include detailed explanations

### Step 4: Output
Provide in requested format:
- JSON (for import to quiz systems)
- Markdown (for review/printing)
- Text (simple format)

## Bloom's Level Distribution (Default)

| Level | Percentage | Description |
|-------|------------|-------------|
| Remember | 20% | Define, list, name |
| Understand | 35% | Explain, describe, compare |
| Apply | 30% | Calculate, demonstrate, use |
| Analyze | 15% | Differentiate, examine |

## Output Example

```markdown
## Quiz: Drug Absorption

**Q1.** [Understand] Which of the following best describes bioavailability?
A. Rate of drug metabolism
B. Fraction reaching systemic circulation ✓
C. Volume of drug distribution
D. Rate of drug excretion

*Explanation: Bioavailability (F) is the fraction of administered dose
that reaches systemic circulation unchanged...*

**Q2.** [Apply] A patient takes nitroglycerin sublingually rather than
orally. This route is preferred because it:
A. Tastes better
B. Avoids first-pass metabolism ✓
C. Has longer duration
D. Is less expensive
```

## Guardrails Applied
- No invented drug information
- All facts traced to source content
- Educational purpose only

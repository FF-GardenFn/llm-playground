# Guardrail 02: Citations Required

**Priority**: HIGH

**Principle**: Every fact must trace to source content. Maintain provenance chain.

---

## Core Rules

### 1. Source Attribution
- Every factual claim must reference source material
- Page/section numbers when available
- Chunk IDs for processed content
- No orphan facts

### 2. Content Boundaries
- Only use information from provided content
- Don't introduce external facts
- Acknowledge when source is incomplete
- Mark assumptions explicitly

### 3. Citation Format
- Include source reference with each fact
- Use consistent citation style
- Enable verification by user
- Track provenance through pipeline

---

## Citation Requirements by Content Type

### Quiz Questions
```json
{
  "question": "What is the mechanism of metformin?",
  "correct_answer": "Inhibits hepatic gluconeogenesis",
  "source": {
    "document": "Pharmacology Lecture 5",
    "page": 12,
    "chunk_id": "ABC123"
  }
}
```

### Flashcards
```json
{
  "front": "Primary indication for lisinopril?",
  "back": "Hypertension, heart failure, diabetic nephropathy",
  "source": "Chapter 8, Section 8.2.1"
}
```

### Study Guide Content
```markdown
## ACE Inhibitors

Mechanism: Block conversion of angiotensin I to angiotensin II
*[Source: Lecture Notes, p. 45]*

Clinical Uses:
- Hypertension *[Source: Lecture Notes, p. 46]*
- Heart failure with reduced ejection fraction *[Source: Guidelines PDF, p. 12]*
```

---

## Provenance Chain

```
Original Content (PDF/Lecture)
    ↓ [format_converter.py]
Raw Text + Metadata
    ↓ [content_chunker.py]
Chunks with Source References
    ↓ [concept_extractor.py]
Concepts with Chunk IDs
    ↓ [quiz_generator.py / flashcard_generator.py]
Generated Content with Source Attribution
    ↓
Final Output with Verifiable Citations
```

---

## Citation Levels

### Level 1: Specific
- Exact page number
- Specific section heading
- Direct quote reference

### Level 2: General
- Chapter or document
- Topic area
- Approximate location

### Level 3: Derived
- Synthesized from multiple sources
- Inferred from context
- Marked as interpretation

---

## What Requires Citation

| Content Type | Citation Required | Format |
|--------------|-------------------|--------|
| Drug mechanism | Yes | Source, page |
| Drug dose | Yes | Source, page |
| Clinical indication | Yes | Source or guideline |
| Adverse effect | Yes | Source |
| Drug interaction | Yes | Source |
| General principle | Optional | Topic area |
| Mnemonic/memory aid | No | Mark as study aid |

---

## Handling Missing Sources

When source is unclear:

```
Option 1: Flag for review
"[Source needed: Drug X half-life]"

Option 2: Acknowledge limitation
"Based on general pharmacology principles (not from specific source)"

Option 3: Exclude from output
Skip the item if source cannot be verified
```

---

## Citation Verification

Before finalizing content:

- [ ] Every factual claim has a source
- [ ] Source references are valid (exist in input)
- [ ] Citations are consistently formatted
- [ ] Provenance chain is traceable
- [ ] User can verify each fact

---

## Examples

### Correct
```
Q: What is the half-life of warfarin?
A: 36-42 hours (Source: Chapter 12, p. 234)
```

### Incorrect
```
Q: What is the half-life of warfarin?
A: 36-42 hours
(Missing source attribution)
```

### For Synthesized Content
```
Based on the lecture content:
- Warfarin has a long half-life [Lecture 5, slide 12]
- This requires ~5 days to reach steady state [derived from t½]
- Bridging with heparin is often needed [Lecture 5, slide 14]
```

---

## Integration with Quality Scoring

Citations contribute to quality score:

- 100% cited: Full score
- 80-99% cited: Minor deduction
- <80% cited: Major deduction
- <50% cited: Fail quality gate

---

**This guardrail ensures educational content can be verified against source material.**

# Example: Pharmacokinetics Lecture Processing

Complete walkthrough of transforming a PK lecture into study materials.

---

## User Request

> "Create flashcards and a quiz from my pharmacokinetics lecture on drug absorption. I'm a P2 pharmacy student preparing for my midterm next week."

---

## Phase 1: Content Ingestion

### Input
- File: `pharmacokinetics_absorption.pdf` (45 pages)

### Processing
```bash
# Convert PDF to text
python atools/format_converter.py \
  --input pharmacokinetics_absorption.pdf \
  --output lecture.txt

# Chunk content
python atools/content_chunker.py \
  --input lecture.txt \
  --output chunks.json \
  --chunk-size 800 \
  --overlap 160
```

### Output: ingestion_report.md
```
## Ingestion Summary

- Source: pharmacokinetics_absorption.pdf
- Pages: 45
- Total chunks: 32
- Total tokens: 24,500
- Avg tokens/chunk: 766
- Sections detected: 8
- Figures: 12
- Tables: 3

## Sections
1. Introduction to Absorption
2. Passive Diffusion
3. Active Transport
4. Bioavailability
5. First-Pass Effect
6. Factors Affecting Absorption
7. Clinical Applications
8. Summary
```

**Gate Check**: ✅ Content indexed successfully

---

## Phase 2: Concept Extraction

### Processing
```bash
python atools/concept_extractor.py \
  --input chunks.json \
  --output concepts.json
```

### Output: concepts.json (excerpt)
```json
{
  "concepts": [
    {
      "name": "Bioavailability",
      "definition": "Fraction of administered dose reaching systemic circulation",
      "symbol": "F",
      "category": "pharmacokinetics",
      "related": ["First-pass effect", "Route of administration"],
      "source_chunk": "chunk_008"
    },
    {
      "name": "First-pass metabolism",
      "definition": "Metabolism of drug during first passage through liver before reaching systemic circulation",
      "mechanism": "Hepatic CYP450 enzymes metabolize drug before systemic availability",
      "clinical_significance": "Reduces bioavailability of oral drugs",
      "category": "pharmacokinetics",
      "source_chunk": "chunk_012"
    },
    {
      "name": "Passive diffusion",
      "definition": "Movement of drug across membrane down concentration gradient",
      "factors": ["Lipophilicity", "Molecular weight", "Ionization state", "Surface area"],
      "category": "absorption",
      "source_chunk": "chunk_004"
    }
  ],
  "hierarchy": {
    "Pharmacokinetics": {
      "Absorption": {
        "Passive Diffusion": {},
        "Active Transport": {
          "P-glycoprotein": {},
          "OATP transporters": {}
        },
        "Facilitated Diffusion": {}
      },
      "Bioavailability": {
        "First-Pass Effect": {},
        "Route of Administration": {}
      }
    }
  },
  "prerequisites": [
    "Cell membrane structure",
    "pH and ionization (Henderson-Hasselbalch)",
    "Basic liver anatomy"
  ]
}
```

**Gate Check**: ✅ Concepts mapped with hierarchy

---

## Phase 3: Adaptive Clarification

### Expertise Detection
- Vocabulary: "P2 pharmacy student" → Intermediate
- Context: "midterm next week" → Exam prep
- Request: "flashcards and quiz" → Clear format

### Clarification Questions
```
I see you're a P2 student preparing for your pharmacokinetics midterm.
I can create flashcards and a quiz from your absorption lecture.

Quick questions:
1. How many flashcards would be ideal? (I recommend 40-50 for this topic)
2. How many quiz questions? (I suggest 20-25 for effective practice)
3. Should quiz questions include clinical scenarios/vignettes?
4. Do you want explanations with quiz answers?
```

### User Responses
- Flashcards: 50
- Quiz questions: 20
- Vignettes: Yes, some
- Explanations: Yes

### Output: requirements.md
```markdown
# Requirements

## Profile
- User: P2 pharmacy student
- Context: Midterm exam prep
- Expertise: Intermediate

## Outputs
- 50 flashcards (basic + cloze)
- 20 MCQ questions with explanations
- Some clinical vignettes included

## Scope
- Topic: Drug absorption (from lecture)
- Concepts: Passive diffusion, active transport, bioavailability, first-pass effect

## Bloom's Distribution
- Remember: 30%
- Understand: 40%
- Apply: 30%

## Success Criteria
- All key concepts covered
- Clinically relevant examples
- Difficulty appropriate for P2 midterm
```

**Gate Check**: ✅ Requirements clear

---

## Phase 4: Subagent Delegation

### Task Decomposition
```
Task 1: Generate 50 flashcards on absorption concepts
Task 2: Generate 20 MCQ questions with vignettes and explanations
Task 3: Calibrate difficulty for P2 level
```

### Subagent Assignment
```bash
python atools/subagent_selector.py --task "Generate 50 flashcards on absorption concepts"
# Output: flashcard-generator (confidence: 0.95)

python atools/subagent_selector.py --task "Generate 20 MCQ with clinical vignettes"
# Output: quiz-maker (confidence: 0.92)

python atools/subagent_selector.py --task "Calibrate for P2 midterm level"
# Output: difficulty-calibrator (confidence: 0.88)
```

### Output: task_assignments.json
```json
{
  "assignments": [
    {
      "task": "Generate 50 flashcards on absorption concepts",
      "specialist": "flashcard-generator",
      "confidence": 0.95,
      "context": "Focus on bioavailability, first-pass effect, transport mechanisms"
    },
    {
      "task": "Generate 20 MCQ with clinical vignettes and explanations",
      "specialist": "quiz-maker",
      "confidence": 0.92,
      "context": "Include patient scenarios, 30% clinical application"
    },
    {
      "task": "Calibrate difficulty for P2 midterm level",
      "specialist": "difficulty-calibrator",
      "confidence": 0.88,
      "context": "Target: 30% remember, 40% understand, 30% apply"
    }
  ]
}
```

**Gate Check**: ✅ Tasks assigned

---

## Phase 5: Material Generation

### Flashcard Generation
```bash
python atools/flashcard_generator.py \
  --concepts concepts.json \
  --types basic,cloze \
  --output flashcards.json
```

### Output: flashcards.json (excerpt)
```json
{
  "cards": [
    {
      "id": "FC001",
      "type": "basic",
      "front": "What is bioavailability (F)?",
      "back": "The fraction of an administered dose that reaches the systemic circulation unchanged",
      "tags": ["pharmacokinetics", "absorption", "difficulty::medium"],
      "source": "Lecture slides 12-14"
    },
    {
      "id": "FC002",
      "type": "cloze",
      "front": "First-pass metabolism occurs primarily in the [...]",
      "back": "First-pass metabolism occurs primarily in the {{c1::liver}} and {{c2::intestinal wall}}",
      "tags": ["pharmacokinetics", "first-pass", "difficulty::easy"]
    },
    {
      "id": "FC015",
      "type": "basic",
      "front": "How does the Henderson-Hasselbalch equation relate to drug absorption?",
      "back": "It predicts the ionization state of weak acids/bases based on pKa and environmental pH. Un-ionized forms are lipophilic and better absorbed.",
      "tags": ["absorption", "pH", "difficulty::medium"]
    }
  ]
}
```

### Quiz Generation
```bash
python atools/quiz_generator.py \
  --concepts concepts.json \
  --type mcq \
  --count 20 \
  --vignettes \
  --explanations
```

### Output: quiz.json (excerpt)
```json
{
  "questions": [
    {
      "id": "Q001",
      "type": "mcq",
      "vignette": "A 45-year-old patient takes nitroglycerin tablets but places them under the tongue rather than swallowing them.",
      "stem": "Which of the following best explains why sublingual administration is preferred for nitroglycerin?",
      "options": [
        "A. Avoids extensive first-pass hepatic metabolism",
        "B. Increases the half-life of the drug",
        "C. Enhances binding to plasma proteins",
        "D. Reduces the risk of drug interactions"
      ],
      "correct_answer": "A",
      "explanation": "Nitroglycerin undergoes extensive first-pass metabolism (>90%) when taken orally. Sublingual administration allows the drug to enter the systemic circulation directly via the sublingual veins, bypassing hepatic metabolism and achieving rapid therapeutic effect.",
      "bloom_level": "apply",
      "concept": "first-pass metabolism"
    },
    {
      "id": "Q005",
      "type": "mcq",
      "stem": "A weak acid drug with pKa of 4 is in the stomach (pH 2). What percentage is un-ionized?",
      "options": [
        "A. 1%",
        "B. 10%",
        "C. 50%",
        "D. 99%"
      ],
      "correct_answer": "D",
      "explanation": "Using Henderson-Hasselbalch: pH = pKa + log([A-]/[HA]). At pH 2 with pKa 4: 2 = 4 + log([A-]/[HA]), so [A-]/[HA] = 0.01. This means 99% is in the un-ionized (HA) form, which is better absorbed.",
      "bloom_level": "apply",
      "concept": "ionization"
    }
  ]
}
```

### Quality Check
```bash
python atools/quality_scorer.py --materials flashcards.json quiz.json
```

### Output: quality_report.md
```
## Quality Report

### Flashcards (50 cards)
- Accuracy: 100% (no errors detected)
- Coverage: 95% (24/25 key concepts)
- Clarity: 92%
- Difficulty distribution:
  - Easy: 12 (24%)
  - Medium: 28 (56%)
  - Hard: 10 (20%)

### Quiz (20 questions)
- Accuracy: 100%
- Coverage: 88% (concepts well distributed)
- Bloom's distribution:
  - Remember: 6 (30%)
  - Understand: 8 (40%)
  - Apply: 6 (30%)
- Vignette inclusion: 8/20 (40%)

### Overall Score: 94/100 ✅
```

**Gate Check**: ✅ Materials validated

---

## Phase 6: Integration & Delivery

### Conflict Check
- No overlapping content detected
- Consistent terminology across materials
- No contradictions

### Final Package
```
output/
├── flashcards.json          # 50 flashcards
├── flashcards.md            # Markdown format
├── quiz.json                # 20 MCQs
├── quiz.md                  # Printable format
├── answer_key.md            # With explanations
├── quality_report.md        # Quality summary
└── usage_guide.md           # How to use
```

### Usage Guide
```markdown
# Study Materials: Drug Absorption

## Contents
- 50 Flashcards covering absorption mechanisms
- 20 Practice Questions for exam preparation

## Recommended Study Plan
1. Review flashcards (1-2 hours)
2. Take practice quiz (30-45 minutes)
3. Review explanations for missed questions
4. Repeat flashcards daily until exam

## Importing to Anki
The flashcards.json file can be imported to Anki:
1. File → Import
2. Select flashcards.json
3. Match fields: front, back, tags

## Disclaimer
These materials are for educational purposes. Always verify with
your course materials and consult your professor for clarification.
```

**Gate Check**: ✅ Delivery ready

---

## Summary

| Phase | Duration | Output |
|-------|----------|--------|
| Content Ingestion | 2 min | 32 chunks |
| Concept Extraction | 3 min | 25 concepts |
| Clarification | 1 min | Clear requirements |
| Delegation | 1 min | 3 task assignments |
| Generation | 5 min | 50 cards + 20 questions |
| Integration | 1 min | Complete package |

**Total Time**: ~15 minutes
**Materials Created**: 50 flashcards + 20 MCQs with explanations

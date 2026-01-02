# 5W2H Framework for Pharmaceutical Education

Systematic clarification framework adapted for pharmacy professor tasks.

---

## The Seven Dimensions

### WHO - Target Audience

**Question**: "Who is this for?"

**Options**:
- Pharmacy students (P1-P4)
- Nursing students
- Medical students/residents
- Practicing pharmacists
- Pharmacy technicians
- Other healthcare providers
- Patients/caregivers

**Why it matters**:
- Determines appropriate depth and complexity
- Influences terminology and jargon use
- Affects clinical relevance emphasis
- Guides assessment difficulty

**Example Questions**:
- "Are these for pharmacy students or practicing pharmacists?"
- "What year/level are your students?"
- "Will this be used for certification preparation?"

---

### WHAT - Desired Outputs

**Question**: "What materials do you need?"

**Options**:
- Quizzes (MCQ, T/F, matching)
- Flashcards (basic, cloze, reversible)
- Study guides (summary, outline)
- Case studies (clinical scenarios)
- Exams (full assessment)
- Calculation problems
- Review materials
- Mixed formats

**Why it matters**:
- Determines which subagents to engage
- Affects content structuring
- Influences time/effort estimation

**Example Questions**:
- "Do you want quizzes, flashcards, or both?"
- "Should I create a full exam or practice questions?"
- "What mix of question types works best?"

---

### WHEN - Timeline & Context

**Question**: "When is this needed / What's the context?"

**Options**:
- Immediate exam prep (< 1 week)
- Short-term study (1-4 weeks)
- Semester-long course
- Ongoing review
- Just-in-time learning
- Board exam preparation

**Why it matters**:
- Affects scope and quantity
- Influences prioritization
- Determines study schedule integration

**Example Questions**:
- "When is your exam?"
- "Is this for ongoing review or focused preparation?"
- "Do you have a specific deadline?"

---

### WHERE - Usage Context

**Question**: "Where will this be used?"

**Options**:
- Self-study (individual)
- Classroom instruction
- Clinical rotations
- Small group discussion
- Online learning platform
- Professional development
- Patient education

**Why it matters**:
- Affects format and presentation
- Determines interactivity needs
- Influences explanatory depth

**Example Questions**:
- "Will you use these alone or in a class?"
- "Are these for self-study or instructor-led sessions?"
- "Should these work on mobile/digital or print?"

---

### WHY - Learning Objectives

**Question**: "What should learners be able to do after?"

**Bloom's Taxonomy Levels**:
1. **Remember**: Recall facts, terms, definitions
2. **Understand**: Explain concepts, mechanisms
3. **Apply**: Use knowledge in new situations
4. **Analyze**: Compare, differentiate, examine
5. **Evaluate**: Justify, assess, critique
6. **Create**: Design, formulate, synthesize

**Why it matters**:
- Drives question/content difficulty
- Ensures alignment with goals
- Enables appropriate assessment

**Example Questions**:
- "Should learners memorize facts or apply concepts?"
- "Do you want clinical application questions?"
- "Is the goal recognition or deeper understanding?"

---

### HOW - Format Preferences

**Question**: "How should the materials be formatted?"

**Options**:
- Digital (Anki, PDF, web)
- Printable (formatted for paper)
- Interactive (with feedback)
- Mobile-friendly
- Plain text/Markdown
- Structured JSON

**Why it matters**:
- Determines output format
- Affects usability
- Influences distribution method

**Example Questions**:
- "Do you need print-ready or digital format?"
- "Should flashcards be Anki-compatible?"
- "What platform will you use?"

---

### HOW MUCH - Scope & Volume

**Question**: "How much content do you need?"

**Considerations**:
- Number of questions/cards
- Topic breadth vs depth
- Time available for study
- Comprehensiveness vs focus

**Guidelines**:
| Study Time | Flashcards | Quiz Questions |
|------------|------------|----------------|
| 30 min | 20-30 | 10-15 |
| 1 hour | 40-60 | 20-30 |
| 2 hours | 80-100 | 40-50 |
| Comprehensive | 150+ | 75+ |

**Example Questions**:
- "How many flashcards do you need?"
- "Should I cover the entire topic or focus areas?"
- "Is 50 questions about right, or do you need more?"

---

## Question Templates by Dimension

### Minimal Set (Quick Clarification)
```
For your [topic] materials:
1. Who is the target audience?
2. What format - quizzes, flashcards, or both?
3. How many items do you need?
```

### Standard Set (Most Cases)
```
I'd like to understand your needs better:

1. WHO: Is this for students, practitioners, or self-study?
2. WHAT: Do you want quizzes, flashcards, study guides, or a mix?
3. WHY: Should the focus be on memorization, application, or clinical reasoning?
4. HOW MUCH: How many questions/cards would be ideal?
```

### Comprehensive Set (Complex Requests)
```
To create the most useful materials, please tell me:

1. WHO: Who is the target audience and their level?
2. WHAT: What types of materials do you need?
3. WHEN: When do you need this / what's the timeline?
4. WHERE: How will these be used (self-study, class, clinical)?
5. WHY: What should learners be able to do afterward?
6. HOW: What format works best (digital, printable, Anki)?
7. HOW MUCH: What quantity do you need?
```

---

## Pharmaceutical-Specific Questions

### Drug-Focused Content
- "Which drug(s) or drug class(es) should I focus on?"
- "Should I include mechanisms, clinical uses, or both?"
- "Do you want adverse effects and interactions included?"

### Clinical Application
- "Should questions include patient scenarios?"
- "Do you want calculation problems?"
- "How much emphasis on monitoring and labs?"

### Assessment Style
- "Should questions match NAPLEX/board exam style?"
- "Do you want explanations with answers?"
- "Should difficulty increase progressively?"

---

## Decision Tree

```
START
│
├─ Is audience clear?
│   ├─ NO → Ask WHO question
│   └─ YES ↓
│
├─ Is output format clear?
│   ├─ NO → Ask WHAT question
│   └─ YES ↓
│
├─ Is scope clear?
│   ├─ NO → Ask HOW MUCH question
│   └─ YES ↓
│
├─ Is learning objective clear?
│   ├─ NO → Ask WHY question
│   └─ YES ↓
│
└─ PROCEED with generation
```

---

## Scope Bounding

After gathering requirements, confirm bounded scope:

```
"Based on our discussion, I'll create:
- [X] flashcards on [topic]
- For [audience]
- Focused on [objectives]
- In [format]

Does this match what you need?"
```

This prevents scope creep and ensures alignment.

# Expertise Level Detection

Framework for detecting user expertise and adapting clarification questions accordingly.

---

## Expertise Levels

### Level 1: Novice
**Indicators**:
- Broad, unscoped requests ("help me study pharmacology")
- Unfamiliar with terminology ("the heart pills")
- No specific learning objectives mentioned
- Asks for "everything" or "all topics"
- May confuse drug names or classes

**Question Approach**:
- Start with scope-limiting questions
- Offer structured options rather than open-ended
- Provide context and definitions
- Suggest appropriate starting points

**Example Interaction**:
```
User: "I need to study for my pharmacy exam"

Response: "I'd be happy to help you prepare! To create the most useful
study materials, I need to understand a few things:

1. What specific exam? (e.g., pharmacy school midterm, NAPLEX, certification)
2. What topics does it cover?
3. When is your exam?
4. What format works best - flashcards, practice questions, or both?"
```

---

### Level 2: Intermediate
**Indicators**:
- Uses some correct terminology
- Has general learning goals ("need to know drug interactions")
- Can identify topic areas
- May not know specific drugs or details
- Reasonable scope but needs refinement

**Question Approach**:
- Clarify scope within topic area
- Ask about preferred depth
- Confirm format preferences
- Offer options with recommendations

**Example Interaction**:
```
User: "Create flashcards for cardiovascular drug classes"

Response: "I can create cardiovascular flashcards for you. Let me confirm:

1. Should I include all classes (ACE-I, ARBs, beta-blockers, CCBs, diuretics,
   antiarrhythmics, anticoagulants) or focus on specific ones?
2. Do you want mechanism-focused or clinically-focused cards?
3. How many cards are you looking for? (I recommend 40-60 for this topic)
4. Should I include drug interactions and contraindications?"
```

---

### Level 3: Advanced
**Indicators**:
- Specific concept requests
- Uses precise terminology
- Clear format preferences
- Aware of learning objectives
- Can articulate what they don't know

**Question Approach**:
- Minimal clarification needed
- Confirm assumptions
- Ask about edge cases or depth
- Offer advanced options

**Example Interaction**:
```
User: "Create 20 MCQs on CYP450 drug interactions, focus on 2D6 and 3A4,
       application-level questions"

Response: "Understood. I'll create 20 application-level MCQs on CYP2D6 and
CYP3A4 interactions. Quick confirmations:

1. Should I include clinical vignettes with each question?
2. Emphasis on inhibitors, inducers, or both equally?
3. Any specific drug pairs you want included (e.g., fluoxetine-codeine)?"
```

---

### Level 4: Expert
**Indicators**:
- Highly specific requests
- Deep domain knowledge evident
- References specific guidelines or literature
- Clear on format, depth, and scope
- May be teaching or developing curriculum

**Question Approach**:
- Minimal questions
- Confirm only if genuinely ambiguous
- Offer to exceed expectations
- Suggest advanced features

**Example Interaction**:
```
User: "Generate 30 NAPLEX-style questions on antibiotic stewardship
       following IDSA guidelines, include TDM scenarios for aminoglycosides
       and vancomycin, Bloom's distribution: 30% understand, 50% apply, 20% analyze"

Response: "I'll create 30 NAPLEX-style questions with your exact
specifications. I'll include:
- Aminoglycoside (trough-based and AUC-based dosing scenarios)
- Vancomycin (AUC/MIC optimization per 2020 guidelines)
- Antibiotic selection cases per IDSA PNA and UTI guidelines

Should I also include answer explanations with guideline citations?"
```

---

## Detection Triggers

### Vocabulary Analysis
| Indicator | Novice | Intermediate | Advanced | Expert |
|-----------|--------|--------------|----------|--------|
| Drug names | Generic/unclear | Some correct | Precise | Nuanced |
| Classes | Confused | Generally correct | Specific | Including subtypes |
| Mechanisms | Absent | Basic | Detailed | Mechanistic depth |
| Parameters | None | Some awareness | Correct use | Citations |

### Request Structure
| Indicator | Novice | Intermediate | Advanced | Expert |
|-----------|--------|--------------|----------|--------|
| Scope | Too broad | Reasonable | Focused | Precise |
| Format | Unspecified | General preference | Specific | Detailed specs |
| Objectives | Absent | Implicit | Explicit | Measurable |
| Timeline | Often missing | General | Specific | Planned |

### Question Sophistication
| Indicator | Novice | Intermediate | Advanced | Expert |
|-----------|--------|--------------|----------|--------|
| Bloom's level | Remember | Understand | Apply | Analyze/Evaluate |
| Connections | Isolated facts | Related concepts | Integration | Synthesis |
| Application | Theoretical | Some clinical | Clinical focus | Research/teaching |

---

## Adaptive Response Matrix

| Expertise | Questions to Ask | Question Style | Depth |
|-----------|------------------|----------------|-------|
| Novice | 4-5 structured | Multiple choice | Basic scope |
| Intermediate | 2-3 targeted | Brief options | Topic refinement |
| Advanced | 1-2 confirmatory | Open-ended ok | Edge cases |
| Expert | 0-1 if needed | Minimal | Enhancement offers |

---

## Example Expertise Progression

**Same Topic, Different Levels**:

**Novice Request**: "help with warfarin"
→ Ask: "What do you need to know about warfarin? (monitoring, interactions, dosing, patient education)"

**Intermediate Request**: "create warfarin interaction flashcards"
→ Ask: "Should I focus on common interactions (NSAIDs, antibiotics) or comprehensive including rare ones?"

**Advanced Request**: "30 MCQs on warfarin-antibiotic interactions with INR interpretation"
→ Ask: "Should I include DOAC comparison questions as well?"

**Expert Request**: "Generate case-based questions on warfarin-antibiotic interactions following 2023 CHEST guidelines, include genetic polymorphism considerations"
→ Proceed with minimal clarification

---

## Expertise Detection Algorithm

```
1. Analyze vocabulary specificity (1-4 points)
2. Assess request structure (1-4 points)
3. Evaluate question sophistication indicators (1-4 points)
4. Average score → Expertise level

Score 1-1.5 → Novice
Score 1.5-2.5 → Intermediate
Score 2.5-3.5 → Advanced
Score 3.5-4 → Expert
```

---

## Calibration Notes

- When uncertain, default to asking one clarifying question
- Better to slightly underestimate than overestimate
- Watch for expertise in specific areas but not others
- Allow expertise level to adjust mid-conversation

# Flashcard Generator Subagent

**Cognitive Model**: Spaced Repetition Specialist

**Domain**: Anki-style flashcard creation for pharmaceutical education

---

## Capabilities

1. **Basic Card Creation**
   - Front/back pair format
   - Clear, concise content
   - Single fact per card

2. **Cloze Deletion**
   - Fill-in-the-blank format
   - Multiple cloze deletions per note
   - Context preservation

3. **Reversible Cards**
   - Bidirectional testing
   - Drug → Property and Property → Drug
   - Useful for associations

4. **Tagging System**
   - Topic-based tags
   - Difficulty levels
   - Exam relevance markers

---

## Input Requirements

- **concepts**: List of pharmaceutical concepts
- **card_types**: basic, cloze, reversible, image_occlusion
- **include_tags**: Boolean for organization tags
- **reversible**: Boolean for bidirectional cards
- **max_length**: Maximum characters per card side

---

## Output Format

```json
{
  "cards": [
    {
      "id": "FC001",
      "type": "basic",
      "front": "What is the mechanism of action of lisinopril?",
      "back": "ACE inhibitor - blocks conversion of angiotensin I to angiotensin II",
      "tags": ["cardiovascular", "ACE-inhibitors", "mechanism", "difficulty::medium"],
      "source": "Chapter 5, Page 142",
      "difficulty": "medium"
    },
    {
      "id": "FC002",
      "type": "cloze",
      "front": "Warfarin works by inhibiting [...] synthesis.",
      "back": "Warfarin works by inhibiting {{c1::vitamin K-dependent clotting factor}} synthesis.",
      "tags": ["anticoagulants", "mechanism"],
      "difficulty": "medium"
    }
  ],
  "metadata": {
    "total_cards": 50,
    "type_distribution": {"basic": 30, "cloze": 15, "reversible": 5},
    "estimated_study_time_minutes": 25
  }
}
```

---

## Card Design Principles

### Front Side (Question)
- One question per card
- Clear, unambiguous phrasing
- Context when needed
- Maximum 2-3 sentences

### Back Side (Answer)
- Direct answer first
- Supporting details below
- Maximum 3-4 key points
- Avoid paragraphs

---

## Pharmaceutical Card Templates

### Drug Mechanism
**Front**: What is the mechanism of action of [drug]?
**Back**: [mechanism description]

### Drug Class
**Front**: What drug class does [drug] belong to?
**Back**: [drug class]

### Drug Indication
**Front**: What is the primary indication for [drug]?
**Back**: [indication]

### Drug Adverse Effect
**Front**: What is a major adverse effect of [drug]?
**Back**: [adverse effect] - [clinical significance]

### Drug Interaction
**Front**: What is a significant drug interaction with [drug]?
**Back**: [interacting drug] - [mechanism] - [clinical effect]

### PK Parameter
**Front**: What is the half-life of [drug]?
**Back**: [value] - [clinical implication]

### Contraindication
**Front**: What is a contraindication for [drug]?
**Back**: [contraindication] - [reason]

---

## Cloze Deletion Patterns

### Single Cloze
```
{{c1::Metformin}} is first-line therapy for type 2 diabetes.
```

### Multiple Cloze (Same Card)
```
Warfarin inhibits synthesis of clotting factors {{c1::II}}, {{c2::VII}}, {{c3::IX}}, and {{c4::X}}.
```

### Overlapping Cloze
```
{{c1::ACE inhibitors::Drug class}} cause {{c2::dry cough::Adverse effect}} due to {{c3::bradykinin accumulation::Mechanism}}.
```

---

## Tagging Conventions

### Topic Tags
- `cardiovascular`, `endocrine`, `infectious`, `CNS`, `oncology`

### Drug Class Tags
- `ACE-inhibitors`, `beta-blockers`, `statins`, `antibiotics`

### Difficulty Tags
- `difficulty::easy`, `difficulty::medium`, `difficulty::hard`

### Exam Tags
- `NAPLEX`, `BCPS`, `board-relevant`

### Learning Stage
- `new`, `review`, `mastered`

---

## Quality Criteria

- [ ] One fact per card (atomic)
- [ ] Clear question/answer format
- [ ] No ambiguity
- [ ] Appropriate length (front < 50 words, back < 100 words)
- [ ] Proper tagging
- [ ] Spelling and terminology correct
- [ ] Clinically accurate

---

## Spaced Repetition Optimization

1. **Atomic cards**: One piece of information per card
2. **Context independence**: Cards work without other cards
3. **Personal connection**: Relate to clinical scenarios
4. **Imagery**: Use memorable associations
5. **Redundancy**: Multiple angles on important concepts

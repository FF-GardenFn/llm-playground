---
name: flashcards
description: Generate Anki-style flashcards from pharmaceutical content
arguments:
  - name: content
    description: The content to create flashcards from (file path, text, or topic)
    required: false
  - name: count
    description: Number of flashcards to generate (default: 50)
    required: false
  - name: type
    description: Card type - basic, cloze, or reversible (default: basic)
    required: false
---

# Generate Pharmacy Flashcards

Create spaced-repetition flashcards from pharmaceutical educational content.

## What This Command Does

1. **Process content** to extract key pharmaceutical concepts
2. **Generate flashcards** optimized for:
   - Active recall (question format)
   - Spaced repetition (atomic facts)
   - Multiple formats (basic, cloze, reversible)
3. **Tag and organize** for efficient studying

## Quick Examples

```
/flashcards                          # Interactive mode
/flashcards pharmacology 100         # 100 cards on pharmacology
/flashcards lecture.pdf cloze        # Cloze deletion cards from PDF
/flashcards "beta blockers" basic 30 # 30 basic cards on beta blockers
```

## Your Task

When invoked, follow this workflow:

### Step 1: Content Source
If content provided:
- File path → Load and chunk content
- Topic name → Generate cards on that topic
- Inline text → Process directly

If no content:
- Ask: "What content should I create flashcards from?"

### Step 2: Quick Clarification
- How many cards? (suggest 40-60 per topic)
- Card type? (basic for most, cloze for fill-in-blank practice)
- Include which elements?
  - Drug mechanisms
  - Indications
  - Adverse effects
  - Drug interactions
  - Dosing
  - Clinical pearls

### Step 3: Generate Cards
For each key concept, create appropriate cards:

**Basic Cards**:
```
Front: What is the mechanism of action of metformin?
Back: Inhibits hepatic gluconeogenesis, increases peripheral glucose uptake
```

**Cloze Cards**:
```
Metformin works by inhibiting {{c1::hepatic gluconeogenesis}}.
```

**Reversible Cards**:
```
Card 1: What drug class does lisinopril belong to? → ACE inhibitor
Card 2: Name an ACE inhibitor → Lisinopril
```

### Step 4: Output with Tags
Provide cards with organizational tags:
- `topic::pharmacokinetics`
- `drug-class::ACE-inhibitors`
- `difficulty::medium`
- `exam::NAPLEX`

## Card Templates

### Drug Mechanism
| Front | Back |
|-------|------|
| What is the mechanism of [drug]? | [mechanism description] |

### Drug Class
| Front | Back |
|-------|------|
| What class is [drug]? | [drug class] |
| Name a drug in [class] | [drug example] |

### Adverse Effects
| Front | Back |
|-------|------|
| Major adverse effect of [drug]? | [adverse effect] |
| Which drug causes [effect]? | [drug name] |

### Drug Interactions
| Front | Back |
|-------|------|
| Interaction between [drug1] and [drug2]? | [mechanism and effect] |

### Clinical Pearls
| Front | Back |
|-------|------|
| Key monitoring for [drug]? | [parameters] |
| When to avoid [drug]? | [contraindications] |

## Output Formats

### JSON (Anki-compatible)
```json
{
  "cards": [
    {
      "front": "What is the half-life of warfarin?",
      "back": "36-42 hours",
      "tags": ["anticoagulants", "pharmacokinetics"]
    }
  ]
}
```

### Markdown (for review)
```markdown
## Flashcard Deck: Anticoagulants

### Card 1
**Q:** What is the mechanism of warfarin?
**A:** Inhibits vitamin K epoxide reductase, preventing synthesis of clotting factors II, VII, IX, X

### Card 2
**Q:** Warfarin inhibits synthesis of clotting factors {{c1::II, VII, IX, X}}
```

## Spaced Repetition Tips (included with output)
- Study new cards daily
- Review due cards before adding new ones
- Keep cards atomic (one fact per card)
- Use images for drug structures when helpful

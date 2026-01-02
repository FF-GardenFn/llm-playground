# Guardrail 01: Accuracy First

**Priority**: CRITICAL

**Principle**: Never hallucinate pharmaceutical information. Accuracy is non-negotiable.

---

## Core Rules

### 1. No Invented Drug Information
- Never create fictional drug names
- Never invent mechanisms of action
- Never fabricate dosing information
- Never guess at drug interactions

### 2. Verification Requirements
- Drug names must match known medications
- Doses must be within established ranges
- Mechanisms must be pharmacologically accurate
- Interactions must be documented

### 3. Uncertainty Handling
- When uncertain, flag for review
- Use hedging language appropriately
- Recommend verification from authoritative sources
- Never present speculation as fact

---

## Critical Information Categories

### Must Be Accurate
| Category | Example | Risk if Wrong |
|----------|---------|---------------|
| Drug names | Metoprolol vs Methotrexate | Wrong medication |
| Doses | 5 mg vs 50 mg | Over/underdose |
| Routes | IV vs PO | Toxicity |
| Frequencies | Daily vs BID | Therapeutic failure |
| Interactions | Major DDIs | Patient harm |
| Contraindications | Pregnancy category | Fetal harm |
| Black box warnings | Suicidality, QT | Death |

### Allowable Simplification
- General mechanism descriptions (but not invented ones)
- Rounding of PK parameters for teaching
- Consolidation of similar adverse effects
- Grouping of minor interactions

---

## Verification Checklist

Before generating content about a drug:

- [ ] Is this a real medication?
- [ ] Is the drug name spelled correctly?
- [ ] Are brand/generic names correct?
- [ ] Is the mechanism pharmacologically accurate?
- [ ] Are doses within established ranges?
- [ ] Are adverse effects clinically documented?
- [ ] Are interactions evidence-based?

---

## Error Prevention Strategies

### 1. Cross-Reference
- Compare drug information across multiple concept sources
- Flag inconsistencies for review
- Use conservative estimates when ranges vary

### 2. Scope Limitation
- Only generate content from provided source material
- Don't extrapolate beyond available information
- Acknowledge gaps rather than fill them

### 3. Template-Based Safety
- Use validated question templates
- Pre-verify distractor options
- Lock critical facts in approved formats

---

## When in Doubt

```
If uncertain about drug information:
1. Do NOT guess
2. Flag the uncertainty
3. Recommend verification
4. Provide general principle if safe
5. Cite source material only
```

---

## Examples

### Correct Approach
```
Question: "What is the mechanism of atorvastatin?"

✓ "Atorvastatin is an HMG-CoA reductase inhibitor that blocks
   cholesterol synthesis in the liver."

✗ "Atorvastatin blocks CYP3A4 to reduce cholesterol production."
   (Incorrect mechanism - confuses metabolism with action)
```

### Handling Uncertainty
```
Question: "What is the half-life of [obscure drug]?"

✓ "I don't have specific half-life data for this medication
   in the provided materials. Please verify with current
   product labeling or a drug information resource."

✗ "The half-life is approximately 12 hours."
   (Invented data)
```

---

## Escalation Protocol

If accuracy cannot be verified:

1. **STOP** content generation for that item
2. **FLAG** the specific uncertainty
3. **RECOMMEND** authoritative source check
4. **CONTINUE** with verified content only

---

## Authoritative Sources for Verification

- Drug product labeling (package inserts)
- Clinical Pharmacology / Lexicomp / Micromedex
- UpToDate drug monographs
- Published clinical guidelines
- Peer-reviewed literature

---

**This guardrail is BLOCKING. Content with unverified critical drug information must not proceed.**

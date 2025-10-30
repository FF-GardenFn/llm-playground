---
description: Formalize mechanistic claims with structural templates (Research Phase 1)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: [hypothesis-text]
---

# Formalize Hypothesis Command

Execute Phase 1 research: receive hypothesis, formalize with mechanistic specificity, select template.

## What this does

1. **Receives hypothesis** from user (informal or formal claim)
2. **Selects template** (causal-claim, circuit-hypothesis, emergence-hypothesis)
3. **Formalizes claim** using hypotheses/FORMALIZATION.md
4. **Validates specificity** (components, mechanisms, interventions, falsifiability)
5. **Documents formalized hypothesis** for investigation design

## Usage

```bash
# Formalize informal hypothesis
/formalize-hypothesis "I think attention heads are doing error correction"

# Formalize with specific template
/formalize-hypothesis --template causal-claim "Head 5.1 corrects errors via residual inhibition"

# Review templates first
/formalize-hypothesis --list-templates
```

## Your Task

1. **Load formalization workflow**: Read `hypotheses/FORMALIZATION.md`
2. **Receive hypothesis**: User provides claim (informal or formal)
3. **Select template**: Choose from:
   - `hypotheses/templates/causal-claim.md` - Component X causes Y via mechanism Z
   - `hypotheses/templates/circuit-hypothesis.md` - Heads H implement algorithm A
   - `hypotheses/templates/emergence-hypothesis.md` - Phenomenon P emerges at phase T
4. **Formalize claim**: Apply mechanistic specificity checks
5. **Validate formalization**: Ensure components named, mechanism described, interventions predicted, falsifiability clear
6. **Complete gate**: `hypotheses/GATE-HYPOTHESIS-FORMALIZED.md`
7. **Report**: Formalized hypothesis with template, specificity validation

## Expected Output

```
✓ Hypothesis formalized

Original claim:
"Attention heads perform error correction"

Template selected: causal-claim.md

Formalized hypothesis:
**Component**: Attention head 5.1 (layer 5, head 1)
**Effect**: Error correction in next-token prediction
**Mechanism**: Residual path inhibition of competing predictions

Mechanistic specificity validation:
✓ Components named: Layer 5, head 1 (L5.H1)
✓ Mechanism described: Residual inhibition (not just correlation)
✓ Interventions predicted: Ablating L5.H1 increases error rate
✓ Falsifiability: If ablation has no effect, hypothesis falsified

Causal predictions:
- Ablation experiment: Remove L5.H1 → error rate increases
- Patching experiment: Patch L5.H1 activations → errors decrease
- Steering experiment: Amplify L5.H1 → over-correction appears

→ Hypothesis ready for framework contextualization
→ Recommend: /contextualize to connect to theoretical foundations
```

## Mechanistic Specificity Checks

**Required for formalization**:
- [ ] Names specific components (layers, heads, neurons, circuits)
- [ ] Describes mechanism (causal pathway, not correlation)
- [ ] Predicts interventions (what happens if ablated/patched)
- [ ] Shows falsifiability (what evidence would disprove)

## Gate

**Cannot proceed to /contextualize without**:
- [ ] Hypothesis formalized using template
- [ ] All 4 specificity checks passed
- [ ] Causal predictions documented
- [ ] Template filed in hypotheses/

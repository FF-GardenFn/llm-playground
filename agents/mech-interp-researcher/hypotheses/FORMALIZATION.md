# Hypothesis Formalization

## Purpose
Transform vague claims into mechanistically specific, testable hypotheses.

## Mechanistic Specificity Requirements

**Vague (not acceptable):**
- "The model learns to do X"
- "Attention is important for Y"
- "The network represents Z"

**Mechanistically specific (required):**
- "Attention heads L4.H2 and L4.H5 implement X via residual path composition"
- "Neuron L2.N145 detects feature Y with activation threshold >3.2"
- "Circuit [L0.H1 → L1.H3 → L2.H7] computes Z using OV matrix composition"

## Three Components Required

### 1. Components Named
- Specific layers (L0, L5, etc.)
- Specific heads (H2, H7, etc.)
- Specific neurons (N145, N822, etc.)
- Specific circuits (paths through network)

**Not:** "Some attention heads"
**Yes:** "Heads L5.H1, L5.H4, L5.H9"

### 2. Mechanism Described
- How does it work?
- What operations occur?
- What information flows where?

**Not:** "The head does error correction"
**Yes:** "Head L5.H1 detects errors by comparing predicted next token (via OV circuit) to actual distribution, then suppresses erroneous predictions via negative residual contribution"

### 3. Interventions Predicted
- What happens if we ablate component X?
- What happens if we patch activation Y?
- What happens if we amplify signal Z?

**Not:** "The circuit is necessary"
**Yes:** "Ablating L5.H1 increases error rate by 15% on tasks requiring error correction, but has <2% effect on other tasks"

## Formalization Templates

Select appropriate template:

### Causal Claim
"Component X causes effect Y via mechanism Z"
→ Use: templates/causal-claim.md

### Circuit Hypothesis
"Heads/neurons H implement algorithm A using operations O"
→ Use: templates/circuit-hypothesis.md

### Emergence Hypothesis
"Phenomenon P emerges at training phase T via process R"
→ Use: templates/emergence-hypothesis.md

## Falsifiability Check

**Every hypothesis must specify:**
- What evidence would validate it?
- What evidence would falsify it?
- How to distinguish from alternative explanations?

**If hypothesis cannot be falsified, it's not science - refine it.**

## Example Transformation

### Before (vague):
"Induction heads are important for in-context learning"

### After (mechanistic):
**Components:** L0.H7 → L1.H4 (two-layer circuit)

**Mechanism:**
- L0.H7 copies token identities to next position (QK pattern)
- L1.H4 attends back to previous occurrence of current token (QK pattern matching L0.H7 output)
- L1.H4 copies value of token following previous occurrence (OV circuit)
- Result: Predicts token that followed similar context

**Predictions:**
- Ablating L0.H7: Induction performance drops 80%+
- Ablating L1.H4: Induction performance drops 80%+
- Ablating both: Residual 5% from other circuits
- Patching L0.H7 activations from incorrect context: L1.H4 makes errors matching patched context

**Falsifiable via:** Ablation studies, activation patching, attention pattern analysis

**Alternative explanations to test:**
1. Single-layer lookup (refuted by ablation showing 2-layer requirement)
2. Bigram statistics (refuted by performance on novel bigrams)
3. Position-based memorization (refuted by position randomization)

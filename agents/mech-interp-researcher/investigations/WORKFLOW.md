# Investigation Workflow

## Purpose
Standard pattern for rigorous hypothesis testing. Not rigid steps - natural scientific flow.

---

## Core Pattern

```
Hypothesis → Decomposition → Alternatives → Predictions → Experiments → Validation
     ↓                                                                        ↓
  Refine ←──────────────────────────────────────────────────────────────── Evidence
```

---

## 1. Hypothesis Decomposition

**Break into atomic testable claims:**

Example hypothesis: "Attention head L5.H1 performs error correction"

**Atomic claims:**
1. L5.H1 activates on errors
2. L5.H1 suppresses incorrect predictions
3. Ablating L5.H1 increases error rate
4. Effect is specific to error contexts
5. Mechanism uses negative residual contribution

**Why decompose:** Test each claim independently, identify which parts hold

---

## 2. Generate Alternative Mechanisms

**Critical step:** Generate 3-4 competing explanations

**Example alternatives for error correction:**
1. **Prediction suppression:** Head detects errors, suppresses wrong predictions
2. **Context amplification:** Head amplifies correct context, doesn't directly suppress errors
3. **Attention routing:** Head routes attention away from error-prone features
4. **Spurious correlation:** Head correlates with errors but doesn't cause correction

**Requirements:**
- Each alternative mechanistically specified
- Alternatives differ in observable predictions
- Include null hypothesis (no causal relationship)

**Why:** Single hypothesis testing is confirmation bias. Science requires alternatives.

---

## 3. Differential Predictions

**For each alternative, what differs observably?**

| Mechanism | Prediction 1 | Prediction 2 | Prediction 3 |
|-----------|-------------|-------------|-------------|
| Prediction suppression | Ablation → errors ↑ | Patching from error → error ↑ | Negative residual on errors |
| Context amplification | Ablation → errors ↑ | Patching from correct → errors ↓ | Positive residual on correct |
| Attention routing | Ablation → errors ↑ | Attention pattern changes | No direct output effect |
| Spurious correlation | Ablation → no effect | Correlation but not causation | Confound exists |

**Key:** Find experiments that discriminate between alternatives

---

## 4. Critical Experiments

**Design tests that rule out alternatives:**

**Experiment 1: Ablation**
- Method: Zero head L5.H1 activations
- If prediction suppression: Error rate increases
- If spurious correlation: No effect
- **Discriminates:** Causation vs correlation

**Experiment 2: Activation Patching**
- Method: Patch activations from error context → correct context
- If prediction suppression: Errors appear in correct context
- If context amplification: Correct context becomes more confident
- **Discriminates:** Suppression vs amplification

**Experiment 3: Residual Analysis**
- Method: Measure residual contributions on error vs correct
- If prediction suppression: Negative on errors
- If context amplification: Positive on correct
- **Discriminates:** Mechanism direction

**Experiment 4: Attention Pattern Analysis**
- Method: Where does head attend?
- If attention routing: Attention away from error features
- If prediction suppression: Attention pattern irrelevant
- **Discriminates:** Attention-based vs output-based

---

## 5. Controls & Sanity Checks

**Controls to run:**
- Baseline: Test on non-error contexts (should show no effect)
- Specificity: Test on other heads (should not show same pattern)
- Task specificity: Test on unrelated tasks (should not generalize inappropriately)

**Sanity checks:**
- Does ablation of random heads show effect? (No → good)
- Does effect disappear on random inputs? (Yes → good)
- Does effect size match hypothesis prediction? (Yes → good)

**See:** validation/sanity-checks.md for standard checks

---

## 6. Evidence Synthesis

**What did experiments show?**
- Which alternatives ruled out:
- Which remain plausible:
- Confidence level:

**Update hypothesis:**
- Original claim:
- Refined claim based on evidence:
- Boundary conditions discovered:

**Next questions:**
- What remains unexplained:
- What new questions emerged:
- What deeper investigation needed:

---

## 7. Robustness Testing

**Test hypothesis boundaries:**
- Different model sizes:
- Different training stages:
- Different datasets:
- Different architectures:

**Cross-validation approaches:**
- Replicate with different methods
- Test on edge cases
- Check for confounds

**See:** validation/robustness-tests.md

---

## Example: Full Workflow

**Hypothesis:** "Induction heads implement in-context learning via token copying"

**1. Decomposition:**
- Claim 1: Two-layer circuit exists (L0.H7 → L1.H4)
- Claim 2: L0.H7 copies token identities
- Claim 3: L1.H4 attends to previous occurrence
- Claim 4: Circuit predicts following token

**2. Alternatives:**
- Alt 1: Two-layer copying circuit
- Alt 2: Single-layer bigram statistics
- Alt 3: Position-based memorization
- Alt 4: Unigram boosting (no copying)

**3. Differential Predictions:**
- If two-layer: Ablating either layer breaks performance
- If single-layer: Only one layer matters
- If position-based: Randomizing positions breaks performance
- If unigram: No context dependence

**4. Critical Experiments:**
- Exp 1: Ablate L0.H7 → Performance drops 80%
- Exp 2: Ablate L1.H4 → Performance drops 80%
- Exp 3: Ablate both → Drops 95%
- Exp 4: Position randomization → Performance maintained
- **Result:** Strong evidence for two-layer circuit, rules out position-based

**5. Evidence → Alt 1 (two-layer circuit) strongly supported**

**6. Next questions:**
- What about attention heads beyond L0.H7 and L1.H4?
- Does this generalize to longer-range dependencies?
- What other algorithms use similar composition patterns?

---

## Workflow Principles

**Generate alternatives:** Always 3-4 competing explanations
**Test discriminatively:** Design experiments that rule out alternatives
**Control rigorously:** Use proper baselines and negative controls
**Update iteratively:** Refine hypothesis based on evidence
**Document failures:** Negative results constrain theory space

**Not checklist:** Natural scientific investigation flow
**Not rigid:** Adapt to specific hypothesis and context
**But structured:** Ensure rigor and avoid confirmation bias

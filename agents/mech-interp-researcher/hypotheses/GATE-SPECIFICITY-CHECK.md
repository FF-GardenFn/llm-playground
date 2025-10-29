# GATE: Mechanistic Specificity Checkpoint

## ⚠️ MANDATORY CHECKPOINT - DO NOT PROCEED UNTIL ALL ITEMS VERIFIED

**Purpose**: Ensure hypothesis has mechanistic specificity before framework selection.

---

## Verification Checklist

**Hypothesis Formalization Complete:**

□ **Template filled**: hypotheses/[hypothesis-name].md exists with all sections complete
□ **Components explicitly named**: Specific layers, heads, or circuits identified (not "the model")
□ **Mechanism described**: Actual causal mechanism, not just correlation or behavior
□ **Interventions predicted**: Specific ablation/modification predictions stated
□ **Falsifiability defined**: Clear criteria for what would disprove the hypothesis

**Mechanistic Detail Verification:**

□ **Input-output mapping**: Clear transformation described
□ **Intermediate steps**: Processing stages identified
□ **Component interactions**: How parts work together specified
□ **Alternative ruled out**: At least one simpler explanation considered

**Required Artifacts Present:**

□ Completed template in: hypotheses/templates/[selected-template].md
□ Formalization notes in: hypotheses/FORMALIZATION.md reviewed
□ Specific predictions documented

---

## GATE STATUS

**IF ANY CHECKBOX UNCHECKED:**
- ❌ **BLOCKED** - Return to hypotheses/FORMALIZATION.md
- Review mechanistic specificity requirements
- Complete missing elements
- Cannot access Phase 2 until resolved

**IF ALL CHECKBOXES COMPLETE:**
- ✅ **GATE PASSED** - Proceed to frameworks/INDEX.md
- Hypothesis has sufficient mechanistic specificity
- Ready for framework contextualization

---

## Common Failures Requiring Return

**Vague Components:**
- ❌ "The model understands" → Specify which components
- ❌ "Attention mechanism" → Which heads specifically?
- ❌ "Later layers" → Which layers exactly?

**Missing Mechanism:**
- ❌ "X correlates with Y" → Describe causal path
- ❌ "Performance improves" → What mechanism causes improvement?
- ❌ "Learns to recognize" → How does recognition occur mechanistically?

**Unfalsifiable Claims:**
- ❌ "Might involve" → Make specific prediction
- ❌ "Could be related" → State definite relationship
- ❌ "Possibly through" → Commit to specific mechanism

---

## Navigation

**BLOCKED → Return to:** hypotheses/FORMALIZATION.md
**PASSED → Proceed to:** frameworks/INDEX.md

---

*Gate enforcement is mandatory. Skipping this checkpoint invalidates the investigation.*
# GATE: Experimental Controls Checkpoint

## ⚠️ MANDATORY CHECKPOINT - CONTROLS REQUIRED FOR VALIDITY

**Purpose**: Ensure proper controls are designed before running experiments. Without controls, results are uninterpretable.

---

## Verification Checklist

**Control Design Complete:**

□ **Negative controls** defined: What should NOT activate the mechanism
□ **Positive controls** defined: What should DEFINITELY activate it
□ **Randomization controls** defined: Shuffled/random baselines
□ **Ablation controls** defined: Component removal effects

**Statistical Rigor:**

□ **Sample size** justified (not arbitrary)
□ **Multiple seeds** for training-based experiments
□ **Statistical tests** selected (not just eyeballing)
□ **Effect size** expectations stated

**Confound Management:**

□ **Known confounds** identified
□ **Mitigation strategies** defined
□ **Cannot be mitigated** → acknowledged as limitation
□ **Alternative explanations** controls address

---

## Required Artifacts from Previous Phases

**Must reference:**
- ✓ Primary hypothesis (Phase 1)
- ✓ Alternative mechanisms (Phase 3a)
- ✓ Differential predictions between alternatives
- ✓ All previous gates passed

**Controls must test differences between competing hypotheses.**

---

## GATE STATUS

**IF CONTROLS MISSING:**
- ❌ **BLOCKED** - Experiments without controls are invalid
- Return to investigations/validation/
- Design proper controls
- Cannot proceed to execution

**IF CONTROLS INADEQUATE:**
- ❌ **BLOCKED** - Weak controls = weak conclusions
- Each hypothesis needs distinguishing control
- Statistical rigor required

**IF ALL CONTROLS VERIFIED:**
- ✅ **GATE PASSED** - Proceed to experiment execution
- Controls will enable valid interpretation
- Results will be scientifically meaningful

---

## Control Design Patterns

**Essential Control Types:**

1. **Negative Control** - Should produce null result
   - Random input → No pattern detection
   - Shuffled tokens → No syntax understanding
   - Untrained model → No learned behavior

2. **Positive Control** - Should definitely work
   - Canonical example → Clear activation
   - Amplified pattern → Strong response
   - Known mechanism → Verified behavior

3. **Ablation Control** - Remove hypothesized component
   - Zero out attention head → Behavior persists?
   - Remove circuit → Function remains?
   - Mask features → Performance drops?

4. **Permutation Control** - Scramble but preserve statistics
   - Shuffle within categories
   - Random pairing of inputs/outputs
   - Preserve marginals, break relationships

---

## Common Control Failures

**Inadequate Negative Controls:**
- ❌ No true negative → Can't prove specificity
- ❌ Negative too similar → Doesn't test boundary
- ❌ Single negative → Not robust

**Missing Statistical Controls:**
- ❌ Single run → No variance estimate
- ❌ No significance test → Just "looks different"
- ❌ Cherry-picked examples → Not representative

**Confound Blindness:**
- ❌ Correlated features → Can't determine cause
- ❌ Training artifacts → Memorization vs computation
- ❌ Dataset biases → Spurious patterns

---

## Control Verification Questions

Before proceeding, answer:

1. **If the mechanism doesn't exist, will controls show null result?**
2. **If alternative mechanism is true, will controls distinguish it?**
3. **Are controls strong enough to convince a skeptic?**
4. **Do controls rule out trivial explanations?**

If any answer is "No" → Design better controls

---

## Navigation

**BLOCKED → Return to:** investigations/validation/sanity-checks.md
**PASSED → Proceed to:** Experiment execution phase

---

*Controls are not optional. They are the difference between science and storytelling.*
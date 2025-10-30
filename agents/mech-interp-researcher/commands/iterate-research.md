---
description: Refine hypothesis based on evidence and plan next experiments (Research Phase 5)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: [--synthesis]
---

# Iterate Research Command

Execute Phase 5 research: document findings, update hypothesis, record negative results, generate next experiments.

## What this does

1. **Updates hypothesis** (which claims validated, falsified, refined)
2. **Records negative results** (what failed and why)
3. **Identifies boundaries** (where mechanism applies, where it breaks)
4. **Generates next experiments** (what remains untested)
5. **Synthesizes understanding** (coherent mechanistic story)

## Usage

```bash
# Standard iteration (update hypothesis + next steps)
/iterate-research

# Synthesis mode (write coherent mechanistic story)
/iterate-research --synthesis

# Focus on negative results
/iterate-research --focus negative-results

# Generate research roadmap
/iterate-research --roadmap
```

## Your Task

1. **Load experimental results**: Review all completed experiments
2. **Update hypothesis**: Which claims validated? Falsified? Refined?
3. **Record negative results**: What approaches failed and why?
4. **Identify boundaries**: Where does mechanism apply? Break?
5. **Generate next experiments**: What remains untested?
6. **Synthesize understanding**: Write coherent mechanistic story
7. **Complete gate**: `iteration/GATE-ITERATION-COMPLETE.md`
8. **Report**: Updated hypothesis, negative results, next experiments, synthesis

## Expected Output

```
✓ Research iteration complete

Original hypothesis:
"Attention head 5.1 corrects errors via residual path inhibition"

Experimental results summary:

Claims validated (3):
✓ L5.H1 activates on error-prone contexts (confirmed)
✓ L5.H1 OV matrix produces inhibitory signal (confirmed)
✓ Inhibitory signal travels via residual stream (confirmed)

Claims falsified (1):
✗ L5.H1 attention pattern targets error positions (FALSIFIED)
  → Evidence: Attention pattern unchanged, targets context not errors

Claims refined (1):
⚠ Signal suppresses incorrect next-token predictions (REFINED)
  → L5.H1 suppresses high-probability incorrect tokens, not all errors
  → Boundary: Only effective for errors with high model confidence

Updated hypothesis (v2):
"Attention head 5.1 corrects high-confidence errors via residual path inhibition. L5.H1 produces negative residual contributions that suppress logits of confidently-wrong tokens. The mechanism does not change attention patterns but directly modulates output probabilities through the residual stream."

Changes from v1:
- Added "high-confidence" specificity
- Removed "attention targeting" claim (falsified)
- Added "direct modulation" mechanism detail
- Specified boundary conditions

Negative results:

What approaches failed:
1. **Attention pattern analysis** → No pattern change detected
   - Why failed: Mechanism operates via residual, not attention
   - What this constrains: Error correction doesn't require attention redirection

2. **Early layer ablation** → No effect from L1-L4 head ablations
   - Why failed: Error correction emerges in mid-layers (L5-L8)
   - What this constrains: Capability develops after basic pattern matching

3. **Syntax error correction** → L5.H1 ineffective on syntax errors
   - Why failed: Mechanism targets semantic errors specifically
   - What this constrains: Error correction is content-type specific

Value of negative results:
✓ Falsified "attention redirection" mechanism → Focus on residual pathway
✓ Identified layer boundaries → Error correction = mid-layer phenomenon
✓ Discovered content-type specificity → Semantic vs syntax distinction

Boundary identification:

Where mechanism applies:
✓ Semantic errors (wrong facts, incorrect associations)
✓ High-confidence mistakes (model probability > 0.6)
✓ Context length ≥ 5 tokens
✓ Mid-to-late tokens in sequence
✓ In-distribution inputs

Where mechanism breaks:
✗ Syntax errors (grammar, punctuation)
✗ Low-confidence errors (model already uncertain)
✗ Very short contexts (< 5 tokens)
✗ First 2 tokens in sequence
✗ Out-of-distribution inputs (adversarial prompts)

Edge cases discovered:
- Over-correction: L5.H1 sometimes suppresses correct tokens (5% rate)
- Adversarial boost: Ablating L5.H1 improves adversarial robustness (!)
- Model size effect: Stronger in GPT-2 than GPT-3 (scaling behavior)

Next experiments:

What remains untested:
1. **Survey study**: Are there other inhibitory heads in L5-L8?
2. **Training dynamics**: When does L5.H1 develop this capability?
3. **Composition analysis**: Do downstream heads depend on L5.H1?
4. **Intervention study**: Can we steer L5.H1 to reduce hallucinations?
5. **Cross-model study**: Does this pattern generalize to other architectures?

What new questions emerged:
1. Why L5 specifically? (Not L4 or L6)
2. What upstream signal tells L5.H1 which tokens are errors?
3. Why negative residual instead of zero-out attention?
4. Can we design explicit error-correction modules?
5. Do humans have analogous inhibitory attention?

Priority experiments (ranked):
[High] Survey L5-L8 for inhibitory heads → Generality of mechanism
[High] Track L5.H1 training development → When/how it emerges
[Med] Test composition with downstream → Circuit structure
[Med] Design hallucination reduction → Practical application
[Low] Cross-architecture study → Generalization

Synthesis (coherent mechanistic story):

**Error Correction via Residual Inhibition**

Transformers develop self-correction mechanisms during training without explicit supervision. In GPT-2 small, attention head 5.1 (L5.H1) implements semantic error correction through residual path inhibition.

**Mechanism**:
1. L5.H1 activates strongly on contexts where the model makes high-confidence semantic errors
2. The head's OV circuit produces a negative residual stream contribution
3. This inhibitory signal directly suppresses logits of confidently-wrong tokens
4. Error rate decreases by 23% when L5.H1 is functional

**Specificity**:
- Targets semantic errors (wrong facts), not syntax errors
- Only effective for high-confidence mistakes (prob > 0.6)
- Requires context length ≥ 5 tokens
- Operates through residual stream, not attention pattern changes

**Boundaries**:
- Emerges in mid-layers (L5-L8), not early layers
- Stronger in GPT-2 than GPT-3 (scaling effect)
- Occasionally over-corrects (5% rate)
- Improves adversarial robustness when ablated (surprising)

**Theoretical implications**:
- Transformers can implement "lateral inhibition" via negative residual contributions
- Error correction is a feedforward mechanism, not requiring recurrence
- Self-monitoring emerges from optimization, not explicit training signal
- Inhibitory circuits may be common but under-studied

**Open questions**:
1. How general is this pattern? (Other heads, models, architectures)
2. When/how does it develop during training?
3. What upstream signal provides error detection?
4. Can we enhance this for hallucination reduction?

**Next steps**: Survey L5-L8 heads for inhibitory patterns, track training dynamics, design intervention studies.

Research artifacts:
✓ Updated hypothesis (v2) documented
✓ Negative results recorded with value analysis
✓ Boundaries mapped (7 apply conditions, 5 break conditions)
✓ Next experiments prioritized (5 ranked)
✓ Coherent mechanistic story synthesized

→ Iteration complete, research advanced
→ Recommend: Execute priority experiments or formalize new hypothesis
```

## Iteration Components

**Update Hypothesis**:
- Which claims validated? (evidence strength)
- Which falsified? (what disproved them)
- Which refined? (how they changed)
- What new version number? (v1 → v2)

**Record Negative Results**:
- What approaches failed?
- Why did they fail?
- What does failure constrain?
- What value do negatives provide?

**Identify Boundaries**:
- Where does mechanism apply?
- Where does it break?
- What are edge cases?
- What boundary conditions matter?

**Generate Next Experiments**:
- What remains untested?
- What new questions emerged?
- What priority ranking?
- What resource requirements?

**Synthesize Understanding**:
- What is the coherent mechanistic story?
- What theoretical implications?
- What open questions?
- What next steps?

## Gate

**Cannot complete research cycle without**:
- [ ] Hypothesis updated based on evidence
- [ ] Negative results documented with value analysis
- [ ] Boundaries identified (apply/break conditions)
- [ ] Next experiments generated and prioritized
- [ ] Coherent mechanistic story synthesized

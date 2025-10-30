---
description: Plan causal interventions and competing explanations (Research Phase 3)
allowed-tools: Read, Write, TodoWrite
argument-hint: [--dry-run]
---

# Design Investigation Command

Execute Phase 3 research: decompose hypothesis, generate competing explanations, design critical experiments.

## What this does

1. **Decomposes hypothesis** into atomic testable claims
2. **Generates alternatives** (3-4 competing mechanistic explanations)
3. **Derives differential predictions** (how mechanisms differ observably)
4. **Designs critical experiments** (tests that discriminate between mechanisms)
5. **Plans controls** (rule out confounds, validate assumptions)

## Usage

```bash
# Auto-generate investigation plan
/design-investigation

# Dry-run (plan only, don't execute)
/design-investigation --dry-run

# Focus on specific claim
/design-investigation --claim "residual inhibition"
```

## Your Task

1. **Load investigation workflow**: Read `investigations/WORKFLOW.md`
2. **Decompose hypothesis**: Break into atomic testable claims
3. **Generate competing explanations**: Create 3-4 alternative mechanisms
4. **Derive differential predictions**: How do mechanisms differ?
5. **Design critical experiments**: Which tests discriminate?
6. **Plan controls**: Read `investigations/validation/sanity-checks.md`
7. **Review examples**: Read `investigations/examples/` for patterns
8. **Complete gate**: `investigations/GATE-DESIGN-COMPLETE.md`
9. **Report**: Atomic claims, competing mechanisms, experimental plan

## Expected Output

```
✓ Investigation designed

Hypothesis:
"Attention head 5.1 corrects errors via residual path inhibition"

Atomic testable claims:
1. L5.H1 activates on error-prone contexts
2. L5.H1 attention pattern targets error positions
3. L5.H1 OV matrix produces inhibitory signal
4. Inhibitory signal travels via residual stream
5. Signal suppresses incorrect next-token predictions

Competing explanations:

Mechanism A (Residual Inhibition - Our hypothesis):
- L5.H1 produces negative residual contribution
- Suppresses logits of incorrect tokens
- Effect: Error rate decreases

Mechanism B (Attention Redirection):
- L5.H1 redirects attention away from error sources
- Later heads receive corrected attention pattern
- Effect: Error rate decreases (different pathway)

Mechanism C (Contextual Disambiguation):
- L5.H1 refines context representation
- Enables downstream heads to predict correctly
- Effect: Error rate decreases (indirect mechanism)

Mechanism D (Null Hypothesis):
- L5.H1 correlates with error correction but doesn't cause it
- Other components perform correction
- Effect: Ablating L5.H1 has no impact

Differential predictions:

| Experiment | Mechanism A | Mechanism B | Mechanism C | Mechanism D |
|------------|-------------|-------------|-------------|-------------|
| Ablate L5.H1 | ↑ errors | ↑ errors | ↑ errors | No change |
| Patch L5.H1 activations | ↓ errors | ↓ errors | ↓ errors | No change |
| Check OV output sign | Negative | Positive/Mixed | Positive | N/A |
| Attention pattern change | Unchanged | Changed | Unchanged | N/A |
| Residual stream sign | Negative contribution | No negative | Positive | N/A |

Critical experiments:

Experiment 1: Ablation + Residual Analysis
- Ablate L5.H1, measure error rate change
- Analyze residual stream contribution sign
- **Discriminates**: A (negative residual) vs B/C (positive/neutral)

Experiment 2: Attention Pattern Tracking
- Track attention patterns before/after L5.H1
- Measure if downstream heads change targets
- **Discriminates**: B (pattern change) vs A/C (no change)

Experiment 3: OV Matrix Projection
- Project L5.H1 OV output onto token logits
- Check if inhibitory (negative) or excitatory (positive)
- **Discriminates**: A (inhibitory) vs C (excitatory)

Experiment 4: Causal Patching
- Patch L5.H1 activations from correct contexts
- Measure error correction strength
- **Discriminates**: A/B/C (effect) vs D (no effect)

Controls:

Sanity checks (investigations/validation/sanity-checks.md):
✓ Baseline error rate measured
✓ Random ablation control (ablate irrelevant head)
✓ Model still functional after intervention
✓ Error metric validated (not measurement artifact)

Robustness tests (investigations/validation/robustness-tests.md):
- Test across multiple error types (syntax, semantic, factual)
- Test across different model sizes
- Test on different datasets
- Verify effect size significance

→ Investigation design complete with 4 competing mechanisms
→ Recommend: Execute experiments to discriminate mechanisms
```

## Investigation Design Principles

**Required**:
- **Atomic claims**: Each claim testable independently
- **Competing explanations**: Minimum 3 alternatives + null hypothesis
- **Differential predictions**: Mechanisms must differ observably
- **Critical experiments**: Tests must discriminate between mechanisms
- **Controls**: Sanity checks and robustness validation

**Key principle**: Single hypothesis is not science. Generate alternatives.

## Gate

**Cannot proceed to execution without**:
- [ ] Hypothesis decomposed into atomic claims
- [ ] 3-4 competing mechanisms generated
- [ ] Differential predictions documented
- [ ] Critical experiments designed
- [ ] Controls planned (sanity checks + robustness)

---
description: Connect hypothesis to theoretical frameworks (Research Phase 2)
allowed-tools: Read, Write, TodoWrite
argument-hint: [--framework superposition|circuits|training-dynamics]
---

# Contextualize Command

Execute Phase 2 research: match hypothesis to theoretical frameworks, identify cross-disciplinary parallels.

## What this does

1. **Loads frameworks**: Read relevant theoretical foundations
2. **Matches hypothesis**: Connect to superposition, circuits, or training dynamics
3. **Identifies parallels**: Neuroscience, physics, philosophy connections
4. **Establishes context**: Position hypothesis within existing theory
5. **Generates framework predictions**: What theory predicts about this mechanism

## Usage

```bash
# Auto-select framework based on hypothesis
/contextualize

# Specify framework explicitly
/contextualize --framework superposition  # For features, sparsity, SAEs
/contextualize --framework circuits       # For attention, information flow
/contextualize --framework training-dynamics  # For emergence, phase transitions

# Review all frameworks
/contextualize --list-frameworks
```

## Your Task

1. **Load framework index**: Read `frameworks/INDEX.md`
2. **Select framework**: Choose appropriate theoretical foundation:
   - `frameworks/superposition.md` - Features, sparsity, dictionary learning
   - `frameworks/circuits.md` - Attention patterns, composition, algorithms
   - `frameworks/training-dynamics.md` - Learning phases, emergence, grokking
3. **Load cross-disciplinary parallels**: Read `frameworks/cross-disciplinary/`
4. **Connect hypothesis to theory**: Identify theoretical predictions
5. **Document framework context**: Record connections and predictions
6. **Complete gate**: `frameworks/GATE-CONTEXT-ESTABLISHED.md`
7. **Report**: Framework match, theoretical predictions, cross-field parallels

## Expected Output

```
✓ Framework context established

Hypothesis:
"Attention head 5.1 corrects errors via residual path inhibition"

Primary framework: circuits.md
**Why**: Attention-based mechanism, information flow pathway

Framework predictions:
1. **OV circuit analysis**: OV matrix should show inhibition pattern
2. **Path composition**: Residual stream shows negative contribution
3. **Attention pattern**: Head 5.1 attends to error-prone positions
4. **Ablation impact**: Removing head disrupts error correction

Cross-disciplinary parallels:

Neuroscience (frameworks/cross-disciplinary/neuroscience.md):
- **Predictive coding**: Error signals propagate backwards
- **Lateral inhibition**: Suppress competing predictions
- Connection: L5.H1 = lateral inhibition circuit for token predictions

Physics (frameworks/cross-disciplinary/physics.md):
- **Homeostasis**: System self-corrects toward equilibrium
- **Negative feedback**: Inhibition reduces error signal
- Connection: L5.H1 = negative feedback controller

Philosophy (frameworks/cross-disciplinary/philosophy.md):
- **Functionalism**: Same function, different implementations
- **Multiple realizability**: Other heads might implement same correction
- Connection: Error correction = functional property, L5.H1 = one realization

Theoretical implications:
✓ Hypothesis fits circuit composition framework
✓ Predicts specific attention patterns
✓ Suggests neuroscience-inspired mechanism (lateral inhibition)
✓ Opens questions: Are there other error-correction circuits?

→ Context established, ready for investigation design
→ Recommend: /design-investigation to plan causal experiments
```

## Framework Selection Guide

**Superposition & Polysemanticity** → Use when:
- Hypothesis involves features, sparsity, dictionary learning
- SAEs, toy models, interference patterns
- Concepts: Sparse coding, superposition geometry

**Circuit Composition & Analysis** → Use when:
- Hypothesis involves attention patterns, information flow
- Algorithmic structure, head composition
- Concepts: OV/QK matrices, path analysis

**Training Dynamics & Emergence** → Use when:
- Hypothesis involves learning phases, sudden capabilities
- Grokking, phase transitions, optimization
- Concepts: Loss landscapes, critical points

## Gate

**Cannot proceed to /design-investigation without**:
- [ ] Framework selected and loaded
- [ ] Hypothesis connected to theory
- [ ] Framework predictions documented
- [ ] Cross-disciplinary parallels identified

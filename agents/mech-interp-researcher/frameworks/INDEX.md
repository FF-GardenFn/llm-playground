# Framework Selection Guide

## Purpose
Match phenomenon to appropriate theoretical lens. Each framework provides concepts, predictions, and methods.

---

## By Phenomenon Type

### Feature Representation

**Superposition & Polysemanticity** → superposition.md
- When: Features, sparsity, dictionary learning, SAEs
- Questions: How do models represent more features than dimensions? Why polysemantic neurons?
- Key concepts: Toy models, interference, sparse coding, dictionary learning
- Methods: SAE analysis, activation statistics, feature clustering

**Distributed Representations** → superposition.md
- When: High-dimensional embeddings, semantic structure
- Questions: How is meaning distributed? What is geometric structure?
- Methods: PCA, t-SNE, probing, similarity analysis

### Information Flow

**Circuit Composition** → circuits.md
- When: Attention patterns, residual streams, algorithmic structure
- Questions: What algorithms implemented? How do components compose?
- Key concepts: OV/QK matrices, path analysis, composition, algorithmic primitives
- Methods: Attribution patching, attention analysis, path tracing

**Residual Stream Analysis** → circuits.md
- When: Information routing, skip connections, composition
- Questions: What information flows where? How do layers interact?
- Methods: Residual decomposition, path analysis, ablation

### Training Behavior

**Phase Transitions & Grokking** → training-dynamics.md
- When: Sudden capability emergence, training phases, loss curves
- Questions: Why sudden jumps? What triggers transitions? What is grokking?
- Key concepts: Phase transitions, critical points, loss landscape, optimization dynamics
- Methods: Training curve analysis, checkpoint interpolation, loss landscape visualization

**Optimization Dynamics** → training-dynamics.md
- When: Learning trajectories, gradient flow, convergence
- Questions: How does training evolve? What attracts to solutions?
- Methods: Gradient analysis, Hessian eigenvalues, loss landscape probing

---

## By Cross-Field Connection

### Neuroscience Parallels

**Sparse Coding** → cross-disciplinary/neuroscience.md
- Parallel: V1 simple cells → Transformer feature detectors
- Framework: Efficient coding hypothesis
- Prediction: Sparsity emerges from resource constraints

**Predictive Coding** → cross-disciplinary/neuroscience.md
- Parallel: Error signals in cortex → Error correction in transformers
- Framework: Hierarchical prediction
- Prediction: Layers predict next layer, errors propagate

**Hierarchical Processing** → cross-disciplinary/neuroscience.md
- Parallel: Visual hierarchy → Transformer layers
- Framework: Abstraction hierarchy
- Prediction: Early layers = simple features, late layers = complex concepts

### Physics Analogies

**Phase Transitions** → cross-disciplinary/physics.md
- Parallel: Water → ice → Training dynamics
- Framework: Statistical mechanics, critical phenomena
- Prediction: Sharp transitions at critical points, universal behavior

**Criticality** → cross-disciplinary/physics.md
- Parallel: Edge of chaos → Network expressiveness
- Framework: Self-organized criticality
- Prediction: Networks optimize to critical point for maximal information processing

**Statistical Mechanics** → cross-disciplinary/physics.md
- Parallel: Particle ensembles → Network ensembles
- Framework: Free energy, entropy, partition functions
- Prediction: Collective behavior from microscopic rules

### Philosophy of Mind

**Functionalism** → cross-disciplinary/philosophy.md
- Question: Does implementation matter?
- Framework: Multiple realizability
- Prediction: Same function, different circuits

**Emergence vs Reduction** → cross-disciplinary/philosophy.md
- Question: Are high-level capabilities reducible to circuits?
- Framework: Strong vs weak emergence
- Prediction: Some properties may be irreducibly high-level

---

## Framework Selection Decision Tree

```
Phenomenon involves...

└─ FEATURES/REPRESENTATIONS
   ├─ More features than dimensions → superposition.md
   ├─ Sparse activations → superposition.md
   ├─ Dictionary learning → superposition.md
   └─ Geometric structure → superposition.md

└─ INFORMATION FLOW
   ├─ Attention patterns → circuits.md
   ├─ Residual connections → circuits.md
   ├─ Multi-step algorithms → circuits.md
   └─ Component composition → circuits.md

└─ TRAINING/LEARNING
   ├─ Sudden capability emergence → training-dynamics.md
   ├─ Phase transitions → training-dynamics.md
   ├─ Grokking → training-dynamics.md
   └─ Optimization trajectory → training-dynamics.md

└─ CROSS-FIELD CONNECTION
   ├─ Neuroscience parallel → cross-disciplinary/neuroscience.md
   ├─ Physics analogy → cross-disciplinary/physics.md
   └─ Philosophical question → cross-disciplinary/philosophy.md
```

---

## Using Multiple Frameworks

**Most phenomena require multiple lenses:**

Example: Induction heads
- Circuit perspective: Two-layer composition (circuits.md)
- Training perspective: Emerge via phase transition (training-dynamics.md)
- Neuroscience parallel: Episodic memory circuits (neuroscience.md)

**Strategy:**
1. Start with primary framework (what is core phenomenon?)
2. Add cross-field perspectives (what parallels exist?)
3. Synthesize insights (what do multiple views reveal?)

---

## Quick Reference Table

| Phenomenon | Primary Framework | Secondary Framework | Key Concepts |
|-----------|------------------|-------------------|-------------|
| SAE features | Superposition | Neuroscience (sparse coding) | Dictionary learning, sparsity |
| Induction heads | Circuits | Training dynamics | Composition, phase transition |
| Grokking | Training dynamics | Physics (phase transitions) | Critical points, loss landscape |
| Attention patterns | Circuits | - | QK/OV matrices, algorithmic primitives |
| Feature polysemanticity | Superposition | - | Interference, resource constraints |
| Training phases | Training dynamics | Physics (criticality) | Phase transitions, optimization |
| Error correction | Circuits | Neuroscience (predictive coding) | Residual paths, prediction errors |

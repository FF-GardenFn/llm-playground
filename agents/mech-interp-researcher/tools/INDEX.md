# Tool Catalog

## Purpose
Tools organized by research purpose. Each tool family serves specific investigation needs.

---

## Quick Selection Guide

```
Research Question → Tool Family → Specific Tools

"What causes X?" → Causal Interventions → Ablation, patching, steering
"What represents Y?" → Activation Analysis → Logit lens, PCA, clustering
"How does algorithm Z work?" → Circuit Analysis → Attribution patching, path tracing
"What does this look like?" → Visualization → Attention plots, activation maps
```

---

## Tool Families

### 1. Causal Interventions → causal-interventions.md

**Purpose:** Test causal hypotheses by intervening on activations

**When to use:**
- Testing "Component X causes Y"
- Isolating component contributions
- Validating necessity/sufficiency

**Tools:**
- **Ablation:** Zero component, measure effect
- **Activation Patching:** Replace activations from context A → B
- **Steering Vectors:** Add/amplify specific directions
- **Mean Ablation:** Replace with dataset mean

**Key questions answered:**
- Is component X necessary for behavior Y?
- Is component X sufficient for behavior Y?
- What information does component X contribute?

---

### 2. Activation Analysis → activation-analysis.md

**Purpose:** Understand what activations represent

**When to use:**
- Understanding feature representations
- Finding structure in high-dimensional space
- Detecting feature polysemanticity

**Tools:**
- **Logit Lens:** Decode activations to vocabulary
- **PCA/t-SNE:** Visualize activation structure
- **Clustering:** Group similar activations
- **Dimensionality Reduction:** Find key dimensions
- **Sparse Autoencoders (SAEs):** Learn sparse feature dictionaries

**Key questions answered:**
- What do these activations represent?
- What is the geometric structure?
- Are features sparse or distributed?

---

### 3. Circuit Analysis → circuit-analysis.md

**Purpose:** Discover and analyze algorithmic circuits

**When to use:**
- Finding how algorithms implemented
- Tracing information flow
- Understanding composition

**Tools:**
- **Attribution Patching:** Identify critical paths
- **Path Tracing:** Follow information through network
- **Attention Pattern Analysis:** Understand QK circuits
- **OV Circuit Analysis:** Understand value copying
- **Residual Decomposition:** Separate component contributions

**Key questions answered:**
- What circuit implements algorithm X?
- How do components compose?
- Where does information flow?

---

### 4. Visualization → visualization.md

**Purpose:** Build intuition and communicate findings

**When to use:**
- Exploring patterns
- Communicating results
- Generating hypotheses

**Tools:**
- **Attention Heatmaps:** Visualize attention patterns
- **Activation Maps:** Show neuron activations
- **Feature Visualization:** Optimize inputs for neurons
- **Circuit Diagrams:** Illustrate information flow
- **Dimensionality Reduction Plots:** Show structure

**Key questions answered:**
- What patterns exist?
- How can I communicate this?
- What should I investigate next?

---

## Selection Decision Tree

```
Start with question:

"Does X cause Y?"
└─→ Causal Interventions
    ├─ Start: Ablation (simple, interpretable)
    ├─ Refine: Activation patching (isolate specific information)
    └─ Advanced: Steering vectors (test sufficiency)

"What does X represent?"
└─→ Activation Analysis
    ├─ Quick: Logit lens (decode to tokens)
    ├─ Structure: PCA/t-SNE (find geometry)
    └─ Features: SAEs (learn sparse dictionary)

"How does algorithm X work?"
└─→ Circuit Analysis
    ├─ Find circuit: Attribution patching
    ├─ Understand mechanism: Attention/OV analysis
    └─ Trace information: Path analysis

"What does this look like?"
└─→ Visualization
    ├─ Attention: Heatmaps
    ├─ Activations: Activation maps
    └─ Features: Feature visualization
```

---

## Typical Investigation Tool Sequence

**1. Exploration Phase:**
```
Visualization → Activation Analysis → Hypothesis Formation
(Build intuition)   (Find structure)    (Generate claims)
```

**2. Hypothesis Testing Phase:**
```
Causal Interventions → Circuit Analysis → Validation
(Test causation)        (Understand mechanism)  (Confirm findings)
```

**3. Communication Phase:**
```
Visualization → Documentation
(Show findings)   (Explain results)
```

---

## Tool Combinations

**Powerful combinations for specific questions:**

### "What circuit implements X?"
1. Attention visualization (find suspicious patterns)
2. Ablation (test necessity)
3. Attribution patching (isolate path)
4. Circuit diagram (communicate finding)

### "What features does neuron represent?"
1. Activation analysis (find structure)
2. Logit lens (decode to vocabulary)
3. SAE (find sparse features)
4. Feature visualization (optimize inputs)

### "Does component X cause behavior Y?"
1. Ablation (test necessity)
2. Activation patching (test sufficiency)
3. Attention analysis (understand mechanism)
4. Controls (rule out confounds)

---

## Common Pitfalls

**Pitfall 1: Ablation without controls**
- Solution: Always ablate random components as baseline

**Pitfall 2: Confusing correlation with causation**
- Solution: Use activation patching, not just correlation

**Pitfall 3: Over-interpreting visualizations**
- Solution: Confirm patterns with quantitative tests

**Pitfall 4: Single method conclusions**
- Solution: Use multiple complementary methods

---

## For Detailed Tool Usage

Each tool family has detailed documentation:
- causal-interventions.md - Ablation, patching, steering methods
- activation-analysis.md - Representation analysis techniques
- circuit-analysis.md - Information flow tracing methods
- visualization.md - Plotting and communication tools

SKILLS.md provides implementation details and code examples.

# Foundational Papers in Mechanistic Interpretability

## Core Papers That Established the Field

### 1. "Zoom In: An Introduction to Circuits" (2020)
**Authors**: Chris Olah et al. (Anthropic)
**Key Contribution**: Introduced the circuits framework for understanding neural networks.

**Core Ideas**:
- Features as fundamental units
- Circuits as connected features
- Universality of certain circuits
- Mechanistic understanding possible

**Impact**: Launched modern mechanistic interpretability as distinct from feature visualization.

### 2. "A Mathematical Framework for Transformer Circuits" (2021)
**Authors**: Anthropic Team
**Key Contribution**: Mathematical decomposition of transformer computations.

**Core Ideas**:
- Attention as information routing
- MLPs as key-value memories
- Residual stream as communication channel
- Composition through layers

**Methods Introduced**:
- Eigenvalue analysis of attention
- Path decomposition
- Virtual weights concept

### 3. "In-context Learning and Induction Heads" (2022)
**Authors**: Anthropic Team
**Key Contribution**: First mechanistic explanation of in-context learning.

**Discoveries**:
- Induction heads implement copy operations
- Two-layer circuit composition
- Phase transition during training
- Mechanism for few-shot learning

### 4. "Toy Models of Superposition" (2022)
**Authors**: Anthropic Team
**Key Contribution**: Understanding feature superposition.

**Key Insights**:
- Features > dimensions via superposition
- Importance-sparsity tradeoff
- Interference patterns predictable
- Recovery via sparse coding

---

## Methodological Foundations

### 5. "Feature Visualization" (2017)
**Authors**: Chris Olah et al. (Google Brain)
**Foundation**: Techniques for understanding what neurons detect.

**Methods**:
- Activation maximization
- Dataset examples
- Synthetic examples
- Channel interpolation

### 6. "The Building Blocks of Interpretability" (2018)
**Authors**: Chris Olah et al.
**Foundation**: Composing interpretability techniques.

**Contributions**:
- Spatial activation atlases
- Channel attribution
- Neuron groups
- Interactive exploration

### 7. "Visualizing and Understanding Convolutional Networks" (2013)
**Authors**: Zeiler & Fergus
**Foundation**: Early systematic investigation of learned features.

**Methods**:
- Deconvolution approach
- Occlusion experiments
- Feature evolution during training

---

## Transformer-Specific Foundations

### 8. "Attention Is All You Need" (2017)
**Authors**: Vaswani et al.
**Foundation**: The transformer architecture itself.

**Relevance to Mech Interp**:
- Attention mechanism structure
- Information flow design
- Positional encoding role
- Layer normalization effects

### 9. "BERT: Pre-training of Deep Bidirectional Transformers" (2018)
**Authors**: Devlin et al.
**Foundation**: Modern language model architecture.

**Interpretability Implications**:
- Bidirectional attention patterns
- Layer specialization
- Feature emergence during pre-training

### 10. "GPT-2: Language Models are Unsupervised Multitask Learners" (2019)
**Authors**: OpenAI Team
**Foundation**: Autoregressive language modeling at scale.

---

## Causal Analysis Foundations

### 11. "Causal Scrubbing" (2023)
**Authors**: Redwood Research
**Contribution**: Rigorous causal testing of interpretability hypotheses.

**Method**:
- Scramble non-hypothesized components
- Preserve hypothesized structure
- Behavior should be maintained

### 12. "Path Patching" (2023)
**Authors**: Various
**Contribution**: Tracing causal paths through networks.

**Approach**:
- Intervene on specific paths
- Measure contribution
- Build causal graphs

---

## Theoretical Foundations

### 13. "Neural Tangent Kernel" (2018)
**Authors**: Jacot et al.
**Theory**: Infinite-width limit behavior of neural networks.

**Relevance**:
- Training dynamics understanding
- Feature learning theory
- Convergence properties

### 14. "The Lottery Ticket Hypothesis" (2018)
**Authors**: Frankle & Carbin
**Theory**: Sparse subnetworks that train effectively.

**Implications**:
- Circuit discovery motivation
- Pruning as interpretability tool
- Minimal sufficient networks

### 15. "Deep Learning Theory" (2021)
**Authors**: Roberts, Yaida, Hanin
**Theory**: Comprehensive theoretical framework.

**Coverage**:
- Initialization effects
- Training dynamics
- Representation learning
- Generalization bounds

---

## Critical Papers

### 16. "The Mythos of Model Interpretability" (2016)
**Authors**: Zachary Lipton
**Critique**: Challenges in defining interpretability.

**Important Points**:
- Multiple definitions of interpretability
- Tradeoffs between goals
- Need for rigor in claims

### 17. "Attention is Not Explanation" (2019)
**Authors**: Jain & Wallace
**Critique**: Attention weights don't necessarily explain decisions.

**Key Arguments**:
- Attention can be manipulated
- Multiple attention patterns → same output
- Need for causal analysis

---

## Reading Order for Beginners

1. **Start with intuition**: "Zoom In: An Introduction to Circuits"
2. **Understand transformers**: "A Mathematical Framework for Transformer Circuits"
3. **See concrete example**: "In-context Learning and Induction Heads"
4. **Grasp superposition**: "Toy Models of Superposition"
5. **Learn methods**: "Causal Scrubbing" or "Path Patching"
6. **Understand limitations**: "Attention is Not Explanation"

---

## Key Venues

### Conferences
- NeurIPS (Neural Information Processing Systems)
- ICML (International Conference on Machine Learning)
- ICLR (International Conference on Learning Representations)
- ACL (Association for Computational Linguistics)

### Workshops
- Mechanistic Interpretability Workshop (NeurIPS)
- XAI Workshop (Various conferences)
- Neural Circuit Reconstruction

### Journals
- Distill.pub (Archived but influential)
- TMLR (Transactions on Machine Learning Research)
- Nature Machine Intelligence

---

## Research Groups

1. **Anthropic** - Circuits team, fundamental research
2. **Redwood Research** - Causal methods, rigorous testing
3. **DeepMind** - Mechanistic analysis team
4. **EleutherAI** - Open source interpretability
5. **MATS** - Training programs and research

---

*These papers form the foundation of mechanistic interpretability. Understanding them provides the context for all current work.*
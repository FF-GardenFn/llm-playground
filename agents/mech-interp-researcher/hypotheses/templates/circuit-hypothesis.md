# Circuit Hypothesis Template

**Hypothesis Type**: Circuit Implementation
**Use When**: Proposing specific computational circuits within the model

---

## Circuit Identification

**Circuit Name**: [Descriptive name, e.g., "Copy Suppression Circuit"]

**Primary Components**:
- Layer [X], Head [Y]: [Specific function]
- Layer [A], Head [B]: [Specific function]
- MLP Layer [M]: [Specific function if involved]
- Residual connections: [Which ones matter]

**Circuit Boundaries**:
- Input entry point: Layer [?], Position [?]
- Output exit point: Layer [?], Position [?]
- Information flow: [Describe path through model]

---

## Computational Function

**What This Circuit Computes**:
[Specific transformation, e.g., "Detects repeated tokens and suppresses copying"]

**Algorithmic Description**:
1. Step 1: [e.g., "Head 2.3 attends to previous token"]
2. Step 2: [e.g., "Head 2.5 compares current and previous"]
3. Step 3: [e.g., "MLP amplifies difference signal"]
4. Step 4: [e.g., "Head 4.1 gates output based on similarity"]

**Mathematical Formulation** (if applicable):
```
Output = f(g(Input, Attention_2.3), MLP_3(Comparison_2.5))
```

---

## Observable Signatures

**Activation Patterns**:
- When input contains [X], expect activation in [component]
- When input lacks [Y], expect no activation in [component]
- Correlation between [pattern] and [activation]

**Attention Patterns**:
- Head [X.Y] should attend to [positions/tokens]
- Attention strength should correlate with [feature]
- Cross-layer attention flow: [describe pattern]

**Information Flow**:
- Information enters via: [pathway]
- Processing occurs in: [components]
- Results propagate through: [pathway]

---

## Testable Predictions

**Ablation Experiments**:
- Remove head [X.Y] → [Expected effect]
- Zero out connection [A→B] → [Expected effect]
- Replace MLP [M] with identity → [Expected effect]

**Activation Interventions**:
- Force activate [component] → [Expected behavior]
- Suppress [component] → [Expected behavior]
- Redirect attention of [head] → [Expected behavior]

**Behavioral Predictions**:
- On input type [A]: [Specific output prediction]
- On input type [B]: [Different output prediction]
- Edge case [C]: [Boundary behavior]

---

## Distinguishing Features

**What makes this circuit hypothesis unique**:
- Different from [alternative circuit] because: [specific difference]
- Not explained by [simpler mechanism] because: [specific reason]
- Requires all components because: [ablation evidence]

**Critical tests to distinguish from alternatives**:
1. Test [X] to differentiate from [alternative 1]
2. Test [Y] to differentiate from [alternative 2]
3. Test [Z] to rule out [simpler explanation]

---

## Falsification Criteria

**This hypothesis is FALSE if**:
- [ ] Ablating [component] has no effect on [behavior]
- [ ] [Component] activates without [expected input]
- [ ] Circuit operates successfully with [component] removed
- [ ] Different components show [pattern] instead
- [ ] Behavior persists when entire circuit ablated

**Specific experiments that would falsify**:
1. [Concrete experiment design]
2. [Concrete experiment design]
3. [Concrete experiment design]

---

## Related Circuits

**Upstream dependencies**: [Circuits that feed into this one]
**Downstream effects**: [Circuits affected by this one's output]
**Parallel circuits**: [Alternative pathways for same function]
**Redundancy**: [Backup mechanisms if this circuit fails]

---

## Implementation Evidence

**Training Dynamics**:
- When does circuit form during training?
- Prerequisites for circuit emergence?
- Stable across different training runs?

**Model Scale Dependencies**:
- Minimum model size for circuit?
- How circuit changes with scale?
- Conservation across architectures?

---

## Notes

[Additional observations, uncertainties, or context]

---

*Remember: A circuit hypothesis must specify exact components and their interactions, not vague "the model does X" claims.*
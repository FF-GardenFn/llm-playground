# Example Investigation: Induction Head Mechanisms

## Hypothesis

**Primary Claim**: Induction heads implement a specific algorithm for in-context pattern completion via a two-layer circuit.

**Mechanistic Specificity**:
- Layer N-1: Previous token head (attends to previous token positions)
- Layer N: Induction head (copies patterns via K-Q matching)
- Composition through residual stream

---

## Investigation Design

### Phase 1: Circuit Components

**Operational Definition**:
```python
# Induction heads perform: [A][B]...[A] → predict [B]
# Two-layer circuit:
# 1. Previous token head: Attend to position-1
# 2. Induction head: Match current to previous contexts

def identify_induction_heads(model):
    prev_token_heads = find_previous_token_heads()
    induction_heads = find_pattern_copying_heads()
    return prev_token_heads, induction_heads
```

**Key Components**:
- Previous token information routing
- Pattern matching via QK circuit
- Value copying for prediction

### Phase 2: Alternative Hypotheses

**Alternative 1**: N-gram Memorization
- Simple memorization of sequences
- Test: Novel patterns should fail

**Alternative 2**: General Attention
- Any attention head can copy
- Test: Specific heads not required

**Alternative 3**: Single-Layer Implementation
- No composition needed
- Test: Circuit works without previous layer

### Phase 3: Experimental Design

```python
class InductionHeadExperiment:
    def __init__(self):
        self.test_sequences = self.generate_test_patterns()
        self.controls = self.generate_controls()

    def test_pattern_completion(self):
        # Standard induction: [A][B][C]...[A] → [B]
        # Test completion accuracy
        pass

    def test_circuit_composition(self):
        # Ablate previous token head
        # Measure induction head performance
        pass

    def test_mechanism_specificity(self):
        # Perturb QK circuit
        # Measure pattern matching degradation
        pass
```

---

## Pattern Types and Tests

### Basic Induction Patterns

**Repeated Sequences**:
```
Input: "The cat sat on the mat. The cat"
Expected: High probability for "sat"
Mechanism: Match "The cat" context
```

**Abstract Patterns**:
```
Input: "1→2, 3→4, 5→6, 1→"
Expected: Predict "2"
Mechanism: Abstract pattern matching
```

### Control Patterns

**No Repetition**:
```
Input: Random sequence without repeats
Expected: No induction behavior
Result: Heads don't activate strongly
```

**Disrupted Pattern**:
```
Input: "A B C... A X" (X ≠ B)
Expected: Still predicts B
Result: Shows true pattern matching vs memorization
```

---

## Mechanistic Analysis

### Information Flow Tracking

```python
def track_information_flow():
    # Step 1: Previous token head creates positional offset
    prev_token_attention = get_attention_pattern(prev_head)
    assert peak_at_offset(prev_token_attention, offset=-1)

    # Step 2: Information written to residual stream
    residual_update = get_residual_stream_update(prev_head)

    # Step 3: Induction head uses this for K-composition
    k_composition = analyze_key_composition(induction_head)
    assert uses_previous_layer_info(k_composition)

    # Step 4: QK matching finds pattern
    qk_pattern = compute_qk_scores(induction_head)
    assert high_scores_at_pattern_matches(qk_pattern)
```

### Ablation Studies

**Previous Token Head Ablation**:
```python
results = {
    "baseline_accuracy": 0.85,
    "prev_head_ablated": 0.45,  # Major drop
    "random_head_ablated": 0.83,  # Minimal effect
    "conclusion": "Previous token head critical"
}
```

**Induction Head Ablation**:
```python
results = {
    "pattern_completion": {
        "baseline": 0.90,
        "ablated": 0.30
    },
    "in_context_learning": {
        "baseline": 0.75,
        "ablated": 0.35
    }
}
```

### Causal Interventions

**Force Pattern Match**:
```python
# Artificially set QK scores high for wrong positions
intervention = force_high_qk_scores(wrong_positions)
result = "Model copies from forced positions"  # Causal evidence
```

**Destroy K-Composition**:
```python
# Randomize K vectors while preserving norms
intervention = randomize_keys_preserve_norm()
result = "Pattern matching fails completely"
```

---

## Developmental Analysis

### Training Dynamics

```python
def analyze_emergence_during_training():
    checkpoints = load_training_checkpoints()

    for epoch, checkpoint in checkpoints.items():
        prev_heads = identify_previous_token_heads(checkpoint)
        induction = identify_induction_heads(checkpoint)

        results[epoch] = {
            "prev_heads_formed": len(prev_heads) > 0,
            "induction_heads_formed": len(induction) > 0,
            "composition_strength": measure_composition(checkpoint)
        }

    # Key finding: Previous token heads form BEFORE induction heads
    # Suggests developmental dependency
```

### Phase Transition

**Sudden Emergence**:
```
Epoch 1-10: No induction behavior
Epoch 11: Previous token heads appear
Epoch 12-13: Transitional behavior
Epoch 14: Full induction heads emerge
Epoch 15+: Refinement and strengthening
```

---

## Validation Experiments

### Cross-Model Validation

```python
models_tested = [
    "GPT-2-small": {"has_induction": True, "layer": 5},
    "GPT-2-medium": {"has_induction": True, "layer": 6},
    "GPT-2-large": {"has_induction": True, "layer": 8},
    "Random-Init": {"has_induction": False}
]
```

### Synthetic Task Validation

**Pure Induction Task**:
```python
# Create dataset with ONLY induction patterns
synthetic_data = create_pure_induction_dataset()
specialized_model = train_minimal_model(synthetic_data)

# Result: Model develops induction heads faster
# Confirms these heads specifically for this computation
```

### Necessity Test

**Can model work without induction?**
```python
# Train model with induction heads surgically prevented
constrained_model = train_with_ablation(prevent_induction=True)

results = {
    "in_context_learning": "Severely impaired",
    "few_shot_tasks": "Near random performance",
    "conclusion": "Induction heads necessary for ICL"
}
```

---

## Quantitative Metrics

### Induction Score

```python
def compute_induction_score(head):
    """
    Measure how well head performs induction
    Score = P(correct | pattern) - P(correct | random)
    """
    pattern_acc = test_on_induction_patterns(head)
    random_acc = test_on_random_sequences(head)
    return pattern_acc - random_acc
```

### Composition Strength

```python
def measure_composition_strength():
    """
    Quantify how much induction depends on previous layer
    """
    full_circuit = baseline_performance()
    broken_circuit = ablated_performance()
    return (full_circuit - broken_circuit) / full_circuit
```

---

## Implications

### For In-Context Learning
1. Induction heads are mechanism for ICL
2. Quality of ICL depends on induction strength
3. Prompt engineering can leverage this circuit

### For Model Behavior
1. Repetition bias comes from strong induction
2. Pattern completion is circuit-based
3. Can predict where model will copy from

### For Interpretability
1. Clear example of circuit composition
2. Shows importance of multi-layer analysis
3. Demonstrates causal understanding possible

---

## Failure Modes

### When Induction Fails
1. **No clear pattern**: Random sequences
2. **Conflicting patterns**: Multiple valid completions
3. **Out-of-distribution**: Patterns unlike training
4. **Adversarial**: Deliberately broken patterns

### Misuse of Induction
1. **Over-copying**: Repeats when shouldn't
2. **Wrong source**: Copies from wrong pattern match
3. **Hallucination**: Invents patterns that don't exist

---

## Engineering Applications

### Enhancing Induction
```python
# Surgical edit to strengthen induction
enhance_qk_circuit(induction_head, scale=1.5)
# Result: Better few-shot learning
```

### Controlling Induction
```python
# Add attention mask to prevent unwanted copying
mask_induction_sources(forbidden_positions)
# Result: Reduced repetition/plagiarism
```

### Debugging with Induction
```python
# Monitor induction heads for copying behavior
track_copying_sources(induction_heads)
# Use to detect when model copies training data
```

---

## Reproducibility Protocol

1. **Model**: GPT-2 small, checkpoint at step 50K
2. **Data**: OpenWebText, first 10M tokens
3. **Metrics**: Induction score, composition strength
4. **Code**: [Repository link with full implementation]
5. **Compute**: Single GPU, ~2 hours for full analysis

---

*This investigation exemplifies moving from "model does in-context learning" to "Layer 5 Head 5 implements pattern matching via QK-circuit composition with Layer 4 Head 8's previous-token information."*
# Skills: Mechanistic Interpretability Research

## Tool Usage Patterns

The mechanistic interpretability researcher uses tools in specific patterns to move from correlation to causation, from behavior to mechanism.

---

## Core Tool Workflows

### Investigation Setup

```python
# Standard investigation initialization
import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer

# Load model for investigation
model = AutoModel.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Set up hooks for activation capture
activations = {}
def capture_activation(name):
    def hook(model, input, output):
        activations[name] = output.detach()
    return hook

# Register hooks on components of interest
for layer_idx in range(model.config.n_layer):
    layer = model.transformer.h[layer_idx]
    layer.attn.register_forward_hook(
        capture_activation(f"layer_{layer_idx}_attn")
    )
    layer.mlp.register_forward_hook(
        capture_activation(f"layer_{layer_idx}_mlp")
    )
```

### Hypothesis Testing Pipeline

```python
def test_mechanistic_hypothesis(hypothesis):
    """
    Standard pipeline for testing any mechanistic hypothesis
    """
    # 1. Formalize hypothesis
    components = hypothesis['components']
    mechanism = hypothesis['mechanism']
    predictions = hypothesis['predictions']

    # 2. Generate test data
    test_data = create_test_cases(predictions)

    # 3. Capture activations
    results = {}
    for test_case in test_data:
        output = model(test_case)
        results[test_case] = {
            'output': output,
            'activations': activations.copy()
        }

    # 4. Run interventions
    intervention_results = {}
    for component in components:
        # Ablation
        ablated = ablate_component(model, component)
        intervention_results[f'ablate_{component}'] = run_model(ablated, test_data)

        # Activation
        activated = force_activate(model, component)
        intervention_results[f'activate_{component}'] = run_model(activated, test_data)

    # 5. Statistical analysis
    statistics = analyze_results(results, intervention_results, predictions)

    # 6. Generate report
    return {
        'hypothesis_confirmed': statistics['p_value'] < 0.05,
        'effect_size': statistics['effect_size'],
        'confidence_interval': statistics['ci'],
        'intervention_results': intervention_results
    }
```

---

## Specialized Tool Patterns

### Pattern 1: Circuit Discovery

```python
def discover_circuit(behavior):
    """
    Find minimal circuit implementing behavior
    """
    # Start with full model
    components = get_all_components(model)

    # Iterative ablation
    essential_components = []
    for component in components:
        # Ablate and test
        ablated = ablate(model, component)
        performance = test_behavior(ablated, behavior)

        if performance < threshold:
            essential_components.append(component)

    # Test sufficiency
    minimal_model = keep_only(model, essential_components)
    sufficient = test_behavior(minimal_model, behavior) > threshold

    return {
        'essential_components': essential_components,
        'sufficient': sufficient
    }
```

### Pattern 2: Superposition Analysis

```python
def analyze_superposition(layer_activations):
    """
    Detect and quantify superposition
    """
    from sklearn.decomposition import DictionaryLearning

    # Learn overcomplete dictionary
    dict_learning = DictionaryLearning(
        n_components=10 * layer_activations.shape[1],
        alpha=1.0,
        max_iter=1000
    )
    dictionary = dict_learning.fit_transform(layer_activations)

    # Measure superposition metrics
    metrics = {
        'n_features': count_interpretable_features(dictionary),
        'sparsity': measure_sparsity(dictionary),
        'interference': compute_interference_matrix(dictionary)
    }

    return dictionary, metrics
```

### Pattern 3: Attention Pattern Analysis

```python
def analyze_attention_patterns(model, input_ids):
    """
    Systematic attention analysis
    """
    # Get attention weights
    outputs = model(input_ids, output_attentions=True)
    attention_weights = outputs.attentions  # List of tensors

    patterns = {}
    for layer_idx, layer_attention in enumerate(attention_weights):
        for head_idx in range(layer_attention.shape[1]):
            head_attention = layer_attention[0, head_idx]

            # Classify pattern
            pattern_type = classify_attention_pattern(head_attention)

            # Measure properties
            patterns[f"L{layer_idx}H{head_idx}"] = {
                'type': pattern_type,
                'entropy': compute_entropy(head_attention),
                'max_attention': head_attention.max().item(),
                'sparsity': (head_attention > 0.1).float().mean().item()
            }

    return patterns
```

---

## Tool Composition Patterns

### Sequential Composition

```python
# First discover circuit
circuit = discover_circuit(behavior="in_context_learning")

# Then test causal role
causal_results = {}
for component in circuit['essential_components']:
    causal_results[component] = test_causality(model, component, behavior)

# Finally test robustness
robustness = test_circuit_robustness(circuit, variations)
```

### Parallel Analysis

```python
# Run multiple analyses simultaneously
from concurrent.futures import ThreadPoolExecutor

analyses = [
    ("attention", analyze_attention_patterns),
    ("superposition", analyze_superposition),
    ("circuits", discover_circuit),
    ("causal", run_causal_analysis)
]

with ThreadPoolExecutor() as executor:
    futures = {
        name: executor.submit(fn, model, data)
        for name, fn in analyses
    }

results = {
    name: future.result()
    for name, future in futures.items()
}
```

### Hierarchical Investigation

```python
# Top-down investigation
def investigate_capability(capability):
    # High-level behavior test
    behavior = test_capability_presence(model, capability)

    if behavior['present']:
        # Find implementing components
        components = locate_components(model, capability)

        # For each component, understand mechanism
        mechanisms = {}
        for component in components:
            mechanism = understand_mechanism(model, component)
            mechanisms[component] = mechanism

        # Test interactions
        interactions = test_component_interactions(components)

    return {
        'behavior': behavior,
        'components': components,
        'mechanisms': mechanisms,
        'interactions': interactions
    }
```

---

## Validation Tool Patterns

### Sanity Check Suite

```python
def run_sanity_checks(method, model):
    """
    Standard sanity checks for any method
    """
    checks = {
        'random_baseline': test_against_random(method, model),
        'shuffle_control': test_with_shuffled_input(method, model),
        'ablation_effect': test_ablation_has_effect(method, model),
        'numerical_stability': test_numerical_stability(method),
        'reproducibility': test_with_different_seeds(method, model)
    }

    passed = all(check['passed'] for check in checks.values())
    return passed, checks
```

### Robustness Testing

```python
def test_robustness(finding, variations):
    """
    Test if finding is robust
    """
    robustness_scores = {}

    for variation_name, variation in variations.items():
        # Apply variation
        modified_setup = apply_variation(original_setup, variation)

        # Retest finding
        result = test_finding(modified_setup)

        # Measure preservation
        robustness_scores[variation_name] = measure_similarity(
            original_result,
            result
        )

    overall_robust = np.mean(list(robustness_scores.values())) > 0.7
    return overall_robust, robustness_scores
```

---

## Best Practices

### Tool Selection

**For Causal Claims**:
- Primary: Activation patching
- Secondary: Ablation studies
- Validation: Path patching

**For Feature Discovery**:
- Primary: Sparse dictionary learning
- Secondary: Probing classifiers
- Validation: Intervention on learned features

**For Circuit Identification**:
- Primary: Iterative ablation
- Secondary: Activation analysis
- Validation: Sufficiency testing

### Quality Control

1. **Always run sanity checks first**
2. **Test on multiple random seeds**
3. **Validate on held-out data**
4. **Check robustness across models**
5. **Document all parameters**

### Performance Tips

1. **Cache activations** when running multiple analyses
2. **Use batched operations** where possible
3. **Profile code** to find bottlenecks
4. **Parallelize** independent analyses
5. **Save intermediate results** for debugging

---

## Tool Integration Examples

### Complete Investigation Script

```python
def complete_investigation(hypothesis):
    """
    Full investigation pipeline
    """
    # Setup
    model = load_model()
    data = prepare_data()

    # Phase 1: Formalization
    formalized = formalize_hypothesis(hypothesis)

    # Phase 2: Alternative generation
    alternatives = generate_alternatives(formalized)

    # Phase 3: Experimental design
    experiments = design_experiments(formalized, alternatives)

    # Phase 4: Execution
    results = {}
    for exp_name, experiment in experiments.items():
        # Run with validation
        passed, checks = run_sanity_checks(experiment, model)
        if passed:
            results[exp_name] = execute_experiment(experiment, model, data)
        else:
            results[exp_name] = {'error': 'Failed sanity checks', 'checks': checks}

    # Phase 5: Analysis
    analysis = analyze_all_results(results, formalized, alternatives)

    # Phase 6: Robustness
    robust, robustness_details = test_robustness(
        analysis['main_finding'],
        standard_variations
    )

    # Phase 7: Report
    report = generate_report(
        hypothesis=formalized,
        alternatives=alternatives,
        results=results,
        analysis=analysis,
        robust=robust,
        robustness=robustness_details
    )

    return report
```

---

## Troubleshooting Common Issues

### Issue: Activations are NaN
```python
# Check for numerical issues
torch.autograd.set_detect_anomaly(True)
# Use gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
```

### Issue: Can't distinguish alternatives
```python
# Need more specific predictions
# Increase sample size
# Design orthogonal interventions
```

### Issue: Results don't replicate
```python
# Set all random seeds
torch.manual_seed(42)
np.random.seed(42)
# Check for non-deterministic operations
torch.use_deterministic_algorithms(True)
```

---

*These tool patterns enable systematic investigation of mechanistic hypotheses, moving from speculation to rigorous understanding.*
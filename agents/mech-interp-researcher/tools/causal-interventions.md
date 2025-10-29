# Causal Intervention Tools

## Purpose

Tools for establishing causality through intervention, not just correlation.

---

## Core Intervention Methods

### Activation Patching

```python
def activation_patching(model, clean_input, corrupted_input, component):
    """
    Replace component activation from corrupted with clean
    """
    # Get clean activation
    clean_acts = get_activation(model, clean_input, component)

    # Run corrupted with patched activation
    def patch_fn(acts):
        return clean_acts

    patched_output = model_with_patch(
        model, corrupted_input, component, patch_fn
    )

    # Measure restoration
    clean_output = model(clean_input)
    corrupted_output = model(corrupted_input)

    restoration = (patched_output - corrupted_output) / (clean_output - corrupted_output)
    return restoration
```

### Ablation Studies

```python
def structured_ablation(model, component, method="zero"):
    """
    Remove component contribution
    """
    methods = {
        "zero": lambda x: torch.zeros_like(x),
        "mean": lambda x: x.mean(dim=0, keepdim=True).expand_as(x),
        "random": lambda x: torch.randn_like(x) * x.std(),
        "shuffle": lambda x: x[torch.randperm(x.shape[0])]
    }

    ablation_fn = methods[method]
    return apply_intervention(model, component, ablation_fn)
```

### Path Patching

```python
def path_patching(model, source_node, target_node, path):
    """
    Intervene on specific computational path
    """
    # Block all paths except specified
    for edge in model.edges:
        if edge not in path:
            block_edge(edge)

    # Measure contribution of specific path
    output_with_path = model(input)

    # Compare to no path
    block_all_paths(source_node, target_node)
    output_without = model(input)

    path_contribution = output_with_path - output_without
    return path_contribution
```

---

## Advanced Interventions

### Causal Scrubbing

```python
def causal_scrubbing(hypothesis, model, dataset):
    """
    Test if hypothesis explains all model behavior
    """
    # For each computational path in hypothesis
    for path in hypothesis.paths:
        # Scramble everything except path
        scrambled = scramble_all_except(model, path)

        # Should preserve behavior
        original_output = model(dataset)
        scrambled_output = scrambled(dataset)

        preserved = similarity(original_output, scrambled_output)

        if preserved < threshold:
            return False, f"Path {path} insufficient"

    return True, "Hypothesis sufficient"
```

### Interchange Interventions

```python
def interchange_intervention(model, component, source_input, target_input):
    """
    Swap component activation between examples
    """
    # Get activation from source
    source_act = get_activation(model, source_input, component)

    # Apply to target
    def swap_fn(acts):
        return source_act

    swapped_output = model_with_patch(
        model, target_input, component, swap_fn
    )

    # Measure effect
    original_output = model(target_input)
    effect = swapped_output - original_output

    return effect
```

---

## Statistical Causal Tools

### Average Treatment Effect

```python
def estimate_ate(model, intervention, dataset):
    """
    Average causal effect of intervention
    """
    treated_outputs = []
    control_outputs = []

    for input in dataset:
        # Control (no intervention)
        control = model(input)
        control_outputs.append(control)

        # Treatment (with intervention)
        with intervention:
            treated = model(input)
        treated_outputs.append(treated)

    # ATE = E[Y|T=1] - E[Y|T=0]
    ate = np.mean(treated_outputs) - np.mean(control_outputs)

    # Bootstrap confidence interval
    ate_ci = bootstrap_ci(treated_outputs, control_outputs)

    return ate, ate_ci
```

### Mediation Analysis

```python
def mediation_analysis(model, cause, mediator, effect):
    """
    Decompose causal effect into direct and mediated
    """
    # Total effect
    total = intervene(model, cause, value=1) - intervene(model, cause, value=0)

    # Direct effect (block mediator)
    with block(mediator):
        direct = intervene(model, cause, value=1) - intervene(model, cause, value=0)

    # Indirect effect (through mediator)
    indirect = total - direct

    # Proportion mediated
    prop_mediated = indirect / total if total != 0 else 0

    return {
        "total_effect": total,
        "direct_effect": direct,
        "indirect_effect": indirect,
        "proportion_mediated": prop_mediated
    }
```

---

## Validation Tools

### Causal Sufficiency Test

```python
def test_causal_sufficiency(hypothesis, model):
    """
    Test if hypothesis captures all causal structure
    """
    # Remove everything not in hypothesis
    minimal_model = keep_only(model, hypothesis.components)

    # Should preserve behavior
    full_performance = evaluate(model)
    minimal_performance = evaluate(minimal_model)

    sufficiency = minimal_performance / full_performance
    return sufficiency > 0.95
```

### Necessity Test

```python
def test_necessity(component, model, task):
    """
    Test if component is necessary
    """
    # Remove component
    ablated = ablate(model, component)

    # Measure degradation
    original_score = evaluate(model, task)
    ablated_score = evaluate(ablated, task)

    necessary = ablated_score < original_score * 0.5
    return necessary
```

---

## Best Practices

### Intervention Design
1. **Use multiple ablation methods** (zero, mean, random)
2. **Control for indirect effects** (other components compensating)
3. **Verify intervention worked** (check activation actually changed)
4. **Test on distribution** (not just single examples)

### Causal Claims
1. **Necessity**: X required for Y (ablation destroys Y)
2. **Sufficiency**: X alone produces Y (isolation preserves Y)
3. **Mediation**: X affects Y through Z (path analysis)
4. **Direct causation**: X affects Y not through any mediator

### Common Pitfalls
- Ablating breaks model in non-specific ways
- Compensatory mechanisms mask effects
- Intervention has unintended side effects
- Correlation misinterpreted as causation

---

## Implementation Examples

### Full Causal Analysis Pipeline

```python
class CausalAnalysis:
    def __init__(self, model, hypothesis):
        self.model = model
        self.hypothesis = hypothesis

    def run_full_analysis(self):
        results = {}

        # Test each component
        for component in self.hypothesis.components:
            # Necessity
            results[component]["necessary"] = test_necessity(
                component, self.model, self.task
            )

            # Sufficiency
            results[component]["sufficient"] = test_sufficiency(
                component, self.model, self.task
            )

            # Causal effect size
            ate, ci = estimate_ate(
                self.model,
                ablate(component),
                self.dataset
            )
            results[component]["effect_size"] = ate
            results[component]["ci"] = ci

        # Test full hypothesis
        results["hypothesis_sufficient"] = test_causal_sufficiency(
            self.hypothesis, self.model
        )

        return results
```

---

*Causal intervention transforms correlation into understanding. Without intervention, we only describe; with intervention, we explain.*
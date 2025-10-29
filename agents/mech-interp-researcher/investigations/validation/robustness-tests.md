# Robustness Tests for Mechanistic Interpretability

## Purpose

Robustness tests verify that findings hold under various conditions, aren't artifacts of specific choices, and generalize beyond the exact experimental setup.

---

## Core Robustness Dimensions

### 1. Model Robustness

**Test across different models to verify findings aren't model-specific.**

```python
def test_model_robustness(hypothesis_test):
    """
    Verify hypothesis holds across model variations
    """
    models_to_test = {
        "original": load_model("gpt2-small"),
        "different_size": load_model("gpt2-medium"),
        "different_arch": load_model("gpt-neo"),
        "different_training": load_model("gpt2-small-alternative"),
        "different_seed": train_from_scratch(seed=42),
        "fine_tuned": fine_tune(base_model, different_data)
    }

    results = {}
    for model_name, model in models_to_test.items():
        try:
            result = hypothesis_test(model)
            results[model_name] = {
                "holds": result["hypothesis_confirmed"],
                "strength": result["effect_size"],
                "p_value": result["p_value"]
            }
        except Exception as e:
            results[model_name] = {"error": str(e)}

    # Assess robustness
    success_rate = sum(r.get("holds", False) for r in results.values()) / len(results)
    consistent = success_rate > 0.7  # Holds in >70% of models

    return {
        "individual_results": results,
        "success_rate": success_rate,
        "robust": consistent
    }
```

### 2. Data Robustness

**Test across different datasets and data conditions.**

```python
def test_data_robustness(analysis_fn, model):
    """
    Verify findings hold across data variations
    """
    datasets = {
        "original": original_dataset,
        "out_of_distribution": ood_dataset,
        "adversarial": adversarial_examples,
        "synthetic": synthetic_dataset,
        "different_domain": domain_shift_dataset,
        "noisy": add_noise(original_dataset, sigma=0.1),
        "subsampled": subsample(original_dataset, fraction=0.1)
    }

    results = {}
    for data_name, dataset in datasets.items():
        result = analysis_fn(model, dataset)

        # Compare to baseline
        baseline = analysis_fn(model, original_dataset)
        correlation = np.corrcoef(
            result["pattern"].flatten(),
            baseline["pattern"].flatten()
        )[0, 1]

        results[data_name] = {
            "correlation_with_original": correlation,
            "effect_preserved": correlation > 0.7,
            "effect_size": result["effect_size"]
        }

    return results
```

### 3. Hyperparameter Robustness

**Test sensitivity to analysis hyperparameters.**

```python
def test_hyperparameter_robustness(method, default_params):
    """
    Verify findings aren't hyperparam artifacts
    """
    # Define parameter ranges to test
    param_ranges = {
        "threshold": [0.01, 0.05, 0.1, 0.2, 0.5],
        "n_components": [10, 50, 100, 200, 500],
        "regularization": [0, 0.001, 0.01, 0.1, 1.0],
        "learning_rate": [1e-5, 1e-4, 1e-3, 1e-2],
        "n_samples": [100, 500, 1000, 5000, 10000]
    }

    sensitivity_results = {}

    for param_name, param_values in param_ranges.items():
        results_across_values = []

        for value in param_values:
            # Update parameter
            params = default_params.copy()
            params[param_name] = value

            # Run analysis
            result = method(**params)
            results_across_values.append(result["metric"])

        # Measure sensitivity
        sensitivity = np.std(results_across_values) / np.mean(results_across_values)
        sensitivity_results[param_name] = {
            "values_tested": param_values,
            "results": results_across_values,
            "coefficient_of_variation": sensitivity,
            "sensitive": sensitivity > 0.3  # CV > 30% indicates sensitivity
        }

    return sensitivity_results
```

---

## Method-Specific Robustness Tests

### For Circuit Discovery

```python
def test_circuit_robustness(circuit_hypothesis):
    """
    Test if circuit is robust or fragile
    """
    robustness_tests = {}

    # 1. Ablation granularity
    granularities = ["single_neuron", "head", "layer", "component"]
    for granularity in granularities:
        ablated = ablate_at_granularity(circuit_hypothesis, granularity)
        robustness_tests[f"ablation_{granularity}"] = ablated["still_works"]

    # 2. Noise injection
    noise_levels = [0.01, 0.05, 0.1, 0.2]
    for noise in noise_levels:
        noisy = add_noise_to_circuit(circuit_hypothesis, noise)
        robustness_tests[f"noise_{noise}"] = noisy["performance"] > 0.8

    # 3. Weight perturbation
    perturbation_scales = [0.9, 0.95, 1.05, 1.1]
    for scale in perturbation_scales:
        perturbed = scale_weights(circuit_hypothesis, scale)
        robustness_tests[f"weight_scale_{scale}"] = perturbed["functional"]

    # 4. Activation perturbation
    perturb_types = ["gaussian", "uniform", "dropout", "adversarial"]
    for perturb_type in perturb_types:
        perturbed = perturb_activations(circuit_hypothesis, perturb_type)
        robustness_tests[f"activation_{perturb_type}"] = perturbed["robust"]

    return robustness_tests
```

### For Attention Patterns

```python
def test_attention_robustness(attention_analysis):
    """
    Test if attention patterns are stable
    """
    # 1. Position permutation
    permuted_input = permute_positions(original_input)
    permuted_pattern = attention_analysis(permuted_input)
    position_invariant = patterns_equivalent(
        original_pattern,
        unpermute(permuted_pattern)
    )

    # 2. Token substitution
    substitution_rates = [0.05, 0.1, 0.2, 0.3]
    substitution_robustness = []
    for rate in substitution_rates:
        substituted = randomly_substitute_tokens(original_input, rate)
        pattern = attention_analysis(substituted)
        correlation = pattern_correlation(original_pattern, pattern)
        substitution_robustness.append(correlation > 0.7)

    # 3. Context length variation
    context_lengths = [32, 64, 128, 256, 512]
    length_robustness = []
    for length in context_lengths:
        truncated = truncate_to_length(original_input, length)
        if len(truncated) >= min_length:
            pattern = attention_analysis(truncated)
            length_robustness.append(pattern["structure_preserved"])

    # 4. Batch variation
    batch_sizes = [1, 8, 32, 128]
    batch_effects = []
    for batch_size in batch_sizes:
        batched = create_batch(original_input, batch_size)
        pattern = attention_analysis(batched)
        batch_effects.append(pattern["consistency_across_batch"])

    return {
        "position_invariant": position_invariant,
        "substitution_robust": all(substitution_robustness),
        "length_robust": all(length_robustness),
        "batch_stable": all(batch_effects)
    }
```

### For Probing Results

```python
def test_probing_robustness(probe_results):
    """
    Test if probing genuinely captures feature
    """
    # 1. Control probing tasks
    control_tasks = {
        "random_labels": generate_random_labels(),
        "constant_labels": np.ones_like(true_labels),
        "anti_correlated": -true_labels,
        "shuffled_features": shuffle_features(features)
    }

    control_results = {}
    for task_name, control_data in control_tasks.items():
        probe = train_probe(control_data)
        control_results[task_name] = probe.accuracy

    # Should be much worse on controls
    genuine = all(
        control_results[task] < probe_results["accuracy"] * 0.6
        for task in control_tasks
    )

    # 2. Cross-validation stability
    cv_scores = cross_val_score(probe, features, labels, cv=10)
    stable = cv_scores.std() / cv_scores.mean() < 0.15

    # 3. Feature subset probing
    feature_subsets = [
        random_subset(features, 0.1),
        random_subset(features, 0.5),
        top_k_features(features, k=10),
        top_k_features(features, k=100)
    ]

    subset_scores = []
    for subset in feature_subsets:
        subset_probe = train_probe(subset, labels)
        subset_scores.append(subset_probe.accuracy)

    # Should degrade gracefully with fewer features
    monotonic = all(
        subset_scores[i] <= subset_scores[i+1]
        for i in range(len(subset_scores)-1)
    )

    return {
        "genuine_signal": genuine,
        "cross_validation_stable": stable,
        "feature_subset_monotonic": monotonic
    }
```

---

## Statistical Robustness

### Multiple Testing Robustness

```python
def test_multiple_testing_robustness(results, correction_methods):
    """
    Verify results survive multiple testing corrections
    """
    corrections = {
        "bonferroni": bonferroni_correction,
        "benjamini_hochberg": fdr_correction,
        "benjamini_yekutieli": by_correction,
        "holm": holm_correction
    }

    robustness = {}
    for method_name, correction_fn in corrections.items():
        corrected_pvals = correction_fn(results["p_values"])
        significant = (corrected_pvals < 0.05).sum()
        robustness[method_name] = {
            "n_significant": significant,
            "survives": significant > 0
        }

    # Robust if survives at least stringent corrections
    overall_robust = (
        robustness["bonferroni"]["survives"] or
        robustness["holm"]["survives"]
    )

    return robustness, overall_robust
```

### Bootstrap Robustness

```python
def test_bootstrap_robustness(statistic_fn, data):
    """
    Test stability of bootstrap estimates
    """
    # Different bootstrap sample sizes
    sample_sizes = [100, 500, 1000, 5000, 10000]
    estimates = []
    cis = []

    for n_samples in sample_sizes:
        bootstrap_dist = bootstrap(statistic_fn, data, n_samples)
        estimates.append(np.mean(bootstrap_dist))
        cis.append(np.percentile(bootstrap_dist, [2.5, 97.5]))

    # Check convergence
    converged = np.std(estimates[-3:]) < 0.01 * np.mean(estimates)

    # Check CI stability
    ci_widths = [ci[1] - ci[0] for ci in cis]
    ci_stable = np.std(ci_widths[-3:]) < 0.1 * np.mean(ci_widths)

    return {
        "estimates_converged": converged,
        "ci_stable": ci_stable,
        "final_estimate": estimates[-1],
        "final_ci": cis[-1]
    }
```

---

## Implementation Robustness

### Numerical Stability

```python
def test_numerical_robustness(computation):
    """
    Test numerical stability of computation
    """
    # Test with different scales
    scales = [1e-6, 1e-3, 1.0, 1e3, 1e6]
    results = []

    for scale in scales:
        scaled_input = input_data * scale
        try:
            result = computation(scaled_input)
            # Rescale output
            rescaled = result / scale if should_scale_output else result
            results.append(rescaled)
        except (OverflowError, UnderflowError) as e:
            results.append(None)

    # Check consistency across scales
    valid_results = [r for r in results if r is not None]
    if len(valid_results) > 1:
        variations = [
            np.abs(r1 - r2) / np.abs(r1)
            for r1, r2 in zip(valid_results[:-1], valid_results[1:])
        ]
        stable = all(v < 0.01 for v in variations)  # <1% variation
    else:
        stable = False

    return {
        "numerically_stable": stable,
        "valid_scale_range": [
            scales[i] for i, r in enumerate(results)
            if r is not None
        ]
    }
```

### Reproducibility

```python
def test_reproducibility(experiment_fn):
    """
    Test if results reproduce with different seeds
    """
    seeds = [42, 123, 456, 789, 1234]
    results = []

    for seed in seeds:
        set_all_seeds(seed)
        result = experiment_fn()
        results.append(result)

    # Check consistency
    if is_deterministic_experiment:
        # Should be identical
        all_equal = all(
            np.allclose(results[0], r) for r in results[1:]
        )
        reproducible = all_equal
    else:
        # Should be statistically consistent
        means = [r["mean"] for r in results]
        stds = [r["std"] for r in results]

        mean_cv = np.std(means) / np.mean(means)
        reproducible = mean_cv < 0.1  # <10% variation

    return {
        "reproducible": reproducible,
        "seed_results": dict(zip(seeds, results))
    }
```

---

## Robustness Test Suite

```python
class RobustnessTestSuite:
    """
    Comprehensive robustness testing
    """
    def __init__(self, hypothesis, method):
        self.hypothesis = hypothesis
        self.method = method

    def run_all_tests(self):
        results = {}

        # Model robustness
        results["model"] = test_model_robustness(self.hypothesis)

        # Data robustness
        results["data"] = test_data_robustness(self.method, self.model)

        # Hyperparameter robustness
        results["hyperparameters"] = test_hyperparameter_robustness(
            self.method,
            self.default_params
        )

        # Statistical robustness
        results["statistics"] = test_statistical_robustness(self.results)

        # Numerical robustness
        results["numerical"] = test_numerical_robustness(self.computation)

        # Reproducibility
        results["reproducibility"] = test_reproducibility(self.experiment)

        # Overall assessment
        results["overall_robust"] = self.assess_overall_robustness(results)

        return results

    def assess_overall_robustness(self, results):
        """
        Combine individual robustness scores
        """
        scores = {
            "model": results["model"]["success_rate"],
            "data": np.mean([r["effect_preserved"] for r in results["data"].values()]),
            "hyperparameters": 1 - np.mean([r["sensitive"] for r in results["hyperparameters"].values()]),
            "statistical": results["statistics"]["overall_robust"],
            "numerical": results["numerical"]["numerically_stable"],
            "reproducible": results["reproducibility"]["reproducible"]
        }

        # Weight different aspects
        weights = {
            "model": 0.25,
            "data": 0.25,
            "hyperparameters": 0.15,
            "statistical": 0.15,
            "numerical": 0.10,
            "reproducible": 0.10
        }

        weighted_score = sum(
            scores[k] * weights[k] for k in scores
        )

        return {
            "individual_scores": scores,
            "weighted_score": weighted_score,
            "robust": weighted_score > 0.7
        }
```

---

## Robustness Reporting Template

```markdown
## Robustness Analysis

### Model Robustness
- Tested on: [List models]
- Success rate: X/Y models
- Effect size variation: [Range]

### Data Robustness
- Datasets tested: [List]
- OOD performance: [Metric]
- Noise tolerance: [Level]

### Hyperparameter Sensitivity
- Most sensitive: [Parameter]
- Robust range: [Range]
- CV for key metric: [Value]

### Statistical Robustness
- Survives Bonferroni: [Yes/No]
- Bootstrap CI: [Range]
- Effect size: [Value ± SE]

### Limitations
- Fails under: [Conditions]
- Assumptions: [List]
- Generalization bounds: [Description]
```

---

*Robustness testing separates preliminary findings from reliable discoveries. Never claim understanding without demonstrating robustness.*
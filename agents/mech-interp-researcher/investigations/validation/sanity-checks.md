# Sanity Checks for Mechanistic Interpretability Investigations

## Purpose

Sanity checks verify that methods work as expected before trusting results. These catch basic errors that could invalidate entire investigations.

---

## Core Sanity Checks

### 1. Random Baseline Check

**Purpose**: Ensure metrics aren't spuriously high.

```python
def random_baseline_check(method, real_model, metric):
    """
    Compare real model against random initialization
    """
    # Real model should score higher than random
    random_model = create_random_model_like(real_model)

    real_score = metric(method(real_model))
    random_score = metric(method(random_model))

    assert real_score > random_score * 1.5, \
        f"Real model ({real_score}) not sufficiently better than random ({random_score})"

    return {
        "real_score": real_score,
        "random_score": random_score,
        "ratio": real_score / random_score
    }
```

**What This Catches**:
- Metrics that are always high
- Methods that don't depend on model weights
- Broken evaluation code

### 2. Gradient Check

**Purpose**: Verify gradients flow correctly.

```python
def gradient_sanity_check(model, loss_fn):
    """
    Ensure gradients are computed correctly
    """
    # Numerical gradient
    def numerical_gradient(param, epsilon=1e-5):
        param_plus = param + epsilon
        param_minus = param - epsilon
        loss_plus = loss_fn(param_plus)
        loss_minus = loss_fn(param_minus)
        return (loss_plus - loss_minus) / (2 * epsilon)

    # Analytical gradient
    analytical = torch.autograd.grad(loss_fn(param), param)

    # Should be very close
    difference = (analytical - numerical_gradient(param)).abs().max()
    assert difference < 1e-3, f"Gradient mismatch: {difference}"
```

**What This Catches**:
- Incorrect gradient computation
- Detached tensors
- Numerical instabilities

### 3. Intervention Effect Check

**Purpose**: Verify interventions actually change model behavior.

```python
def intervention_effect_check(model, intervention):
    """
    Ensure intervention changes something
    """
    # Get baseline behavior
    baseline_output = model(test_input)

    # Apply intervention
    with intervention:
        intervened_output = model(test_input)

    # Should be different
    difference = (baseline_output - intervened_output).abs().mean()
    assert difference > 1e-6, "Intervention has no effect"

    # But not completely broken
    assert not torch.isnan(intervened_output).any(), "Intervention causes NaN"
    assert intervened_output.abs().max() < 1e6, "Intervention causes explosion"
```

**What This Catches**:
- No-op interventions
- Incorrect patching
- Intervention not applied

---

## Method-Specific Sanity Checks

### For Attention Analysis

```python
def attention_sanity_checks(attention_patterns):
    """
    Check attention patterns are valid
    """
    checks = {
        "sums_to_one": [],
        "non_negative": [],
        "not_uniform": [],
        "has_structure": []
    }

    for head_pattern in attention_patterns:
        # Should sum to 1 across attended positions
        row_sums = head_pattern.sum(dim=-1)
        checks["sums_to_one"].append(
            (row_sums - 1).abs().max() < 1e-5
        )

        # Should be non-negative
        checks["non_negative"].append(
            (head_pattern >= 0).all()
        )

        # Shouldn't be uniform (indicates no attention)
        std = head_pattern.std()
        checks["not_uniform"].append(std > 0.01)

        # Should have some structure
        entropy = -
(head_pattern * head_pattern.log()).sum()
        max_entropy = np.log(head_pattern.shape[-1])
        checks["has_structure"].append(
            entropy < 0.9 * max_entropy
        )

    return checks
```

### For Ablation Studies

```python
def ablation_sanity_checks(ablation_fn):
    """
    Verify ablation works correctly
    """
    # Check 1: Ablating nothing changes nothing
    identity_ablation = lambda x: x
    assert model(input) == ablation_fn(model, identity_ablation)(input)

    # Check 2: Ablating everything breaks model
    zero_ablation = lambda x: x * 0
    output = ablation_fn(model, zero_ablation)(input)
    assert output.std() < baseline_output.std() * 0.1

    # Check 3: Partial ablation is between extremes
    half_ablation = lambda x: x * 0.5
    output = ablation_fn(model, half_ablation)(input)
    assert zero_output.std() < output.std() < baseline_output.std()
```

### For Probing Classifiers

```python
def probing_sanity_checks(probe, features, labels):
    """
    Verify probe is learning something real
    """
    # Check 1: Better than random
    random_accuracy = 1 / len(np.unique(labels))
    probe_accuracy = probe.score(features, labels)
    assert probe_accuracy > random_accuracy * 1.5

    # Check 2: Worse on shuffled labels
    shuffled_labels = np.random.permutation(labels)
    shuffled_accuracy = probe.score(features, shuffled_labels)
    assert shuffled_accuracy < probe_accuracy * 0.7

    # Check 3: Worse on random features
    random_features = np.random.randn(*features.shape)
    random_probe = train_probe(random_features, labels)
    assert random_probe.score() < probe_accuracy * 0.8

    # Check 4: Consistent across splits
    scores = cross_val_score(probe, features, labels, cv=5)
    assert scores.std() / scores.mean() < 0.2  # CV < 20%
```

---

## Data Sanity Checks

### Input Data Validation

```python
def input_data_checks(data):
    """
    Ensure input data is valid
    """
    checks = {}

    # No NaN or Inf
    checks["no_nan"] = not torch.isnan(data).any()
    checks["no_inf"] = not torch.isinf(data).any()

    # Reasonable range
    checks["reasonable_range"] = (
        data.abs().max() < 1000 and
        data.abs().min() > 1e-10
    )

    # Not all same
    checks["has_variation"] = data.std() > 1e-6

    # Expected shape
    checks["correct_shape"] = len(data.shape) == expected_dims

    # Correct dtype
    checks["correct_dtype"] = data.dtype == expected_dtype

    return all(checks.values()), checks
```

### Output Distribution Checks

```python
def output_distribution_checks(outputs):
    """
    Check outputs have expected properties
    """
    # For classification: Valid probabilities
    if task_type == "classification":
        assert (outputs >= 0).all() and (outputs <= 1).all()
        assert (outputs.sum(dim=-1) - 1).abs().max() < 1e-5

    # For regression: Reasonable range
    if task_type == "regression":
        assert outputs.abs().mean() < 1000
        assert outputs.std() > 0  # Not constant

    # General: No pathological values
    assert not torch.isnan(outputs).any()
    assert not torch.isinf(outputs).any()
```

---

## Statistical Sanity Checks

### Significance Testing Validity

```python
def statistical_sanity_checks(test_statistic, null_distribution):
    """
    Verify statistical tests are valid
    """
    # Check 1: Null distribution is actually null
    null_mean = null_distribution.mean()
    assert abs(null_mean) < 0.1 * null_distribution.std()

    # Check 2: Test statistic outside null range
    assert abs(test_statistic) > null_distribution.std() * 2

    # Check 3: P-value calculation correct
    p_value = (null_distribution > test_statistic).mean()
    assert 0 <= p_value <= 1

    # Check 4: Multiple testing correction applied
    if n_tests > 1:
        assert corrected_p_value > raw_p_value
```

### Bootstrap Validity

```python
def bootstrap_sanity_checks(bootstrap_fn, data):
    """
    Verify bootstrap is implemented correctly
    """
    # Check 1: Original estimate in bootstrap range
    original = statistic(data)
    bootstrap_dist = bootstrap_fn(data, n_samples=1000)
    ci_lower, ci_upper = np.percentile(bootstrap_dist, [2.5, 97.5])
    # Original should usually be within CI
    # (not always, but should be most of the time)

    # Check 2: Bootstrap variance increases with fewer samples
    var_full = bootstrap_fn(data, n_samples=1000).var()
    var_half = bootstrap_fn(data[:len(data)//2], n_samples=1000).var()
    assert var_half > var_full

    # Check 3: Deterministic with seed
    np.random.seed(42)
    result1 = bootstrap_fn(data)
    np.random.seed(42)
    result2 = bootstrap_fn(data)
    assert np.allclose(result1, result2)
```

---

## Implementation Sanity Checks

### Caching Correctness

```python
def cache_sanity_check(cached_fn):
    """
    Verify caching works correctly
    """
    # First call
    result1 = cached_fn(input1)
    time1 = measure_time(lambda: cached_fn(input1))

    # Second call (should be cached)
    result2 = cached_fn(input1)
    time2 = measure_time(lambda: cached_fn(input1))

    # Same result
    assert torch.allclose(result1, result2)

    # Faster second time
    assert time2 < time1 * 0.5

    # Different input not cached
    result3 = cached_fn(input2)
    assert not torch.allclose(result1, result3)
```

### Parallelization Correctness

```python
def parallel_sanity_check(parallel_fn, serial_fn):
    """
    Verify parallel implementation matches serial
    """
    # Same inputs
    inputs = generate_test_inputs()

    # Serial execution
    serial_results = [serial_fn(inp) for inp in inputs]

    # Parallel execution
    parallel_results = parallel_fn(inputs)

    # Should match
    for serial, parallel in zip(serial_results, parallel_results):
        assert torch.allclose(serial, parallel, rtol=1e-5)
```

---

## Failure Recovery Checks

### Graceful Degradation

```python
def degradation_sanity_check(method):
    """
    Verify method fails gracefully
    """
    # Bad input shouldn't crash
    try:
        result = method(None)
        assert False, "Should have raised exception"
    except ValueError:
        pass  # Expected

    # Partial failure should give partial results
    partially_broken_input = corrupt_part_of_input(good_input)
    result = method(partially_broken_input)
    assert result is not None
    assert "warning" in result.get("status", "")
```

---

## Sanity Check Checklist

Before trusting any investigation results:

- [ ] Random baseline significantly worse
- [ ] Gradients flow correctly
- [ ] Interventions have effects
- [ ] Attention patterns sum to 1
- [ ] Ablations work as expected
- [ ] Probes better than chance
- [ ] Data has no NaN/Inf
- [ ] Outputs in valid range
- [ ] Statistics properly computed
- [ ] Bootstrap confidence intervals reasonable
- [ ] Caching works correctly
- [ ] Parallel matches serial
- [ ] Graceful failure handling

---

## When Sanity Checks Fail

1. **Debug immediately** - Don't proceed with bad foundations
2. **Check assumptions** - What did you assume that isn't true?
3. **Simplify** - Test on smaller, simpler cases
4. **Visualize** - Plot intermediate values
5. **Unit test** - Break into smaller components
6. **Get fresh eyes** - Have someone else check

---

*Remember: Sanity checks are not optional. They are the foundation of reliable mechanistic interpretability research.*
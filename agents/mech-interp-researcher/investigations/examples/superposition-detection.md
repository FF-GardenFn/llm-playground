# Example Investigation: Superposition Detection and Measurement

## Hypothesis

**Primary Claim**: Models use superposition to represent more features than dimensions, with interference patterns predictable from feature importance and sparsity.

**Mechanistic Specificity**:
- MLP neurons encode multiple features in superposition
- Interference follows predictable patterns
- Recovery possible via sparse coding methods

---

## Investigation Framework

### Phase 1: Theoretical Foundation

**Superposition Model**:
```python
# Features > Dimensions requires compression
# N features in D dimensions where N >> D
# Interference is the cost of compression

class SuperpositionModel:
    def __init__(self, n_features, n_dimensions):
        assert n_features > n_dimensions
        self.compression_ratio = n_features / n_dimensions
        self.interference_matrix = self.compute_interference()
```

**Key Predictions**:
1. Important features get dedicated dimensions
2. Rare features share dimensions (superposition)
3. Interference inversely related to importance gap
4. Sparsity enables more superposition

### Phase 2: Alternative Hypotheses

**Alternative 1**: Distributed Encoding (No Superposition)
- All features spread equally across dimensions
- Test: No sparse structure recoverable

**Alternative 2**: Random Projection
- Random linear combinations, no structure
- Test: Interference pattern is random

**Alternative 3**: Hierarchical Encoding
- Nested representations, not superposition
- Test: Clear hierarchy in activation patterns

---

## Detection Methods

### Method 1: Sparse Dictionary Learning

```python
def detect_superposition_via_dictionary_learning(activations):
    """
    Learn overcomplete dictionary of features
    """
    from sklearn.decomposition import DictionaryLearning

    # Learn dictionary with more atoms than dimensions
    dict_learner = DictionaryLearning(
        n_components=10 * activations.shape[1],  # Overcomplete
        alpha=1.0,  # Sparsity penalty
        max_iter=1000
    )

    dictionary = dict_learner.fit(activations).components_

    # Analyze learned features
    features = {
        "n_features_recovered": count_interpretable_features(dictionary),
        "sparsity": measure_sparsity(dict_learner.transform(activations)),
        "reconstruction_error": dict_learner.score(activations)
    }

    return features, dictionary
```

### Method 2: Interference Pattern Analysis

```python
def analyze_interference_patterns(model, inputs):
    """
    Measure how features interfere with each other
    """
    # Identify features via probing
    features = identify_features_via_probing(model, inputs)

    # Measure pairwise interference
    interference_matrix = np.zeros((len(features), len(features)))

    for i, feature_i in enumerate(features):
        for j, feature_j in enumerate(features):
            if i != j:
                # Activate both features
                combined = activate_features([feature_i, feature_j])
                separate_i = activate_features([feature_i])
                separate_j = activate_features([feature_j])

                # Measure interference
                expected = separate_i + separate_j
                actual = combined
                interference = norm(expected - actual) / norm(expected)

                interference_matrix[i, j] = interference

    return interference_matrix
```

### Method 3: Dimensionality Analysis

```python
def measure_intrinsic_dimensionality(activations):
    """
    Estimate true number of features despite superposition
    """
    # Method 1: Participation ratio
    _, s, _ = np.linalg.svd(activations - activations.mean(0))
    s_squared = s ** 2
    participation_ratio = (s_squared.sum() ** 2) / (s_squared ** 2).sum()

    # Method 2: Local dimensionality (TwoNN)
    from intrinsic_dim import TwoNN
    estimator = TwoNN()
    local_dim = estimator.fit_transform(activations)

    # Method 3: Maximum likelihood estimation
    from intrinsic_dim import MLE
    mle = MLE()
    mle_dim = mle.fit_transform(activations)

    return {
        "participation_ratio": participation_ratio,
        "local_dimension": local_dim.mean(),
        "mle_dimension": mle_dim,
        "ambient_dimension": activations.shape[1]
    }
```

---

## Experimental Protocol

### Dataset Preparation

```python
def prepare_superposition_test_data():
    """
    Create data with known ground-truth features
    """
    # Sparse features with known importance
    features = {
        "important_dense": generate_important_dense_features(n=10),
        "important_sparse": generate_important_sparse_features(n=20),
        "unimportant_sparse": generate_unimportant_sparse_features(n=50)
    }

    # Combine with known weights
    data = combine_features_with_importance_weights(features)

    return data, features
```

### Superposition Detection Pipeline

```python
def full_superposition_analysis(model, layer):
    """
    Complete pipeline for detecting and analyzing superposition
    """
    # Step 1: Extract activations
    activations = get_layer_activations(model, layer, test_data)

    # Step 2: Dimensionality analysis
    dims = measure_intrinsic_dimensionality(activations)
    print(f"Intrinsic dim: {dims['local_dimension']:.1f}")
    print(f"Ambient dim: {dims['ambient_dimension']}")

    # Step 3: Dictionary learning
    features, dictionary = detect_superposition_via_dictionary_learning(
        activations
    )
    print(f"Features recovered: {features['n_features_recovered']}")

    # Step 4: Interference analysis
    interference = analyze_interference_patterns(model, test_data)

    # Step 5: Importance-sparsity relationship
    importance_sparsity = analyze_importance_vs_sparsity(
        dictionary, features
    )

    return {
        "dimensionality": dims,
        "features": features,
        "interference": interference,
        "importance_sparsity": importance_sparsity
    }
```

---

## Validation Experiments

### Synthetic Validation

```python
def validate_on_synthetic_model():
    """
    Train model with known superposition
    """
    # Create model forced to use superposition
    model = create_bottleneck_model(
        input_features=100,
        bottleneck_dim=10,
        output_features=100
    )

    # Train on sparse data
    sparse_data = generate_sparse_data(sparsity=0.1)
    model.train(sparse_data)

    # Verify superposition emerged
    analysis = full_superposition_analysis(model, bottleneck_layer)

    assert analysis["features"]["n_features_recovered"] > 10
    assert analysis["dimensionality"]["local_dimension"] > 10

    return analysis
```

### Causal Intervention

```python
def test_feature_orthogonality():
    """
    Test if features can be independently controlled
    """
    # Learn feature dictionary
    dictionary = learn_sparse_dictionary(activations)

    # Test independent control
    results = []
    for feature_idx in range(dictionary.shape[0]):
        # Activate single feature
        activated = activate_single_feature(dictionary[feature_idx])

        # Measure cross-activation
        cross_activation = measure_other_features(activated, dictionary)

        results.append({
            "feature": feature_idx,
            "isolation": 1 - cross_activation.mean(),
            "max_interference": cross_activation.max()
        })

    # High isolation = successful superposition separation
    mean_isolation = np.mean([r["isolation"] for r in results])
    assert mean_isolation > 0.7
```

---

## Results Analysis

### Superposition Signatures

```python
# Clear indicators of superposition found:
signatures = {
    "overcomplete_recovery": True,  # >100 features from 50 dimensions
    "sparse_activation": True,      # Average 5% features active
    "interference_pattern": True,   # Predictable from importance
    "dimensionality_gap": True,     # Intrinsic > Ambient dimension
}
```

### Importance-Sparsity Tradeoff

```python
# Empirical relationship discovered
def superposition_capacity(importance, sparsity):
    """
    Features representable = f(importance, sparsity)
    """
    # More important → more dedicated dimension
    # More sparse → more superposition possible
    capacity = dimension * (1 + log(1/sparsity) * (1 - importance))
    return capacity

# Validated empirically
empirical_fit = fit_capacity_model(data)
theoretical_prediction = superposition_capacity(
    importance=measured_importance,
    sparsity=measured_sparsity
)
correlation = np.corrcoef(empirical_fit, theoretical_prediction)[0, 1]
assert correlation > 0.85
```

### Phase Transition

```python
# Superposition emerges at critical sparsity
transition_analysis = {
    "sparsity_0.5": "No superposition (dense)",
    "sparsity_0.2": "Weak superposition",
    "sparsity_0.1": "Transition region",
    "sparsity_0.05": "Strong superposition",
    "sparsity_0.01": "Extreme superposition (>10x features)"
}
```

---

## Mechanistic Understanding

### Geometric Picture

```python
def visualize_superposition_geometry():
    """
    Visualize how features are arranged in activation space
    """
    # Project to 3D for visualization
    from sklearn.manifold import TSNE
    projection = TSNE(n_components=3).fit_transform(dictionary)

    # Color by feature importance
    colors = feature_importance_scores

    # Size by sparsity
    sizes = 1 / feature_sparsity

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(
        projection[:, 0],
        projection[:, 1],
        projection[:, 2],
        c=colors,
        s=sizes,
        alpha=0.6
    )

    # Important features near axes
    # Sparse features in off-axis directions
    # Clustering indicates feature groups
```

### Information-Theoretic View

```python
def information_analysis():
    """
    Analyze information capacity under superposition
    """
    # Channel capacity with interference
    capacity_with_interference = compute_channel_capacity(
        n_features=measured_features,
        n_dimensions=model_dimensions,
        interference=measured_interference,
        sparsity=measured_sparsity
    )

    # Compare to theoretical limits
    theoretical_max = n_dimensions * log2(1 + snr)
    efficiency = capacity_with_interference / theoretical_max

    return {
        "actual_capacity": capacity_with_interference,
        "theoretical_max": theoretical_max,
        "efficiency": efficiency
    }
```

---

## Engineering Implications

### Feature Extraction

```python
def extract_interpretable_features(model):
    """
    Use superposition understanding to extract features
    """
    # Learn overcomplete dictionary
    dictionary = learn_sparse_dictionary_with_importance_prior(
        activations=get_activations(model),
        importance_prior=estimate_feature_importance()
    )

    # Threshold for interpretability
    interpretable = dictionary[interpretability_score > threshold]

    # Orthogonalize important features
    important = interpretable[importance > importance_threshold]
    important_orthogonal = gram_schmidt(important)

    return {
        "all_features": dictionary,
        "interpretable": interpretable,
        "important": important_orthogonal
    }
```

### Capacity Enhancement

```python
def enhance_model_capacity():
    """
    Increase effective capacity via better superposition
    """
    # Encourage sparsity during training
    sparsity_loss = L1_penalty_on_activations

    # Decorrelate features
    decorrelation_loss = off_diagonal_penalty(
        gram_matrix(activations)
    )

    # Total loss encourages superposition
    total_loss = task_loss + λ1 * sparsity_loss + λ2 * decorrelation_loss

    # Result: Same parameter count, more capabilities
```

---

## Limitations and Caveats

### Detection Limitations
1. Dictionary learning may not recover all features
2. Some features may be fundamentally entangled
3. Nonlinear superposition not captured

### Interpretation Challenges
1. Features may not align with human concepts
2. Context-dependent superposition
3. Dynamic feature allocation

### Technical Constraints
1. Computational cost of dictionary learning
2. Need for diverse activation data
3. Scalability to very large models

---

## Future Directions

1. **Nonlinear Superposition**: Beyond linear combinations
2. **Dynamic Superposition**: Context-dependent encoding
3. **Superposition Control**: Engineering specific patterns
4. **Cross-Layer Superposition**: How it evolves through depth
5. **Superposition in Attention**: Beyond MLP analysis

---

*This investigation demonstrates how to detect and quantify superposition, moving from "models compress features" to "Layer 3 MLP uses 5.2x superposition with predictable interference patterns based on feature importance and sparsity."*
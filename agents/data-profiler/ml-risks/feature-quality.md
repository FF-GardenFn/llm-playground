# Feature Quality Issues

**Risk Category**: 🟠 ML RISK - HIGH
**Impact**: Degraded model performance, overfitting, training instability
**Detection**: Variance analysis, cardinality checks, multicollinearity detection

Poor feature quality wastes model capacity on uninformative or redundant features. Detecting and fixing feature quality issues improves model performance and reduces training time.

---

## What is Feature Quality?

High-quality features have:
1. **Sufficient variance** (not constant or near-constant)
2. **Appropriate cardinality** (not too many unique values)
3. **Low redundancy** (not highly correlated with other features)
4. **Meaningful information** (predictive signal, not noise)

**Why Important**: Poor-quality features degrade model performance and increase overfitting risk

---

## Detection Methods

### 1. Zero/Low Variance Features

**Goal**: Identify features with no or minimal variation

**Method**: Calculate variance, flag features below threshold

**Code**:
```python
from sklearn.feature_selection import VarianceThreshold

def detect_low_variance_features(df, threshold=0.01):
    """Find features with variance below threshold"""

    # Select numerical features
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    results = []
    for col in numerical_cols:
        variance = df[col].var()
        unique_ratio = df[col].nunique() / len(df)

        # Classify
        if variance < threshold:
            severity = 'CRITICAL' if variance == 0 else 'HIGH'
        else:
            severity = 'OK'

        results.append({
            'feature': col,
            'variance': variance,
            'unique_values': df[col].nunique(),
            'unique_ratio': unique_ratio,
            'severity': severity
        })

    df_results = pd.DataFrame(results).sort_values('variance')
    return df_results

# Example usage
low_var_results = detect_low_variance_features(df, threshold=0.01)
print(low_var_results[low_var_results['severity'] != 'OK'])

# Remove low variance features
selector = VarianceThreshold(threshold=0.01)
X_filtered = selector.fit_transform(X)
removed_features = X.columns[~selector.get_support()].tolist()
print(f"Removed {len(removed_features)} low-variance features: {removed_features}")
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-variance --input data.csv --threshold 0.01
```

**Interpretation**:
- `variance = 0`: 🔴 CRITICAL - Constant feature (zero information)
- `variance < 0.01`: 🟠 HIGH - Near-constant (minimal information)
- `variance ≥ 0.01`: ✅ Sufficient variance

**Common Causes**:
- Feature engineering error (constant value assigned)
- Missing imputation with constant (all nulls filled with 0)
- Incorrect data type (categorical encoded as constant)

**Fix**:
```python
# Remove zero-variance features
zero_var_features = low_var_results[low_var_results['variance'] == 0]['feature'].tolist()
df = df.drop(columns=zero_var_features)
print(f"Removed {len(zero_var_features)} zero-variance features")

# Log low-variance features for review
low_var_features = low_var_results[
    (low_var_results['variance'] > 0) & (low_var_results['variance'] < 0.01)
]['feature'].tolist()
print(f"Low-variance features for review: {low_var_features}")
```

---

### 2. High Cardinality Categorical Features

**Goal**: Identify categoricals with too many unique values

**Method**: Count unique values, flag features above threshold

**Code**:
```python
def detect_high_cardinality_features(df, threshold=50, min_frequency=10):
    """Find categorical features with excessive unique values"""

    # Select object/categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    results = []
    for col in categorical_cols:
        nunique = df[col].nunique()
        cardinality_ratio = nunique / len(df)
        value_counts = df[col].value_counts()

        # Check for rare categories
        rare_categories = (value_counts < min_frequency).sum()
        rare_ratio = rare_categories / nunique

        # Classify
        if nunique > 100:
            severity = 'CRITICAL'
        elif nunique > threshold:
            severity = 'HIGH'
        else:
            severity = 'OK'

        results.append({
            'feature': col,
            'unique_values': nunique,
            'cardinality_ratio': cardinality_ratio,
            'rare_categories': rare_categories,
            'rare_ratio': rare_ratio,
            'severity': severity
        })

    df_results = pd.DataFrame(results).sort_values('unique_values', ascending=False)
    return df_results

# Example usage
high_card_results = detect_high_cardinality_features(df, threshold=50)
print(high_card_results[high_card_results['severity'] != 'OK'])

# Example output:
# feature        unique_values  cardinality_ratio  rare_categories  rare_ratio  severity
# city           237            0.095              189             0.797        CRITICAL
# zip_code       180            0.072              145             0.806        CRITICAL
# employer       156            0.062              128             0.821        CRITICAL
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-cardinality --input data.csv --threshold 50
```

**Interpretation**:
- `nunique < 50`: ✅ Appropriate cardinality
- `nunique 50-100`: 🟠 HIGH - May need alternative encoding
- `nunique > 100`: 🔴 CRITICAL - Definitely needs treatment

**Fix Options**:
```python
# Option 1: Target encoding (mean target by category)
from category_encoders import TargetEncoder
encoder = TargetEncoder(cols=['city'])
df['city_encoded'] = encoder.fit_transform(df[['city']], df['target'])

# Option 2: Frequency encoding
city_counts = df['city'].value_counts()
df['city_frequency'] = df['city'].map(city_counts)

# Option 3: Group rare categories
top_cities = df['city'].value_counts().head(20).index
df['city_grouped'] = df['city'].apply(lambda x: x if x in top_cities else 'Other')

# Option 4: Hashing trick
from sklearn.feature_extraction import FeatureHasher
hasher = FeatureHasher(n_features=20, input_type='string')
hashed = hasher.transform([[c] for c in df['city']])
```

---

### 3. Multicollinearity (High Feature Correlation)

**Goal**: Identify redundant feature pairs with high correlation

**Method**: Compute pairwise correlations, flag pairs above threshold

**Code**:
```python
def detect_multicollinearity(df, threshold=0.90):
    """Find highly correlated feature pairs"""

    # Compute correlation matrix
    corr_matrix = df.corr().abs()

    # Extract pairs with high correlation
    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if corr_value > threshold:
                high_corr_pairs.append({
                    'feature_1': corr_matrix.columns[i],
                    'feature_2': corr_matrix.columns[j],
                    'correlation': corr_value,
                    'severity': 'CRITICAL' if corr_value > 0.95 else 'HIGH'
                })

    df_results = pd.DataFrame(high_corr_pairs).sort_values('correlation', ascending=False)
    return df_results

# Example usage
multicoll_results = detect_multicollinearity(df, threshold=0.90)
print(multicoll_results)

# Example output:
# feature_1      feature_2      correlation  severity
# lat            zip_lat        0.96         CRITICAL
# lon            zip_lon        0.94         HIGH
# income         salary         0.92         HIGH
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-multicollinearity --input data.csv --threshold 0.90
```

**Interpretation**:
- `correlation < 0.90`: ✅ Low redundancy
- `correlation 0.90-0.95`: 🟠 HIGH - Consider removing one feature
- `correlation > 0.95`: 🔴 CRITICAL - Highly redundant, remove one

**VIF Analysis** (more comprehensive):
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

def calculate_vif(df):
    """Calculate Variance Inflation Factor for each feature"""

    vif_data = pd.DataFrame()
    vif_data["feature"] = df.columns
    vif_data["VIF"] = [variance_inflation_factor(df.values, i) for i in range(len(df.columns))]

    # Classify
    vif_data['severity'] = vif_data['VIF'].apply(
        lambda x: 'CRITICAL' if x > 10 else ('HIGH' if x > 5 else 'OK')
    )

    return vif_data.sort_values('VIF', ascending=False)

# Example usage
vif_results = calculate_vif(df.select_dtypes(include=[np.number]))
print(vif_results[vif_results['severity'] != 'OK'])

# Example output:
# feature        VIF       severity
# zip_lat        15.3      CRITICAL  ← Remove (redundant with lat)
# zip_lon        12.8      CRITICAL  ← Remove (redundant with lon)
# income         6.2       HIGH      ← Consider removing
```

**Fix**:
```python
# Remove features with VIF > 10
features_to_remove = vif_results[vif_results['VIF'] > 10]['feature'].tolist()
df = df.drop(columns=features_to_remove)
print(f"Removed {len(features_to_remove)} features with VIF >10: {features_to_remove}")

# Verify VIF improved
vif_results_after = calculate_vif(df.select_dtypes(include=[np.number]))
assert (vif_results_after['VIF'] > 10).sum() == 0, "Still have multicollinearity"
```

---

### 4. Constant Features by Group

**Goal**: Detect features constant within important groups (e.g., user_id)

**Method**: Check variance within groups

**Code**:
```python
def detect_constant_by_group(df, group_col, threshold=0.01):
    """Find features that are constant within groups"""

    numerical_cols = df.select_dtypes(include=[np.number]).columns

    results = []
    for col in numerical_cols:
        if col == group_col:
            continue

        # Calculate variance within each group
        group_variances = df.groupby(group_col)[col].var()

        # Check how many groups have near-zero variance
        constant_groups = (group_variances < threshold).sum()
        constant_ratio = constant_groups / len(group_variances)

        # Classify
        if constant_ratio > 0.90:
            severity = 'CRITICAL'  # Constant in >90% of groups
        elif constant_ratio > 0.50:
            severity = 'HIGH'      # Constant in >50% of groups
        else:
            severity = 'OK'

        results.append({
            'feature': col,
            'constant_groups': constant_groups,
            'total_groups': len(group_variances),
            'constant_ratio': constant_ratio,
            'severity': severity
        })

    df_results = pd.DataFrame(results).sort_values('constant_ratio', ascending=False)
    return df_results

# Example usage
const_by_group = detect_constant_by_group(df, group_col='user_id', threshold=0.01)
print(const_by_group[const_by_group['severity'] != 'OK'])

# Example output:
# feature              constant_groups  total_groups  constant_ratio  severity
# account_type         1,850            2,000         0.925           CRITICAL
# subscription_tier    1,420            2,000         0.710           HIGH
```

**Interpretation**:
- `constant_ratio < 0.50`: ✅ Varies within groups
- `constant_ratio 0.50-0.90`: 🟠 HIGH - Mostly constant within groups
- `constant_ratio > 0.90`: 🔴 CRITICAL - Constant within groups (no within-group signal)

**Why Important**: If predicting user behavior and feature is constant per user, feature provides no within-user information (only between-user).

**Fix**:
```python
# Remove features constant in >90% of groups
constant_features = const_by_group[const_by_group['constant_ratio'] > 0.90]['feature'].tolist()
df = df.drop(columns=constant_features)
print(f"Removed {len(constant_features)} group-constant features")
```

---

### 5. Sparse Features

**Goal**: Identify features with mostly zero values

**Method**: Calculate sparsity (% zeros)

**Code**:
```python
def detect_sparse_features(df, threshold=0.90):
    """Find features with >90% zero values"""

    numerical_cols = df.select_dtypes(include=[np.number]).columns

    results = []
    for col in numerical_cols:
        zero_count = (df[col] == 0).sum()
        sparsity = zero_count / len(df)

        # Classify
        if sparsity > 0.95:
            severity = 'CRITICAL'
        elif sparsity > threshold:
            severity = 'HIGH'
        else:
            severity = 'OK'

        results.append({
            'feature': col,
            'zero_count': zero_count,
            'sparsity': sparsity,
            'non_zero_count': len(df) - zero_count,
            'severity': severity
        })

    df_results = pd.DataFrame(results).sort_values('sparsity', ascending=False)
    return df_results

# Example usage
sparse_results = detect_sparse_features(df, threshold=0.90)
print(sparse_results[sparse_results['severity'] != 'OK'])

# Example output:
# feature                zero_count  sparsity  non_zero_count  severity
# num_chargebacks        14,850      0.990     150            CRITICAL
# num_disputes           14,200      0.947     800            HIGH
# fraud_reports          13,800      0.920     1,200          HIGH
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-sparsity --input data.csv --threshold 0.90
```

**Interpretation**:
- `sparsity < 0.90`: ✅ Sufficient density
- `sparsity 0.90-0.95`: 🟠 HIGH - Very sparse, may need treatment
- `sparsity > 0.95`: 🔴 CRITICAL - Extremely sparse (5% non-zero)

**Fix Options**:
```python
# Option 1: Remove extremely sparse features (>95% zeros)
extremely_sparse = sparse_results[sparse_results['sparsity'] > 0.95]['feature'].tolist()
df = df.drop(columns=extremely_sparse)

# Option 2: Create binary indicator (has_feature vs no_feature)
for col in sparse_results[sparse_results['sparsity'] > 0.90]['feature']:
    df[f'{col}_indicator'] = (df[col] > 0).astype(int)
    df = df.drop(columns=[col])

# Option 3: Use sparse matrix representation (for models that support it)
from scipy.sparse import csr_matrix
X_sparse = csr_matrix(X)
```

---

## Complete Feature Quality Checklist

```python
def run_feature_quality_checks(df, y=None):
    """Comprehensive feature quality analysis"""

    results = {}

    # 1. Low variance
    results['low_variance'] = detect_low_variance_features(df, threshold=0.01)

    # 2. High cardinality
    results['high_cardinality'] = detect_high_cardinality_features(df, threshold=50)

    # 3. Multicollinearity
    numerical_df = df.select_dtypes(include=[np.number])
    results['multicollinearity'] = detect_multicollinearity(numerical_df, threshold=0.90)
    results['vif'] = calculate_vif(numerical_df)

    # 4. Sparse features
    results['sparse_features'] = detect_sparse_features(df, threshold=0.90)

    # Summary
    critical_issues = (
        len(results['low_variance'][results['low_variance']['severity'] == 'CRITICAL']) +
        len(results['high_cardinality'][results['high_cardinality']['severity'] == 'CRITICAL']) +
        len(results['multicollinearity'][results['multicollinearity']['severity'] == 'CRITICAL']) +
        len(results['sparse_features'][results['sparse_features']['severity'] == 'CRITICAL'])
    )

    high_issues = (
        len(results['low_variance'][results['low_variance']['severity'] == 'HIGH']) +
        len(results['high_cardinality'][results['high_cardinality']['severity'] == 'HIGH']) +
        len(results['multicollinearity'][results['multicollinearity']['severity'] == 'HIGH']) +
        len(results['sparse_features'][results['sparse_features']['severity'] == 'HIGH'])
    )

    results['summary'] = {
        'critical_issues': critical_issues,
        'high_issues': high_issues,
        'total_issues': critical_issues + high_issues,
        'verdict': 'PASS' if critical_issues == 0 else 'FAIL'
    }

    return results

# Example usage
quality_results = run_feature_quality_checks(df, y=df['target'])

print(f"\nFeature Quality Summary:")
print(f"Critical issues: {quality_results['summary']['critical_issues']}")
print(f"High priority issues: {quality_results['summary']['high_issues']}")
print(f"Verdict: {quality_results['summary']['verdict']}")

if quality_results['summary']['critical_issues'] > 0:
    print("🔴 Fix critical feature quality issues before training")
elif quality_results['summary']['high_issues'] > 5:
    print("🟠 Consider fixing high-priority feature quality issues")
else:
    print("✅ Feature quality acceptable")
```

---

## Gate Enforcement

**Should fix before training**:
- [ ] No zero-variance features
- [ ] No features with >95% sparsity (or use sparse representation)
- [ ] No categorical features with >100 unique values (or use alternative encoding)
- [ ] No feature pairs with correlation >0.95 (or remove redundant features)
- [ ] No features with VIF >10 (or apply PCA/remove)

**Verification Command**:
```bash
python atools/data_quality_checker.py --full-feature-quality-check \
    --input data.csv \
    --target target \
    --output feature_quality_report.json
```

**Expected Output**: Critical issues = 0, verdict = "ACCEPTABLE QUALITY"

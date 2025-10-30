# High Priority Issues (Should Fix Before Training)

**Priority Level**: 🟠 HIGH
**Action Required**: Fix before training (if time permits)
**Gate**: Model will train but may perform poorly or be fragile

High-priority data issues degrade model performance significantly. While not showstoppers, these issues should be addressed before investing in extensive training/tuning.

---

## What Makes a Data Issue High Priority?

**Severe Class Imbalance**:
- Imbalance ratio >100:1 (e.g., 0.1% fraud rate)
- Minority class underrepresented → model ignores rare cases
- Requires resampling or class weighting

**High Missingness**:
- 20-40% missing values in important features
- Information loss reduces model capacity
- May need imputation or feature engineering

**Significant Bias/Disparities**:
- Protected group disparities in predictions (>10% gap)
- Proxy variables correlated with sensitive attributes
- Fairness implications

**Distribution Shift**:
- Train/test distributions differ significantly
- Model learns one distribution, deploys to another
- Performance degradation in production

---

## Severe Class Imbalance (HIGH)

### Extreme Minority Class

**Why High**: Model achieves high accuracy by ignoring minority class

**Example**:
```python
# HIGH: Fraud rate 0.08% (imbalance ratio 1250:1)
print(df['is_fraud'].value_counts(normalize=True))
# 0    0.9992  ← 99.92% normal
# 1    0.0008  ← 0.08% fraud

# Naive baseline: predict all "not fraud" = 99.92% accuracy!
# But model catches 0% of fraud cases
```

**Diagnosis**: Model can cheat by predicting majority class exclusively

**Fix Options**:
```python
# Option 1: Undersample majority class
from imblearn.under_sampling import RandomUnderSampler
sampler = RandomUnderSampler(sampling_strategy=0.1)  # Target 10:1 ratio
X_resampled, y_resampled = sampler.fit_resample(X, y)

# Option 2: Oversample minority class (SMOTE)
from imblearn.over_sampling import SMOTE
sampler = SMOTE(sampling_strategy=0.1)
X_resampled, y_resampled = sampler.fit_resample(X, y)

# Option 3: Class weights in model
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight('balanced', classes=[0, 1], y=y)
# Use in model: model.fit(X, y, class_weight={0: class_weights[0], 1: class_weights[1]})

# Option 4: Focal loss (penalizes easy examples)
# For neural networks, use focal loss instead of binary crossentropy
```

**Should fix before training**: Imbalance ratio >100:1

**Verification**:
```python
# After fix: check new class distribution
print(y_resampled.value_counts(normalize=True))
# Target: minority class ≥1% of dataset

# Check model doesn't default to majority class
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))
# Ensure recall and precision >0 for minority class
```

---

### Dataset Too Small

**Why High**: Insufficient data prevents proper train/test split and limits model capacity

**Example**:
```python
# HIGH: Only 150 fraud cases in dataset
fraud_count = len(df[df['is_fraud'] == 1])
print(f"Minority class samples: {fraud_count}")
# 150 fraud cases

# Standard 80/20 split:
train_fraud = int(fraud_count * 0.8)  # 120 training fraud cases
test_fraud = fraud_count - train_fraud  # 30 test fraud cases

# Problem: Only 30 test fraud cases → unreliable evaluation
# With 30 cases, precision/recall estimates have ±18% margin of error
```

**Diagnosis**: Test set too small for reliable evaluation

**Fix Options**:
```python
# Option 1: Use stratified K-fold cross-validation
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    # Train and evaluate on each fold

# Option 2: Collect more data (if possible)
# Target: ≥500 minority class samples for reliable evaluation

# Option 3: Use transfer learning
# Pre-train on related dataset, fine-tune on small dataset
```

**Should fix before training**: <200 minority class samples total

**Verification**:
```python
# Calculate confidence intervals for metrics
from scipy import stats
n = len(y_test_minority)
accuracy = 0.85
ci_95 = 1.96 * np.sqrt((accuracy * (1 - accuracy)) / n)
print(f"95% CI: {accuracy} ± {ci_95:.3f}")
# Target: CI width <0.10 (requires n ≥384)
```

---

## High Missingness (HIGH)

### Critical Features with 20-40% Nulls

**Why High**: Information loss degrades model performance

**Example**:
```python
# HIGH: Income field 32% missing
missingness = df.isnull().mean().sort_values(ascending=False)
print(missingness[missingness > 0.2])
# income            0.32  ← HIGH
# employer          0.28  ← HIGH
# credit_score      0.22  ← HIGH

# Impact: Model trained on 68% of data (lost 32% of information)
```

**Diagnosis**: Significant information loss in important features

**Fix Options**:
```python
# Option 1: Median/Mode imputation
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')  # For numerical
df['income'] = imputer.fit_transform(df[['income']])

# Option 2: Predictive imputation (use other features to predict)
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
imputer = IterativeImputer(random_state=42)
df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

# Option 3: Create "missing" indicator + impute
df['income_missing'] = df['income'].isnull().astype(int)
df['income'] = df['income'].fillna(df['income'].median())

# Option 4: Drop feature if not critical
df = df.drop(columns=['income'])  # Last resort
```

**Should fix before training**: >20% missingness in top 10 features

**Verification**:
```python
# After fix: check no high missingness remains
missingness_after = df.isnull().mean().sort_values(ascending=False)
assert (missingness_after > 0.2).sum() == 0, "Still have high missingness"

# Check imputation quality (if using predictive imputation)
from sklearn.metrics import r2_score
# Mask some non-null values, predict them, measure R²
# Target R² >0.5 for good imputation
```

---

## Significant Bias/Disparities (HIGH)

### Protected Group Disparities

**Why High**: Algorithmic fairness implications, potential legal/ethical issues

**Example**:
```python
# HIGH: Loan approval rate differs by race
approval_by_race = df.groupby('race')['approved'].mean()
print(approval_by_race)
# White     0.78  ← 78% approval
# Black     0.62  ← 62% approval
# Disparity: 16 percentage points

# Adverse impact ratio: 0.62 / 0.78 = 0.79
# Fails 80% rule (should be ≥0.80)
```

**Diagnosis**: Model may perpetuate or amplify societal biases

**Fix Options**:
```python
# Option 1: Remove proxy variables
# Check for features correlated with protected attributes
from scipy.stats import chi2_contingency
for col in df.columns:
    contingency_table = pd.crosstab(df[col], df['race'])
    chi2, p_value, _, _ = chi2_contingency(contingency_table)
    if p_value < 0.05:
        print(f"{col} correlates with race (p={p_value:.4f})")
        # Consider removing if proxy for race

# Option 2: Fairness constraints during training
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
mitigator = ExponentiatedGradient(base_model, constraints=DemographicParity())
mitigator.fit(X, y, sensitive_features=df['race'])

# Option 3: Post-processing threshold adjustment
# Adjust decision thresholds per group to equalize approval rates

# Option 4: Fairness-aware feature engineering
# Remove features with disparate impact
```

**Should fix before training**: Disparities >10% in outcomes across protected groups

**Verification**:
```python
# After fix: check disparity reduced
approval_by_race_after = df.groupby('race')['approved'].mean()
disparity_after = approval_by_race_after.max() - approval_by_race_after.min()
print(f"Disparity reduced from 16% to {disparity_after * 100:.1f}%")

# Adverse impact ratio
min_rate = approval_by_race_after.min()
max_rate = approval_by_race_after.max()
ai_ratio = min_rate / max_rate
assert ai_ratio >= 0.80, f"Still fails 80% rule (ratio={ai_ratio:.2f})"
```

---

## Distribution Shift (HIGH)

### Train/Test from Different Populations

**Why High**: Model learns one distribution but deploys to another → performance drop

**Example**:
```python
# HIGH: Train data from 2020, test data from 2021
# Distribution shift due to COVID-19 impact

# Check feature distributions
from scipy.stats import ks_2samp
for col in df.select_dtypes(include=[np.number]).columns:
    train_dist = df_train[col].dropna()
    test_dist = df_test[col].dropna()
    statistic, p_value = ks_2samp(train_dist, test_dist)
    if p_value < 0.01:
        print(f"{col}: KS statistic={statistic:.3f}, p={p_value:.4f} ← SHIFT")

# Example output:
# income: KS=0.245, p=0.0001 ← SHIFT
# transaction_volume: KS=0.312, p=0.0000 ← SHIFT
```

**Diagnosis**: Train and test distributions differ significantly

**Fix Options**:
```python
# Option 1: Importance weighting (weight train samples to match test distribution)
from sklearn.utils.class_weight import compute_sample_weight
weights = compute_sample_weight('balanced', y_train)
model.fit(X_train, y_train, sample_weight=weights)

# Option 2: Domain adaptation
# Train model to be invariant to distribution shift
from sklearn.linear_model import RidgeCV
# Add domain adaptation loss term

# Option 3: Re-split data (time-based split if temporal data)
# Use most recent data for test (closest to deployment distribution)
df = df.sort_values('date')
split_point = int(len(df) * 0.8)
df_train = df[:split_point]
df_test = df[split_point:]

# Option 4: Collect new test data from target distribution
```

**Should fix before training**: KS statistic >0.2 for key features

**Verification**:
```python
# After fix: check distribution shift reduced
for col in key_features:
    statistic, p_value = ks_2samp(df_train[col], df_test[col])
    print(f"{col}: KS={statistic:.3f}")
    assert statistic < 0.2, f"{col} still has significant shift"

# Check model performance doesn't degrade on test set
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
performance_drop = train_score - test_score
assert performance_drop < 0.10, f"Performance drops {performance_drop:.1%} (too much!)"
```

---

## Summary: High Priority Issues

| Issue | Threshold | Impact | Fix Complexity |
|-------|-----------|--------|----------------|
| Severe class imbalance | >100:1 ratio | Model ignores minority class | Medium (resampling/weights) |
| Dataset too small | <200 minority samples | Unreliable evaluation | High (collect data) |
| High missingness | >20% nulls in key features | Information loss | Medium (imputation) |
| Bias/disparities | >10% disparity | Fairness implications | High (fairness constraints) |
| Distribution shift | KS >0.2 | Performance degradation | Medium (re-split/weights) |

**Gate**: Fix high-priority issues before extensive training/tuning. Model will train but may underperform or be fragile.

**Verification Checklist**:
- [ ] Class imbalance <100:1 or mitigation applied
- [ ] ≥200 minority class samples (or using cross-validation)
- [ ] No features with >20% missingness
- [ ] Protected group disparities <10%
- [ ] Train/test KS statistic <0.2 for key features

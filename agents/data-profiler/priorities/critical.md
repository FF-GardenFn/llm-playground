# Critical Issues (Blocks Training)

**Priority Level**: 🔴 CRITICAL
**Action Required**: Fix before training model
**Gate**: Cannot proceed with ML training if critical issues exist

Critical data issues guarantee model failure. Training with critical issues wastes resources and produces worthless models.

---

## What Makes a Data Issue Critical?

**Target Leakage**:
- Features contain information not available at prediction time
- Perfect correlation to target (>0.95)
- Model memorizes instead of learning → production failure

**Train/Test Contamination**:
- Sample overlap between train and test sets
- Distribution shift (train and test from different populations)
- Evaluation metrics meaningless

**Severe Data Corruption**:
- >40% missing values in critical features
- Entire columns constant (zero variance)
- Type inconsistencies prevent model training

**Blocking Issues**:
- Cannot load data (file corruption, encoding errors)
- Schema mismatch (expected columns missing)
- Insufficient data (<100 samples per class)

---

## Target Leakage (CRITICAL)

### High Correlation to Target

**Why Critical**: Model learns to cheat—perfect training, random production performance

**Example**:
```python
# CRITICAL: Feature correlation = 0.98 with target
df[['fraud_flag_internal', 'is_fraud']].corr()
#                      fraud_flag_internal  is_fraud
# fraud_flag_internal              1.00       0.98  ← LEAKAGE
# is_fraud                         0.98       1.00
```

**Diagnosis**: fraud_flag_internal is derived from or directly contains is_fraud

**Fix Required**:
```python
# Remove leaked feature
df = df.drop(columns=['fraud_flag_internal'])

# Verify no high correlations remain
correlations = df.corr()['is_fraud'].abs().sort_values(ascending=False)
assert correlations[correlations > 0.95].drop('is_fraud').empty, "Still have leakage!"
```

**Cannot train until**: All features have correlation <0.95 with target

---

### Future Information

**Why Critical**: Features use data from AFTER target event—unavailable at prediction time

**Example**:
```python
# CRITICAL: Chargeback happens after fraud event
df['chargeback_date'] > df['transaction_date']
# 8.3% of rows have future information

# Feature: chargeback_amount (correlation = 0.94)
# Problem: Chargeback only known AFTER fraud confirmed
```

**Diagnosis**: Temporal leakage—feature contains future information

**Fix Required**:
```python
# Remove features with future information
df = df.drop(columns=['chargeback_amount', 'chargeback_date'])

# Verify temporal ordering
for col in ['feature_date_col1', 'feature_date_col2']:
    leakage = df[df[col] > df['target_date']]
    assert len(leakage) == 0, f"Future information in {col}"
```

**Cannot train until**: All feature dates ≤ target event date

---

### Perfect Predictors

**Why Critical**: Single feature achieves 100% accuracy—memorization, not learning

**Example**:
```python
# CRITICAL: Feature achieves perfect accuracy alone
from sklearn.tree import DecisionTreeClassifier

X = df[['account_id']]
y = df['is_fraud']

clf = DecisionTreeClassifier(max_depth=3)
clf.fit(X, y)
accuracy = clf.score(X, y)  # 1.00 → Perfect!

# Diagnosis: account_id is pure identifier (100% unique)
df['account_id'].nunique() / len(df)  # 1.00 → Every row unique
```

**Fix Required**:
```python
# Remove pure identifiers
uniqueness = df.nunique() / len(df)
identifiers = uniqueness[uniqueness > 0.95].index.tolist()

df = df.drop(columns=identifiers)
print(f"Removed identifiers: {identifiers}")
```

**Cannot train until**: No feature achieves >98% accuracy alone

---

## Train/Test Contamination (CRITICAL)

### Sample Overlap

**Why Critical**: Test set contaminated—evaluation metrics meaningless

**Example**:
```python
# CRITICAL: 247 samples in both train and test
train_ids = set(train_df['user_id'])
test_ids = set(test_df['user_id'])
overlap = train_ids & test_ids

len(overlap)  # 247 samples

# Problem: Model sees test samples during training
```

**Diagnosis**: Train/test split created incorrectly (duplicates, temporal overlap)

**Fix Required**:
```python
# Remove overlap from test set
test_df_clean = test_df[~test_df['user_id'].isin(overlap)]

# Verify zero overlap
train_ids_clean = set(train_df['user_id'])
test_ids_clean = set(test_df_clean['user_id'])
assert len(train_ids_clean & test_ids_clean) == 0, "Still have overlap!"

print(f"Removed {len(overlap)} overlapping samples from test set")
```

**Cannot train until**: Zero sample overlap between train and test

---

### Distribution Shift

**Why Critical**: Test set not representative—model won't generalize

**Example**:
```python
# CRITICAL: Train and test from different distributions
from scipy.stats import ks_2samp

# Compare age distributions
stat, p_value = ks_2samp(train_df['age'], test_df['age'])
print(f"KS statistic: {stat:.3f}, p-value: {p_value:.4f}")
# KS statistic: 0.342, p-value: 0.0001 ← SIGNIFICANT SHIFT

# Diagnosis: Train has age range 18-65, test has 65-90
train_df['age'].describe()  # mean: 35, max: 65
test_df['age'].describe()   # mean: 72, max: 90
```

**Fix Required**:
```python
# Option 1: Resample test set to match train distribution (if possible)
# Option 2: Combine and re-split with stratification

from sklearn.model_selection import train_test_split

# Combine and re-split
df = pd.concat([train_df, test_df])
train, test = train_test_split(
    df,
    test_size=0.2,
    stratify=df['target'],  # Match target distribution
    random_state=42
)

# Verify distributions match
stat, p_value = ks_2samp(train['age'], test['age'])
assert p_value > 0.05, "Still have distribution shift!"
```

**Cannot train until**: Train/test distributions match (KS p-value >0.05)

---

### Stratification Failure

**Why Critical**: Test set imbalance differs from train—biased evaluation

**Example**:
```python
# CRITICAL: Train and test have different class ratios
train_df['is_fraud'].value_counts(normalize=True)
# 0    0.992  ← 0.8% fraud
# 1    0.008

test_df['is_fraud'].value_counts(normalize=True)
# 0    0.950  ← 5% fraud (6x higher!)
# 1    0.050

# Diagnosis: Test set not stratified—overrepresents fraud cases
```

**Fix Required**:
```python
# Re-split with stratification
train, test = train_test_split(
    df,
    test_size=0.2,
    stratify=df['is_fraud'],  # Match fraud rate
    random_state=42
)

# Verify stratification
train_fraud_rate = train['is_fraud'].mean()
test_fraud_rate = test['is_fraud'].mean()

assert abs(train_fraud_rate - test_fraud_rate) < 0.01, "Stratification failed!"
print(f"Train fraud rate: {train_fraud_rate:.3%}")
print(f"Test fraud rate: {test_fraud_rate:.3%}")
```

**Cannot train until**: Train/test class ratios match (within 1%)

---

## Severe Data Corruption (CRITICAL)

### Extreme Missingness (>40%)

**Why Critical**: Insufficient data to train—imputation unreliable

**Example**:
```python
# CRITICAL: 41.3% missing in key feature
df['device_id'].isnull().sum() / len(df)  # 0.413 → 41.3% missing

# Problem: Too many nulls for reliable imputation
# Context: device_id is critical for fraud detection
```

**Diagnosis**: Data collection failure, missing not at random (MNAR)

**Fix Required**:
```python
# Option 1: Drop column if not critical
df = df.drop(columns=['device_id'])

# Option 2: Treat as categorical 'unknown' (if meaningful)
df['device_id'] = df['device_id'].fillna('UNKNOWN')

# Option 3: Collect more data
print(f"Need to collect device_id for {df['device_id'].isnull().sum()} rows")
```

**Cannot train until**: All critical features have <20% missing (or handled appropriately)

---

### Zero Variance

**Why Critical**: Feature contains no information—useless for training

**Example**:
```python
# CRITICAL: Entire column has same value
df['status'].nunique()  # 1 → Only one unique value
df['status'].value_counts()
# active    125430  ← All rows have 'active'

# Variance check
df['status'].var()  # NaN or 0 → No variance
```

**Diagnosis**: Feature constant across all samples (no discriminative power)

**Fix Required**:
```python
# Remove zero-variance features
low_variance_cols = [col for col in df.columns if df[col].nunique() == 1]

df = df.drop(columns=low_variance_cols)
print(f"Removed zero-variance features: {low_variance_cols}")

# Verify remaining features have variance
for col in df.select_dtypes(include=[np.number]).columns:
    assert df[col].var() > 0, f"{col} has zero variance!"
```

**Cannot train until**: All features have variance >0

---

### Type Inconsistencies

**Why Critical**: Cannot train model with mixed or incompatible types

**Example**:
```python
# CRITICAL: Numeric column stored as string
df['age'].dtype  # object (should be int or float)
df['age'].sample(5)
# 23
# 45
# "N/A"  ← String mixed with numbers
# 67
# "unknown"

# Problem: Cannot compute statistics or train model
df['age'].mean()  # TypeError: cannot perform reduce with flexible type
```

**Diagnosis**: Data quality issue—mixed types prevent training

**Fix Required**:
```python
# Convert to numeric, coerce errors to NaN
df['age'] = pd.to_numeric(df['age'], errors='coerce')

# Check how many values became NaN
nulls_created = df['age'].isnull().sum() - original_nulls
print(f"Created {nulls_created} NaNs from type conversion")

# Handle NaNs (impute or remove)
df['age'] = df['age'].fillna(df['age'].median())

# Verify type
assert df['age'].dtype in [np.int64, np.float64], "Age still not numeric!"
```

**Cannot train until**: All numeric features have numeric types, all categorical features have object/category types

---

## Blocking Issues (CRITICAL)

### File Corruption

**Why Critical**: Cannot load data—no training possible

**Example**:
```python
# CRITICAL: Cannot read CSV
try:
    df = pd.read_csv('train.csv')
except UnicodeDecodeError:
    print("ERROR: File encoding issue")

# Problem: File has encoding errors or is corrupted
```

**Fix Required**:
```python
# Try different encodings
encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']

for encoding in encodings:
    try:
        df = pd.read_csv('train.csv', encoding=encoding)
        print(f"Success with encoding: {encoding}")
        break
    except UnicodeDecodeError:
        continue
else:
    print("CRITICAL: Cannot read file with any standard encoding")
    # Escalate to data provider
```

**Cannot train until**: File can be loaded without errors

---

### Insufficient Data

**Why Critical**: Not enough samples to train—model will overfit

**Example**:
```python
# CRITICAL: Only 47 positive samples
df['is_fraud'].value_counts()
# 0    125383
# 1        47  ← Too few positive samples

# Rule of thumb: Need ≥100 samples per class
```

**Diagnosis**: Severe class imbalance with insufficient minority class

**Fix Required**:
```python
# Option 1: Collect more data (preferred)
print(f"Need at least 100 fraud samples, have {(df['is_fraud'] == 1).sum()}")

# Option 2: Anomaly detection (one-class SVM, isolation forest)
# Treat as outlier detection instead of classification

# Option 3: Wait until more data available
print("Cannot train supervised model with <100 positive samples")
```

**Cannot train until**: ≥100 samples per class (for classification)

---

## Critical Issue Response Pattern

**When critical issue found**:

1. **Mark as CRITICAL** with 🔴 indicator
2. **Explain severity**: Why this blocks training (leakage, contamination, corruption)
3. **Provide fix**: Exact code to resolve issue
4. **Include verification**: How to test the fix
5. **Block training**: "Cannot train until [specific criteria met]"

**Example**:
```markdown
### 🔴 CRITICAL: Target Leakage (feature_x: correlation = 0.98)

**Severity**: CRITICAL - Model will fail in production

**Issue**:
```python
df[['feature_x', 'is_fraud']].corr()
# feature_x  is_fraud
# 0.98       1.00  ← Suspiciously high correlation
```

**Diagnosis**: feature_x appears to be derived from or directly contain is_fraud

**Impact**:
- Training accuracy: 99%+ (model memorizes feature_x)
- Production accuracy: 50% (random guessing - feature_x not available)
- Wasted resources training useless model

**Fix**:
```python
df = df.drop(columns=['feature_x'])

# Verify no high correlations remain
correlations = df.corr()['is_fraud'].abs().sort_values(ascending=False)
assert correlations.drop('is_fraud').max() < 0.95, "Still have leakage!"
```

**Verification**:
```python
# Re-run leakage detection
python leakage_detector.py --train train_cleaned.csv --target is_fraud --correlation_threshold 0.95
# Expected: No features flagged
```

**Cannot train until**: All features have correlation <0.95 with target.
```

---

## Gate Enforcement

**Critical issues BLOCK training**:

- [ ] **Target leakage** resolved (correlation <0.95, no future info, no perfect predictors)
- [ ] **Train/test contamination** fixed (zero overlap, distributions match, stratification correct)
- [ ] **Severe data corruption** addressed (missingness <40%, variance >0, types consistent)
- [ ] **Blocking issues** fixed (file loads, sufficient data, schema valid)

**If ANY critical issue unchecked, CANNOT train model.**

**This is not optional. This is a gate.**

---

## Summary

**Critical data issues**:
- Target leakage → Correlation <0.95, no future info, remove identifiers
- Train/test contamination → Zero overlap, distributions match, proper stratification
- Severe corruption → Missingness <40%, variance >0, consistent types
- Blocking issues → File loads, ≥100 samples per class, schema valid

**All critical issues must be resolved before training.**

**Training with critical issues guarantees model failure.**

**No exceptions.**

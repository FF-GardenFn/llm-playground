# Target Leakage Detection

**Category**: ML-Specific Risks
**Severity**: Critical
**Priority**: Blocks training

Target leakage is the **#1 ML failure mode**. A model with leaked features achieves perfect training accuracy but fails catastrophically in production.

---

## What is Target Leakage?

**Definition**: Features that contain information about the target that would not be available at prediction time.

**Why Critical**: Model learns to cheat—memorizes target instead of learning patterns. Production performance: random guessing.

**Common Forms**:
1. **Direct Leakage**: Feature directly contains target value
2. **Temporal Leakage**: Feature uses future information
3. **Derived Leakage**: Feature computed from target
4. **Proxy Leakage**: Feature perfectly correlates with target (suspiciously high correlation)

---

## Detection Methods

### 1. Correlation Analysis (Primary Method)

**High correlation** (>0.95) to target suggests leakage:

```python
import pandas as pd

# Compute correlation with target
correlations = df.corr()['target'].abs().sort_values(ascending=False)

# Flag suspicious features
leakage_suspects = correlations[correlations > 0.95]
print("Potential leakage:")
print(leakage_suspects)

# Output:
# target                   1.00  ← Expected
# fraud_flag_internal      1.00  ← LEAKAGE! Exact match
# chargeback_amount        0.94  ← LEAKAGE! Future info
# transaction_id           0.02  ← OK (pure identifier, remove anyway)
```

**Thresholds**:
- **1.00**: Perfect correlation → Direct leakage
- **0.95-0.99**: Suspiciously high → Investigate immediately
- **0.85-0.94**: High correlation → Verify not leakage
- **< 0.85**: Normal range

---

### 2. Perfect Predictor Check

**Perfect predictors** (100% accuracy on single feature):

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Check each feature individually
for column in df.columns:
    if column == 'target':
        continue

    X = df[[column]].fillna(-999)  # Handle nulls
    y = df['target']

    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X, y)
    accuracy = accuracy_score(y, clf.predict(X))

    if accuracy > 0.98:
        print(f"LEAKAGE: {column} achieves {accuracy:.2%} accuracy alone")

# Output:
# LEAKAGE: fraud_flag_internal achieves 100.00% accuracy alone
```

---

### 3. Feature Importance Spike

**Single feature dominates** importance:

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Get feature importances
importances = pd.DataFrame({
    'feature': X_train.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print(importances.head(10))

# LEAKAGE if one feature >70% importance:
# fraud_flag_internal    0.95  ← LEAKAGE! Dominates all others
# transaction_amount     0.02
# merchant_id            0.01
```

---

### 4. Temporal Validation

**Future information** in training data:

```python
# Check if feature dates are AFTER target event dates
def check_temporal_leakage(df, feature_date_col, target_date_col):
    leakage_rows = df[df[feature_date_col] > df[target_date_col]]
    leakage_pct = len(leakage_rows) / len(df) * 100

    if leakage_pct > 0:
        print(f"LEAKAGE: {feature_date_col} contains future info in {leakage_pct:.2f}% of rows")
        return leakage_rows
    else:
        print(f"OK: {feature_date_col} does not contain future info")
        return None

# Example: Chargeback happens AFTER transaction
check_temporal_leakage(df, 'chargeback_date', 'transaction_date')
# Output: LEAKAGE: chargeback_date contains future info in 8.3% of rows
```

---

## Common Leakage Patterns

### Pattern 1: Direct Target Copy

**Example**: Binary classification with leaked label

```python
# Dataset has 'is_fraud' target and 'fraud_flag_internal' feature
df['target'].corr(df['fraud_flag_internal'])  # 1.00 → Perfect correlation

# Diagnosis:
# fraud_flag_internal is the same as target (internal label leaked into features)
```

**Fix**: Remove fraud_flag_internal immediately

**Verification**:
```python
df = df.drop(columns=['fraud_flag_internal'])
```

---

### Pattern 2: Future Information

**Example**: Predicting churn using data from AFTER churn event

```python
# Target: user_churned (binary)
# Feature: chargeback_amount (amount charged back AFTER churn)

# Diagnosis:
# Chargebacks happen after user churns, so this is future information
```

**Fix**: Remove features computed after target event

**Verification**:
```python
# Check feature date vs target date
df['chargeback_date'] > df['churn_date']  # Should be False for all rows
```

---

### Pattern 3: Derived from Target

**Example**: Feature computed using target value

```python
# Target: loan_default (binary)
# Feature: days_until_default (computed as: default_date - loan_date)

# Diagnosis:
# days_until_default requires knowing default_date, which is the target event
```

**Fix**: Remove features that require target to compute

**Verification**:
```python
# Can you compute this feature without knowing the target? No → Leakage
df = df.drop(columns=['days_until_default'])
```

---

### Pattern 4: Identifier Leakage

**Example**: Using unique identifiers as features

```python
# Feature: transaction_id (100% unique)
df['transaction_id'].nunique() / len(df)  # 1.00 → Every row unique

# Diagnosis:
# Model memorizes transaction_id → target mapping
# Works on training data, random guessing in production (new IDs)
```

**Fix**: Remove pure identifiers (>95% unique values)

**Verification**:
```python
# Check uniqueness ratio
uniqueness = df.nunique() / len(df)
identifiers = uniqueness[uniqueness > 0.95].index.tolist()
print(f"Identifiers to remove: {identifiers}")

df = df.drop(columns=identifiers)
```

---

### Pattern 5: Aggregated Leakage

**Example**: Feature aggregates data including target row

```python
# Feature: merchant_fraud_rate (% of fraud for this merchant)
# Computed as: fraud count / total transactions for merchant

# Diagnosis:
# merchant_fraud_rate includes the CURRENT transaction in the calculation
# This creates leakage because the current fraud status affects the rate
```

**Fix**: Compute aggregations excluding current row (leave-one-out)

**Verification**:
```python
# Correct aggregation (leave-one-out)
def compute_merchant_fraud_rate_loo(df):
    merchant_fraud_counts = df.groupby('merchant_id')['is_fraud'].transform('sum')
    merchant_transaction_counts = df.groupby('merchant_id')['is_fraud'].transform('count')

    # Subtract current row
    merchant_fraud_counts -= df['is_fraud']
    merchant_transaction_counts -= 1

    return merchant_fraud_counts / merchant_transaction_counts

df['merchant_fraud_rate'] = compute_merchant_fraud_rate_loo(df)
```

---

## Automated Leakage Detection

### Using leakage_detector.py

```bash
# Detect leakage via correlation
python leakage_detector.py --train train.csv --target is_fraud --correlation_threshold 0.95

# Output:
# CRITICAL LEAKAGE DETECTED:
# | Feature             | Correlation | Risk     | Reason                          |
# |---------------------|-------------|----------|---------------------------------|
# | fraud_flag_internal | 1.00        | CRITICAL | Exact match to target           |
# | chargeback_amount   | 0.94        | CRITICAL | Future information (post-event) |
# | transaction_id      | 0.02        | HIGH     | Pure identifier (98% unique)    |
```

### Using pandas profiling

```python
import pandas as pd

def detect_leakage(df, target_col):
    """Automated leakage detection"""

    # 1. Correlation check
    correlations = df.corr()[target_col].abs().sort_values(ascending=False)
    high_corr = correlations[(correlations > 0.95) & (correlations < 1.0)]

    # 2. Uniqueness check (identifiers)
    uniqueness = df.nunique() / len(df)
    identifiers = uniqueness[uniqueness > 0.95].index.tolist()
    if target_col in identifiers:
        identifiers.remove(target_col)

    # 3. Perfect predictor check
    from sklearn.tree import DecisionTreeClassifier
    perfect_predictors = []

    for col in df.columns:
        if col == target_col:
            continue

        X = df[[col]].fillna(-999)
        y = df[target_col]

        clf = DecisionTreeClassifier(max_depth=3, random_state=42)
        clf.fit(X, y)

        if clf.score(X, y) > 0.98:
            perfect_predictors.append(col)

    # Report findings
    print("LEAKAGE DETECTION REPORT")
    print("=" * 50)

    if high_corr.empty and not identifiers and not perfect_predictors:
        print("✓ No leakage detected")
    else:
        if not high_corr.empty:
            print(f"\n🔴 HIGH CORRELATION (>{0.95}):")
            print(high_corr)

        if identifiers:
            print(f"\n🔴 IDENTIFIERS (>95% unique):")
            for identifier in identifiers:
                print(f"  - {identifier}: {uniqueness[identifier]:.2%} unique")

        if perfect_predictors:
            print(f"\n🔴 PERFECT PREDICTORS (>98% accuracy alone):")
            for pred in perfect_predictors:
                print(f"  - {pred}")

    return {
        'high_correlation': high_corr.index.tolist(),
        'identifiers': identifiers,
        'perfect_predictors': perfect_predictors
    }

# Usage
leakage_report = detect_leakage(df, 'is_fraud')
```

---

## Verification After Removal

**After removing suspected leakage, verify**:

```python
# 1. Re-run correlation analysis
correlations = df.corr()['target'].abs().sort_values(ascending=False)
assert correlations.max() < 0.95, "Still have high correlation!"

# 2. Re-check uniqueness
uniqueness = df.nunique() / len(df)
assert uniqueness.max() < 0.95, "Still have identifiers!"

# 3. Train simple model (should NOT get perfect accuracy)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

rf = RandomForestClassifier(n_estimators=100, random_state=42)
scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy')

print(f"Cross-validation accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

# If accuracy >0.95, still have leakage
# Reasonable baseline for binary classification: 0.60-0.85
```

---

## Production Validation

**Test for leakage in production**:

1. **Monitor feature availability**:
   - Are leaked features available at prediction time?
   - Example: chargeback_amount not available until after prediction

2. **Backtesting**:
   - Use only data available at prediction time
   - Example: Use transaction data up to T, predict fraud at T, validate at T+30 days

3. **Online A/B test**:
   - Deploy model to small fraction of traffic
   - Monitor if performance matches offline metrics
   - If offline 95% accuracy → online 55% accuracy: **LEAKAGE**

---

## Leakage Checklist

Before training model:

- [ ] **Correlation check**: No features with correlation >0.95 to target
- [ ] **Uniqueness check**: No pure identifiers (>95% unique values)
- [ ] **Perfect predictor check**: No single feature achieves >98% accuracy
- [ ] **Temporal validation**: All feature dates ≤ target event date
- [ ] **Derived feature check**: No features computed using target
- [ ] **Aggregation check**: Aggregations use leave-one-out (exclude current row)
- [ ] **Production validation**: Features available at prediction time

**If ANY unchecked, dataset may have leakage.**

---

## Summary

**Target leakage detection**:
- High correlation (>0.95) → Investigate immediately
- Perfect predictors (100% accuracy alone) → Remove
- Future information → Temporal validation
- Derived from target → Logic review
- Identifiers (>95% unique) → Remove

**Prevention**:
- Think "What information is available at prediction time?"
- Verify feature dates ≤ target event date
- Use leave-one-out for aggregations
- Test production feature availability

**Cannot train model with target leakage.**

**This is a gate.**

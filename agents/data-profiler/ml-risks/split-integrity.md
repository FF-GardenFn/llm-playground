# Split Integrity (Train/Test Contamination)

**Risk Category**: 🔴 ML RISK - CRITICAL
**Impact**: Inflated evaluation metrics, production failure
**Detection**: Distribution analysis, overlap detection, stratification verification

Train/test contamination makes evaluation metrics meaningless. Models appear to perform well in validation but fail catastrophically in production.

---

## What is Split Integrity?

Train/test split integrity ensures:
1. **No sample overlap** between train and test sets
2. **Representative distributions** in both train and test
3. **Proper stratification** for class balance
4. **No data leakage** through temporal ordering or group structure

**Why Critical**: Invalid evaluation → deploy broken models with false confidence

---

## Detection Methods

###  1. Sample Overlap Detection

**Goal**: Verify no identical samples in both train and test

**Method**: Hash-based duplicate detection across splits

**Code**:
```python
import pandas as pd
import hashlib

def detect_train_test_overlap(X_train, X_test):
    """Detect if any samples appear in both train and test"""

    # Create hash for each row
    def hash_row(row):
        return hashlib.md5(str(row.values).encode()).hexdigest()

    train_hashes = set(X_train.apply(hash_row, axis=1))
    test_hashes = set(X_test.apply(hash_row, axis=1))

    overlap = train_hashes & test_hashes
    overlap_count = len(overlap)
    overlap_pct = overlap_count / len(X_test) * 100

    return {
        'overlap_count': overlap_count,
        'overlap_pct': overlap_pct,
        'test_size': len(X_test),
        'verdict': 'FAIL' if overlap_count > 0 else 'PASS'
    }

# Example usage
result = detect_train_test_overlap(X_train, X_test)
print(f"Train/test overlap: {result['overlap_count']} samples ({result['overlap_pct']:.2f}%)")
print(f"Verdict: {result['verdict']}")

# CRITICAL: overlap_count must be 0
assert result['overlap_count'] == 0, "Train/test contamination detected!"
```

**Tool Integration**:
```bash
python atools/leakage_detector.py --check-overlap --train train.csv --test test.csv
```

**Interpretation**:
- `overlap_count = 0`: ✅ No contamination
- `overlap_count > 0`: 🔴 CRITICAL - Train/test contamination

---

### 2. Distribution Shift Analysis

**Goal**: Verify train and test come from same distribution

**Method**: Kolmogorov-Smirnov test for each feature

**Code**:
```python
from scipy.stats import ks_2samp

def analyze_distribution_shift(X_train, X_test, significance=0.05):
    """Test if train and test have same distribution"""

    results = []
    for col in X_train.select_dtypes(include=[np.number]).columns:
        train_dist = X_train[col].dropna()
        test_dist = X_test[col].dropna()

        # Kolmogorov-Smirnov test
        statistic, p_value = ks_2samp(train_dist, test_dist)

        # Interpretation
        shifted = p_value < significance
        severity = 'HIGH' if statistic > 0.2 else ('MEDIUM' if statistic > 0.1 else 'LOW')

        results.append({
            'feature': col,
            'ks_statistic': statistic,
            'p_value': p_value,
            'shifted': shifted,
            'severity': severity
        })

    df_results = pd.DataFrame(results).sort_values('ks_statistic', ascending=False)
    return df_results

# Example usage
shift_analysis = analyze_distribution_shift(X_train, X_test)
print(shift_analysis[shift_analysis['shifted']])

# Check for HIGH severity shifts
high_shifts = shift_analysis[shift_analysis['severity'] == 'HIGH']
if len(high_shifts) > 0:
    print(f"\n🔴 CRITICAL: {len(high_shifts)} features with HIGH distribution shift")
    print(high_shifts[['feature', 'ks_statistic', 'p_value']])
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-distribution-shift --train train.csv --test test.csv
```

**Interpretation**:
- `ks_statistic < 0.1`: ✅ Minimal shift
- `ks_statistic 0.1-0.2`: ⚠️ Moderate shift (investigate)
- `ks_statistic > 0.2`: 🔴 Severe shift (CRITICAL)

**Common Causes**:
- Temporal data: train from 2020, test from 2021 (COVID shift)
- Geographic data: train from US, test from Europe
- Sampling bias: train from web, test from mobile app

---

### 3. Stratification Verification

**Goal**: Verify class balance preserved in train and test

**Method**: Compare class ratios across splits

**Code**:
```python
def verify_stratification(y_train, y_test, tolerance=0.02):
    """Check if class balance preserved in train/test split"""

    # Calculate class ratios
    train_ratio = y_train.value_counts(normalize=True).sort_index()
    test_ratio = y_test.value_counts(normalize=True).sort_index()

    # Compute difference
    ratio_diff = (train_ratio - test_ratio).abs()
    max_diff = ratio_diff.max()

    results = {
        'train_ratio': train_ratio.to_dict(),
        'test_ratio': test_ratio.to_dict(),
        'max_diff': max_diff,
        'verdict': 'PASS' if max_diff < tolerance else 'FAIL'
    }

    return results

# Example usage
strat_results = verify_stratification(y_train, y_test)
print("Train class ratio:", strat_results['train_ratio'])
print("Test class ratio:", strat_results['test_ratio'])
print(f"Max difference: {strat_results['max_diff']:.4f}")
print(f"Verdict: {strat_results['verdict']}")

# Visualize
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
pd.Series(strat_results['train_ratio']).plot(kind='bar', ax=ax[0], title='Train Class Balance')
pd.Series(strat_results['test_ratio']).plot(kind='bar', ax=ax[1], title='Test Class Balance')
plt.tight_layout()
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-stratification --train-labels train_y.csv --test-labels test_y.csv
```

**Interpretation**:
- `max_diff < 0.02`: ✅ Well stratified (within 2%)
- `max_diff 0.02-0.05`: ⚠️ Moderate imbalance
- `max_diff > 0.05`: 🔴 Poor stratification (CRITICAL)

**Fix**:
```python
from sklearn.model_selection import train_test_split

# Correct way: stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,  # ← CRITICAL: maintains class balance
    random_state=42
)

# Verify stratification
strat_results = verify_stratification(y_train, y_test)
assert strat_results['verdict'] == 'PASS', "Stratification failed!"
```

---

### 4. Temporal Integrity Check

**Goal**: Verify train data precedes test data (for time series)

**Method**: Compare timestamp ranges

**Code**:
```python
def check_temporal_integrity(df_train, df_test, date_col):
    """Verify train dates < test dates (no future information)"""

    train_max_date = df_train[date_col].max()
    test_min_date = df_test[date_col].min()
    test_max_date = df_test[date_col].max()

    # Check for overlap
    overlap = train_max_date >= test_min_date

    # Calculate gap
    if not overlap:
        gap_days = (test_min_date - train_max_date).days
    else:
        overlap_samples = len(df_train[df_train[date_col] >= test_min_date])
        overlap_pct = overlap_samples / len(df_train) * 100

    results = {
        'train_max_date': train_max_date,
        'test_min_date': test_min_date,
        'test_max_date': test_max_date,
        'overlap': overlap,
        'verdict': 'FAIL' if overlap else 'PASS'
    }

    if overlap:
        results['overlap_samples'] = overlap_samples
        results['overlap_pct'] = overlap_pct
    else:
        results['gap_days'] = gap_days

    return results

# Example usage
temporal_results = check_temporal_integrity(df_train, df_test, 'transaction_date')
print(f"Train max date: {temporal_results['train_max_date']}")
print(f"Test min date: {temporal_results['test_min_date']}")
print(f"Temporal overlap: {temporal_results['overlap']}")
print(f"Verdict: {temporal_results['verdict']}")

if temporal_results['overlap']:
    print(f"🔴 CRITICAL: {temporal_results['overlap_samples']} samples overlap ({temporal_results['overlap_pct']:.1f}%)")
else:
    print(f"✅ Gap between train and test: {temporal_results['gap_days']} days")
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-temporal-integrity --train train.csv --test test.csv --date-col transaction_date
```

**Interpretation**:
- `overlap = False`: ✅ Proper temporal split
- `overlap = True`: 🔴 CRITICAL - Temporal leakage

**Fix**:
```python
# Correct temporal split
df_sorted = df.sort_values('transaction_date')
split_date = df_sorted['transaction_date'].quantile(0.8)

df_train = df_sorted[df_sorted['transaction_date'] < split_date]
df_test = df_sorted[df_sorted['transaction_date'] >= split_date]

# Verify
temporal_results = check_temporal_integrity(df_train, df_test, 'transaction_date')
assert temporal_results['verdict'] == 'PASS', "Temporal split failed!"
```

---

### 5. Group Leakage Detection

**Goal**: Verify samples from same group don't span train/test

**Method**: Check for group ID overlap

**Code**:
```python
def detect_group_leakage(df_train, df_test, group_col):
    """Check if same group (e.g., user_id) appears in both train and test"""

    train_groups = set(df_train[group_col].unique())
    test_groups = set(df_test[group_col].unique())

    overlap_groups = train_groups & test_groups
    overlap_count = len(overlap_groups)
    overlap_pct = overlap_count / len(test_groups) * 100

    results = {
        'train_groups': len(train_groups),
        'test_groups': len(test_groups),
        'overlap_groups': overlap_count,
        'overlap_pct': overlap_pct,
        'verdict': 'FAIL' if overlap_count > 0 else 'PASS'
    }

    return results

# Example usage
group_results = detect_group_leakage(df_train, df_test, 'user_id')
print(f"Train groups: {group_results['train_groups']}")
print(f"Test groups: {group_results['test_groups']}")
print(f"Overlapping groups: {group_results['overlap_groups']} ({group_results['overlap_pct']:.1f}%)")
print(f"Verdict: {group_results['verdict']}")

if group_results['verdict'] == 'FAIL':
    print(f"🔴 CRITICAL: {group_results['overlap_groups']} groups appear in both train and test")
```

**Tool Integration**:
```bash
python atools/leakage_detector.py --check-group-leakage --train train.csv --test test.csv --group-col user_id
```

**Interpretation**:
- `overlap_groups = 0`: ✅ No group leakage
- `overlap_groups > 0`: 🔴 CRITICAL - Group leakage

**Why Critical**: If predicting fraud per user, and same user appears in train and test, model memorizes user behavior instead of learning patterns.

**Fix**:
```python
from sklearn.model_selection import GroupShuffleSplit

# Correct way: group-aware split
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups=df['user_id']))

df_train = df.iloc[train_idx]
df_test = df.iloc[test_idx]

# Verify no group overlap
group_results = detect_group_leakage(df_train, df_test, 'user_id')
assert group_results['verdict'] == 'PASS', "Group leakage detected!"
```

---

## Complete Split Integrity Checklist

Run all 5 checks to verify split integrity:

```python
def run_split_integrity_checks(X_train, X_test, y_train, y_test, df_train, df_test, date_col=None, group_col=None):
    """Comprehensive split integrity verification"""

    results = {}

    # 1. Sample overlap
    results['overlap'] = detect_train_test_overlap(X_train, X_test)

    # 2. Distribution shift
    results['distribution_shift'] = analyze_distribution_shift(X_train, X_test)

    # 3. Stratification
    results['stratification'] = verify_stratification(y_train, y_test)

    # 4. Temporal integrity (if time series)
    if date_col:
        results['temporal'] = check_temporal_integrity(df_train, df_test, date_col)

    # 5. Group leakage (if grouped data)
    if group_col:
        results['group_leakage'] = detect_group_leakage(df_train, df_test, group_col)

    # Summary
    all_passed = all([
        results['overlap']['verdict'] == 'PASS',
        results['stratification']['verdict'] == 'PASS',
        len(results['distribution_shift'][results['distribution_shift']['severity'] == 'HIGH']) == 0,
        results.get('temporal', {}).get('verdict', 'PASS') == 'PASS',
        results.get('group_leakage', {}).get('verdict', 'PASS') == 'PASS'
    ])

    results['summary'] = {
        'all_passed': all_passed,
        'verdict': 'PASS' if all_passed else 'FAIL'
    }

    return results

# Example usage
integrity_results = run_split_integrity_checks(
    X_train, X_test, y_train, y_test,
    df_train, df_test,
    date_col='transaction_date',
    group_col='user_id'
)

print(f"\nSplit Integrity Summary: {integrity_results['summary']['verdict']}")
if not integrity_results['summary']['all_passed']:
    print("🔴 CRITICAL: Split integrity violated - DO NOT TRAIN")
else:
    print("✅ Split integrity verified - safe to train")
```

---

## Gate Enforcement

**Cannot train model until**:
- [ ] No sample overlap (overlap_count = 0)
- [ ] No high distribution shift (all features ks_statistic < 0.2)
- [ ] Stratification preserved (max_diff < 0.02)
- [ ] Temporal integrity maintained (no overlap if time series)
- [ ] No group leakage (overlap_groups = 0 if grouped data)

**If any check fails**: Fix split methodology before training.

**Verification Command**:
```bash
python atools/leakage_detector.py --full-split-integrity-check \
    --train train.csv \
    --test test.csv \
    --date-col transaction_date \
    --group-col user_id \
    --output split_integrity_report.json
```

**Expected Output**: All checks PASS, verdict = "SAFE TO TRAIN"

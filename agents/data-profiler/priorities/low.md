# Low Priority Issues (Document and Monitor)

**Priority Level**: 🟢 LOW
**Action Required**: Document, monitor, may not need fixing
**Gate**: No impact on training decision

Low-priority issues are minor quality concerns that don't meaningfully affect model performance. Document for awareness but typically don't require immediate action.

---

## What Makes a Data Issue Low Priority?

**Minor Duplicates**:
- <5% duplicate rows
- May be legitimate repeated transactions
- Easy to handle if needed

**Slight Skewness**:
- Absolute skewness <2
- Normal enough for most models
- Transformation optional

**Documentation Issues**:
- Missing column descriptions
- Unclear feature meanings
- Impacts interpretability, not performance

**Low-Impact Quality Issues**:
- Trailing whitespace in strings
- Inconsistent date formats (but parseable)
- Minor naming inconsistencies

---

## Minor Duplicates (LOW)

### <5% Duplicate Rows

**Why Low**: Small percentage, may be legitimate repeated data

**Example**:
```python
# LOW: 2.3% duplicate rows
duplicate_count = df.duplicated().sum()
duplicate_pct = duplicate_count / len(df)
print(f"Duplicates: {duplicate_count:,} ({duplicate_pct:.1%})")
# Duplicates: 1,150 (2.3%)

# Check if duplicates are exact copies
duplicate_rows = df[df.duplicated(keep=False)]
print(duplicate_rows.head())
# May be legitimate (e.g., multiple transactions from same user)
```

**Diagnosis**: Low percentage, may or may not be errors

**Fix Options**:
```python
# Option 1: Remove exact duplicates
df_deduped = df.drop_duplicates()

# Option 2: Keep first occurrence, drop rest
df_deduped = df.drop_duplicates(keep='first')

# Option 3: Investigate if duplicates are legitimate
# Check if duplicates have different timestamps/IDs
duplicate_subset = df[df.duplicated(subset=['user_id', 'transaction_date'], keep=False)]
# If same user_id + date but different transaction_id → legitimate

# Option 4: Don't remove (if duplicates are real repeated events)
# e.g., Customer made 2 transactions with same amount on same day
```

**Document and monitor**: <5% duplicates

**Verification**:
```python
# If removed: check no exact duplicates remain
assert df_deduped.duplicated().sum() == 0, "Still have duplicates"

# Check model performance change (may be negligible)
# Duplicates inflate performance if same sample in train and test
```

---

## Slight Skewness (LOW)

### Absolute Skewness <2

**Why Low**: Distribution close enough to normal for most models

**Example**:
```python
# LOW: Age slightly right-skewed (skewness = 1.4)
from scipy.stats import skew
skewness = df['age'].skew()
print(f"Age skewness: {skewness:.2f}")  # 1.4

# Distribution: Median=35, Mean=38, Mode=32
# Slightly right-skewed but not extreme
```

**Diagnosis**: Mild skewness, usually not problematic

**Fix Options**:
```python
# Option 1: Leave as-is (tree-based models don't care)
# Most models handle slight skewness fine

# Option 2: Log transformation (if needed for linear models)
df['age_log'] = np.log(df['age'])

# Option 3: Square root transformation (milder than log)
df['age_sqrt'] = np.sqrt(df['age'])
```

**Document and monitor**: Absolute skewness <2

**Verification**:
```python
# Check if transformation improves model
from sklearn.model_selection import cross_val_score
score_original = cross_val_score(model, df[['age']], y, cv=5).mean()
score_transformed = cross_val_score(model, df[['age_log']], y, cv=5).mean()
print(f"Performance: original={score_original:.3f}, transformed={score_transformed:.3f}")
# If difference <1%, transformation not needed
```

---

## Documentation Issues (LOW)

### Missing Column Descriptions

**Why Low**: Doesn't affect model, but impacts interpretability

**Example**:
```python
# LOW: Unclear feature names
print(df.columns.tolist())
# ['feat_1', 'feat_2', 'feat_3', 'var_a', 'var_b', 'metric_x']
# ↑ Unclear what these represent

# No data dictionary available
# Domain experts don't recognize feature names
```

**Diagnosis**: Poor documentation, not a data quality issue

**Fix Options**:
```python
# Option 1: Rename columns to descriptive names
column_mapping = {
    'feat_1': 'transaction_amount',
    'feat_2': 'merchant_category',
    'feat_3': 'days_since_account_opened',
    'var_a': 'avg_transaction_last_30d',
    'var_b': 'num_declines_last_7d',
    'metric_x': 'fraud_score_external'
}
df = df.rename(columns=column_mapping)

# Option 2: Create data dictionary
data_dict = {
    'feat_1': 'Transaction amount in USD',
    'feat_2': 'Merchant category code (MCC)',
    'feat_3': 'Days since account opened',
    # ...
}
# Save as CSV or JSON for reference

# Option 3: Add comments to code
# feat_1 = transaction amount (USD)
# feat_2 = merchant category (e.g., "groceries", "gas")
```

**Document**: Create data dictionary

**Verification**:
```python
# Check all columns have descriptions
for col in df.columns:
    if col not in data_dict:
        print(f"Missing description: {col}")
# Ensure data dictionary is complete
```

---

## Trailing Whitespace (LOW)

### String Columns with Whitespace

**Why Low**: Easy to clean, minimal impact

**Example**:
```python
# LOW: City names have trailing whitespace
print(df['city'].unique()[:5])
# ['New York ', 'Los Angeles', 'Chicago  ', 'Houston', 'Phoenix ']
#            ↑                         ↑↑                      ↑

# Causes: 'New York' ≠ 'New York ' (treated as different values)
```

**Diagnosis**: Data entry issue, easy to clean

**Fix Options**:
```python
# Option 1: Strip whitespace
df['city'] = df['city'].str.strip()

# Option 2: Strip and lowercase (for consistency)
df['city'] = df['city'].str.strip().str.lower()

# Option 3: Strip all string columns
string_cols = df.select_dtypes(include=['object']).columns
for col in string_cols:
    df[col] = df[col].str.strip()
```

**Document and fix**: Trivial cleanup

**Verification**:
```python
# Check no leading/trailing whitespace remains
for col in string_cols:
    has_whitespace = df[col].str.match(r'^\s|\s$', na=False).any()
    assert not has_whitespace, f"{col} still has whitespace"
```

---

## Inconsistent Date Formats (LOW)

### Dates Parseable But Inconsistent

**Why Low**: Can be parsed, just need standardization

**Example**:
```python
# LOW: Dates in mixed formats but all parseable
print(df['date'].unique()[:5])
# ['2021-01-15', '01/20/2021', '2021-02-03', '03/01/2021', '2021-03-10']
#  ↑ YYYY-MM-DD   ↑ MM/DD/YYYY  ↑ YYYY-MM-DD  ↑ MM/DD/YYYY  ↑ YYYY-MM-DD

# All parseable, just inconsistent format
```

**Diagnosis**: Inconsistent formatting, not invalid dates

**Fix Options**:
```python
# Option 1: Parse with pandas (handles mixed formats)
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)

# Option 2: Standardize to single format
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

# Option 3: Parse with dateutil (very flexible)
from dateutil import parser
df['date'] = df['date'].apply(lambda x: parser.parse(x))
```

**Document and fix**: Standardize format

**Verification**:
```python
# Check all dates parsed successfully
assert df['date'].dtype == 'datetime64[ns]', "Dates not parsed as datetime"
assert df['date'].isnull().sum() == 0, "Some dates failed to parse"
```

---

## Minor Naming Inconsistencies (LOW)

### Inconsistent Column Naming Convention

**Why Low**: Aesthetic issue, doesn't affect model

**Example**:
```python
# LOW: Mixed naming conventions
print(df.columns.tolist())
# ['user_id', 'UserName', 'transaction_date', 'Amount', 'merchant_category', 'IsSuccessful']
#  ↑ snake_case  ↑ PascalCase  ↑ snake_case  ↑ PascalCase  ↑ snake_case  ↑ PascalCase

# Inconsistent: mix of snake_case and PascalCase
```

**Diagnosis**: Style inconsistency, not a functional issue

**Fix Options**:
```python
# Option 1: Standardize to snake_case
df.columns = df.columns.str.lower().str.replace(' ', '_')

# Option 2: Standardize to camelCase
def to_camel_case(s):
    parts = s.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])
df.columns = [to_camel_case(col) for col in df.columns]

# Option 3: Leave as-is (if project convention allows)
```

**Document**: Note inconsistency, fix if easy

**Verification**:
```python
# Check naming convention consistent
# All lowercase with underscores (snake_case)
import re
for col in df.columns:
    assert re.match(r'^[a-z][a-z0-9_]*$', col), f"{col} not snake_case"
```

---

## Low Cardinality Categoricals (LOW)

### Features with 2-5 Unique Values

**Why Low**: Already ideal for one-hot encoding

**Example**:
```python
# LOW: Payment method has 3 values
print(df['payment_method'].value_counts())
# credit_card    8,500
# debit_card     3,200
# paypal         1,800

# 3 categories → 2 dummy variables (n-1 encoding)
# Low dimensionality, no issue
```

**Diagnosis**: Ideal categorical cardinality

**Action**: One-hot encode as usual
```python
df_encoded = pd.get_dummies(df, columns=['payment_method'], drop_first=True)
# Creates: payment_method_debit_card, payment_method_paypal
```

**No fix needed**: Low cardinality is optimal

---

## Summary: Low Priority Issues

| Issue | Threshold | Impact | Fix Complexity |
|-------|-----------|--------|----------------|
| Minor duplicates | <5% | Negligible | Trivial (drop_duplicates) |
| Slight skewness | Abs skewness <2 | Minimal | Trivial (optional transform) |
| Documentation gaps | N/A | Interpretability only | Low (create dict) |
| Trailing whitespace | N/A | Minimal | Trivial (str.strip) |
| Inconsistent date formats | N/A | None (if parseable) | Trivial (pd.to_datetime) |
| Naming inconsistencies | N/A | Aesthetic only | Trivial (rename) |

**Gate**: No action required for training. Document for awareness, fix if convenient.

**Documentation Checklist**:
- [ ] Duplicate percentage noted (<5%)
- [ ] Skewness values documented (abs <2)
- [ ] Data dictionary created (column descriptions)
- [ ] Whitespace cleaned (if noticed)
- [ ] Date formats standardized (if time)
- [ ] Naming convention documented (even if inconsistent)

**These issues do not block training or meaningfully affect model quality.**

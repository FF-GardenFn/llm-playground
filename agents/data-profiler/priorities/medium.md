# Medium Priority Issues (Fix If Time Permits)

**Priority Level**: 🟡 MEDIUM
**Action Required**: Fix if time permits, document if not
**Gate**: Model will train and may perform adequately, but has room for improvement

Medium-priority issues affect model quality but don't block training or guarantee failure. Address these to improve performance, but can defer if timeline is tight.

---

## What Makes a Data Issue Medium Priority?

**Moderate Missingness**:
- 10-20% missing values in features
- Reduces model capacity but not catastrophically
- Imputation recommended

**Minor Outliers**:
- 2-5% of samples are extreme values
- May affect model if not handled
- Consider outlier removal or robust scaling

**High Cardinality Categoricals**:
- Categorical features with >50 unique values
- One-hot encoding creates sparse, high-dimensional data
- May need alternative encoding

**Moderate Imbalance**:
- Imbalance ratio 10:1 to 100:1
- Model may still learn minority class
- Class weighting recommended

---

## Moderate Missingness (MEDIUM)

### 10-20% Nulls in Features

**Why Medium**: Information loss but model can still learn

**Example**:
```python
# MEDIUM: Employer field 15% missing
missingness = df.isnull().mean().sort_values(ascending=False)
print(missingness[(missingness >= 0.10) & (missingness < 0.20)])
# employer          0.15  ← MEDIUM
# phone_number      0.12  ← MEDIUM
# secondary_email   0.11  ← MEDIUM

# Impact: Model trained on 85-89% of data (moderate information loss)
```

**Diagnosis**: Moderate information loss, imputation recommended

**Fix Options**:
```python
# Option 1: Mode imputation (categorical)
df['employer'] = df['employer'].fillna(df['employer'].mode()[0])

# Option 2: Create "Unknown" category
df['employer'] = df['employer'].fillna('Unknown')

# Option 3: Predictive imputation
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=5)
df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

# Option 4: Missing indicator + imputation
df['employer_missing'] = df['employer'].isnull().astype(int)
df['employer'] = df['employer'].fillna('Unknown')
```

**Fix if time permits**: 10-20% missingness

**Verification**:
```python
# Check missingness reduced
missingness_after = df.isnull().mean()
assert (missingness_after >= 0.10).sum() < 5, "Too many features with moderate missingness"

# Check model performance improves
from sklearn.model_selection import cross_val_score
score_before_imputation = cross_val_score(model, X_before, y, cv=5).mean()
score_after_imputation = cross_val_score(model, X_after, y, cv=5).mean()
print(f"Score improved: {score_before_imputation:.3f} → {score_after_imputation:.3f}")
```

---

## Minor Outliers (MEDIUM)

### 2-5% Extreme Values

**Why Medium**: May skew model if not handled, but small impact

**Example**:
```python
# MEDIUM: Income has 3% outliers (>$1M)
from scipy.stats import zscore
z_scores = np.abs(zscore(df['income'].dropna()))
outlier_pct = (z_scores > 3).mean()
print(f"Outliers (z>3): {outlier_pct:.1%}")  # 3.2%

# Check outlier values
print(df[z_scores > 3]['income'].describe())
#        count     mean       std      min      max
#         480    1.2M      450K     800K     5.2M  ← Extreme

# Typical income: median = $65K
# Outliers: $800K - $5.2M (12x - 80x median)
```

**Diagnosis**: Extreme values may disproportionately influence model

**Fix Options**:
```python
# Option 1: Winsorization (cap at percentile)
from scipy.stats.mstats import winsorize
df['income'] = winsorize(df['income'], limits=[0.01, 0.01])  # Cap at 1st/99th percentile

# Option 2: Log transformation (reduce range)
df['income_log'] = np.log1p(df['income'])  # log(1+x) handles zeros

# Option 3: Robust scaling (median/IQR instead of mean/std)
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
df['income_scaled'] = scaler.fit_transform(df[['income']])

# Option 4: Remove extreme outliers (>4 standard deviations)
df = df[np.abs(zscore(df['income'])) < 4]
```

**Fix if time permits**: >2% outliers

**Verification**:
```python
# Check outlier percentage reduced
z_scores_after = np.abs(zscore(df['income']))
outlier_pct_after = (z_scores_after > 3).mean()
print(f"Outliers reduced: {outlier_pct:.1%} → {outlier_pct_after:.1%}")
assert outlier_pct_after < 0.02, "Still have too many outliers"

# Check model performance (outliers may have been informative!)
# If performance drops, consider keeping outliers or using robust model
```

---

## High Cardinality Categoricals (MEDIUM)

### >50 Unique Values

**Why Medium**: One-hot encoding creates sparse, high-dimensional data

**Example**:
```python
# MEDIUM: City has 237 unique values
cardinality = df.select_dtypes(include=['object']).nunique().sort_values(ascending=False)
print(cardinality[cardinality > 50])
# city               237  ← MEDIUM
# zip_code           180  ← MEDIUM
# employer           156  ← MEDIUM

# Problem: One-hot encoding creates 237 sparse columns for city
# Most cities have <10 samples → uninformative features
```

**Diagnosis**: High dimensionality, sparsity, potential overfitting

**Fix Options**:
```python
# Option 1: Target encoding (mean target by category)
city_target_means = df.groupby('city')['target'].mean()
df['city_encoded'] = df['city'].map(city_target_means)

# Option 2: Frequency encoding (replace with count)
city_counts = df['city'].value_counts()
df['city_encoded'] = df['city'].map(city_counts)

# Option 3: Group rare categories into "Other"
top_cities = df['city'].value_counts().head(20).index
df['city_grouped'] = df['city'].apply(lambda x: x if x in top_cities else 'Other')

# Option 4: Hashing trick (fixed-size hash encoding)
from sklearn.feature_extraction import FeatureHasher
hasher = FeatureHasher(n_features=20, input_type='string')
hashed = hasher.transform([[c] for c in df['city']])
```

**Fix if time permits**: Cardinality >50

**Verification**:
```python
# Check cardinality reduced
cardinality_after = df.select_dtypes(include=['object']).nunique()
assert (cardinality_after > 50).sum() == 0, "Still have high cardinality"

# Check model performance
# Target encoding may overfit → use cross-validated target encoding
from category_encoders import TargetEncoder
encoder = TargetEncoder(cols=['city'])
df_encoded = encoder.fit_transform(df[['city']], df['target'])
```

---

## Moderate Imbalance (MEDIUM)

### Imbalance Ratio 10:1 to 100:1

**Why Medium**: Model may still learn minority class, but benefits from class weighting

**Example**:
```python
# MEDIUM: Fraud rate 1.2% (imbalance ratio 82:1)
print(df['is_fraud'].value_counts(normalize=True))
# 0    0.988  ← 98.8% normal
# 1    0.012  ← 1.2% fraud

# Baseline: predict all "not fraud" = 98.8% accuracy
# But recall for fraud may be low
```

**Diagnosis**: Model may underweight minority class

**Fix Options**:
```python
# Option 1: Class weights
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight('balanced', classes=[0, 1], y=y)
model.fit(X, y, class_weight={0: class_weights[0], 1: class_weights[1]})

# Option 2: Stratified sampling in cross-validation
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True)
for train_idx, test_idx in skf.split(X, y):
    # Ensures each fold has same class ratio
    pass

# Option 3: Undersample majority (if dataset large)
from imblearn.under_sampling import RandomUnderSampler
sampler = RandomUnderSampler(sampling_strategy=0.2)  # Target 5:1 ratio
X_resampled, y_resampled = sampler.fit_resample(X, y)

# Option 4: SMOTE (if dataset small)
from imblearn.over_sampling import SMOTE
sampler = SMOTE(sampling_strategy=0.1)
X_resampled, y_resampled = sampler.fit_resample(X, y)
```

**Fix if time permits**: Imbalance ratio 10:1 to 100:1

**Verification**:
```python
# Check model doesn't ignore minority class
from sklearn.metrics import classification_report, roc_auc_score
print(classification_report(y_test, y_pred))
# Ensure precision and recall >0.5 for minority class

# Check PR-AUC (better metric for imbalanced data)
pr_auc = average_precision_score(y_test, y_pred_proba)
print(f"PR-AUC: {pr_auc:.3f}")
# Target: PR-AUC >0.5 (better than random)
```

---

## Skewed Distributions (MEDIUM)

### Highly Skewed Features

**Why Medium**: May affect linear models, less impact on tree-based models

**Example**:
```python
# MEDIUM: Transaction amount highly right-skewed
from scipy.stats import skew
skewness = df['amount'].skew()
print(f"Skewness: {skewness:.2f}")  # 4.8 (highly right-skewed)

# Median: $50, Mean: $120, Max: $10K
# Long tail of high-value transactions
```

**Diagnosis**: Distribution not normal, may affect some models

**Fix Options**:
```python
# Option 1: Log transformation
df['amount_log'] = np.log1p(df['amount'])  # log(1+x)

# Option 2: Square root transformation
df['amount_sqrt'] = np.sqrt(df['amount'])

# Option 3: Box-Cox transformation (finds optimal transformation)
from scipy.stats import boxcox
df['amount_boxcox'], lambda_param = boxcox(df['amount'] + 1)

# Option 4: Quantile transformation (maps to normal distribution)
from sklearn.preprocessing import QuantileTransformer
qt = QuantileTransformer(output_distribution='normal')
df['amount_qt'] = qt.fit_transform(df[['amount']])
```

**Fix if time permits**: Absolute skewness >2

**Verification**:
```python
# Check skewness reduced
skewness_after = df['amount_log'].skew()
print(f"Skewness reduced: {skewness:.2f} → {skewness_after:.2f}")
assert abs(skewness_after) < 1, "Still highly skewed"

# Visualize distribution
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(df['amount'], bins=50)
ax[0].set_title('Original (skewed)')
ax[1].hist(df['amount_log'], bins=50)
ax[1].set_title('Log-transformed (normal)')
```

---

## Multicollinearity (MEDIUM)

### Highly Correlated Features

**Why Medium**: Redundant features, unstable coefficient estimates (linear models)

**Example**:
```python
# MEDIUM: lat/lon highly correlated (0.94) with zip_code embeddings
corr_matrix = df.corr().abs()
high_corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        if corr_matrix.iloc[i, j] > 0.90:
            high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))

print("Highly correlated pairs (>0.90):")
for feat1, feat2, corr in high_corr_pairs:
    print(f"{feat1} <-> {feat2}: {corr:.3f}")

# lat <-> zip_lat: 0.94  ← MEDIUM
# lon <-> zip_lon: 0.96  ← MEDIUM
```

**Diagnosis**: Redundant features (same information encoded multiple ways)

**Fix Options**:
```python
# Option 1: Remove one of correlated pair
df = df.drop(columns=['zip_lat', 'zip_lon'])  # Keep lat/lon

# Option 2: PCA (combine correlated features)
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
location_pca = pca.fit_transform(df[['lat', 'lon', 'zip_lat', 'zip_lon']])
df['location_pc1'] = location_pca[:, 0]
df['location_pc2'] = location_pca[:, 1]

# Option 3: VIF analysis (drop features with VIF >10)
from statsmodels.stats.outliers_influence import variance_inflation_factor
vifs = [variance_inflation_factor(df.values, i) for i in range(df.shape[1])]
# Drop features with VIF >10
```

**Fix if time permits**: Feature pairs with correlation >0.90

**Verification**:
```python
# Check no high correlations remain
corr_matrix_after = df.corr().abs()
max_corr = corr_matrix_after.where(~np.eye(len(corr_matrix_after), dtype=bool)).max().max()
print(f"Max correlation: {max_corr:.3f}")
assert max_corr < 0.90, "Still have multicollinearity"
```

---

## Summary: Medium Priority Issues

| Issue | Threshold | Impact | Fix Complexity |
|-------|-----------|--------|----------------|
| Moderate missingness | 10-20% nulls | Reduced capacity | Low (imputation) |
| Minor outliers | 2-5% extreme values | Skewed models | Low (winsorize/log) |
| High cardinality | >50 categories | Sparse features | Medium (encoding) |
| Moderate imbalance | 10:1 to 100:1 | Underweight minority | Low (class weights) |
| Skewed distributions | Abs skewness >2 | Affects linear models | Low (log transform) |
| Multicollinearity | Correlation >0.90 | Redundancy | Low (drop feature) |

**Gate**: Fix medium-priority issues if time permits. Model will train and may perform adequately, but quality can be improved.

**Verification Checklist**:
- [ ] No features with 10-20% missingness (or imputed)
- [ ] Outliers <2% of samples
- [ ] No categoricals with >50 unique values (or re-encoded)
- [ ] Class imbalance <100:1 (or using class weights)
- [ ] Skewness <2 for key features (or transformed)
- [ ] No feature pairs with correlation >0.90

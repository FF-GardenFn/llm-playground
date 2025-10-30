---
name: data-profiler
description: ML data quality engineer specializing in dataset profiling, risk assessment, bias detection, and data integrity validation. Use when assessing data quality, validating schemas, detecting bias, or preparing datasets for ML pipelines.
---

# Data Profiler

Systematic dataset analysis for ML production readiness through quality assessment, risk identification, bias detection, and quantified findings with verification code.

---

## Profiling Workflow

Data profiling flows through systematic phases:

### Phase 1: Reconnaissance → `schema/`, `quality/`
Initial dataset exploration and overview.
- Load dataset and inspect shape, memory usage
- Validate schema (types, nulls, cardinality)
- Compute basic statistics
- Identify immediate red flags
- **Output**: Dataset overview with red flags

### Phase 2: Quality Assessment → `quality/`
Analyze distributions, outliers, duplicates.
- Characterize numeric and categorical distributions
- Detect outliers (IQR, Z-score, isolation forest)
- Identify duplicates (exact and near-duplicates)
- Compute statistical summaries
- **Output**: Quality metrics report

### Phase 3: Integrity Validation → `integrity/`
Verify constraints, temporal coherence, cross-column relationships.
- Check business logic constraints (age 0-120, price > 0)
- Validate temporal ordering and gaps
- Detect impossible combinations (end_date < start_date)
- Assess data freshness
- **Output**: Constraint violation report

### Phase 4: ML Risk Assessment → `ml-risks/`
Identify ML-specific issues that degrade model performance.
- Detect target leakage (correlation > 0.95)
- Validate train/test split integrity (overlap, stratification)
- Assess feature quality (low variance, high cardinality)
- Quantify class imbalance
- **Output**: ML risk report

### Phase 5: Bias & Fairness Analysis → `bias/`
Detect disparities and discrimination risks.
- Analyze protected group distributions
- Measure outcome rate disparities (chi-square, Fisher's exact)
- Assess representation bias
- Identify proxy features for protected attributes
- **Output**: Fairness report

**Full workflow details**: workflows/PROFILING_PROCESS.md

---

## Profiling Categories

Load category based on analysis type:

### Schema & Types → `schema/`

**Type Validation**:
- Expected vs actual type checking
- Type mismatch detection (numeric stored as string)
- Mixed-type column identification
- Type inference strategies
- File: schema/type-validation.md

**Null Analysis**:
- Null percentage computation per column
- Pattern detection (MCAR/MAR/MNAR)
- Correlation with other features
- Imputation recommendations
- File: schema/null-analysis.md

**Cardinality**:
- High-cardinality detection (>50% unique values)
- Uniqueness ratio computation
- Categorical encoding implications (one-hot explosion)
- Dimension reduction strategies (entity embeddings)
- File: schema/cardinality.md

### Quality Assessment → `quality/`

**Distribution Profiling**:
- Numeric distributions (mean, median, std, skew, kurtosis)
- Categorical distributions (top values, entropy)
- Normality tests (Shapiro-Wilk, Kolmogorov-Smirnov)
- Class imbalance quantification
- File: quality/distributions.md

**Outlier Detection**:
- IQR method (1.5×IQR rule for box plots)
- Z-score method (>3σ threshold)
- Isolation forest (unsupervised anomaly detection)
- Contextual outliers (unusual in context)
- File: quality/outliers.md

**Duplicate Detection**:
- Exact duplicates (identical rows)
- Near-duplicates (Jaccard similarity, hash-based)
- Data redundancy measurement
- Deduplication strategies
- File: quality/duplicates.md

**Statistical Validation**:
- Descriptive statistics (quartiles, ranges)
- Correlation matrices (Pearson, Spearman)
- Variance inflation factors (VIF >10 indicates multicollinearity)
- Statistical significance tests
- File: quality/statistics.md

### Integrity Validation → `integrity/`

**Constraint Validation**:
- Business logic constraints (age 0-120, price > 0)
- Range violations
- Format validation (email, phone, date patterns)
- Referential integrity (foreign keys exist)
- File: integrity/constraints.md

**Temporal Coherence**:
- Time ordering validation
- Temporal gap detection
- Future information leakage (target event date < feature date)
- Timestamp consistency across columns
- File: integrity/temporal.md

**Cross-Column Validation**:
- Impossible combinations (end_date < start_date)
- Derived feature verification (sum_col = col_a + col_b)
- Calculated field validation
- Aggregation checks
- File: integrity/cross-column.md

**Data Freshness**:
- Dataset currency assessment (how old is data?)
- Stale record detection (unchanged for long periods)
- Update timestamp validation
- Version consistency
- File: integrity/freshness.md

### ML-Specific Risks → `ml-risks/`

**Target Leakage Detection**:
- Suspiciously high correlation to target (>0.95)
- Perfect predictors (correlation = 1.0)
- Temporal leakage (future information in training)
- Derived features from target
- File: ml-risks/target-leakage.md

**Split Integrity Validation**:
- Train/test sample overlap (set intersection)
- Stratification verification (target distribution match)
- Distribution shift (KS statistic, p-values)
- Sample independence (no duplicates across splits)
- File: ml-risks/split-integrity.md

**Feature Quality Assessment**:
- Zero-variance features (all same value)
- Low-variance features (<0.01 threshold)
- High-cardinality categoricals (>50% unique)
- Multicollinearity (VIF >10, correlation >0.9)
- Redundant feature pairs
- File: ml-risks/feature-quality.md

**Class Imbalance Analysis**:
- Imbalance ratio (majority:minority)
- Minority class coverage (sufficient samples?)
- Sampling strategies (SMOTE, undersampling, class weights)
- Metric implications (precision-recall vs accuracy)
- File: ml-risks/class-imbalance.md

### Bias & Fairness → `bias/`

**Protected Group Analysis**:
- Distribution of sensitive attributes (race, gender, age)
- Underrepresented group detection (<100 samples)
- Coverage across intersections (race × gender)
- Sample size adequacy per group
- File: bias/protected-groups.md

**Disparity Detection**:
- Outcome rates by group (approval rate by race)
- Statistical significance (chi-square test, Fisher's exact)
- Effect size measurement (Cohen's d, Cramér's V)
- Disparate impact ratio (80% rule / four-fifths rule)
- File: bias/disparities.md

**Representation Bias**:
- Sampling bias detection (non-random sample)
- Geographic/demographic skews
- Temporal bias (recent data overrepresented)
- Selection bias identification
- File: bias/representation.md

**Proxy Detection**:
- Potential proxy features for protected attributes
- Correlation network analysis (zip_code → race)
- Indirect discrimination risk
- File: bias/proxy-detection.md

**Category index**: categories/INDEX.md

---

## Risk Framework

Issues prioritized by severity and impact on ML model:

### 🔴 Critical (Blocks Training) → `priorities/critical.md`

**Cannot train model with critical issues.**

**Target Leakage**:
- Features with correlation >0.95 to target
- Perfect predictors (correlation = 1.0)
- Temporal leakage (future information)

**Train/Test Overlap**:
- Sample IDs present in both splits
- Data leakage across splits

**Severe Data Corruption**:
- >40% nulls in critical features
- Entire columns constant (zero variance)
- Type inconsistencies (numeric stored as string)

**Enforcement**: Critical issues must be resolved before training.

---

### 🟡 High (Degrades Performance) → `priorities/high.md`

**Model will train but perform poorly.**

**Severe Class Imbalance**:
- Imbalance ratio >100:1
- Minority class <100 samples

**High Missingness**:
- 20-40% nulls in important features
- MNAR pattern (missing not at random)

**Significant Bias/Disparities**:
- Outcome rate disparities (p < 0.001)
- Fails 80% rule (disparate impact < 0.8)

**Distribution Shift**:
- Train/test KS statistic p-value < 0.01
- Major distribution differences

**Enforcement**: High issues should be addressed before training.

---

### 🔵 Medium (Technical Debt) → `priorities/medium.md`

**Manageable issues, but should address.**

**Moderate Missingness**:
- 10-20% nulls (imputation recommended)

**Minor Outliers**:
- 2-5% outliers (cap or investigate)

**High Cardinality**:
- Categorical features >50% unique
- Encoding challenges (one-hot explosion)

**Moderate Imbalance**:
- Imbalance ratio 10:1 to 100:1

**Enforcement**: Medium issues noted, addressed if time permits.

---

### 🟢 Low (Nice to Fix) → `priorities/low.md`

**Low impact, optional fixes.**

**Minor Duplicates**:
- <5% exact duplicates

**Slight Skewness**:
- Numeric features with mild skew

**Documentation**:
- Missing column descriptions
- Unclear feature names

**Enforcement**: Low issues optional.

---

## Verification Pattern

All findings include verification code → `verification/`

**Quantification Requirement**:
```
❌ Bad: "Some nulls in column X"
✅ Good: "Column X: 23.4% nulls (MCAR pattern, p=0.18)"

❌ Bad: "High correlation with target"
✅ Good: "Feature Y: 0.94 correlation with target (leakage risk)"
```

**Verification Commands**:
Every finding includes reproducible code:

```python
# Finding: Column 'income': 38.7% nulls
# Verification:
import pandas as pd
df = pd.read_csv('train.csv')
null_pct = df['income'].isnull().sum() / len(df) * 100
print(f"Income nulls: {null_pct:.1f}%")
# Expected output: Income nulls: 38.7%
```

**Tool Commands**:
```bash
# Finding: Target leakage in feature_x (correlation = 0.98)
# Verification:
python leakage_detector.py --train train.csv --target is_fraud --correlation_threshold 0.95
# Expected: feature_x flagged with correlation 0.98
```

**Full verification guide**: verification/code-templates.md

---

## Profiling Tools

Available tools for programmatic validation:

### data_quality_checker.py → `tools/data-quality-checker.md`

**Purpose**: Comprehensive dataset profiling

**Capabilities**:
- Null analysis, outlier detection, distribution profiling
- Supports CSV, Parquet, JSON formats
- Outputs summary statistics, distribution plots, anomaly scores

**Usage**:
```bash
# Basic profiling
python data_quality_checker.py --data train.csv --output profile_report.json

# With outlier detection
python data_quality_checker.py --data train.csv --outlier_method zscore --outlier_threshold 3.5

# Focused column analysis
python data_quality_checker.py --data train.csv --columns age,income,credit_score --detailed
```

### schema_validator.py → `tools/schema-validator.md`

**Purpose**: Schema and data integrity validation

**Capabilities**:
- Validate expected schemas against actual data
- Check data types, ranges, allowed values, nullability
- Detect schema drift and violations
- Generate schema from existing data

**Usage**:
```bash
# Infer schema from data
python schema_validator.py --infer --data train.csv --output schema.json

# Validate against schema
python schema_validator.py --validate --data test.csv --schema schema.json --strict

# Check specific constraints
python schema_validator.py --data train.csv --type_check --range_check --null_check
```

### bias_detector.py → `tools/bias-detector.md`

**Purpose**: Fairness and bias analysis

**Capabilities**:
- Analyze protected group distributions and disparities
- Compute statistical significance (chi-square, Fisher's exact)
- Detect underrepresentation
- Measure disparate impact ratios (80% rule)

**Usage**:
```bash
# Analyze by protected attribute
python bias_detector.py --data train.csv --target approved --protected_attrs gender,race,age_group

# Detailed disparity analysis
python bias_detector.py --data train.csv --target outcome --protected_attrs race --test_type chi2 --alpha 0.05

# Intersectional analysis
python bias_detector.py --data train.csv --target hired --protected_attrs gender,race --intersectional
```

### leakage_detector.py → `tools/leakage-detector.md`

**Purpose**: Train/test leakage and temporal validation

**Capabilities**:
- Detect target leakage via correlation analysis
- Validate train/test split integrity
- Check temporal ordering in time-series data
- Identify suspiciously perfect features

**Usage**:
```bash
# Basic leakage detection
python leakage_detector.py --train train.csv --test test.csv --target churned

# Temporal validation
python leakage_detector.py --data timeseries.csv --time_col timestamp --target sales --window 30d

# Feature correlation analysis
python leakage_detector.py --train train.csv --target fraud --correlation_threshold 0.95 --report suspicious_features.json
```

**Tool index**: tools/INDEX.md

---

## Example: Fraud Detection Dataset

**User**: "Profile train.csv for fraud detection. Target is 'is_fraud'."

**Workflow**:

1. **Phase 1: Reconnaissance**
   - Load schema/type-validation.md
   - Detect: 125,430 rows, 34 features, 42.3 MB
   - Load schema/cardinality.md
   - Identify: transaction_id 100% unique (leakage risk)
   - Red Flag: fraud_flag_internal column (suspiciously named)

2. **Phase 2: Quality Assessment**
   - Load quality/distributions.md
   - Analyze: Severe class imbalance (0.8% fraud, 124:1 ratio)
   - Load quality/outliers.md
   - Detect: Few outliers in transaction_amount

3. **Phase 3: Integrity Validation**
   - Load integrity/temporal.md
   - Verify: transaction_date ordering valid
   - Load integrity/constraints.md
   - Check: No constraint violations

4. **Phase 4: ML Risk Assessment**
   - Load ml-risks/target-leakage.md
   - CRITICAL: fraud_flag_internal (correlation = 1.0) → exact match to target
   - CRITICAL: chargeback_amount (correlation = 0.94) → future information
   - HIGH: transaction_id must be removed (pure identifier)
   - Load ml-risks/class-imbalance.md
   - HIGH: 124:1 imbalance ratio (severe, requires SMOTE or class weights)

5. **Phase 5: Bias Analysis**
   - (Not applicable for fraud detection unless analyzing by demographics)

6. **Prioritized Findings**
   - Load priorities/critical.md
   - Issue 1: Remove fraud_flag_internal (target leakage)
   - Issue 2: Remove chargeback_amount (future information)
   - Issue 3: Remove transaction_id (identifier leakage)
   - Load priorities/high.md
   - Issue 4: Address class imbalance (SMOTE, class weights, PR-AUC metric)

**Result**: Systematic analysis identifies critical leakage and provides actionable fixes.

---

## Quantification Requirements

Every finding must be quantified:

**Null Analysis**:
```
❌ Vague: "Many nulls"
✅ Quantified: "23.4% nulls (2,934 / 12,543 rows)"
```

**Outliers**:
```
❌ Vague: "Some outliers"
✅ Quantified: "127 outliers (2.1% of data, Z-score > 3)"
```

**Correlation**:
```
❌ Vague: "High correlation"
✅ Quantified: "Pearson correlation = 0.94 (leakage risk)"
```

**Class Imbalance**:
```
❌ Vague: "Imbalanced classes"
✅ Quantified: "124:1 imbalance (99.2% negative, 0.8% positive)"
```

**Statistical Significance**:
```
❌ Vague: "Disparity exists"
✅ Quantified: "χ² = 45.3, p < 0.001 (highly significant), Cramér's V = 0.21 (medium effect)"
```

**Enforcement**: Findings without exact numbers are incomplete.

---

## Acceptance Criteria

Data profiling complete when:

- ✅ Schema validated (types, nulls, cardinality)
- ✅ Quality assessed (distributions, outliers, duplicates, statistics)
- ✅ Integrity checked (constraints, temporal, cross-column, freshness)
- ✅ ML risks identified (target leakage, split integrity, feature quality, class imbalance)
- ✅ Bias analyzed (protected groups, disparities, representation, proxies)
- ✅ Issues prioritized (Critical/High/Medium/Low)
- ✅ Findings quantified (exact percentages, counts, p-values, effect sizes)
- ✅ Verification code provided (pandas snippets, tool commands)

**If any criteria unmet, profiling incomplete.**

---

## Statistical Tests Reference

Common tests for data profiling → `verification/statistical-tests.md`

**Normality**:
- Shapiro-Wilk (n < 5000)
- Kolmogorov-Smirnov (n ≥ 5000)
- Anderson-Darling

**Independence**:
- Chi-square test (categorical × categorical)
- Fisher's exact test (small sample sizes)

**Group Differences**:
- t-test (parametric, normal distributions)
- Mann-Whitney U (non-parametric, any distribution)
- Kruskal-Wallis (3+ groups, non-parametric)

**Correlation**:
- Pearson (linear correlation)
- Spearman (monotonic correlation, non-parametric)
- Kendall's tau (ordinal data)

**Homogeneity**:
- Levene's test (variance equality)
- Bartlett's test (assumes normality)

---

## Data Quality Heuristics

Rules of thumb for quick assessment → `quality/heuristics.md`

**Null Threshold**: >20% nulls usually requires specialized handling (model-based imputation or dropping)

**Outlier Definition**: Values beyond 3σ (Z-score) or 1.5×IQR are suspicious

**High Cardinality**: Categorical features with >50% unique values often problematic (encoding explosion)

**Correlation Threshold**: Feature-target correlation >0.95 suggests leakage

**Imbalance Ratio**: Class ratios >10:1 require resampling or specialized metrics (precision-recall)

**Duplicate Tolerance**: >5% duplicates indicates data collection issues

**VIF Threshold**: VIF >10 indicates severe multicollinearity (feature redundancy)

**Distribution Shift**: KS statistic p-value <0.01 indicates significant train/test shift

---

## Success Criteria

Data profiling complete when:

- ✅ All 5 phases executed (Reconnaissance → Quality → Integrity → ML Risks → Bias)
- ✅ Critical issues flagged prominently (target leakage, train/test overlap)
- ✅ Every finding quantified (exact percentages, statistical tests)
- ✅ Verification commands provided (pandas snippets, tool commands)
- ✅ Issues prioritized by severity (Critical/High/Medium/Low)
- ✅ Actionable recommendations with priorities
- ✅ Bias analysis conducted (if applicable to problem domain)

**If any criteria unmet, profiling incomplete.**

---

Navigate through phases as data profiling demands: reconnaissance → quality → integrity → ML risks → bias.

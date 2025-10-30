# Data Profiler: Cognitive Model Design

**Agent Type**: Task-Specific (Data Quality Assessment)
**Creation**: Transformation from instructional prompt to structural agent

---

## Core Cognitive Model

**Mental Process Embodied**: **ML Data Quality Engineer**

The agent embodies a senior data quality engineer who systematically assesses datasets before modeling through:

1. **Data Quality First** - ML models are only as good as their training data
2. **Risk-Driven Prioritization** - Identifying critical issues that block training
3. **Quantification Obsession** - Every finding backed by statistics, not adjectives
4. **Reproducibility Focus** - All findings verifiable through code
5. **ML Production Awareness** - Thinking about deployed model implications
6. **Bias & Fairness Vigilance** - Detecting disparities and discrimination risks

**Core Insight**: This is a **data quality auditor** who thinks in distributions, detects subtle risks before they derail ML projects, and provides actionable findings with verification code.

---

## Key Capabilities (By Category)

### 1. Core Data Profiling

**Schema Analysis**:
- Data type validation (expected vs actual)
- Null pattern analysis (MCAR/MAR/MNAR)
- High-cardinality feature detection
- Uniqueness ratio computation
- Type mismatch identification

**Distribution Profiling**:
- Numeric distributions (mean, median, std, skew, kurtosis)
- Categorical distributions (cardinality, top values, entropy)
- Outlier detection (IQR, Z-score, isolation forest)
- Class imbalance quantification
- Normality tests (Shapiro-Wilk, K-S)

**Statistical Validation**:
- Descriptive statistics
- Correlation analysis (Pearson, Spearman)
- Feature importance proxies
- Variance inflation factors (VIF)
- Statistical significance tests

**Missing Data Analysis**:
- Missingness patterns (MCAR/MAR/MNAR)
- Impact on downstream models
- Imputation strategy recommendations
- Correlation with other features

**Duplicate Detection**:
- Exact duplicates
- Near-duplicates (hash-based, Jaccard similarity)
- Data redundancy measurement

### 2. Data Integrity & Quality Assurance

**Constraint Validation**:
- Business logic constraints (age 0-120, price > 0)
- Range violations
- Format consistency (email, phone, date patterns)
- Referential integrity

**Temporal Coherence**:
- Time ordering validation
- Temporal gap detection
- Future information leakage
- Timestamp consistency

**Cross-Column Validation**:
- Impossible combinations (end_date < start_date)
- Derived feature verification
- Calculated field validation
- Aggregation checks

**Data Freshness**:
- Dataset currency assessment
- Stale record detection
- Update timestamp validation
- Version consistency

### 3. ML-Specific Risk Assessment

**Target Leakage Detection**:
- Suspiciously high correlation to target (>0.95)
- Temporal leakage (future info in training)
- Perfect predictors (correlation = 1.0)
- Derived features from target

**Train/Val/Test Integrity**:
- Split stratification verification
- Data leakage across splits (sample overlap)
- Sample independence validation
- Split representativeness assessment

**Feature Engineering Risks**:
- High-dimensional sparse features
- Redundant features (multicollinearity)
- Low-variance features (<0.01)
- Feature importance proxies

**Class Imbalance Analysis**:
- Imbalance ratio quantification (majority:minority)
- Minority class coverage
- Sampling strategy recommendations
- Metric implications (precision-recall vs accuracy)

### 4. Bias & Fairness Profiling

**Protected Group Analysis**:
- Distribution of sensitive attributes (race, gender, age)
- Underrepresented group detection
- Coverage across intersections
- Sample size adequacy per group

**Target Disparity Detection**:
- Outcome rates by group
- Statistical significance (chi-square, Fisher's exact)
- Effect size measurement (Cohen's d, Cramér's V)
- Disparate impact ratio (80% rule)

**Representation Bias**:
- Sampling bias detection
- Geographic/demographic skews
- Temporal biases
- Selection bias identification

**Proxy Detection**:
- Potential proxy features for protected attributes
- Correlation networks
- Indirect discrimination risks

### 5. Advanced Diagnostics

**Drift Detection Prep**:
- Baseline distribution establishment
- High-drift-risk feature identification
- Monitoring strategy recommendations

**Data Lineage Validation**:
- Data provenance verification
- Transformation consistency checks
- Join correctness validation
- Pipeline corruption detection

**Anomaly Profiling**:
- Cluster-based anomaly detection
- Isolation forest scores
- Local outlier factors (LOF)
- Contextual anomalies

**Sampling Strategy Design**:
- Stratified sampling for quick validation
- Reservoir sampling for streaming data
- Bootstrap validation
- Monte Carlo simulation

---

## Structural Architecture Design

### Main Navigation (AGENT.md)

**Structure** (~500 lines):
```markdown
---
name: data-profiler
description: ML data quality engineer specializing in dataset profiling, risk assessment, and bias detection.
---

# Data Profiler

Systematic dataset analysis for ML production readiness through quality assessment, bias detection, and risk identification.

## Profiling Workflow

Data profiling flows through systematic phases:
- Phase 1: Reconnaissance → schema/, quality/
- Phase 2: Integrity Validation → integrity/
- Phase 3: ML Risk Assessment → ml-risks/
- Phase 4: Bias & Fairness Analysis → bias/
- Phase 5: Prioritized Findings → priorities/

## Profiling Categories

Load category based on analysis type:
- Schema & Types → schema/
- Quality Assessment → quality/
- Integrity Validation → integrity/
- ML-Specific Risks → ml-risks/
- Bias & Fairness → bias/

## Risk Framework

Issues prioritized by severity:
- Critical (Blocks Training) → priorities/critical.md
- High (Degrades Performance) → priorities/high.md
- Medium (Technical Debt) → priorities/medium.md
- Low (Nice to Fix) → priorities/low.md

## Verification Pattern

All findings include verification code → verification/
```

### Supporting File Structure

#### 1. schema/ Directory

**schema/type-validation.md**:
- Expected vs actual type checking
- Type mismatch detection
- Mixed-type column identification
- Type inference strategies

**schema/null-analysis.md**:
- Null percentage computation
- MCAR/MAR/MNAR pattern detection
- Null correlation analysis
- Imputation recommendations

**schema/cardinality.md**:
- High-cardinality detection (>50% unique)
- Uniqueness ratio computation
- Categorical encoding implications
- Dimension reduction strategies

#### 2. quality/ Directory

**quality/distributions.md**:
- Numeric distribution characterization
- Categorical distribution analysis
- Skewness and kurtosis
- Normality tests

**quality/outliers.md**:
- IQR method (1.5×IQR rule)
- Z-score method (>3σ)
- Isolation forest detection
- Outlier impact assessment

**quality/duplicates.md**:
- Exact duplicate detection
- Near-duplicate algorithms
- Deduplication strategies
- Data redundancy metrics

**quality/statistics.md**:
- Descriptive statistics
- Correlation matrices
- Variance inflation factors
- Statistical tests

#### 3. integrity/ Directory

**integrity/constraints.md**:
- Business logic validation
- Range checking
- Format validation
- Referential integrity

**integrity/temporal.md**:
- Time ordering validation
- Temporal gap detection
- Future information leakage
- Timestamp consistency

**integrity/cross-column.md**:
- Impossible combination detection
- Derived feature verification
- Calculated field validation

#### 4. ml-risks/ Directory

**ml-risks/target-leakage.md**:
- High correlation detection (>0.95)
- Perfect predictor identification
- Temporal leakage patterns
- Derived feature analysis

**ml-risks/split-integrity.md**:
- Train/test overlap detection
- Stratification verification
- Distribution shift measurement (KS statistic)
- Sample independence validation

**ml-risks/feature-quality.md**:
- Low-variance detection (<0.01)
- High-cardinality issues
- Multicollinearity (VIF >10)
- Redundant feature pairs

**ml-risks/class-imbalance.md**:
- Imbalance ratio computation
- Minority class coverage
- Sampling strategies (SMOTE, undersampling)
- Metric selection (PR-AUC vs accuracy)

#### 5. bias/ Directory

**bias/protected-groups.md**:
- Group distribution analysis
- Underrepresentation detection
- Intersection coverage
- Sample size adequacy

**bias/disparities.md**:
- Outcome rate computation by group
- Statistical significance testing
- Effect size measurement
- Disparate impact ratio (80% rule)

**bias/representation.md**:
- Sampling bias detection
- Geographic/demographic skews
- Temporal bias identification
- Selection bias analysis

**bias/proxy-detection.md**:
- Proxy feature identification
- Correlation network analysis
- Indirect discrimination risk

#### 6. priorities/ Directory

**priorities/critical.md**:
- Blocks training completely
- Target leakage
- Train/test overlap
- Severe data corruption

**priorities/high.md**:
- Degrades performance significantly
- Severe class imbalance
- High missingness (>40%)
- Significant bias/disparities

**priorities/medium.md**:
- Technical debt, manageable
- Moderate missingness (20-40%)
- Minor outliers
- High cardinality

**priorities/low.md**:
- Nice to fix, low impact
- Minor duplicates (<5%)
- Slight skewness
- Documentation improvements

#### 7. verification/ Directory

**verification/code-templates.md**:
- Pandas snippets for validation
- Polars alternatives (for large data)
- csvkit one-liners
- Statistical test code

**verification/tool-commands.md**:
- data_quality_checker.py usage
- schema_validator.py patterns
- bias_detector.py examples
- leakage_detector.py commands

---

## Architectural Mechanisms

### 1. Risk-Driven Prioritization (Severity Classification)

**Problem**: Not all data issues are equal—focus on what blocks training

**Solution**: Issue severity determines urgency
```
Issue detected → Classify by impact
  ├─ Target leakage → priorities/critical.md (blocks training)
  ├─ Class imbalance → priorities/high.md (degrades performance)
  └─ Minor duplicates → priorities/low.md (nice to fix)
```

**Enforcement**: Critical issues must be resolved before training

### 2. Quantification Requirement (No Adjectives, Only Numbers)

**Problem**: Vague findings like "some nulls exist" are useless

**Solution**: Every finding requires exact statistics
```
Bad: "Some nulls in column X"
Good: "Column X: 23.4% nulls (MCAR pattern, p=0.18)"

Bad: "High correlation with target"
Good: "Feature Y: 0.94 correlation with target (leakage risk)"
```

**Enforcement**: Findings without numbers are incomplete

### 3. Verification Commands (Reproducibility Gate)

**Problem**: Findings should be independently verifiable

**Solution**: Every finding includes verification code
```
Finding: "Column 'income': 38.7% nulls"

Verification:
```python
import pandas as pd
df = pd.read_csv('train.csv')
null_pct = df['income'].isnull().sum() / len(df) * 100
print(f"Income nulls: {null_pct:.1f}%")
```

**Enforcement**: No finding without verification code

### 4. Phase-Based Analysis (Systematic Coverage)

**Problem**: Easy to skip critical checks (like bias analysis)

**Solution**: 5-phase workflow ensures comprehensive coverage
```
Phase 1: Reconnaissance (schema, types)
  → Output: Dataset overview

Phase 2: Quality Assessment (nulls, outliers, duplicates)
  → Output: Quality metrics

Phase 3: Integrity Validation (constraints, temporal, cross-column)
  → Output: Violation report

Phase 4: ML Risk Assessment (leakage, splits, features, imbalance)
  → Output: ML risk report

Phase 5: Bias Analysis (protected groups, disparities, proxies)
  → Output: Fairness report
```

**Enforcement**: Cannot skip phases (especially bias analysis)

---

## Example Workflow

**User**: "Profile train.csv for fraud detection. Target is 'is_fraud'."

**Structural Flow**:

1. **Phase 1: Reconnaissance**
   - Load schema/type-validation.md
   - Detect: 125,430 rows, 34 features, 42.3 MB
   - Load schema/cardinality.md
   - Identify: transaction_id 100% unique (leakage risk)

2. **Phase 2: Quality Assessment**
   - Load quality/distributions.md
   - Analyze: Severe class imbalance (0.8% fraud)
   - Load quality/outliers.md
   - Detect: Few outliers in transaction_amount

3. **Phase 3: Integrity Validation**
   - Load integrity/temporal.md
   - Verify: transaction_date ordering valid

4. **Phase 4: ML Risk Assessment**
   - Load ml-risks/target-leakage.md
   - CRITICAL: fraud_flag_internal (correlation = 1.0) → exact match to target
   - Load ml-risks/class-imbalance.md
   - HIGH: 124:1 imbalance ratio (severe)

5. **Phase 5: Bias Analysis**
   - (Not applicable for fraud detection unless analyzing by demographics)

6. **Prioritized Findings**
   - Load priorities/critical.md
   - Issue: Remove fraud_flag_internal (target leakage)
   - Load priorities/high.md
   - Issue: Address class imbalance (124:1 ratio)

**Architecture guides through profiling phases without instructions.**

---

## File Count Estimate

**Main File**: AGENT.md (~500 lines)

**Supporting Files** (~40-45 files):
- schema/: 5 files (type validation, null analysis, cardinality, etc.)
- quality/: 6 files (distributions, outliers, duplicates, statistics, etc.)
- integrity/: 4 files (constraints, temporal, cross-column, freshness)
- ml-risks/: 6 files (target leakage, split integrity, feature quality, class imbalance, etc.)
- bias/: 6 files (protected groups, disparities, representation, proxy detection, etc.)
- priorities/: 4 files (critical, high, medium, low)
- verification/: 3 files (code templates, tool commands, statistical tests)
- tools/: 4 files (data_quality_checker guide, schema_validator guide, bias_detector guide, leakage_detector guide)

**Total System**: ~3000-3500 lines

---

## Success Criteria

Data profiling complete when:

- ✅ Schema validated (types, nulls, cardinality)
- ✅ Quality assessed (distributions, outliers, duplicates, statistics)
- ✅ Integrity checked (constraints, temporal, cross-column)
- ✅ ML risks identified (target leakage, split integrity, feature quality, class imbalance)
- ✅ Bias analyzed (protected groups, disparities, representation, proxies)
- ✅ Issues prioritized (Critical/High/Medium/Low)
- ✅ Findings quantified (exact percentages, counts, p-values)
- ✅ Verification code provided (pandas snippets, tool commands)

---

## Next Steps

1. Create AGENT.md (~500 lines)
2. Create key category files (ml-risks/target-leakage.md, bias/disparities.md)
3. Create priority framework (critical, high, medium, low)
4. Create verification command templates
5. Create tool usage guides
6. Create statistical test reference

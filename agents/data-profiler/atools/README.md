# Data Profiler Agent Tools

This directory contains tools for the **data-profiler** agent, enabling comprehensive dataset quality assessment, bias detection, and ML-specific risk profiling.

## Tools Overview

### 1. data_quality_checker.py
**Purpose**: Comprehensive dataset profiling - nulls, outliers, distributions, types, duplicates

**Key Features**:
- Schema analysis (types, nulls, cardinality)
- Distribution profiling (stats, skewness, kurtosis)
- Outlier detection (Z-score, IQR, Isolation Forest)
- Duplicate analysis
- Missing data patterns

**Usage**:
```bash
# Basic profiling
python data_quality_checker.py --data train.csv --output profile.json

# With outlier detection
python data_quality_checker.py --data train.csv --outlier_method isolation_forest --outlier_threshold 0.1

# Detailed column analysis
python data_quality_checker.py --data train.csv --columns age,income,score --detailed
```

### 2. schema_validator.py
**Purpose**: Validate data schemas, check constraints, detect schema drift

**Key Features**:
- Infer schemas from data
- Validate data against expected schemas
- Type, range, and null constraint checking
- Schema drift detection

**Usage**:
```bash
# Infer schema
python schema_validator.py --infer --data train.csv --output schema.json

# Validate against schema
python schema_validator.py --validate --data test.csv --schema schema.json --strict

# Full constraint checking
python schema_validator.py --validate --data test.csv --schema schema.json --type_check --range_check --null_check
```

### 3. bias_detector.py
**Purpose**: Detect data bias, fairness issues, group disparities

**Key Features**:
- Protected group distribution analysis
- Disparate impact computation (80% rule)
- Statistical significance testing (chi-square)
- Intersectional analysis
- Effect size measurement (Cramér's V)

**Usage**:
```bash
# Basic bias analysis
python bias_detector.py --data train.csv --target approved --protected_attrs gender,race

# With statistical testing
python bias_detector.py --data train.csv --target hired --protected_attrs race --test_type chi2 --alpha 0.05

# Intersectional analysis
python bias_detector.py --data train.csv --target outcome --protected_attrs gender,race --intersectional
```

### 4. leakage_detector.py
**Purpose**: Detect train/test leakage, temporal violations, suspiciously perfect features

**Key Features**:
- Target leakage via correlation analysis
- Train/test overlap detection
- Temporal ordering validation
- Perfect predictor identification
- Future information leakage detection

**Usage**:
```bash
# Basic leakage detection
python leakage_detector.py --train train.csv --test test.csv --target churned

# Temporal validation
python leakage_detector.py --data timeseries.csv --time_col timestamp --target sales

# High correlation features
python leakage_detector.py --train train.csv --target fraud --correlation_threshold 0.95
```

## Installation

All tools require:
```bash
pip install pandas numpy scipy scikit-learn
```

## Common Workflows

### Complete Dataset Profiling
```bash
# 1. Quality check
python data_quality_checker.py --data train.csv --detailed --output quality.json

# 2. Schema validation
python schema_validator.py --infer --data train.csv --output schema.json

# 3. Leakage detection
python leakage_detector.py --train train.csv --test test.csv --target outcome

# 4. Bias analysis
python bias_detector.py --data train.csv --target outcome --protected_attrs gender,race --intersectional
```

### Quick Health Check
```bash
# One-liner quality summary
python data_quality_checker.py --data train.csv --format text | grep -E "CRITICAL|HIGH"

# Quick schema check
python schema_validator.py --infer --data train.csv | jq '.columns[] | select(.flags != [])'
```

## Output Formats

All tools support:
- **JSON**: Structured machine-readable output (default)
- **Text**: Human-readable summaries

## Error Handling

All tools include:
- Comprehensive input validation
- Graceful error handling
- Informative error messages
- Verbose logging mode (`-v` flag)

## Integration with Data Profiler Agent

These tools are designed to be invoked by the data-profiler agent following the Tool Usage Protocol:

1. **Announce**: State intent to use tool
2. **Execute**: Run with appropriate parameters
3. **Present**: Extract key findings from output
4. **Interpret**: Explain implications for ML project
5. **Recommend**: Provide prioritized action items

## Contributing

When adding new tools:
1. Follow the existing structure (argparse, logging, JSON output)
2. Include comprehensive docstring with examples
3. Implement error handling and validation
4. Add usage examples to this README
5. Ensure compatibility with pandas/numpy ecosystem

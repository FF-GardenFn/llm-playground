# ML Evaluator Tools

Comprehensive toolkit for rigorous machine learning model evaluation with statistical rigor, calibration analysis, and error diagnostics.

## Tools Overview

### 1. evaluation_runner.py
**Purpose:** Execute comprehensive model evaluation with multiple metrics, stratification, and bootstrap confidence intervals.

**Key Features:**
- Multiple classification metrics (accuracy, precision, recall, F1, AUC-ROC, AUC-PR, MCC, Cohen's kappa)
- Multiple regression metrics (MAE, MSE, RMSE, R², MAPE, median AE)
- Bootstrap confidence intervals for uncertainty quantification
- Stratified evaluation by subgroups
- Data integrity checks
- Reproducible results with seed control

**Usage Examples:**

```bash
# Basic evaluation with confidence intervals
python evaluation_runner.py \
  --predictions preds.csv \
  --labels labels.csv \
  --metrics accuracy,f1_macro,auc_roc \
  --bootstrap 1000 \
  --seed 42 \
  --format markdown

# Stratified evaluation
python evaluation_runner.py \
  --predictions preds.csv \
  --labels labels.csv \
  --features features.csv \
  --stratify_by category \
  --metrics accuracy,f1 \
  --bootstrap 1000

# Data integrity check only
python evaluation_runner.py \
  --data_check \
  --test_set test.csv \
  --label target \
  --format json
```

**Input Formats:**
- `predictions.csv`: Single column with model predictions
- `labels.csv`: Single column with ground truth labels
- `probabilities.csv`: Single column (binary) or multiple columns (multi-class) with probabilities
- `features.csv`: Multiple columns including stratification column

**Output Format:**
```json
{
  "status": "success",
  "task_type": "classification",
  "n_samples": 5000,
  "seed": 42,
  "metrics": {
    "accuracy": {
      "value": 0.847,
      "ci_lower": 0.831,
      "ci_upper": 0.862,
      "ci_width": 0.031
    },
    "f1_macro": {
      "value": 0.823,
      "ci_lower": 0.805,
      "ci_upper": 0.840
    }
  }
}
```

---

### 2. metrics_analyzer.py
**Purpose:** Compare models statistically with significance testing and cost-benefit analysis.

**Key Features:**
- Paired statistical tests (McNemar, paired t-test, Wilcoxon)
- Effect size calculations (Cohen's d, odds ratio)
- Multiple comparison corrections (Bonferroni, Holm)
- Cost-benefit analysis with threshold scanning
- Metric comparison reports

**Usage Examples:**

```bash
# Compare two models with McNemar's test
python metrics_analyzer.py \
  --model_a preds_a.csv \
  --model_b preds_b.csv \
  --labels labels.csv \
  --paired_test \
  --test_type mcnemar \
  --format text

# With Bonferroni correction
python metrics_analyzer.py \
  --model_a preds_a.csv \
  --model_b preds_b.csv \
  --labels labels.csv \
  --paired_test \
  --correction bonferroni

# Cost-benefit analysis
python metrics_analyzer.py \
  --probabilities probs.csv \
  --labels labels.csv \
  --cost_fp 10 \
  --cost_fn 500 \
  --threshold_scan 0.1,0.9,100 \
  --output cost_analysis.json
```

**Output Format (Paired Test):**
```json
{
  "status": "success",
  "test_type": "mcnemar",
  "correction": "bonferroni",
  "alpha": 0.05,
  "test_result": {
    "test": "mcnemar",
    "statistic": 847.3,
    "p_value": 0.0001,
    "significant": true,
    "conclusion": "Model A significantly better (p=0.0001)",
    "contingency_table": {
      "both_correct": 4200,
      "both_incorrect": 150,
      "only_a_correct": 520,
      "only_b_correct": 130
    }
  }
}
```

**Output Format (Cost Analysis):**
```json
{
  "status": "success",
  "cost_fp_per_instance": 10.0,
  "cost_fn_per_instance": 500.0,
  "optimal_threshold": 0.30,
  "optimal_total_cost": 343950.0,
  "optimal_metrics": {
    "precision": 0.591,
    "recall": 0.894,
    "f1": 0.712
  },
  "threshold_analysis": [
    {
      "threshold": 0.30,
      "precision": 0.591,
      "recall": 0.894,
      "f1": 0.712,
      "tp": 939,
      "tn": 48240,
      "fp": 710,
      "fn": 111,
      "cost_fp": 7100.0,
      "cost_fn": 55500.0,
      "total_cost": 62600.0
    }
  ]
}
```

---

### 3. calibration_plotter.py
**Purpose:** Generate calibration diagnostics, reliability plots, and threshold analysis.

**Key Features:**
- Calibration curves and reliability diagrams
- ECE (Expected Calibration Error) and MCE (Maximum Calibration Error)
- Brier score computation
- Temperature scaling for post-hoc calibration
- ROC and PR curve generation
- Optimal threshold recommendations

**Usage Examples:**

```bash
# Basic calibration analysis
python calibration_plotter.py \
  --labels labels.csv \
  --probabilities probs.csv \
  --num_bins 10 \
  --format markdown

# With ROC/PR curves
python calibration_plotter.py \
  --labels labels.csv \
  --probabilities probs.csv \
  --compute_curves \
  --output calibration_report.json

# Apply temperature scaling
python calibration_plotter.py \
  --labels labels.csv \
  --probabilities probs.csv \
  --logits logits.csv \
  --calibrate temperature_scaling \
  --output calibrated_analysis.json
```

**Output Format:**
```json
{
  "status": "success",
  "n_samples": 5000,
  "positive_rate": 0.021,
  "ece": 0.042,
  "mce": 0.089,
  "brier_score": 0.134,
  "calibration_quality": "well-calibrated",
  "calibration_curve": {
    "num_bins": 10,
    "bins": [
      {
        "bin_center": 0.05,
        "predicted_prob": 0.048,
        "true_freq": 0.052,
        "count": 1200,
        "error": 0.004
      }
    ]
  },
  "roc_curve": {
    "auc": 0.924,
    "fpr": [0.0, 0.01, 0.05, ...],
    "tpr": [0.0, 0.45, 0.78, ...],
    "thresholds": [1.0, 0.95, 0.85, ...]
  }
}
```

**Calibration Quality Interpretation:**
- **ECE < 0.05**: Well-calibrated (model confidence matches reality)
- **ECE 0.05-0.10**: Moderately calibrated (minor overconfidence/underconfidence)
- **ECE > 0.10**: Poorly calibrated (significant confidence issues)

---

## Installation Requirements

```bash
pip install numpy pandas scikit-learn scipy
```

For full functionality including plotting (if extended):
```bash
pip install matplotlib seaborn
```

## Common Workflows

### Workflow 1: Complete Model Evaluation

```bash
# Step 1: Run comprehensive evaluation
python evaluation_runner.py \
  --predictions model_preds.csv \
  --labels test_labels.csv \
  --probabilities model_probs.csv \
  --metrics accuracy,f1_macro,auc_roc,auc_pr \
  --bootstrap 1000 \
  --seed 42 \
  --output evaluation_results.json

# Step 2: Assess calibration
python calibration_plotter.py \
  --labels test_labels.csv \
  --probabilities model_probs.csv \
  --num_bins 10 \
  --compute_curves \
  --output calibration_report.json

# Step 3: Compare to baseline
python metrics_analyzer.py \
  --model_a model_preds.csv \
  --model_b baseline_preds.csv \
  --labels test_labels.csv \
  --paired_test \
  --test_type mcnemar \
  --correction bonferroni \
  --output comparison_report.json
```

### Workflow 2: Production Readiness Check

```bash
# Data integrity check
python evaluation_runner.py \
  --data_check \
  --test_set production_test.csv \
  --label target \
  --output data_integrity.json

# Comprehensive evaluation with stratification
python evaluation_runner.py \
  --predictions model_preds.csv \
  --labels test_labels.csv \
  --probabilities model_probs.csv \
  --features test_features.csv \
  --stratify_by customer_segment \
  --metrics accuracy,precision,recall,f1,auc_roc \
  --bootstrap 1000 \
  --output stratified_eval.json

# Cost-benefit optimization
python metrics_analyzer.py \
  --probabilities model_probs.csv \
  --labels test_labels.csv \
  --cost_fp 10 \
  --cost_fn 500 \
  --threshold_scan 0.0,1.0,200 \
  --output optimal_threshold.json

# Calibration check
python calibration_plotter.py \
  --labels test_labels.csv \
  --probabilities model_probs.csv \
  --output calibration_check.json
```

### Workflow 3: Model Comparison

```bash
# Statistical comparison
python metrics_analyzer.py \
  --model_a new_model_preds.csv \
  --model_b current_model_preds.csv \
  --labels test_labels.csv \
  --paired_test \
  --test_type mcnemar \
  --output statistical_comparison.json

# Detailed evaluation of both models
python evaluation_runner.py \
  --predictions new_model_preds.csv \
  --labels test_labels.csv \
  --metrics accuracy,f1,auc_roc \
  --bootstrap 1000 \
  --output new_model_eval.json

python evaluation_runner.py \
  --predictions current_model_preds.csv \
  --labels test_labels.csv \
  --metrics accuracy,f1,auc_roc \
  --bootstrap 1000 \
  --output current_model_eval.json
```

## Best Practices

### 1. Reproducibility
Always use fixed seeds:
```bash
--seed 42
```

### 2. Statistical Rigor
- Use bootstrap confidence intervals for uncertainty quantification (--bootstrap 1000)
- Apply multiple comparison corrections when testing multiple metrics (--correction bonferroni)
- Report both p-values and effect sizes
- Check assumptions before using parametric tests

### 3. Calibration
- Always check calibration for probability-based models
- ECE < 0.05 is the gold standard
- Apply temperature scaling if ECE > 0.10
- Monitor calibration in production

### 4. Stratification
Always stratify evaluation by relevant subgroups:
```bash
--stratify_by category
```

Common stratification dimensions:
- Class/category
- Demographic groups
- Difficulty levels
- Time periods
- Data sources

### 5. Cost-Benefit Analysis
For production systems, always:
- Define explicit costs for FP and FN
- Scan threshold space thoroughly (e.g., 100+ thresholds)
- Validate optimal threshold on hold-out set
- Monitor costs in production

## Troubleshooting

### Issue: "Length mismatch" error
**Solution:** Ensure all input files have the same number of rows.

```bash
wc -l predictions.csv labels.csv
```

### Issue: "NaN values in metrics"
**Causes:**
- AUC metrics require probabilities (--probabilities)
- Empty classes in multi-class classification
- Insufficient samples in bootstrap

**Solution:** Check input data and provide probabilities for AUC metrics.

### Issue: "Bootstrap CI too wide"
**Causes:**
- Small sample size
- High variance in data
- Insufficient bootstrap samples

**Solution:**
- Increase bootstrap samples: --bootstrap 5000
- Collect more test data
- Check for data quality issues

### Issue: "Calibration error very high"
**Causes:**
- Model overconfident or underconfident
- Imbalanced classes
- Distribution shift

**Solution:**
- Apply temperature scaling: --calibrate temperature_scaling
- Retrain with proper calibration objective
- Check train/test distribution match

## Output File Management

Recommended naming convention:
```
evaluation_results_{model_name}_{date}.json
calibration_{model_name}_{date}.json
comparison_{model_a}_vs_{model_b}_{date}.json
cost_analysis_{model_name}_{threshold}_{date}.json
```

## Version Information

These tools require:
- Python 3.7+
- NumPy 1.19+
- pandas 1.1+
- scikit-learn 0.24+
- SciPy 1.5+

## Support

For issues or questions about these tools, check:
1. Input data format (CSV with proper structure)
2. Missing or NaN values
3. Correct metric names (case-sensitive)
4. Sufficient sample sizes for statistical tests

## Example Data Formats

### predictions.csv
```csv
prediction
1
0
1
1
0
```

### labels.csv
```csv
label
1
0
1
0
0
```

### probabilities.csv (binary)
```csv
prob_positive
0.87
0.23
0.91
0.45
0.12
```

### probabilities.csv (multi-class)
```csv
prob_class_0,prob_class_1,prob_class_2
0.10,0.85,0.05
0.70,0.20,0.10
0.05,0.90,0.05
```

### features.csv (for stratification)
```csv
category,amount,region
A,100,US
B,250,EU
A,50,US
C,500,APAC
B,150,US
```

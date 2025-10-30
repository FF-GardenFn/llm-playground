# Class Imbalance

**Risk Category**: 🟠 ML RISK - HIGH (severity depends on ratio)
**Impact**: Model ignores minority class, poor generalization, misleading metrics
**Detection**: Class ratio calculation, performance analysis

Class imbalance causes models to achieve high accuracy by predicting only the majority class, completely ignoring the minority class (often the class of interest).

---

## What is Class Imbalance?

**Definition**: Severe disparity in class frequencies

**Imbalance Ratio**: Majority class count / Minority class count

**Severity Levels**:
- **Slight** (2:1 to 10:1): ✅ Usually no issue
- **Moderate** (10:1 to 100:1): 🟡 May need class weights
- **Severe** (100:1 to 1000:1): 🟠 Requires resampling or special techniques
- **Extreme** (>1000:1): 🔴 CRITICAL - Very difficult to train

**Why Problematic**: Model can achieve 99% accuracy by always predicting majority class

---

## Detection & Diagnosis

### 1. Calculate Imbalance Ratio

**Goal**: Quantify class imbalance severity

**Code**:
```python
def analyze_class_imbalance(y):
    """Calculate imbalance ratio and classify severity"""

    # Count samples per class
    class_counts = y.value_counts().sort_index()

    # Calculate imbalance ratio
    majority_count = class_counts.max()
    minority_count = class_counts.min()
    imbalance_ratio = majority_count / minority_count

    # Calculate minority class percentage
    minority_pct = minority_count / len(y) * 100

    # Classify severity
    if imbalance_ratio < 10:
        severity = 'SLIGHT'
        priority = 'LOW'
    elif imbalance_ratio < 100:
        severity = 'MODERATE'
        priority = 'MEDIUM'
    elif imbalance_ratio < 1000:
        severity = 'SEVERE'
        priority = 'HIGH'
    else:
        severity = 'EXTREME'
        priority = 'CRITICAL'

    results = {
        'class_counts': class_counts.to_dict(),
        'majority_count': int(majority_count),
        'minority_count': int(minority_count),
        'imbalance_ratio': float(imbalance_ratio),
        'minority_pct': float(minority_pct),
        'severity': severity,
        'priority': priority
    }

    return results

# Example usage
imbalance_results = analyze_class_imbalance(y)
print(f"Imbalance ratio: {imbalance_results['imbalance_ratio']:.1f}:1")
print(f"Minority class: {imbalance_results['minority_pct']:.2f}%")
print(f"Severity: {imbalance_results['severity']} (Priority: {imbalance_results['priority']})")

# Example outputs:
# Fraud detection: 1250:1 ratio, 0.08% minority → EXTREME (CRITICAL)
# Churn prediction: 4:1 ratio, 20% minority → SLIGHT (LOW)
# Disease diagnosis: 80:1 ratio, 1.2% minority → MODERATE (MEDIUM)
```

**Tool Integration**:
```bash
python atools/data_quality_checker.py --check-imbalance --labels y_train.csv
```

---

### 2. Baseline Performance Analysis

**Goal**: Quantify naive baseline to demonstrate need for balancing

**Code**:
```python
def analyze_baseline_performance(y):
    """Calculate what naive baseline achieves"""

    # Majority class baseline (always predict majority)
    majority_class = y.value_counts().idxmax()
    majority_accuracy = (y == majority_class).mean()

    # Minority class metrics with naive baseline
    from sklearn.metrics import precision_score, recall_score, f1_score

    # Naive predictions (all majority class)
    y_naive = np.full(len(y), majority_class)

    naive_metrics = {
        'accuracy': majority_accuracy,
        'precision_minority': precision_score(y, y_naive, pos_label=1, zero_division=0),
        'recall_minority': recall_score(y, y_naive, pos_label=1, zero_division=0),
        'f1_minority': f1_score(y, y_naive, pos_label=1, zero_division=0)
    }

    return naive_metrics

# Example usage
baseline = analyze_baseline_performance(y)
print("Naive Baseline (always predict majority class):")
print(f"  Accuracy: {baseline['accuracy']:.3f}")
print(f"  Precision (minority): {baseline['precision_minority']:.3f}")
print(f"  Recall (minority): {baseline['recall_minority']:.3f}")
print(f"  F1 (minority): {baseline['f1_minority']:.3f}")

# Example output (fraud detection, 0.08% fraud rate):
# Accuracy: 0.992  ← Looks great but useless!
# Precision (minority): 0.000  ← Never predicts fraud
# Recall (minority): 0.000  ← Catches 0% of fraud
# F1 (minority): 0.000  ← Complete failure for fraud class
```

**Interpretation**: If naive baseline achieves >90% accuracy, imbalance is severe.

---

## Mitigation Strategies

### Strategy 1: Class Weights

**When to Use**: Moderate imbalance (10:1 to 100:1), large dataset

**Pros**: Simple, no data loss, fast training
**Cons**: May not work for extreme imbalance

**Code**:
```python
from sklearn.utils.class_weight import compute_class_weight
from sklearn.linear_model import LogisticRegression

# Compute balanced class weights
classes = np.unique(y_train)
class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
weight_dict = {classes[i]: class_weights[i] for i in range(len(classes))}

print(f"Class weights: {weight_dict}")
# Example: {0: 0.5, 1: 50.0}  ← Minority class gets 100x weight

# Train with class weights
model = LogisticRegression(class_weight='balanced')
model.fit(X_train, y_train)

# Or specify custom weights
model = LogisticRegression(class_weight=weight_dict)
model.fit(X_train, y_train)
```

**Tree-based models**:
```python
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Random Forest
rf = RandomForestClassifier(class_weight='balanced', random_state=42)
rf.fit(X_train, y_train)

# XGBoost
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
xgb = XGBClassifier(scale_pos_weight=scale_pos_weight, random_state=42)
xgb.fit(X_train, y_train)
```

---

### Strategy 2: Undersampling (Majority Class)

**When to Use**: Large dataset, extreme imbalance (>1000:1)

**Pros**: Fast training, reduces data size
**Cons**: Discards potentially useful majority class data

**Code**:
```python
from imblearn.under_sampling import RandomUnderSampler, TomekLinks, NearMiss

# Option 1: Random undersampling
rus = RandomUnderSampler(sampling_strategy=0.1, random_state=42)  # Target 10:1 ratio
X_resampled, y_resampled = rus.fit_resample(X_train, y_train)

print(f"Original: {len(y_train)} samples, {y_train.value_counts().to_dict()}")
print(f"Undersampled: {len(y_resampled)} samples, {y_resampled.value_counts().to_dict()}")

# Example:
# Original: 100,000 samples, {0: 99,200, 1: 800}  (124:1 ratio)
# Undersampled: 8,800 samples, {0: 8,000, 1: 800}  (10:1 ratio)

# Option 2: Tomek Links (remove borderline majority samples)
tomek = TomekLinks()
X_resampled, y_resampled = tomek.fit_resample(X_train, y_train)

# Option 3: NearMiss (keep majority samples far from minority)
nearmiss = NearMiss(version=1)
X_resampled, y_resampled = nearmiss.fit_resample(X_train, y_train)
```

---

### Strategy 3: Oversampling (Minority Class)

**When to Use**: Small dataset, moderate to severe imbalance

**Pros**: No data loss, can improve minority class coverage
**Cons**: Risk of overfitting, slower training

**Code**:
```python
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN

# Option 1: Random oversampling (duplicate minority samples)
ros = RandomOverSampler(sampling_strategy=0.5, random_state=42)  # Target 2:1 ratio
X_resampled, y_resampled = ros.fit_resample(X_train, y_train)

# Option 2: SMOTE (Synthetic Minority Over-sampling Technique)
smote = SMOTE(sampling_strategy=0.5, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

print(f"Original: {len(y_train)} samples, {y_train.value_counts().to_dict()}")
print(f"SMOTE: {len(y_resampled)} samples, {y_resampled.value_counts().to_dict()}")

# Example:
# Original: 10,000 samples, {0: 9,200, 1: 800}  (11.5:1 ratio)
# SMOTE: 13,600 samples, {0: 9,200, 1: 4,600}  (2:1 ratio)

# Option 3: ADASYN (Adaptive Synthetic Sampling)
# Generates more synthetic samples for minority samples that are harder to learn
adasyn = ADASYN(sampling_strategy=0.5, random_state=42)
X_resampled, y_resampled = adasyn.fit_resample(X_train, y_train)
```

**SMOTE Variants**:
```python
from imblearn.over_sampling import SMOTENC, SMOTEN, BorderlineSMOTE, SVMSMOTE

# SMOTENC: For datasets with categorical features
smotenc = SMOTENC(categorical_features=[0, 2, 5], sampling_strategy=0.5)
X_resampled, y_resampled = smotenc.fit_resample(X_train, y_train)

# BorderlineSMOTE: Only synthetic samples near decision boundary
borderline_smote = BorderlineSMOTE(sampling_strategy=0.5)
X_resampled, y_resampled = borderline_smote.fit_resample(X_train, y_train)
```

---

### Strategy 4: Combined Sampling

**When to Use**: Extreme imbalance, want balanced approach

**Code**:
```python
from imblearn.combine import SMOTEENN, SMOTETomek

# SMOTEENN: SMOTE + Edited Nearest Neighbors
# Oversamples minority, then cleans up noisy majority samples
smoteenn = SMOTEENN(random_state=42)
X_resampled, y_resampled = smoteenn.fit_resample(X_train, y_train)

# SMOTETomek: SMOTE + Tomek Links
# Oversamples minority, then removes Tomek pairs
smotetomek = SMOTETomek(random_state=42)
X_resampled, y_resampled = smotetomek.fit_resample(X_train, y_train)
```

---

### Strategy 5: Ensemble Methods

**When to Use**: Extreme imbalance, want best performance

**Code**:
```python
from imblearn.ensemble import BalancedRandomForestClassifier, EasyEnsembleClassifier, RUSBoostClassifier

# Balanced Random Forest (undersamples each tree)
brf = BalancedRandomForestClassifier(n_estimators=100, random_state=42)
brf.fit(X_train, y_train)

# EasyEnsemble (multiple balanced subsets)
eec = EasyEnsembleClassifier(n_estimators=10, random_state=42)
eec.fit(X_train, y_train)

# RUSBoost (combines boosting with random undersampling)
rusboost = RUSBoostClassifier(n_estimators=100, random_state=42)
rusboost.fit(X_train, y_train)
```

---

### Strategy 6: Focal Loss (Deep Learning)

**When to Use**: Neural networks, extreme imbalance

**Code**:
```python
import torch
import torch.nn as nn

class FocalLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        BCE_loss = nn.BCEWithLogitsLoss()(inputs, targets)
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1-pt)**self.gamma * BCE_loss
        return F_loss.mean()

# Use focal loss instead of BCELoss
criterion = FocalLoss(alpha=0.25, gamma=2.0)
```

---

## Evaluation Metrics for Imbalanced Data

### 1. Proper Metrics (NOT Accuracy!)

**Code**:
```python
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score
)

# Get predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Classification report
print(classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)
# [[TN  FP]
#  [FN  TP]]

# Key metrics
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)
pr_auc = average_precision_score(y_test, y_pred_proba)

print(f"Precision: {precision:.3f}")  # How many predicted positives are correct?
print(f"Recall: {recall:.3f}")        # How many actual positives did we catch?
print(f"F1: {f1:.3f}")                # Harmonic mean of precision and recall
print(f"ROC-AUC: {roc_auc:.3f}")      # Area under ROC curve
print(f"PR-AUC: {pr_auc:.3f}")        # Area under Precision-Recall curve (BETTER for imbalanced data)
```

**Which metrics to use**:
- ❌ **Accuracy**: Misleading with imbalance (can be 99% but useless)
- ✅ **Precision**: How many predicted frauds are actually fraud?
- ✅ **Recall**: How many frauds did we catch?
- ✅ **F1**: Balance between precision and recall
- ✅ **PR-AUC**: Better than ROC-AUC for extreme imbalance

---

### 2. Threshold Optimization

**Goal**: Find optimal decision threshold (not default 0.5)

**Code**:
```python
from sklearn.metrics import precision_recall_curve

# Get predicted probabilities
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Calculate precision-recall curve
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)

# Find optimal threshold (maximize F1)
f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
optimal_idx = np.argmax(f1_scores)
optimal_threshold = thresholds[optimal_idx]

print(f"Optimal threshold: {optimal_threshold:.3f}")
print(f"Precision at optimal: {precision[optimal_idx]:.3f}")
print(f"Recall at optimal: {recall[optimal_idx]:.3f}")
print(f"F1 at optimal: {f1_scores[optimal_idx]:.3f}")

# Use optimal threshold for predictions
y_pred_optimal = (y_pred_proba >= optimal_threshold).astype(int)
```

---

## Complete Imbalance Handling Workflow

```python
def handle_class_imbalance(X_train, y_train, X_test, y_test, strategy='auto'):
    """Complete workflow for handling class imbalance"""

    # 1. Analyze imbalance
    imbalance_results = analyze_class_imbalance(y_train)
    print(f"Imbalance ratio: {imbalance_results['imbalance_ratio']:.1f}:1")
    print(f"Severity: {imbalance_results['severity']}")

    # 2. Choose strategy based on severity
    if strategy == 'auto':
        ratio = imbalance_results['imbalance_ratio']
        if ratio < 10:
            strategy = 'none'
        elif ratio < 100:
            strategy = 'class_weights'
        elif ratio < 1000:
            strategy = 'smote'
        else:
            strategy = 'ensemble'

    print(f"Strategy: {strategy}")

    # 3. Apply strategy
    if strategy == 'none':
        X_train_resampled, y_train_resampled = X_train, y_train
        model = LogisticRegression(random_state=42)

    elif strategy == 'class_weights':
        X_train_resampled, y_train_resampled = X_train, y_train
        model = LogisticRegression(class_weight='balanced', random_state=42)

    elif strategy == 'undersample':
        rus = RandomUnderSampler(sampling_strategy=0.1, random_state=42)
        X_train_resampled, y_train_resampled = rus.fit_resample(X_train, y_train)
        model = LogisticRegression(random_state=42)

    elif strategy == 'smote':
        smote = SMOTE(sampling_strategy=0.5, random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
        model = LogisticRegression(random_state=42)

    elif strategy == 'ensemble':
        X_train_resampled, y_train_resampled = X_train, y_train
        model = BalancedRandomForestClassifier(n_estimators=100, random_state=42)

    # 4. Train model
    model.fit(X_train_resampled, y_train_resampled)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    results = {
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_pred_proba),
        'pr_auc': average_precision_score(y_test, y_pred_proba)
    }

    print("\nPerformance:")
    for metric, value in results.items():
        print(f"{metric}: {value:.3f}")

    return model, results
```

---

## Gate Enforcement

**Imbalance severity → Required action**:
- **Slight** (<10:1): ✅ No action required
- **Moderate** (10:1 to 100:1): 🟡 Use class weights
- **Severe** (100:1 to 1000:1): 🟠 Use SMOTE or ensemble methods
- **Extreme** (>1000:1): 🔴 Use specialized techniques (focal loss, ensemble, cost-sensitive)

**Evaluation requirements**:
- [ ] Must report precision, recall, F1 (not just accuracy)
- [ ] Must report PR-AUC (not just ROC-AUC)
- [ ] Must show confusion matrix
- [ ] Must compare to naive baseline

**Verification Command**:
```bash
python atools/data_quality_checker.py --check-imbalance-handling \
    --train-labels y_train.csv \
    --test-labels y_test.csv \
    --predictions y_pred.csv \
    --output imbalance_report.json
```

# Diagnostic: Overfitting Detection

**Trigger**: Train-validation gap > 15%

**Auto-loaded when**: Training monitor detects large train-val performance disparity

---

## Symptoms

### Primary Indicators
- **Train accuracy >> Val accuracy** (gap >10-15%)
- **Train loss << Val loss** (val loss significantly higher)
- **Val loss starts increasing** while train loss continues decreasing
- **Early stopping triggered** due to val performance plateauing/degrading

### Secondary Indicators
- Model performs well on training examples but poorly on held-out data
- Perfect or near-perfect training accuracy (99-100%)
- Learning curves show divergence (train improving, val plateauing/worsening)

### Example Metrics
```
Epoch 20:
  Train Loss: 0.15  |  Val Loss: 0.48   (Gap: 0.33 - HIGH)
  Train Acc:  0.94  |  Val Acc:  0.75   (Gap: 0.19 - HIGH)

Epoch 30:
  Train Loss: 0.08  |  Val Loss: 0.52   (Gap: 0.44 - WORSENING)
  Train Acc:  0.97  |  Val Acc:  0.73   (Gap: 0.24 - WORSENING)
```

**Interpretation**: Model overfitting—memorizing training data instead of learning generalizable patterns.

---

## Root Causes

### 1. Model Too Complex for Data Size
**Evidence**:
- Large model (millions of parameters)
- Small dataset (thousands of examples)
- Model capacity >> data complexity

**Ratio Check**: Parameters / Training Samples
- >10: High risk of overfitting
- 1-10: Moderate risk
- <1: Low risk

**Example**: 10M parameters, 5K training samples → Ratio = 2000 (very high risk)

### 2. Insufficient Regularization
**Evidence**:
- No dropout or very low dropout (0.0-0.1)
- No weight decay or very low weight decay (<1e-5)
- No data augmentation
- No early stopping or late early stopping (patience >20)

### 3. Training Too Long
**Evidence**:
- Val loss starts increasing after epoch N
- Continuing training past val loss minimum
- Early stopping patience too high

### 4. Data Leakage
**Evidence**:
- Unrealistically low training loss
- Train accuracy 99-100% early in training
- Features contain information about target

**Critical**: Check for leakage (see Phase 2 data assessment)

### 5. Data Quality Issues
**Evidence**:
- Training data "easier" than validation data
- Validation set not representative
- Train-val distribution mismatch

---

## Fixes (Ordered by Effectiveness)

### Fix 1: Add or Increase Dropout ⭐⭐⭐

**What**: Randomly drop neurons during training

**Implementation**:
```python
# PyTorch
model = nn.Sequential(
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Dropout(0.3),  # Add dropout layer
    nn.Linear(64, 10)
)
```

**Recommended values**:
- Start: 0.1-0.2 (mild)
- Moderate: 0.3-0.4
- Aggressive: 0.5+ (only if severe overfitting)

**Expected impact**: Reduce train-val gap by 3-10%

**Trade-off**: May slightly reduce train accuracy, but improves val accuracy

### Fix 2: Increase Weight Decay ⭐⭐⭐

**What**: L2 regularization on weights

**Implementation**:
```python
# PyTorch
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-3  # Increase from 1e-5
)
```

**Recommended values**:
- Mild: 1e-5
- Moderate: 1e-4 to 1e-3
- Aggressive: 1e-2+

**Expected impact**: Reduce train-val gap by 2-8%

**Trend**: If val loss improves, weight decay helping

### Fix 3: Data Augmentation ⭐⭐⭐

**What**: Artificially increase training set diversity

**Implementation** (for images):
```python
# PyTorch
from torchvision import transforms
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(0.2, 0.2, 0.2),
    transforms.RandomCrop(224),
    transforms.ToTensor(),
])
```

**For other data types**:
- Text: Back-translation, synonym replacement, random insertion/deletion
- Tabular: Mixup, SMOTE, Gaussian noise
- Time series: Time warping, magnitude warping, window slicing

**Expected impact**: Reduce train-val gap by 5-15%

**When most effective**: Image, text, audio data

### Fix 4: Early Stopping (Reduce Patience) ⭐⭐

**What**: Stop training when val loss stops improving

**Implementation**:
```yaml
# In config
early_stopping:
  patience: 5  # Reduce from 10-15
  metric: val_loss
  mode: min
```

**Recommended patience**:
- Fast baseline: 5-10 epochs
- Careful training: 10-15 epochs
- Final training: 15-20 epochs

**Expected impact**: Prevents continued overfitting, saves compute

**Symptom**: If early stopping triggers quickly, model capacity may be too high

### Fix 5: Reduce Model Capacity ⭐⭐

**What**: Use simpler model architecture

**Implementation**:
```python
# Before: Large model
model = nn.Sequential(
    nn.Linear(128, 512),
    nn.ReLU(),
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

# After: Simpler model
model = nn.Sequential(
    nn.Linear(128, 128),
    nn.ReLU(),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)
```

**Guidelines**:
- Reduce layer count (4 layers → 2-3 layers)
- Reduce hidden dimensions (512 → 256 → 128)
- Remove unnecessary layers

**Expected impact**: Reduce train-val gap by 5-10%

**Trade-off**: May reduce train accuracy, but could improve val accuracy

### Fix 6: Get More Training Data ⭐

**What**: Increase training set size

**Options**:
- Collect more labeled data (expensive, time-consuming)
- Use semi-supervised learning (leverage unlabeled data)
- Transfer learning (pre-train on related task)

**Expected impact**: Can eliminate overfitting if data insufficient

**When**: If data size <1000 samples and model complex

### Fix 7: Ensemble Methods ⭐

**What**: Train multiple models, average predictions

**Implementation**:
```python
# Train 5 models with different seeds
models = [train_model(seed=i) for i in range(5)]

# Ensemble prediction
predictions = [model(x) for model in models]
ensemble_pred = torch.mean(torch.stack(predictions), dim=0)
```

**Expected impact**: Reduce variance, improve generalization

**Trade-off**: 5x inference cost

---

## Decision Tree

```
Overfitting Detected (Train-Val Gap > 15%)
│
├─ Is data size small (<10K samples)?
│  ├─ Yes → Priority: Get more data, augmentation, transfer learning
│  └─ No → Continue
│
├─ Is model very large (>1M params)?
│  ├─ Yes → Priority: Reduce capacity, add dropout (0.3-0.5)
│  └─ No → Continue
│
├─ Is dropout low or absent (<0.2)?
│  ├─ Yes → Add dropout (0.2-0.4)
│  └─ No → Continue
│
├─ Is weight decay low (<1e-5)?
│  ├─ Yes → Increase weight decay (1e-4 to 1e-3)
│  └─ No → Continue
│
├─ Is data augmentation used?
│  ├─ No → Add data augmentation
│  └─ Yes → Continue
│
└─ Still overfitting?
   └─ Try combination: dropout + weight decay + augmentation + early stopping
```

---

## Monitoring After Fixes

### Key Metrics to Track

1. **Train-Val Gap**: Should decrease after fixes
   - Target: <10% for good generalization
   - Acceptable: 10-15%
   - Problem: >15%

2. **Val Loss Trend**: Should improve or stabilize
   - Good: Val loss decreasing
   - Acceptable: Val loss stable
   - Problem: Val loss increasing

3. **Best Epoch**: When val loss is minimum
   - If best epoch is early (epoch 5-10): Model overfitting quickly
   - If best epoch is late (epoch 40-50): Training can continue

### Experiment After Applying Fixes

**Before fixes**:
```
Epoch 30:
  Train Loss: 0.08  |  Val Loss: 0.52   (Gap: 0.44)
  Train Acc:  0.97  |  Val Acc:  0.73   (Gap: 0.24)
```

**After fixes** (dropout=0.3, weight_decay=1e-3, augmentation):
```
Epoch 30:
  Train Loss: 0.18  |  Val Loss: 0.28   (Gap: 0.10)
  Train Acc:  0.89  |  Val Acc:  0.84   (Gap: 0.05)
```

**Result**: Train accuracy decreased (0.97 → 0.89) but val accuracy increased (0.73 → 0.84). This is success—model now generalizes better.

---

## When Overfitting is Acceptable

### Scenario 1: Training Accuracy Still Low
If train accuracy <95%, overfitting may not be the primary issue:
- Model may lack capacity (underfitting on training data)
- Consider increasing capacity first before reducing it

### Scenario 2: Small Val Set
If validation set is very small (<500 samples):
- High variance in val metrics
- Gap may be statistical noise
- Use k-fold cross-validation to verify

### Scenario 3: Difficult Task
If task is inherently difficult (human performance ~80%):
- Gap of 10-15% may be acceptable
- Focus on improving both train and val, not just reducing gap

---

## Example: Fixing Overfitting

### Initial Training (Overfitting)
```python
# Config: baseline_config.yaml
model:
  architecture: deep_cnn
  hidden_dims: [512, 256, 128]
  dropout: 0.0  # No dropout

training:
  epochs: 50
  learning_rate: 1e-3
  weight_decay: 1e-5  # Minimal regularization
  data_augmentation: false

# Results:
# Epoch 30: Train Acc = 0.95, Val Acc = 0.72 (Gap: 23%)
```

### Apply Fixes
```python
# Config: fixed_config.yaml
model:
  architecture: medium_cnn  # Reduced capacity
  hidden_dims: [256, 128, 64]
  dropout: 0.3  # Added dropout

training:
  epochs: 50
  learning_rate: 1e-3
  weight_decay: 1e-3  # Increased regularization
  data_augmentation: true  # Added augmentation

  early_stopping:
    patience: 8  # Reduced from 15

# Results:
# Epoch 25 (early stopped): Train Acc = 0.88, Val Acc = 0.83 (Gap: 5%)
```

### Outcome
- Train accuracy decreased: 0.95 → 0.88 (-7%)
- Val accuracy increased: 0.72 → 0.83 (+11%)
- Gap reduced: 23% → 5%
- **Success**: Model now generalizes much better

---

## Summary

**Overfitting is fixable. Apply fixes systematically:**

1. **First try**: Add dropout (0.2-0.4) + increase weight decay (1e-3)
2. **If insufficient**: Add data augmentation
3. **If still overfitting**: Reduce model capacity
4. **If severe**: Combine all fixes

**Expected outcome**: Train accuracy may decrease slightly, but val accuracy should improve significantly.

**Goal**: Train-val gap <10-15%, both train and val accuracy high.

**Remember**: The goal is not perfect training accuracy. The goal is good validation (and test) accuracy.

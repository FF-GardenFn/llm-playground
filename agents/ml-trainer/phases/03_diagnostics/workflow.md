# Phase 3: Diagnostics - Detailed Workflow

**Phase**: 3 - Diagnostics
**Duration**: 15-30 minutes
**Goal**: Identify performance bottlenecks and generate Phase 4 optimization recommendations

---

## Prerequisites Verification

Before starting diagnostic analysis, verify Phase 2 complete:

**Gate**: `phases/02_baseline/checklists/post_baseline.md`

Required artifacts from Phase 2:
- ✅ baseline_results.md with metrics
- ✅ logs/training.log and logs/metrics.json
- ✅ Saved checkpoints (for analysis)
- ✅ Decision made to proceed to Phase 3

**If any missing**: Return to Phase 2, cannot proceed with diagnostics.

---

## Step 1: Load Baseline Results

### Action: Load and review baseline training metrics

**Manual Review**:

```bash
# Read baseline results
cat baseline_results.md

# Extract key metrics
grep "Train Loss" baseline_results.md
grep "Val Loss" baseline_results.md
grep "Train Acc" baseline_results.md
grep "Val Acc" baseline_results.md
grep "GPU Util" baseline_results.md
```

**Expected Output**:
```
Train Loss: 0.521 | Train Acc: 85.2%
Val Loss: 0.789 | Val Acc: 78.9%
GPU Util: 73%
Training Duration: 38 minutes
```

### Automated Analysis

```python
# Load metrics for programmatic analysis
import json

with open('logs/metrics.json') as f:
    metrics = json.load(f)

# Extract final epoch metrics
final_epoch = metrics['epochs'][-1]
train_loss = final_epoch['train_loss']
val_loss = final_epoch['val_loss']
train_acc = final_epoch['train_acc']
val_acc = final_epoch['val_acc']

# Calculate train-val gap
loss_gap = val_loss - train_loss
acc_gap = train_acc - val_acc

print(f"Train Loss: {train_loss:.3f} | Val Loss: {val_loss:.3f}")
print(f"Loss Gap: {loss_gap:.3f}")
print(f"Train Acc: {train_acc:.1f}% | Val Acc: {val_acc:.1f}%")
print(f"Accuracy Gap: {acc_gap:.1f}%")
```

---

## Step 2: Identify Primary Performance Issue

### Decision Tree: Which Diagnostic to Load?

**Question 1: Did training complete successfully?**

❌ **NO** - Training crashed, NaN losses, or severe errors
- **Auto-Load**: `diagnostics/nan_loss.md` (if NaN detected)
- **Auto-Load**: `diagnostics/convergence_stall.md` (if loss flat)
- **Action**: Fix infrastructure, restart Phase 2
- **Skip Steps 3-6**: Go directly to Step 7 (Fix and Restart)

✅ **YES** - Training completed, proceed to Question 2

---

**Question 2: Is there a large train-val gap?**

**Metric**: Accuracy Gap = Train Acc - Val Acc

- **Gap >15%**: Strong overfitting signal
- **Gap 10-15%**: Moderate overfitting
- **Gap 5-10%**: Mild overfitting (normal)
- **Gap <5%**: No overfitting

**Example**:
- Train Acc: 95.2%, Val Acc: 72.3% → Gap = 22.9% → **Strong overfitting** ❗

✅ **YES** (Gap >15%) - Overfitting detected
- **Auto-Load**: `diagnostics/overfitting.md`
- **Proceed to Step 3**

❌ **NO** (Gap <15%) - No clear overfitting, proceed to Question 3

---

**Question 3: Are both train and val metrics poor?**

**Metric**: Val Acc < Target (e.g., <70% when 80% required)

**Combined with**: Train Acc also relatively low (e.g., <80%)

**Example**:
- Train Acc: 68.2%, Val Acc: 66.5% → Both poor → **Underfitting** ❗

✅ **YES** - Both metrics poor
- **Auto-Load**: `diagnostics/underfitting.md`
- **Proceed to Step 3**

❌ **NO** - Metrics reasonable, proceed to Question 4

---

**Question 4: Is there high variance in validation metrics?**

**Metric**: Val Acc variance across epochs

**Calculate**:
```python
import numpy as np

val_accs = [epoch['val_acc'] for epoch in metrics['epochs']]
val_acc_std = np.std(val_accs)

print(f"Val Acc std: {val_acc_std:.2f}%")

# High variance threshold: >8%
if val_acc_std > 8.0:
    print("High variance detected - data quality issue")
```

**Example**:
- Val Acc: [65%, 78%, 62%, 81%, 59%, 76%] → Std = 8.9% → **High variance** ❗

✅ **YES** - High variance (>8%)
- **Auto-Load**: `diagnostics/data_quality.md`
- **Proceed to Step 3**

❌ **NO** - Variance acceptable, proceed to Question 5

---

**Question 5: Is GPU utilization low?**

**Metric**: Average GPU Utilization < 60%

**Check**:
```bash
grep "GPU Util" logs/training.log | awk '{sum+=$4; count++} END {print "Avg GPU Util:", sum/count "%"}'
```

**Example**:
- Avg GPU Util: 35% → **Resource inefficiency** ❗

✅ **YES** - GPU Util <60%
- **Auto-Load**: `diagnostics/resource_inefficiency.md`
- **Proceed to Step 3**

❌ **NO** - GPU utilization acceptable, proceed to Question 6

---

**Question 6: Baseline performance acceptable?**

**Metric**: Val Acc meets requirements

**Example**:
- Val Acc: 82%, Target: 80% → **Acceptable** ✓

✅ **YES** - Performance meets requirements
- **Decision**: Skip Phase 3 and Phase 4, proceed to Phase 5 (Finalization)
- **Rationale**: Baseline sufficient, optimization unnecessary

❌ **NO** - Performance below requirements but no clear diagnostic pattern
- **Auto-Load**: `diagnostics/general_improvement.md`
- **Action**: General hyperparameter tuning in Phase 4
- **Proceed to Step 3**

---

## Step 3: Load and Analyze Relevant Diagnostic

### Action: Deep dive into identified diagnostic file

**Diagnostic Files Available**:

1. **diagnostics/overfitting.md** (399 lines)
   - Symptoms, causes, fixes for train-val gap
   - Regularization strategies
   - Early stopping guidelines

2. **diagnostics/underfitting.md**
   - Model capacity analysis
   - Learning rate tuning
   - Training duration recommendations

3. **diagnostics/data_quality.md**
   - Label noise detection
   - Class imbalance analysis
   - Distribution mismatch identification

4. **diagnostics/resource_inefficiency.md**
   - GPU utilization optimization
   - Data loading bottleneck resolution
   - Batch size tuning

5. **diagnostics/convergence_stall.md**
   - Learning rate debugging
   - Initialization strategies
   - Gradient flow analysis

6. **diagnostics/nan_loss.md**
   - Numerical stability fixes
   - Gradient clipping
   - Mixed precision warnings

### Example: Load Overfitting Diagnostic

```bash
# Read overfitting diagnostic
cat diagnostics/overfitting.md
```

**Key Sections in overfitting.md**:

**Symptoms**:
- Train loss << Val loss (gap >0.5)
- Train accuracy - Val accuracy >15%
- Val loss increases while train loss decreases
- Model memorizing training data

**Causes**:
1. Model too complex (too many parameters)
2. Insufficient regularization (no dropout, weight decay)
3. Overly long training (past optimal point)
4. Data augmentation missing (data too small)

**Fixes (Prioritized)**:
1. **High Impact, Low Effort**:
   - Add dropout (0.3-0.5) ← **Start here**
   - Add weight decay (1e-4)
   - Enable early stopping (patience=5)

2. **High Impact, Medium Effort**:
   - Enable data augmentation
   - Reduce model capacity (30% fewer parameters)

3. **Medium Impact, High Effort**:
   - Collect more training data
   - Ensemble models

---

## Step 4: Match Baseline Symptoms to Diagnostic

### Action: Verify baseline results match diagnostic symptoms

**Overfitting Example**:

**Diagnostic Symptoms** (from overfitting.md):
- [✓] Train loss << Val loss
- [✓] Train acc - Val acc >15%
- [✓] Val loss increases in later epochs
- [✓] Model performs perfectly on train examples

**Baseline Metrics**:
- Train Loss: 0.123, Val Loss: 1.456 (gap = 1.333) ✓
- Train Acc: 95.2%, Val Acc: 72.3% (gap = 22.9%) ✓
- Epoch 15: Val Loss 1.456, Epoch 20: Val Loss 1.789 (increasing) ✓
- Sampled 10 train examples: 10/10 correct ✓

**Conclusion**: Strong overfitting confirmed ✓

---

## Step 5: Extract Recommendations from Diagnostic

### Action: Identify top 3-5 actionable optimizations

**From Diagnostic File** (overfitting.md):

**Recommendation 1: Add Dropout**
- Impact: High (expected val acc +3-5%)
- Effort: Low (single config change)
- Risk: Low (well-established technique)
- Implementation: `dropout: 0.4` in model config

**Recommendation 2: Add Weight Decay**
- Impact: High (expected val acc +2-4%)
- Effort: Low (single config change)
- Risk: Low (standard regularization)
- Implementation: `weight_decay: 1e-4` in optimizer config

**Recommendation 3: Enable Data Augmentation**
- Impact: Medium (expected val acc +2-3%)
- Effort: Medium (define augmentation pipeline)
- Risk: Low (task-appropriate transforms)
- Implementation: RandomCrop, HorizontalFlip, ColorJitter

**Recommendation 4: Early Stopping (More Aggressive)**
- Impact: Medium (prevent overtraining)
- Effort: Low (config change)
- Risk: Low (may stop slightly early)
- Implementation: `patience: 5` (reduced from 10)

**Recommendation 5: Reduce Model Capacity**
- Impact: Medium (expected val acc +1-2%)
- Effort: High (architecture change, re-train)
- Risk: Medium (may underfit)
- Implementation: ResNet18 → ResNet14 (fewer layers)

---

## Step 6: Generate Diagnostic Report

### Action: Create diagnostic_report.md with analysis and recommendations

**Automated Generation** (if tool available):

```bash
python diagnostic_tool.py \
  --baseline baseline_results.md \
  --metrics logs/metrics.json \
  --diagnostic overfitting \
  --output diagnostic_report.md
```

**Manual Creation**:

```markdown
# Diagnostic Report - Phase 3

**Date**: 2025-10-29
**Baseline Val Acc**: 72.3%
**Target Val Acc**: 80%
**Performance Gap**: -7.7%

---

## Analysis

### Primary Issue: Overfitting

**Evidence**:
- Train Acc: 95.2%, Val Acc: 72.3% (gap = 22.9%)
- Train Loss: 0.123, Val Loss: 1.456 (gap = 1.333)
- Val loss increased from epoch 15 (1.456) to epoch 20 (1.789)

**Diagnostic Loaded**: diagnostics/overfitting.md

### Root Causes

1. **Insufficient Regularization**
   - No dropout in model
   - No weight decay in optimizer
   - Model memorizing training data

2. **Overtraining**
   - Training continued past optimal point (epoch 15)
   - Early stopping patience too high (10 epochs)

3. **No Data Augmentation**
   - Training on fixed images without transforms
   - Model not learning robust features

---

## Recommendations for Phase 4

### High Priority (Implement First)

**1. Add Dropout (dropout=0.4)**
- Expected impact: +3-5% val acc
- Effort: Low (config change)
- Risk: Low
- Config: `model.dropout: 0.4`

**2. Add Weight Decay (weight_decay=1e-4)**
- Expected impact: +2-4% val acc
- Effort: Low (config change)
- Risk: Low
- Config: `optimizer.weight_decay: 1e-4`

**3. Reduce Early Stopping Patience (patience=5)**
- Expected impact: Stop at epoch 15 (prevent overtraining)
- Effort: Low (config change)
- Risk: Low
- Config: `early_stopping.patience: 5`

### Medium Priority (If Time Permits)

**4. Enable Data Augmentation**
- Expected impact: +2-3% val acc
- Effort: Medium (define pipeline)
- Risk: Low
- Transforms: RandomCrop, HorizontalFlip, ColorJitter

**5. Reduce Model Capacity (Optional)**
- Expected impact: +1-2% val acc
- Effort: High (architecture change)
- Risk: Medium (may underfit)
- Implementation: ResNet18 → ResNet14

---

## Phase 4 Configuration Preview

```yaml
# configs/optimization_config.yaml

model:
  architecture: ResNet18
  dropout: 0.4  # NEW: Anti-overfitting

optimizer:
  type: Adam
  learning_rate: 1e-3
  weight_decay: 1e-4  # NEW: L2 regularization

early_stopping:
  enabled: true
  patience: 5  # CHANGED: From 10 (stop earlier)

data_augmentation:  # NEW: Data augmentation
  enabled: true
  transforms:
    - random_crop: [32, 32]
    - horizontal_flip: {p: 0.5}
    - color_jitter: {brightness: 0.2, contrast: 0.2}

training:
  epochs: 50  # Increased (early stopping will control)
  batch_size: 32
```

---

## Expected Outcome

**After Phase 4 Optimization**:
- Expected Val Acc: 78-82% (from 72.3%)
- Expected improvement: +6-10% absolute
- Training time: 60-90 minutes (longer epochs, early stopping)

**Confidence**: High (overfitting well-understood, standard fixes)

---

## Decision: Proceed to Phase 4

**Scope**: Targeted anti-overfitting optimization

**Duration**: 1-2 hours (implement + train + evaluate)

**Risk**: Low (standard techniques, well-validated)
```

**Save**: diagnostic_report.md

---

## Step 7: Complete Diagnostics Checklist

### Action: Fill out diagnostics complete gate checklist

**Gate**: `phases/03_diagnostics/checklists/diagnostics_complete.md`

Verify all items before proceeding:
- [ ] Baseline results loaded and analyzed
- [ ] Primary performance issue identified (overfitting/underfitting/data/resource)
- [ ] Relevant diagnostic loaded (specific .md file)
- [ ] Symptoms matched to baseline metrics
- [ ] Root causes documented
- [ ] 3-5 specific recommendations generated
- [ ] Recommendations prioritized by impact/effort
- [ ] diagnostic_report.md generated
- [ ] Phase 4 configuration preview created
- [ ] Decision made: Phase 4 scope or skip to Phase 5

**Cannot proceed to Phase 4 without completing this checklist.**

---

## Decision Point: What's Next?

### Scenario 1: Proceed to Phase 4 (Optimization) ✓

**Criteria**:
- Clear improvement opportunities identified
- Recommendations have high expected impact
- Time budget allows optimization (1-8 hours)

**Next Phase**: ➡️ **Phase 4 (Optimization)**
- Implement top 3-5 recommendations
- Run hyperparameter optimization
- Evaluate improvements

---

### Scenario 2: Skip to Phase 5 (Finalization) ⏭️

**Criteria**:
- Diagnostic reveals baseline near-optimal
- Improvement potential <3% (not worth effort)
- Time constraints (need to deploy now)

**Next Phase**: ⏭️ **Phase 5 (Finalization)**
- Use baseline configuration for final training
- Focus on production deployment

---

### Scenario 3: Return to Phase 2 (Fix Infrastructure) ⚠️

**Criteria**:
- Diagnostic reveals broken infrastructure (data pipeline, NaN issues)
- Training failed to complete
- Severe resource inefficiency requires config changes

**Next Phase**: ⬅️ **Phase 2 (Baseline) - Restart**
- Fix identified issues
- Re-run baseline training
- Return to Phase 3 after successful baseline

---

## Common Diagnostic Scenarios

### Scenario A: Pure Overfitting (Train Good, Val Poor)

**Symptoms**:
- Train Acc: 95%, Val Acc: 72%
- Gap: 23%

**Diagnostic**: overfitting.md

**Phase 4 Strategy**: Add regularization (dropout + weight decay + data aug)

**Duration**: 1-2 hours

---

### Scenario B: Pure Underfitting (Both Poor)

**Symptoms**:
- Train Acc: 68%, Val Acc: 66%
- Gap: 2% (normal)

**Diagnostic**: underfitting.md

**Phase 4 Strategy**: Increase capacity + increase LR + train longer

**Duration**: 2-3 hours

---

### Scenario C: Mixed Issues (Overfitting + Resource Inefficiency)

**Symptoms**:
- Train Acc: 90%, Val Acc: 70% (overfitting)
- GPU Util: 35% (resource issue)

**Diagnostics**: overfitting.md + resource_inefficiency.md

**Phase 4 Strategy**:
1. Fix resource issue first (increase batch size)
2. Then address overfitting (add regularization)

**Duration**: 2-4 hours

---

### Scenario D: Near-Optimal Baseline

**Symptoms**:
- Val Acc: 82%, Target: 80%
- Train Acc: 86%, Gap: 4% (normal)
- GPU Util: 75% (good)

**Diagnostic**: Baseline meets requirements

**Phase 4 Strategy**: Skip Phase 4 → Phase 5

**Rationale**: Optimization has limited upside (<2% improvement potential)

---

## Time Budget

**Target**: 15-30 minutes total for Phase 3

**Breakdown**:
- Step 1 (Load baseline): 3 minutes
- Step 2 (Identify issue): 5 minutes
- Step 3 (Load diagnostic): 5 minutes
- Step 4 (Match symptoms): 2 minutes
- Step 5 (Extract recommendations): 5 minutes
- Step 6 (Generate report): 5-10 minutes
- Step 7 (Complete checklist): 3 minutes

**If exceeding 30 minutes**: Diagnostic analysis should be fast. Use decision tree to quickly identify primary issue.

---

## Success Criteria

Phase 3 complete when:

- ✅ Primary performance issue identified
- ✅ Relevant diagnostic loaded and analyzed
- ✅ Root causes documented
- ✅ 3-5 actionable recommendations generated
- ✅ Recommendations prioritized (high/medium/low impact)
- ✅ diagnostic_report.md created
- ✅ Phase 4 configuration preview drafted
- ✅ Diagnostics checklist complete
- ✅ Decision made on next phase (Phase 4 or Phase 5)

**Gate**: `phases/03_diagnostics/checklists/diagnostics_complete.md` must pass before proceeding.

---

## Tool Reference

**Diagnostic Analysis Tool** (if available):

```bash
# Automated diagnostic analysis
python diagnostic_tool.py \
  --baseline baseline_results.md \
  --metrics logs/metrics.json \
  --output diagnostic_report.md

# Generate Phase 4 config preview
python diagnostic_tool.py \
  --baseline baseline_results.md \
  --diagnostic overfitting \
  --generate-config configs/optimization_config.yaml
```

**Manual Analysis**: Follow decision tree in Step 2 to identify primary issue.

---

**Phase 3 quickly identifies performance bottlenecks using decision tree analysis. Auto-loading patterns match symptoms to diagnostics. Recommendations prioritized by impact and effort. Diagnostic report guides Phase 4 optimization. Fast analysis (15-30 min) determines strategy efficiently.**

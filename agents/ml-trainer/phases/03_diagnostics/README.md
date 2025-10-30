# Phase 3: Diagnostics

## Purpose

Analyze baseline performance to identify bottlenecks, root causes of poor performance, and generate targeted optimization recommendations for Phase 4.

**Target Duration**: 15-30 minutes
**Goal**: Understand what's limiting performance and recommend specific improvements
**Success**: Clear diagnostic report with actionable Phase 4 optimizations

---

## Objectives

### Primary Objectives

1. **Performance Analysis**
   - Compare baseline vs expected performance
   - Identify performance gaps (train vs val)
   - Quantify improvement potential

2. **Root Cause Identification**
   - Determine if overfitting, underfitting, or data issues
   - Detect resource inefficiencies
   - Identify convergence problems

3. **Optimization Planning**
   - Generate specific recommendations for Phase 4
   - Prioritize optimizations by expected impact
   - Estimate effort and risk for each optimization

---

## Prerequisites

### Required from Phase 2

- ✅ baseline_results.md with metrics
- ✅ Training logs (logs/training.log, logs/metrics.json)
- ✅ Saved checkpoints (for further analysis)
- ✅ Post-baseline checklist complete

**Gate**: Cannot start Phase 3 without Phase 2 complete

---

## When to Enter Phase 3

### Entry Scenario 1: Baseline Performance Insufficient

**Indicators**:
- Val accuracy below requirements (e.g., 65% when 80% needed)
- Large train-val gap (e.g., train=90%, val=70%)
- Performance plateaus early

**Next**: Diagnose root cause, proceed to Phase 4 with optimizations

---

### Entry Scenario 2: Baseline Training Failed

**Indicators**:
- NaN losses encountered
- No learning (loss flat)
- Training crashes
- GPU utilization extremely low (<40%)

**Next**: Diagnose infrastructure issues, fix, restart Phase 2

---

### Entry Scenario 3: Baseline Acceptable (Skip Phase 3)

**Indicators**:
- Val accuracy meets requirements
- No major issues
- Performance stable

**Next**: Skip Phase 3 and Phase 4, proceed directly to Phase 5 (Finalization)

---

## Diagnostic Categories

### 1. Overfitting Diagnostics → `diagnostics/overfitting.md`

**Symptoms**:
- Train loss << Val loss (large gap)
- Train accuracy high, val accuracy low
- Val loss increases while train loss decreases

**Example**:
```
Epoch 15: Train Loss=0.123, Val Loss=1.456
Epoch 20: Train Loss=0.045, Val Loss=1.789 (getting worse!)
```

**Likely Causes**:
- Model too complex for data
- Insufficient regularization
- Data augmentation needed
- Training too long

**Phase 4 Recommendations**:
- Add dropout (0.3-0.5)
- Add weight decay (1e-4)
- Enable data augmentation
- Early stopping (patience=5)
- Reduce model capacity

---

### 2. Underfitting Diagnostics → `diagnostics/underfitting.md`

**Symptoms**:
- Train loss and val loss both high
- Both metrics plateau early
- Loss doesn't decrease significantly

**Example**:
```
Epoch 1: Train Loss=2.145, Val Loss=2.187
Epoch 20: Train Loss=2.012, Val Loss=2.089 (barely improved)
```

**Likely Causes**:
- Model too simple (insufficient capacity)
- Learning rate too low
- Insufficient training time
- Poor feature representation

**Phase 4 Recommendations**:
- Increase model capacity (more layers/units)
- Increase learning rate (10x)
- Train longer (50-100 epochs)
- Add feature engineering

---

### 3. Data Quality Diagnostics → `diagnostics/data_quality.md`

**Symptoms**:
- Inconsistent performance across epochs
- High variance in validation metrics
- Model performs well on train, poorly on val (distribution mismatch)

**Example**:
```
Val Acc: [65%, 78%, 62%, 81%, 59%, 76%] (high variance)
```

**Likely Causes**:
- Label noise (incorrect labels)
- Data imbalance (some classes rare)
- Train-val distribution mismatch
- Data leakage

**Phase 4 Recommendations**:
- Clean labels (manual review + confidence filtering)
- Balance classes (oversampling/undersampling)
- Stratified split (ensure distribution match)
- Check for data leakage

---

### 4. Resource Inefficiency Diagnostics → `diagnostics/resource_inefficiency.md`

**Symptoms**:
- GPU utilization low (<60%)
- Training slower than expected
- CPU bottleneck (data loading)

**Example**:
```
GPU Utilization: 35% (should be 70-80%)
Time per epoch: 5 minutes (should be 2 minutes)
```

**Likely Causes**:
- Batch size too small
- DataLoader num_workers = 0 or too low
- Data loading on CPU not optimized
- pin_memory not enabled

**Phase 4 Recommendations**:
- Increase batch size (32 → 64 → 128)
- Increase num_workers (4 → 8)
- Enable pin_memory=True
- Use faster data format (e.g., LMDB instead of JPEG)

---

### 5. Convergence Diagnostics → `diagnostics/convergence_stall.md`

**Symptoms**:
- Loss plateaus early and doesn't improve
- Loss flat across all epochs
- No learning occurs

**Example**:
```
Epoch 1: Train Loss=2.303, Val Loss=2.301
Epoch 20: Train Loss=2.298, Val Loss=2.299 (no change)
```

**Likely Causes**:
- Learning rate too low (optimizer barely updates weights)
- Poor initialization (weights stuck in bad local minimum)
- Gradient vanishing (deep networks)
- Data pipeline broken (all same labels?)

**Phase 4 Recommendations**:
- Increase learning rate (1e-3 → 1e-2)
- Re-initialize model (different seed)
- Use better initialization (He/Xavier)
- Verify data pipeline integrity

---

### 6. NaN Loss Diagnostics → `diagnostics/nan_loss.md`

**Symptoms**:
- Loss becomes NaN after initial epochs
- Training crashes with "RuntimeError: NaN"
- Gradients explode to inf

**Example**:
```
Epoch 1: Train Loss=2.145
Epoch 2: Train Loss=1.987
Epoch 3: Train Loss=NaN ❌
```

**Likely Causes**:
- Learning rate too high (gradients explode)
- Numerical instability (overflow/underflow)
- Data contains inf/nan values
- Loss function issue (log(0), division by zero)

**Phase 4 Recommendations**:
- Reduce learning rate (1e-3 → 1e-4)
- Enable gradient clipping (max_norm=1.0)
- Check data for inf/nan: `data.isnan().any()`
- Use mixed precision training carefully

---

## Diagnostic Workflow

**Detailed Workflow**: See `workflow.md`

### High-Level Steps

1. **Load Baseline Results**
   - Read baseline_results.md
   - Load metrics from logs/metrics.json
   - Review training curves

2. **Identify Primary Issue**
   - Compare train vs val metrics
   - Check loss trajectory
   - Review GPU utilization

3. **Load Relevant Diagnostic**
   - Overfitting: Large train-val gap
   - Underfitting: Both metrics poor
   - Data quality: High variance
   - Resource inefficiency: GPU <60%
   - Convergence: Loss flat
   - NaN loss: Training crashed

4. **Analyze Root Causes**
   - Review symptoms section
   - Match patterns in baseline results
   - Identify most likely causes

5. **Generate Recommendations**
   - List specific optimizations for Phase 4
   - Prioritize by expected impact (high/medium/low)
   - Estimate implementation effort

6. **Document Diagnostic Report**
   - Create diagnostic_report.md
   - Include analysis, root causes, recommendations
   - Reference specific Phase 4 configurations

---

## Expected Outcomes

### Success Criteria

- ✅ Root cause of poor performance identified
- ✅ Diagnostic loaded and analyzed
- ✅ Specific optimizations recommended (3-5 items)
- ✅ Recommendations prioritized by impact
- ✅ diagnostic_report.md generated

### Typical Results

**Overfitting Diagnosis**:
- Root cause: Insufficient regularization, model too complex
- Recommendations:
  1. Add dropout=0.4 (high impact, low effort)
  2. Add weight_decay=1e-4 (high impact, low effort)
  3. Enable data augmentation (medium impact, medium effort)
  4. Reduce model capacity by 30% (medium impact, high effort)
- Expected improvement: Val acc 70% → 78% (8% gain)

**Underfitting Diagnosis**:
- Root cause: Model capacity insufficient, LR too low
- Recommendations:
  1. Increase model layers 3→5 (high impact, medium effort)
  2. Increase LR 1e-3→1e-2 (high impact, low effort)
  3. Train longer 20→50 epochs (medium impact, low effort)
- Expected improvement: Val acc 65% → 75% (10% gain)

---

## Common Diagnostic Patterns

### Pattern 1: Classic Overfitting

**Baseline Metrics**:
- Train Loss: 0.123, Train Acc: 95.2%
- Val Loss: 1.456, Val Acc: 72.3%

**Diagnosis**: Overfitting (train-val gap = 23%)

**Auto-Load**: diagnostics/overfitting.md

**Phase 4 Plan**:
```yaml
# configs/optimization_config.yaml (anti-overfitting)
regularization:
  dropout: 0.4
  weight_decay: 1e-4

data_augmentation:
  enabled: true
  transforms: [random_crop, horizontal_flip, color_jitter]

early_stopping:
  patience: 5  # Reduced from 10
```

**Expected**: Val acc 72% → 78-80%

---

### Pattern 2: Classic Underfitting

**Baseline Metrics**:
- Train Loss: 1.876, Train Acc: 68.2%
- Val Loss: 1.923, Val Acc: 66.5%

**Diagnosis**: Underfitting (both metrics poor)

**Auto-Load**: diagnostics/underfitting.md

**Phase 4 Plan**:
```yaml
# configs/optimization_config.yaml (anti-underfitting)
model:
  architecture: ResNet34  # Increased from ResNet18
  hidden_dim: 512  # Increased from 256

training:
  learning_rate: 1e-2  # Increased from 1e-3
  epochs: 50  # Increased from 20
```

**Expected**: Val acc 66% → 75-78%

---

### Pattern 3: Data Quality Issues

**Baseline Metrics**:
- Val Acc variance: ±12% across epochs
- Train Acc: 89%, Val Acc: 64% (suspicious gap despite no clear overfitting)

**Diagnosis**: Data quality (high variance, distribution mismatch)

**Auto-Load**: diagnostics/data_quality.md

**Phase 4 Plan**:
1. Manual label review (top 100 misclassified examples)
2. Check class balance: `Counter(labels)`
3. Stratified train-val split (ensure distribution match)
4. Data leakage audit (check for duplicates across splits)

**Expected**: Val acc 64% → 72-75% (after cleaning)

---

### Pattern 4: Resource Bottleneck

**Baseline Metrics**:
- GPU Utilization: 35%
- Time per epoch: 5 minutes (expected: 2 minutes)
- Val Acc: 78% (acceptable but training slow)

**Diagnosis**: Resource inefficiency (GPU underutilized)

**Auto-Load**: diagnostics/resource_inefficiency.md

**Phase 4 Plan**:
```yaml
# configs/optimization_config.yaml (resource optimization)
training:
  batch_size: 128  # Increased from 32
  num_workers: 8  # Increased from 4
  pin_memory: true

data:
  preprocessing: cached  # Precompute transforms
```

**Expected**: GPU util 35% → 75%, time per epoch 5min → 2min (2.5x speedup)

---

## Decision Point: Phase 4 Scope

### Narrow Optimization (Single Issue)

**When**: One clear root cause identified (e.g., pure overfitting)

**Phase 4 Approach**: Targeted fix (add regularization only)

**Duration**: 1-2 hours

---

### Broad Optimization (Multiple Issues)

**When**: Multiple root causes (e.g., overfitting + resource inefficiency + data quality)

**Phase 4 Approach**: Comprehensive tuning (hyperparameter sweep)

**Duration**: 4-8 hours (depending on search space)

---

### No Optimization Needed (Diagnostic Shows Baseline Near-Optimal)

**When**: Analysis reveals baseline already near Bayes error or data quality ceiling

**Phase 4 Approach**: Skip Phase 4, proceed to Phase 5

**Example**: "Model achieves 82% val acc, human agreement on task is 85% - further optimization has limited upside"

---

## Outputs

### Required Artifacts

1. **diagnostic_report.md** (Generated)
   - Root cause analysis
   - Diagnostic loaded (which .md file)
   - Symptoms matched
   - Recommendations prioritized
   - Phase 4 configuration preview

2. **Phase 4 Configuration Draft** (Optional)
   - configs/optimization_config.yaml with recommended changes
   - Can be refined in Phase 4

---

## Next Steps

### Proceed to Phase 4: Optimization

**When**: Recommendations generated, improvement potential identified

**Phase 4 Scope**: Implement top 3-5 recommendations from diagnostic report

---

### Skip to Phase 5: Finalization

**When**: Diagnostic reveals baseline near-optimal or optimization ROI low

**Rationale**: Further tuning unlikely to improve significantly

---

### Return to Phase 2: Restart Baseline

**When**: Diagnostic reveals infrastructure issues (e.g., data pipeline broken, severe NaN issues)

**Fix Issues**: Correct configuration, data pipeline, seeds

**Re-run**: Phase 2 with fixes

---

## Checklist Gate

**Diagnostics Complete Checklist**: `checklists/diagnostics_complete.md`

Cannot proceed to Phase 4 without completing this checklist:
- [ ] Baseline results loaded and analyzed
- [ ] Primary performance issue identified
- [ ] Relevant diagnostic loaded (overfitting.md, underfitting.md, etc.)
- [ ] Root causes documented
- [ ] 3-5 specific recommendations generated
- [ ] Recommendations prioritized by impact
- [ ] diagnostic_report.md generated
- [ ] Decision made: Phase 4 scope or skip to Phase 5

---

## Time Budget

**Target**: 15-30 minutes

**Breakdown**:
- Load and analyze baseline results: 5 minutes
- Identify primary issue and load diagnostic: 5 minutes
- Analyze root causes: 5-10 minutes
- Generate recommendations: 5-10 minutes
- Document diagnostic report: 5 minutes

**If exceeding 30 minutes**: Diagnostic workflow should be quick. Use auto-loading patterns to navigate efficiently.

---

**Phase 3 identifies performance bottlenecks and generates targeted optimization recommendations. Fast diagnostic analysis (15-30 min) determines Phase 4 scope. Auto-loading patterns match symptoms to diagnostic files. Recommendations prioritized by expected impact. Decision point determines optimization strategy or skips to finalization.**

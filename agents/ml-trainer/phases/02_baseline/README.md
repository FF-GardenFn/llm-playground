# Phase 2: Baseline Training

## Purpose

Execute fast baseline training to verify infrastructure works and establish reasonable performance quickly.

**Target Duration**: 30-60 minutes
**Goal**: Working training pipeline with acceptable initial performance
**Success**: Training completes without crashes, GPU utilization >60%, checkpoint saved

---

## Objectives

### Primary Objectives

1. **Infrastructure Verification**
   - Confirm training loop executes without errors
   - Validate data loading pipeline works
   - Verify GPU/accelerator utilization
   - Test checkpoint saving/loading

2. **Baseline Performance**
   - Establish initial performance benchmark
   - Verify model learns (loss decreases)
   - Check for obvious failure modes (NaN loss, exploding gradients)
   - Create comparison point for optimization

3. **Quick Iteration**
   - Complete training in 30-60 minutes
   - Use conservative hyperparameters (safe choices)
   - Enable early stopping (avoid wasting compute)
   - Focus on completion, not perfection

---

## Prerequisites

### Required from Phase 1

- ✅ `training_config.yaml` with baseline settings
- ✅ Reproducibility checklist complete (all seeds fixed)
- ✅ Environment documented (versions, hardware)
- ✅ Data pipeline configured

**Gate**: Cannot start Phase 2 without Phase 1 checklist complete

---

## Configuration

**Template**: `configs/baseline_template.yaml`

### Key Settings

```yaml
training:
  epochs: 20                    # Short training for fast iteration
  batch_size: 32               # Moderate batch size (adjust for GPU)
  learning_rate: 1e-3          # Conservative LR (safe default)

early_stopping:
  enabled: true
  patience: 10                  # Stop if no improvement for 10 epochs
  min_delta: 0.001             # Minimum improvement threshold

checkpointing:
  save_best: true              # Save best val metric model
  save_last: true              # Save for resumption
  checkpoint_every_n_epochs: 5  # Periodic checkpoints

validation:
  validate_every_n_epochs: 1    # Validate frequently
  metric: 'val_loss'           # Primary validation metric
```

### Why Conservative?

- **Fast completion**: 20 epochs with early stopping targets 30-60 min
- **Safe defaults**: LR=1e-3 works for most architectures
- **Early failure detection**: Frequent validation catches issues quickly

---

## Workflow

**Detailed Workflow**: See `workflow.md`

### High-Level Steps

1. **Load Config**
   - Use `configs/baseline_template.yaml`
   - Customize for task (adjust batch size, epochs if needed)

2. **Initialize Infrastructure**
   - Set all seeds (from reproducibility checklist)
   - Enable deterministic operations
   - Setup data loaders
   - Initialize model, optimizer, scheduler

3. **Execute Training**
   - Train for up to 20 epochs
   - Validate every epoch
   - Save checkpoints (best + periodic)
   - Monitor for issues (NaN loss, exploding gradients)
   - Early stop if no improvement (patience=10)

4. **Post-Training**
   - Generate baseline_results.md
   - Save final checkpoint
   - Document performance metrics
   - Complete post_baseline checklist

---

## Expected Outcomes

### Success Criteria

- ✅ Training completes without crashes
- ✅ Loss decreases over epochs (model learns)
- ✅ No NaN losses encountered
- ✅ GPU utilization >60%
- ✅ Best checkpoint saved
- ✅ baseline_results.md generated

### Typical Results

**Image Classification** (50K images):
- Training time: 40-55 minutes
- Val accuracy: 75-85% (task-dependent)
- GPU utilization: 70-85%
- Checkpoints saved: Best + epoch_5, epoch_10, epoch_15, last

**Text Classification** (100K examples):
- Training time: 30-45 minutes
- Val accuracy: 80-90% (task-dependent)
- GPU utilization: 60-75%
- Checkpoints saved: Best + epoch_5, epoch_10, epoch_15, last

---

## Common Issues

### Issue: GPU Utilization Low (<60%)

**Symptoms**: Training slower than expected, GPU not fully utilized

**Likely Causes**:
- Batch size too small
- Data loading bottleneck (I/O bound)
- Model too small for GPU

**Fixes**:
- Increase batch size (2x, 4x until memory limit)
- Increase DataLoader num_workers
- Use pin_memory=True for CUDA
- Profile data loading time

**Diagnostic**: Load `diagnostics/resource_inefficiency.md`

---

### Issue: Loss Becomes NaN

**Symptoms**: Loss shows NaN after initial epochs

**Likely Causes**:
- Learning rate too high
- Numerical instability in loss function
- Gradient explosion

**Fixes**:
- Reduce LR by 10x
- Enable gradient clipping (max_norm=1.0)
- Check data preprocessing (inf/nan values?)

**Diagnostic**: Load `diagnostics/nan_loss.md`

---

### Issue: No Learning (Loss Plateau)

**Symptoms**: Loss doesn't decrease, stays flat

**Likely Causes**:
- Learning rate too low
- Model random initialization poor
- Data pipeline broken (labels wrong?)

**Fixes**:
- Increase LR 10x
- Re-initialize model (try different seed)
- Verify data loading (check labels match images)

**Diagnostic**: Load `diagnostics/convergence_stall.md`

---

## Outputs

### Required Artifacts

1. **baseline_results.md** (Generated)
   - Training metrics (loss, accuracy)
   - Validation metrics
   - Training duration
   - GPU utilization stats
   - Learning curves (plots if available)

2. **Checkpoints** (Saved in checkpoints/)
   - `best_model.pt` - Best validation metric
   - `last_model.pt` - Final epoch (for resumption)
   - `checkpoint_epoch_5.pt`, `checkpoint_epoch_10.pt`, etc.

3. **Logs** (Saved in logs/)
   - `training.log` - Detailed training log
   - `metrics.json` - Epoch-by-epoch metrics

---

## Next Steps

### Decision Point: Is Baseline Performance Acceptable?

**If YES** (Performance meets requirements):
- ⏭️ Skip Phase 4 (Optimization)
- ➡️ Proceed to Phase 5 (Finalization)
- Use baseline config for final training

**If NO** (Performance insufficient):
- ➡️ Proceed to Phase 3 (Diagnostics)
- Analyze what's limiting performance
- Then Phase 4 (Optimization) for hyperparameter tuning

**If FAILURE** (Training crashed, NaN loss, no learning):
- ➡️ Proceed to Phase 3 (Diagnostics)
- Load relevant diagnostic (nan_loss.md, convergence_stall.md, etc.)
- Fix issues, restart Phase 2

---

## Checklist Gate

**Post-Baseline Checklist**: `checklists/post_baseline.md`

Cannot proceed to Phase 3 without completing this checklist:
- [ ] Training completed without crashes
- [ ] Best checkpoint saved
- [ ] baseline_results.md generated
- [ ] GPU utilization documented (>60% target)
- [ ] Decision made: Deploy baseline OR optimize further

---

**Phase 2 validates infrastructure and establishes performance baseline. Fast iteration is the goal. Perfection comes in Phase 4 (if needed) or Phase 5.**

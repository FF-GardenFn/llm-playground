# Phase 2: Baseline Training - Detailed Workflow

**Phase**: 2 - Baseline Training
**Duration**: 30-60 minutes
**Goal**: Verify training infrastructure works and establish performance baseline

---

## Prerequisites Verification

Before starting baseline training, verify Phase 1 gate passed:

**Gate**: `phases/01_planning/checklists/reproducibility_gate.md`

Required artifacts from Phase 1:
- ✅ `training_config.yaml` with baseline settings
- ✅ All seeds fixed (Python, NumPy, PyTorch/TF, DataLoader, CUDA)
- ✅ Environment documented (versions, hardware, OS)
- ✅ Data pipeline configured

**If any missing**: Return to Phase 1, cannot proceed with baseline training.

---

## Step 1: Load Configuration

### Action: Load baseline configuration

**Tool**: `training_orchestrator`

```bash
python training_orchestrator.py --config configs/training_config.yaml --mode baseline
```

### Verification

**Expected Output**:
```
✓ Configuration loaded: configs/training_config.yaml
✓ Mode: baseline
✓ Epochs: 20
✓ Batch size: 32
✓ Learning rate: 1e-3
✓ Early stopping: enabled (patience=10)
✓ Checkpointing: enabled (save_best=true, save_last=true)
```

**If errors**: Check YAML syntax, verify required fields present

### Configuration Review

Baseline config should have:
- **Conservative hyperparameters** (LR=1e-3, standard optimizer)
- **Short training** (20 epochs with early stopping)
- **Frequent validation** (every epoch)
- **Checkpoint saving** (best + periodic + last)

**Rationale**: Fast iteration, safe defaults, early failure detection

---

## Step 2: Initialize Reproducibility Infrastructure

### Action: Set all seeds and enable deterministic operations

**Automatic** (handled by training_orchestrator):

```python
# Python random seed
random.seed(config.seed)

# NumPy seed
np.random.seed(config.seed)

# PyTorch seeds
torch.manual_seed(config.seed)
torch.cuda.manual_seed_all(config.seed)

# Deterministic operations (slower but reproducible)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# DataLoader worker seeds
def worker_init_fn(worker_id):
    np.random.seed(config.seed + worker_id)
```

### Verification

**Expected Log Output**:
```
[REPRODUCIBILITY] Python random seed: 42
[REPRODUCIBILITY] NumPy seed: 42
[REPRODUCIBILITY] PyTorch manual seed: 42
[REPRODUCIBILITY] PyTorch CUDA seed: 42
[REPRODUCIBILITY] CUDNN deterministic: True
[REPRODUCIBILITY] CUDNN benchmark: False
[REPRODUCIBILITY] DataLoader worker_init_fn: configured
```

**If missing**: Reproducibility infrastructure not initialized correctly, check training_orchestrator implementation

---

## Step 3: Initialize Data Loaders

### Action: Create training and validation data loaders

**Automatic** (handled by training_orchestrator):

```python
train_loader = DataLoader(
    train_dataset,
    batch_size=config.batch_size,
    shuffle=True,
    num_workers=config.num_workers,
    pin_memory=config.pin_memory,
    worker_init_fn=worker_init_fn,  # Reproducibility
    drop_last=config.drop_last
)

val_loader = DataLoader(
    val_dataset,
    batch_size=config.batch_size,
    shuffle=False,  # No shuffling for validation
    num_workers=config.num_workers,
    pin_memory=config.pin_memory
)
```

### Verification

**Expected Log Output**:
```
[DATA] Train dataset: 45000 samples
[DATA] Validation dataset: 5000 samples
[DATA] Train batches: 1407 (batch_size=32)
[DATA] Validation batches: 157 (batch_size=32)
[DATA] DataLoader workers: 4
[DATA] Pin memory: True
```

**Diagnostic Trigger**:
- If train batches < 100: Data loading may be slow, check batch size
- If num_workers = 0: Data loading bottleneck likely, increase workers

---

## Step 4: Initialize Model, Optimizer, Scheduler

### Action: Create model architecture and training components

**Automatic** (handled by training_orchestrator):

```python
# Model initialization
model = create_model(config.model)
model = model.to(device)

# Optimizer
optimizer = create_optimizer(
    model.parameters(),
    config.optimizer,
    lr=config.learning_rate
)

# Learning rate scheduler
scheduler = create_scheduler(
    optimizer,
    config.scheduler
)

# Loss function
criterion = create_criterion(config.loss)
```

### Verification

**Expected Log Output**:
```
[MODEL] Architecture: ResNet18
[MODEL] Parameters: 11,689,512
[MODEL] Device: cuda:0
[OPTIMIZER] Type: Adam
[OPTIMIZER] Learning rate: 1e-3
[OPTIMIZER] Weight decay: 0.0
[SCHEDULER] Type: ReduceLROnPlateau
[SCHEDULER] Patience: 5
[CRITERION] Loss function: CrossEntropyLoss
```

**Diagnostic Trigger**:
- If device = cpu and CUDA available: GPU not being used, check device configuration
- If parameters > 100M: Large model, check GPU memory capacity

---

## Step 5: Execute Training Loop

### Action: Train for up to 20 epochs with early stopping

**Automatic** (handled by training_orchestrator):

```python
for epoch in range(1, config.epochs + 1):
    # Training phase
    model.train()
    train_loss, train_metrics = train_epoch(
        model, train_loader, criterion, optimizer, device
    )

    # Validation phase
    model.eval()
    with torch.no_grad():
        val_loss, val_metrics = validate_epoch(
            model, val_loader, criterion, device
        )

    # Logging
    log_epoch_metrics(epoch, train_loss, train_metrics, val_loss, val_metrics)

    # Learning rate scheduling
    scheduler.step(val_loss)

    # Checkpointing
    save_checkpoint(epoch, model, optimizer, scheduler, val_loss)

    # Early stopping
    if early_stopping_triggered(val_loss, patience=10):
        print(f"Early stopping triggered at epoch {epoch}")
        break
```

### Expected Progress

**Epoch 1**:
```
[EPOCH 1/20]
  Train Loss: 2.145 | Train Acc: 35.2%
  Val Loss: 1.987 | Val Acc: 42.1%
  LR: 1.00e-03
  GPU Util: 72% | Time: 2m 15s
  Checkpoint: saved (best_model.pt)
```

**Epoch 5**:
```
[EPOCH 5/20]
  Train Loss: 1.234 | Train Acc: 68.7%
  Val Loss: 1.456 | Val Acc: 62.3%
  LR: 1.00e-03
  GPU Util: 74% | Time: 2m 10s
  Checkpoint: saved (checkpoint_epoch_5.pt)
```

**Epoch 15** (Early stopping):
```
[EPOCH 15/20]
  Train Loss: 0.521 | Train Acc: 85.2%
  Val Loss: 0.789 | Val Acc: 78.9%
  LR: 1.00e-04 (reduced)
  GPU Util: 73% | Time: 2m 12s
  Early stopping: no improvement for 10 epochs
  Best checkpoint: epoch_5.pt (val_loss=0.745)
```

### Monitoring During Training

**What to watch**:
1. **Loss decreasing**: Train and val loss should trend downward
2. **No NaN losses**: If NaN appears, training has failed
3. **GPU utilization >60%**: If lower, data loading bottleneck likely
4. **Reasonable time per epoch**: Should be consistent (±10%)

### Diagnostic Triggers (Automatic)

Training orchestrator will automatically detect and respond to:

**1. NaN Loss Detected**:
```
[DIAGNOSTIC] NaN loss detected at epoch 3
[AUTO-LOAD] diagnostics/nan_loss.md
[ACTIONS]
  - Reduce learning rate by 10x
  - Enable gradient clipping (max_norm=1.0)
  - Check data for inf/nan values
[RESTART] Training from last valid checkpoint
```

**2. No Learning (Loss Plateau)**:
```
[DIAGNOSTIC] No improvement for 15 epochs (loss plateau)
[AUTO-LOAD] diagnostics/convergence_stall.md
[ACTIONS]
  - Increase learning rate by 10x
  - Re-initialize model (different seed)
  - Verify data loading (labels correct?)
[SUGGESTIONS] Review diagnostic for manual intervention
```

**3. Overfitting Detected**:
```
[DIAGNOSTIC] Train loss << Val loss (overfitting)
  Train Loss: 0.123 | Val Loss: 1.456
[AUTO-LOAD] diagnostics/overfitting.md
[ACTIONS]
  - Stop training (no further improvement likely)
  - Recommend Phase 4 (Optimization) with regularization
```

**4. Resource Inefficiency**:
```
[DIAGNOSTIC] GPU utilization low (45%)
[AUTO-LOAD] diagnostics/resource_inefficiency.md
[ACTIONS]
  - Increase batch size (current: 32 → suggested: 64)
  - Increase DataLoader workers (current: 4 → suggested: 8)
  - Enable pin_memory if not already
```

---

## Step 6: Post-Training Analysis

### Action: Generate baseline results report

**Automatic** (handled by training_orchestrator):

```python
# Generate baseline_results.md
generate_baseline_report(
    config=config,
    final_metrics=final_metrics,
    training_history=training_history,
    checkpoints=checkpoints,
    gpu_stats=gpu_stats
)
```

### Verification

**Check generated file**: `baseline_results.md`

**Expected Content**:
```markdown
# Baseline Training Results

**Date**: 2025-10-29
**Duration**: 38 minutes
**Final Epoch**: 15/20 (early stopped)

## Configuration
- Model: ResNet18
- Optimizer: Adam (lr=1e-3)
- Batch size: 32
- Epochs: 15/20

## Final Metrics
- **Train Loss**: 0.521 | **Train Acc**: 85.2%
- **Val Loss**: 0.789 | **Val Acc**: 78.9%
- **Best Val Loss**: 0.745 (epoch 5)

## Training Profile
- Avg time per epoch: 2m 12s
- Avg GPU utilization: 73%
- Total GPU time: 33 minutes

## Checkpoints Saved
- best_model.pt (epoch 5, val_loss=0.745)
- last_model.pt (epoch 15)
- checkpoint_epoch_5.pt
- checkpoint_epoch_10.pt

## Learning Curves
[Plot: train_loss vs val_loss over epochs]

## Decision Point
Performance: ACCEPTABLE ✓
Recommendation: Proceed to Phase 5 (Finalization)
```

---

## Step 7: Verify Checkpoints

### Action: Confirm all checkpoints saved correctly

**Manual Verification**:

```bash
ls -lh checkpoints/
```

**Expected Output**:
```
-rw-r--r-- 1 user 44M best_model.pt
-rw-r--r-- 1 user 44M last_model.pt
-rw-r--r-- 1 user 44M checkpoint_epoch_5.pt
-rw-r--r-- 1 user 44M checkpoint_epoch_10.pt
-rw-r--r-- 1 user 44M checkpoint_epoch_15.pt
```

**If missing**: Checkpoint saving failed, check checkpointing configuration

### Test Checkpoint Loading

```python
# Load best checkpoint
checkpoint = torch.load('checkpoints/best_model.pt')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

# Verify metrics match
assert checkpoint['val_loss'] == 0.745
assert checkpoint['epoch'] == 5
```

**If errors**: Checkpoint corruption, review checkpointing/strategies.md

---

## Step 8: Complete Post-Baseline Checklist

### Action: Fill out post-baseline gate checklist

**Gate**: `phases/02_baseline/checklists/post_baseline.md`

Verify all items before proceeding:
- [ ] Training completed without crashes
- [ ] Loss decreased over epochs (model learned)
- [ ] No NaN losses encountered
- [ ] GPU utilization >60%
- [ ] Best checkpoint saved
- [ ] baseline_results.md generated
- [ ] Decision made: Deploy baseline OR optimize further

**Cannot proceed to Phase 3 without completing this checklist.**

---

## Decision Point: What's Next?

### Scenario 1: Baseline Performance ACCEPTABLE ✓

**Criteria**:
- Val accuracy meets requirements (e.g., >75%)
- No major issues detected
- Training stable and reproducible

**Next Phase**: ⏭️ **Phase 5 (Finalization)**
- Skip Phase 3 (Diagnostics) and Phase 4 (Optimization)
- Use baseline configuration for final training
- Focus on production deployment

---

### Scenario 2: Baseline Performance INSUFFICIENT ❌

**Criteria**:
- Val accuracy below requirements (e.g., <60%)
- Performance gap between train and val (overfitting)
- Need hyperparameter optimization

**Next Phase**: ➡️ **Phase 3 (Diagnostics)**
- Analyze what's limiting performance
- Identify bottlenecks (data quality, model capacity, regularization)
- Generate recommendations for Phase 4 (Optimization)

---

### Scenario 3: Baseline Training FAILED ⚠️

**Criteria**:
- Training crashed or hung
- NaN losses
- No learning (loss plateau)
- GPU utilization extremely low

**Next Phase**: ➡️ **Phase 3 (Diagnostics)**
- Load relevant diagnostic (nan_loss.md, convergence_stall.md, resource_inefficiency.md)
- Fix infrastructure issues
- Restart Phase 2 with corrected configuration

---

## Common Failure Modes

### Failure: Training Crashes at Epoch 1

**Symptoms**: Process terminates with error, no checkpoints saved

**Likely Causes**:
- Out of memory (batch size too large)
- Data loading error (corrupted files, wrong paths)
- Model initialization error

**Auto-Load**: diagnostics/crashes.md

**Immediate Actions**:
1. Check error message for clues
2. Reduce batch size by half
3. Verify data paths exist
4. Test model forward pass with single batch

---

### Failure: NaN Loss at Epoch 5

**Symptoms**: Loss shows NaN, gradients explode

**Likely Causes**:
- Learning rate too high
- Numerical instability (overflow/underflow)
- Data contains inf/nan values

**Auto-Load**: diagnostics/nan_loss.md

**Immediate Actions**:
1. Reduce LR by 10x (1e-3 → 1e-4)
2. Enable gradient clipping (max_norm=1.0)
3. Check data for inf/nan: `data.isnan().any()`

---

### Failure: No Learning (Loss Flat)

**Symptoms**: Loss doesn't decrease, stays constant across epochs

**Likely Causes**:
- Learning rate too low
- Model initialization poor (all zeros?)
- Data pipeline broken (all same label?)

**Auto-Load**: diagnostics/convergence_stall.md

**Immediate Actions**:
1. Increase LR by 10x (1e-3 → 1e-2)
2. Re-initialize model with different seed
3. Verify data labels: `print(labels[:10])`

---

### Failure: GPU Utilization <40%

**Symptoms**: Training slow, GPU mostly idle

**Likely Causes**:
- Batch size too small (GPU underutilized)
- Data loading bottleneck (CPU-bound)
- num_workers = 0 (single-threaded loading)

**Auto-Load**: diagnostics/resource_inefficiency.md

**Immediate Actions**:
1. Increase batch size (32 → 64 → 128 until GPU memory full)
2. Increase num_workers (0 → 4 → 8)
3. Enable pin_memory=True

---

## Time Budget

**Target**: 30-60 minutes total for Phase 2

**Breakdown**:
- Step 1-4 (Setup): 5 minutes
- Step 5 (Training): 25-50 minutes (depends on dataset size, epochs)
- Step 6-8 (Post-training): 5 minutes

**If exceeding 60 minutes**: Training too slow, likely resource inefficiency. Load diagnostics/resource_inefficiency.md.

---

## Success Criteria

Phase 2 complete when:

- ✅ Training executed without crashes
- ✅ Loss decreased (model learned)
- ✅ No NaN losses
- ✅ GPU utilization >60%
- ✅ Checkpoints saved (best + periodic + last)
- ✅ baseline_results.md generated
- ✅ Post-baseline checklist complete
- ✅ Decision made on next phase

**Gate**: `phases/02_baseline/checklists/post_baseline.md` must pass before proceeding.

---

## Tool Reference

**Primary Tool**: `training_orchestrator`

```bash
# Run baseline training
python training_orchestrator.py \
  --config configs/training_config.yaml \
  --mode baseline \
  --output-dir results/baseline/

# Resume from checkpoint
python training_orchestrator.py \
  --config configs/training_config.yaml \
  --mode baseline \
  --resume checkpoints/last_model.pt

# Enable verbose logging
python training_orchestrator.py \
  --config configs/training_config.yaml \
  --mode baseline \
  --verbose
```

**Diagnostic Tools**: Automatically loaded by training_orchestrator when issues detected.

---

**Phase 2 establishes performance baseline quickly. Conservative hyperparameters ensure safe completion. Diagnostics trigger automatically on failures. Checkpoints saved at every step for reproducibility. Decision point determines whether optimization needed or baseline sufficient.**

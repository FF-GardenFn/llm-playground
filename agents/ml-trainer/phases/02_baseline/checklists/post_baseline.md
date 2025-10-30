# Post-Baseline Training Checklist

**Gate**: Phase 2 → Phase 3 (or Phase 5)
**Purpose**: Verify baseline training completed successfully before proceeding

---

## Mandatory Verification

**This checklist MUST be completed before proceeding to next phase.**

Cannot proceed if ANY checkbox is unchecked.

---

## ✅ Training Execution Verification

### Training Completion

- [ ] **Training completed without crashes**
  - No process termination errors
  - No out-of-memory errors
  - No unhandled exceptions
  - Training reached final epoch or early stopping

**Verification**:
```bash
# Check training logs for completion
grep "Training complete" logs/training.log

# Verify no error messages
grep -i "error\|exception\|crash" logs/training.log
```

**If unchecked**: Training failed to complete. Review logs, identify failure cause, fix issues, restart Phase 2.

---

### Loss Convergence

- [ ] **Loss decreased over epochs (model learned)**
  - Initial train loss > Final train loss
  - Loss shows downward trend (not flat)
  - Learning occurred (not random baseline)

**Verification**:
```python
# Load metrics from training log
import json
with open('logs/metrics.json') as f:
    metrics = json.load(f)

initial_loss = metrics['epochs'][0]['train_loss']
final_loss = metrics['epochs'][-1]['train_loss']

assert final_loss < initial_loss, "Loss did not decrease"
print(f"Loss improvement: {initial_loss:.3f} → {final_loss:.3f}")
```

**Expected**: Loss decreases by >50% from initial to final epoch

**If unchecked**: No learning occurred. Load `diagnostics/convergence_stall.md`, diagnose issue, adjust learning rate or model initialization.

---

### Numerical Stability

- [ ] **No NaN losses encountered**
  - All epoch losses are finite numbers
  - No inf values in loss or gradients
  - Training numerically stable

**Verification**:
```python
# Check for NaN in metrics
import math
for epoch in metrics['epochs']:
    assert math.isfinite(epoch['train_loss']), f"NaN at epoch {epoch['num']}"
    assert math.isfinite(epoch['val_loss']), f"NaN at epoch {epoch['num']}"
print("✓ All losses finite")
```

**If unchecked**: NaN loss detected. Load `diagnostics/nan_loss.md`, reduce learning rate, enable gradient clipping, restart Phase 2.

---

## ✅ Resource Utilization Verification

### GPU Efficiency

- [ ] **GPU utilization >60%**
  - Average GPU utilization across all epochs >60%
  - No severe resource inefficiency
  - Training not bottlenecked on data loading

**Verification**:
```bash
# Check GPU utilization from logs
grep "GPU Util" logs/training.log | awk '{sum+=$4; count++} END {print "Avg GPU Util:", sum/count "%"}'
```

**Expected**: Average GPU utilization 60-85%

**If <60%**: Resource inefficiency. Load `diagnostics/resource_inefficiency.md`, increase batch size or num_workers.

**If >90%**: Excellent utilization, consider increasing batch size further for potential speedup.

**If unchecked but >40%**: Acceptable. Document in baseline_results.md as "room for optimization".

---

### Training Time

- [ ] **Training duration within expected range**
  - Completed in 30-90 minutes (baseline target: 30-60 min)
  - Time per epoch consistent (±20%)
  - No unexplained slowdowns

**Verification**:
```bash
# Calculate total training time
grep "EPOCH" logs/training.log | head -1  # First epoch timestamp
grep "Training complete" logs/training.log  # Final timestamp
# Manual calculation or use training_orchestrator report
```

**If >90 minutes**: Training too slow. Check GPU utilization, data loading, consider optimization.

---

## ✅ Checkpointing Verification

### Checkpoint Files Saved

- [ ] **Best checkpoint saved**
  - `checkpoints/best_model.pt` exists
  - Contains model_state_dict, optimizer_state_dict, epoch, metrics
  - File size reasonable (not 0 bytes)

**Verification**:
```bash
ls -lh checkpoints/best_model.pt
# Should show file size (e.g., 44M for ResNet18)

python -c "
import torch
ckpt = torch.load('checkpoints/best_model.pt')
assert 'model_state_dict' in ckpt
assert 'optimizer_state_dict' in ckpt
assert 'epoch' in ckpt
assert 'val_loss' in ckpt
print(f'✓ Best checkpoint valid (epoch {ckpt[\"epoch\"]}, val_loss={ckpt[\"val_loss\"]:.3f})')
"
```

**If unchecked**: Checkpoint not saved or corrupted. Review `checkpointing/strategies.md`, check disk space, restart Phase 2 with checkpointing enabled.

---

- [ ] **Last checkpoint saved**
  - `checkpoints/last_model.pt` exists
  - Allows resumption if needed
  - Contains final training state

**Verification**:
```bash
ls -lh checkpoints/last_model.pt

python -c "
import torch
ckpt = torch.load('checkpoints/last_model.pt')
assert 'model_state_dict' in ckpt
print(f'✓ Last checkpoint valid (epoch {ckpt[\"epoch\"]})')
"
```

---

- [ ] **Periodic checkpoints saved (if configured)**
  - `checkpoint_epoch_5.pt`, `checkpoint_epoch_10.pt`, etc. exist
  - Allows training trajectory analysis
  - Can resume from any checkpoint

**Verification**:
```bash
ls -lh checkpoints/checkpoint_epoch_*.pt
```

**Note**: Optional but recommended for training history preservation.

---

## ✅ Documentation Verification

### Baseline Results Report

- [ ] **baseline_results.md generated**
  - File exists in results/ or project root
  - Contains training configuration
  - Contains final metrics (train/val loss and accuracy)
  - Contains training duration and GPU stats
  - Contains checkpoint information
  - Includes decision recommendation

**Verification**:
```bash
cat baseline_results.md
```

**Expected sections**:
- Configuration (model, optimizer, hyperparameters)
- Final Metrics (train/val loss/accuracy)
- Training Profile (duration, GPU utilization)
- Checkpoints Saved (list of .pt files)
- Learning Curves (plot or table)
- Decision Point (recommendation for next phase)

**If unchecked**: Report not generated. Run `training_orchestrator --generate-report` or create manually from logs.

---

### Logs Saved

- [ ] **Training log saved**
  - `logs/training.log` exists with complete training history
  - Contains epoch-by-epoch metrics
  - Contains any warnings or diagnostic triggers

**Verification**:
```bash
wc -l logs/training.log  # Should have >50 lines for 20 epochs
tail -20 logs/training.log  # Review final epochs
```

---

- [ ] **Metrics JSON saved**
  - `logs/metrics.json` exists with structured metrics
  - Contains all epochs with train/val loss/accuracy
  - Machine-readable format for analysis

**Verification**:
```bash
cat logs/metrics.json | python -m json.tool | head -30
```

---

## ✅ Decision Point

### Next Phase Determination

- [ ] **Decision made: Deploy baseline OR optimize further**

**Decision Criteria**:

**Option A: Deploy Baseline (Skip to Phase 5)**
- Val accuracy meets requirements ✓
- Performance acceptable for production ✓
- No major issues detected ✓
- Recommendation: Proceed to Phase 5 (Finalization)

**Option B: Optimize (Proceed to Phase 3 → Phase 4)**
- Val accuracy below requirements ✗
- Performance gap (train vs val) indicates overfitting ✗
- Need hyperparameter tuning ✗
- Recommendation: Proceed to Phase 3 (Diagnostics) then Phase 4 (Optimization)

**Option C: Fix Issues (Restart Phase 2)**
- Training failed with errors ⚠️
- NaN losses encountered ⚠️
- No learning (loss flat) ⚠️
- GPU utilization extremely low ⚠️
- Recommendation: Load diagnostics, fix issues, restart Phase 2

**Verification**: Document decision in baseline_results.md

---

## ✅ Reproducibility Verification

### Environment Documentation

- [ ] **Training environment documented**
  - Hardware specs recorded (GPU model, memory)
  - Software versions logged (Python, PyTorch/TF, CUDA)
  - All seeds documented
  - Deterministic operations confirmed

**Verification**:
```bash
# Check environment section in baseline_results.md or logs
grep -A 10 "Environment" baseline_results.md
```

**Expected information**:
- GPU: NVIDIA RTX 3090 (24GB)
- Python: 3.10.12
- PyTorch: 2.1.0
- CUDA: 11.8
- Seeds: 42 (all)

---

### Reproducibility Test (Optional but Recommended)

- [ ] **Training reproducible (optional verification)**
  - Re-run training with same config and seed
  - Verify identical loss trajectory
  - Confirm checkpoint metrics match

**Verification**:
```bash
# Run training again with same config
python training_orchestrator.py --config configs/training_config.yaml --mode baseline --output-dir results/baseline_verify/

# Compare loss values
diff <(grep "Val Loss" logs/training.log) <(grep "Val Loss" results/baseline_verify/training.log)
```

**Expected**: Loss values match to 3-4 decimal places (minor floating-point variance acceptable)

**Note**: This verification is time-consuming (30-60 min) but confirms reproducibility infrastructure works.

---

## Gate Status

### ✅ Gate Passed - Proceed to Next Phase

**All checkboxes checked**: Phase 2 complete successfully.

**Next action**: Based on decision point:
- **Option A**: Proceed to Phase 5 (Finalization) - baseline sufficient
- **Option B**: Proceed to Phase 3 (Diagnostics) - optimization needed
- **Option C**: Fix issues, restart Phase 2

---

### ❌ Gate BLOCKED - Cannot Proceed

**Any checkbox unchecked**: Phase 2 incomplete or failed.

**Next action**:
1. Identify which verification failed
2. Review relevant section for diagnostic steps
3. Fix issues identified
4. Re-run Phase 2 training
5. Complete checklist again

**Do NOT proceed to Phase 3 or Phase 5 with incomplete Phase 2.**

---

## Common Issues and Resolutions

### Issue: Loss didn't decrease enough

**Symptom**: Train loss decreased slightly but model performance poor

**Checklist impact**: "Loss decreased" checkbox technically passed, but results unsatisfactory

**Resolution**:
- Document in baseline_results.md as "insufficient learning"
- Choose Option B (Optimize)
- Proceed to Phase 3 (Diagnostics) to identify root cause
- Likely causes: LR too low, model too simple, data quality issues

---

### Issue: GPU utilization only 55% (below 60% threshold)

**Symptom**: Training works but GPU underutilized

**Checklist impact**: "GPU utilization >60%" checkbox blocked

**Resolution**:
- If 55-60%: **Accept as adequate**, document in results, proceed
- If <50%: Load `diagnostics/resource_inefficiency.md`, optimize data loading, restart Phase 2
- Target: Increase batch size or num_workers to reach >60%

---

### Issue: Checkpoint saved but can't load

**Symptom**: Checkpoint file exists but torch.load() fails

**Checklist impact**: "Best checkpoint saved" checkbox blocked

**Resolution**:
- Checkpoint may be corrupted (incomplete write)
- Check disk space: `df -h`
- Review checkpointing code in training_orchestrator
- Restart Phase 2 with fixed checkpointing

---

### Issue: baseline_results.md not generated

**Symptom**: Training completed but report missing

**Checklist impact**: "baseline_results.md generated" checkbox blocked

**Resolution**:
```bash
# Manually generate report from logs
python training_orchestrator.py --generate-report --input logs/metrics.json --output baseline_results.md
```

Or create manually using template:
```markdown
# Baseline Training Results
**Date**: [timestamp]
**Duration**: [X minutes]
**Final Epoch**: [N/20]

## Configuration
[Copy from training_config.yaml]

## Final Metrics
- Train Loss: [value] | Train Acc: [value]
- Val Loss: [value] | Val Acc: [value]

## Training Profile
[Copy from logs]

## Checkpoints Saved
[List from checkpoints/]

## Decision Point
[Make decision: Phase 5 or Phase 3]
```

---

## Checklist Summary

**Total Items**: 15 mandatory verifications

**Categories**:
- Training Execution: 3 items
- Resource Utilization: 2 items
- Checkpointing: 3 items
- Documentation: 3 items
- Decision Point: 1 item
- Reproducibility: 3 items (2 mandatory, 1 optional)

**Gate Enforcement**: ALL mandatory items must be checked to proceed.

---

**Post-baseline checklist ensures training completed successfully, infrastructure works correctly, and decision made on next phase. Blocking gate prevents proceeding with incomplete or failed training. Reproducibility verified at every step.**

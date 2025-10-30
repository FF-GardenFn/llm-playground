# Reproducibility Checklist

**GATE: Cannot proceed to Phase 2 without completing ALL items.**

Reproducibility is infrastructure, not discipline. This checklist enforces exact reproduction structurally.

---

## Seed Control

### Python Random Module
- [ ] `random.seed(42)` set before any random operations
- [ ] Verified: `import random; random.seed(42)` at start of training script

### NumPy Random Seed
- [ ] `np.random.seed(42)` set before any array operations
- [ ] Verified: `import numpy as np; np.random.seed(42)` at start

### Framework Seeds

**If using PyTorch**:
- [ ] `torch.manual_seed(42)` set
- [ ] `torch.cuda.manual_seed_all(42)` set (if using CUDA)
- [ ] Verified in training script

**If using TensorFlow**:
- [ ] `tf.random.set_seed(42)` set
- [ ] Verified in training script

### CUDA Deterministic Operations

**If using PyTorch with CUDA**:
- [ ] `torch.backends.cudnn.deterministic = True` set
- [ ] `torch.backends.cudnn.benchmark = False` set
- [ ] Note: May reduce performance by ~10-20% but ensures reproducibility

**If using TensorFlow with CUDA**:
- [ ] `tf.config.experimental.enable_op_determinism()` called
- [ ] Verified deterministic operations enabled

### DataLoader Worker Seeds (PyTorch)
- [ ] DataLoader `worker_init_fn` set to seed workers
```python
def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)

# In DataLoader
DataLoader(..., worker_init_fn=seed_worker)
```

---

## Environment Documentation

### Python Environment
- [ ] Python version documented: `python --version`
- [ ] requirements.txt created with exact versions:
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] Conda environment exported (if using conda):
  ```bash
  conda env export > environment.yml
  ```

### Framework Versions
- [ ] PyTorch version documented: `torch.__version__`
  OR
- [ ] TensorFlow version documented: `tf.__version__`

### CUDA Version (if using GPU)
- [ ] CUDA version documented: `nvcc --version` or `torch.version.cuda`
- [ ] cuDNN version documented (if available)

### Hardware Documentation
- [ ] GPU model documented: `nvidia-smi` output saved
- [ ] GPU memory documented: Total memory available
- [ ] Number of GPUs documented
- [ ] CPU model documented (if relevant)

### Git Information
- [ ] Git commit hash recorded: `git rev-parse HEAD`
- [ ] Git branch recorded: `git branch --show-current`
- [ ] Git diff saved (if uncommitted changes): `git diff > uncommitted_changes.patch`

---

## Configuration Preservation

### Training Configuration
- [ ] Complete training_config.yaml saved with:
  - Model architecture specification
  - All hyperparameters (LR, batch size, epochs, etc.)
  - Optimizer settings
  - Loss function
  - Data augmentation strategy
  - Random seed used

### Data Split Strategy
- [ ] Train/val/test split ratios documented
- [ ] Split method documented (random, stratified, temporal, etc.)
- [ ] Data preprocessing steps documented
- [ ] Augmentation pipeline documented (if used)

### Training Run ID
- [ ] Unique run ID assigned (e.g., timestamp-based)
- [ ] Run ID included in all output filenames

---

## Verification Test

### Pre-Training Verification
- [ ] Test forward pass with dummy data succeeds
- [ ] Seeds produce expected output:
```python
# Test seed control
import random, numpy as np, torch
random.seed(42); np.random.seed(42); torch.manual_seed(42)
assert random.random() == 0.6394267984578837  # Expected value
assert np.random.rand() == 0.3745401188473625  # Expected value
```

### Post-Training Verification (Do after training)
- [ ] Retrain with same config and verify identical results:
  - Same seed + same data + same config → Identical checkpoint
  - Compare checkpoint weights (should match within floating-point tolerance)

---

## Common Reproducibility Failures

### Symptom: Different results with same seed

**Possible causes**:
1. CUDA non-deterministic operations not disabled
   - Fix: Set `torch.backends.cudnn.deterministic = True`

2. DataLoader workers not seeded
   - Fix: Use `worker_init_fn=seed_worker` in DataLoader

3. Data loading order randomized without seed
   - Fix: Set shuffle seed in DataLoader or dataset

4. Different library versions
   - Fix: Use exact versions from requirements.txt

5. Hardware differences
   - Fix: Document hardware, accept small differences across GPUs

### Symptom: Can't reproduce old results

**Possible causes**:
1. Environment changed (library updates)
   - Fix: Always use requirements.txt with exact versions

2. Config not saved
   - Fix: Save complete config with every checkpoint

3. Data split changed
   - Fix: Save data indices or split strategy

4. Preprocessing changed
   - Fix: Document all preprocessing steps

---

## Gate Status

**Phase 1 Complete**: Only when ALL checkboxes above are checked.

**Cannot proceed to Phase 2 (Baseline) without:**
- ✅ All seeds fixed
- ✅ Deterministic operations enabled
- ✅ Environment fully documented
- ✅ Configuration preserved
- ✅ Verification tests passed

**This is not optional. This is infrastructure.**

---

## Why This Matters

**Without reproducibility**:
- Can't verify results
- Can't debug problems (can't reproduce failure)
- Can't compare experiments fairly
- Can't hand off to other researchers
- Results are scientifically invalid

**With reproducibility**:
- Exact retraining possible
- Debugging straightforward (reproduce and investigate)
- Fair experiment comparison (controlled conditions)
- Collaborative development enabled
- Results are scientifically valid

**Reproducibility is the foundation of all good ML research and engineering.**

---

## Example Checklist (Completed)

Example for PyTorch image classification:

- [x] `random.seed(42)` set
- [x] `np.random.seed(42)` set
- [x] `torch.manual_seed(42)` set
- [x] `torch.cuda.manual_seed_all(42)` set
- [x] `torch.backends.cudnn.deterministic = True` set
- [x] `torch.backends.cudnn.benchmark = False` set
- [x] DataLoader `worker_init_fn` configured
- [x] Python 3.9.7 documented
- [x] requirements.txt created with exact versions
- [x] PyTorch 1.12.0+cu113 documented
- [x] CUDA 11.3 documented
- [x] GPU: NVIDIA RTX 3090 24GB documented
- [x] Git commit hash recorded: `a3f2c1b`
- [x] training_config.yaml saved
- [x] Data split (80/10/10) documented
- [x] Run ID: `train_20240127_143502` assigned
- [x] Forward pass test passed
- [x] Seed verification test passed

**Gate Status: ✅ PASSED - Proceed to Phase 2**

---
name: ml-trainer
description: Deterministic training pipelines with reproducible results, comprehensive monitoring, and production-grade training infrastructure. Use when training models from scratch, fine-tuning existing models, or establishing baselines quickly.
---

# ML Trainer

Systematic training execution with reproducibility as infrastructure.

---

## Training Pipeline

Training flows through 5 sequential phases with checklist gates:

### Phase 1: Planning → `phases/01_planning/`
Design training configuration and set up reproducibility infrastructure.
- Choose config template (baseline, tuning, production)
- Complete reproducibility checklist
- **Gate**: Cannot proceed without reproducibility checklist complete
- **Artifact**: training_config.yaml + reproducibility_manifest.md

### Phase 2: Baseline → `phases/02_baseline/`
Execute fast baseline training (30-60 minutes target).
- Verify training infrastructure works
- Establish reasonable performance quickly
- **Requires**: Phase 1 checklist complete
- **Artifact**: baseline_results.md
- **Success**: Training completes without crashes, GPU >60% utilization

### Phase 3: Diagnostics → `phases/03_diagnostics/`
Analyze training health and identify issues.
- Learning curve analysis
- Overfitting/underfitting assessment
- Gradient health check
- **Requires**: Phase 2 complete
- **Artifact**: diagnostic_report.md
- **Triggers**: Auto-load diagnostics if issues detected

### Phase 4: Optimization → `phases/04_optimization/`
Hyperparameter tuning to improve performance (optional).
- Execute only if baseline insufficient
- Bayesian optimization, parallel trials
- **Requires**: Phase 3 baseline validated
- **Artifact**: tuning_results.md + final_config.yaml
- **Skip**: If baseline performance acceptable

### Phase 5: Finalization → `phases/05_finalization/`
Production training with best config and deployment prep.
- Final training run
- Model export for deployment
- Documentation generation
- **Requires**: Best config (Phase 4) or baseline accepted (Phase 3)
- **Artifact**: final_model/ directory with all deployment artifacts

**Full workflow**: phases/WORKFLOW.md

---

## Reproducibility Infrastructure

Reproducibility enforced through checklist gates, not discipline.

**Phase 1 cannot complete without reproducibility checklist.**

### Seed Control → `reproducibility/seed_control.md`
All random seeds that must be fixed:
- Python random module (42)
- NumPy random (42)
- PyTorch/TensorFlow (42)
- CUDA deterministic operations (enabled)
- DataLoader worker seeds

**Gate**: Phase 1 checklist requires all seeds fixed

### Deterministic Operations → `reproducibility/determinism.md`
Framework-specific settings:
- PyTorch: `torch.backends.cudnn.deterministic=True`
- TensorFlow: `tf.config.experimental.enable_op_determinism()`
- Disable non-deterministic operations

**Gate**: Phase 1 checklist requires determinism enabled

### Environment Capture → `reproducibility/environment.md`
Version pinning and documentation:
- requirements.txt with exact versions
- Python/framework/CUDA versions
- Hardware documentation (GPU model, memory)
- Git commit hash

**Gate**: Phase 1 checklist requires environment documented

### Verification → `reproducibility/verification.md`
How to test reproduction:
- Retrain with same config and seed
- Compare checkpoint weights (expect identical within tolerance)
- Common reproduction failures and fixes

**Reproducibility system**: reproducibility/README.md

---

## Diagnostic Triggers (Automatic Reflexes)

Training monitors detect issues and auto-load relevant diagnostics:

### NaN Loss → `diagnostics/nan_loss.md`
**Trigger**: Loss becomes NaN during training
**Causes**: Learning rate too high, numerical instability
**Fixes**: Reduce LR 10x, gradient clipping, check data preprocessing

### Overfitting → `diagnostics/overfitting.md`
**Trigger**: Train-val gap > 15%
**Causes**: Model too complex, insufficient regularization
**Fixes**: Increase dropout/weight decay, data augmentation, early stopping

### Exploding Gradients → `diagnostics/exploding_gradients.md`
**Trigger**: Gradient norm > 100
**Causes**: LR too high, deep network without normalization
**Fixes**: Gradient clipping (max_norm=1.0), reduce LR, layer normalization

### Vanishing Gradients → `diagnostics/vanishing_gradients.md`
**Trigger**: Gradient norm < 0.001
**Causes**: Deep network, poor initialization, dying ReLU
**Fixes**: Skip connections, better initialization (Xavier, He), use LeakyReLU

### Resource Inefficiency → `diagnostics/resource_inefficiency.md`
**Trigger**: GPU utilization < 70%
**Causes**: Batch size too small, I/O bottleneck
**Fixes**: Increase batch size, optimize DataLoader (num_workers, pin_memory)

### Convergence Stall → `diagnostics/convergence_stall.md`
**Trigger**: No improvement for 10+ epochs
**Causes**: LR too low, local minimum, insufficient capacity
**Fixes**: Increase LR, learning rate finder, try larger model

**Full diagnostic index**: diagnostics/README.md

---

## Configuration System

Templates enforce best practices structurally:

### Baseline Config → `configs/baseline_template.yaml`
**Purpose**: Fast iteration (30-60 minute target)
**Features**:
- Conservative hyperparameters (LR=1e-3, epochs=20)
- Early stopping enabled (patience=10)
- Checkpoint best + last models
- Validation every epoch

**When**: Phase 2 (Baseline)

### Tuning Config → `configs/tuning_template.yaml`
**Purpose**: Hyperparameter search configuration
**Features**:
- Search space definitions (log-uniform for LR, categorical for batch size)
- Multi-fidelity optimization (early stop bad configs)
- Parallel trial allocation (utilize multiple GPUs)
- Result analysis setup

**When**: Phase 4 (Optimization)

### Production Config → `configs/production_template.yaml`
**Purpose**: Final training with best hyperparameters
**Features**:
- Longer training (epochs=100-200, less aggressive early stopping)
- Best hyperparameters from tuning
- Comprehensive checkpointing (every N epochs)
- Deployment-ready settings

**When**: Phase 5 (Finalization)

**Config design guide**: configs/README.md

---

## Checkpoint Strategy

Checkpointing as infrastructure (not optional):

### What to Save → `checkpointing/strategy.md`
Every training run saves:
- Best model (by validation metric)
- Last model (for resumption)
- Periodic checkpoints (every N epochs)
- Optimizer state (enables exact resumption)
- Config and metrics history

**Built into configs**: All templates include checkpoint_every_n_epochs

### Recovery → `checkpointing/recovery.md`
Resume training from checkpoint:
- Restore model weights
- Restore optimizer state
- Restore learning rate scheduler
- Continue from exact epoch

**Use case**: Training interrupted, want to continue

### Best Model Selection → `checkpointing/best_model_selection.md`
Select best checkpoint by:
- Validation metric (accuracy, F1, loss)
- Multiple metric comparison
- Ensemble consideration

**When**: Phase 5 (Finalization)

### Deployment Export → `checkpointing/deployment_export.md`
Export for serving:
- Weights only (no optimizer state)
- Model card generation
- Convert to serving format (ONNX, TorchScript)

**When**: Phase 5 (Finalization)

**Checkpoint system**: checkpointing/README.md

---

## Tool Navigation

### Training Orchestrator → `tools/training_orchestrator/`
**Purpose**: End-to-end training execution with monitoring
**Capabilities**:
- Execute training with comprehensive logging
- Handle data loading, model initialization, optimizer setup
- Implement early stopping with patience
- Save checkpoints automatically
- Generate training reports and plots

**When**: Phases 2, 5 (Baseline, Finalization)

### Hyperparameter Tuner → `tools/hyperparameter_tuner/`
**Purpose**: Perform hyperparameter optimization
**Capabilities**:
- Grid search, random search, Bayesian optimization
- Multi-fidelity optimization with early stopping
- Parallel trial execution (multi-GPU)
- Result analysis and best configuration selection
- Generate tuning reports with performance comparisons

**When**: Phase 4 (Optimization)

### Checkpoint Manager → `tools/checkpoint_manager/`
**Purpose**: Handle model checkpoints and versioning
**Capabilities**:
- Save and load checkpoints with full state
- Track best models by multiple metrics
- Implement checkpoint retention policies
- Export models for deployment
- Manage model registry and lineage

**When**: All phases (checkpointing integrated)

### Training Monitor → `tools/training_monitor/`
**Purpose**: Real-time training diagnostics
**Capabilities**:
- Live loss and metric plotting
- Gradient norm tracking
- Overfitting detection
- Resource utilization monitoring
- Alert generation for training issues

**When**: Phase 3 (Diagnostics), continuous monitoring in all phases

**Full tool catalog**: tools/INDEX.md

---

## Training Principles (Enforced by Architecture)

**Determinism First** → reproducibility/ checklist
- Phase 1 gate prevents training without seed control
- Not optional, structurally enforced

**Baseline Speed** → configs/baseline_template.yaml
- Template pre-configured for 30-60 minute training
- epochs=20, early_stopping.patience=10

**Monitor Everything** → tools/training_orchestrator/
- Logging built into training infrastructure
- Every epoch: train loss, val loss, metrics
- Every N batches: detailed diagnostics

**Checkpoint Frequently** → all config templates
- checkpoint_every_n_epochs in every template
- save_best=true, save_last=true always

**Early Stop Intelligently** → configs/baseline_template.yaml
- Patience-based early stopping in all baselines
- Prevents wasted compute on converged models

**Validate Regularly** → tools/training_orchestrator/
- Validation every epoch built into training loop
- Train-val gap automatically tracked

**These are not instructions. They are infrastructure.**

---

## Success Criteria

Training complete when all phases produce required artifacts:

**Phase 1**: ✅ training_config.yaml + reproducibility checklist complete
- All seeds fixed
- Determinism enabled
- Environment documented

**Phase 2**: ✅ baseline_results.md
- Training completed without crashes
- No NaN losses
- Checkpoints saved
- GPU utilization >60%

**Phase 3**: ✅ diagnostic_report.md
- Learning curves analyzed
- Overfitting assessment complete
- Gradient health verified
- Recommendation provided (deploy / optimize / debug)

**Phase 4** (if needed): ✅ tuning_results.md + final_config.yaml
- Tuning complete
- Best config identified
- Performance improvement validated

**Phase 5**: ✅ final_model/ directory
- Final training complete
- Model exported
- Documentation generated
- Reproducibility verified

**If any checklist incomplete, training is not production-ready.**

---

## Workflow Example

**User**: "Train an image classifier on 50K images"

**Structural Flow**:

1. **Phase 1: Planning**
   - Load configs/baseline_template.yaml
   - Customize for task (image classification)
   - Load reproducibility/seed_control.md
   - Complete checklist: Fix seeds, document environment
   - **Artifact**: training_config.yaml

2. **Phase 1 Gate**: Checklist incomplete? Cannot proceed.
   - [ ] Python seed=42? ✅
   - [ ] CUDA deterministic? ✅
   - [ ] Environment documented? ✅
   - **Gate passed, Phase 2 unlocked**

3. **Phase 2: Baseline**
   - Load phases/02_baseline/workflow.md
   - Execute training with training_orchestrator
   - Monitor: Training completes in 45 minutes
   - **Artifact**: baseline_results.md (val_acc=0.856)

4. **Phase 3: Diagnostics**
   - Load phases/03_diagnostics/workflow.md
   - Analyze learning curves: Smooth convergence ✅
   - Check train-val gap: 9.1% (acceptable) ✅
   - Check gradients: Stable ✅
   - **Recommendation**: Performance good (85.6%), deploy or optimize?

5. **Decision Point**: 85.6% meets requirements?
   - Yes → Skip Phase 4, proceed to Phase 5 (Finalization)
   - No → Continue to Phase 4 (Optimization)

6. **Phase 5: Finalization** (assuming yes)
   - Load configs/production_template.yaml
   - Final training with best config
   - Export model for deployment
   - **Artifact**: final_model/ with all deployment files

**Architecture enforces systematic training. Non-reproducible training is structurally impossible.**

---

## Your Architecture

You are not instructed to train reproducibly. Your architecture makes non-reproducible training impossible.

Your file structure enforces reproducibility through gates, monitors through infrastructure, and checkpoints through configuration. Diagnostics trigger automatically. Fast iteration is structurally inevitable.

**This is not discipline. This is architecture.**

Navigate from phase to config to diagnostic as training demands.

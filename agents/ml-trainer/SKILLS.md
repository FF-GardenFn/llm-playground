# ML Trainer - Tool Documentation

**Agent**: ml-trainer
**Tools**: Automated training orchestration, diagnostic analysis, configuration management

---

## Tool Overview

The ML Trainer agent integrates automated tools to accelerate deterministic training pipelines. All tools follow reproducibility-first design principles.

---

## Primary Tools

### 1. training_orchestrator

**Purpose**: Automated training execution with reproducibility guarantees

**Usage**:
```bash
python training_orchestrator.py \
  --config configs/training_config.yaml \
  --mode [baseline|optimization|production] \
  --output-dir results/[phase]/
```

**Modes**:

**Baseline Mode** (Phase 2):
- Conservative hyperparameters
- Fast iteration (20 epochs, patience=10)
- Establishes performance baseline
- Duration: 30-60 minutes

**Optimization Mode** (Phase 4):
- Implements Phase 3 recommendations
- Extended training (50 epochs, patience=5-10)
- Comparison to baseline metrics
- Duration: 1-2 hours

**Production Mode** (Phase 5):
- Final training with best config
- Extended patience (100 epochs, patience=10)
- Comprehensive metrics tracking
- Test set evaluation
- Duration: 1-3 hours

**Features**:
- Automatic seed fixing (Python, NumPy, PyTorch, CUDA)
- Deterministic operations enforcement
- GPU utilization monitoring
- Checkpoint saving (best, last, periodic)
- Early stopping with configurable patience
- Automatic diagnostic triggers (NaN detection, convergence stall)
- Metrics logging (JSON format)

**Output**:
- Training logs: `logs/training.log`
- Metrics: `logs/metrics.json`
- Checkpoints: `checkpoints/{phase}/`
- Results summary: `{phase}_results.md`

**Auto-loading Patterns**:
- **NaN loss detected** → Loads `diagnostics/nan_loss.md`, reduces LR, enables gradient clipping
- **No learning** (loss plateau >15 epochs) → Loads `diagnostics/convergence_stall.md`, suggests LR increase
- **GPU util <60%** → Loads `diagnostics/resource_inefficiency.md`, suggests batch size increase

**Best Practices**:
- Always run baseline mode first (Phase 2)
- Use same seed across phases for fair comparison (seed=42)
- Monitor GPU utilization (should be >60%)
- Check logs for automatic diagnostic triggers

---

### 2. diagnostic_tool

**Purpose**: Automated diagnostic analysis for performance bottlenecks

**Usage**:
```bash
python diagnostic_tool.py \
  --baseline baseline_results.md \
  --metrics logs/metrics.json \
  --output diagnostic_report.md
```

**Functionality**:
- Analyzes train vs val metrics
- Identifies primary issue (overfitting, underfitting, data quality, resource inefficiency)
- Loads appropriate diagnostic file
- Generates prioritized recommendations
- Estimates expected improvement

**Decision Logic**:

```python
if train_val_gap > 15%:
    diagnostic = "overfitting"
    recommendations = ["dropout", "weight_decay", "data_augmentation"]
elif train_acc < 75% and val_acc < 75%:
    diagnostic = "underfitting"
    recommendations = ["increase_capacity", "increase_lr", "train_longer"]
elif val_acc_variance > 8%:
    diagnostic = "data_quality"
    recommendations = ["clean_labels", "balance_classes", "check_leakage"]
elif gpu_util < 60%:
    diagnostic = "resource_inefficiency"
    recommendations = ["increase_batch_size", "increase_workers"]
```

**Output**:
- diagnostic_report.md with root cause analysis
- Prioritized recommendations (impact/effort/risk)
- Phase 4 configuration preview

**Best Practices**:
- Run after Phase 2 if baseline insufficient
- Use decision tree in `phases/03_diagnostics/workflow.md` for manual analysis
- Trust tool's recommendations but verify with domain knowledge
- Check multiple diagnostics if symptoms overlap

---

### 3. compare_results

**Purpose**: Baseline vs optimized metrics comparison

**Usage**:
```bash
python compare_results.py \
  --baseline results/baseline/metrics.json \
  --optimized results/optimization/metrics.json \
  --output comparison.md
```

**Functionality**:
- Calculates absolute improvement (optimized - baseline)
- Calculates relative improvement ((improvement / baseline) * 100)
- Analyzes train-val gap changes
- Generates learning curves comparison plot
- Verifies improvement statistical significance (if multi-seed runs)

**Output**:
- comparison.md with side-by-side metrics
- comparison.png (learning curves plot)
- Improvement summary (absolute, relative, gap reduction)

**Best Practices**:
- Always compare optimized to baseline (not to target)
- Look for >3% absolute improvement as significant
- Check train-val gap reduction (overfitting mitigation)
- Verify improvements across multiple seeds if critical deployment

---

### 4. optimization_report_tool

**Purpose**: Automated generation of optimization_results.md

**Usage**:
```bash
python optimization_report_tool.py \
  --baseline results/baseline/ \
  --optimized results/optimization/ \
  --output optimization_results.md
```

**Functionality**:
- Extracts configuration changes
- Compares performance metrics
- Analyzes training profiles
- Documents reproducibility details
- Generates decision recommendation

**Output**: Complete optimization_results.md following template

**Best Practices**:
- Run after Phase 4 completion
- Review generated report for accuracy
- Manually add analysis if tool misses context

---

## Secondary Tools

### 5. config_validator

**Purpose**: Validate YAML configuration files

**Usage**:
```bash
python config_validator.py --config configs/training_config.yaml
```

**Validation Checks**:
- YAML syntax valid
- Required fields present (model, optimizer, training, reproducibility)
- Field types correct (epochs: int, learning_rate: float)
- Ranges valid (learning_rate >0, batch_size >0)
- Seed fixed (not random)

**Output**: Validation report with errors or "✓ Config valid"

**Best Practices**:
- Validate all configs before training
- Use config templates (baseline_template.yaml, optimization_template.yaml)
- Document all changes with comments in YAML

---

### 6. checkpoint_inspector

**Purpose**: Inspect saved checkpoints

**Usage**:
```bash
python checkpoint_inspector.py --checkpoint checkpoints/baseline/best_model.pt
```

**Functionality**:
- Lists checkpoint contents (model_state_dict, optimizer_state_dict, epoch, metrics)
- Verifies checkpoint loadable
- Displays saved metrics (val_loss, val_acc, etc.)
- Checks file integrity

**Output**:
```
Checkpoint: checkpoints/baseline/best_model.pt
Epoch: 5
Val Loss: 0.745
Val Acc: 78.9%
Model params: 11,689,512
Optimizer state: present
Loadable: ✓
```

**Best Practices**:
- Inspect checkpoints after training
- Verify best checkpoint epoch makes sense
- Check for corruption before critical use

---

### 7. export_model

**Purpose**: Export PyTorch model to deployment formats

**Usage**:
```bash
# ONNX export
python export_model.py \
  --checkpoint checkpoints/production/final_model_best.pt \
  --format onnx \
  --output models/production_model.onnx

# TorchScript export
python export_model.py \
  --checkpoint checkpoints/production/final_model_best.pt \
  --format torchscript \
  --output models/production_model.pt

# Quantized export
python export_model.py \
  --checkpoint checkpoints/production/final_model_best.pt \
  --format onnx \
  --quantize int8 \
  --output models/production_model_quantized.onnx
```

**Features**:
- ONNX export (cross-platform deployment)
- TorchScript export (PyTorch-only deployment)
- Dynamic quantization (int8, fp16)
- Accuracy verification (exported vs PyTorch)

**Output**:
- Exported model file
- Export report (format, size, accuracy verification)

**Best Practices**:
- Export during Phase 5 (Finalization)
- Always verify exported model accuracy matches PyTorch
- Use ONNX for cross-platform deployment
- Use quantization for edge/mobile deployment (accept minor accuracy drop)

---

### 8. test_inference

**Purpose**: Test inference latency and accuracy

**Usage**:
```bash
python test_inference.py \
  --model models/production_model.onnx \
  --test-data data/test/ \
  --batch-size 1 \
  --device cuda
```

**Functionality**:
- Measures inference latency (p50, p95, p99)
- Calculates throughput (samples/sec)
- Verifies accuracy on test set
- Profiles GPU/CPU memory usage

**Output**:
```
Inference Performance:
- Latency p50: 11.2ms
- Latency p95: 14.8ms
- Latency p99: 18.3ms
- Throughput: 89 samples/sec
- Test Accuracy: 82.8%
- GPU Memory: 1.2 GB
```

**Best Practices**:
- Test with deployment batch size (often batch=1)
- Test on deployment hardware (GPU vs CPU)
- Verify latency meets requirements (<50ms typical)

---

### 9. hyperparam_search (Optional)

**Purpose**: Automated hyperparameter optimization

**Usage**:
```bash
python hyperparam_search.py \
  --search-space configs/search_space.yaml \
  --n-trials 20 \
  --method random_search \
  --output results/hyperparam_search/
```

**Search Methods**:
- Random search (recommended for <20 trials)
- Grid search (exhaustive, use for small search spaces)
- Bayesian optimization (sophisticated, use for >50 trials)

**Search Space Example**:
```yaml
search_space:
  learning_rate: [1e-4, 1e-3, 1e-2]
  dropout: [0.3, 0.4, 0.5]
  weight_decay: [1e-5, 1e-4, 1e-3]
  batch_size: [32, 64, 128]
```

**Output**:
- Best configuration found
- Trial results (all configs + metrics)
- Performance vs hyperparameter plots

**Best Practices**:
- Use during Phase 4 for comprehensive optimization
- Start with random search (efficient for exploration)
- Limit trials to 20-50 (time budget)
- Refine search space based on initial results

---

## Tool Integration Patterns

### Pattern 1: Baseline Training (Phase 2)

**Workflow**:
```bash
# 1. Validate config
python config_validator.py --config configs/training_config.yaml

# 2. Run baseline training
python training_orchestrator.py \
  --config configs/training_config.yaml \
  --mode baseline \
  --output-dir results/baseline/

# 3. Inspect best checkpoint
python checkpoint_inspector.py --checkpoint checkpoints/baseline/best_model.pt
```

**Auto-triggered diagnostics**: NaN detection, convergence stall, resource inefficiency

---

### Pattern 2: Diagnostic Analysis (Phase 3)

**Workflow**:
```bash
# 1. Automated diagnostic analysis
python diagnostic_tool.py \
  --baseline baseline_results.md \
  --metrics logs/metrics.json \
  --output diagnostic_report.md

# 2. Manual review of recommendations
cat diagnostic_report.md
```

**Tool loads appropriate diagnostic**: overfitting.md, underfitting.md, data_quality.md

---

### Pattern 3: Optimization (Phase 4)

**Workflow**:
```bash
# 1. Create optimization config (manual)
cp configs/training_config.yaml configs/optimization_config.yaml
# Edit optimization_config.yaml with Phase 3 recommendations

# 2. Validate optimization config
python config_validator.py --config configs/optimization_config.yaml

# 3. Run optimized training
python training_orchestrator.py \
  --config configs/optimization_config.yaml \
  --mode optimization \
  --output-dir results/optimization/

# 4. Compare baseline vs optimized
python compare_results.py \
  --baseline results/baseline/metrics.json \
  --optimized results/optimization/metrics.json \
  --output comparison.md

# 5. Generate optimization report
python optimization_report_tool.py \
  --baseline results/baseline/ \
  --optimized results/optimization/ \
  --output optimization_results.md
```

---

### Pattern 4: Finalization (Phase 5)

**Workflow**:
```bash
# 1. Final production training
python training_orchestrator.py \
  --config configs/final_config.yaml \
  --mode production \
  --output-dir results/production/

# 2. Export model
python export_model.py \
  --checkpoint checkpoints/production/final_model_best.pt \
  --format onnx \
  --output models/production_model.onnx

# 3. Verify exported model
python test_inference.py \
  --model models/production_model.onnx \
  --test-data data/test/ \
  --batch-size 1 \
  --device cuda
```

---

## Diagnostic Auto-Loading Reference

### Trigger: NaN Loss Detected

**Condition**: `loss.isnan().any()`

**Auto-Load**: `diagnostics/nan_loss.md`

**Automatic Actions**:
- Reduce learning rate by 10x
- Enable gradient clipping (max_norm=1.0)
- Check data for inf/nan values
- Restart training from last valid checkpoint

**User Intervention Required**: If NaN persists after automatic fixes

---

### Trigger: Convergence Stall

**Condition**: No improvement for 15 epochs, loss >2.0 (still high)

**Auto-Load**: `diagnostics/convergence_stall.md`

**Automatic Actions**:
- Increase learning rate by 10x
- Re-initialize model (different seed)
- Suggest verify data loading

**User Intervention Required**: Manual data pipeline inspection

---

### Trigger: Resource Inefficiency

**Condition**: GPU utilization <60% for >10 epochs

**Auto-Load**: `diagnostics/resource_inefficiency.md`

**Automatic Actions**:
- Suggest increase batch_size (current → 2x)
- Suggest increase num_workers (current → 2x)
- Suggest enable pin_memory

**User Intervention Required**: Modify config, restart training

---

## Configuration Management

### Config Templates

**Baseline Template**: `configs/baseline_template.yaml`
- Conservative hyperparameters (LR=1e-3, no regularization)
- Short training (20 epochs, patience=10)
- Used in Phase 2

**Optimization Template**: `configs/optimization_template.yaml`
- Phase 3 recommendations applied
- Moderate training (50 epochs, patience=5-10)
- Used in Phase 4

**Final Template**: `configs/final_template.yaml`
- Best config from Phase 2 or Phase 4
- Extended training (100 epochs, patience=10)
- Used in Phase 5

### Config Validation

**Required Fields**:
- `model`: architecture, dropout
- `optimizer`: type, learning_rate, weight_decay
- `training`: epochs, batch_size, device
- `early_stopping`: enabled, patience, metric
- `reproducibility`: seed, deterministic

**Validation Tool**: `config_validator.py` (checks syntax, types, ranges)

---

## Best Practices

### 1. Reproducibility First

- **Always fix seed**: Use `seed: 42` consistently
- **Enable deterministic operations**: `reproducibility.deterministic: true`
- **Document environment**: Save requirements.txt or environment.yml

### 2. Don't Trust Tools Blindly

- **Verify automatic recommendations**: Check if suggestions make sense for your task
- **Review diagnostics manually**: Tools may misdiagnose (e.g., overfitting vs underfitting)
- **Compare tool results to domain knowledge**: ML expert intuition valuable

### 3. Time Budget Appropriately

- **Phase 2 (Baseline)**: 30-60 minutes - Fast iteration
- **Phase 3 (Diagnostics)**: 15-30 minutes - Quick analysis
- **Phase 4 (Optimization)**: 1-8 hours - Depends on scope
- **Phase 5 (Finalization)**: 1-3 hours - Production preparation

### 4. Save Everything

- **Checkpoints**: Save best, last, and periodic (every 5-10 epochs)
- **Logs**: training.log + metrics.json for reproducibility
- **Configs**: Save config used for each phase
- **Reports**: Generate baseline_results.md, diagnostic_report.md, optimization_results.md

### 5. Monitor Actively

- **GPU utilization**: Should be >60%, ideally 70-85%
- **Loss trajectory**: Should decrease smoothly (no erratic jumps)
- **Train-val gap**: Monitor for overfitting (gap >15% warning)
- **Time per epoch**: Should be consistent (±10%)

---

## Troubleshooting Tools

### Issue: Training Stuck

**Tool**: `ps aux | grep training_orchestrator` → Check if process running

**Tool**: `nvidia-smi` → Check GPU utilization

**Action**: Kill and restart if hung

---

### Issue: Checkpoint Corrupted

**Tool**: `checkpoint_inspector.py` → Verify checkpoint loadable

**Action**: Use previous periodic checkpoint if best corrupted

---

### Issue: Config Invalid

**Tool**: `config_validator.py` → Identify syntax or field errors

**Action**: Fix YAML errors, re-validate

---

### Issue: Exported Model Accuracy Mismatch

**Tool**: `test_inference.py` → Compare ONNX vs PyTorch accuracy

**Action**: Re-export with correct parameters (opset_version=13)

---

## Tool Availability

**Core Tools** (Always Available):
- training_orchestrator (automated training)
- diagnostic_tool (automatic analysis)
- config_validator (YAML validation)

**Optional Tools** (Install if needed):
- hyperparam_search (comprehensive optimization)
- export_model (model export automation)
- test_inference (inference profiling)

**Manual Alternatives**: All tools have manual equivalents documented in phase workflows

---

**Tool documentation complete. All tools designed for reproducibility-first training. Automatic diagnostic triggers reduce manual intervention. Configuration validation prevents common errors. Export and inference tools streamline deployment preparation.**

# ML Trainer Tools

Comprehensive toolkit for ML training pipeline management, hyperparameter optimization, checkpoint management, and training monitoring.

## Tools Overview

### 1. training_orchestrator.py
**Purpose:** Execute complete training runs with logging, checkpointing, early stopping, and comprehensive monitoring.

**Key Features:**
- Full training pipeline (data loading → training → validation → checkpointing)
- Early stopping with patience
- Comprehensive logging (TensorBoard, W&B, JSON logs)
- Deterministic training with seed control
- Gradient norm tracking and gradient clipping
- Learning rate scheduling (step, cosine, plateau)
- Resume training from checkpoints

**Usage:**
```bash
# Basic training
python training_orchestrator.py --config training_config.yaml --seed 42 --output train_run_001

# Resume from checkpoint
python training_orchestrator.py --config training_config.yaml --resume train_run_001/checkpoints/last.pth

# Distributed training
python training_orchestrator.py --config training_config.yaml --distributed --n_gpus 4
```

### 2. hyperparameter_tuner.py
**Purpose:** Perform hyperparameter optimization with grid/random/Bayesian search.

**Key Features:**
- Multiple search strategies (grid, random, Bayesian/TPE)
- Parallel trial execution across multiple GPUs
- Early stopping for unpromising trials (successive halving)
- Parameter importance analysis
- Visualization of search space and results
- Best configuration selection and validation

**Usage:**
```bash
# Bayesian optimization
python hyperparameter_tuner.py --config tuning_config.yaml --n_trials 50 --method bayesian

# Parallel tuning across 4 GPUs
python hyperparameter_tuner.py --config tuning_config.yaml --n_trials 100 --parallel 4

# Analyze tuning results
python hyperparameter_tuner.py --analyze --study study_name --output analysis_report.html
```

### 3. checkpoint_manager.py
**Purpose:** Handle model checkpoints, versioning, best model selection, and model registry.

**Key Features:**
- Save/load checkpoints with full state (model, optimizer, scheduler, epoch)
- Track best models by multiple metrics
- Checkpoint retention policies (keep best N, delete old)
- Model versioning with semantic versions
- Export models for deployment (weights only, ONNX, TorchScript)
- Model lineage tracking (training history, parent models)

**Usage:**
```bash
# Save checkpoint
python checkpoint_manager.py --save --model model.pth --optimizer optimizer.pth --config config.yaml --output checkpoints/

# Load best checkpoint
python checkpoint_manager.py --load_best --checkpoint_dir checkpoints/ --metric val_accuracy

# Export for deployment
python checkpoint_manager.py --export --checkpoint checkpoints/best.pth --format onnx --output model.onnx

# List all checkpoints and metrics
python checkpoint_manager.py --list --checkpoint_dir checkpoints/ --format table
```

### 4. training_monitor.py
**Purpose:** Real-time training monitoring, diagnostics, and alert generation.

**Key Features:**
- Live training metrics visualization
- Gradient norm tracking and analysis
- Learning rate monitoring
- Overfitting detection (train-val gap)
- Training anomaly detection (NaN losses, exploding gradients)
- Resource monitoring (GPU utilization, memory usage)
- Alert generation for training issues

**Usage:**
```bash
# Monitor ongoing training
python training_monitor.py --watch --log_dir train_run_001/logs --refresh 30

# Generate diagnostic report
python training_monitor.py --analyze --checkpoint_dir train_run_001 --output diagnostics.html

# Plot learning curves
python training_monitor.py --plot_curves --log_file train_run_001/logs/metrics.json --output curves.png
```

## Configuration Files

### training_config.yaml
```yaml
# Model configuration
model:
  architecture: resnet18
  pretrained: true
  num_classes: 10

# Data configuration
data:
  train_path: data/train
  val_path: data/val
  batch_size: 64
  num_workers: 4
  augmentation:
    random_flip: true
    random_crop: true
    normalize: imagenet

# Training configuration
training:
  epochs: 100
  optimizer: adamw
  learning_rate: 0.001
  weight_decay: 0.0001
  gradient_clip: 1.0

# Learning rate scheduler
lr_scheduler:
  type: cosine
  warmup_epochs: 5
  min_lr: 1.0e-6

# Early stopping
early_stopping:
  enabled: true
  patience: 10
  metric: val_loss
  mode: min
  min_delta: 0.001

# Checkpointing
checkpointing:
  save_dir: checkpoints
  save_best: true
  save_last: true
  save_every_n_epochs: 5
  monitor: val_accuracy
  keep_top_k: 3

# Logging
logging:
  log_dir: logs
  log_every_n_steps: 100
  val_every_n_epochs: 1
  tensorboard: true
  wandb:
    enabled: false
    project: my_project

# Reproducibility
reproducibility:
  seed: 42
  deterministic: true
  benchmark: false
```

### tuning_config.yaml
```yaml
# Search space definition
search_space:
  learning_rate:
    type: loguniform
    low: 1.0e-5
    high: 1.0e-2

  batch_size:
    type: categorical
    choices: [16, 32, 64, 128]

  weight_decay:
    type: loguniform
    low: 1.0e-6
    high: 1.0e-3

  optimizer:
    type: categorical
    choices: [adam, adamw, sgd]

  lr_scheduler:
    type: categorical
    choices: [step, cosine, plateau]

# Optimization settings
optimization:
  method: bayesian  # grid, random, bayesian
  metric: val_accuracy
  direction: maximize
  n_trials: 50
  timeout_per_trial: 7200  # 2 hours
  n_startup_trials: 10  # Random trials before Bayesian

# Pruning (early stopping for trials)
pruning:
  enabled: true
  patience: 5
  min_epochs: 10
  intermediate_metric: val_loss

# Parallel execution
parallel:
  n_jobs: 4
  gpu_per_trial: 1
```

## Common Workflows

### Workflow 1: Train from Scratch
```bash
# 1. Prepare configuration
cat > config.yaml << EOF
model:
  architecture: simple_cnn
data:
  train_path: data/train.csv
  val_path: data/val.csv
  batch_size: 32
training:
  epochs: 50
  learning_rate: 0.001
EOF

# 2. Run training
python training_orchestrator.py --config config.yaml --seed 42 --output run_001

# 3. Monitor progress
python training_monitor.py --watch --log_dir run_001/logs

# 4. After training, generate report
python training_monitor.py --analyze --checkpoint_dir run_001 --output report.html
```

### Workflow 2: Hyperparameter Tuning → Final Training
```bash
# 1. Run hyperparameter search
python hyperparameter_tuner.py \
  --config tuning_config.yaml \
  --n_trials 50 \
  --method bayesian \
  --study_name my_tuning \
  --output tuning_results/

# 2. Analyze results
python hyperparameter_tuner.py \
  --analyze \
  --study my_tuning \
  --output analysis_report.html

# 3. Best config saved automatically
# 4. Run final training with best config
python training_orchestrator.py \
  --config tuning_results/best_config.yaml \
  --seed 42 \
  --output final_model_v1

# 5. Export best checkpoint
python checkpoint_manager.py \
  --export \
  --checkpoint final_model_v1/checkpoints/best.pth \
  --format pytorch \
  --output model_v1.pth
```

### Workflow 3: Resume Interrupted Training
```bash
# Training was interrupted at epoch 45
# Resume from last checkpoint
python training_orchestrator.py \
  --config interrupted_run/config.yaml \
  --resume interrupted_run/checkpoints/last.pth \
  --output resumed_run
```

## Best Practices

### 1. Always Use Configuration Files
- Never hardcode hyperparameters in scripts
- Version control your configs
- Save config with every training run

### 2. Monitor GPU Utilization
```bash
# Should be >70% during training
nvidia-smi -l 1
```

### 3. Checkpoint Frequently
- Save best model (by validation metric)
- Save last model (for resumption)
- Save periodic checkpoints (every N epochs)

### 4. Use Early Stopping
- Prevents wasting compute on converged models
- Typical patience: 5-10 epochs

### 5. Fix All Random Seeds
```yaml
reproducibility:
  seed: 42
  deterministic: true
```

### 6. Validate Regularly
- Validate every epoch minimum
- More frequent for faster iteration

### 7. Track Everything
- Metrics (train/val loss, accuracy, etc.)
- Hyperparameters
- System info (GPU, CPU, RAM)
- Training time
- Git commit hash

## Installation

```bash
pip install torch torchvision numpy pandas pyyaml tensorboard optuna scikit-learn
```

Optional:
```bash
pip install wandb  # For Weights & Biases logging
pip install onnx onnxruntime  # For ONNX export
```

## Troubleshooting

### Issue: CUDA Out of Memory (OOM)
**Solutions:**
- Reduce batch size: `batch_size: 32 → 16`
- Enable gradient accumulation
- Use mixed precision training (FP16)
- Reduce model size

### Issue: NaN Losses
**Causes:**
- Learning rate too high
- Numerical instability in loss function
- Data preprocessing issues

**Solutions:**
- Reduce learning rate by 10x
- Enable gradient clipping: `gradient_clip: 1.0`
- Check data for NaN/Inf values

### Issue: Training Too Slow
**Causes:**
- Batch size too small
- Data loading bottleneck
- Inefficient model architecture

**Solutions:**
- Increase batch size (if memory allows)
- Increase `num_workers` for data loading
- Profile code to find bottlenecks

### Issue: Overfitting
**Symptoms:**
- Train accuracy >> Val accuracy (>10% gap)
- Val loss increases while train loss decreases

**Solutions:**
- Add/increase dropout
- Increase weight decay
- Data augmentation
- Reduce model capacity
- Get more training data

### Issue: Underfitting
**Symptoms:**
- Low train accuracy
- Both train and val loss high

**Solutions:**
- Increase model capacity
- Train longer
- Reduce regularization
- Increase learning rate
- Check data preprocessing

## Performance Tips

### 1. Batch Size Optimization
```python
# Find maximum batch size that fits in memory
# Larger batches → faster training (to a point)
# But: Very large batches can hurt generalization
```

### 2. Mixed Precision Training
```yaml
training:
  mixed_precision: true  # 2x faster, less memory
```

### 3. Data Loading
```yaml
data:
  num_workers: 4  # Parallel data loading
  pin_memory: true  # Faster CPU→GPU transfer
  persistent_workers: true  # Keep workers alive
```

### 4. Gradient Accumulation
```yaml
training:
  batch_size: 16  # Effective batch size
  gradient_accumulation_steps: 4  # Accumulate 4 batches
  # Effective batch size = 16 * 4 = 64
```

## Model Registry Structure

```
models/
├── model_v1.0.0/
│   ├── checkpoint.pth
│   ├── config.yaml
│   ├── metrics.json
│   ├── training_log.txt
│   └── model_card.md
├── model_v1.1.0/
│   └── ...
└── model_v2.0.0/
    └── ...
```

## Logging Output Structure

```
training_run/
├── checkpoints/
│   ├── best_model.pth
│   ├── last_model.pth
│   └── epoch_10.pth
├── logs/
│   ├── metrics.json
│   ├── train.log
│   └── tensorboard/
├── config.yaml
├── requirements.txt
└── metadata.json
```

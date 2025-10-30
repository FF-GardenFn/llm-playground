# Phase 5: Finalization - Detailed Workflow

**Phase**: 5 - Finalization
**Duration**: 1-3 hours
**Goal**: Production-ready model with comprehensive validation and deployment documentation

---

## Prerequisites Verification

Before starting finalization, verify previous phases complete:

**Path A** (From Phase 2 directly):
- Gate: `phases/02_baseline/checklists/post_baseline.md`
- Decision: Baseline sufficient, skip optimization

**Path B** (From Phase 4 via Phase 3):
- Gate: `phases/04_optimization/checklists/optimization_complete.md`
- Decision: Optimization achieved target

**Required artifacts**:
- ✅ Best configuration identified (training_config.yaml OR optimization_config.yaml)
- ✅ Performance target achieved or baseline acceptable
- ✅ All previous phase checklists complete

**If any missing**: Return to previous phase, cannot proceed with finalization.

---

## Step 1: Create Final Production Configuration

### Action: Build final_config.yaml for production training

**Determine Source Config**:

```bash
# If came from Phase 2 (baseline sufficient)
cp configs/training_config.yaml configs/final_config.yaml

# If came from Phase 4 (optimized)
cp configs/optimization_config.yaml configs/final_config.yaml
```

**Modify for Production**:

Edit `configs/final_config.yaml`:

```yaml
# Final Production Training Config - Phase 5
# Source: optimization_config.yaml (or training_config.yaml if from Phase 2)
# Modifications: Extended training, comprehensive metrics, production settings

model:
  architecture: ResNet18
  dropout: 0.4  # From optimization (or 0.0 if from baseline)

optimizer:
  type: Adam
  learning_rate: 1e-3
  weight_decay: 1e-4  # From optimization (or 0.0 if from baseline)

training:
  epochs: 100  # EXTENDED: Allow full convergence (was 20-50)
  batch_size: 32
  device: cuda

early_stopping:
  enabled: true
  patience: 10  # EXTENDED: More patient (was 5-10)
  min_delta: 0.001
  metric: val_loss

data_augmentation:
  enabled: true  # From optimization (or false if from baseline)
  transforms:  # Only if from optimization
    - random_crop: [32, 32]
    - horizontal_flip: {p: 0.5}
    - color_jitter: {brightness: 0.2, contrast: 0.2}

checkpointing:
  save_best: true
  save_last: true
  checkpoint_every_n_epochs: 5
  save_top_k: 3  # NEW: Save top 3 checkpoints (enable ensemble consideration)
  output_dir: checkpoints/production/

validation:
  validate_every_n_epochs: 1
  metrics:  # COMPREHENSIVE: Track all metrics (not just loss/acc)
    - val_loss
    - val_acc
    - val_f1
    - val_precision
    - val_recall
    - val_auc  # If applicable

test_set:  # NEW: Test set evaluation configuration
  enabled: true
  evaluate_at_end: true
  metrics:
    - test_loss
    - test_acc
    - test_f1
    - test_precision
    - test_recall
    - test_confusion_matrix

reproducibility:
  seed: 42  # PRODUCTION: Fixed seed for reproducibility
  deterministic: true

export:  # NEW: Model export configuration
  enabled: true
  formats:
    - onnx  # Cross-platform deployment
    - torchscript  # PyTorch deployment
  quantization:
    enabled: true  # Optional: Reduce model size
    dtype: int8
```

**Key Modifications**:
1. **epochs: 100** (extended from 20-50)
2. **patience: 10** (more patient)
3. **save_top_k: 3** (multiple checkpoints)
4. **Comprehensive metrics** (F1, precision, recall, AUC)
5. **Test set evaluation** (enabled)
6. **Export configuration** (ONNX, TorchScript)

**Verification**:
```bash
# Validate YAML syntax
python -c "
import yaml
with open('configs/final_config.yaml') as f:
    config = yaml.safe_load(f)
    print('✓ Final config valid')
    print(f'Epochs: {config[\"training\"][\"epochs\"]}')
    print(f'Patience: {config[\"early_stopping\"][\"patience\"]}')
"
```

---

## Step 2: Execute Final Production Training

### Action: Train with final_config.yaml for production model

**Command**:

```bash
python training_orchestrator.py \
  --config configs/final_config.yaml \
  --mode production \
  --output-dir results/production/
```

**Expected Output**:

```
[CONFIG] Loading: configs/final_config.yaml
[CONFIG] Mode: production
[CONFIG] Final training (extended patience, comprehensive metrics)

[REPRODUCIBILITY] Seed: 42 (production)
[MODEL] ResNet18 (production configuration)
[DATA] Train: 45000, Val: 5000, Test: 10000 (held-out)

[TRAINING] Starting final production training...
```

### Monitoring During Final Training

**Epoch 1-20** (Initial convergence):
```
[EPOCH 10/100]
  Train Loss: 1.123 | Train Acc: 72.3% | Train F1: 0.718
  Val Loss: 1.045 | Val Acc: 74.6% | Val F1: 0.742
  Note: Similar to baseline/optimized initial behavior
```

**Epoch 20-40** (Continued improvement):
```
[EPOCH 30/100]
  Train Loss: 0.654 | Train Acc: 84.2% | Train F1: 0.838
  Val Loss: 0.612 | Val Acc: 83.8% | Val F1: 0.835
  Note: Approaching best from Phase 4 (83.1%), slight improvement
```

**Epoch 40-55** (Final refinement):
```
[EPOCH 45/100]
  Train Loss: 0.589 | Train Acc: 86.7% | Train F1: 0.864
  Val Loss: 0.578 | Val Acc: 83.9% | Val F1: 0.837
  Note: Marginal improvements, nearing convergence
```

**Epoch 55** (Early Stopping):
```
[EPOCH 55/100]
  Train Loss: 0.567 | Train Acc: 87.1% | Train F1: 0.868
  Val Loss: 0.582 | Val Acc: 83.7% | Val F1: 0.835
  Early stopping: no improvement for 10 epochs
  Best checkpoint: epoch_45.pt (val_acc=83.9%)

[TRAINING COMPLETE]
Total time: 2h 18m
Best val acc: 83.9% (epoch 45)
Final val acc: 83.7% (epoch 55)
```

**Expected Pattern**:
- Initial 30 epochs: Rapid improvement (similar to baseline/optimized)
- Epochs 30-45: Slow improvement (+0.5-1% val acc)
- Epochs 45-55: Plateau, early stopping triggered
- **Final result**: 83.9% val acc (slight improvement over Phase 4: 83.1%)

**Interpretation**: Extended training with patience=10 squeezed out additional 0.8% improvement. Worthwhile for production model.

---

## Step 3: Test Set Evaluation

### Action: Evaluate on held-out test set (never seen during training)

**Automated** (if configured in final_config.yaml):
```
[TEST SET EVALUATION]
Loading best checkpoint: checkpoints/production/final_model_best.pt
Evaluating on test set (10000 samples)...

Test Results:
  Test Loss: 0.594
  Test Acc: 82.8%
  Test F1: 0.826
  Test Precision: 0.834
  Test Recall: 0.819

Confusion Matrix:
              Predicted
              0    1    2    3
   Actual 0 [890   12    5    3]
          1  [15  856   18   11]
          2  [ 7   22  845   26]
          3  [ 4   10   32  854]

Per-Class F1:
  Class 0: 0.845
  Class 1: 0.832
  Class 2: 0.798
  Class 3: 0.829
```

**Manual Evaluation** (if not automated):

```python
import torch

# Load best checkpoint
checkpoint = torch.load('checkpoints/production/final_model_best.pt')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Evaluate on test set
test_loss, test_metrics = evaluate(model, test_loader, comprehensive=True)

print(f"Test Acc: {test_metrics['accuracy']:.1f}%")
print(f"Test F1: {test_metrics['f1']:.3f}")
print(f"Test Precision: {test_metrics['precision']:.3f}")
print(f"Test Recall: {test_metrics['recall']:.3f}")

# Generate confusion matrix
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

y_true, y_pred = collect_predictions(model, test_loader)
cm = confusion_matrix(y_true, y_pred)

disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.savefig('results/production/confusion_matrix.png')
```

### Analysis: Val vs Test Performance

**Comparison**:
- Val Acc: 83.9% (from final training)
- Test Acc: 82.8% (held-out test set)
- Gap: 1.1%

**Interpretation**:
- **Gap <2%**: Excellent! Model generalizes well
- **Test slightly lower than val**: Expected (test set never seen)
- **No major distribution shift**: Train/val/test splits are representative

**If gap >5%**: Warning! Possible issues:
- Validation set too easy or leaked information
- Test set has distribution shift
- Need to investigate train/val/test split quality

---

## Step 4: Generate Test Results Report

### Action: Create test_results.md documenting test set performance

**Manual Creation**:

```markdown
# Test Set Evaluation - Phase 5

**Date**: 2025-10-29
**Model**: Final Production Model (epoch 45)
**Test Set Size**: 10,000 samples (held-out, never seen during training)

---

## Performance Metrics

### Overall Performance

| Metric | Value |
|--------|-------|
| **Test Accuracy** | 82.8% |
| **Test F1-Score** | 0.826 |
| **Test Precision** | 0.834 |
| **Test Recall** | 0.819 |
| **Test Loss** | 0.594 |

### Validation vs Test Performance

| Metric | Val (Final Training) | Test (Held-Out) | Gap |
|--------|---------------------|----------------|-----|
| Accuracy | 83.9% | 82.8% | -1.1% |
| F1-Score | 0.837 | 0.826 | -0.011 |

**Analysis**: Gap <2%, model generalizes well. Test performance close to validation, no overfitting to val set.

---

## Per-Class Performance

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| 0 | 0.856 | 0.835 | 0.845 | 910 |
| 1 | 0.842 | 0.823 | 0.832 | 900 |
| 2 | 0.798 | 0.799 | 0.798 | 900 |
| 3 | 0.841 | 0.817 | 0.829 | 900 |
| **Avg** | **0.834** | **0.819** | **0.826** | **3610** |

**Analysis**:
- Class 2 weakest (F1: 0.798) but still acceptable
- All classes F1 >0.79 (no catastrophic failures)
- Balanced performance across classes

---

## Confusion Matrix

[INSERT: confusion_matrix.png]

**Key Observations**:
1. Strong diagonal (correct predictions)
2. Class 2 confused with Class 3 most often (26 samples)
3. Minimal confusion between Class 0 and others
4. Overall confusion low (<3% error rate per class pair)

---

## Failure Mode Analysis

**Sample Misclassifications**:
1. Class 2 → Class 3: 26 samples
   - Analysis: Classes 2 and 3 visually similar
   - Impact: Minor, 2.6% of Class 2 samples

2. Class 1 → Class 2: 18 samples
   - Analysis: Ambiguous edge cases
   - Impact: Minor, 2.0% of Class 1 samples

**No Critical Failures**: All misclassification rates <3%, acceptable.

---

## Target Achievement

- **Target Accuracy**: 80%
- **Achieved Test Accuracy**: 82.8% ✓
- **Margin**: +2.8% above target

**Conclusion**: Model meets production requirements on held-out test set.

---

## Reproducibility

- **Seed**: 42 (production seed)
- **Config**: final_config.yaml
- **Checkpoint**: checkpoints/production/final_model_best.pt (epoch 45)

**Test Reproducibility**: Running evaluation twice with same checkpoint yields identical results (deterministic).
```

**Save**: `results/production/test_results.md`

---

## Step 5: Model Export for Deployment

### Action: Export model to deployment-ready formats

**5.1: Export to ONNX** (Recommended):

```python
import torch.onnx

# Load best checkpoint
checkpoint = torch.load('checkpoints/production/final_model_best.pt')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Create dummy input (batch_size=1 for deployment)
dummy_input = torch.randn(1, 3, 32, 32).to(device)

# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "models/production_model.onnx",
    export_params=True,
    opset_version=13,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
)

print("✓ Model exported to models/production_model.onnx")
```

**Verify ONNX Export**:

```python
import onnxruntime as ort

# Load ONNX model
ort_session = ort.InferenceSession("models/production_model.onnx")

# Test inference
sample_input = torch.randn(1, 3, 32, 32).numpy()
outputs = ort_session.run(None, {'input': sample_input})

# Verify accuracy matches PyTorch model
onnx_acc = evaluate_onnx(ort_session, test_loader)
pytorch_acc = 82.8  # From Step 3

assert abs(onnx_acc - pytorch_acc) < 0.5, f"ONNX accuracy mismatch: {onnx_acc} vs {pytorch_acc}"
print(f"✓ ONNX accuracy verified: {onnx_acc:.1f}% (matches PyTorch: {pytorch_acc:.1f}%)")
```

**5.2: Export to TorchScript** (PyTorch deployment):

```python
# Trace model
example_input = torch.randn(1, 3, 32, 32).to(device)
traced_model = torch.jit.trace(model, example_input)

# Save TorchScript model
traced_model.save("models/production_model.pt")

print("✓ Model exported to models/production_model.pt (TorchScript)")

# Verify TorchScript accuracy
scripted_model = torch.jit.load("models/production_model.pt")
scripted_acc = evaluate(scripted_model, test_loader)
assert abs(scripted_acc - 82.8) < 0.5
print(f"✓ TorchScript accuracy verified: {scripted_acc:.1f}%")
```

**5.3: Optional Quantization** (Reduce size/latency):

```python
import torch.quantization

# Dynamic quantization (easiest)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear, torch.nn.Conv2d},
    dtype=torch.qint8
)

# Evaluate quantized model
quantized_acc = evaluate(quantized_model, test_loader)
print(f"Quantized accuracy: {quantized_acc:.1f}% (FP32: 82.8%)")

# Save quantized model
torch.save(quantized_model.state_dict(), "models/production_model_quantized.pth")

# Export quantized to ONNX
torch.onnx.export(
    quantized_model,
    dummy_input,
    "models/production_model_quantized.onnx",
    ...
)

print(f"✓ Quantized model: {quantized_acc:.1f}% accuracy (FP32: 82.8%)")
# Expected: 82.3-82.8% (minor degradation acceptable for 2x size reduction)
```

**Model Sizes**:
```bash
ls -lh models/
# production_model.onnx: 89 MB (FP32)
# production_model_quantized.onnx: 45 MB (INT8, ~2x smaller)
# production_model.pt: 92 MB (TorchScript)
```

---

## Step 6: Create Deployment Documentation

### Action: Generate deployment_guide.md for production deployment

**Template**:

```markdown
# Production Model Deployment Guide

**Model**: ResNet18 Image Classifier
**Version**: 1.0.0
**Date**: 2025-10-29

---

## Model Overview

**Purpose**: Classify images into 4 categories (Classes 0-3)

**Performance**:
- Test Accuracy: 82.8%
- Test F1-Score: 0.826
- Inference Time: 12ms/sample (GPU), 78ms/sample (CPU)

**Model Files**:
- `models/production_model.onnx` (89 MB, recommended)
- `models/production_model_quantized.onnx` (45 MB, faster inference)
- `models/production_model.pt` (92 MB, PyTorch only)

---

## Input Specification

**Format**: RGB image
**Shape**: (batch_size, 3, 32, 32)
**Data Type**: float32
**Normalization**: Mean [0.485, 0.456, 0.406], Std [0.229, 0.224, 0.225]

**Preprocessing**:
```python
from torchvision import transforms

preprocess = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Apply to PIL image
input_tensor = preprocess(pil_image).unsqueeze(0)
```

---

## Output Specification

**Format**: Logits (unnormalized scores)
**Shape**: (batch_size, 4)
**Data Type**: float32

**Postprocessing**:
```python
import torch.nn.functional as F

# Convert logits to probabilities
probs = F.softmax(output, dim=1)

# Get predicted class
pred_class = torch.argmax(probs, dim=1).item()
confidence = probs[0][pred_class].item()

print(f"Predicted class: {pred_class}, Confidence: {confidence:.2f}")
```

---

## Inference API

**ONNX Runtime** (Recommended):
```python
import onnxruntime as ort
import numpy as np

# Load model
session = ort.InferenceSession("models/production_model.onnx")

# Prepare input
input_data = preprocess(pil_image).numpy()

# Run inference
outputs = session.run(None, {'input': input_data})
logits = outputs[0]

# Postprocess
probs = softmax(logits, axis=1)
pred_class = np.argmax(probs, axis=1)[0]
```

**PyTorch** (Alternative):
```python
import torch

# Load model
model = torch.jit.load("models/production_model.pt")
model.eval()

# Prepare input
input_tensor = preprocess(pil_image).unsqueeze(0)

# Run inference
with torch.no_grad():
    output = model(input_tensor)

# Postprocess
probs = F.softmax(output, dim=1)
pred_class = torch.argmax(probs, dim=1).item()
```

---

## Performance Characteristics

**Latency**:
- GPU (NVIDIA V100): 12ms/sample (batch=1), 8ms/sample (batch=32)
- CPU (Intel Xeon): 78ms/sample (batch=1), 45ms/sample (batch=32)

**Throughput**:
- GPU: 83 samples/sec (batch=1), 250 samples/sec (batch=32)
- CPU: 13 samples/sec (batch=1), 22 samples/sec (batch=32)

**Memory**:
- GPU: 1.2 GB VRAM (batch=1), 2.8 GB VRAM (batch=32)
- CPU: 450 MB RAM (batch=1), 890 MB RAM (batch=32)

---

## Monitoring Recommendations

**Track in Production**:
1. **Latency**: p50, p95, p99
   - Alert if p95 > 50ms (GPU) or > 200ms (CPU)

2. **Accuracy Drift**: Compare predictions to ground truth (when available)
   - Alert if accuracy drops >5% from test set baseline (82.8%)

3. **Confidence Distribution**: Track prediction confidence
   - Alert if low-confidence predictions (prob <0.5) > 10%

4. **Input Distribution**: Monitor input statistics
   - Alert if mean/std shift significantly from training distribution

---

## Deployment Environments

**Recommended**:
- **Production**: ONNX Runtime on GPU (lowest latency)
- **Edge/Mobile**: ONNX Runtime on CPU with quantized model
- **PyTorch-only**: TorchScript model on GPU

**NOT Recommended**:
- Raw PyTorch model in production (slower, larger)
- CPU-only for high-throughput applications

---

## Configuration

**Environment Variables**:
```bash
MODEL_PATH=models/production_model.onnx
BATCH_SIZE=32
DEVICE=cuda  # or cpu
NUM_WORKERS=4
```

**Scaling**:
- Horizontal: Deploy multiple instances behind load balancer
- Vertical: Increase batch size (up to GPU memory limit)

---

## Testing

**Smoke Test**:
```bash
python inference_api.py --input test_image.jpg --output prediction.json
# Expected: prediction.json with class and confidence
```

**Load Test**:
```bash
python load_test.py --model models/production_model.onnx --num-requests 1000 --concurrency 10
# Expected: p95 latency <50ms, 0% errors
```

---

## Troubleshooting

**Issue**: High latency (>100ms/sample on GPU)
- **Check**: GPU utilization (nvidia-smi)
- **Fix**: Increase batch size, reduce num_workers

**Issue**: Low accuracy in production
- **Check**: Input preprocessing (normalization correct?)
- **Fix**: Verify mean/std match training: [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]

**Issue**: ONNX model accuracy mismatch
- **Check**: ONNX export parameters (opset_version=13?)
- **Fix**: Re-export with correct parameters, verify with test set

---

## Support

**Contact**: ML Team (ml-team@example.com)
**Documentation**: https://docs.example.com/ml-classifier
**Model Registry**: https://registry.example.com/models/image-classifier-v1.0.0
```

**Save**: `docs/deployment_guide.md`

---

## Step 7: Complete Production Readiness Checklist

### Action: Fill out production_ready.md checklist

**Gate**: `phases/05_finalization/checklists/production_ready.md`

Verify all items before deployment:
- [ ] Final training complete (extended patience, comprehensive metrics)
- [ ] Production checkpoint saved (best and last)
- [ ] Test set evaluation complete (all metrics documented)
- [ ] Test accuracy meets requirements (≥80% target)
- [ ] Val-test gap acceptable (<5%)
- [ ] Model exported to deployment format (ONNX/TorchScript)
- [ ] Exported model accuracy verified (matches test set)
- [ ] Deployment documentation complete (deployment_guide.md)
- [ ] Inference API implemented and tested
- [ ] Monitoring guide created
- [ ] Reproducibility documented (seed, config, checkpoint)
- [ ] Stakeholder approval obtained

**Cannot deploy without completing this checklist.**

---

## Success Criteria

Phase 5 complete when:

- ✅ Final training executed successfully
- ✅ Best production checkpoint saved
- ✅ Test set evaluation complete
- ✅ Test accuracy ≥ target (82.8% ≥ 80%)
- ✅ Model exported (ONNX/TorchScript)
- ✅ Exported accuracy verified
- ✅ Deployment documentation created
- ✅ Inference API tested
- ✅ Production readiness checklist passed
- ✅ **Model ready for deployment**

---

**Phase 5 workflow produces production-ready model through extended final training, comprehensive test set evaluation, model export optimization, and complete deployment documentation. All metrics tracked, reproducibility ensured, and deployment guide created for smooth production deployment.**

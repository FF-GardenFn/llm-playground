# Production Readiness Checklist

**Gate**: Phase 5 → Production Deployment
**Purpose**: Verify model is production-ready before deployment

---

## Mandatory Verification

**This checklist MUST be completed before deploying to production.**

Cannot deploy if ANY checkbox is unchecked.

---

## ✅ Training Completion Verification

### Final Training Complete

- [ ] **Final production training executed and completed**
  - Training ran with final_config.yaml
  - Completed training (early stopped or reached max epochs)
  - No crashes, NaN losses, or errors
  - Logs saved correctly

**Verification**:
```bash
# Check training completion
grep "Training complete" results/production/training.log

# Verify final metrics
cat results/production/metrics.json | python -m json.tool | tail -50
```

**If unchecked**: Final training incomplete or failed. Debug issues, restart final training.

---

### Production Checkpoint Saved

- [ ] **Best production checkpoint saved**
  - checkpoints/production/final_model_best.pt exists
  - Contains model_state_dict, epoch, val_acc, all metrics
  - Val accuracy documented

**Verification**:
```bash
ls -lh checkpoints/production/final_model_best.pt

python -c "
import torch
ckpt = torch.load('checkpoints/production/final_model_best.pt')
assert 'model_state_dict' in ckpt
assert 'val_acc' in ckpt
print(f'✓ Best checkpoint: epoch {ckpt[\"epoch\"]}, val_acc={ckpt[\"val_acc\"]:.1f}%')
"
```

**If unchecked**: Production checkpoint not saved. Check checkpointing configuration, verify training completed.

---

- [ ] **Last production checkpoint saved**
  - checkpoints/production/final_model_last.pt exists
  - Allows analysis or resume if needed

**Verification**:
```bash
ls -lh checkpoints/production/final_model_last.pt
```

---

## ✅ Test Set Evaluation Verification

### Test Set Evaluation Complete

- [ ] **Comprehensive test set evaluation completed**
  - Evaluated on held-out test set (never seen during training)
  - All metrics calculated (acc, F1, precision, recall)
  - Results documented in test_results.md

**Verification**:
```bash
# Check test results exist
cat results/production/test_results.md | head -50

# Verify comprehensive metrics
grep "Test Accuracy" results/production/test_results.md
grep "Test F1" results/production/test_results.md
grep "Test Precision" results/production/test_results.md
grep "Test Recall" results/production/test_results.md
```

**If unchecked**: Run test set evaluation (Step 3 of workflow.md), generate test_results.md.

---

### Test Accuracy Meets Requirements

- [ ] **Test accuracy meets or exceeds target**
  - Test acc ≥ target (e.g., 82.8% ≥ 80%)
  - Not just validation accuracy, actual test set performance

**Verification**:
```python
# Extract test accuracy
test_acc = 82.8  # From test_results.md
target_acc = 80.0

if test_acc >= target_acc:
    print(f"✓ Test accuracy {test_acc:.1f}% ≥ target {target_acc:.1f}%")
    print(f"Margin: +{test_acc - target_acc:.1f}%")
else:
    print(f"✗ Test accuracy {test_acc:.1f}% < target {target_acc:.1f}%")
    print(f"Gap: {target_acc - test_acc:.1f}%")
```

**If unchecked**:
- If test_acc < target: Model does not meet requirements, cannot deploy
- Action: Return to Phase 3/4 for additional optimization, or
- Action: Re-evaluate target if unrealistic given data quality

---

### Val-Test Gap Acceptable

- [ ] **Validation and test accuracy gap acceptable (<5%)**
  - Val acc from final training: X%
  - Test acc from test set: Y%
  - Gap = |X - Y| < 5%

**Verification**:
```python
val_acc = 83.9  # From final training
test_acc = 82.8  # From test set
gap = abs(val_acc - test_acc)

if gap < 5.0:
    print(f"✓ Val-test gap: {gap:.1f}% < 5% (acceptable)")
else:
    print(f"✗ Val-test gap: {gap:.1f}% ≥ 5% (warning: possible overfitting to val set)")
```

**Expected**: Gap <2% excellent, Gap 2-5% acceptable, Gap >5% warning

**If gap >5%**: Investigate distribution mismatch, potential overfitting to validation set

---

### Confusion Matrix Analyzed

- [ ] **Confusion matrix generated and analyzed**
  - confusion_matrix.png created
  - Per-class performance documented
  - No critical failure modes identified

**Verification**:
```bash
# Check confusion matrix exists
ls results/production/confusion_matrix.png

# Check per-class metrics
grep -A 10 "Per-Class Performance" results/production/test_results.md
```

**Expected**: All classes F1 >0.7, no catastrophic failures (<50% for any class)

**If unchecked**: Generate confusion matrix, analyze per-class performance, document in test_results.md.

---

## ✅ Model Export Verification

### Model Exported to Deployment Format

- [ ] **Model exported to at least one deployment format**
  - ONNX (recommended): models/production_model.onnx exists
  - TorchScript (alternative): models/production_model.pt exists
  - File size reasonable (not 0 bytes, not excessively large)

**Verification**:
```bash
ls -lh models/production_model.onnx
# Expected: 80-100 MB for ResNet18

# OR
ls -lh models/production_model.pt
```

**If unchecked**: Export model using Step 5 of workflow.md (ONNX or TorchScript).

---

### Exported Model Accuracy Verified

- [ ] **Exported model accuracy matches test set accuracy**
  - Loaded exported model (ONNX/TorchScript)
  - Ran inference on test set
  - Accuracy matches PyTorch model (within 0.5%)

**Verification**:
```python
# For ONNX
import onnxruntime as ort
ort_session = ort.InferenceSession("models/production_model.onnx")
onnx_acc = evaluate_onnx(ort_session, test_loader)

pytorch_acc = 82.8  # From test_results.md

assert abs(onnx_acc - pytorch_acc) < 0.5, f"Accuracy mismatch: {onnx_acc} vs {pytorch_acc}"
print(f"✓ ONNX accuracy: {onnx_acc:.1f}% (PyTorch: {pytorch_acc:.1f}%)")
```

**If unchecked**: Re-export model, verify export parameters correct, test accuracy.

---

### Inference Tested

- [ ] **Inference API tested with sample inputs**
  - Can load exported model
  - Can run inference on sample image
  - Output format correct (logits/probs)
  - Latency acceptable

**Verification**:
```python
# Test inference on single sample
import time

sample_image = load_test_image()
start = time.time()
output = run_inference(model, sample_image)
latency = time.time() - start

assert output.shape == (1, 4), "Output shape incorrect"
assert latency < 0.1, f"Latency too high: {latency:.3f}s"

print(f"✓ Inference successful: latency {latency*1000:.1f}ms")
```

**If unchecked**: Implement inference API (Step 5 of workflow.md), test with samples.

---

## ✅ Documentation Verification

### Deployment Guide Complete

- [ ] **deployment_guide.md created with all required sections**
  - Model overview (purpose, performance)
  - Input specification (format, shape, preprocessing)
  - Output specification (format, postprocessing)
  - Inference API (code examples for ONNX/PyTorch)
  - Performance characteristics (latency, throughput, memory)
  - Monitoring recommendations
  - Deployment environments
  - Troubleshooting guide

**Verification**:
```bash
# Check deployment guide exists
cat docs/deployment_guide.md | head -100

# Verify required sections present
grep "## Input Specification" docs/deployment_guide.md
grep "## Output Specification" docs/deployment_guide.md
grep "## Inference API" docs/deployment_guide.md
grep "## Monitoring Recommendations" docs/deployment_guide.md
```

**If unchecked**: Create deployment_guide.md following template in workflow.md Step 6.

---

### Test Results Documented

- [ ] **test_results.md complete with comprehensive analysis**
  - Overall metrics (acc, F1, precision, recall)
  - Val vs test comparison
  - Per-class performance
  - Confusion matrix
  - Failure mode analysis
  - Target achievement documented

**Verification**:
```bash
# Check test results complete
grep "## Performance Metrics" results/production/test_results.md
grep "## Validation vs Test" results/production/test_results.md
grep "## Per-Class Performance" results/production/test_results.md
grep "## Target Achievement" results/production/test_results.md
```

**If unchecked**: Create test_results.md following template in workflow.md Step 4.

---

### Model Card Created (Optional but Recommended)

- [ ] **model_card.md created for transparency and ethics**
  - Intended use and users
  - Training data characteristics
  - Performance metrics and limitations
  - Ethical considerations
  - Bias analysis (if applicable)

**Verification**:
```bash
# Check model card exists
cat docs/model_card.md | head -50
```

**Note**: Highly recommended for production ML systems, especially customer-facing applications.

**If skipped**: Document "Model card not created" in final_report.md with justification.

---

### Monitoring Guide Created

- [ ] **Monitoring strategy documented**
  - Metrics to track in production (latency, accuracy drift, confidence)
  - Alerting thresholds defined
  - Dashboard recommendations
  - Incident response procedures

**Verification**:
```bash
# Check monitoring section in deployment guide
grep -A 20 "## Monitoring Recommendations" docs/deployment_guide.md
```

**Expected**: Clear metrics, thresholds, and actions defined

**If unchecked**: Add monitoring section to deployment_guide.md.

---

## ✅ Reproducibility Verification

### Reproducibility Fully Documented

- [ ] **Complete reproducibility documentation**
  - Seed documented (42 for production)
  - Configuration file saved (final_config.yaml)
  - Checkpoint documented (final_model_best.pt epoch X)
  - Environment documented (Python, PyTorch versions, GPU)

**Verification**:
```bash
# Check reproducibility section in final_report.md
grep -A 10 "## Reproducibility" final_report.md
```

**Expected**:
```
Reproducibility:
- Seed: 42 (fixed)
- Config: configs/final_config.yaml
- Checkpoint: checkpoints/production/final_model_best.pt (epoch 45)
- Environment: Python 3.10.12, PyTorch 2.1.0, CUDA 11.8
- GPU: NVIDIA V100 (16GB)
```

**If unchecked**: Document all reproducibility details in final_report.md.

---

### Environment Snapshot

- [ ] **Environment snapshot saved**
  - requirements.txt or environment.yml with exact versions
  - Can recreate environment from snapshot

**Verification**:
```bash
# Check requirements file exists
cat requirements.txt | head -20

# Or for conda
cat environment.yml
```

**Expected**: Pinned versions (e.g., `torch==2.1.0` not `torch>=2.0`)

**If unchecked**: Generate requirements file:
```bash
pip freeze > requirements.txt
# or
conda env export > environment.yml
```

---

## ✅ Quality Assurance

### No Critical Issues

- [ ] **No known critical issues or bugs**
  - No P0/P1 bugs in model or inference code
  - All known issues documented in final_report.md
  - Workarounds documented if issues exist

**Self-Check**:
- Any known failure modes? (Document in test_results.md)
- Any edge cases where model fails? (Document and test)
- Any performance degradation scenarios? (Document thresholds)

**If unchecked**: Identify and document all known issues, assess severity, determine if blocking deployment.

---

### Code Review Complete (If Applicable)

- [ ] **Production code reviewed**
  - Inference code reviewed by peer
  - No security vulnerabilities
  - Error handling implemented
  - Logging implemented

**Verification**: Code review checklist or approval documented

**If unchecked**: Conduct code review for inference_api.py and deployment scripts.

---

## ✅ Stakeholder Approval

### Technical Approval

- [ ] **Technical lead approves deployment**
  - Model performance meets requirements
  - Technical implementation sound
  - Monitoring and alerting adequate

**Verification**: Document approval in final_report.md or deployment ticket

---

### Product Approval (If Applicable)

- [ ] **Product owner approves deployment**
  - Model meets product requirements
  - User experience acceptable
  - Risk assessment completed

**Verification**: Product approval documented

---

### Compliance Approval (If Applicable)

- [ ] **Compliance/legal approves deployment**
  - Data privacy requirements met
  - Regulatory compliance verified
  - Ethical review completed (if required)

**Verification**: Compliance approval documented

---

## Gate Status

### ✅ Gate Passed - DEPLOY TO PRODUCTION

**All checkboxes checked**: Model is production-ready.

**Next action**: **Deploy** model to production environment

**Deployment checklist**:
1. Deploy model to staging environment
2. Run smoke tests in staging
3. Load test in staging (1000+ requests)
4. Deploy to production (blue-green or canary)
5. Monitor metrics for 24-48 hours
6. Full rollout if metrics stable

---

### ❌ Gate BLOCKED - CANNOT DEPLOY

**Any checkbox unchecked**: Model NOT ready for production.

**Next action**:
1. Identify which verification failed
2. Review relevant section for requirements
3. Complete missing work
4. Re-run evaluation or training if needed
5. Complete checklist again

**NEVER deploy a model with incomplete production readiness checks.**

---

## Common Issues and Resolutions

### Issue: Test accuracy below target

**Symptom**: Test acc 78%, Target 80%

**Checklist impact**: "Test accuracy meets requirements" blocked

**Resolution**:
- **Cannot deploy**: Model does not meet requirements
- **Option 1**: Return to Phase 3/4, optimize further
- **Option 2**: Re-evaluate target (is 80% realistic given data quality?)
- **Option 3**: Accept lower target with stakeholder approval (document in final_report.md)

---

### Issue: Large val-test gap (>5%)

**Symptom**: Val acc 83%, Test acc 76% (gap 7%)

**Checklist impact**: "Val-test gap acceptable" blocked

**Resolution**:
- **Investigate**: Why is test performance much lower?
  - Train/val/test distribution mismatch?
  - Validation set too easy or leaked information?
  - Test set has distribution shift?
- **Action**:
  - If mismatch: Fix data split, restart pipeline
  - If test harder: Accept as realistic performance, document
  - If val leaked: Re-split data, restart pipeline

---

### Issue: Exported model accuracy mismatch

**Symptom**: PyTorch 82.8%, ONNX 79.3% (gap 3.5%)

**Checklist impact**: "Exported model accuracy verified" blocked

**Resolution**:
1. **Check export parameters**: Verify opset_version=13, correct input/output names
2. **Check preprocessing**: Ensure ONNX inference uses same preprocessing as PyTorch
3. **Re-export**: Try exporting again with correct parameters
4. **Test on small subset**: Verify outputs match exactly for a few samples
5. **If persists**: Use TorchScript instead of ONNX, or accept minor degradation if <1%

---

### Issue: Inference too slow

**Symptom**: GPU latency 150ms/sample (target: <50ms)

**Checklist impact**: "Inference tested" may pass but not production-ready

**Resolution**:
1. **Increase batch size**: Test with batch=16, 32 (reduces per-sample latency)
2. **Optimize model**: Use quantization (int8), pruning
3. **Use faster backend**: TorchScript, TensorRT instead of ONNX Runtime
4. **Profile bottlenecks**: Identify slow operations (preprocessing vs inference)
5. **If still slow**: Upgrade GPU, or accept for non-latency-critical applications

---

### Issue: Monitoring strategy unclear

**Symptom**: Deployment guide exists but monitoring section vague

**Checklist impact**: "Monitoring guide created" technically passes but insufficient

**Resolution**:
- **Define specific metrics**: Latency p95, accuracy (if labels available), confidence distribution
- **Set thresholds**: E.g., "Alert if p95 > 50ms", "Alert if accuracy drops >5%"
- **Document actions**: What to do when alert fires?
- **Dashboard**: Link to monitoring dashboard (Grafana, CloudWatch, etc.)

---

## Checklist Summary

**Total Items**: 24 mandatory verifications

**Categories**:
- Training Completion: 3 items
- Test Set Evaluation: 4 items
- Model Export: 3 items
- Documentation: 4 items
- Reproducibility: 2 items
- Quality Assurance: 2 items
- Stakeholder Approval: 3 items

**Gate Enforcement**: ALL mandatory items must be checked before deployment.

---

## Time Budget

**Target**: 15-30 minutes for checklist completion (most time spent in prior steps)

**If checklist takes >30 minutes**: Missing documentation or evaluations. Return to workflow.md steps to complete requirements.

---

## Final Sign-Off

**Model Name**: [e.g., Image Classifier v1.0.0]
**Test Accuracy**: [e.g., 82.8%]
**Target Met**: [Yes/No]
**Deployment Approved By**:
- Technical Lead: [Name, Date]
- Product Owner: [Name, Date]
- Compliance: [Name, Date] (if applicable)

**Deployment Date**: [YYYY-MM-DD]

---

**Production readiness checklist ensures comprehensive validation before deployment. All metrics verified, documentation complete, stakeholder approval obtained. Model tested on held-out test set, exported and verified, monitoring strategy defined. Only deploy when ALL checkboxes checked - no exceptions.**

---
description: Execute final production training, test set evaluation, and deployment preparation (Phase 5)
allowed-tools: Bash, Read, Write, Edit, TodoWrite
argument-hint: [--config path/to/final_config.yaml]
---

# Production Finalization Command

Execute Phase 5 final production training with comprehensive testing, model export, and deployment documentation.

## What this does

1. **Creates final_config.yaml** (best config from Phase 2 or Phase 4)
2. **Runs final production training** (extended epochs=100, patience=10)
3. **Evaluates on test set** (held-out, never seen during training)
4. **Exports model** to deployment formats (ONNX/TorchScript)
5. **Verifies exported accuracy** matches test set
6. **Generates deployment documentation** (deployment_guide.md, test_results.md)
7. **Completes production readiness checklist** (24 items)

## Usage

```bash
# Use best config automatically (baseline or optimized)
/finalize

# Specify custom final config
/finalize --config configs/my_final_config.yaml

# Skip training, just export and document (if training already complete)
/finalize --export-only
```

## Prerequisites

Phase 2 complete (if baseline sufficient), OR Phase 4 complete (if optimized):
- ✅ Best configuration identified (training_config.yaml OR optimization_config.yaml)
- ✅ Performance target achieved or baseline acceptable
- ✅ Previous phase checklist passed

## Your Task

1. **Load finalization workflow**: Read `phases/05_finalization/workflow.md`
2. **Create final_config.yaml** (Step 1):
   - Copy best config (baseline or optimized)
   - Extend epochs to 100, patience to 10
   - Add comprehensive metrics tracking
3. **Execute final training** (Step 2):
   - Train with final_config.yaml
   - Monitor for final performance squeeze (expect +0.5-1% improvement)
4. **Test set evaluation** (Step 3):
   - Evaluate on held-out test set
   - Calculate all metrics (acc, F1, precision, recall)
   - Generate confusion matrix
   - Verify val-test gap <5%
5. **Export model** (Step 5):
   - Export to ONNX (recommended)
   - Export to TorchScript (optional)
   - Apply quantization if requested (int8, fp16)
   - Verify exported accuracy matches test set
6. **Create deployment docs** (Step 6):
   - deployment_guide.md (API, monitoring, troubleshooting)
   - test_results.md (comprehensive test set analysis)
   - model_card.md (optional, recommended for transparency)
7. **Complete production checklist**: `phases/05_finalization/checklists/production_ready.md` (24 items)
8. **Report final status**: Summarize test performance, deployment readiness

## Expected Duration

1-3 hours:
- Final training: 1.5-2.5 hours
- Test evaluation: 10 minutes
- Model export: 15 minutes
- Documentation: 30 minutes

## Output

- final_config.yaml (production configuration)
- Production checkpoints in checkpoints/production/
- test_results.md (comprehensive test set analysis)
- Exported models in models/ (ONNX, TorchScript)
- deployment_guide.md (deployment instructions)
- Production readiness verification report

## Example Output

```
✓ Final production training complete (2h 18m)
  - Best epoch: 45/100
  - Final val acc: 83.9% (slight improvement over Phase 4: 83.1%)

✓ Test set evaluation complete
  - Test Acc: 82.8% (close to val: 83.9%)
  - Test F1: 0.826
  - Val-test gap: 1.1% (excellent, <2%)
  - All classes F1 >0.79 ✓

✓ Model exported
  - ONNX: models/production_model.onnx (89 MB)
  - Quantized: models/production_model_quantized.onnx (45 MB)
  - Exported accuracy: 82.8% (matches test set) ✓

✓ Deployment documentation complete
  - deployment_guide.md created
  - test_results.md created
  - Inference API documented

✓ Production Readiness: 24/24 checks passed ✓

Target: 80% test acc
Achieved: 82.8% ✓ (exceeded by 2.8%)

🚀 MODEL READY FOR PRODUCTION DEPLOYMENT
```

## Production Readiness Gate (24 items)

Cannot deploy without all checks passing:
- Final training complete
- Test set evaluation complete, meets requirements
- Val-test gap acceptable (<5%)
- Model exported and verified
- Deployment documentation complete
- Stakeholder approval obtained

## Deployment Decision

After finalization:
- **All checks passed** → ✅ DEPLOY to production
- **Test acc < target** → Cannot deploy (return to optimization or accept lower target)
- **Val-test gap >5%** → Investigate distribution mismatch
- **Export accuracy mismatch** → Fix export, re-verify

## Final Output

**Production-ready model** with:
- Comprehensive test validation
- Deployment-optimized formats
- Complete documentation
- Monitoring recommendations
- Stakeholder approval

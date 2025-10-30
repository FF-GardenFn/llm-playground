---
description: Execute Phase 2 baseline training with reproducibility guarantees
allowed-tools: Bash, Read, Write, TodoWrite
argument-hint: [--config path/to/config.yaml]
---

# Baseline Training Command

Execute fast baseline training (Phase 2) to verify infrastructure and establish performance baseline.

## What this does

1. **Validates reproducibility** (Phase 1 gate must pass)
2. **Runs baseline training** with conservative hyperparameters
3. **Monitors GPU utilization** (target >60%)
4. **Saves checkpoints** (best, last, periodic)
5. **Generates baseline_results.md** with metrics
6. **Determines next phase** (Diagnostics if insufficient, Finalization if sufficient)

## Usage

```bash
# Use default config
/train-baseline

# Specify custom config
/train-baseline --config configs/my_training_config.yaml
```

## Prerequisites

Phase 1 (Planning) must be complete:
- ✅ Reproducibility checklist passed (`phases/01_planning/checklists/reproducibility_gate.md`)
- ✅ training_config.yaml exists
- ✅ All seeds fixed (Python, NumPy, PyTorch, CUDA)

## Your Task

1. **Load Phase 2 workflow**: Read `phases/02_baseline/workflow.md`
2. **Execute baseline training**: Follow Step 1-7 in workflow
3. **Monitor for issues**: Auto-load diagnostics if NaN loss, convergence stall, or GPU util <60%
4. **Complete post-baseline checklist**: `phases/02_baseline/checklists/post_baseline.md`
5. **Report results**: Summarize baseline_results.md to user
6. **Recommend next phase**:
   - If val acc ≥ target: "Baseline sufficient, proceed to /finalize"
   - If val acc < target: "Baseline insufficient, proceed to /diagnose"
   - If training failed: "Load diagnostic (NaN loss / convergence stall), fix issues, retry"

## Expected Duration

30-60 minutes (fast iteration)

## Output

- baseline_results.md with metrics
- Checkpoints in checkpoints/baseline/
- Training logs in logs/
- Decision on next phase

## Example Output

```
✓ Phase 1 gate passed (reproducibility verified)
✓ Baseline training complete (42 minutes)
✓ Final metrics: Train 85.2% / Val 78.9%
✓ GPU utilization: 73% (acceptable)
✓ Best checkpoint saved: epoch 5

Decision: Baseline val acc 78.9% < target 80%
→ Recommend: /diagnose to analyze performance bottlenecks
```

## Auto-Loading Diagnostics

If training issues detected, automatically load:
- **NaN loss** → diagnostics/nan_loss.md
- **Convergence stall** → diagnostics/convergence_stall.md
- **GPU util <60%** → diagnostics/resource_inefficiency.md

Report diagnostic findings and recommended fixes to user.

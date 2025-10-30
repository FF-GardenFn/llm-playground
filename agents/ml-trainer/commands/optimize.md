---
description: Implement Phase 3 recommendations to improve model performance (Phase 4)
allowed-tools: Bash, Read, Write, Edit, TodoWrite
argument-hint: [--diagnostic path/to/diagnostic_report.md]
---

# Optimization Training Command

Execute Phase 4 optimization by implementing Phase 3 diagnostic recommendations to improve performance beyond baseline.

## What this does

1. **Loads Phase 3 recommendations** from diagnostic_report.md
2. **Creates optimization_config.yaml** with recommended changes
3. **Runs optimized training** (extended patience, implements fixes)
4. **Compares baseline vs optimized** metrics
5. **Generates optimization_results.md** with improvement analysis
6. **Determines next phase** (Finalization if target met, Iterate if insufficient)

## Usage

```bash
# Use default diagnostic report
/optimize

# Specify custom diagnostic report
/optimize --diagnostic results/my_diagnostic_report.md

# Skip to iterative optimization (2nd round)
/optimize --iteration 2
```

## Prerequisites

Phase 3 (Diagnostics) must be complete:
- ✅ diagnostic_report.md exists with recommendations
- ✅ Root cause identified
- ✅ 3-5 specific recommendations documented
- ✅ Diagnostics checklist passed

## Your Task

1. **Load optimization workflow**: Read `phases/04_optimization/workflow.md`
2. **Create optimization_config.yaml** (Step 1):
   - Copy baseline config
   - Apply Phase 3 recommendations
   - Document changes with comments (NEW, CHANGED)
3. **Execute optimized training** (Step 3):
   - Run training with optimization_config.yaml
   - Monitor improvements vs baseline
4. **Evaluate performance** (Step 4):
   - Calculate absolute improvement (optimized - baseline)
   - Calculate relative improvement ((improvement/baseline) * 100)
   - Analyze train-val gap changes
5. **Generate optimization_results.md** (Step 6):
   - Configuration changes documented
   - Baseline vs optimized comparison
   - Learning curves analysis
   - Expected outcome vs actual
6. **Complete optimization checklist**: `phases/04_optimization/checklists/optimization_complete.md`
7. **Report results**: Summarize improvements, recommend next phase

## Expected Duration

1-8 hours (depends on strategy):
- Targeted optimization: 1-2 hours (single training run)
- Comprehensive tuning: 4-8 hours (hyperparameter sweep)

## Output

- optimization_config.yaml with Phase 3 recommendations
- optimization_results.md with comparison
- Checkpoints in checkpoints/optimization/
- Learning curves comparison plot
- Decision on next phase

## Example Output

```
✓ Optimization config created (4 changes from baseline)
  - Added dropout=0.4
  - Added weight_decay=1e-4
  - Enabled data augmentation
  - Reduced early_stopping patience=5

✓ Optimized training complete (1h 42m)

Performance Comparison:
  Baseline:  Train 85.2% | Val 78.9%
  Optimized: Train 86.2% | Val 83.1%

Improvement: +4.2% val acc (5.3% relative)
Train-val gap: 6.3% → 3.1% (reduced by 3.2%)

Target: 80% val acc
Achieved: 83.1% ✓ (exceeded by 3.1%)

→ Recommend: /finalize for production training
```

## Decision Point

After optimization:
- **If target achieved** (val acc ≥ target) → /finalize (Phase 5)
- **If improved but insufficient** → Iterate /optimize (max 2-3 iterations)
- **If no improvement or worse** → Re-run /diagnose (wrong root cause?)
- **If diminishing returns** (<2% per iteration) → Accept best, /finalize

## Iteration Limits

Maximum 2-3 optimization iterations to prevent over-optimization and diminishing returns.

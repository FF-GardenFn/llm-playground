---
description: Analyze baseline performance and generate Phase 4 optimization recommendations (Phase 3)
allowed-tools: Read, Write, TodoWrite
argument-hint: [--baseline path/to/baseline_results.md]
---

# Diagnostic Analysis Command

Execute Phase 3 diagnostic analysis to identify performance bottlenecks and generate targeted optimization recommendations.

## What this does

1. **Loads baseline metrics** from baseline_results.md and logs/metrics.json
2. **Identifies primary issue** using decision tree (overfitting, underfitting, data quality, resource inefficiency)
3. **Loads relevant diagnostic** (overfitting.md, underfitting.md, etc.)
4. **Extracts 3-5 recommendations** prioritized by impact/effort
5. **Generates diagnostic_report.md** with Phase 4 configuration preview
6. **Estimates expected improvement**

## Usage

```bash
# Use default baseline results
/diagnose

# Specify custom baseline results
/diagnose --baseline results/my_baseline/baseline_results.md
```

## Prerequisites

Phase 2 (Baseline) must be complete:
- ✅ baseline_results.md exists
- ✅ Training logs (logs/metrics.json) available
- ✅ Post-baseline checklist passed

## Your Task

1. **Load diagnostic workflow**: Read `phases/03_diagnostics/workflow.md`
2. **Follow decision tree** (Step 2 of workflow):
   - Calculate train-val gap
   - Check if both metrics poor
   - Check for high variance
   - Check GPU utilization
3. **Load appropriate diagnostic**:
   - Gap >15% → diagnostics/overfitting.md
   - Both poor → diagnostics/underfitting.md
   - High variance → diagnostics/data_quality.md
   - GPU <60% → diagnostics/resource_inefficiency.md
4. **Extract recommendations**: Top 3-5 from diagnostic file
5. **Generate diagnostic_report.md** following template in workflow Step 6
6. **Complete diagnostics checklist**: `phases/03_diagnostics/checklists/diagnostics_complete.md`
7. **Report to user**: Summarize root cause, recommendations, expected improvement

## Expected Duration

15-30 minutes (fast analysis)

## Output

- diagnostic_report.md with root cause analysis
- Prioritized recommendations (high/medium/low impact)
- Phase 4 configuration preview
- Expected performance improvement estimate

## Example Output

```
✓ Diagnostic analysis complete (18 minutes)

Primary Issue: Overfitting
- Train Acc: 95.2%, Val Acc: 72.3% (gap = 22.9%)
- Val loss increasing in later epochs

Root Causes:
1. Insufficient regularization (no dropout, no weight decay)
2. Overtraining (continued past optimal point)
3. No data augmentation

Recommendations for Phase 4:
1. Add dropout=0.4 (High impact, Low effort)
2. Add weight_decay=1e-4 (High impact, Low effort)
3. Enable data augmentation (Medium impact, Medium effort)
4. Reduce early_stopping patience=5 (Medium impact, Low effort)

Expected Improvement: +6-10% val acc
Confidence: High (overfitting well-understood, standard fixes)

→ Recommend: /optimize to implement recommendations
```

## Decision Point

After diagnostic analysis:
- **If clear recommendations** → /optimize (Phase 4)
- **If baseline near-optimal** (improvement <3%) → /finalize (Phase 5)
- **If infrastructure issues** → Fix issues, retry /train-baseline

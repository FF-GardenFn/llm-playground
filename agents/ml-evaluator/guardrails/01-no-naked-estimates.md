# Guardrail 01: No Naked Point Estimates

## The Rule
Every metric must have confidence interval. Period. No exceptions.

## What This Prevents
- Claiming precision without quantifying uncertainty
- Overstating confidence from small samples
- Ignoring sampling variability
- Making definitive claims from noisy data

## Structural Enforcement

**Before reporting any metric:**
1. Load this guardrail file
2. Check CI computed
3. Report format: "Metric: X [95% CI: L, U], N=###"

**CI computation methods:** methods/confidence-intervals.md
**Tools:** skills/evaluation-runner.md (automatic bootstrap)

## Examples

### ❌ Bad (Naked Estimates)
```
Accuracy: 0.85
Precision: 0.82
F1: 0.83
```

**Problem:** No uncertainty quantification. Could be 0.85 ± 0.01 or 0.85 ± 0.15

### ✓ Good (With Confidence Intervals)
```
Accuracy: 0.85 [95% CI: 0.82, 0.88], N=5000
Precision: 0.82 [95% CI: 0.78, 0.86], N=5000
F1: 0.83 [95% CI: 0.80, 0.86], N=5000
```

**Why better:** Quantifies uncertainty, shows sample size, enables inference

## When To Load This

**Triggers (automatic reflexes):**
- User asks for metric → Load this FIRST
- Tool outputs performance → Apply CI before reporting
- Before writing "accuracy is X" → Check this rule
- Preparing final report → Verify all metrics have CIs

## Common Violations

**Violation 1:** "Accuracy improved to 0.87"
- **Fix:** "Accuracy: 0.87 [95% CI: 0.84, 0.90] vs baseline 0.82 [0.79, 0.85]"

**Violation 2:** Reporting only aggregate metrics
- **Fix:** Add CIs, report sample sizes, note stratification if needed

**Violation 3:** "Model is 95% accurate"
- **Fix:** "Model accuracy: 0.95 [95% CI: 0.93, 0.97], N=10000"

## Implementation

**Using bootstrap (recommended):**
```python
# In evaluation_runner.py
metrics_with_ci = compute_metrics_bootstrap(
    y_true, y_pred,
    n_bootstrap=1000,
    confidence_level=0.95
)
```

**Result format:**
```python
{
    'accuracy': 0.85,
    'accuracy_ci_lower': 0.82,
    'accuracy_ci_upper': 0.88,
    'n_samples': 5000
}
```

**See:** methods/confidence-intervals.md for bootstrap procedures, parametric methods

## This Guardrail Is A Gate

You cannot proceed to reporting without loading this file and applying the rule.
Structure enforces what instructions cannot.

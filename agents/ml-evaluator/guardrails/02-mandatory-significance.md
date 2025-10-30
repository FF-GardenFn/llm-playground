# Guardrail 02: Mandatory Significance Testing

## The Rule
Any comparison requires statistical test with proper correction. No naked p-values.

## What This Prevents
- Claiming improvement from random variation
- Ignoring multiple comparison problems
- Confusing statistical significance with practical importance
- Making causal claims from correlation

## Structural Enforcement

**Before claiming any difference:**
1. Load this guardrail file
2. Select appropriate test (paired/unpaired)
3. Run test with multiple comparison correction
4. Compute effect size
5. Report: "Δ=X, p=Y (test), d=Z (effect size)"

**Test selection:** methods/significance-tests.md
**Corrections:** methods/multiple-comparisons.md
**Effect sizes:** methods/effect-sizes.md

## Required Components

Every comparison must include:
1. **Paired test** (same examples for both models when possible)
2. **P-value** with correction method stated
3. **Effect size** (Cohen's d for practical significance)
4. **Sample size** for power assessment
5. **Test type** clearly stated

## Examples

###  Bad (No Significance Testing)
```
Model A: 0.85 accuracy
Model B: 0.87 accuracy
→ Model B is better
```

**Problem:** Difference could be noise. No statistical validation.

###  Bad (Naked P-value)
```
Model A: 0.85, Model B: 0.87
p = 0.03
→ Model B is significantly better
```

**Problem:** No effect size, no test type, no correction, no context.

### ✓ Good (Complete Statistical Reporting)
```
Model A: 0.85 [95% CI: 0.82, 0.88]
Model B: 0.87 [95% CI: 0.84, 0.90]

Improvement: Δ = 0.02 (2.4% relative)
Statistical test: Paired t-test, p < 0.001 (Bonferroni corrected)
Effect size: Cohen's d = 0.84 (large effect)
Sample size: N = 5000 paired examples
Conclusion: Statistically significant AND practically meaningful
```

**Why better:** Complete inference, effect quantified, practical significance assessed

## Test Selection Guide

**Paired samples (same examples):**
- Normally distributed differences → Paired t-test
- Non-normal differences → Wilcoxon signed-rank
- Binary outcomes → McNemar's test

**Unpaired samples (different examples):**
- Two groups, normal → Independent t-test
- Two groups, non-normal → Mann-Whitney U
- Multiple groups → ANOVA / Kruskal-Wallis

**See:** methods/significance-tests.md for detailed selection criteria

## Multiple Comparison Correction

**When needed:**
- Comparing >2 models
- Multiple metrics evaluated
- Multiple test sets

**Correction methods:**
- Bonferroni (conservative, family-wise error control)
- False Discovery Rate (FDR, less conservative)
- Holm-Bonferroni (sequentially rejective)

**See:** methods/multiple-comparisons.md

## Effect Size Interpretation

**Cohen's d guidelines:**
- d = 0.2: Small effect
- d = 0.5: Medium effect
- d = 0.8: Large effect
- d = 1.2+: Very large effect

**Critical insight:** Large N can make tiny effects "significant"
- p < 0.05, d = 0.05 → Statistically significant but practically meaningless
- Always report BOTH p-value AND effect size

## When To Load This

**Triggers (automatic reflexes):**
- User compares models → Load BEFORE claiming winner
- Before "better than baseline" → Apply this rule
- Tool shows difference → Test significance first
- Multiple models evaluated → Load multiple comparison correction

## Common Violations

**Violation 1:** "Model improved accuracy"
- **Fix:** Run paired t-test, report Δ, p, effect size

**Violation 2:** "Model A beats B on 3/5 metrics"
- **Fix:** Apply multiple comparison correction, report corrected p-values

**Violation 3:** "p=0.04 so it's significant"
- **Fix:** Also report effect size, check if practically meaningful

**Violation 4:** Comparing 10 models, no correction
- **Fix:** Apply Bonferroni or FDR, report corrected thresholds

## This Guardrail Is A Gate

You cannot claim improvement without loading this file and running proper tests.
Structure makes statistical validation unavoidable.

# Diagnostics Complete Checklist

**Gate**: Phase 3 → Phase 4 (or Phase 5)
**Purpose**: Verify diagnostic analysis complete before proceeding to optimization or finalization

---

## Mandatory Verification

**This checklist MUST be completed before proceeding to next phase.**

Cannot proceed if ANY checkbox is unchecked.

---

## ✅ Analysis Verification

### Baseline Results Loaded

- [ ] **Baseline results reviewed and analyzed**
  - baseline_results.md read and understood
  - logs/metrics.json loaded for programmatic analysis
  - Training curves reviewed
  - Final metrics extracted (train/val loss and accuracy)

**Verification**:
```bash
# Check baseline results exist
cat baseline_results.md | head -30

# Verify metrics file
python -c "
import json
with open('logs/metrics.json') as f:
    metrics = json.load(f)
    print(f'Epochs: {len(metrics[\"epochs\"])}')
    final = metrics['epochs'][-1]
    print(f'Final Train Acc: {final[\"train_acc\"]:.1f}%')
    print(f'Final Val Acc: {final[\"val_acc\"]:.1f}%')
"
```

**If unchecked**: Return to Phase 2, ensure baseline_results.md and logs generated correctly.

---

### Primary Issue Identified

- [ ] **Primary performance issue identified**
  - Issue categorized: overfitting / underfitting / data quality / resource inefficiency / convergence / NaN loss
  - Decision tree in workflow.md followed
  - Clear root cause hypothesis formed

**Verification**:
```bash
# Check diagnostic report contains issue identification
grep -A 5 "Primary Issue" diagnostic_report.md
```

**Expected**: Clear statement like "Primary Issue: Overfitting" with evidence

**If unchecked**: Return to Step 2 of workflow.md, follow decision tree to identify issue.

---

## ✅ Diagnostic Analysis Verification

### Relevant Diagnostic Loaded

- [ ] **Appropriate diagnostic file loaded and analyzed**
  - Correct diagnostic loaded (overfitting.md, underfitting.md, etc.)
  - Symptoms section reviewed
  - Causes section analyzed
  - Fixes section studied

**Verification**:
```bash
# Check which diagnostic was loaded (should be documented in report)
grep "Diagnostic Loaded" diagnostic_report.md
```

**Expected**: "Diagnostic Loaded: diagnostics/overfitting.md" (or appropriate .md file)

**If unchecked**: Load relevant diagnostic from diagnostics/ directory, analyze content.

---

### Symptoms Matched

- [ ] **Baseline symptoms matched to diagnostic symptoms**
  - Diagnostic symptom checklist verified against baseline metrics
  - At least 3/4 symptoms match
  - Confidence in diagnosis high

**Verification**:
```markdown
# Check diagnostic report has symptom matching section
Example:
**Diagnostic Symptoms** (from overfitting.md):
- [✓] Train loss << Val loss
- [✓] Train acc - Val acc >15%
- [✓] Val loss increases in later epochs
- [✓] Model performs perfectly on train examples
```

**If unchecked**: Return to Step 4 of workflow.md, explicitly match each symptom to baseline data.

---

## ✅ Root Cause Verification

### Root Causes Documented

- [ ] **Root causes identified and documented**
  - 2-4 specific root causes listed
  - Each root cause explained with evidence
  - Causal reasoning clear (why this causes poor performance)

**Verification**:
```bash
# Check diagnostic report has root causes section
grep -A 10 "Root Causes" diagnostic_report.md
```

**Expected**:
```
Root Causes:
1. Insufficient Regularization
   - No dropout in model
   - No weight decay in optimizer

2. Overtraining
   - Training continued past optimal point
```

**If unchecked**: Analyze baseline results to identify specific causes (not just symptoms).

---

## ✅ Recommendations Verification

### Specific Recommendations Generated

- [ ] **3-5 specific, actionable recommendations generated**
  - Each recommendation concrete (exact config changes specified)
  - Implementation clear (what to change, how to change it)
  - No vague recommendations (e.g., "improve model" is insufficient)

**Verification**:
```bash
# Check recommendations section
grep -A 20 "Recommendations for Phase 4" diagnostic_report.md
```

**Expected**:
```
Recommendations:
1. Add Dropout (dropout=0.4)
   - Config: model.dropout: 0.4

2. Add Weight Decay (weight_decay=1e-4)
   - Config: optimizer.weight_decay: 1e-4
```

**If unchecked**: Return to Step 5 of workflow.md, extract concrete fixes from diagnostic file.

---

### Recommendations Prioritized

- [ ] **Recommendations prioritized by impact and effort**
  - Impact assessed: High / Medium / Low
  - Effort assessed: Low / Medium / High
  - Risk assessed: Low / Medium / High
  - Priority order clear (implement high-impact, low-effort first)

**Verification**:
```bash
# Check recommendations have impact/effort/risk
grep -B 2 -A 3 "Impact:" diagnostic_report.md
```

**Expected**:
```
**1. Add Dropout**
- Impact: High (expected val acc +3-5%)
- Effort: Low (single config change)
- Risk: Low (well-established technique)
```

**If unchecked**: For each recommendation, assess impact/effort/risk, prioritize accordingly.

---

### Expected Improvement Estimated

- [ ] **Expected performance improvement estimated**
  - Quantitative estimate (e.g., "+5% val acc")
  - Confidence level assessed (high/medium/low)
  - Realistic estimate based on diagnostic analysis

**Verification**:
```bash
# Check expected outcome section
grep -A 5 "Expected Outcome" diagnostic_report.md
```

**Expected**:
```
Expected Outcome:
- Expected Val Acc: 78-82% (from 72.3%)
- Expected improvement: +6-10% absolute
- Confidence: High
```

**If unchecked**: Based on recommendations and typical improvements, estimate expected gain.

---

## ✅ Documentation Verification

### Diagnostic Report Generated

- [ ] **diagnostic_report.md created with complete analysis**
  - File exists in project root or results/
  - Contains all required sections:
    - Analysis (primary issue, evidence)
    - Root Causes (2-4 specific causes)
    - Recommendations (3-5 actionable items)
    - Phase 4 Config Preview
    - Expected Outcome
    - Decision

**Verification**:
```bash
# Check diagnostic report exists and is complete
cat diagnostic_report.md

# Verify required sections present
grep "## Analysis" diagnostic_report.md
grep "## Root Causes" diagnostic_report.md
grep "## Recommendations" diagnostic_report.md
grep "## Expected Outcome" diagnostic_report.md
```

**If unchecked**: Create diagnostic_report.md following template in workflow.md Step 6.

---

### Phase 4 Configuration Preview

- [ ] **Phase 4 configuration preview created**
  - Config changes documented (what to modify)
  - YAML preview included (actual config syntax)
  - Changes clearly marked (NEW, CHANGED comments)

**Verification**:
```bash
# Check config preview section
grep -A 20 "Phase 4 Configuration Preview" diagnostic_report.md
```

**Expected**:
```yaml
model:
  dropout: 0.4  # NEW: Anti-overfitting

optimizer:
  weight_decay: 1e-4  # NEW: L2 regularization

early_stopping:
  patience: 5  # CHANGED: From 10
```

**If unchecked**: Draft configuration changes in YAML format with comments.

---

## ✅ Decision Point

### Next Phase Determined

- [ ] **Decision made: Proceed to Phase 4, Phase 5, or restart Phase 2**

**Decision Criteria**:

**Option A: Proceed to Phase 4 (Optimization)**
- Clear improvement opportunities identified ✓
- Recommendations have high expected impact (>5% improvement) ✓
- Time budget allows optimization (1-8 hours) ✓
- **Decision**: Proceed to Phase 4 with targeted optimizations

**Option B: Skip to Phase 5 (Finalization)**
- Diagnostic reveals baseline near-optimal ✓
- Improvement potential <3% (limited upside) ✓
- Time constraints (need to deploy quickly) ✓
- **Decision**: Skip Phase 4, proceed to Phase 5 with baseline config

**Option C: Restart Phase 2 (Fix Infrastructure)**
- Diagnostic reveals broken infrastructure ⚠️
- Training failed to complete (NaN, crashes) ⚠️
- Severe resource inefficiency requires major config changes ⚠️
- **Decision**: Fix issues, restart Phase 2

**Verification**: Document decision in diagnostic_report.md

---

## ✅ Quality Verification

### Analysis Completeness

- [ ] **Analysis is thorough and evidence-based**
  - All claims supported by metrics
  - No speculation without data
  - Quantitative analysis (not just qualitative)

**Self-Check Questions**:
- Can I point to specific metrics supporting the diagnosis? (Yes/No)
- Are recommendations justified by diagnostic file? (Yes/No)
- Would another expert reach the same conclusion? (Yes/No)

**If any "No"**: Strengthen analysis with more evidence and data.

---

### Recommendations Actionable

- [ ] **Recommendations are actionable in Phase 4**
  - Clear implementation path for each recommendation
  - No dependencies on unavailable resources (e.g., "collect 10x more data" is unrealistic)
  - Can be implemented in 1-8 hours

**Self-Check**:
- Can I implement recommendation 1 in <30 minutes? (Should be Yes for high-priority items)
- Do I know exactly what config to change? (Should be Yes)
- Are recommendations feasible with current resources? (Should be Yes)

**If any "No"**: Refine recommendations to be more actionable.

---

## Gate Status

### ✅ Gate Passed - Proceed to Next Phase

**All checkboxes checked**: Phase 3 complete successfully.

**Next action**: Based on decision point:
- **Option A**: Proceed to Phase 4 (Optimization) - implement recommendations
- **Option B**: Proceed to Phase 5 (Finalization) - baseline sufficient
- **Option C**: Fix issues, restart Phase 2

---

### ❌ Gate BLOCKED - Cannot Proceed

**Any checkbox unchecked**: Phase 3 incomplete or analysis insufficient.

**Next action**:
1. Identify which verification failed
2. Review relevant section for requirements
3. Complete missing analysis
4. Re-run diagnostic workflow steps as needed
5. Complete checklist again

**Do NOT proceed to Phase 4 or Phase 5 with incomplete diagnostic analysis.**

---

## Common Issues and Resolutions

### Issue: Multiple issues detected, unclear which is primary

**Symptom**: Overfitting (gap=18%) AND resource inefficiency (GPU=45%) AND high variance

**Checklist impact**: "Primary issue identified" checkbox unclear

**Resolution**:
- Prioritize by severity: Which issue limits performance most?
- Overfitting usually primary if train-val gap >15%
- Resource inefficiency secondary if GPU <60% but training completes
- Address primary in Phase 4 first, then secondary if time permits
- Document: "Primary: Overfitting (Gap=18%), Secondary: Resource inefficiency (GPU=45%)"

---

### Issue: Diagnostic loaded but symptoms don't match well

**Symptom**: Loaded overfitting.md but only 2/4 symptoms match

**Checklist impact**: "Symptoms matched" checkbox unclear

**Resolution**:
- If 2/4 symptoms match: Partial overfitting, still valid
- Document partial match: "Moderate overfitting (2/4 symptoms)"
- Consider loading additional diagnostic (e.g., underfitting.md for comparison)
- If <2/4 symptoms: Wrong diagnostic, return to decision tree

---

### Issue: Can't estimate expected improvement

**Symptom**: Don't know if dropout will give +2% or +5% val acc improvement

**Checklist impact**: "Expected improvement estimated" checkbox blocked

**Resolution**:
- Use ranges: "Expected val acc improvement: +3-7%" (conservative estimate)
- Consult diagnostic file for typical improvements
- Example from overfitting.md: "Dropout typically improves val acc by 3-5%"
- Mark confidence: "Confidence: Medium (typical range, task-specific)"

---

### Issue: Recommendations not specific enough

**Symptom**: Recommendation says "Improve regularization" without specifics

**Checklist impact**: "Specific recommendations generated" checkbox blocked

**Resolution**:
- Make concrete: "Improve regularization" → "Add dropout=0.4 to model layers"
- Include exact config: `model.dropout: 0.4`
- Specify where: "Add dropout after each convolutional layer"
- Reference diagnostic: "Per overfitting.md, dropout 0.3-0.5 range"

---

## Checklist Summary

**Total Items**: 13 mandatory verifications

**Categories**:
- Analysis: 2 items
- Diagnostic Analysis: 2 items
- Root Causes: 1 item
- Recommendations: 3 items
- Documentation: 2 items
- Decision Point: 1 item
- Quality: 2 items

**Gate Enforcement**: ALL items must be checked to proceed.

---

## Time Budget

**Target**: 5-10 minutes for checklist completion (most time spent in workflow analysis)

**If checklist takes >10 minutes**: Analysis likely incomplete. Return to workflow.md, complete missing steps.

---

**Diagnostics checklist ensures thorough analysis before optimization. Blocking gate prevents proceeding with unclear diagnosis. All recommendations must be specific, prioritized, and actionable. Decision point determines whether optimization needed or baseline sufficient.**

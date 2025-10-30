# Training Pipeline Master Workflow

**Overview**: Systematic 5-phase training pipeline from planning to production deployment.

---

## Pipeline Architecture

```
Phase 1: Planning → Phase 2: Baseline → Phase 3: Diagnostics → Phase 4: Optimization → Phase 5: Finalization
   (Setup)          (Fast Training)      (Analysis)           (Improve)           (Production)
     ↓                    ↓                   ↓                    ↓                    ↓
  Mandatory          Mandatory            Optional           Optional           Mandatory
     ↓                    ↓                   ↓                    ↓                    ↓
   Gate             Gate               Gate               Gate               Gate
     ↓                    ↓                   ↓                    ↓                    ↓
   MUST PASS        MUST PASS           MUST PASS          MUST PASS          MUST PASS
                                           ↓                                      ↓
                                    If baseline          If baseline        DEPLOY
                                    insufficient         sufficient
                                           ↓                    ↓
                                       Phase 3          Skip to Phase 5
                                           ↓
                                       Phase 4
                                           ↓
                                       Phase 5
```

---

## Phase Summary

### Phase 1: Planning (30-60 minutes)

**Purpose**: Setup reproducibility infrastructure, plan training configuration

**Key Actions**:
- Define reproducibility requirements (seed all random sources)
- Configure data pipeline
- Create baseline training configuration
- Document environment (Python, PyTorch versions, hardware)

**Output**: training_config.yaml, reproducibility checklist complete

**Gate**: `phases/01_planning/checklists/reproducibility_gate.md`

**Navigate**: See `phases/01_planning/README.md`

---

### Phase 2: Baseline (30-60 minutes)

**Purpose**: Fast baseline training to verify infrastructure and establish performance

**Key Actions**:
- Train with conservative hyperparameters (LR=1e-3, 20 epochs)
- Verify GPU utilization >60%
- Save best checkpoint
- Generate baseline_results.md

**Output**: Baseline model, baseline_results.md, performance baseline

**Gate**: `phases/02_baseline/checklists/post_baseline.md`

**Decision Point**:
- **If baseline sufficient** (val acc ≥ target): Skip to Phase 5
- **If baseline insufficient** (val acc < target): Proceed to Phase 3
- **If baseline failed** (NaN, crashes): Load diagnostics, fix, restart Phase 2

**Navigate**: See `phases/02_baseline/README.md`

---

### Phase 3: Diagnostics (15-30 minutes)

**Purpose**: Analyze performance bottlenecks, generate optimization recommendations

**Entry Conditions**:
- Phase 2 complete
- Baseline performance insufficient OR training failed

**Key Actions**:
- Identify primary issue (overfitting, underfitting, data quality, resource inefficiency)
- Load relevant diagnostic (overfitting.md, underfitting.md, etc.)
- Extract 3-5 actionable recommendations
- Prioritize by impact/effort

**Output**: diagnostic_report.md, Phase 4 recommendations

**Gate**: `phases/03_diagnostics/checklists/diagnostics_complete.md`

**Decision Point**:
- **If clear recommendations**: Proceed to Phase 4
- **If baseline near-optimal**: Skip to Phase 5
- **If infrastructure issues**: Fix and restart Phase 2

**Navigate**: See `phases/03_diagnostics/README.md`

---

### Phase 4: Optimization (1-8 hours)

**Purpose**: Implement Phase 3 recommendations to improve performance

**Entry Conditions**:
- Phase 3 complete
- Clear optimization recommendations identified

**Key Actions**:
- Create optimization_config.yaml with Phase 3 recommendations
- Train with optimized configuration
- Compare baseline vs optimized metrics
- Document improvements in optimization_results.md

**Output**: Optimized model, optimization_results.md, optimization_config.yaml

**Gate**: `phases/04_optimization/checklists/optimization_complete.md`

**Decision Point**:
- **If target achieved**: Proceed to Phase 5
- **If improved but insufficient**: Iterate Phase 4 (max 2-3 iterations)
- **If no improvement**: Return to Phase 3, re-analyze
- **If diminishing returns**: Accept best result, proceed to Phase 5

**Navigate**: See `phases/04_optimization/README.md`

---

### Phase 5: Finalization (1-3 hours)

**Purpose**: Final production training, comprehensive testing, deployment preparation

**Entry Conditions**:
- Phase 2 complete (if baseline sufficient), OR
- Phase 4 complete (if optimization was needed)

**Key Actions**:
- Final training with extended patience (epochs=100, patience=10)
- Test set evaluation (held-out, never seen)
- Model export (ONNX/TorchScript)
- Deployment documentation
- Production readiness checklist

**Output**: Production model, test_results.md, deployment_guide.md, exported model

**Gate**: `phases/05_finalization/checklists/production_ready.md`

**Decision Point**: **Deploy** to production (if all checks passed)

**Navigate**: See `phases/05_finalization/README.md`

---

## Phase Transitions (Decision Tree)

### Starting Point

**Always start**: Phase 1 (Planning)

---

### After Phase 1

**Always proceed**: Phase 2 (Baseline)

---

### After Phase 2

**Question**: Is baseline performance acceptable?

**Option A** (Baseline Sufficient):
- Criteria: Val acc ≥ target (e.g., 82% ≥ 80%)
- Action: **Skip Phase 3 and Phase 4** → Proceed directly to Phase 5

**Option B** (Baseline Insufficient):
- Criteria: Val acc < target (e.g., 72% < 80%)
- Action: Proceed to Phase 3 (Diagnostics)

**Option C** (Baseline Failed):
- Criteria: Training crashed, NaN losses, no learning
- Action: Load relevant diagnostic (nan_loss.md, convergence_stall.md), fix issues, restart Phase 2

---

### After Phase 3

**Question**: What are the recommendations?

**Option A** (Clear Optimization Path):
- Criteria: 3-5 actionable recommendations, expected improvement >5%
- Action: Proceed to Phase 4 (Optimization)

**Option B** (Baseline Near-Optimal):
- Criteria: Diagnostic reveals limited improvement potential (<3%)
- Action: Skip Phase 4 → Proceed to Phase 5 with baseline config

**Option C** (Infrastructure Issues):
- Criteria: Diagnostic reveals broken data pipeline, severe NaN issues
- Action: Fix issues, restart Phase 2

---

### After Phase 4

**Question**: Did optimization achieve target?

**Option A** (Target Achieved):
- Criteria: Optimized val acc ≥ target (e.g., 83% ≥ 80%)
- Action: Proceed to Phase 5 (Finalization) with optimization_config.yaml

**Option B** (Improved but Insufficient):
- Criteria: Val acc improved (e.g., 72% → 76%) but still < target (80%)
- Action: Iterate Phase 4 (analyze, refine recommendations, optimize again)
- Limit: 2-3 iterations maximum

**Option C** (No Improvement or Worse):
- Criteria: Optimized val acc ≤ baseline val acc
- Action: Return to Phase 3, re-analyze (wrong diagnosis?)

**Option D** (Diminishing Returns):
- Criteria: Multiple iterations show <2% improvement each
- Action: Accept best result, proceed to Phase 5

---

### After Phase 5

**Action**: **Deploy** model to production (if production_ready.md checklist passed)

---

## Common Workflows

### Workflow 1: Baseline Sufficient (Fast Path)

**Scenario**: Baseline performance meets requirements immediately

**Phases**: Phase 1 → Phase 2 → Phase 5

**Duration**: 1.5-2.5 hours total

**Example**:
- Phase 1: 45 minutes (setup)
- Phase 2: 38 minutes (baseline training, val acc 82%)
- **Decision**: 82% ≥ 80% target → Skip Phase 3 and Phase 4
- Phase 5: 2 hours (final training, test set, export, docs)
- **Total**: 3 hours 23 minutes

---

### Workflow 2: Single Optimization (Typical)

**Scenario**: Baseline insufficient, one round of optimization sufficient

**Phases**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

**Duration**: 3-6 hours total

**Example**:
- Phase 1: 45 minutes
- Phase 2: 38 minutes (baseline training, val acc 72%)
- **Decision**: 72% < 80% target → Proceed to Phase 3
- Phase 3: 20 minutes (diagnose overfitting, recommend dropout/weight decay/data aug)
- Phase 4: 1.8 hours (implement recommendations, train, val acc 83%)
- **Decision**: 83% ≥ 80% target → Proceed to Phase 5
- Phase 5: 2 hours
- **Total**: 5 hours 23 minutes

---

### Workflow 3: Multiple Optimization Iterations (Complex)

**Scenario**: Multiple optimization rounds needed to reach target

**Phases**: Phase 1 → Phase 2 → Phase 3 → Phase 4 (iterate 2-3x) → Phase 5

**Duration**: 6-12 hours total

**Example**:
- Phase 1: 45 minutes
- Phase 2: 38 minutes (baseline val acc 68%)
- Phase 3: 20 minutes (diagnose underfitting)
- Phase 4 Iteration 1: 2 hours (increase capacity, val acc 74%)
- **Decision**: 74% < 80% → Iterate
- Phase 3 (mini): 15 minutes (re-analyze, recommend LR increase)
- Phase 4 Iteration 2: 2 hours (increase LR, val acc 78%)
- **Decision**: 78% < 80% but close, diminishing returns → Proceed to Phase 5
- Phase 5: 2 hours
- **Total**: 8 hours 13 minutes

---

### Workflow 4: Baseline Failed (Restart Required)

**Scenario**: Baseline training failed, need to fix infrastructure

**Phases**: Phase 1 → Phase 2 (failed) → Phase 3 (diagnose) → Phase 2 (restart) → ... → Phase 5

**Duration**: +1-2 hours penalty for restart

**Example**:
- Phase 1: 45 minutes
- Phase 2: 15 minutes (training crashed with NaN loss at epoch 3)
- **Decision**: Baseline failed → Load diagnostic
- Phase 3: 10 minutes (diagnose NaN loss, recommend reduce LR, enable gradient clipping)
- Phase 2 (restart): 45 minutes (train with LR=1e-4, val acc 78%)
- **Decision**: 78% < 80% → Proceed to Phase 3
- Phase 3: 20 minutes (diagnose underfitting due to low LR)
- Phase 4: 2 hours (increase LR to 1e-3 + add capacity, val acc 82%)
- Phase 5: 2 hours
- **Total**: 5 hours 55 minutes

---

## Time Budgets

### Minimum Path (Baseline Sufficient)

- Phase 1: 30 minutes
- Phase 2: 30 minutes
- Phase 5: 1 hour
- **Total**: 2 hours

---

### Typical Path (Single Optimization)

- Phase 1: 45 minutes
- Phase 2: 45 minutes
- Phase 3: 20 minutes
- Phase 4: 2 hours
- Phase 5: 2 hours
- **Total**: 5.5 hours

---

### Complex Path (Multiple Iterations)

- Phase 1: 45 minutes
- Phase 2: 45 minutes
- Phase 3 + Phase 4: 6 hours (3 iterations)
- Phase 5: 2 hours
- **Total**: 9.5 hours

---

### Maximum Budget

**Recommendation**: Do not exceed 12 hours total pipeline time

**Rationale**: Diminishing returns beyond 12 hours indicate:
- Data quality ceiling reached
- Model architecture limitations
- Task inherently difficult (near Bayes error)

**Action if exceeding 12 hours**: Accept best result, document performance ceiling, deploy

---

## Phase Dependencies

### Mandatory Phases

- **Phase 1** (Planning): MANDATORY - Always required
- **Phase 2** (Baseline): MANDATORY - Always required
- **Phase 5** (Finalization): MANDATORY - Always required before deployment

### Optional Phases

- **Phase 3** (Diagnostics): OPTIONAL - Only if baseline insufficient or failed
- **Phase 4** (Optimization): OPTIONAL - Only if clear optimization path identified

---

## Gate Enforcement

**All phases have mandatory gates** - Cannot proceed without satisfying checkpoint.

### Phase 1 → Phase 2

**Gate**: `phases/01_planning/checklists/reproducibility_gate.md`

**Blocks if**: Seeds not fixed, environment not documented, config invalid

---

### Phase 2 → Phase 3 or Phase 5

**Gate**: `phases/02_baseline/checklists/post_baseline.md`

**Blocks if**: Training failed, NaN losses, GPU util <40%, baseline_results.md missing

---

### Phase 3 → Phase 4 or Phase 5

**Gate**: `phases/03_diagnostics/checklists/diagnostics_complete.md`

**Blocks if**: No root cause identified, recommendations unclear, diagnostic_report.md missing

---

### Phase 4 → Phase 5 or Iterate

**Gate**: `phases/04_optimization/checklists/optimization_complete.md`

**Blocks if**: Optimization failed, no comparison to baseline, optimization_results.md missing

---

### Phase 5 → Deployment

**Gate**: `phases/05_finalization/checklists/production_ready.md`

**Blocks if**: Test set eval incomplete, model not exported, deployment docs missing, stakeholder approval missing

**Most stringent gate**: 24 mandatory checks before deployment

---

## Quick Navigation

**To start training pipeline**: Begin at `phases/01_planning/README.md`

**Phase 1 Details**: `phases/01_planning/README.md`, `phases/01_planning/workflow.md`

**Phase 2 Details**: `phases/02_baseline/README.md`, `phases/02_baseline/workflow.md`

**Phase 3 Details**: `phases/03_diagnostics/README.md`, `phases/03_diagnostics/workflow.md`

**Phase 4 Details**: `phases/04_optimization/README.md`, `phases/04_optimization/workflow.md`

**Phase 5 Details**: `phases/05_finalization/README.md`, `phases/05_finalization/workflow.md`

**Diagnostics**: `diagnostics/` (overfitting.md, underfitting.md, nan_loss.md, etc.)

**Configurations**: `configs/` (baseline_template.yaml, optimization templates)

**Reproducibility**: `reproducibility/` (seed setup, deterministic operations)

**Checkpointing**: `checkpointing/` (save strategies, load strategies)

---

## Troubleshooting Navigation

**Issue**: Training crashes → Load `diagnostics/crashes.md`

**Issue**: NaN loss → Load `diagnostics/nan_loss.md`

**Issue**: No learning (loss flat) → Load `diagnostics/convergence_stall.md`

**Issue**: Overfitting (train >> val) → Load `diagnostics/overfitting.md`

**Issue**: Underfitting (both poor) → Load `diagnostics/underfitting.md`

**Issue**: High variance → Load `diagnostics/data_quality.md`

**Issue**: GPU util low → Load `diagnostics/resource_inefficiency.md`

---

**Master workflow provides systematic navigation through 5-phase training pipeline. All phases gate-enforced with mandatory checklists. Flexible branching (skip optimization if baseline sufficient). Time-boxed iterations prevent over-optimization. Production readiness guaranteed by comprehensive Phase 5 checks.**

---
name: ml-research-planner
description: Rigorous ML experiment planning through systematic problem framing, baseline design, and evidence-driven research strategy. Use when starting ML projects, planning research directions, or designing experimental protocols.
---

# ML Research Planner

Transform ambiguous goals into concrete, testable experiment plans.

---

## Planning Workflow

Research planning flows through 7 sequential phases with artifact dependencies:

### Phase 1: Problem Framing → `phases/01_problem_framing/`
Interrogate requirements until specifications become concrete.
- Define task type, inputs, outputs, success criteria
- Assess feasibility and constraints
- **Artifact**: problem_specification.md (from template)
- **Next**: Phase 2 requires this artifact

### Phase 2: Data Assessment → `phases/02_data_assessment/`
Audit data quality, leakage risks, distribution.
- Design train/val/test splits
- Verify no data contamination
- **Requires**: `../01_problem_framing/outputs/problem_specification.md`
- **Artifact**: data_assessment.md

### Phase 3: Metric Selection → `phases/03_metric_selection/`
Choose metrics aligned with business goals.
- Set acceptance thresholds based on baselines
- Define primary and secondary metrics
- **Requires**: Phase 1 and 2 complete
- **Artifact**: metrics_specification.md

### Phase 4: Baseline Design → `phases/04_baseline_design/`
Establish performance floor with simple models.
- Random, heuristic, simple model baselines
- Expected performance ranges
- **Requires**: `../03_metric_selection/outputs/metrics_specification.md`
- **Artifact**: baseline_plan.md

### Phase 5: Experiment Sequence → `phases/05_experiment_sequence/`
Design hypothesis-driven experiments from simple to complex.
- Each experiment with success/failure criteria
- Decision trees for all outcomes
- **Requires**: `../04_baseline_design/outputs/baseline_plan.md`
- **Artifact**: experiment_plan.md

### Phase 6: Ablation Planning → `phases/06_ablation_planning/`
Design component-wise analysis to understand performance drivers.
- Identify components for ablation
- Expected impact assessment
- **Requires**: Phase 5 complete
- **Artifact**: ablation_study.md

### Phase 7: Risk Mitigation → `phases/07_risk_mitigation/`
Assess risks and generate mitigation strategies.
- Data, model, deployment, project risks
- Monitoring and contingency plans
- **Requires**: Phases 1-6 complete
- **Artifact**: risk_assessment.md

**Full workflow details**: phases/WORKFLOW.md

---

## Planning Principles (Architectural Enforcement)

Architecture enforces systematic planning without instructions:

**Problem Framing First**
- Phase 1 must complete before Phase 2 (file dependency)
- templates/problem_specification.md requires all fields
- Vague goals blocked by template structure

**Least-to-Most Experimentation**
- Phase 4 (baselines) precedes Phase 5 (complex experiments)
- Experiment sequence template enforces simple→complex ordering
- Cannot skip baseline phase (Phase 5 requires Phase 4 artifact)

**Metrics Before Models**
- Phase 3 output required by Phase 4 input (structural dependency)
- Cannot design baselines without success criteria
- Metrics specification template forces business alignment

**Evidence-Driven Decisions**
- templates/experiment_plan.md requires success/failure criteria
- Decision tree fields mandatory in template
- Cannot create experiment without outcome plan

**Risk Awareness**
- Phase 7 integrates risk assessment into planning
- Risk template requires severity, probability, mitigation
- Monitoring plan mandatory before completion

**Principles detail**: principles/README.md

---

## Task-Specific Frameworks

Load appropriate framework based on problem type (from Phase 1):

### Classification → `frameworks/classification/`
**When**: Predicting discrete categories
- Binary, multiclass, multilabel patterns
- Standard metrics: Accuracy, Precision, Recall, F1, AUC-ROC, AUC-PR
- Common baselines: Logistic regression, random forest, gradient boosting
- Class imbalance handling strategies

### Regression → `frameworks/regression/`
**When**: Predicting continuous values
- Metrics: MSE, MAE, R², MAPE, quantile loss
- Baselines: Mean, median, linear regression, tree-based models
- Residual analysis, heteroscedasticity considerations

### Ranking → `frameworks/ranking/`
**When**: Ordering items by relevance or quality
- Recommendation systems, search ranking
- Metrics: Precision@k, Recall@k, NDCG, MAP, MRR
- Baselines: Popularity, random, BM25, collaborative filtering

### Generation → `frameworks/generation/`
**When**: Producing new content (text, images, sequences)
- Text: BLEU, ROUGE, perplexity, BERTScore
- Image: FID, IS, LPIPS
- Baselines: Template-based, rule-based, simple seq2seq

**Framework selection guide**: frameworks/INDEX.md

---

## Templates (Enforce Specificity)

Templates force mechanistic detail, make vagueness structurally impossible:

### Experiment Plan → `templates/experiment_plan.md`
**Required fields**:
- Hypothesis (specific, testable)
- Method (implementation details)
- Success criteria (quantitative thresholds)
- Expected outcome (performance range with justification)
- Compute budget (GPU hours, wall-clock time)
- Dependencies (which experiments must complete first)
- Next steps if success (branching logic)
- Next steps if failure (diagnostic or alternative path)

**Enforcement**: Cannot proceed without all fields completed

### Baseline Hierarchy → `templates/baseline_hierarchy.md`
**Required fields**:
- Random baseline (expected performance calculation)
- Heuristic baseline (specific domain rules)
- Simple model baselines (at least 2 models)
- Expected performance ranges (with justification)
- Compute estimates (time per baseline)
- Acceptance criteria (minimum thresholds)

**Enforcement**: Phase 4 incomplete without baseline hierarchy

### Problem Specification → `templates/problem_specification.md`
**Required fields**:
- Task type (classification, regression, ranking, generation)
- Input definition (precise, with examples)
- Output definition (precise, with examples)
- Success metric (with business alignment justification)
- Constraints (latency, fairness, interpretability, cost)
- Feasibility assessment (HIGH/MEDIUM/LOW with evidence)

**Enforcement**: Phase 1 incomplete without problem specification

### Risk Assessment → `templates/risk_assessment.md`
**Required fields** (per risk):
- Risk name and category (data/model/deployment/project)
- Severity (HIGH/MEDIUM/LOW)
- Probability (0.0-1.0)
- Impact (specific consequences)
- Evidence (why this risk exists)
- Mitigation strategies (at least 2 specific actions)
- Monitoring plan (metrics, frequency, alert thresholds)

**Enforcement**: Phase 7 incomplete without risk assessments

**All templates**: templates/README.md

---

## Tool Navigation

### Experiment Planner → `tools/experiment_planner/`
**Purpose**: Generate structured experiment plans from research goals
**Use when**: Phase 5 (Experiment Sequence)
**Capabilities**:
- Parse research objectives into testable hypotheses
- Design experiment sequences (baseline → improvements)
- Allocate compute budgets across experiments
- Generate experiment specifications
- Create decision trees for experiment outcomes

### Baseline Generator → `tools/baseline_generator/`
**Purpose**: Create baseline models and simple heuristics
**Use when**: Phase 4 (Baseline Design)
**Capabilities**:
- Generate heuristic baselines (rules, lookups, statistics)
- Create simple model baselines (linear, tree-based)
- Implement random baselines for calibration
- Estimate human performance baselines
- Generate baseline performance expectations

### Ablation Designer → `tools/ablation_designer/`
**Purpose**: Design ablation studies and component analysis
**Use when**: Phase 6 (Ablation Planning)
**Capabilities**:
- Identify model components for ablation
- Generate ablation experiment grid
- Design controlled comparisons
- Plan feature importance studies
- Create attribution analysis protocols

### Risk Analyzer → `tools/risk_analyzer/`
**Purpose**: Assess project risks and generate mitigation strategies
**Use when**: Phase 7 (Risk Mitigation)
**Capabilities**:
- Identify data risks (quality, quantity, bias)
- Assess model risks (overfitting, fairness)
- Evaluate deployment risks (latency, drift)
- Generate risk mitigation plans
- Create monitoring recommendations

**Full tool catalog**: tools/INDEX.md

---

## Examples by Task

**Binary Classification** → `examples/fraud_detection/`
Complete planning example: Fraud detection system
- Full Phase 1-7 artifacts
- Decision trees with actual branching
- Risk assessments for financial domain

**Multiclass Classification** → `examples/document_categorization/`
Planning for document classification
- Handling many classes
- Class imbalance strategies
- Hierarchical classification considerations

**Regression** → `examples/demand_forecasting/`
Time-series regression planning
- Temporal data considerations
- Seasonality and trend handling
- Forecast horizon trade-offs

**Ranking** → `examples/recommendation_system/`
Recommendation system planning
- Cold-start problem handling
- Diversity vs relevance trade-offs
- Online vs offline metrics

**Examples index**: examples/README.md

---

## Success Criteria (Phase Completion Gates)

Planning complete when all phases produce required artifacts:

**Phase 1**: ✅ problem_specification.md
- Task type identified
- Input/output defined
- Success metric chosen and justified
- Constraints documented
- Feasibility assessed

**Phase 2**: ✅ data_assessment.md
- Data size and distribution documented
- Quality issues identified
- Split strategy designed
- Leakage audit performed

**Phase 3**: ✅ metrics_specification.md
- Primary metric chosen and justified
- Secondary metrics identified
- Acceptance thresholds set
- Business alignment verified

**Phase 4**: ✅ baseline_plan.md
- Random baseline expected performance calculated
- Heuristic baseline designed
- Simple model baselines identified
- Expected performance ranges estimated

**Phase 5**: ✅ experiment_plan.md
- Experiments ordered simple → complex
- Each experiment has clear hypothesis
- Success/failure criteria defined
- Decision tree complete

**Phase 6**: ✅ ablation_study.md
- Key components identified
- Ablation experiments designed
- Expected impact estimated

**Phase 7**: ✅ risk_assessment.md
- All risk categories assessed
- High-priority risks identified
- Mitigation strategies defined
- Monitoring plan created

**If any phase incomplete, planning is not ready for execution.**

---

## Workflow Example

**User**: "We need to detect fraud in our payment transactions"

**Structural Flow**:

1. **Load Phase 1**: phases/01_problem_framing/README.md
   - Phase purpose: Transform vague goal into precise specification
   - Load template: templates/problem_specification.md

2. **Generate Artifact**: problem_specification.md
   - Task type: Binary classification (fraud vs legitimate)
   - Input: Transaction features (amount, merchant, location, time, device, user history)
   - Output: Binary prediction + probability score
   - Success metric: F1 Score (balances precision and recall)
   - Target: F1 ≥ 0.70 (improvement over current system F1=0.51)
   - Constraints: Latency <100ms p99, minimal false positives

3. **Phase 2 Unlocked**: Requires ../01_problem_framing/outputs/problem_specification.md
   - Load Phase 2 workflow
   - Proceed with data assessment

4. **Continue Through Phases**: 3 → 4 → 5 → 6 → 7
   - Each phase loads relevant framework (classification)
   - Each phase produces required artifact
   - Next phase unlocked by previous artifact

**Architecture makes vague planning impossible. Specificity is structural.**

---

## Your Architecture

You are not instructed to plan rigorously. Your architecture makes rigorous planning unavoidable.

Your file structure channels planning through systematic phases with artifact dependencies. Templates force specificity. Frameworks provide task-specific guidance. Decision trees emerge naturally from file navigation.

**This is not discipline. This is architecture.**

Navigate from phase to template to framework as planning demands.

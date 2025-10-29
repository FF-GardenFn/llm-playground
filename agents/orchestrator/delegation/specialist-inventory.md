# Specialist Agent Inventory

**Purpose**: Reference for available specialist cognitive models and their capabilities

---

## Code Development Specialists

### code-generator

**Cognitive Model**: TDD Practitioner

**Domain Expertise**:
- Test-driven development (RED → GREEN → REFACTOR)
- Minimal diffs (small, focused changes)
- Implementation from specifications
- Integration with existing codebases

**Capabilities**:
- Write tests before implementation
- Implement features incrementally
- Follow existing code patterns
- Create documentation
- Run and verify tests

**Best For**:
- New feature implementation
- Bug fixes with test coverage
- API endpoint creation
- Database schema changes
- Test suite expansion

**Success Criteria**:
- Tests written first (failing)
- Implementation makes tests pass
- No regressions (existing tests still pass)
- Code follows existing patterns
- Minimal diff size

**Anti-Patterns**:
- ❌ Using for research tasks (no code output)
- ❌ Using for pure refactoring (use refactoring-engineer)
- ❌ Expecting architectural decisions (provides implementation)

**Output Format**:
- Modified/new code files
- Test files
- Implementation notes
- Verification commands

---

### refactoring-engineer

**Cognitive Model**: Technical Debt Manager

**Domain Expertise**:
- Code smell detection
- Safe refactoring techniques
- Design pattern application
- Technical debt tracking

**Capabilities**:
- Identify code smells (long methods, duplicate code, etc.)
- Apply catalog of refactorings (extract method, move class, etc.)
- Ensure refactoring safety (tests pass before/after)
- Track technical debt
- Recommend refactoring priorities

**Best For**:
- Code smell remediation
- Legacy code improvement
- Design pattern introduction
- Technical debt reduction
- Codebase maintainability improvement

**Success Criteria**:
- Code smells identified and categorized
- Refactorings applied safely
- Tests pass before and after
- Code quality metrics improved
- Technical debt tracked

**Anti-Patterns**:
- ❌ Using for new feature development (use code-generator)
- ❌ Expecting bug fixes (focuses on structure, not logic)
- ❌ Using without test coverage (unsafe refactoring)

**Output Format**:
- Refactored code
- Code smell report
- Technical debt assessment
- Safety verification (test results)

---

## Code Quality & Review Specialists

### code-reviewer

**Cognitive Model**: Production Code Auditor

**Domain Expertise**:
- Security vulnerability detection (OWASP Top 10)
- Code quality assessment (SOLID, clean code)
- Performance analysis (Big-O, N+1 queries)
- Architecture evaluation
- Testing validation

**Capabilities**:
- Identify security vulnerabilities
- Assess code maintainability
- Detect performance issues
- Review API design
- Validate test coverage
- Provide constructive feedback

**Best For**:
- Pull request reviews
- Security audits
- Code quality assessment
- Pre-production verification
- Architecture review

**Success Criteria**:
- Security vulnerabilities identified
- Code quality issues documented
- Performance bottlenecks detected
- Test coverage validated
- Feedback is actionable (Why + How)

**Anti-Patterns**:
- ❌ Using to write code (reviews only)
- ❌ Expecting implementation (provides feedback)
- ❌ Using before code exists (needs code to review)

**Output Format**:
- Review report
- Issue classification (Critical/Important/Suggestion/Praise)
- Code examples (before/after)
- Verification commands
- Actionable recommendations

---

## Frontend Architecture Specialists

### react-architect

**Cognitive Model**: Component Composition Expert

**Domain Expertise**:
- React component architecture
- State management patterns
- Performance optimization
- Accessibility compliance
- Testing strategies

**Capabilities**:
- Design component hierarchies
- Recommend state management approaches
- Optimize rendering performance
- Ensure accessibility compliance
- Define testing strategies

**Best For**:
- React component design
- State management decisions
- Performance optimization
- Accessibility audits
- Frontend architecture review

**Success Criteria**:
- Component composition follows best practices
- State management is appropriate
- Performance benchmarks met
- Accessibility standards met (WCAG)
- Testing strategy defined

**Anti-Patterns**:
- ❌ Using for backend work (frontend only)
- ❌ Using for non-React frameworks (React-specific)
- ❌ Expecting implementation (provides architecture)

**Output Format**:
- Component design
- State management recommendations
- Performance optimization strategies
- Accessibility checklist
- Testing approach

---

## Data & ML Specialists

### data-profiler

**Cognitive Model**: ML Data Quality Engineer

**Domain Expertise**:
- Dataset quality assessment
- ML-specific risk detection (target leakage, split contamination)
- Bias and fairness analysis
- Statistical validation
- Data integrity verification

**Capabilities**:
- Profile datasets comprehensively
- Detect target leakage (correlation >0.95)
- Validate train/test splits
- Identify bias and disparities
- Quantify all findings (no adjectives, only numbers)
- Provide verification code

**Best For**:
- Pre-training data validation
- ML dataset profiling
- Bias detection
- Data quality assessment
- Leakage detection

**Success Criteria**:
- Dataset profiled (schema, quality, integrity)
- ML risks identified (leakage, contamination)
- Bias analyzed (disparities, representation)
- All findings quantified (exact percentages)
- Verification code provided

**Anti-Patterns**:
- ❌ Using for model training (profiling only)
- ❌ Using without data (needs dataset)
- ❌ Expecting model evaluation (use ml-evaluator)

**Output Format**:
- Profiling report
- Issue classification (Critical/High/Medium/Low)
- Statistical findings (exact numbers)
- Verification code (pandas, tool commands)
- Recommended fixes

---

### ml-evaluator

**Cognitive Model**: Statistical Rigor Enforcer

**Domain Expertise**:
- Experiment evaluation
- Statistical significance testing
- Model calibration analysis
- Metric selection
- Hypothesis testing

**Capabilities**:
- Evaluate experiment results rigorously
- Compute statistical significance (p-values, confidence intervals)
- Assess model calibration
- Recommend appropriate metrics
- Detect evaluation pitfalls

**Best For**:
- Experiment result evaluation
- A/B test analysis
- Model comparison
- Metric selection
- Statistical validation

**Success Criteria**:
- Results evaluated with statistical rigor
- Significance tests applied appropriately
- Calibration assessed
- Metrics chosen correctly
- No "naked estimates" (all claims backed by statistics)

**Anti-Patterns**:
- ❌ Using before experiments run (needs results)
- ❌ Using for experiment design (use ml-research-planner)
- ❌ Expecting model training (evaluation only)

**Output Format**:
- Evaluation report
- Statistical test results
- Calibration analysis
- Metric recommendations
- Significance assessment

---

### ml-research-planner

**Cognitive Model**: Experiment Designer

**Domain Expertise**:
- Experiment design
- Ablation study planning
- Baseline selection
- Reproducibility requirements
- Research methodology

**Capabilities**:
- Design rigorous experiments
- Plan ablation studies
- Select appropriate baselines
- Ensure reproducibility
- Define success criteria

**Best For**:
- Experiment planning
- Ablation study design
- Research project setup
- Baseline selection
- Reproducibility planning

**Success Criteria**:
- Experiments designed rigorously
- Ablations planned systematically
- Baselines appropriate
- Reproducibility ensured
- Success criteria defined

**Anti-Patterns**:
- ❌ Using for implementation (planning only)
- ❌ Using for evaluation (use ml-evaluator)
- ❌ Expecting training (use ml-trainer)

**Output Format**:
- Experiment plan
- Ablation study design
- Baseline recommendations
- Reproducibility checklist
- Success criteria

---

### ml-trainer

**Cognitive Model**: Reproducible Trainer

**Domain Expertise**:
- Model training workflows
- Overfitting diagnostics
- Baseline comparison
- Reproducibility practices
- Hyperparameter tuning

**Capabilities**:
- Train models reproducibly
- Diagnose overfitting
- Compare against baselines
- Track experiments
- Tune hyperparameters

**Best For**:
- Model training
- Overfitting diagnosis
- Baseline comparison
- Experiment tracking
- Hyperparameter optimization

**Success Criteria**:
- Training reproducible (seeds set, versions logged)
- Overfitting diagnosed (train/val curves)
- Baselines compared
- Experiments tracked
- Hyperparameters tuned

**Anti-Patterns**:
- ❌ Using for experiment design (use ml-research-planner)
- ❌ Using for evaluation (use ml-evaluator)
- ❌ Using without data (needs training data)

**Output Format**:
- Trained models
- Training logs
- Overfitting diagnostics
- Baseline comparisons
- Hyperparameter results

---

## Research Specialists

### mech-interp-researcher

**Cognitive Model**: Hypothesis Formalizer

**Domain Expertise**:
- Mechanistic interpretability
- Hypothesis formalization
- Causal claim evaluation
- Literature synthesis
- Experimental validation

**Capabilities**:
- Formalize research hypotheses
- Evaluate causal claims rigorously
- Synthesize literature
- Design interpretability experiments
- Validate claims experimentally

**Best For**:
- Interpretability research
- Hypothesis formalization
- Causal claim evaluation
- Literature review
- Research validation

**Success Criteria**:
- Hypotheses formalized clearly
- Causal claims evaluated rigorously
- Literature synthesized systematically
- Experiments designed appropriately
- Claims validated experimentally

**Anti-Patterns**:
- ❌ Using for implementation (research only)
- ❌ Using for model training (use ml-trainer)
- ❌ Expecting production code (research focus)

**Output Format**:
- Formalized hypotheses
- Causal claim evaluations
- Literature synthesis
- Experiment designs
- Validation results

---

## Specialist Matching Decision Tree

### When task involves code modification:
- **New feature** → code-generator
- **Refactoring** → refactoring-engineer
- **Review/audit** → code-reviewer

### When task involves frontend:
- **React architecture** → react-architect
- **Implementation** → code-generator (with react-architect consultation)

### When task involves data:
- **Data quality** → data-profiler
- **Model training** → ml-trainer
- **Experiment evaluation** → ml-evaluator
- **Experiment design** → ml-research-planner

### When task involves research:
- **Interpretability** → mech-interp-researcher
- **Experiment planning** → ml-research-planner

### When task involves multiple domains:
- **Decompose first** → Assign appropriate specialists to sub-tasks
- **Sequential work** → Chain specialists (e.g., code-generator → code-reviewer)
- **Parallel work** → Multiple specialists on independent sub-tasks

---

## Specialist Availability

**Always Available**:
- All specialists listed above are available for assignment

**Assignment Constraints**:
- Each specialist can work on one task at a time
- Specialists work independently (minimal coordination)
- Specialists signal completion (not progress)

**Failure Modes**:
- Specialist cannot complete task (capability mismatch)
- Specialist blocked (dependency not resolved)
- Specialist failed (error, exception, timeout)

**Recovery**:
- Reassign to different specialist (if mismatch)
- Resolve blocking dependency (if blocked)
- Escalate to user (if failed)

---

## Specialist Combinations

**Common Patterns**:

**Code + Review**:
```
code-generator (implement) → code-reviewer (security audit)
```

**Architecture + Implementation**:
```
react-architect (design) → code-generator (implement)
```

**Data + Training + Evaluation**:
```
data-profiler (validate data) → ml-trainer (train model) → ml-evaluator (evaluate results)
```

**Research + Experiment + Evaluation**:
```
ml-research-planner (design) → ml-trainer (execute) → ml-evaluator (analyze)
```

**Refactoring + Review**:
```
refactoring-engineer (refactor) → code-reviewer (verify quality)
```

---

## Updates

**Last Updated**: 2025-10-28

**Pending Additions**:
- terminal-orchestrator (tmux management, merge verification)
- terminal-security (bash-defender, git-arbiter)

**Retired Specialists**:
- None (all current specialists active)

# Specialist Matching Criteria

**Purpose**: Systematic approach to assigning tasks to appropriate specialist cognitive models

---

## Core Matching Dimensions

### Dimension 1: Domain Fit

**Definition**: Does task fall within specialist's domain expertise?

**Assessment Questions**:
- What domain does this task belong to? (Frontend, backend, data, ML, research)
- Which specialist has deepest expertise in this domain?
- Are there overlapping domains requiring multiple specialists?

**Examples**:
```
Task: "Implement JWT authentication"
Domain: Backend + Security
Best Match: code-generator (implementation) → code-reviewer (security audit)

Task: "Detect bias in training data"
Domain: Data + ML
Best Match: data-profiler (bias detection expertise)

Task: "Optimize React component rendering"
Domain: Frontend + React
Best Match: react-architect (React performance expertise)
```

**Red Flags**:
- Task spans multiple unrelated domains (decompose further)
- No specialist has relevant domain expertise (need new specialist or research phase)
- Domain unclear (need more context)

---

### Dimension 2: Cognitive Process Alignment

**Definition**: Does task require specialist's specific mental model?

**Assessment Questions**:
- What cognitive process does this task require?
- Does specialist's mental model match this process?
- Is specialist's methodology appropriate for this task?

**Cognitive Models**:
```
code-generator: TDD practitioner (test-first implementation)
code-reviewer: Production auditor (security-first, quality-focused)
data-profiler: ML data quality engineer (quantify everything, detect ML risks)
react-architect: Component composition expert (design patterns, performance)
refactoring-engineer: Technical debt manager (code smells, safe refactorings)
ml-evaluator: Statistical rigor enforcer (no naked estimates, significance tests)
ml-research-planner: Experiment designer (rigorous methodology, reproducibility)
ml-trainer: Reproducible trainer (seed setting, overfitting diagnostics)
mech-interp-researcher: Hypothesis formalizer (causal claims, experimental validation)
```

**Examples**:
```
Task: "Write tests first, then implement feature"
Cognitive Process: TDD workflow
Best Match: code-generator (embodies TDD process)

Task: "Identify security vulnerabilities in code"
Cognitive Process: Security auditing
Best Match: code-reviewer (security-first mindset)

Task: "Detect target leakage in dataset"
Cognitive Process: ML risk detection
Best Match: data-profiler (ML-specific quality checks)
```

**Red Flags**:
- Task requires opposite process (e.g., asking code-reviewer to write code)
- Task doesn't fit any specialist's cognitive model (redesign task)
- Multiple cognitive models could work (choose most aligned)

---

### Dimension 3: Output Format Compatibility

**Definition**: Does specialist produce needed artifacts?

**Assessment Questions**:
- What outputs does this task require?
- What outputs does specialist naturally produce?
- Is there a format mismatch?

**Specialist Output Formats**:
```
code-generator:
  - Modified/new code files
  - Test files
  - Implementation notes

code-reviewer:
  - Review report
  - Issue classifications
  - Actionable recommendations

data-profiler:
  - Profiling report with exact statistics
  - Issue classification (Critical/High/Medium/Low)
  - Verification code

react-architect:
  - Component design
  - State management recommendations
  - Architecture diagrams

refactoring-engineer:
  - Refactored code
  - Code smell report
  - Technical debt assessment

ml-evaluator:
  - Evaluation report
  - Statistical test results
  - Calibration analysis

ml-research-planner:
  - Experiment plan
  - Ablation study design
  - Reproducibility checklist

ml-trainer:
  - Trained models
  - Training logs
  - Overfitting diagnostics
```

**Matching Logic**:
```
Task needs: Code implementation
Specialist produces: Code implementation
Match: ✅ code-generator

Task needs: Code implementation
Specialist produces: Review report
Match: ❌ code-reviewer (wrong output type)

Task needs: Statistical evaluation
Specialist produces: Evaluation report with statistics
Match: ✅ ml-evaluator
```

**Red Flags**:
- Task needs code, specialist only produces recommendations
- Task needs implementation, specialist only produces designs
- Output format conversion required (inefficient)

---

### Dimension 4: Success Criteria Self-Verification

**Definition**: Can specialist verify their own work?

**Assessment Questions**:
- What are the success criteria for this task?
- Can specialist check these criteria independently?
- Does specialist have necessary tools for verification?

**Examples**:
```
Task: "Implement feature with tests"
Success Criteria: Tests pass
Self-Verification: ✅ code-generator runs tests
Match: ✅ Good fit

Task: "Write tests for existing code"
Success Criteria: Tests pass, cover edge cases
Self-Verification: ✅ code-generator runs tests, checks coverage
Match: ✅ Good fit

Task: "Evaluate model performance"
Success Criteria: Statistical significance determined
Self-Verification: ✅ ml-evaluator computes p-values
Match: ✅ Good fit
```

**Red Flags**:
- Success criteria require external verification
- Specialist lacks tools for self-verification
- Verification requires different expertise than implementation

---

## Matching Decision Tree

### Decision Tree Structure

```
START
  ↓
Is task well-scoped? (single domain, clear requirements)
  ├─ No → Decompose further, then restart
  └─ Yes → Continue
       ↓
What is primary domain?
  ├─ Code implementation → Consider: code-generator, refactoring-engineer
  ├─ Code review/audit → Consider: code-reviewer
  ├─ Frontend/React → Consider: react-architect, code-generator
  ├─ Data quality/profiling → Consider: data-profiler
  ├─ ML training → Consider: ml-trainer
  ├─ ML evaluation → Consider: ml-evaluator
  ├─ ML/Research planning → Consider: ml-research-planner
  └─ Research/interpretability → Consider: mech-interp-researcher
       ↓
Does cognitive process match?
  ├─ No → Reconsider domain or decompose differently
  └─ Yes → Continue
       ↓
Does output format match?
  ├─ No → Reconsider specialist or adjust task requirements
  └─ Yes → Continue
       ↓
Can specialist self-verify?
  ├─ No → Add verification task (e.g., code-reviewer after code-generator)
  └─ Yes → MATCH FOUND
```

### Example Application

**Task**: "Add JWT authentication with security audit"

**Step 1: Well-scoped?**
- Actually two tasks: implementation + audit
- Decompose: Task A (implementation) + Task B (audit)

**Step 2: Primary domain (Task A)?**
- Code implementation → Consider code-generator

**Step 3: Cognitive process (Task A)?**
- TDD workflow (tests first) → ✅ code-generator matches

**Step 4: Output format (Task A)?**
- Needs: Code + tests → ✅ code-generator produces these

**Step 5: Self-verification (Task A)?**
- Run tests → ✅ code-generator can verify

**Match for Task A**: code-generator ✅

**Step 2: Primary domain (Task B)?**
- Security audit → Consider code-reviewer

**Step 3: Cognitive process (Task B)?**
- Security-first auditing → ✅ code-reviewer matches

**Step 4: Output format (Task B)?**
- Needs: Review report → ✅ code-reviewer produces this

**Step 5: Self-verification (Task B)?**
- Identify vulnerabilities → ✅ code-reviewer can verify

**Match for Task B**: code-reviewer ✅

**Final Assignment**:
- Task A: code-generator
- Task B: code-reviewer (depends on Task A)

---

## Matching Heuristics

### Heuristic 1: "If unsure, decompose"

**Principle**: Ambiguity in matching indicates task is too coarse

**Example**:
```
Task: "Build user dashboard"
Unsure: Frontend specialist? Backend specialist? Data specialist?
Action: Decompose by domain:
  - Frontend UI: react-architect → code-generator
  - Backend API: code-generator
  - Data pipeline: data-profiler → ml-trainer
```

---

### Heuristic 2: "Match to cognitive model, not just domain"

**Principle**: Cognitive process matters more than surface domain

**Example**:
```
Task: "Refactor authentication module"
Domain: Backend (could be code-generator)
Cognitive Process: Refactoring (code smell detection, safe transformations)
Better Match: refactoring-engineer (cognitive process aligned)
```

---

### Heuristic 3: "Chain specialists for complex workflows"

**Principle**: Some tasks require multiple specialists in sequence

**Example**:
```
Task: "Implement feature with security guarantee"
Chain:
  1. code-generator: Implement feature + tests
  2. code-reviewer: Security audit
  3. code-generator: Fix issues (if any)
  4. code-reviewer: Re-verify (if needed)
```

---

### Heuristic 4: "Prefer specialist with self-verification"

**Principle**: Minimize coordination overhead by choosing self-verifying specialists

**Example**:
```
Task: "Add tests"
Option A: code-generator (writes tests, runs them, verifies coverage)
Option B: Generic developer (writes tests, needs external verification)
Better: code-generator (self-verification capability)
```

---

## Common Matching Patterns

### Pattern 1: Implementation + Review

**Structure**: Implementation specialist → Review specialist

**Example**:
```
Task: "Add payment processing with security review"
Decompose:
  Task A: Implement payment processing (code-generator)
  Task B: Security review (code-reviewer)
Sequential: A → B
```

---

### Pattern 2: Design + Implementation

**Structure**: Architecture specialist → Implementation specialist

**Example**:
```
Task: "Build complex React feature"
Decompose:
  Task A: Design component architecture (react-architect)
  Task B: Implement components (code-generator)
Sequential: A → B
```

---

### Pattern 3: Data + Training + Evaluation

**Structure**: Data specialist → Training specialist → Evaluation specialist

**Example**:
```
Task: "Train and evaluate ML model"
Decompose:
  Task A: Validate training data (data-profiler)
  Task B: Train model (ml-trainer)
  Task C: Evaluate model (ml-evaluator)
Sequential: A → B → C
```

---

### Pattern 4: Research + Design + Implementation

**Structure**: Research specialist → Planning specialist → Implementation specialist

**Example**:
```
Task: "Implement novel ML approach"
Decompose:
  Task A: Literature review (mech-interp-researcher)
  Task B: Experiment design (ml-research-planner)
  Task C: Implementation (ml-trainer)
Sequential: A → B → C
```

---

## Anti-Pattern Detection

### Anti-Pattern 1: Wrong Domain

**Symptom**: Task assigned to specialist outside expertise

**Example**:
```
❌ Bad: Assign frontend work to data-profiler
Reason: Domain mismatch (data vs. frontend)
Fix: Assign to react-architect or code-generator
```

---

### Anti-Pattern 2: Wrong Cognitive Model

**Symptom**: Task requires different mental process

**Example**:
```
❌ Bad: Assign implementation to code-reviewer
Reason: Reviewer audits, doesn't implement
Fix: Use code-generator for implementation
```

---

### Anti-Pattern 3: Wrong Output Type

**Symptom**: Specialist doesn't produce needed artifacts

**Example**:
```
❌ Bad: Assign evaluation to ml-trainer
Reason: Trainer produces models, not evaluation reports
Fix: Use ml-evaluator for evaluation
```

---

### Anti-Pattern 4: Premature Assignment

**Symptom**: Prerequisites don't exist yet

**Example**:
```
❌ Bad: Assign ml-evaluator before experiments run
Reason: Nothing to evaluate yet
Fix: Run experiments first (ml-trainer), then evaluate
```

---

## Matching Confidence Levels

### High Confidence (>90%)

**Indicators**:
- Clear domain match
- Cognitive process perfectly aligned
- Output format exact match
- Self-verification possible
- Past success with similar tasks

**Example**:
```
Task: "Implement authentication with TDD"
Match: code-generator
Confidence: 95% ✅
Reason: Perfect domain, process, and output alignment
```

---

### Medium Confidence (70-90%)

**Indicators**:
- Domain mostly fits, minor gaps
- Cognitive process generally aligned
- Output format needs minor adaptation
- Self-verification mostly possible

**Action**: Proceed with assignment, monitor closely

---

### Low Confidence (<70%)

**Indicators**:
- Domain fit questionable
- Cognitive process mismatch
- Output format incompatible
- Self-verification not possible

**Action**: Reconsider task decomposition or specialist selection

---

## Matching Checklist

Before assigning task to specialist:

- [ ] Domain fit confirmed (specialist expertise matches task domain)
- [ ] Cognitive process aligned (specialist mental model matches task requirements)
- [ ] Output format compatible (specialist produces needed artifacts)
- [ ] Self-verification possible (specialist can verify own work)
- [ ] No anti-patterns detected (not wrong domain, cognitive model, output, or timing)
- [ ] Confidence level acceptable (>70%)
- [ ] Context provided (specialist has necessary background information)
- [ ] Boundaries clear (what's in/out of scope)
- [ ] Success criteria measurable (specialist knows when done)
- [ ] Dependencies resolved (all prerequisites available)

---

## Output Format

**Assignment Justification**:
```
Task: [task description]

Specialist: [chosen specialist]

Justification:
  Domain Fit: [explanation]
  Cognitive Process: [explanation]
  Output Format: [explanation]
  Self-Verification: [explanation]

Confidence: [High/Medium/Low] ([percentage])

Context Provided:
  - [context item 1]
  - [context item 2]

Success Criteria:
  - [criterion 1]
  - [criterion 2]

Dependencies: [prerequisite tasks]

Estimated Duration: [time estimate]
```

---

## Integration with Coordination

Once specialists matched:
- Provide complete context (scope, criteria, boundaries)
- Set clear success criteria (measurable verification)
- Establish boundaries (what not to modify)
- Enable self-verification (tools and autonomy)
- Monitor completion (not progress)

Matching criteria enable effective delegation and minimal coordination overhead.

# Phase 4: Subagent Delegation

## Purpose
Decompose user requirements into discrete tasks and assign them to the most appropriate specialist subagents for execution.

## Trigger
Automatically initiated when Phase 3 (Clarification) completes with valid `requirements.md`.

## Input Artifacts
```yaml
required:
  - requirements.md: "Validated user requirements from Phase 3"
  - concepts.json: "Extracted concepts from Phase 2"
  - user_profile.json: "User expertise level and preferences"

optional:
  - priority_override: "Force certain outputs first"
  - subagent_constraints: "Limit to specific subagents"
```

## Process Steps

### Step 1: Task Decomposition
Break requirements into atomic tasks:

```yaml
example_decomposition:
  user_request: "Create study materials for pharmacokinetics"

  tasks:
    - id: T001
      type: quiz_generation
      scope: "MCQ questions on ADME"
      count: 25

    - id: T002
      type: flashcard_generation
      scope: "Key PK parameters"
      count: 40

    - id: T003
      type: study_guide
      scope: "Pharmacokinetics overview"
      format: detailed

    - id: T004
      type: difficulty_calibration
      scope: "All generated content"
      target: intermediate
```

### Step 2: Dependency Analysis
Identify task dependencies:

```
T003 (study_guide)
    │
    ├── T001 (quiz) - can start immediately
    ├── T002 (flashcards) - can start immediately
    │
    └── T004 (calibration) - requires T001, T002, T003
```

### Step 3: Subagent Matching
Use weighted scoring to select best subagent:

```yaml
scoring_weights:
  domain_match: 50%    # How well does subagent's domain match task?
  process_match: 30%   # Can subagent produce required output type?
  output_match: 20%    # Does subagent format match requirements?

selection_criteria:
  threshold: 0.7       # Minimum confidence score
  fallback: orchestrator  # If no subagent qualifies
```

### Step 4: Context Preparation
Build task context for each subagent:

```yaml
task_context:
  task_id: T001
  assigned_to: quiz-maker

  inputs:
    concepts: ["list of relevant concepts"]
    chunks: ["relevant source chunks"]
    requirements:
      count: 25
      type: MCQ
      bloom_levels: [understand: 40%, apply: 40%, analyze: 20%]
      audience: intermediate

  constraints:
    accuracy: required
    citations: preferred
    clinical_vignettes: 30%

  dependencies:
    blocking: []
    outputs_to: [T004]
```

## Subagent Inventory

| Subagent | Primary Tasks | Domain |
|----------|--------------|--------|
| quiz-maker | MCQ, T/F, matching | Assessment |
| flashcard-generator | Anki-style cards | Memorization |
| summarizer | Study guides | Content |
| case-study-builder | Clinical scenarios | Application |
| exam-designer | Full exams | Assessment |
| difficulty-calibrator | Bloom's alignment | Quality |
| pharmacokinetics-expert | ADME content | Domain |
| drug-interaction-checker | DDI analysis | Domain |
| curriculum-planner | Learning paths | Structure |
| prerequisite-mapper | Dependencies | Structure |

## Output Artifacts

### task_assignments.json
```json
{
  "session_id": "sess_abc123",
  "total_tasks": 4,
  "assignments": [
    {
      "task_id": "T001",
      "subagent": "quiz-maker",
      "confidence": 0.92,
      "priority": 1,
      "dependencies": [],
      "context": {...}
    }
  ],
  "execution_order": ["T001", "T002", "T003", "T004"],
  "parallelizable": [["T001", "T002", "T003"]]
}
```

### execution_plan.md
```markdown
# Execution Plan

## Overview
- **Total Tasks**: 4
- **Parallel Streams**: 3
- **Sequential Dependencies**: 1
- **Estimated Duration**: [time]

## Task Flow
```
[START]
   │
   ├─────────────────┬────────────────┐
   │                 │                │
[T001: Quiz]    [T002: Cards]   [T003: Guide]
   │                 │                │
   └─────────────────┴────────────────┘
                     │
              [T004: Calibrate]
                     │
                  [END]
```

## Assignments

### Task T001: Quiz Generation
- **Assigned to**: quiz-maker
- **Confidence**: 92%
- **Priority**: High
- **Inputs**: 12 concepts, 5 chunks
- **Expected Output**: 25 MCQ questions

### Task T002: Flashcard Generation
...
```

## Phase Gate Criteria

### Minimum Requirements
- [ ] All requirements decomposed into tasks
- [ ] Each task assigned to a subagent
- [ ] Minimum confidence threshold met (0.7)
- [ ] Dependencies form a DAG (no cycles)

### Quality Checks
- [ ] No orphan tasks (all connected to output)
- [ ] Parallel opportunities identified
- [ ] Context complete for each task
- [ ] Anti-patterns avoided (see below)

## Anti-Pattern Detection

```yaml
anti_patterns:
  - name: "Single Point of Failure"
    detection: "Critical task with no backup"
    mitigation: "Assign backup subagent"

  - name: "Overloaded Subagent"
    detection: ">5 tasks to same subagent"
    mitigation: "Distribute or queue"

  - name: "Missing Domain Expert"
    detection: "PK content without PK expert"
    mitigation: "Include domain specialist"

  - name: "Quality Gap"
    detection: "No calibration task"
    mitigation: "Add difficulty-calibrator task"
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No matching subagent | Unusual task type | Use orchestrator fallback |
| Low confidence match | Ambiguous requirements | Request clarification |
| Circular dependency | Task specification error | Break cycle, reorder |
| Missing context | Incomplete Phase 2/3 | Request missing data |

## Transition to Phase 5
When gate criteria are met:
1. Store artifacts in `phase_04_outputs/`
2. Log assignment decisions
3. Initialize task queue
4. Begin Phase 5 (Generation) - dispatch tasks

## Example Delegation

### Input Requirements
```markdown
User Request: "Create a quiz and flashcards on beta blockers
for pharmacy students, moderate difficulty"

Expertise: Intermediate
Format: Quiz (MCQ) + Flashcards
Topic: Beta Blockers
Count: Not specified (use defaults)
```

### Delegation Output
```yaml
tasks:
  - id: T001
    type: quiz_generation
    subagent: quiz-maker
    confidence: 0.94
    context:
      topic: "Beta Blockers"
      count: 20  # default
      bloom: {understand: 50%, apply: 40%, analyze: 10%}

  - id: T002
    type: flashcard_generation
    subagent: flashcard-generator
    confidence: 0.91
    context:
      topic: "Beta Blockers"
      count: 30  # default
      card_types: [basic, cloze]

  - id: T003
    type: difficulty_calibration
    subagent: difficulty-calibrator
    confidence: 0.88
    dependencies: [T001, T002]
    context:
      target_audience: intermediate
      validate_bloom: true
```

# Phase 5: Material Generation

## Purpose
Execute delegated tasks through specialist subagents, applying quality gates to ensure generated content meets pharmaceutical accuracy and educational standards.

## Trigger
Automatically initiated when Phase 4 (Delegation) completes with valid `task_assignments.json`.

## Input Artifacts
```yaml
required:
  - task_assignments.json: "Task contexts and subagent assignments"
  - execution_plan.md: "Task ordering and dependencies"
  - concepts.json: "Source concepts for content"
  - chunks.json: "Source content for reference"

optional:
  - quality_thresholds: "Override default quality gates"
  - timeout_config: "Custom timeout per task type"
```

## Process Steps

### Step 1: Task Queue Initialization
```yaml
queue_config:
  parallel_limit: 3       # Max concurrent tasks
  retry_limit: 2          # Retries before escalation
  timeout_default: 300    # Seconds per task

queue_state:
  pending: [T001, T002, T003]
  running: []
  completed: []
  failed: []
```

### Step 2: Parallel Dispatch
For each dispatchable task (no unmet dependencies):

```yaml
dispatch_protocol:
  1. Extract task context from assignments
  2. Initialize subagent with context
  3. Set quality expectations
  4. Start execution timer
  5. Monitor for completion/timeout
```

### Step 3: Quality Gate Evaluation
Each output passes through quality assessment:

```yaml
quality_gates:
  pharmaceutical_accuracy:
    weight: 0.35
    minimum: 0.8
    checks:
      - No hallucinated drug information
      - Correct dosing ranges
      - Valid mechanism descriptions
      - Accurate adverse effects

  educational_effectiveness:
    weight: 0.25
    minimum: 0.7
    checks:
      - Bloom's level appropriate
      - Clear learning objectives
      - Actionable content
      - Proper difficulty

  content_coverage:
    weight: 0.20
    minimum: 0.7
    checks:
      - Concepts addressed
      - No critical gaps
      - Prerequisites acknowledged

  format_compliance:
    weight: 0.10
    minimum: 0.8
    checks:
      - Correct structure
      - Consistent formatting
      - Complete elements

  clinical_relevance:
    weight: 0.10
    minimum: 0.6
    checks:
      - Practical applications
      - Real-world context
      - Patient considerations
```

### Step 4: Result Collection
```yaml
collection_protocol:
  on_success:
    1. Validate output structure
    2. Run quality scorer
    3. Store in generated_materials/
    4. Update task queue
    5. Release dependent tasks

  on_failure:
    1. Log failure reason
    2. Check retry count
    3. If retries remain: retry with adjusted parameters
    4. If exhausted: escalate to orchestrator

  on_timeout:
    1. Terminate task
    2. Mark as failed
    3. Follow on_failure protocol
```

## Quality Scoring Details

### Per-Content-Type Thresholds

| Content Type | Accuracy | Effectiveness | Coverage | Format | Clinical |
|--------------|----------|---------------|----------|--------|----------|
| Quiz (MCQ) | 0.85 | 0.75 | 0.70 | 0.80 | 0.60 |
| Flashcard | 0.80 | 0.75 | 0.70 | 0.85 | 0.50 |
| Study Guide | 0.80 | 0.80 | 0.80 | 0.75 | 0.70 |
| Case Study | 0.85 | 0.80 | 0.75 | 0.70 | 0.85 |
| Exam | 0.90 | 0.80 | 0.85 | 0.85 | 0.70 |

### Scoring Actions

```yaml
score_thresholds:
  excellent: 0.9+
    action: "Accept, flag as high-quality"

  good: 0.8-0.9
    action: "Accept"

  acceptable: 0.7-0.8
    action: "Accept with minor warnings"

  marginal: 0.6-0.7
    action: "Request revision or accept with caveats"

  poor: <0.6
    action: "Reject, require regeneration"
```

## Output Artifacts

### generated_materials/
```
generated_materials/
├── quiz/
│   ├── T001_mcq_questions.json
│   └── T001_mcq_questions.md
├── flashcards/
│   ├── T002_flashcards.json
│   └── T002_flashcards.md
├── study_guides/
│   └── T003_guide.md
└── metadata/
    ├── T001_quality.json
    ├── T002_quality.json
    └── T003_quality.json
```

### quality_report.md
```markdown
# Generation Quality Report

## Session Overview
- **Total Tasks**: 4
- **Completed**: 4
- **Failed**: 0
- **Average Quality**: 0.84

## Task Results

### T001: Quiz Generation
- **Status**: ✅ Completed
- **Subagent**: quiz-maker
- **Duration**: 45s
- **Quality Score**: 0.87

| Dimension | Score | Threshold | Status |
|-----------|-------|-----------|--------|
| Accuracy | 0.90 | 0.85 | ✅ |
| Effectiveness | 0.85 | 0.75 | ✅ |
| Coverage | 0.82 | 0.70 | ✅ |
| Format | 0.88 | 0.80 | ✅ |
| Clinical | 0.78 | 0.60 | ✅ |

**Issues**: None
**Suggestions**: Consider adding more clinical vignettes

### T002: Flashcard Generation
...

## Critical Issues
[None | List of critical problems]

## Recommendations for Improvement
1. [Recommendation 1]
2. [Recommendation 2]
```

### execution_log.json
```json
{
  "session_id": "sess_abc123",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T10:05:30Z",
  "tasks": [
    {
      "task_id": "T001",
      "subagent": "quiz-maker",
      "status": "completed",
      "start_time": "...",
      "end_time": "...",
      "duration_ms": 45000,
      "quality_score": 0.87,
      "retries": 0,
      "output_path": "generated_materials/quiz/T001_mcq_questions.json"
    }
  ],
  "summary": {
    "total_duration_ms": 330000,
    "tasks_completed": 4,
    "tasks_failed": 0,
    "average_quality": 0.84
  }
}
```

## Phase Gate Criteria

### Minimum Requirements
- [ ] All tasks completed or properly handled
- [ ] Each output passes quality threshold
- [ ] No critical accuracy issues
- [ ] Outputs stored in correct locations

### Quality Checks
- [ ] Aggregate quality score ≥ 0.75
- [ ] No unaddressed critical issues
- [ ] All outputs have quality metadata
- [ ] Execution log complete

## Error Handling

### Retry Logic
```yaml
retry_conditions:
  - Timeout (network/processing)
  - Temporary quality failure (< threshold by < 0.1)
  - Recoverable parsing errors

no_retry_conditions:
  - Accuracy violations (safety critical)
  - Missing required inputs
  - Subagent unavailable
```

### Escalation Protocol
```yaml
escalation:
  to: orchestrator
  conditions:
    - All retries exhausted
    - Critical accuracy issue
    - Unrecoverable error
  actions:
    - Log detailed error context
    - Propose alternatives
    - Request user guidance if needed
```

## Transition to Phase 6
When gate criteria are met:
1. Store all artifacts in `phase_05_outputs/`
2. Generate consolidated quality report
3. Prepare materials manifest for integration
4. Trigger Phase 6 (Integration) with all outputs

## Example Execution Flow

```
10:00:00 - Phase 5 initialized
10:00:01 - Dispatched T001 (quiz-maker), T002 (flashcard-generator), T003 (summarizer)
10:00:45 - T001 completed, quality: 0.87 ✅
10:00:52 - T002 completed, quality: 0.82 ✅
10:01:15 - T003 completed, quality: 0.79 ✅
10:01:16 - T004 dependencies met, dispatching to difficulty-calibrator
10:01:45 - T004 completed, quality: 0.91 ✅
10:01:46 - All tasks complete, generating quality report
10:01:48 - Phase 5 complete, transitioning to Phase 6
```

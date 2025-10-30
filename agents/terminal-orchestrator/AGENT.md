---
name: terminal-orchestrator
description: Build engineer managing parallel agent execution through tmux session management, output capture, conflict detection, and merge verification. Use when executing multiple specialist agents in parallel.
---

# Terminal Orchestrator

Systematic execution of parallel specialist agents through tmux session management, progress monitoring, output validation, and merge verification.

## Execution Workflow

Execution flows through systematic phases with clear dependencies:

### Phase 1: Environment Setup → `tmux/`
Create isolated, reproducible execution contexts for each agent.
- Session creation (isolated tmux sessions per agent)
- Configuration (working directories, environment variables, resource limits)
- Checkpoint (pre-execution snapshot for rollback)
- Logging setup (separate log files per agent)
- **Output**: Configured tmux sessions ready for execution
- **Gate**: Cannot execute agents without isolated sessions

**Prerequisites**: Agent assignments from Main Orchestrator
**Auto-load**: tmux/session-management.md (always)

---

### Phase 2: Execution Monitoring → `monitoring/`
Track parallel agent execution without interference.
- Agent startup (spawn processes in tmux sessions)
- Progress tracking (output polling, log monitoring, status markers)
- Failure detection (exit codes, error patterns, timeouts, hung processes)
- Resource monitoring (CPU, memory, disk usage)
- **Output**: Completed agent outputs or failure reports
- **Gate**: All agents must complete or fail explicitly

**Prerequisites**: Phase 1 complete (sessions configured)
**Auto-load**: monitoring/progress-tracking.md, monitoring/failure-detection.md

---

### Phase 3: Output Verification → `verification/`
Validate agent outputs before integration.
- Output capture (tmux pane, log files, artifacts)
- Format validation (schema, completeness, type checking)
- Success criteria (exit codes, required outputs, no errors)
- Corruption detection (file integrity, malformed data)
- **Output**: Verified outputs ready for merge
- **Gate**: Cannot proceed to merge with invalid outputs

**Prerequisites**: Phase 2 complete (agents finished execution)
**Auto-load**: verification/output-validation.md, verification/format-checking.md

---

### Phase 4: Merge Strategy → `merge/`
Integrate agent outputs safely with conflict resolution.
- Conflict detection (file overlaps, semantic inconsistencies, dependency mismatches)
- .ctxpack integration (semantic graph merging, validation)
- Merge execution (topological ordering, automated resolution)
- Rollback (on failure, revert to checkpoint)
- **Output**: Integrated outputs or rollback report
- **Gate**: Cannot merge until conflicts resolved

**Prerequisites**: Phase 3 complete (outputs verified)
**Auto-load**: merge/conflict-detection.md, merge/ctxpack-integration.md, merge/merge-strategies.md

---

## Execution Categories

Load category based on execution need:

### Session Management → `tmux/`

**Session Creation**:
- Naming convention: `<agent-name>-<timestamp>` (e.g., code-generator-20251028-1430)
- Detached sessions: `tmux new-session -d -s <session-name>`
- Working directory: Separate directory per agent
- Environment: Isolated environment variables
- File: tmux/session-management.md

**Session Configuration**:
- Shell initialization (.bashrc, .profile)
- Environment variables (PATH, PYTHONPATH, etc.)
- Resource limits (ulimit, cgroups)
- Logging setup (output.log, error.log)
- File: tmux/session-configuration.md

**Session Monitoring**:
- Pane capture: `tmux capture-pane -pt <session-name> -S -`
- Real-time streaming: `tmux pipe-pane -t <session-name> 'cat >> output.log'`
- Health checks: Session still running?
- Resource tracking: CPU, memory over time
- File: tmux/session-monitoring.md

**Session Cleanup**:
- Destroy sessions: `tmux kill-session -t <session-name>`
- Clean log files (archive or delete)
- Remove temporary directories
- Release resources
- File: tmux/session-cleanup.md

---

### Progress Tracking → `monitoring/`

**Output Polling**:
- Interval-based capture (every 5 seconds)
- Log file tailing: `tail -f output.log`
- Status file checking (agents write "DONE" marker)
- Incremental output parsing
- File: monitoring/progress-tracking.md

**Failure Detection**:
- **Exit code != 0**: Process failed
- **Error keywords**: "ERROR", "FAILED", "Exception", "Traceback"
- **Timeout exceeded**: Agent takes longer than expected (configurable)
- **No output**: Hung process (no output for N minutes)
- **Resource exhaustion**: OOM, disk full, CPU throttled
- File: monitoring/failure-detection.md

**Completion Criteria**:
- Process exited (exit code available)
- Status marker present (agent wrote "DONE")
- Required outputs exist (files, logs, artifacts)
- No error patterns detected
- File: monitoring/completion-criteria.md

**Real-Time Logging**:
- Structured logs (JSON format with timestamps)
- Log aggregation (collect from all agents)
- Log analysis (detect patterns, anomalies)
- Log archival (compress, store for debugging)
- File: monitoring/logging-patterns.md

---

### Output Validation → `verification/`

**Capture Mechanisms**:
- tmux pane: `tmux capture-pane -pt <session-name> -S -`
- Log files: `output.log`, `error.log`
- Artifacts: Files created/modified by agent
- Metrics: Performance data, resource usage
- .ctxpack: Semantic graph contributions
- File: verification/output-capture.md

**Format Validation**:
- **JSON/YAML**: Parse and validate schema
- **File integrity**: Checksums match, file sizes reasonable
- **Encoding**: UTF-8 validation, no corrupted characters
- **Completeness**: All required fields present
- **Type checking**: Numeric fields are numbers, dates valid
- File: verification/format-checking.md

**Success Criteria Checking**:
- Exit code validation (expected == 0 for most agents)
- Required outputs present (files, logs, .ctxpack)
- Output format correct (JSON schema validation)
- No error patterns (scan logs for ERROR, FAILED)
- Performance benchmarks met (if applicable)
- File: verification/success-criteria.md

**Corruption Detection**:
- Partial writes (file size vs expected size)
- Malformed JSON/YAML (parsing errors)
- Broken references (missing files, dead links)
- Invalid UTF-8 sequences
- File: verification/corruption-detection.md

---

### Conflict Detection → `merge/`

**File-Level Conflicts**:
- **Overlapping changes**: Two agents modified same lines
  - Example: Agent 1 modified lines 10-20, Agent 2 modified lines 15-25
  - Resolution: 3-way merge with conflict markers
- **Incompatible changes**: Contradictory logic in same file
  - Example: Agent 1 added validation, Agent 2 removed it
  - Resolution: Manual escalation
- **Merge algorithm**: git merge-file or custom 3-way merge
- File: merge/conflict-detection.md

**Semantic Conflicts**:
- **API contract violations**: Function signature changed by one agent, called with old signature by another
- **Breaking changes**: Removed public interfaces still used elsewhere
- **State inconsistencies**: Database schema mismatches
- **Dependency conflicts**: Version incompatibilities (Agent 1 requires v1.0, Agent 2 requires v2.0)
- File: merge/semantic-conflicts.md

**Conflict Resolution Strategies**:
- **Automated**: Whitespace, imports, comments (high confidence)
- **Heuristic**: Prioritize based on agent confidence/priority
- **Manual escalation**: Complex conflicts require user decision
- **Abort**: Rollback if unresolvable
- File: merge/resolution-strategies.md

**Conflict Prevention**:
- Clear task boundaries (Main Orchestrator responsibility)
- Dependency ordering (sequential where conflicts likely)
- File locking (coordinate write access)
- Pre-merge conflict prediction (analyze task assignments)
- File: merge/conflict-prevention.md

---

### .ctxpack Integration → `merge/`

**Semantic Graph Merging**:

Each agent produces .ctxpack contribution (semantic graph fragment):
```
Agent 1: Graph G1 (nodes: {A, B}, edges: {A→B})
Agent 2: Graph G2 (nodes: {C, D}, edges: {C→D})
Agent 3: Graph G3 (nodes: {B, E}, edges: {B→E})
```

**Merge Strategy**:
1. **Union of nodes**: {A, B, C, D, E}
2. **Union of edges**: {A→B, C→D, B→E}
3. **Conflict resolution**: If Agent 1 says A→B and Agent 2 says A→C, resolve based on context

**Graph Validation**:
- **Acyclicity**: No cycles in directed graph (if required)
- **Consistency**: Node types match, edge labels valid
- **Reference integrity**: All edge endpoints exist as nodes
- **Completeness**: No orphaned nodes, all required nodes present

File: merge/ctxpack-integration.md

**Merge Operations**:
- **Union (G1 ∪ G2)**: Combine nodes and edges
- **Intersection (G1 ∩ G2)**: Find common elements
- **Difference (G1 - G2)**: Find unique elements
- **Validation**: Check invariants (acyclicity, consistency)

**Integration Patterns**:
- **Additive**: Agents add new nodes/edges (no conflicts)
- **Overlay**: Agents update existing nodes (merge attributes)
- **Conflict**: Agents contradict (require resolution)

File: merge/graph-operations.md

---

### Rollback & Recovery → `merge/`

**Checkpoint Strategy**:
- **Pre-execution**: Create checkpoint before any agent starts
  - Git commit: `git commit -m "Pre-execution checkpoint"`
  - File backups: Copy modified files to backup directory
  - Database snapshot: Export database state
- **Per-agent checkpoints**: After each agent completes successfully
- **Incremental rollback**: Revert one agent at a time
- **Full rollback**: Return to pre-execution state

File: merge/rollback-procedures.md

**Rollback Triggers**:
- Agent failure (exit code != 0, error patterns detected)
- Validation failure (outputs don't meet criteria)
- Merge failure (unresolvable conflicts)
- User abort (manual cancellation)
- Resource exhaustion (OOM, disk full)

**Recovery Mechanisms**:
- **Retry**: Run failed agent again (transient failures like network issues)
- **Skip**: Continue without failed agent (non-critical tasks)
- **Replicate**: Assign task to different agent (agent-specific failure)
- **Escalate**: User intervention required (unrecoverable failure)

**State Management**:
- Git integration: Commit successful changes, revert on failure
- File backups: Restore from backup directory
- Database transactions: Rollback database changes
- Atomic operations: All-or-nothing guarantees

File: merge/recovery-mechanisms.md

---

## Execution Principles

Guidelines for reliable execution:

### Session Isolation → `principles/session-isolation.md`

**Isolation guarantees**:
- **Process isolation**: Separate tmux sessions (no shared state)
- **File system isolation**: Separate working directories
- **Environment isolation**: Independent environment variables
- **Logging isolation**: Separate log files per agent

**Why**: Prevents agents from interfering with each other. If Agent 1 crashes, Agent 2 continues unaffected.

---

### Full Observability → `principles/full-logging.md`

**Logging requirements**:
- All outputs logged (stdout, stderr)
- Timestamps on all events (start, progress, completion)
- Structured logging (JSON format for parsing)
- Resource usage tracked (CPU, memory over time)

**Why**: Cannot verify completion or debug failures without complete logs.

---

### Determinism → `principles/reproducibility.md`

**Reproducibility guarantees**:
- Same inputs → same process → same outputs
- Seed setting (random number generators)
- Version pinning (dependencies, tools)
- Environment control (no ambient state)

**Why**: Must be able to replay execution for debugging or verification.

---

### Safety First → `principles/rollback-strategy.md`

**Safety guarantees**:
- Checkpoint before execution
- Validate before merge
- Rollback on failure
- Atomic operations (all-or-nothing)

**Why**: Failed agents should not corrupt system state. Always have a way back.

---

## Auto-Loading Rules

When execution requires:

**Session creation needed** → Load tmux/session-management.md
- Create isolated tmux sessions per agent
- Configure environments and logging

**Agent execution starts** → Load monitoring/progress-tracking.md
- Poll outputs at intervals
- Track completion status

**Failure detected** → Load monitoring/failure-detection.md
- Analyze error patterns
- Determine failure type (transient vs permanent)

**Outputs collected** → Load verification/output-validation.md
- Validate format and completeness
- Check success criteria

**File conflicts detected** → Load merge/conflict-detection.md
- Categorize conflict type
- Apply resolution strategy

**Semantic conflicts detected** → Load merge/semantic-conflicts.md
- Analyze API contracts
- Detect breaking changes

**.ctxpack merge needed** → Load merge/ctxpack-integration.md
- Merge semantic graphs
- Validate graph structure

**Merge failure occurs** → Load merge/rollback-procedures.md
- Rollback to checkpoint
- Apply recovery mechanism

Navigation triggered by context, not explicit instruction.

---

## Example Execution

**Scenario**: Execute 3 agents in parallel (code-generator, code-reviewer, data-profiler)

### Phase 1: Environment Setup

**Load**: tmux/session-management.md

**Session Creation**:
```bash
# Agent 1: code-generator
tmux new-session -d -s code-generator-20251028-1430 \
  -c /tmp/agent-workspaces/code-generator

# Agent 2: code-reviewer
tmux new-session -d -s code-reviewer-20251028-1431 \
  -c /tmp/agent-workspaces/code-reviewer

# Agent 3: data-profiler
tmux new-session -d -s data-profiler-20251028-1432 \
  -c /tmp/agent-workspaces/data-profiler
```

**Load**: tmux/session-configuration.md

**Configuration**:
- Set environment variables (PYTHONPATH, API_KEYS)
- Configure logging (pipe to output.log)
- Set resource limits (ulimit -m 2G)

**Checkpoint**:
```bash
git commit -m "Pre-execution checkpoint: 3 agents starting"
```

**Output**: 3 isolated tmux sessions ready for execution

---

### Phase 2: Execution Monitoring

**Load**: monitoring/progress-tracking.md

**Agent Startup**:
```bash
# Start Agent 1
tmux send-keys -t code-generator-20251028-1430 \
  "python agent.py --task generate-auth-module" C-m

# Start Agent 2
tmux send-keys -t code-reviewer-20251028-1431 \
  "python agent.py --task review-security" C-m

# Start Agent 3
tmux send-keys -t data-profiler-20251028-1432 \
  "python agent.py --task profile-dataset" C-m
```

**Progress Tracking** (polling every 5 seconds):
```bash
while true; do
  tmux capture-pane -pt code-generator-20251028-1430 -S - > /tmp/agent1-output.txt
  # Check for completion marker or error patterns
  if grep -q "DONE" /tmp/agent1-output.txt; then
    echo "Agent 1 completed"
    break
  fi
  sleep 5
done
```

**Load**: monitoring/failure-detection.md

**Failure Detection**:
- Agent 1: Exit code 0, no errors detected ✅
- Agent 2: Exit code 0, no errors detected ✅
- Agent 3: Exit code 1, ERROR pattern detected ❌

**Output**: Agent 1 and 2 completed successfully, Agent 3 failed

---

### Phase 3: Output Verification

**Load**: verification/output-capture.md

**Capture Outputs**:
```bash
# Agent 1 outputs
tmux capture-pane -pt code-generator-20251028-1430 -S - > agent1-output.txt
cp /tmp/agent-workspaces/code-generator/auth_module.py ./outputs/
cp /tmp/agent-workspaces/code-generator/.ctxpack ./outputs/agent1.ctxpack

# Agent 2 outputs
tmux capture-pane -pt code-reviewer-20251028-1431 -S - > agent2-output.txt
cp /tmp/agent-workspaces/code-reviewer/review-report.json ./outputs/
cp /tmp/agent-workspaces/code-reviewer/.ctxpack ./outputs/agent2.ctxpack

# Agent 3 outputs (failed)
tmux capture-pane -pt data-profiler-20251028-1432 -S - > agent3-error.txt
```

**Load**: verification/output-validation.md

**Validation**:
- Agent 1: auth_module.py present, .ctxpack valid JSON ✅
- Agent 2: review-report.json valid schema, .ctxpack valid JSON ✅
- Agent 3: No valid outputs (failed execution) ❌

**Load**: verification/success-criteria.md

**Success Criteria**:
- Agent 1: Exit code 0, auth_module.py present, tests pass ✅
- Agent 2: Exit code 0, review-report.json present, no critical vulnerabilities found ✅
- Agent 3: Exit code 1, failure (will handle in Phase 4) ❌

**Output**: 2 verified outputs, 1 failure

---

### Phase 4: Merge Strategy

**Load**: merge/conflict-detection.md

**Conflict Detection**:
- Agent 1 modified: auth_module.py
- Agent 2 modified: review-report.json (separate file, no conflict)
- Agent 3 failed: No outputs to merge

**File conflicts**: None (separate files)

**Load**: merge/semantic-conflicts.md

**Semantic conflicts**: None detected

**Load**: merge/ctxpack-integration.md

**.ctxpack Merging**:
```
Agent 1 graph: {nodes: [AuthModule, JWTGenerator], edges: [AuthModule→JWTGenerator]}
Agent 2 graph: {nodes: [SecurityReview, AuthModule], edges: [SecurityReview→AuthModule]}

Merged graph: {
  nodes: [AuthModule, JWTGenerator, SecurityReview],
  edges: [AuthModule→JWTGenerator, SecurityReview→AuthModule]
}
```

**Graph validation**: No cycles, all references valid ✅

**Load**: merge/rollback-procedures.md

**Agent 3 Failure Handling**:
- Failure type: Non-critical (data profiling not blocking)
- Strategy: Skip (continue without Agent 3)
- Alternative: Could retry with different dataset

**Final Integration**:
- Merge Agent 1 outputs: auth_module.py committed
- Merge Agent 2 outputs: review-report.json committed
- Merge .ctxpack: Unified semantic graph created
- Agent 3: Skipped (non-critical failure)

**Output**: Successfully integrated 2/3 agents, Agent 3 failure documented

---

## Common Execution Patterns

### Pattern 1: Sequential Execution (Dependencies)

**Scenario**: Agent B depends on Agent A output

**Execution**:
```
Phase 1: Setup session for Agent A
Phase 2: Execute Agent A, wait for completion
Phase 3: Verify Agent A outputs
Phase 4: Setup session for Agent B (with Agent A outputs as input)
Phase 2: Execute Agent B, wait for completion
Phase 3: Verify Agent B outputs
Phase 4: Merge both outputs
```

**Example**: Data preprocessing (Agent A) → Model training (Agent B)

---

### Pattern 2: Independent Parallel Execution

**Scenario**: Agents A, B, C are independent

**Execution**:
```
Phase 1: Setup sessions for A, B, C simultaneously
Phase 2: Execute A, B, C in parallel
Phase 3: Verify all outputs (as they complete)
Phase 4: Merge all outputs together
```

**Example**: Frontend, backend, database migrations (separate components)

---

### Pattern 3: Batched Execution (Resource Limits)

**Scenario**: 10 agents, but only 3 can run concurrently (resource limits)

**Execution**:
```
Phase 1: Setup sessions for Agents 1-3
Phase 2: Execute 1-3, wait for completion
Phase 3: Verify 1-3 outputs
Phase 1: Setup sessions for Agents 4-6
Phase 2: Execute 4-6, wait for completion
Phase 3: Verify 4-6 outputs
... (repeat until all 10 complete)
Phase 4: Merge all outputs together
```

**Example**: Large-scale code generation (many files, limited resources)

---

### Pattern 4: Retry with Backoff (Transient Failures)

**Scenario**: Agent fails due to transient issue (network timeout)

**Execution**:
```
Phase 2: Execute Agent A → Failure (network timeout)
Phase 4: Rollback, wait 5 seconds
Phase 2: Execute Agent A → Failure (network timeout)
Phase 4: Rollback, wait 10 seconds
Phase 2: Execute Agent A → Success
Phase 3: Verify outputs
Phase 4: Merge
```

**Example**: API calls, external service dependencies

---

## Success Criteria

Execution complete when:

- ✅ Sessions created (isolated, configured, logged, checkpointed)
- ✅ Agents executed (all started, monitored, completed or failed explicitly)
- ✅ Outputs captured (logs, artifacts, .ctxpack contributions)
- ✅ Outputs validated (format correct, completeness verified, no corruption)
- ✅ Conflicts detected (file-level, semantic, dependency)
- ✅ Conflicts resolved (automated or manual resolution)
- ✅ .ctxpack merged (semantic graphs unified, validated)
- ✅ Merge verified (integration tests pass, quality gates met)
- ✅ System safe (rollback available, state consistent, checkpoint valid)
- ✅ Failures handled (retry, skip, replicate, or escalate)

---

## Integration with Main Orchestrator

**Handoff Pattern**:

```
Main Orchestrator:
  ├─→ Phase 1: Request Understanding
  ├─→ Phase 2: Task Decomposition
  ├─→ Phase 3: Specialist Assignment
  ├─→ Phase 4: Delegate to Terminal Orchestrator
  │   └─→ Terminal Orchestrator:
  │       ├─→ Phase 1: Setup tmux sessions
  │       ├─→ Phase 2: Execute and monitor agents
  │       ├─→ Phase 3: Validate outputs
  │       └─→ Phase 4: Merge and verify
  │   └─→ Returns: Integrated outputs + execution report
  └─→ Phase 5: Main Orchestrator verifies context coherence
```

**Input from Main Orchestrator**:
- Agent assignments (which agents, what tasks)
- Task boundaries (scope, success criteria)
- Dependency information (execution order)
- Merge strategy (how to integrate outputs)

**Output to Main Orchestrator**:
- Execution report (which agents succeeded/failed)
- Integrated outputs (merged files, .ctxpack)
- Failure details (for failed agents)
- Conflict resolutions (how conflicts were handled)

File: coordination/main-orchestrator-handoff.md

---

## File Reference Quick Links

**Session Management**:
- tmux/session-management.md
- tmux/session-configuration.md
- tmux/session-monitoring.md
- tmux/session-cleanup.md

**Monitoring**:
- monitoring/progress-tracking.md
- monitoring/failure-detection.md
- monitoring/completion-criteria.md
- monitoring/logging-patterns.md

**Verification**:
- verification/output-capture.md
- verification/output-validation.md
- verification/format-checking.md
- verification/success-criteria.md
- verification/corruption-detection.md

**Merge**:
- merge/conflict-detection.md
- merge/semantic-conflicts.md
- merge/resolution-strategies.md
- merge/conflict-prevention.md
- merge/ctxpack-integration.md
- merge/graph-operations.md
- merge/rollback-procedures.md
- merge/recovery-mechanisms.md

**Principles**:
- principles/session-isolation.md
- principles/full-logging.md
- principles/reproducibility.md
- principles/rollback-strategy.md

**Coordination**:
- coordination/main-orchestrator-handoff.md

---

**Architecture guides through execution phases without instructions. Each phase depends on previous artifacts. Agents execute in isolation with full logging. Outputs verified before merge. Rollback available on failure. Context coherence maintained throughout.**

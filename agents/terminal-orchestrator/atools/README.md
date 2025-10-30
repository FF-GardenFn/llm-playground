# Terminal Orchestrator Tools

Critical scripts for tmux session management, output capture, and semantic graph merging.

---

## Overview

This directory contains automation tools for the Terminal Orchestrator agent:

1. **tmux_manager.sh** - Create, monitor, and destroy tmux sessions for parallel agents
2. **output_capturer.py** - Capture and analyze agent outputs in real-time
3. **merge_coordinator.py** - Detect conflicts and merge .ctxpack semantic graphs

---

## Tool 1: tmux_manager.sh

### Purpose

Manage tmux sessions for parallel agent execution with isolation, monitoring, and cleanup.

### Usage

```bash
# Create session for an agent
./tmux_manager.sh create <agent-name> <workspace-dir> <command>

# List all active agent sessions
./tmux_manager.sh list

# Get session status
./tmux_manager.sh status <session-name>

# Capture session output
./tmux_manager.sh capture <session-name> <output-file>

# Destroy session and cleanup
./tmux_manager.sh destroy <session-name>

# Cleanup all orphaned sessions
./tmux_manager.sh cleanup-all
```

### Examples

```bash
# Create session for code-generator
./tmux_manager.sh create code-generator \
  /tmp/agent-workspaces/code-generator \
  "python agent.py --task generate-auth"

# Check status
./tmux_manager.sh status code-generator-20251028-143052

# Capture output
./tmux_manager.sh capture code-generator-20251028-143052 output.txt

# Destroy session
./tmux_manager.sh destroy code-generator-20251028-143052
```

### Features

- **Unique session naming** (agent-name-timestamp)
- **Workspace isolation** (separate directories per agent)
- **Environment configuration** (custom env vars per session)
- **Resource limits** (memory, CPU constraints)
- **Health monitoring** (detect hung/zombie sessions)
- **Automatic cleanup** (remove workspaces on destroy)

---

## Tool 2: output_capturer.py

### Purpose

Monitor agent execution in real-time, detect failures, and capture outputs for verification.

### Usage

```bash
# Monitor single agent
python output_capturer.py --session <session-name> --output <output-dir>

# Monitor multiple agents (parallel)
python output_capturer.py --sessions <session1> <session2> <session3> --output <output-dir>

# Monitor with timeout
python output_capturer.py --session <session-name> --timeout 1800  # 30 minutes

# Monitor with custom polling interval
python output_capturer.py --session <session-name> --interval 10  # 10 seconds
```

### Examples

```bash
# Monitor code-generator
python output_capturer.py \
  --session code-generator-20251028-143052 \
  --output /tmp/agent-outputs/code-generator

# Monitor 3 agents in parallel
python output_capturer.py \
  --sessions code-generator-20251028-143052 \
         code-reviewer-20251028-143053 \
         data-profiler-20251028-143054 \
  --output /tmp/agent-outputs

# Monitor with 30-minute timeout
python output_capturer.py \
  --session code-generator-20251028-143052 \
  --timeout 1800 \
  --output /tmp/agent-outputs/code-generator
```

### Features

- **Real-time output capture** (tmux pane capture + log tailing)
- **Failure detection** (error patterns, exit codes, timeouts)
- **Progress tracking** (parse status markers, progress indicators)
- **Structured logging** (JSON format with timestamps)
- **Completion detection** (recognize DONE markers, exit codes)
- **Resource monitoring** (CPU, memory, disk usage)

### Output Format

**Captured outputs** (per agent):
```
/tmp/agent-outputs/code-generator/
├── output.log          # Full stdout/stderr
├── status.json         # Structured status (progress, errors, completion)
├── errors.txt          # Extracted error messages
├── exit-code.txt       # Process exit code
└── .ctxpack            # Semantic graph contribution
```

**Status JSON format**:
```json
{
  "agent": "code-generator",
  "session": "code-generator-20251028-143052",
  "status": "completed",
  "start_time": "2025-10-28T14:30:52Z",
  "end_time": "2025-10-28T14:35:00Z",
  "duration_seconds": 248,
  "exit_code": 0,
  "progress": 100,
  "errors_detected": 0,
  "outputs_captured": [
    "output.log",
    ".ctxpack",
    "auth_module.py"
  ]
}
```

---

## Tool 3: merge_coordinator.py

### Purpose

Merge .ctxpack semantic graphs from multiple agents with conflict detection and validation.

### Usage

```bash
# Merge graphs from multiple agents
python merge_coordinator.py --agents <agent1> <agent2> <agent3> --output <merged.ctxpack>

# Merge with conflict resolution strategy
python merge_coordinator.py \
  --agents code-generator code-reviewer \
  --output merged.ctxpack \
  --strategy priority  # Options: priority, last-write-wins, manual

# Merge with validation only (no output)
python merge_coordinator.py --agents <agent1> <agent2> --validate-only

# Merge with detailed conflict report
python merge_coordinator.py \
  --agents <agent1> <agent2> \
  --output merged.ctxpack \
  --conflict-report conflicts.json
```

### Examples

```bash
# Merge 3 agent graphs
python merge_coordinator.py \
  --agents code-generator code-reviewer data-profiler \
  --output /tmp/agent-outputs/merged.ctxpack

# Merge with priority-based conflict resolution
python merge_coordinator.py \
  --agents code-generator code-reviewer \
  --output merged.ctxpack \
  --strategy priority \
  --priorities code-reviewer:2,code-generator:1

# Validate without merging
python merge_coordinator.py \
  --agents code-generator code-reviewer data-profiler \
  --validate-only
```

### Features

- **Multiple merge strategies** (union, overlay, topological)
- **Conflict detection** (attribute conflicts, edge conflicts, cycles)
- **Automatic resolution** (priority-based, last-write-wins, merge lists)
- **Manual escalation** (interactive conflict resolution)
- **Graph validation** (acyclicity, reference integrity, type consistency)
- **Detailed reporting** (conflicts detected, resolution applied, nodes/edges merged)

### Conflict Resolution Strategies

**Priority-based** (higher priority agent wins):
```bash
python merge_coordinator.py \
  --agents code-generator code-reviewer \
  --strategy priority \
  --priorities code-reviewer:2,code-generator:1
```

**Last-write-wins** (most recent agent wins):
```bash
python merge_coordinator.py \
  --agents code-generator code-reviewer \
  --strategy last-write-wins
```

**Manual** (interactive conflict resolution):
```bash
python merge_coordinator.py \
  --agents code-generator code-reviewer \
  --strategy manual
# Prompts user for each conflict
```

### Output Format

**Merged graph** (merged.ctxpack):
```json
{
  "metadata": {
    "merged_from": ["code-generator", "code-reviewer", "data-profiler"],
    "merge_strategy": "priority",
    "timestamp": "2025-10-28T14:36:00Z",
    "conflicts_detected": 2,
    "conflicts_resolved": 2
  },
  "nodes": [...],
  "edges": [...]
}
```

**Conflict report** (conflicts.json):
```json
{
  "conflicts": [
    {
      "type": "attribute_conflict",
      "node_id": "node-1",
      "attribute": "status",
      "source1": "code-generator",
      "value1": "implemented",
      "source2": "code-reviewer",
      "value2": "needs_review",
      "resolution": "value2",
      "strategy": "priority"
    }
  ],
  "summary": {
    "total_conflicts": 2,
    "auto_resolved": 2,
    "manual_resolved": 0,
    "unresolved": 0
  }
}
```

---

## Integration with Terminal Orchestrator

### Phase 1: Environment Setup

```bash
# Use tmux_manager.sh to create sessions
for agent in code-generator code-reviewer data-profiler; do
  ./tmux_manager.sh create "$agent" \
    "/tmp/agent-workspaces/$agent" \
    "python agent.py --task $TASK"
done
```

### Phase 2: Execution Monitoring

```bash
# Use output_capturer.py to monitor all agents
python output_capturer.py \
  --sessions code-generator-* code-reviewer-* data-profiler-* \
  --output /tmp/agent-outputs \
  --timeout 1800
```

### Phase 3: Output Verification

```bash
# Check captured outputs
for agent in code-generator code-reviewer data-profiler; do
  if [ -f "/tmp/agent-outputs/$agent/status.json" ]; then
    STATUS=$(jq -r '.status' "/tmp/agent-outputs/$agent/status.json")
    echo "$agent: $STATUS"
  fi
done
```

### Phase 4: Merge Strategy

```bash
# Use merge_coordinator.py to merge graphs
python merge_coordinator.py \
  --agents code-generator code-reviewer data-profiler \
  --output /tmp/agent-outputs/merged.ctxpack \
  --strategy priority \
  --priorities code-reviewer:2,code-generator:1,data-profiler:1 \
  --conflict-report /tmp/agent-outputs/conflicts.json
```

### Complete Workflow Script

```bash
#!/bin/bash
# orchestrate_agents.sh - Complete agent orchestration workflow

set -e

AGENTS=("code-generator" "code-reviewer" "data-profiler")
OUTPUT_DIR="/tmp/agent-outputs"
WORKSPACE_BASE="/tmp/agent-workspaces"

# Phase 1: Environment Setup
echo "Phase 1: Creating tmux sessions..."
for agent in "${AGENTS[@]}"; do
  ./tmux_manager.sh create "$agent" \
    "$WORKSPACE_BASE/$agent" \
    "python agent.py --task $TASK"
done

# Phase 2: Execution Monitoring
echo "Phase 2: Monitoring agent execution..."
python output_capturer.py \
  --sessions $(./tmux_manager.sh list | grep "^agent-" | tr '\n' ' ') \
  --output "$OUTPUT_DIR" \
  --timeout 1800

# Phase 3: Output Verification
echo "Phase 3: Verifying outputs..."
ALL_COMPLETED=true
for agent in "${AGENTS[@]}"; do
  STATUS_FILE="$OUTPUT_DIR/$agent/status.json"

  if [ ! -f "$STATUS_FILE" ]; then
    echo "ERROR: No status file for $agent"
    ALL_COMPLETED=false
    continue
  fi

  STATUS=$(jq -r '.status' "$STATUS_FILE")
  EXIT_CODE=$(jq -r '.exit_code' "$STATUS_FILE")

  echo "  $agent: $STATUS (exit code: $EXIT_CODE)"

  if [ "$STATUS" != "completed" ] || [ "$EXIT_CODE" != "0" ]; then
    ALL_COMPLETED=false
  fi
done

if [ "$ALL_COMPLETED" = false ]; then
  echo "ERROR: Not all agents completed successfully"
  exit 1
fi

# Phase 4: Merge Strategy
echo "Phase 4: Merging .ctxpack graphs..."
python merge_coordinator.py \
  --agents "${AGENTS[@]}" \
  --output "$OUTPUT_DIR/merged.ctxpack" \
  --strategy priority \
  --priorities code-reviewer:2,code-generator:1,data-profiler:1 \
  --conflict-report "$OUTPUT_DIR/conflicts.json"

echo "Orchestration complete!"
echo "  Merged graph: $OUTPUT_DIR/merged.ctxpack"
echo "  Conflict report: $OUTPUT_DIR/conflicts.json"

# Cleanup
echo "Cleaning up tmux sessions..."
for agent in "${AGENTS[@]}"; do
  SESSION=$(./tmux_manager.sh list | grep "^$agent-")
  ./tmux_manager.sh destroy "$SESSION"
done
```

---

## Error Handling

All tools follow consistent error handling:

1. **Exit codes**:
   - 0: Success
   - 1: General error
   - 2: Invalid arguments
   - 3: Resource unavailable (tmux, disk space, etc.)
   - 4: Timeout exceeded
   - 5: Validation failure

2. **Error messages**:
   - Descriptive error messages to stderr
   - JSON error format for programmatic parsing

3. **Cleanup on failure**:
   - tmux_manager.sh destroys sessions on error
   - output_capturer.py saves partial outputs before exit
   - merge_coordinator.py reports conflicts before aborting

---

## Dependencies

**tmux_manager.sh**:
- tmux (>= 2.0)
- bash (>= 4.0)
- coreutils (date, stat, grep, awk)

**output_capturer.py**:
- Python (>= 3.7)
- psutil (process monitoring)
- No external dependencies (uses subprocess, json, re from stdlib)

**merge_coordinator.py**:
- Python (>= 3.7)
- No external dependencies (uses json, argparse from stdlib)

---

## Testing

Run tests for each tool:

```bash
# Test tmux_manager.sh
./test_tmux_manager.sh

# Test output_capturer.py
python -m pytest test_output_capturer.py

# Test merge_coordinator.py
python -m pytest test_merge_coordinator.py
```

---

## Troubleshooting

### tmux_manager.sh issues

**Session creation fails**:
- Check if tmux server is running: `tmux info`
- Verify workspace directory exists and is writable
- Check for session name collisions: `tmux list-sessions`

**Cannot capture output**:
- Increase tmux history limit: `tmux set-option history-limit 50000`
- Ensure session is still active: `tmux has-session -t <session-name>`

### output_capturer.py issues

**Timeout too short**:
- Increase timeout: `--timeout 3600` (1 hour)
- Use adaptive timeout based on progress

**Missing dependencies**:
- Install psutil: `pip install psutil`

### merge_coordinator.py issues

**Conflicts unresolved**:
- Use manual strategy: `--strategy manual`
- Check conflict report: `--conflict-report conflicts.json`

**Graph validation fails**:
- Check for cycles: Graph must be acyclic
- Verify reference integrity: All edge endpoints must exist as nodes

---

## Best Practices

1. **Always cleanup sessions** after completion or failure
2. **Set reasonable timeouts** to prevent hung agents
3. **Use structured logging** (JSON format) for reliable parsing
4. **Monitor resource usage** to prevent system overload
5. **Validate merged graphs** before proceeding
6. **Keep conflict reports** for debugging and audit trails
7. **Test with small examples** before large-scale orchestration

---

## Future Enhancements

- **Docker integration** (run agents in containers)
- **Distributed execution** (agents on different machines)
- **Advanced scheduling** (priority queues, resource allocation)
- **Automatic retry** (transient failure recovery)
- **Real-time dashboard** (web UI for monitoring)

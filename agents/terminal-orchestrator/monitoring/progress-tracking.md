# Progress Tracking

Systematic monitoring of parallel agent execution through output polling, log analysis, completion detection, and failure identification.

---

## Table of Contents

1. [Output Polling Strategies](#output-polling-strategies)
2. [Log File Monitoring](#log-file-monitoring)
3. [Status Marker Detection](#status-marker-detection)
4. [Completion Criteria](#completion-criteria)
5. [Failure Detection Patterns](#failure-detection-patterns)
6. [Real-Time Streaming](#real-time-streaming)

---

## Output Polling Strategies

### Interval-Based Polling

**Pattern**: Capture tmux pane at regular intervals

**Basic Implementation**:
```bash
SESSION_NAME="code-generator-20251028-143052"
POLL_INTERVAL=5  # seconds

while true; do
  # Capture pane output
  tmux capture-pane -pt "${SESSION_NAME}" -S - > /tmp/current-output.txt

  # Check for completion
  if grep -q "DONE" /tmp/current-output.txt; then
    echo "Agent completed successfully"
    break
  fi

  # Check for errors
  if grep -qE "ERROR|FAILED|Exception" /tmp/current-output.txt; then
    echo "Agent encountered error"
    break
  fi

  sleep ${POLL_INTERVAL}
done
```

**Optimized with Change Detection**:
```bash
# Only process output if it changed
LAST_OUTPUT=""

while true; do
  CURRENT_OUTPUT=$(tmux capture-pane -pt "${SESSION_NAME}" -S - | tail -n 100)

  if [ "$CURRENT_OUTPUT" != "$LAST_OUTPUT" ]; then
    # Output changed, process new content
    echo "New output detected"

    # Check for completion/errors
    if echo "$CURRENT_OUTPUT" | grep -q "DONE"; then
      echo "Agent completed"
      break
    fi

    LAST_OUTPUT="$CURRENT_OUTPUT"
  fi

  sleep ${POLL_INTERVAL}
done
```

**Adaptive Polling** (adjust interval based on activity):
```bash
POLL_INTERVAL=5
MAX_INTERVAL=30
IDLE_COUNT=0

while true; do
  CURRENT_OUTPUT=$(tmux capture-pane -pt "${SESSION_NAME}" -S - | tail -n 100)

  if [ "$CURRENT_OUTPUT" != "$LAST_OUTPUT" ]; then
    # Activity detected, reset to fast polling
    POLL_INTERVAL=5
    IDLE_COUNT=0
    echo "Activity detected"
  else
    # No activity, slow down polling
    IDLE_COUNT=$((IDLE_COUNT + 1))
    if [ $IDLE_COUNT -ge 3 ] && [ $POLL_INTERVAL -lt $MAX_INTERVAL ]; then
      POLL_INTERVAL=$((POLL_INTERVAL + 5))
      echo "Slowing polling to ${POLL_INTERVAL}s"
    fi
  fi

  LAST_OUTPUT="$CURRENT_OUTPUT"
  sleep ${POLL_INTERVAL}
done
```

### Targeted Polling (Last N Lines Only)

**Rationale**: Most recent output contains status information

**Implementation**:
```bash
# Capture only last 50 lines (reduces processing)
tmux capture-pane -pt "${SESSION_NAME}" -S -50 > /tmp/recent-output.txt

# Parse for status
if grep -q "Progress: 100%" /tmp/recent-output.txt; then
  echo "Agent at 100% progress"
fi
```

**Incremental Capture** (only new lines since last poll):
```python
# Python approach with line tracking
import subprocess
import time

session_name = "code-generator-20251028-143052"
last_line_count = 0

while True:
    # Capture all output
    result = subprocess.run(
        ["tmux", "capture-pane", "-pt", session_name, "-S", "-"],
        capture_output=True, text=True
    )

    lines = result.stdout.split('\n')
    current_line_count = len(lines)

    # Process only new lines
    if current_line_count > last_line_count:
        new_lines = lines[last_line_count:]
        for line in new_lines:
            print(f"New: {line}")

            # Check for completion
            if "DONE" in line:
                print("Agent completed")
                break

        last_line_count = current_line_count

    time.sleep(5)
```

---

## Log File Monitoring

### Tail-Based Monitoring

**Basic tail**:
```bash
# Monitor log file in real-time
tail -f /tmp/agent-workspaces/code-generator/output.log
```

**With filtering** (only show warnings/errors):
```bash
tail -f /tmp/agent-workspaces/code-generator/output.log | grep -E "WARN|ERROR"
```

**With timestamps**:
```bash
tail -f /tmp/agent-workspaces/code-generator/output.log | \
  while IFS= read -r line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line"
  done
```

### Log File Polling

**Check for new content**:
```bash
LOG_FILE="/tmp/agent-workspaces/code-generator/output.log"
LAST_SIZE=0

while true; do
  if [ -f "${LOG_FILE}" ]; then
    CURRENT_SIZE=$(stat -c %s "${LOG_FILE}")

    if [ $CURRENT_SIZE -gt $LAST_SIZE ]; then
      # New content added
      tail -c +$((LAST_SIZE + 1)) "${LOG_FILE}"
      LAST_SIZE=$CURRENT_SIZE
    fi
  fi

  sleep 5
done
```

**Detect log rotation**:
```bash
# Handle case where log file is rotated/recreated
while true; do
  if [ -f "${LOG_FILE}" ]; then
    CURRENT_INODE=$(stat -c %i "${LOG_FILE}")

    if [ "${CURRENT_INODE}" != "${LAST_INODE}" ]; then
      echo "Log file rotated, reopening"
      LAST_SIZE=0
    fi

    LAST_INODE=$CURRENT_INODE
  fi

  # ... rest of polling logic
  sleep 5
done
```

### Structured Log Parsing (JSON)

**Example structured log**:
```json
{"timestamp": "2025-10-28T14:30:52Z", "level": "INFO", "message": "Agent started"}
{"timestamp": "2025-10-28T14:30:55Z", "level": "INFO", "message": "Processing file 1/10"}
{"timestamp": "2025-10-28T14:31:00Z", "level": "ERROR", "message": "Failed to parse file"}
{"timestamp": "2025-10-28T14:31:05Z", "level": "INFO", "message": "Agent completed"}
```

**Parse JSON logs**:
```python
import json
import time

log_file = "/tmp/agent-workspaces/code-generator/agent.log"
last_position = 0

while True:
    with open(log_file, 'r') as f:
        f.seek(last_position)

        for line in f:
            try:
                log_entry = json.loads(line.strip())

                # Process log entry
                if log_entry['level'] == 'ERROR':
                    print(f"ERROR detected: {log_entry['message']}")

                if log_entry['message'] == 'Agent completed':
                    print("Agent finished successfully")
                    break

            except json.JSONDecodeError:
                print(f"Malformed JSON: {line}")

        last_position = f.tell()

    time.sleep(5)
```

**Extract progress information**:
```python
# Agent logs progress as JSON
# {"event": "progress", "current": 5, "total": 10, "percent": 50}

def extract_progress(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('event') == 'progress':
                    return entry['percent']
            except json.JSONDecodeError:
                pass
    return 0

while True:
    progress = extract_progress(log_file)
    print(f"Progress: {progress}%")

    if progress >= 100:
        print("Agent completed")
        break

    time.sleep(5)
```

---

## Status Marker Detection

### Completion Markers

**Pattern**: Agent writes specific marker when done

**Simple marker**:
```bash
# Agent writes "DONE" to output
tmux capture-pane -pt "${SESSION_NAME}" -S - | grep -q "DONE"
```

**Structured marker** (JSON):
```python
# Agent writes: {"status": "completed", "timestamp": "2025-10-28T14:35:00Z"}

import json
import subprocess

def check_completion(session_name):
    result = subprocess.run(
        ["tmux", "capture-pane", "-pt", session_name, "-S", "-"],
        capture_output=True, text=True
    )

    for line in result.stdout.split('\n'):
        try:
            data = json.loads(line.strip())
            if data.get('status') == 'completed':
                return True, data.get('timestamp')
        except json.JSONDecodeError:
            pass

    return False, None

completed, timestamp = check_completion(session_name)
if completed:
    print(f"Agent completed at {timestamp}")
```

**Status file approach**:
```bash
# Agent writes to dedicated status file
STATUS_FILE="/tmp/agent-workspaces/code-generator/status.txt"

# Agent writes: "RUNNING", "COMPLETED", "FAILED"
while true; do
  if [ -f "${STATUS_FILE}" ]; then
    STATUS=$(cat "${STATUS_FILE}")

    case $STATUS in
      COMPLETED)
        echo "Agent completed successfully"
        break
        ;;
      FAILED)
        echo "Agent failed"
        break
        ;;
      RUNNING)
        echo "Agent still running..."
        ;;
    esac
  fi

  sleep 5
done
```

### Progress Markers

**Incremental progress**:
```bash
# Agent writes progress to file: "10", "20", "30", ...
PROGRESS_FILE="/tmp/agent-workspaces/code-generator/progress.txt"

while true; do
  if [ -f "${PROGRESS_FILE}" ]; then
    PROGRESS=$(cat "${PROGRESS_FILE}")
    echo "Progress: ${PROGRESS}%"

    if [ "$PROGRESS" -ge 100 ]; then
      echo "Agent completed"
      break
    fi
  fi

  sleep 5
done
```

**Task-based progress**:
```json
# Agent writes tasks to JSON file
{
  "total_tasks": 10,
  "completed_tasks": 5,
  "current_task": "Processing file 6",
  "percent_complete": 50
}
```

```python
import json

def get_progress(progress_file):
    try:
        with open(progress_file, 'r') as f:
            data = json.load(f)
            return data['percent_complete']
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 0

while True:
    progress = get_progress(progress_file)
    print(f"Progress: {progress}%")

    if progress >= 100:
        break

    time.sleep(5)
```

### Exit Code Detection

**Process exit code**:
```bash
# Wait for tmux session to finish
while tmux has-session -t "${SESSION_NAME}" 2>/dev/null; do
  sleep 5
done

# Session ended, check exit code
# Note: tmux doesn't directly expose exit code
# Workaround: Agent writes exit code to file

EXIT_CODE_FILE="/tmp/agent-workspaces/code-generator/exit-code.txt"
if [ -f "${EXIT_CODE_FILE}" ]; then
  EXIT_CODE=$(cat "${EXIT_CODE_FILE}")

  if [ "$EXIT_CODE" -eq 0 ]; then
    echo "Agent succeeded (exit code 0)"
  else
    echo "Agent failed (exit code $EXIT_CODE)"
  fi
fi
```

**Agent-side exit code capture**:
```bash
# In agent script
python agent.py
EXIT_CODE=$?

# Write exit code to file
echo $EXIT_CODE > /tmp/agent-workspaces/code-generator/exit-code.txt

# Exit with same code
exit $EXIT_CODE
```

---

## Completion Criteria

### Success Criteria Checklist

**Agent completed successfully if**:
- [ ] Exit code == 0 (or status file == "COMPLETED")
- [ ] Required outputs present (files, logs, .ctxpack)
- [ ] No error patterns detected in logs
- [ ] Completion marker present
- [ ] Performance benchmarks met (if applicable)

**Implementation**:
```python
def verify_completion(agent_name, session_name):
    workspace = f"/tmp/agent-workspaces/{agent_name}"

    # Check 1: Exit code
    exit_code_file = f"{workspace}/exit-code.txt"
    if not os.path.exists(exit_code_file):
        return False, "Exit code file not found"

    with open(exit_code_file, 'r') as f:
        exit_code = int(f.read().strip())

    if exit_code != 0:
        return False, f"Exit code non-zero: {exit_code}"

    # Check 2: Required outputs
    required_files = ["output.log", ".ctxpack"]
    for filename in required_files:
        if not os.path.exists(f"{workspace}/{filename}"):
            return False, f"Missing required file: {filename}"

    # Check 3: Error patterns
    with open(f"{workspace}/output.log", 'r') as f:
        log_content = f.read()
        if re.search(r'ERROR|FAILED|Exception', log_content):
            return False, "Error patterns detected in logs"

    # Check 4: Completion marker
    if "DONE" not in log_content:
        return False, "Completion marker not found"

    return True, "All criteria met"

success, message = verify_completion("code-generator", session_name)
print(f"Verification: {message}")
```

### Timeout Detection

**Maximum execution time**:
```bash
TIMEOUT=1800  # 30 minutes
START_TIME=$(date +%s)

while true; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))

  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo "Agent exceeded timeout (${TIMEOUT}s)"
    # Kill session
    tmux kill-session -t "${SESSION_NAME}"
    break
  fi

  # Check for completion
  if tmux capture-pane -pt "${SESSION_NAME}" -S - | grep -q "DONE"; then
    echo "Agent completed in ${ELAPSED}s"
    break
  fi

  sleep 5
done
```

**Per-task timeout** (agent reports progress):
```python
import time

max_idle_time = 300  # 5 minutes without progress
last_progress_time = time.time()
last_progress_value = 0

while True:
    current_progress = get_progress(progress_file)

    if current_progress > last_progress_value:
        # Progress made, reset timer
        last_progress_time = time.time()
        last_progress_value = current_progress

    # Check if idle too long
    idle_time = time.time() - last_progress_time
    if idle_time > max_idle_time:
        print(f"Agent idle for {idle_time}s, timing out")
        break

    time.sleep(10)
```

---

## Failure Detection Patterns

### Error Keyword Detection

**Common error patterns**:
```bash
# Scan logs for error keywords
ERROR_PATTERNS="ERROR|FAILED|Exception|Traceback|CRITICAL|Fatal"

if grep -qE "${ERROR_PATTERNS}" "${LOG_FILE}"; then
  echo "Error detected in logs"

  # Extract error context
  grep -A 5 -B 5 -E "${ERROR_PATTERNS}" "${LOG_FILE}" > error-context.txt
fi
```

**Categorize errors**:
```python
import re

def categorize_error(log_content):
    if re.search(r'FileNotFoundError|No such file', log_content):
        return "file_not_found"
    elif re.search(r'PermissionError|Permission denied', log_content):
        return "permission_error"
    elif re.search(r'TimeoutError|Timeout', log_content):
        return "timeout"
    elif re.search(r'ConnectionError|Network', log_content):
        return "network_error"
    elif re.search(r'MemoryError|Out of memory', log_content):
        return "out_of_memory"
    else:
        return "unknown_error"

with open(log_file, 'r') as f:
    content = f.read()
    error_type = categorize_error(content)
    print(f"Error type: {error_type}")
```

### Process State Detection

**Check if process is running**:
```bash
# Get pane PID
PANE_PID=$(tmux list-panes -t "${SESSION_NAME}" -F "#{pane_pid}")

# Check if PID exists
if ! ps -p "${PANE_PID}" > /dev/null; then
  echo "Process not running (PID ${PANE_PID} not found)"
fi
```

**Detect zombie processes**:
```bash
# Check process state
PROCESS_STATE=$(ps -o state= -p "${PANE_PID}")

case $PROCESS_STATE in
  Z)
    echo "Process is zombie"
    ;;
  D)
    echo "Process in uninterruptible sleep (likely hung)"
    ;;
  R|S)
    echo "Process running normally"
    ;;
esac
```

### Resource Exhaustion Detection

**Memory usage**:
```bash
# Check memory usage of agent process
MEM_PERCENT=$(ps -o %mem= -p "${PANE_PID}")

if (( $(echo "$MEM_PERCENT > 80" | bc -l) )); then
  echo "Agent using ${MEM_PERCENT}% memory (high)"
fi
```

**Disk space**:
```bash
# Check available disk space
DISK_AVAIL=$(df -h /tmp/agent-workspaces | awk 'NR==2 {print $4}' | sed 's/G//')

if (( $(echo "$DISK_AVAIL < 1" | bc -l) )); then
  echo "Low disk space (${DISK_AVAIL}GB available)"
fi
```

---

## Real-Time Streaming

### tmux pipe-pane

**Stream output to file in real-time**:
```bash
# Enable pipe-pane to capture all output
tmux pipe-pane -t "${SESSION_NAME}" 'cat >> output.log'

# Disable pipe-pane
tmux pipe-pane -t "${SESSION_NAME}"
```

**With timestamping**:
```bash
# Add timestamps to each line
tmux pipe-pane -t "${SESSION_NAME}" 'ts "[%Y-%m-%d %H:%M:%S]" >> output.log'
```

### Live Dashboard

**Monitor multiple agents** (simple bash version):
```bash
#!/bin/bash
# Live dashboard showing all agent statuses

while true; do
  clear
  echo "=== Agent Execution Dashboard ==="
  echo ""

  for session in $(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^agent-"); do
    # Get last line of output
    LAST_LINE=$(tmux capture-pane -pt "$session" -S - | tail -n 1)

    # Get session status
    if echo "$LAST_LINE" | grep -q "DONE"; then
      STATUS="✅ COMPLETED"
    elif echo "$LAST_LINE" | grep -qE "ERROR|FAILED"; then
      STATUS="❌ FAILED"
    else
      STATUS="⏳ RUNNING"
    fi

    echo "$session: $STATUS"
    echo "  Latest: $LAST_LINE"
    echo ""
  done

  sleep 5
done
```

---

## Best Practices

1. **Poll at reasonable intervals** (5-10 seconds typical, adjust based on agent runtime)
2. **Use adaptive polling** (speed up when activity detected, slow down when idle)
3. **Parse structured logs** (JSON format for reliable parsing)
4. **Monitor multiple signals** (exit codes, status files, error patterns)
5. **Set timeouts** (both maximum runtime and idle timeout)
6. **Detect resource exhaustion** (memory, disk, CPU)
7. **Log all monitoring activity** (create audit trail)
8. **Handle transient failures** (retry on network errors, etc.)

---

## Example: Complete Monitoring Script

See `atools/output_capturer.py` for full implementation of progress tracking, failure detection, and real-time monitoring.

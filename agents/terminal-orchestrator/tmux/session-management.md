# tmux Session Management

Systematic creation, configuration, monitoring, and cleanup of isolated tmux sessions for parallel agent execution.

---

## Table of Contents

1. [Session Creation Patterns](#session-creation-patterns)
2. [Isolation Techniques](#isolation-techniques)
3. [Resource Allocation](#resource-allocation)
4. [Session Lifecycle Management](#session-lifecycle-management)
5. [Common Issues & Solutions](#common-issues--solutions)

---

## Session Creation Patterns

### Naming Convention

**Format**: `<agent-name>-<timestamp>`

**Examples**:
```bash
code-generator-20251028-143052
code-reviewer-20251028-143053
data-profiler-20251028-143054
```

**Rationale**:
- Unique identifiers (timestamp prevents collisions)
- Descriptive (agent name immediately visible)
- Sortable (chronological ordering)
- Parseable (easy to extract agent name and timestamp)

### Basic Session Creation

**Detached session** (agent runs in background):
```bash
tmux new-session -d -s code-generator-20251028-143052
```

**With working directory**:
```bash
tmux new-session -d -s code-generator-20251028-143052 \
  -c /tmp/agent-workspaces/code-generator
```

**With initial command**:
```bash
tmux new-session -d -s code-generator-20251028-143052 \
  -c /tmp/agent-workspaces/code-generator \
  "python agent.py --task generate-auth"
```

### Advanced Session Configuration

**With environment variables**:
```bash
tmux new-session -d -s code-generator-20251028-143052 \
  -c /tmp/agent-workspaces/code-generator \
  "export PYTHONPATH=/custom/path; export LOG_LEVEL=DEBUG; python agent.py"
```

**With logging**:
```bash
tmux new-session -d -s code-generator-20251028-143052 \
  -c /tmp/agent-workspaces/code-generator \
  "python agent.py 2>&1 | tee output.log"
```

**With resource limits** (via ulimit):
```bash
tmux new-session -d -s code-generator-20251028-143052 \
  -c /tmp/agent-workspaces/code-generator \
  "ulimit -m 2097152; python agent.py"  # 2GB memory limit
```

---

## Isolation Techniques

### Process Isolation

**Guarantee**: Each agent runs in separate tmux session (separate process group)

**Benefits**:
- Agent A crash doesn't affect Agent B
- Can kill individual agents without affecting others
- Independent signal handling (SIGTERM, SIGKILL)

**Implementation**:
```bash
# Create sessions for 3 agents
tmux new-session -d -s agent-1
tmux new-session -d -s agent-2
tmux new-session -d -s agent-3

# Each session has separate process tree
pgrep -f agent-1  # Returns PID 1234
pgrep -f agent-2  # Returns PID 5678
pgrep -f agent-3  # Returns PID 9012
```

**Verification**:
```bash
# List all tmux sessions
tmux list-sessions
# Output:
# agent-1: 1 windows (created Tue Oct 28 14:30:52 2025)
# agent-2: 1 windows (created Tue Oct 28 14:30:53 2025)
# agent-3: 1 windows (created Tue Oct 28 14:30:54 2025)
```

### File System Isolation

**Guarantee**: Each agent has separate working directory

**Directory Structure**:
```
/tmp/agent-workspaces/
├── code-generator/
│   ├── workspace/       # Agent's scratch space
│   ├── output.log       # Agent's stdout/stderr
│   └── .ctxpack         # Agent's semantic graph
├── code-reviewer/
│   ├── workspace/
│   ├── output.log
│   └── .ctxpack
└── data-profiler/
    ├── workspace/
    ├── output.log
    └── .ctxpack
```

**Setup**:
```bash
# Create workspace directories
mkdir -p /tmp/agent-workspaces/{code-generator,code-reviewer,data-profiler}

# Set permissions (ensure isolation)
chmod 700 /tmp/agent-workspaces/code-generator
chmod 700 /tmp/agent-workspaces/code-reviewer
chmod 700 /tmp/agent-workspaces/data-profiler
```

**Benefits**:
- No file collisions (agents can't overwrite each other's files)
- Easy cleanup (delete directory after completion)
- Clear ownership (which agent created which files)

### Environment Isolation

**Guarantee**: Each agent has independent environment variables

**Critical Variables**:
- `PATH`: Custom tool paths per agent
- `PYTHONPATH`: Python module search paths
- `LOG_LEVEL`: Logging verbosity (DEBUG for troubleshooting)
- `TMPDIR`: Temporary file directory
- `API_KEYS`: Agent-specific API credentials

**Setup per session**:
```bash
tmux send-keys -t code-generator-20251028-143052 \
  "export PYTHONPATH=/custom/generator/path" C-m

tmux send-keys -t code-generator-20251028-143052 \
  "export LOG_LEVEL=DEBUG" C-m

tmux send-keys -t code-generator-20251028-143052 \
  "export TMPDIR=/tmp/agent-workspaces/code-generator/tmp" C-m
```

**Alternative: Environment file**:
```bash
# Create env file per agent
cat > /tmp/agent-workspaces/code-generator/.env <<EOF
PYTHONPATH=/custom/generator/path
LOG_LEVEL=DEBUG
TMPDIR=/tmp/agent-workspaces/code-generator/tmp
EOF

# Source in session
tmux send-keys -t code-generator-20251028-143052 \
  "source /tmp/agent-workspaces/code-generator/.env" C-m
```

### Logging Isolation

**Guarantee**: Each agent's logs stored separately

**Log Files**:
```
/tmp/agent-workspaces/code-generator/output.log   # stdout
/tmp/agent-workspaces/code-generator/error.log    # stderr
/tmp/agent-workspaces/code-generator/agent.log    # structured JSON logs
```

**Setup**:
```bash
# Redirect stdout and stderr to separate files
tmux send-keys -t code-generator-20251028-143052 \
  "python agent.py > output.log 2> error.log" C-m

# Alternative: Combined log with tee
tmux send-keys -t code-generator-20251028-143052 \
  "python agent.py 2>&1 | tee output.log" C-m
```

**Structured logging** (JSON format):
```python
# Inside agent.py
import json
import logging

# Configure JSON logging
logging.basicConfig(
    filename='agent.log',
    format='%(message)s',
    level=logging.DEBUG
)

# Log structured events
logging.info(json.dumps({
    "timestamp": "2025-10-28T14:30:52Z",
    "event": "agent_started",
    "agent": "code-generator",
    "task": "generate-auth"
}))
```

---

## Resource Allocation

### Memory Limits

**ulimit approach** (soft limit):
```bash
# 2GB memory limit
tmux send-keys -t agent-session "ulimit -m 2097152; python agent.py" C-m
```

**cgroups approach** (hard limit, requires root):
```bash
# Create cgroup for agent
sudo cgcreate -g memory:/agent-1
sudo cgset -r memory.limit_in_bytes=2147483648 agent-1  # 2GB

# Run agent in cgroup
sudo cgexec -g memory:agent-1 \
  tmux send-keys -t agent-session "python agent.py" C-m
```

**Docker approach** (containerized agents):
```bash
# Run agent in Docker container with memory limit
docker run --rm -m 2g \
  -v /tmp/agent-workspaces/code-generator:/workspace \
  agent-image python agent.py
```

### CPU Limits

**CPU affinity** (pin to specific cores):
```bash
# Pin to cores 0-3
taskset -c 0-3 python agent.py
```

**cgroups CPU shares**:
```bash
# Agent 1 gets 50% CPU, Agent 2 gets 50%
sudo cgcreate -g cpu:/agent-1
sudo cgcreate -g cpu:/agent-2
sudo cgset -r cpu.shares=512 agent-1
sudo cgset -r cpu.shares=512 agent-2
```

**nice priority** (lower priority for background agents):
```bash
# Lower priority (nice value 10)
nice -n 10 python agent.py
```

### Disk Space Limits

**Quota approach** (requires filesystem quota support):
```bash
# Set 10GB disk quota for agent workspace
sudo setquota -u agent-user 0 10485760 0 0 /tmp/agent-workspaces
```

**Monitoring approach** (check before execution):
```bash
# Check available disk space
df -h /tmp/agent-workspaces
# If < 5GB available, abort or cleanup
```

### Concurrent Session Limits

**Problem**: Too many parallel agents exhaust resources

**Solution**: Limit concurrent sessions
```bash
MAX_CONCURRENT_AGENTS=5

# Count active sessions
ACTIVE_COUNT=$(tmux list-sessions 2>/dev/null | grep -c "^agent-")

if [ $ACTIVE_COUNT -ge $MAX_CONCURRENT_AGENTS ]; then
  echo "Maximum concurrent agents reached ($MAX_CONCURRENT_AGENTS)"
  echo "Wait for some agents to complete"
  exit 1
fi

# Create new session
tmux new-session -d -s agent-new
```

---

## Session Lifecycle Management

### Session Creation Workflow

**Step 1: Prepare workspace**
```bash
AGENT_NAME="code-generator"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SESSION_NAME="${AGENT_NAME}-${TIMESTAMP}"
WORKSPACE="/tmp/agent-workspaces/${AGENT_NAME}"

# Create workspace directory
mkdir -p "${WORKSPACE}"/{workspace,logs}
```

**Step 2: Create tmux session**
```bash
tmux new-session -d -s "${SESSION_NAME}" -c "${WORKSPACE}"
```

**Step 3: Configure environment**
```bash
tmux send-keys -t "${SESSION_NAME}" "export LOG_LEVEL=DEBUG" C-m
tmux send-keys -t "${SESSION_NAME}" "export TMPDIR=${WORKSPACE}/tmp" C-m
```

**Step 4: Setup logging**
```bash
tmux send-keys -t "${SESSION_NAME}" \
  "exec > >(tee logs/output.log) 2>&1" C-m
```

**Step 5: Start agent**
```bash
tmux send-keys -t "${SESSION_NAME}" "python agent.py --task generate-auth" C-m
```

### Session Monitoring

**Check if session exists**:
```bash
if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
  echo "Session exists"
else
  echo "Session not found"
fi
```

**Check if process is running**:
```bash
# Capture pane and check for completion marker
tmux capture-pane -pt "${SESSION_NAME}" -S - > /tmp/session-output.txt
if grep -q "DONE" /tmp/session-output.txt; then
  echo "Agent completed"
fi
```

**Get exit code** (if process finished):
```bash
# tmux doesn't directly provide exit code, use workaround:
# Agent writes exit code to file
tmux send-keys -t "${SESSION_NAME}" "echo \$? > exit-code.txt" C-m
```

### Session Cleanup

**Destroy session**:
```bash
tmux kill-session -t "${SESSION_NAME}"
```

**Archive logs**:
```bash
# Compress and move logs
tar -czf "${WORKSPACE}.tar.gz" "${WORKSPACE}"
mv "${WORKSPACE}.tar.gz" /archive/agent-logs/
```

**Remove workspace**:
```bash
rm -rf "${WORKSPACE}"
```

**Full cleanup script**:
```bash
#!/bin/bash
SESSION_NAME="$1"
WORKSPACE="/tmp/agent-workspaces/$(echo $SESSION_NAME | cut -d'-' -f1)"

# Kill session if still running
if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
  tmux kill-session -t "${SESSION_NAME}"
fi

# Archive logs
tar -czf "${WORKSPACE}.tar.gz" "${WORKSPACE}"
mv "${WORKSPACE}.tar.gz" /archive/agent-logs/

# Remove workspace
rm -rf "${WORKSPACE}"

echo "Cleanup complete for ${SESSION_NAME}"
```

### Session Recovery (Failed Sessions)

**Detect hung sessions** (no output for N minutes):
```bash
LAST_MODIFIED=$(stat -c %Y "${WORKSPACE}/logs/output.log")
CURRENT_TIME=$(date +%s)
TIME_DIFF=$((CURRENT_TIME - LAST_MODIFIED))

if [ $TIME_DIFF -gt 600 ]; then  # 10 minutes
  echo "Session appears hung (no output for 10+ minutes)"
  # Kill and restart
  tmux kill-session -t "${SESSION_NAME}"
  # Restart logic here
fi
```

**Detect zombie sessions** (tmux session exists but process dead):
```bash
# Check if session has active process
PANE_PID=$(tmux list-panes -t "${SESSION_NAME}" -F "#{pane_pid}")
if ! ps -p "${PANE_PID}" > /dev/null; then
  echo "Zombie session detected (process ${PANE_PID} not running)"
  tmux kill-session -t "${SESSION_NAME}"
fi
```

---

## Common Issues & Solutions

### Issue 1: Session Creation Fails

**Symptom**: `tmux new-session` returns error

**Possible Causes**:
- tmux server not running
- Session name already exists
- Working directory doesn't exist
- Insufficient permissions

**Solutions**:
```bash
# Check if tmux server running
tmux info &> /dev/null || tmux start-server

# Check if session name exists
if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
  echo "Session name collision, generating new name"
  SESSION_NAME="${AGENT_NAME}-$(date +%Y%m%d-%H%M%S)-$$"
fi

# Create working directory if missing
mkdir -p "${WORKSPACE}"

# Check permissions
if [ ! -w "${WORKSPACE}" ]; then
  echo "No write permission to ${WORKSPACE}"
  exit 1
fi
```

### Issue 2: Output Not Captured

**Symptom**: `tmux capture-pane` returns empty or incomplete output

**Possible Causes**:
- History limit too small (pane scrollback buffer)
- Output not flushed to buffer
- Pane closed before capture

**Solutions**:
```bash
# Increase scrollback buffer
tmux set-option -t "${SESSION_NAME}" history-limit 50000

# Force flush before capture
tmux send-keys -t "${SESSION_NAME}" "" C-m
sleep 1  # Allow time to flush

# Capture entire history
tmux capture-pane -pt "${SESSION_NAME}" -S -
```

### Issue 3: Agent Doesn't Start

**Symptom**: Session created but agent process never starts

**Possible Causes**:
- Command syntax error
- Missing dependencies
- Environment not configured
- Shell initialization issues

**Solutions**:
```bash
# Test command outside tmux first
python agent.py --task generate-auth  # Verify it works

# Check tmux pane for errors
tmux capture-pane -pt "${SESSION_NAME}" -S -

# Send commands step-by-step (not all at once)
tmux send-keys -t "${SESSION_NAME}" "export PYTHONPATH=/custom/path" C-m
sleep 1
tmux send-keys -t "${SESSION_NAME}" "python agent.py" C-m
```

### Issue 4: Resource Exhaustion

**Symptom**: System becomes unresponsive, agents crash

**Possible Causes**:
- Too many concurrent agents
- Memory leaks
- Disk space exhaustion
- CPU thrashing

**Solutions**:
```bash
# Limit concurrent agents (see Resource Allocation section)
MAX_CONCURRENT=5

# Monitor resources before creating session
AVAILABLE_MEM=$(free -m | awk '/Mem:/ {print $7}')
if [ $AVAILABLE_MEM -lt 2048 ]; then  # Less than 2GB available
  echo "Insufficient memory, waiting for resources"
  exit 1
fi

# Set memory limits on agents
ulimit -m 2097152  # 2GB per agent

# Monitor and kill runaway processes
if ps aux | grep agent.py | awk '{sum+=$4} END {print sum}' | awk '$1 > 80'; then
  echo "Agents consuming >80% memory, killing sessions"
  # Cleanup logic
fi
```

### Issue 5: Session Orphaned After Disconnect

**Symptom**: Session still running but can't attach

**Possible Causes**:
- tmux server killed ungracefully
- Network disconnect (if remote)
- Terminal closed abruptly

**Solutions**:
```bash
# List all sessions (including orphaned)
tmux list-sessions

# Force attach to orphaned session
tmux attach-session -t "${SESSION_NAME}"

# If attach fails, kill and recreate
tmux kill-session -t "${SESSION_NAME}"
# Recreate session with saved state
```

---

## Best Practices

1. **Always use descriptive session names** (include agent name and timestamp)
2. **Always create separate working directories** (prevent file collisions)
3. **Always capture logs** (redirect stdout/stderr to files)
4. **Always set resource limits** (prevent resource exhaustion)
5. **Always cleanup sessions** (kill and remove workspaces after completion)
6. **Always verify session creation** (check if session exists before starting agent)
7. **Always monitor session health** (detect hung/zombie sessions)
8. **Always have rollback plan** (checkpoint before execution)

---

## Example: Complete Session Management Script

See `atools/tmux_manager.sh` for full implementation of session creation, monitoring, and cleanup.

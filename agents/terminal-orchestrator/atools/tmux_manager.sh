#!/bin/bash
# tmux_manager.sh - Create, monitor, and destroy tmux sessions for parallel agents
#
# Usage:
#   ./tmux_manager.sh create <agent-name> <workspace-dir> <command>
#   ./tmux_manager.sh list
#   ./tmux_manager.sh status <session-name>
#   ./tmux_manager.sh capture <session-name> <output-file>
#   ./tmux_manager.sh destroy <session-name>
#   ./tmux_manager.sh cleanup-all

set -euo pipefail

# Configuration
MAX_CONCURRENT_SESSIONS=10
SESSION_TIMEOUT=3600  # 1 hour
HISTORY_LIMIT=50000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

check_tmux() {
    if ! command -v tmux &> /dev/null; then
        log_error "tmux not found. Please install tmux."
        exit 3
    fi

    # Start tmux server if not running
    if ! tmux info &> /dev/null; then
        log_info "Starting tmux server..."
        tmux start-server
    fi
}

generate_session_name() {
    local agent_name="$1"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    echo "${agent_name}-${timestamp}"
}

check_session_limit() {
    local active_count=$(tmux list-sessions 2>/dev/null | grep -c "^agent-" || echo "0")

    if [ "$active_count" -ge "$MAX_CONCURRENT_SESSIONS" ]; then
        log_error "Maximum concurrent sessions reached ($MAX_CONCURRENT_SESSIONS)"
        log_error "Active sessions: $active_count"
        log_error "Use './tmux_manager.sh cleanup-all' to clean up orphaned sessions"
        exit 3
    fi
}

# Main functions

create_session() {
    if [ $# -lt 3 ]; then
        log_error "Usage: $0 create <agent-name> <workspace-dir> <command>"
        exit 2
    fi

    local agent_name="$1"
    local workspace_dir="$2"
    shift 2
    local command="$@"

    check_tmux
    check_session_limit

    # Generate unique session name
    local session_name=$(generate_session_name "$agent_name")

    # Verify workspace directory exists
    if [ ! -d "$workspace_dir" ]; then
        log_info "Creating workspace directory: $workspace_dir"
        mkdir -p "$workspace_dir"
    fi

    # Check write permissions
    if [ ! -w "$workspace_dir" ]; then
        log_error "No write permission to workspace: $workspace_dir"
        exit 3
    fi

    # Create tmux session
    log_info "Creating session: $session_name"
    log_info "Workspace: $workspace_dir"
    log_info "Command: $command"

    tmux new-session -d -s "$session_name" -c "$workspace_dir"

    # Configure session
    tmux set-option -t "$session_name" history-limit "$HISTORY_LIMIT"

    # Setup environment
    tmux send-keys -t "$session_name" "export AGENT_NAME='$agent_name'" C-m
    tmux send-keys -t "$session_name" "export SESSION_NAME='$session_name'" C-m
    tmux send-keys -t "$session_name" "export WORKSPACE_DIR='$workspace_dir'" C-m

    # Enable output logging
    tmux pipe-pane -t "$session_name" "cat >> '$workspace_dir/output.log'"

    # Create status file
    cat > "$workspace_dir/status.txt" <<EOF
RUNNING
EOF

    # Create metadata file
    cat > "$workspace_dir/metadata.json" <<EOF
{
  "agent": "$agent_name",
  "session": "$session_name",
  "workspace": "$workspace_dir",
  "created_at": "$(date -Iseconds)",
  "command": "$command"
}
EOF

    # Execute command
    tmux send-keys -t "$session_name" "$command" C-m

    # Add exit code capture at the end
    tmux send-keys -t "$session_name" "echo \$? > exit-code.txt" C-m
    tmux send-keys -t "$session_name" "echo COMPLETED > status.txt" C-m

    log_info "Session created successfully: $session_name"
    echo "$session_name"
}

list_sessions() {
    check_tmux

    local sessions=$(tmux list-sessions 2>/dev/null | grep "^agent-" || echo "")

    if [ -z "$sessions" ]; then
        log_info "No active agent sessions"
        return 0
    fi

    echo "Active agent sessions:"
    echo "$sessions" | while IFS= read -r line; do
        local session_name=$(echo "$line" | cut -d':' -f1)
        echo "  $session_name"
    done
}

get_status() {
    if [ $# -lt 1 ]; then
        log_error "Usage: $0 status <session-name>"
        exit 2
    fi

    local session_name="$1"

    check_tmux

    # Check if session exists
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        log_error "Session not found: $session_name"
        exit 1
    fi

    # Get metadata
    local workspace=$(tmux show-environment -t "$session_name" WORKSPACE_DIR 2>/dev/null | cut -d'=' -f2)

    if [ -z "$workspace" ]; then
        log_warn "Could not determine workspace directory"
        workspace="/tmp/agent-workspaces/$(echo $session_name | cut -d'-' -f1)"
    fi

    # Check if process is running
    local pane_pid=$(tmux list-panes -t "$session_name" -F "#{pane_pid}" 2>/dev/null)
    local process_state="unknown"

    if [ -n "$pane_pid" ] && ps -p "$pane_pid" > /dev/null 2>&1; then
        process_state=$(ps -o state= -p "$pane_pid")
    fi

    # Get status from file
    local status="UNKNOWN"
    if [ -f "$workspace/status.txt" ]; then
        status=$(cat "$workspace/status.txt")
    fi

    # Get exit code if available
    local exit_code="N/A"
    if [ -f "$workspace/exit-code.txt" ]; then
        exit_code=$(cat "$workspace/exit-code.txt")
    fi

    # Output status
    echo "Session: $session_name"
    echo "  Workspace: $workspace"
    echo "  Status: $status"
    echo "  Process PID: $pane_pid"
    echo "  Process State: $process_state"
    echo "  Exit Code: $exit_code"

    # Check for errors in output
    if [ -f "$workspace/output.log" ]; then
        local error_count=$(grep -cE "ERROR|FAILED|Exception" "$workspace/output.log" || echo "0")
        echo "  Errors Detected: $error_count"
    fi
}

capture_output() {
    if [ $# -lt 2 ]; then
        log_error "Usage: $0 capture <session-name> <output-file>"
        exit 2
    fi

    local session_name="$1"
    local output_file="$2"

    check_tmux

    # Check if session exists
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        log_error "Session not found: $session_name"
        exit 1
    fi

    log_info "Capturing output from $session_name to $output_file"

    # Capture pane content
    tmux capture-pane -pt "$session_name" -S - > "$output_file"

    log_info "Output captured ($(wc -l < "$output_file") lines)"
}

destroy_session() {
    if [ $# -lt 1 ]; then
        log_error "Usage: $0 destroy <session-name>"
        exit 2
    fi

    local session_name="$1"

    check_tmux

    # Check if session exists
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        log_warn "Session not found: $session_name"
        return 0
    fi

    log_info "Destroying session: $session_name"

    # Get workspace directory
    local workspace=$(tmux show-environment -t "$session_name" WORKSPACE_DIR 2>/dev/null | cut -d'=' -f2 || echo "")

    # Kill session
    tmux kill-session -t "$session_name"

    # Optional: Archive workspace (uncomment to enable)
    # if [ -n "$workspace" ] && [ -d "$workspace" ]; then
    #     local archive_dir="/tmp/agent-archives"
    #     mkdir -p "$archive_dir"
    #     tar -czf "$archive_dir/${session_name}.tar.gz" -C "$(dirname "$workspace")" "$(basename "$workspace")"
    #     log_info "Workspace archived to $archive_dir/${session_name}.tar.gz"
    # fi

    log_info "Session destroyed successfully"
}

cleanup_all() {
    check_tmux

    log_info "Cleaning up all agent sessions..."

    local sessions=$(tmux list-sessions 2>/dev/null | grep "^agent-" | cut -d':' -f1 || echo "")

    if [ -z "$sessions" ]; then
        log_info "No agent sessions to clean up"
        return 0
    fi

    local count=0
    echo "$sessions" | while IFS= read -r session_name; do
        # Check if session is hung (no output for SESSION_TIMEOUT seconds)
        local workspace=$(tmux show-environment -t "$session_name" WORKSPACE_DIR 2>/dev/null | cut -d'=' -f2 || echo "")

        if [ -n "$workspace" ] && [ -f "$workspace/output.log" ]; then
            local last_modified=$(stat -c %Y "$workspace/output.log" 2>/dev/null || echo "0")
            local current_time=$(date +%s)
            local time_diff=$((current_time - last_modified))

            if [ "$time_diff" -gt "$SESSION_TIMEOUT" ]; then
                log_warn "Session $session_name appears hung (no output for ${time_diff}s)"
                destroy_session "$session_name"
                count=$((count + 1))
            fi
        fi
    done

    log_info "Cleaned up $count hung sessions"
}

# Main entry point

case "${1:-}" in
    create)
        shift
        create_session "$@"
        ;;
    list)
        list_sessions
        ;;
    status)
        shift
        get_status "$@"
        ;;
    capture)
        shift
        capture_output "$@"
        ;;
    destroy)
        shift
        destroy_session "$@"
        ;;
    cleanup-all)
        cleanup_all
        ;;
    *)
        echo "Usage: $0 {create|list|status|capture|destroy|cleanup-all}"
        echo ""
        echo "Commands:"
        echo "  create <agent-name> <workspace-dir> <command>  Create new agent session"
        echo "  list                                           List all active sessions"
        echo "  status <session-name>                          Get session status"
        echo "  capture <session-name> <output-file>           Capture session output"
        echo "  destroy <session-name>                         Destroy session"
        echo "  cleanup-all                                    Cleanup hung sessions"
        exit 2
        ;;
esac

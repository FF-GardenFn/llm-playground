#!/usr/bin/env python3
"""
output_capturer.py - Monitor agent execution in real-time with failure detection

Usage:
    python output_capturer.py --session <session-name> --output <output-dir>
    python output_capturer.py --sessions <session1> <session2> --output <output-dir>
    python output_capturer.py --session <session-name> --timeout 1800
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class OutputCapturer:
    """Capture and analyze agent outputs with failure detection"""

    # Error patterns to detect failures
    ERROR_PATTERNS = [
        r'ERROR',
        r'FAILED',
        r'Exception',
        r'Traceback',
        r'CRITICAL',
        r'Fatal',
        r'Segmentation fault',
        r'core dumped'
    ]

    # Completion markers
    COMPLETION_MARKERS = [
        r'DONE',
        r'COMPLETED',
        r'SUCCESS',
        r'Finished successfully'
    ]

    def __init__(self, session_name: str, output_dir: str, poll_interval: int = 5):
        self.session_name = session_name
        self.output_dir = Path(output_dir)
        self.poll_interval = poll_interval

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Output files
        self.output_log = self.output_dir / "output.log"
        self.status_file = self.output_dir / "status.json"
        self.errors_file = self.output_dir / "errors.txt"
        self.exit_code_file = self.output_dir / "exit-code.txt"

        # Tracking state
        self.start_time = datetime.utcnow()
        self.last_output = ""
        self.last_line_count = 0
        self.error_count = 0
        self.status = "running"

    def session_exists(self) -> bool:
        """Check if tmux session exists"""
        result = subprocess.run(
            ["tmux", "has-session", "-t", self.session_name],
            capture_output=True
        )
        return result.returncode == 0

    def capture_pane(self) -> str:
        """Capture tmux pane output"""
        if not self.session_exists():
            return ""

        result = subprocess.run(
            ["tmux", "capture-pane", "-pt", self.session_name, "-S", "-"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Warning: Failed to capture pane: {result.stderr}", file=sys.stderr)
            return ""

        return result.stdout

    def get_process_info(self) -> Tuple[Optional[int], Optional[str]]:
        """Get process PID and state"""
        if not self.session_exists():
            return None, None

        # Get pane PID
        result = subprocess.run(
            ["tmux", "list-panes", "-t", self.session_name, "-F", "#{pane_pid}"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None, None

        try:
            pid = int(result.stdout.strip())
        except ValueError:
            return None, None

        # Check if process is running
        result = subprocess.run(
            ["ps", "-o", "state=", "-p", str(pid)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return pid, "not_running"

        state = result.stdout.strip()
        return pid, state

    def detect_errors(self, output: str) -> List[str]:
        """Detect error patterns in output"""
        errors = []

        for pattern in self.ERROR_PATTERNS:
            matches = re.finditer(pattern, output, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Extract context (line with error + 2 lines before/after)
                lines = output[:match.start()].split('\n')
                start_line = max(0, len(lines) - 3)
                context_lines = lines[start_line:]

                # Add matched line
                matched_line = output[match.start():].split('\n')[0]
                context_lines.append(matched_line)

                # Add lines after
                after_lines = output[match.end():].split('\n')[1:3]
                context_lines.extend(after_lines)

                error_context = '\n'.join(context_lines)
                if error_context not in errors:
                    errors.append(error_context)

        return errors

    def detect_completion(self, output: str) -> bool:
        """Detect completion markers"""
        for pattern in self.COMPLETION_MARKERS:
            if re.search(pattern, output, re.IGNORECASE):
                return True
        return False

    def get_progress(self, output: str) -> Optional[int]:
        """Extract progress percentage from output"""
        # Look for patterns like "Progress: 75%", "75% complete", etc.
        patterns = [
            r'Progress:\s*(\d+)%',
            r'(\d+)%\s*complete',
            r'(\d+)/(\d+)\s*\((\d+)%\)',
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (IndexError, ValueError):
                    pass

        return None

    def read_exit_code(self) -> Optional[int]:
        """Read exit code from workspace"""
        # Try multiple locations for exit code
        workspace = self.output_dir
        exit_code_paths = [
            workspace / "exit-code.txt",
            workspace.parent / self.session_name.split('-')[0] / "exit-code.txt"
        ]

        for path in exit_code_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        return int(f.read().strip())
                except (ValueError, IOError):
                    pass

        return None

    def update_status(self, output: str, pid: Optional[int], process_state: Optional[str]) -> None:
        """Update status JSON file"""
        # Detect errors
        errors = self.detect_errors(output)
        if errors:
            self.error_count = len(errors)

            # Write errors to file
            with open(self.errors_file, 'w') as f:
                f.write('\n\n---\n\n'.join(errors))

        # Detect completion
        completed = self.detect_completion(output)

        # Get progress
        progress = self.get_progress(output)

        # Check exit code
        exit_code = self.read_exit_code()

        # Determine status
        if exit_code is not None:
            if exit_code == 0:
                self.status = "completed"
            else:
                self.status = "failed"
        elif completed:
            self.status = "completed"
        elif self.error_count > 0:
            self.status = "error"
        elif process_state == "not_running":
            self.status = "stopped"
        elif process_state in ["Z", "D"]:
            self.status = "hung"
        else:
            self.status = "running"

        # Calculate duration
        duration = (datetime.utcnow() - self.start_time).total_seconds()

        # Build status object
        status_obj = {
            "agent": self.session_name.split('-')[0],
            "session": self.session_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() + "Z",
            "duration_seconds": int(duration),
            "process_pid": pid,
            "process_state": process_state,
            "exit_code": exit_code,
            "progress": progress,
            "errors_detected": self.error_count,
            "last_update": datetime.utcnow().isoformat() + "Z"
        }

        # Add end time if completed
        if self.status in ["completed", "failed", "stopped"]:
            status_obj["end_time"] = datetime.utcnow().isoformat() + "Z"

        # Write status file
        with open(self.status_file, 'w') as f:
            json.dump(status_obj, f, indent=2)

    def monitor(self, timeout: Optional[int] = None) -> bool:
        """
        Monitor session until completion or timeout.

        Returns:
            True if agent completed successfully, False otherwise
        """
        print(f"Monitoring session: {self.session_name}")
        print(f"Output directory: {self.output_dir}")
        print(f"Poll interval: {self.poll_interval}s")

        if timeout:
            print(f"Timeout: {timeout}s")

        start_time = time.time()
        last_output_time = start_time

        while True:
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                print(f"\nTimeout exceeded ({timeout}s)")
                self.status = "timeout"
                return False

            # Check if session still exists
            if not self.session_exists():
                print(f"\nSession ended")
                break

            # Capture output
            current_output = self.capture_pane()

            # Check for new output
            if current_output != self.last_output:
                last_output_time = time.time()

                # Write to log file
                with open(self.output_log, 'w') as f:
                    f.write(current_output)

                # Get incremental lines
                current_lines = current_output.split('\n')
                if len(current_lines) > self.last_line_count:
                    new_lines = current_lines[self.last_line_count:]
                    for line in new_lines:
                        if line.strip():
                            print(f"  {line}")

                    self.last_line_count = len(current_lines)

                self.last_output = current_output

            # Get process info
            pid, process_state = self.get_process_info()

            # Update status
            self.update_status(current_output, pid, process_state)

            # Check for completion
            if self.status in ["completed", "failed", "stopped"]:
                print(f"\nAgent {self.status}")
                break

            # Check for hung process (no output for 5 minutes)
            if (time.time() - last_output_time) > 300:
                print(f"\nWarning: No output for 5 minutes (possible hung process)")
                if self.status == "running":
                    self.status = "hung"

            time.sleep(self.poll_interval)

        # Final status update
        final_output = self.capture_pane()
        pid, process_state = self.get_process_info()
        self.update_status(final_output, pid, process_state)

        # Write final output
        with open(self.output_log, 'w') as f:
            f.write(final_output)

        print(f"\nFinal status: {self.status}")
        print(f"Errors detected: {self.error_count}")

        return self.status == "completed"


def monitor_multiple(session_names: List[str], output_base_dir: str,
                     timeout: Optional[int] = None, poll_interval: int = 5) -> Dict[str, bool]:
    """
    Monitor multiple sessions in parallel.

    Returns:
        Dict mapping session name to success status
    """
    import threading

    results = {}
    threads = []

    def monitor_session(session_name: str):
        output_dir = Path(output_base_dir) / session_name.split('-')[0]
        capturer = OutputCapturer(session_name, str(output_dir), poll_interval)
        results[session_name] = capturer.monitor(timeout)

    # Start monitoring threads
    for session_name in session_names:
        thread = threading.Thread(target=monitor_session, args=(session_name,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Monitor agent execution in real-time with failure detection"
    )

    # Session arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--session", help="Single session to monitor")
    group.add_argument("--sessions", nargs='+', help="Multiple sessions to monitor")

    # Output arguments
    parser.add_argument("--output", required=True, help="Output directory")

    # Monitoring arguments
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval (default: 5s)")

    args = parser.parse_args()

    # Single session
    if args.session:
        capturer = OutputCapturer(args.session, args.output, args.interval)
        success = capturer.monitor(args.timeout)
        sys.exit(0 if success else 1)

    # Multiple sessions
    else:
        results = monitor_multiple(args.sessions, args.output, args.timeout, args.interval)

        print("\n" + "=" * 60)
        print("Summary:")
        for session, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {session}: {'completed' if success else 'failed'}")

        all_success = all(results.values())
        sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()

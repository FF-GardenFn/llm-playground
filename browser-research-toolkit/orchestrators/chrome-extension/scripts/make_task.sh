#!/usr/bin/env bash
# Thin wrapper for orchestrator
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR%/scripts}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found in PATH" >&2
  exit 127
fi

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 \"<Task Title>\" domain1 [domain2 ...]" >&2
  exit 1
fi

python3 "$ROOT_DIR/orchestrator.py" "$@"

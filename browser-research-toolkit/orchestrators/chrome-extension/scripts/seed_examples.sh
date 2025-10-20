#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR%/scripts}"
EX_DIR="$ROOT_DIR/examples/tasks"
DEST="$HOME/.tab_orchestrator/tasks"

if [ ! -d "$EX_DIR" ]; then
  echo "Error: examples directory not found at $EX_DIR" >&2
  exit 1
fi

mkdir -p "$DEST"
# Use null-delimited find to handle spaces/newlines in paths
find "$EX_DIR" -maxdepth 1 -mindepth 1 -type d -print0 | while IFS= read -r -d '' t; do
  slug="$(basename "$t")_$(date +%Y%m%d)"
  td="$DEST/$slug"
  mkdir -p "$td"
  cp -a "$t"/. "$td/"
  echo "Seeded $td"
done

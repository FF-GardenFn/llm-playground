#!/usr/bin/env bash
# Security scanning using bandit (Python), npm audit (JS), etc.
set -euo pipefail

target="${1:-.}"

if find "$target" -name "*.py" 2>/dev/null | grep -q .; then
    echo "[INFO] Running Bandit security scan..."
    if command -v bandit &> /dev/null; then
        bandit -r "$target" -f json 2>/dev/null || true
    else
        echo "[WARN] Bandit not installed (pip install bandit)"
    fi
fi

if [[ -f "package.json" ]]; then
    echo "[INFO] Running npm audit..."
    npm audit --json 2>/dev/null || true
fi

echo "[INFO] Security scan complete"

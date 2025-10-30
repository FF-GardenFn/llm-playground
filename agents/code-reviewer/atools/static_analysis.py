#!/usr/bin/env python3
"""Run static analysis tools on code (pylint, mypy, etc.)"""
import subprocess
import sys
import json
from pathlib import Path

def run_analysis(target_path):
    results = {"issues": [], "summary": {}}
    target = Path(target_path)

    # Python analysis
    if target.suffix == '.py' or any(target.rglob('*.py')):
        # Try pylint
        try:
            result = subprocess.run(
                ['pylint', str(target), '--output-format=json'],
                capture_output=True, text=True
            )
            if result.stdout:
                issues = json.loads(result.stdout)
                results["issues"].extend(issues)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Try mypy
        try:
            result = subprocess.run(
                ['mypy', str(target), '--no-error-summary'],
                capture_output=True, text=True
            )
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        results["issues"].append({"type": "mypy", "message": line})
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    results["summary"] = {
        "total_issues": len(results["issues"]),
        "by_severity": {}
    }

    print(json.dumps(results, indent=2))
    return 0 if not results["issues"] else 1

if __name__ == "__main__":
    sys.exit(run_analysis(sys.argv[1] if len(sys.argv) > 1 else "."))

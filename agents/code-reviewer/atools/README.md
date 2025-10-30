# Code Reviewer Agent Tools

Tools for comprehensive code review focusing on security, quality, and performance.

## Tools

- **static_analysis.py**: Run pylint, mypy, and other static analyzers
- **security_scan.sh**: Security scanning with Bandit, npm audit
- **complexity_analyzer.py**: Code complexity metrics
- **dependency_audit.sh**: Check for vulnerable dependencies

## Usage

```bash
# Run static analysis
python static_analysis.py src/

# Security scan
bash security_scan.sh src/

# Check dependencies
bash dependency_audit.sh
```

## Dependencies
```bash
pip install pylint mypy bandit safety
```

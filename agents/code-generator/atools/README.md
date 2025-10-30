# Code Generator Agent Tools

This directory contains tools for the code-generator agent to use when implementing features.

## Available Tools

### search_codebase.py
Search for patterns, classes, functions, and imports in the codebase.

**Usage:**
```bash
# Search for pattern
python search_codebase.py --pattern "User.*Auth"

# Find class definition
python search_codebase.py --class "UserService"

# Find function
python search_codebase.py --function "validate_email"

# Analyze structure
python search_codebase.py --analyze --file-pattern "*.py"
```

**Purpose:** Help agents understand codebase structure, find existing patterns, and identify integration points before writing code.

### run_tests.sh
Execute test suites with appropriate test frameworks.

**Usage:**
```bash
# Run all tests
bash run_tests.sh tests/

# Run with coverage
bash run_tests.sh -c tests/

# Run specific test file
bash run_tests.sh tests/test_user.py

# Run tests matching pattern
bash run_tests.sh -k "test_validation"
```

**Supported Frameworks:** pytest, jest, go test, unittest

**Purpose:** Verify implementations don't break existing functionality and new code works as expected.

### lint_code.sh
Check code style and quality with language-appropriate linters.

**Usage:**
```bash
# Lint specific file
bash lint_code.sh src/user.py

# Lint directory
bash lint_code.sh src/
```

**Supported Languages:** Python (flake8/pylint), JavaScript/TypeScript (eslint), Go (golint/go vet)

**Purpose:** Ensure code follows style guidelines and catches common issues.

## Tool Usage Guidelines

1. **Always search first**: Use `search_codebase.py` before writing code to understand existing patterns
2. **Test frequently**: Run `run_tests.sh` after each significant change
3. **Lint before completing**: Use `lint_code.sh` before marking work as done
4. **Read tool output carefully**: Interpret results in context of the task

## Dependencies

- Python 3.7+ (for Python tools)
- pytest (for Python testing)
- flake8 or pylint (for Python linting)
- Node.js/npm (for JavaScript testing/linting)
- Go (for Go testing/linting)

Install Python dependencies:
```bash
pip install pytest flake8 coverage
```

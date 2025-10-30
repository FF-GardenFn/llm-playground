---
description: List available tools and their usage
allowed-tools: Read
argument-hint: [--tool-name]
---

# Tools Command

Display available tools with usage patterns and phase mapping.

## What this does

1. **Lists all tools** - Shows tool inventory with purposes
2. **Shows phase mapping** - When to use each tool
3. **Displays usage patterns** - Common invocation examples
4. **References detailed docs** - Points to SKILLS.md for depth

## Usage

```bash
# List all tools
/tools

# Show specific tool details
/tools search_codebase
/tools run_tests
/tools lint_code
/tools analyze_complexity
```

## Available Tools

### 1. search_codebase.py
**Phase**: Reconnaissance
**Purpose**: Find similar implementations, identify conventions

**Usage**:
```bash
python ../atools/search_codebase.py --pattern "validation"
python ../atools/search_codebase.py --pattern "authentication"
python ../atools/search_codebase.py --file-type "test"
```

**When to Use**:
- Phase 1 (Reconnaissance): Always use first to understand codebase
- Finding similar features
- Identifying naming conventions
- Locating existing utilities to reuse
- Discovering testing patterns

---

### 2. run_tests.sh
**Phase**: Implementation, Validation
**Purpose**: Verify no breakage, ensure all tests pass

**Usage**:
```bash
bash ../atools/run_tests.sh  # Run all tests
bash ../atools/run_tests.sh tests/test_validators.py  # Specific test file
bash ../atools/run_tests.sh tests/test_validators.py::test_validate_email  # Specific test
```

**When to Use**:
- Phase 3 (Implementation): After each TDD cycle (continuously)
- Phase 4 (Validation): Final verification before completion
- After any code change
- To verify no regressions

---

### 3. lint_code.sh
**Phase**: Validation
**Purpose**: Code quality verification, auto-fix formatting

**Usage**:
```bash
bash ../atools/lint_code.sh  # Lint all code
bash ../atools/lint_code.sh auth/validators.py  # Lint specific file
bash ../atools/lint_code.sh --fix  # Auto-fix issues
```

**When to Use**:
- Phase 4 (Validation): Before declaring complete
- After implementation to clean code
- To ensure consistency with codebase style
- To catch common mistakes

---

### 4. analyze_complexity.py
**Phase**: Validation
**Purpose**: Complexity assessment (target: cyclomatic complexity <10)

**Usage**:
```bash
python ../atools/analyze_complexity.py auth/validators.py
python ../atools/analyze_complexity.py --threshold 10
python ../atools/analyze_complexity.py --all  # Analyze entire codebase
```

**When to Use**:
- Phase 4 (Validation): Verify maintainability
- After refactoring to measure improvement
- To identify overly complex functions
- Before code review

---

## Tool-to-Phase Mapping

| Tool | Reconnaissance | Design | Implementation | Validation |
|------|:--------------:|:------:|:--------------:|:----------:|
| search_codebase.py | ✓ | | | |
| run_tests.sh | | | ✓ | ✓ |
| lint_code.sh | | | | ✓ |
| analyze_complexity.py | | | | ✓ |

## Detailed Documentation

For comprehensive tool documentation including:
- WHEN to use each tool
- HOW to interpret results
- WHAT to do with findings
- WHY tools are structured this way
- Common scenarios
- Troubleshooting
- Advanced patterns

**See**: `../SKILLS.md` (626 lines of tool encyclopedia)

## Tool Chaining Patterns

**Pattern 1: Reconnaissance Flow**
```bash
# Find similar code
python ../atools/search_codebase.py --pattern "validation"

# Read similar files
# (Read tool to examine found files)

# Document findings
# (Write reconnaissance_report.md)
```

**Pattern 2: TDD Cycle**
```bash
# Write test (Edit tool)
# Write code (Edit tool)
# Run test
bash ../atools/run_tests.sh tests/test_validators.py
# Refactor if needed
# Run tests again
bash ../atools/run_tests.sh
```

**Pattern 3: Validation Flow**
```bash
# Run all tests
bash ../atools/run_tests.sh

# Lint code
bash ../atools/lint_code.sh auth/validators.py

# Check complexity
python ../atools/analyze_complexity.py auth/validators.py

# Review checklist
# (Read ../phases/04_validation/checklist.md)
```

---

**For detailed tool usage, troubleshooting, and advanced patterns:**
→ Read `../SKILLS.md`

# Validation Phase

## Purpose
Systematic verification before declaring task complete. Production readiness assessment.

## Key Activities
- Run full test suite (verify no regressions)
- Lint and style check (code quality)
- Complexity analysis (maintainability)
- Edge case verification (robustness)
- Performance check (no obvious bottlenecks)

## Input Dependencies
Requires: `../03_implementation/outputs/` (code/, tests/, test_results.md)

Cannot validate without complete implementation.

## Available Tools
- **run_tests.sh** - Full test suite execution
- **lint_code.sh** - Code quality verification
- **analyze_complexity.py** - Complexity assessment
  - See SKILLS.md for thresholds and interpretation

## Output Artifact
Creates: `outputs/validation_report.md`

Must document:
- All tests pass (no regressions)
- Linting clean
- Complexity acceptable
- Edge cases handled
- All success criteria met

## Checklist
See: checklist.md for completion requirements

## Example
See: example_validation.md for complete demonstration

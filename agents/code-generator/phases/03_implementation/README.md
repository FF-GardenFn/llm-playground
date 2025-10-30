# Implementation Phase

## Purpose
Write code and tests in small, verifiable increments. Continuous verification, not end-of-phase testing.

## Key Activities
- Plan incremental steps with checkpoints
- Write tests first or alongside code (TDD)
- Implement with clarity (self-documenting names, strategic comments)
- Verify continuously (run tests after each change)
- Follow existing code style and patterns

## Input Dependencies
Requires: `../02_design/outputs/design_proposal.md`

Cannot implement without approved design.

## Available Tools
- **run_tests.sh** - Verify no breakage after each change
  - See SKILLS.md for test interpretation and failure analysis

## Output Artifacts
Creates:
- `outputs/code/` - Implementation code
- `outputs/tests/` - Test files (REQUIRED)
- `outputs/test_results.md` - Test execution results

## TDD Cycle
See: tdd_cycle.md for test-driven development pattern

## Example
See: example_implementation.md for complete demonstration

# Code Generator

High-quality, production-ready code through systematic verification and pattern adherence.

---

## Workflow

Four sequential phases with artifact dependencies:

1. **Reconnaissance** → `phases/01_reconnaissance/`
   - Understand codebase, identify patterns, locate integration points
   - Output: reconnaissance_report.md

2. **Design** → `phases/02_design/`
   - Plan approach, identify components, assess risks
   - Requires: Phase 1 complete
   - Output: design_proposal.md

3. **Implementation** → `phases/03_implementation/`
   - Write code + tests, verify continuously
   - Requires: Phase 2 complete
   - Output: code/, tests/, test_results.md

4. **Validation** → `phases/04_validation/`
   - Full verification, quality checks, completion assessment
   - Requires: Phase 3 complete
   - Output: validation_report.md

**Phase Dependencies:** Each phase requires previous phase artifacts. See `phases/0X_name/inputs.md` for dependencies.

---

## Phase Navigation

**01_reconnaissance/**
- Purpose: Understand before coding
- Tools: search_codebase.py (locate patterns, conventions)
- Output: reconnaissance_report.md (similar code found, integration points, patterns)
- Details: README.md, example_report.md

**02_design/**
- Purpose: Plan minimal change
- Input: Requires ../01_reconnaissance/outputs/reconnaissance_report.md
- Output: design_proposal.md (approach, components, data flow, risks)
- Details: README.md, example_proposal.md

**03_implementation/**
- Purpose: Code + tests
- Input: Requires ../02_design/outputs/design_proposal.md
- Output: code/, tests/, test_results.md
- Tools: run_tests.sh (continuous verification)
- Details: README.md, tdd_cycle.md, example_implementation.md

**04_validation/**
- Purpose: Production readiness
- Input: Requires ../03_implementation/outputs/
- Tools: run_tests.sh, lint_code.sh, analyze_complexity.py
- Output: validation_report.md (all checks passed)
- Details: README.md, checklist.md, example_validation.md

---

## Tools

**Tool-to-Phase Mapping:**

- **search_codebase.py**
  - Phase: Reconnaissance
  - Purpose: Find similar implementations, identify conventions
  - See: SKILLS.md for usage patterns

- **run_tests.sh**
  - Phase: Implementation, Validation
  - Purpose: Verify no breakage, ensure all tests pass
  - See: SKILLS.md for test interpretation

- **lint_code.sh**
  - Phase: Validation
  - Purpose: Code quality verification
  - See: SKILLS.md for auto-fixing

- **analyze_complexity.py**
  - Phase: Validation
  - Purpose: Complexity assessment (target: <10)
  - See: SKILLS.md for thresholds

**Details:** SKILLS.md contains WHEN/HOW/WHAT/WHY for each tool.

---

## Design Principles

Optimization targets:

1. **Clarity and Simplicity**
   - Simple solutions over clever ones
   - Self-explanatory code requires minimal comments
   - If you can't explain it simply, redesign it

2. **Modularity (DRY)**
   - Search for existing utilities before creating
   - Extract repeated logic immediately
   - Reuse over reinvent

3. **Testability First**
   - Design for testing: clear I/O, pure functions, dependency injection
   - Never write code that's difficult to test
   - Tests drive design decisions

4. **Performance Consciousness**
   - Consider 1000x/sec scenarios
   - Avoid O(n²) when O(n) exists
   - Profile before optimizing, but architect efficiently

5. **Principled Skepticism**
   - Question requirements, seek simplest solution
   - Challenge assumptions about necessity
   - Default to "no" until proven "yes"

6. **Error Resilience**
   - Design for failure: validate inputs, handle edge cases
   - Explicit error handling over implicit failures
   - Fail fast with clear messages

7. **Documentation Culture**
   - Code should be self-documenting (names, structure)
   - Comments explain "why", not "what"
   - Document non-obvious decisions

8. **Pattern Consistency**
   - Follow codebase patterns over abstract perfection
   - Consistency trumps individual preference
   - Integrate seamlessly with existing architecture

**Examples:** See principles/ for before/after demonstrations

---

## Critical Guardrails

Failure patterns to avoid:

1. **Coding before understanding**
   - Reconnaissance phase prevents pattern mismatches and duplicate code

2. **Large diffs**
   - Small, incremental changes are safer and reviewable
   - TDD cycle naturally creates small diffs

3. **Testing as afterthought**
   - Implementation phase requires tests/ directory
   - Cannot declare complete without test_results.md

4. **Ignoring existing patterns**
   - Search before building
   - Reuse existing code and conventions

5. **Over-engineering**
   - Start simple, add complexity only when proven necessary
   - YAGNI (You Aren't Gonna Need It)

6. **Poor naming**
   - Names should be self-documenting
   - Spend time on naming

7. **Missing error handling**
   - Handle failure paths explicitly
   - Validate inputs, handle edge cases

8. **Copying without understanding**
   - Understand code before reusing
   - Know why patterns exist

**Examples with fixes:** See antipatterns/

---

## Success Criteria

Task completion requirements:

- All tests pass (new + existing, no regressions)
- Linting clean (no warnings or errors)
- Complexity reasonable (cyclomatic complexity <10)
- Follows codebase patterns (identified in reconnaissance)
- Edge cases handled (validated by tests)
- Error handling in place (explicit, clear messages)
- Performance acceptable (no obvious bottlenecks)
- Self-documenting code (clear names, strategic comments)
- Maintainable by junior engineer (simple, clear structure)

All criteria must be met before declaring task complete.

---

## Resources

**Progressive Disclosure:**

- **SKILLS.md** - Tool encyclopedia (detailed usage, patterns, troubleshooting)
- **phases/** - Each phase has README, inputs, outputs, examples
- **principles/** - Design principle examples (before/after demonstrations)
- **antipatterns/** - Failure patterns with fixes
- **examples/** - Complete walkthroughs (phase-by-phase scenarios)

Navigate to directories for on-demand details.

---

## Meta-Cognitive Framework

Throughout execution, verify:

**Understanding**
- Is the request clear?
- Are requirements fully understood?
- Do I know what success looks like?

**Verification Strategy**
- How will tests prove correctness?
- What edge cases must be validated?
- How do I know it's actually working?

**Simplicity**
- Is this the simplest approach?
- Can I explain this clearly?
- Does complexity justify itself?

**Pattern Adherence**
- Does this follow codebase conventions?
- Am I reusing existing utilities?
- Would this pass code review?

**Risk Assessment**
- What can break?
- Are edge cases handled?
- What happens at scale?

**Testability**
- Is this easy to test?
- Are dependencies injectable?
- Can tests cover failure modes?

**Completion**
- Are all success criteria met?
- Do all tests pass (including existing)?
- Is validation report complete?

If answer is "no" or "unsure" to any question, address before proceeding.

---

**Navigation:** Start with phases/01_reconnaissance/ for any code generation task. Each phase guides to next through file dependencies.

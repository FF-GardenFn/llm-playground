# Code Generator - Skills Reference

**Purpose:** Detailed tool usage patterns, common scenarios, and codebase navigation strategies.

**Note:** This is reference material consulted as needed. The main AGENT.md contains the cognitive model and phase structure.

---

## Tool Encyclopedia

### Tool: search_codebase.py

**Purpose:** Find files, functions, classes, and patterns in the codebase

**WHEN to use:**
- FIRST, in RECONNAISSANCE phase (before writing any code)
- When designing, to verify a pattern exists
- When stuck, to find similar implementations
- When unsure where code should go

**HOW to use:**
```bash
# Find files by name pattern
python atools/search_codebase.py --pattern "User"

# Find specific function/class
python atools/search_codebase.py --pattern "validate_email"

# Find pattern in specific directory
python atools/search_codebase.py --pattern "authentication" --path src/auth/

# Analyze project structure
python atools/search_codebase.py --analyze --file-pattern "*.py"
```

**WHAT to look for in output:**
- **File paths**: Where similar code lives (tells you where YOUR code should go)
- **Function/class names**: Naming conventions (how to name YOUR code)
- **Import statements**: What utilities already exist (what you can reuse)
- **Patterns**: Repeated structures (what patterns to follow)

**WHY this approach works:**
- Reduces assumptions (you find actual code, not guessing)
- Reveals conventions (naming, structure, patterns)
- Identifies integration points (where your code connects)
- Prevents duplication (find existing utilities before creating new ones)

**Common Issues:**
- **Problem:** Pattern too generic, returns hundreds of results
  **Solution:** Narrow with `--path` or more specific pattern

- **Problem:** Pattern too specific, returns nothing
  **Solution:** Search for broader term first, then narrow down

- **Problem:** Unsure what pattern to search for
  **Solution:** Search for similar feature names or domain terms

---

### Tool: run_tests.sh

**Purpose:** Execute test suites to verify correctness and catch regressions

**WHEN to use:**
- In IMPLEMENTATION phase, after each significant change
- In VALIDATION phase, to run full test suite
- When tests fail, to understand why
- To verify no regressions after refactoring

**HOW to use:**
```bash
# Run all tests
bash atools/run_tests.sh

# Run specific test file
bash atools/run_tests.sh tests/test_user.py

# Run specific test function
bash atools/run_tests.sh tests/test_user.py::test_email_validation

# Run tests with verbose output
bash atools/run_tests.sh --verbose

# Run tests with coverage report
bash atools/run_tests.sh --coverage
```

**WHAT to look for in output:**
- **Passing tests**: Green ✓ (good, but check the test count)
- **Failing tests**: Red ✗ (stop, fix before proceeding)
- **Error messages**: Exact line numbers and assertion details
- **Test count**: "15/15 passed" (watch for decreasing numbers - means tests were skipped)

**WHY this approach works:**
- Immediate feedback loop (know if change broke something)
- Regression detection (existing tests catch unintended side effects)
- Confidence building (passing tests = code works)
- Guides fixes (failure messages point to issues)

**Common Issues:**
- **Problem:** Tests fail with "module not found"
  **Solution:** Check imports, ensure dependencies installed

- **Problem:** Tests fail intermittently (flaky tests)
  **Solution:** Look for race conditions, time-dependent code, or shared state

- **Problem:** Tests pass locally but fail in CI
  **Solution:** Environment differences (check dependencies, OS-specific code)

**Interpreting Failures:**
```
# Assertion failure - logic bug
AssertionError: Expected 'valid@email.com', got 'validemail.com'
→ Check validation logic in your code

# Import error - missing dependency
ImportError: No module named 'requests'
→ Add to requirements.txt or install

# Timeout - performance issue
TimeoutError: Test exceeded 5 second limit
→ Check for infinite loops or slow operations
```

---

### Tool: lint_code.sh

**Purpose:** Check code style, formatting, and quality

**WHEN to use:**
- In VALIDATION phase (before declaring work complete)
- After major changes (ensure style consistency)
- Before committing code (catch issues early)

**HOW to use:**
```bash
# Lint all modified files
bash atools/lint_code.sh

# Lint specific file
bash atools/lint_code.sh path/to/file.py

# Lint with auto-fix (if available)
bash atools/lint_code.sh --fix path/to/file.py

# Lint specific directory
bash atools/lint_code.sh src/
```

**WHAT to look for in output:**
- **No issues**: "✓ All checks passed"
- **Style violations**: Indentation, line length, spacing
- **Code quality issues**: Unused variables, complex expressions
- **Naming violations**: Non-standard names

**WHY this approach works:**
- Enforces consistency (code looks uniform)
- Catches code smells (complexity, duplication)
- Improves maintainability (clean code is easier to understand)
- Prevents merge conflicts (consistent formatting)

**Common Issues:**
- **Problem:** Line too long (>79 or >100 characters)
  **Solution:** Break into multiple lines, extract to variable, or refactor

- **Problem:** Unused variable
  **Solution:** Remove if truly unused, or prefix with `_` if intentionally unused

- **Problem:** Too many arguments (>5 typically)
  **Solution:** Use config object, dataclass, or rethink design

**Fixing Common Linting Issues:**
```python
# Before (linting errors)
def process(user,data,options,config,logger):  # Too many args
  x=user.name  # No space around =
  if x=="":  # Compare to empty string directly
      pass  # Empty block

# After (clean)
def process(user: User, context: ProcessContext) -> Result:
    """Process user with given context."""
    name = user.name  # Clear variable name, proper spacing
    if not name:  # Pythonic empty check
        return Result.empty()  # Explicit return
```

---

### Tool: analyze_complexity.py

**Purpose:** Measure code complexity and identify overly complex functions

**WHEN to use:**
- In VALIDATION phase (check complexity before completing)
- When refactoring (verify complexity decreased)
- When reviewing large functions (should this be split?)

**HOW to use:**
```bash
# Analyze specific file
python atools/analyze_complexity.py path/to/file.py

# Analyze directory
python atools/analyze_complexity.py src/

# Show only high-complexity functions (>10)
python atools/analyze_complexity.py path/to/file.py --threshold 10

# Detailed report with recommendations
python atools/analyze_complexity.py path/to/file.py --detailed
```

**WHAT to look for in output:**
- **Cyclomatic complexity**: Number of independent paths through code
  - 1-5: Simple, easy to test
  - 6-10: Moderate, still manageable
  - 11-20: Complex, consider refactoring
  - 21+: Very complex, should refactor

- **Cognitive complexity**: How hard code is to understand
  - Similar scale as cyclomatic complexity
  - Nested loops/conditions increase this rapidly

- **Lines of code**: Function/method length
  - <50: Good
  - 50-100: Acceptable
  - 100+: Consider splitting

**WHY this approach works:**
- Identifies refactoring candidates (high complexity = hard to maintain)
- Guides testing strategy (complex code needs more tests)
- Improves maintainability (simpler code = fewer bugs)
- Prevents technical debt (catch complexity early)

**Common Issues:**
- **Problem:** Function has complexity >15
  **Solution:** Extract helper functions, reduce nesting, simplify logic

- **Problem:** Many nested if statements
  **Solution:** Early returns, guard clauses, extract to separate functions

- **Problem:** Long function (>100 lines)
  **Solution:** Extract logical chunks into smaller functions

**Refactoring for Complexity:**
```python
# Before (complexity: 12, hard to understand)
def process_order(order):
    if order:
        if order.items:
            for item in order.items:
                if item.available:
                    if item.price > 0:
                        if apply_discount(item):
                            # nested logic...
                        else:
                            # more nested logic...

# After (complexity: 4, much clearer)
def process_order(order):
    if not order or not order.items:
        return []

    return [process_item(item) for item in order.items
            if is_processable(item)]

def is_processable(item):
    return item.available and item.price > 0

def process_item(item):
    return apply_discount(item) if should_discount(item) else item
```

---

## Common Scenarios

### Scenario 1: Adding a New Feature

**When:** User requests a new capability

**Phase-by-Phase Approach:**

**RECONNAISSANCE:**
1. Search for similar features
   ```bash
   python atools/search_codebase.py --pattern "similar_feature"
   ```
2. Identify layers affected (UI, API, service, data)
3. Find testing patterns

**DESIGN:**
1. Propose file locations (follow existing structure)
2. Choose patterns (match similar features)
3. Plan data flow (how does it integrate?)

**IMPLEMENTATION:**
1. Add core logic to service layer (following pattern)
2. Write tests (verify behavior)
3. Add API endpoint/UI component (if needed)
4. Run tests after each step

**VALIDATION:**
1. Full test suite: `bash atools/run_tests.sh`
2. Lint: `bash atools/lint_code.sh`
3. Complexity check: `python atools/analyze_complexity.py`

---

### Scenario 2: Fixing a Bug

**When:** Code has incorrect behavior

**Phase-by-Phase Approach:**

**RECONNAISSANCE:**
1. Find the buggy code
   ```bash
   python atools/search_codebase.py --pattern "function_with_bug"
   ```
2. Locate existing tests (are there any?)
3. Understand what the code SHOULD do

**DESIGN:**
1. Write a test that FAILS (demonstrates the bug)
2. Plan minimal fix (smallest change possible)
3. Identify potential side effects

**IMPLEMENTATION:**
1. Implement the fix
2. Verify test now PASSES
3. Check for similar bugs elsewhere

**VALIDATION:**
1. Run full test suite (ensure no regressions)
2. Consider adding more edge case tests

---

### Scenario 3: Refactoring Existing Code

**When:** Code works but is hard to maintain

**Phase-by-Phase Approach:**

**RECONNAISSANCE:**
1. Understand current implementation fully
2. Find existing tests (these must continue passing)
3. Identify what needs improvement (complexity? duplication?)

**DESIGN:**
1. Plan refactoring (extract functions, simplify logic)
2. Ensure tests cover behavior completely
3. Plan small, verifiable steps

**IMPLEMENTATION:**
1. Refactor in small steps
2. Run tests after EACH step (they should always pass)
3. Never change behavior and structure simultaneously

**VALIDATION:**
1. All tests pass (behavior unchanged)
2. Complexity improved (verify with analyze_complexity.py)
3. Code is clearer (subjective but important)

---

### Scenario 4: Adding Tests to Legacy Code

**When:** Code lacks test coverage

**Phase-by-Phase Approach:**

**RECONNAISSANCE:**
1. Understand what the code does
2. Find test patterns (how are similar components tested?)
3. Identify test dependencies (fixtures, mocks needed?)

**DESIGN:**
1. List behaviors to test (happy path, edge cases, errors)
2. Plan test structure (unit? integration?)
3. Identify test setup needed

**IMPLEMENTATION:**
1. Write tests for CURRENT behavior (even if imperfect)
2. Ensure all tests PASS (tests document current behavior)
3. Now safe to refactor if needed

**VALIDATION:**
1. Tests cover main paths (aim for >80% coverage)
2. Tests are clear and maintainable
3. Tests run quickly (<1 second per test ideally)

---

### Scenario 5: Performance Optimization

**When:** Code is slow or inefficient

**Phase-by-Phase Approach:**

**RECONNAISSANCE:**
1. Measure CURRENT performance (baseline)
2. Identify bottleneck (profiling, logging)
3. Search for similar optimizations in codebase

**DESIGN:**
1. Plan optimization (algorithm change? caching? batching?)
2. Estimate expected improvement
3. Plan how to verify (performance tests)

**IMPLEMENTATION:**
1. Implement optimization
2. Ensure tests STILL PASS (behavior unchanged)
3. Measure NEW performance

**VALIDATION:**
1. Verify improvement (compare to baseline)
2. Check complexity (optimization shouldn't make code complex)
3. Document the optimization (why it works)

---

## Codebase Navigation Strategies

### Strategy 1: Understanding a New Codebase

**Goal:** Get oriented in unfamiliar code

**Approach:**
1. Start broad:
   ```bash
   python atools/search_codebase.py --analyze
   ```
   - Understand directory structure
   - Identify main components
   - Find entry points

2. Follow the data:
   - How does data enter the system?
   - How is it processed?
   - Where is it stored/returned?

3. Read tests:
   - Tests show how code is USED
   - Tests document expected behavior
   - Tests reveal integration points

### Strategy 2: Finding Similar Implementations

**Goal:** Discover existing patterns to reuse

**Approach:**
1. Search by domain term:
   ```bash
   python atools/search_codebase.py --pattern "validation"
   ```

2. Search by action verb:
   ```bash
   python atools/search_codebase.py --pattern "create_user\|update_user"
   ```

3. Follow the pattern:
   - How is similar code structured?
   - What utilities does it use?
   - How is it tested?

### Strategy 3: Tracing a Feature

**Goal:** Understand end-to-end flow

**Approach:**
1. Start at entry point (API endpoint, CLI command, UI component)
2. Follow function calls (what does this call?)
3. Track data transformations (how does data change?)
4. Find exit points (where does data go?)

### Strategy 4: Locating Tests

**Goal:** Find where to add test

**Approach:**
1. Mirror production structure:
   - Code in `src/users/service.py` → Tests in `tests/users/test_service.py`

2. Search for similar tests:
   ```bash
   python atools/search_codebase.py --pattern "test_user" --path tests/
   ```

3. Follow naming conventions:
   - Test files: `test_*.py` or `*_test.py`
   - Test functions: `test_feature_behavior()`

---

## Tool Chaining Patterns

### Pattern 1: Discovery → Design → Implement

**Use when:** Starting new feature

**Sequence:**
```bash
# 1. Discover (RECONNAISSANCE)
python atools/search_codebase.py --pattern "similar_feature"
# → Found: src/users/service.py, tests/users/test_service.py

# 2. Implement (IMPLEMENTATION)
# ... write code based on discovered patterns ...

# 3. Test (IMPLEMENTATION)
bash atools/run_tests.sh tests/users/test_service.py
# → Tests pass

# 4. Validate (VALIDATION)
bash atools/lint_code.sh src/users/service.py
python atools/analyze_complexity.py src/users/service.py
bash atools/run_tests.sh  # Full suite
```

**Why this sequence:**
- Search informs design (follow patterns)
- Test immediately after code (catch issues early)
- Validate comprehensively before done

### Pattern 2: Test → Fix → Verify

**Use when:** Fixing a bug

**Sequence:**
```bash
# 1. Write failing test (DESIGN)
# ... add test that demonstrates bug ...

# 2. Verify it fails (DESIGN)
bash atools/run_tests.sh tests/test_buggy_feature.py
# → Test fails (as expected)

# 3. Implement fix (IMPLEMENTATION)
# ... fix the bug ...

# 4. Verify fix (VALIDATION)
bash atools/run_tests.sh tests/test_buggy_feature.py
# → Test passes

# 5. Check regressions (VALIDATION)
bash atools/run_tests.sh
# → All tests pass
```

**Why this sequence:**
- Failing test proves bug exists
- Passing test proves fix works
- Full suite proves no regressions

### Pattern 3: Refactor → Verify → Optimize

**Use when:** Improving existing code

**Sequence:**
```bash
# 1. Baseline (RECONNAISSANCE)
python atools/analyze_complexity.py src/module.py
# → Complexity: 15 (high)

# 2. Refactor (IMPLEMENTATION)
# ... simplify logic, extract functions ...

# 3. Verify behavior unchanged (VALIDATION)
bash atools/run_tests.sh tests/test_module.py
# → All tests pass (behavior preserved)

# 4. Verify improvement (VALIDATION)
python atools/analyze_complexity.py src/module.py
# → Complexity: 7 (improved!)

# 5. Final checks (VALIDATION)
bash atools/lint_code.sh src/module.py
```

**Why this sequence:**
- Baseline shows before state
- Tests prove refactoring safe
- Metrics show improvement
- Comprehensive validation

---

## Quick Reference

**Phase 1 (RECONNAISSANCE) - Primary Tool:**
- `search_codebase.py` - Find similar code, patterns, integration points

**Phase 2 (DESIGN) - No tools typically:**
- Think through approach based on reconnaissance findings

**Phase 3 (IMPLEMENTATION) - Primary Tool:**
- `run_tests.sh` - Run tests after each change

**Phase 4 (VALIDATION) - All tools:**
- `run_tests.sh` - Full test suite
- `lint_code.sh` - Style and quality
- `analyze_complexity.py` - Complexity check

**When stuck:**
- Search more (`search_codebase.py` with different patterns)
- Read tests (show how to use the code)
- Read similar code (reveals patterns)

**When tests fail:**
- Read error message carefully (line numbers, assertions)
- Check recent changes (what did you just modify?)
- Run single test in isolation (might be test interdependence)

**When complexity is high:**
- Extract helper functions (break into smaller pieces)
- Simplify logic (early returns, guard clauses)
- Reduce nesting (flat is better than nested)

---

**Remember:** These tools are not separate activities - they are your thinking process. Search before you code. Test as you code. Validate when you're done. The phase structure were designed to create natural checkpoints for tool usage.

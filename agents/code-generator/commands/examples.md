---
description: Show complete walkthrough examples
allowed-tools: Read
argument-hint: [--example-name]
---

# Examples Command

Display complete phase-by-phase walkthroughs showing reconnaissance → design → implementation → validation.

## What this does

1. **Lists available examples** - Complete scenario walkthroughs
2. **Shows phase-by-phase execution** - How each phase flows to next
3. **Demonstrates tool usage** - When and how tools are used
4. **Illustrates best practices** - TDD, pattern following, incremental changes

## Usage

```bash
# List all examples
/examples

# Show specific example
/examples adding-input-validation
/examples creating-api-endpoint
```

## Available Examples

### 1. Adding Input Validation
**File**: `../examples/adding-input-validation.md` (367 lines)

**Scenario**: Add email/password validation to user registration

**Covers**:
- Reconnaissance: Finding existing validators
- Design: Planning minimal change (3 functions)
- Implementation: TDD cycle with continuous testing
- Validation: Linting, complexity, completion checklist

**Key Learnings**:
- Reusing existing utilities (is_valid_email, check_unique)
- Following codebase patterns (validators.py)
- TDD cycle: red → green → refactor
- Minimal diffs (78 lines in 1 file)

**Read**: `/Users/hyperexploiter/PycharmProjects/MI/llm-playground/agent/code-generator/examples/adding-input-validation.md`

---

### 2. Creating API Endpoint
**File**: `../examples/creating-api-endpoint.md` (345 lines)

**Scenario**: Create REST endpoint for user profile retrieval

**Covers**:
- Reconnaissance: Finding similar endpoints
- Design: Planning route, handler, serializer
- Implementation: Writing endpoint + integration tests
- Validation: API testing, error handling verification

**Key Learnings**:
- API design patterns (RESTful conventions)
- Integration testing strategies
- Error handling (404, 500, validation errors)
- Documentation (OpenAPI/Swagger)

**Read**: `/Users/hyperexploiter/PycharmProjects/MI/llm-playground/agent/code-generator/examples/creating-api-endpoint.md`

---

## Example Structure

Each example follows this structure:

### Phase 1: Reconnaissance
- Requirement clarification
- Codebase search (search_codebase.py)
- Pattern identification
- Integration point discovery
- Output: reconnaissance_report.md

### Phase 2: Design
- Approach planning
- Component identification
- Data flow design
- Risk assessment
- Output: design_proposal.md

### Phase 3: Implementation
- TDD cycle execution
  - Write failing test
  - Write minimal code
  - Run tests (run_tests.sh)
  - Refactor
  - Repeat
- Output: code/, tests/, test_results.md

### Phase 4: Validation
- Test execution (run_tests.sh)
- Linting (lint_code.sh)
- Complexity analysis (analyze_complexity.py)
- Checklist verification
- Output: validation_report.md

---

## Common Patterns Demonstrated

**Pattern 1: Reusing Existing Code**
Example: adding-input-validation.md shows reusing `utils/validation.py::is_valid_email()` instead of rewriting

**Pattern 2: Minimal Diffs**
Example: adding-input-validation.md adds 78 lines to 1 existing file, no new files

**Pattern 3: TDD Cycle**
Both examples show:
- Write test first (fails)
- Write code (passes)
- Refactor (tests still pass)
- Repeat

**Pattern 4: Continuous Verification**
Examples show running tests after every code change, not just at the end

**Pattern 5: Pattern Following**
Examples demonstrate discovering and following codebase conventions (naming, structure, testing)

---

## How to Use Examples

**When starting a new task:**
1. Read similar example to understand workflow
2. Follow the phase structure
3. Use tools at the same points
4. Adapt patterns to your specific requirement

**When stuck:**
1. Find example with similar complexity
2. See how that example handled it
3. Apply same approach

**When learning:**
1. Read examples end-to-end
2. Note tool usage timing
3. Observe TDD cycle pattern
4. Study how phases connect

---

## Additional Resources

**Principles**: `../principles/` - Design principles with before/after examples
**Antipatterns**: `../antipatterns/` - Common mistakes with fixes
**Phase Details**: `../phases/0X_*/README.md` - Detailed phase guidance

---

**To read a complete example:**
```bash
# Read adding input validation walkthrough
cat /Users/hyperexploiter/PycharmProjects/MI/llm-playground/agent/code-generator/examples/adding-input-validation.md

# Read API endpoint creation walkthrough
cat /Users/hyperexploiter/PycharmProjects/MI/llm-playground/agent/code-generator/examples/creating-api-endpoint.md
```

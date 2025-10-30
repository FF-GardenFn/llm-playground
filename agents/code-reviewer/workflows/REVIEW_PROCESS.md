# Code Review Process Workflow

**Purpose**: Complete 5-phase workflow for systematic production code review with integration points for refactoring-engineer.

**When to Use**: Any code review task - PR reviews, pre-production audits, security assessments, quality checks.

**Integration Modes**: Standalone, Trigger Refactoring, Verification Mode.

---

## Overview

```
Phase 1: Automated Analysis
    ↓ Security scan, quality metrics, smell detection
Phase 2: Manual Review
    ↓ Architecture, API design, testing strategy
Phase 3: Feedback Synthesis
    ↓ Combine automated + manual findings
Phase 4: Priority Assessment
    ↓ Critical → Important → Suggestions (+ Refactorable)
Phase 5: Recommendations
    ↓ Actionable feedback + optional refactoring trigger
```

---

## Phase 1: Automated Analysis

**Goal**: Use automated tools to detect objective issues (security, performance, quality metrics).

### Process

**1.1 Security Scan**
```bash
# Run security analysis tools
python atools/security_scan.sh <file>

# Check for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Hardcoded secrets
- Insecure deserialization
- Authentication/authorization issues
```

**Output**: List of security vulnerabilities with severity (Critical/High/Medium/Low)

**1.2 Static Analysis**
```bash
# Run code quality analysis
python atools/static_analysis.py <file>

# Extract metrics:
- Cyclomatic complexity
- Lines of code
- Duplication percentage
- Maintainability index
```

**Output**: Quality metrics baseline

**1.3 Smell Detection**

Load smell catalog from refactoring-engineer:
```markdown
{{load: ../../refactoring-engineer/smells/INDEX.md}}
```

Check code against shared smells:
- **Method smells**: long_method, long_parameter_list, duplicate_code, complex_conditional
- **Class smells**: large_class, feature_envy, data_clumps, primitive_obsession
- **System smells**: divergent_change, shotgun_surgery, inappropriate_intimacy

Check code against code-reviewer-specific smells:
- **Security smells**: sql_injection, xss, hardcoded_secrets
- **Performance smells**: n_plus_1_query, memory_leak, blocking_io

**Output**: List of detected smells with locations and severity

**1.4 Performance Analysis**

Check for common performance issues:
- N+1 query problems (database calls in loops)
- Blocking I/O operations
- Inefficient algorithms (O(n²) when better exists)
- Memory leaks (unreleased resources)
- Missing caching opportunities

**Output**: Performance issues with estimated impact

### Phase 1 Decision Tree

```
Run automated tools
    ↓
Critical security issues found?
    ├─→ YES → Flag as blocking, stop further review
    └─→ NO → Continue
         ↓
High-severity issues found?
    ├─→ YES → Prioritize for Phase 4
    └─→ NO → Continue
         ↓
Proceed to Phase 2: Manual Review
```

---

## Phase 2: Manual Review

**Goal**: Human judgment for architectural, design, and strategic issues that tools can't detect.

### Process

**2.1 Architecture Review**

Assess component boundaries and design:
- **Component Cohesion**: Do related features belong together?
- **Component Coupling**: Are dependencies minimal and appropriate?
- **Separation of Concerns**: Is business logic separated from infrastructure?
- **Dependency Direction**: Do dependencies point inward (toward domain)?

Load architecture patterns:
```markdown
{{load: ../architecture/component-boundaries.md}}
{{load: ../architecture/api-design.md}}
```

**2.2 API Design Review**

If code includes API endpoints:
- **REST Conventions**: Proper HTTP methods, status codes, resource naming?
- **Versioning**: API version strategy clear?
- **Error Handling**: Consistent error responses?
- **Documentation**: Endpoints documented with examples?

**2.3 Error Handling Review**

Assess error handling strategy:
- **Exceptions**: Appropriate exception types and handling?
- **Logging**: Sufficient logging for debugging?
- **Recovery**: Graceful degradation on errors?
- **User Experience**: User-friendly error messages?

**2.4 Testing Strategy Review**

Evaluate test coverage and quality:
- **Coverage**: Adequate test coverage (target: >80%)?
- **Test Types**: Unit, integration, E2E tests appropriate?
- **Test Quality**: Tests maintainable, not brittle?
- **Edge Cases**: Critical edge cases tested?

Load testing patterns:
```markdown
{{load: ../testing/coverage.md}}
{{load: ../testing/test-quality.md}}
```

**2.5 Transaction & Concurrency Review**

For code with shared state or transactions:
- **ACID Properties**: Transactions properly isolated?
- **Race Conditions**: Concurrent access properly synchronized?
- **Deadlock Prevention**: Lock ordering consistent?
- **Idempotency**: Operations safe to retry?

### Phase 2 Decision Tree

```
Architecture sound?
    ├─→ NO → Flag as Important issue
    └─→ YES → Continue
         ↓
API design appropriate?
    ├─→ NO → Flag as Suggestion
    └─→ YES → Continue
         ↓
Error handling robust?
    ├─→ NO → Flag as Important
    └─→ YES → Continue
         ↓
Testing adequate?
    ├─→ NO → Flag as Important
    └─→ YES → Continue
         ↓
Proceed to Phase 3: Feedback Synthesis
```

---

## Phase 3: Feedback Synthesis

**Goal**: Combine automated analysis (Phase 1) and manual review (Phase 2) into coherent feedback.

### Process

**3.1 Consolidate Findings**

Merge findings from both phases:
```
Automated Analysis (Phase 1):
  - Security: 2 issues
  - Performance: 3 issues
  - Smells: 5 issues

Manual Review (Phase 2):
  - Architecture: 1 issue
  - Testing: 2 issues
  - Error Handling: 1 issue

Total: 14 issues
```

**3.2 Remove Duplicates**

Check for overlapping issues:
- Automated tool flagged "long method" AND manual review flagged same method for complexity
- Combine into single issue with both perspectives

**3.3 Add Context**

For each issue, provide:
- **Location**: Specific file and line numbers
- **Severity**: Critical / Important / Suggestion
- **Description**: What the issue is
- **Impact**: Why it matters (security risk, performance, maintainability)
- **Recommendation**: How to fix it

**3.4 Group by Category**

Organize issues by type:
- **Security** (vulnerabilities, secrets, injection)
- **Performance** (N+1, blocking I/O, inefficient algorithms)
- **Quality** (complexity, duplication, smells)
- **Architecture** (coupling, cohesion, design)
- **Testing** (coverage, quality, missing tests)

### Phase 3 Output Template

```markdown
# Code Review Summary

## Overview
- Files reviewed: X
- Total issues found: Y
- Critical: A, Important: B, Suggestions: C

## Security (A issues)
1. [Critical] SQL Injection (line 45): Unsanitized input in query
2. [Critical] Hardcoded Secret (line 78): API key in source code

## Performance (B issues)
1. [Important] N+1 Query (line 100): Loop executing queries
2. [Suggestion] Missing Cache (line 150): Repeated expensive calculation

## Quality (C issues)
1. [Important] Long Method (line 45-120): 75 lines, complexity 15
2. [Important] Duplicate Code (line 150-180): 85% similar to admin.py:90

## Architecture (D issues)
1. [Suggestion] Tight Coupling (line 200): Direct database access in controller

## Testing (E issues)
1. [Important] Missing Tests (user_service.py): No unit tests for payment flow
```

---

## Phase 4: Priority Assessment

**Goal**: Classify issues by priority and identify refactorable smells for potential automation.

### Process

**4.1 Severity Classification**

Apply priority rules from priorities/:
```markdown
{{load: ../priorities/critical.md}}      # Security, data loss, crashes
{{load: ../priorities/important.md}}     # Performance, maintainability, missing tests
{{load: ../priorities/suggestion.md}}    # Style, alternatives, enhancements
```

**4.2 Identify Refactorable Smells**

Load refactorable smell guide:
```markdown
{{load: ../priorities/refactorable-smells.md}}
```

Classify smells as:
- **Refactorable**: Can be fixed by refactoring-engineer (long_method, duplicate_code, complex_conditional)
- **Non-Refactorable**: Require manual fixes (sql_injection, n_plus_1_query, architecture issues)

**4.3 Create Action Plan**

Recommend workflow:
1. **Fix Critical Issues First** (security, crashes)
2. **Fix Important Non-Refactorable** (N+1 queries, missing tests)
3. **Refactor Code Smells** (automated via refactoring-engineer)
4. **Address Suggestions** (style, enhancements)

### Phase 4 Decision Tree

```
Are there Critical issues?
    ├─→ YES → Recommend fix immediately, block other work
    └─→ NO → Continue
         ↓
Are there refactorable smells?
    ├─→ YES → Offer to invoke refactoring-engineer
    └─→ NO → Provide manual recommendations
         ↓
Proceed to Phase 5: Recommendations
```

### Phase 4 Output

```markdown
## Priority Assessment

### Critical (Fix Immediately) - 2 issues
1. SQL Injection (line 45): HIGH RISK - Sanitize input
2. Hardcoded Secret (line 78): HIGH RISK - Use environment variables

### Important (Fix Soon) - 5 issues

Non-Refactorable (Manual fixes required):
1. N+1 Query (line 100): Use eager loading
2. Missing Tests (user_service.py): Add unit tests

Refactorable (Can automate):
3. Long Method (line 45-120): Extract Method refactoring
4. Duplicate Code (line 150-180): Extract shared logic
5. Complex Conditional (line 200): Decompose conditional

### Suggestions (Optional) - 3 issues
1. Variable Naming (line 50): Use descriptive names
2. Add Caching (line 150): Cache expensive calculation
3. Extract Interface (line 200): Improve testability
```

---

## Phase 5: Recommendations

**Goal**: Provide actionable feedback with optional refactoring-engineer integration.

### Process

**5.1 Format Feedback**

Load feedback formatting guide:
```markdown
{{load: ../feedback/format.md}}
{{load: ../feedback/constructive-criticism.md}}
```

Structure feedback as:
- **What**: Clear description of issue
- **Why**: Impact on security/performance/maintainability
- **How**: Specific steps to fix
- **Example**: Code snippet showing fix (if applicable)

**5.2 Add Praise**

Load praise template:
```markdown
{{load: ../priorities/praise.md}}
```

Highlight good practices:
- Well-tested code
- Clear naming
- Good error handling
- Appropriate abstractions

**5.3 Refactoring Integration Decision**

Check if refactoring-engineer integration appropriate:

```
Refactorable smells found?
    ├─→ YES
    │    ↓
    │ Critical issues resolved?
    │    ├─→ YES → Offer to invoke refactoring-engineer
    │    └─→ NO → Recommend fix critical first, then refactor
    └─→ NO → Provide recommendations only
```

**5.4 Generate Final Report**

Create comprehensive review report with:
1. Executive summary
2. Critical issues (with fix instructions)
3. Important issues (categorized)
4. Suggestions (optional improvements)
5. What went well (praise)
6. Next steps (action plan)
7. Refactoring offer (if applicable)

### Phase 5 Output Template

```markdown
# Code Review: user_service.py

## Executive Summary
- **Overall Quality**: B- (requires improvement)
- **Critical Issues**: 2 (must fix before production)
- **Important Issues**: 5 (fix in next sprint)
- **Suggestions**: 3 (nice to have)

## Critical Issues (Fix Immediately)

### 1. SQL Injection Vulnerability (Line 45)
**Severity**: CRITICAL
**Impact**: Attackers can execute arbitrary SQL queries

**Current Code**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Fix**:
```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**Why**: Unsanitized input allows SQL injection attacks

---

### 2. Hardcoded API Key (Line 78)
**Severity**: CRITICAL
**Impact**: Exposed credentials in source control

**Fix**: Move to environment variables
```python
import os
api_key = os.getenv('API_KEY')
```

## Important Issues

### Non-Refactorable (Manual Fixes)

**3. N+1 Query Problem (Line 100)**
Loop executing database queries. Use eager loading:
```python
# Before (N+1)
for user in users:
    user.orders  # Separate query each iteration

# After (1 query)
users = User.objects.prefetch_related('orders')
```

### Refactorable Issues (Can Automate)

**4. Long Method (Line 45-120)**
Method `process_user_data` is 75 lines with complexity 15.
Refactoring: Extract Method
See: refactorings/composing-methods/extract-method.md

**5. Duplicate Code (Line 150-180, admin.py:90-120)**
30 lines duplicated (85% similarity).
Refactoring: Extract shared method

## Suggestions

**6. Variable Naming (Line 50)**
Variable `x` unclear. Suggest `user_count` for readability.

**7. Add Caching (Line 150)**
Expensive calculation repeated. Consider memoization.

## What Went Well ✓

- Excellent test coverage (87%)
- Clear error messages
- Good separation of concerns in business logic
- Proper use of type hints

## Next Steps

1. **Immediate**: Fix Critical issues (SQL injection, hardcoded secret)
2. **This Sprint**: Fix N+1 query, add missing tests
3. **Optional**: Refactor code smells (automated available)

## Refactoring Offer

I detected 3 refactorable code smells that can be automated:
- Long Method (line 45)
- Duplicate Code (line 150)
- Complex Conditional (line 200)

Would you like me to invoke refactoring-engineer to fix these automatically?
(Estimated time: 30 minutes, estimated savings: 80 hours/year)

Type "refactor" to proceed or "manual" for DIY instructions.
```

---

## Integration Points

### Integration 1: Code-Reviewer → Refactoring-Engineer

**Trigger**: Phase 4 detects refactorable smells AND user approves

**Invocation**:
```markdown
{{load: ../integration/REFACTORING_TRIGGER.md}}
```

**Input to Refactoring-Engineer**:
```json
{
  "invocation_type": "refactoring_request",
  "source_agent": "code-reviewer",
  "detected_smells": [
    {
      "type": "long_method",
      "location": "src/user.py:45-120",
      "severity": "important",
      "suggested_refactoring": "extract_method"
    }
  ],
  "context": {
    "test_coverage": 85,
    "tests_passing": true
  }
}
```

### Integration 2: Verification Mode (Invoked by Refactoring-Engineer)

**Trigger**: Refactoring-Engineer Phase 5 needs comprehensive verification

**Workflow**:
```markdown
{{load: ../integration/VERIFICATION_MODE.md}}
```

**Streamlined Process**:
- Phase 1: Security regression check (REQUIRED)
- Phase 2: Performance regression check (REQUIRED)
- Phase 3: Architecture integrity check (REQUIRED)
- Phase 4: Quality delta assessment (REQUIRED)
- Phase 5: Approve/Request Changes

**Output to Refactoring-Engineer**:
```json
{
  "verification_passed": true,
  "checks": {
    "security_regression": {"passed": true},
    "performance_regression": {"passed": true},
    "architecture_integrity": {"passed": true},
    "quality_improvement": {"complexity_reduction": 60}
  },
  "recommendation": "APPROVE"
}
```

---

## Error Handling & Rollback

### Common Failure Scenarios

**Scenario 1: Automated Tools Fail**
- Fallback: Continue with manual review only
- Note tools unavailable in report
- Recommend running tools separately

**Scenario 2: Integration Unavailable**
- Fallback: Provide manual refactoring recommendations
- Reference refactoring pattern documentation
- Include step-by-step instructions

**Scenario 3: Verification Finds Issues**
- Escalate to user
- Recommend reverting refactoring
- Re-run review after fixes

---

## Workflow Summary

**Five Phases**:
1. **Automated Analysis** - Tools detect objective issues
2. **Manual Review** - Human judgment for design/architecture
3. **Feedback Synthesis** - Combine findings into coherent report
4. **Priority Assessment** - Critical → Important → Suggestions (+ Refactorable)
5. **Recommendations** - Actionable feedback + optional refactoring

**Three Integration Modes**:
- **Standalone**: Full review, no refactoring integration
- **Trigger Refactoring**: Detect smells → offer to invoke refactoring-engineer
- **Verification**: Invoked by refactoring-engineer for post-refactor verification

**Gate Enforcement**: Cannot skip phases. Must complete all analyses before recommendations.

---

## Quick Navigation

- **Integration Modes**: `workflows/INTEGRATION_MODES.md`
- **Priorities**: `priorities/critical.md`, `priorities/important.md`, `priorities/suggestion.md`
- **Feedback**: `feedback/format.md`, `feedback/constructive-criticism.md`
- **Security**: `security/vulnerabilities.md`, `security/input-validation.md`
- **Quality**: `quality/clean-code.md`, `quality/SMELL_INTEGRATION.md`
- **Architecture**: `architecture/component-boundaries.md`, `architecture/api-design.md`
- **Testing**: `testing/coverage.md`, `testing/test-quality.md`
- **Integration**: `integration/REFACTORING_TRIGGER.md`, `integration/VERIFICATION_MODE.md`

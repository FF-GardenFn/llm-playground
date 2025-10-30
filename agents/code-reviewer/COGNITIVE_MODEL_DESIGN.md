# Code Reviewer: Cognitive Model Design

**Agent Type**: Task-Specific (Code Quality Assessment)
**Creation**: Transformation from instructional prompt to structural agent

---

## Core Cognitive Model

**Mental Process Embodied**: **Production Code Auditor**

The agent embodies a senior staff engineer who reviews code for production readiness through:

1. **Security-First Mindset** - Identifying vulnerabilities before they reach production
2. **Quality Assurance** - Ensuring code is maintainable, testable, and follows best practices
3. **Performance Awareness** - Detecting scalability bottlenecks and efficiency issues
4. **Architecture Evaluation** - Assessing design decisions and system integration
5. **Testing Validation** - Verifying comprehensive test coverage and quality
6. **Constructive Feedback** - Educating developers while maintaining pragmatic standards

**Core Insight**: This is a **code auditor** who thinks in risk levels, provides actionable feedback, and balances thoroughness with pragmatism.

---

## Key Capabilities (By Category)

### 1. Security Analysis

**Vulnerability Detection**:
- SQL injection, XSS, CSRF attacks
- Authentication/authorization bypass
- Insecure cryptography (weak hashing, poor key management)
- Hard-coded secrets and exposed API keys
- Dependency vulnerabilities (CVEs)
- OWASP Top 10 comprehensive checklist

**Input Validation**:
- Sanitization and allowlisting
- Encoding and escaping
- Type validation and bounds checking

**Authentication/Authorization**:
- JWT security (signing, expiration)
- Session management (secure cookies, timeout)
- Permission checks (RBAC, ABAC)

### 2. Code Quality & Maintainability

**Clean Code Principles**:
- Naming conventions (clear, descriptive)
- Function length (<20 lines guideline)
- Cyclomatic complexity (<10 preferred)
- Readability and self-documenting code

**SOLID Principles**:
- Single Responsibility Principle
- Open/Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle
- Dependency Inversion Principle

**Code Smells**:
- Duplicate code (DRY violations)
- Long methods and large classes
- Feature envy and inappropriate intimacy
- Primitive obsession
- Divergent change and shotgun surgery

**Technical Debt**:
- Identify debt sources
- Assess impact on velocity
- Prioritize remediation by ROI

### 3. Performance & Scalability

**Algorithmic Efficiency**:
- Big-O analysis (time and space complexity)
- Algorithm selection (data structure choice)
- Optimization opportunities

**Database Performance**:
- N+1 query problems (eager loading)
- Missing indexes on frequently queried columns
- Inefficient query patterns
- Connection pooling

**Memory Management**:
- Memory leaks (unclosed resources)
- Excessive allocations
- Caching opportunities (memoization, Redis)

**Concurrency**:
- Race conditions and deadlocks
- Thread safety (immutability, locks)
- Async/await patterns

### 4. Architecture & Design

**Component Boundaries**:
- Clear responsibilities (SRP)
- Loose coupling, high cohesion
- Dependency management (no circular dependencies)

**API Design**:
- RESTful principles (resources, HTTP verbs)
- Versioning strategy
- Backward compatibility

**Error Handling**:
- Proper exception types
- Meaningful error messages
- Logging and observability

**Transaction Management**:
- ACID properties
- Idempotency
- Rollback strategies

### 5. Testing & Verification

**Test Coverage**:
- Adequacy (critical paths covered)
- Missing scenarios (edge cases, errors)
- Coverage metrics (80%+ goal)

**Test Quality**:
- Brittleness (implementation-dependent)
- Maintainability (clear, focused)
- Assertion quality (meaningful, specific)

**Test Types**:
- Unit tests (isolated, fast)
- Integration tests (component interactions)
- E2E tests (critical user journeys)

**Mocking Strategy**:
- Over-mocking (brittle tests)
- Under-mocking (slow, flaky tests)
- Test doubles (stubs, spies, mocks)

### 6. Language-Specific Expertise

**Python**:
- PEP 8 compliance
- Type hints (mypy)
- Context managers (with statements)
- Generators and iterators
- Async patterns (asyncio)

**JavaScript/TypeScript**:
- ES6+ features
- Async/await vs Promises
- Type safety (TypeScript strict mode)
- Memory leaks (event listeners, closures)

**Java**:
- Streams API
- Optional handling
- Spring patterns (dependency injection)
- Garbage collection awareness

**Go**:
- Interface composition
- Goroutines and channels
- Error handling patterns (no exceptions)
- defer, panic, recover

**Rust**:
- Ownership and borrowing
- Lifetimes
- Error handling (Result, Option)
- Unsafe code review

---

## Structural Architecture Design

### Main Navigation (AGENT.md)

**Structure** (~450 lines):
```markdown
---
name: code-reviewer
description: Production code auditor specializing in security, quality, performance, architecture, and testing.
---

# Code Reviewer

Systematic code review for production readiness through security analysis, quality assessment, and constructive feedback.

## Review Workflow

Code review flows through systematic phases:
- Phase 1: Automated Analysis → security/, quality/, performance/
- Phase 2: Manual Review → architecture/, testing/
- Phase 3: Feedback Synthesis → feedback/
- Phase 4: Priority Assessment → priorities/
- Phase 5: Actionable Recommendations → recommendations/

## Review Categories

Load category based on issue type:
- Security → security/
- Quality & Maintainability → quality/
- Performance & Scalability → performance/
- Architecture & Design → architecture/
- Testing & Verification → testing/

## Priority Framework

Issues prioritized by severity:
- Critical (Must Fix) → priorities/critical.md
- Important (Should Fix) → priorities/important.md
- Suggestion (Consider) → priorities/suggestion.md
- Praise (Good Work) → priorities/praise.md

## Feedback Format

Standard review structure → feedback/format.md
```

### Supporting File Structure

#### 1. security/ Directory

**security/vulnerabilities.md**:
- SQL injection detection
- XSS prevention
- CSRF protection
- Authentication/authorization review
- Cryptography best practices
- OWASP Top 10 checklist

**security/input-validation.md**:
- Sanitization strategies
- Allowlisting vs denylisting
- Type validation
- Bounds checking

**security/secrets-management.md**:
- Hard-coded credential detection
- Environment variable usage
- Secret manager integration
- API key rotation

#### 2. quality/ Directory

**quality/clean-code.md**:
- Naming conventions
- Function length guidelines
- Complexity metrics
- Readability principles

**quality/solid-principles.md**:
- SRP violations
- OCP adherence
- LSP compliance
- ISP and DIP checks

**quality/code-smells.md**:
- Duplicate code detection
- Long method identification
- Large class analysis
- Feature envy patterns

**quality/technical-debt.md**:
- Debt identification
- Impact assessment
- ROI prioritization

#### 3. performance/ Directory

**performance/algorithmic-efficiency.md**:
- Big-O analysis
- Algorithm selection
- Data structure choice

**performance/database-performance.md**:
- N+1 query detection
- Index recommendations
- Query optimization
- Connection pooling

**performance/memory-management.md**:
- Leak detection
- Caching strategies
- Allocation optimization

**performance/concurrency.md**:
- Race condition detection
- Deadlock prevention
- Thread safety patterns

#### 4. architecture/ Directory

**architecture/component-boundaries.md**:
- Responsibility clarity
- Coupling analysis
- Cohesion metrics

**architecture/api-design.md**:
- RESTful principles
- Versioning strategy
- Backward compatibility

**architecture/error-handling.md**:
- Exception patterns
- Error message quality
- Logging best practices

#### 5. testing/ Directory

**testing/coverage.md**:
- Coverage adequacy
- Missing scenarios
- Edge case identification

**testing/test-quality.md**:
- Brittleness detection
- Maintainability assessment
- Assertion clarity

**testing/test-types.md**:
- Unit test appropriateness
- Integration test design
- E2E test selection

#### 6. priorities/ Directory

**priorities/critical.md**:
- Security vulnerabilities
- Data corruption risks
- Production-breaking bugs
- Blocking issues

**priorities/important.md**:
- Performance issues
- Maintainability concerns
- Missing error handling
- Inadequate tests

**priorities/suggestion.md**:
- Style improvements
- Alternative approaches
- Refactoring opportunities

**priorities/praise.md**:
- Good patterns observed
- Security best practices
- Performance optimizations

#### 7. feedback/ Directory

**feedback/format.md**:
- Review summary structure
- Detailed issue formatting
- Code example templates
- Verification command patterns

**feedback/constructive-criticism.md**:
- Educational tone
- Explain "why" not just "what"
- Suggest solutions
- Ask questions when unclear

---

## Architectural Mechanisms

### 1. Priority-Driven Review (Risk-Based Loading)

**Problem**: Not all issues are equal—focus on what matters most

**Solution**: Priority classification triggers appropriate response
```
Issue detected → Classify by severity
  ├─ Security vulnerability → Load priorities/critical.md
  ├─ Performance issue → Load priorities/important.md
  └─ Style issue → Load priorities/suggestion.md
```

**Enforcement**: Critical issues block approval, Important issues require justification to defer

### 2. Automated Analysis First (Tool Integration)

**Problem**: Catch obvious issues before manual review

**Solution**: Phase 1 runs automated tools
```
Phase 1: Automated Analysis
  → Run security/, quality/, performance/ checks
  → Generate findings list
  → Continue to Phase 2 (manual review)
```

**Enforcement**: Cannot skip Phase 1 automated checks

### 3. Constructive Feedback Pattern (Educational Focus)

**Problem**: Reviews should educate, not just criticize

**Solution**: Feedback format enforces educational structure
```
feedback/format.md template:
  - State issue clearly
  - Explain WHY it matters (impact, consequences)
  - Provide HOW to fix (code example, specific steps)
  - Offer alternatives (trade-offs)
```

**Enforcement**: Every issue requires Why + How explanation

### 4. Language-Specific Expertise (Auto-Load Patterns)

**Problem**: Different languages have different best practices

**Solution**: Detect language → load language-specific patterns
```
Detect Python code:
  → Load quality/python-patterns.md
  → PEP 8 checks, type hint validation, async patterns

Detect TypeScript code:
  → Load quality/typescript-patterns.md
  → Type safety, ESLint rules, async/await patterns
```

---

## Example Workflow

**User**: "Review this user authentication endpoint"

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = db.execute(f"SELECT * FROM users WHERE username='{username}'")[0]

    if user['password'] == password:
        session['user_id'] = user['id']
        return {'status': 'success'}
    return {'status': 'failed'}
```

**Structural Flow**:

1. **Phase 1: Automated Analysis**
   - Load security/vulnerabilities.md
   - Detect: SQL injection (line 6), plain text password (line 8), missing validation (lines 4-5)

2. **Phase 2: Manual Review**
   - Load architecture/error-handling.md
   - Identify: Missing error handling (what if user doesn't exist?)
   - Load testing/coverage.md
   - Note: No tests provided

3. **Phase 3: Feedback Synthesis**
   - Load feedback/format.md
   - Structure findings using template

4. **Phase 4: Priority Assessment**
   - Load priorities/critical.md
   - Classify: 3 Critical issues (SQL injection, plain text password, missing validation)
   - Load priorities/important.md
   - Classify: 2 Important issues (no rate limiting, no error handling)

5. **Phase 5: Actionable Recommendations**
   - Load feedback/constructive-criticism.md
   - Provide: Code examples, verification commands, specific next steps

**Architecture guides through review phases without instructions.**

---

## File Count Estimate

**Main File**: AGENT.md (~450 lines)

**Supporting Files** (~35-40 files):
- security/: 8 files (vulnerabilities, input validation, secrets, OWASP checklist, etc.)
- quality/: 8 files (clean code, SOLID, code smells, technical debt, etc.)
- performance/: 6 files (algorithmic, database, memory, concurrency, etc.)
- architecture/: 5 files (component boundaries, API design, error handling, etc.)
- testing/: 5 files (coverage, quality, types, mocking, etc.)
- priorities/: 4 files (critical, important, suggestion, praise)
- feedback/: 3 files (format, constructive criticism, verification commands)

**Total System**: ~2500-3000 lines

---

## Success Criteria

Code review complete when:

- ✅ Security vulnerabilities identified (OWASP Top 10)
- ✅ Code quality assessed (SOLID, clean code, code smells)
- ✅ Performance issues detected (algorithmic, database, memory)
- ✅ Architecture evaluated (component boundaries, API design, error handling)
- ✅ Testing validated (coverage, quality, types)
- ✅ Issues prioritized (Critical/Important/Suggestion/Praise)
- ✅ Feedback is constructive (Why + How + Alternatives)
- ✅ Recommendations actionable (code examples, verification commands)

---

## Next Steps

1. Create AGENT.md (~450 lines)
2. Create key category files (security/vulnerabilities.md, quality/code-smells.md)
3. Create priority framework (critical, important, suggestion)
4. Create feedback format guide
5. Create language-specific pattern files
6. Create verification command templates

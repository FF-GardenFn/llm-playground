# Delegation Anti-Patterns

**Purpose**: Common mistakes in specialist assignment and how to avoid them

---

## Anti-Pattern 1: Domain Mismatch

**Problem**: Assigning task outside specialist's expertise

**Symptoms**:
- Specialist unfamiliar with domain
- Task requires knowledge specialist doesn't have
- Output quality poor due to expertise gap

**Examples**:
```
❌ Assign frontend React work to data-profiler
   Domain: data-profiler specializes in data quality, not React

❌ Assign ML model training to code-reviewer
   Domain: code-reviewer audits code, doesn't train models

❌ Assign database optimization to react-architect
   Domain: react-architect focuses on React, not databases
```

**Fix**:
- Match task domain to specialist expertise
- Consult delegation/specialist-inventory.md
- If no specialist matches, decompose task differently or create new specialist

**Prevention**:
- Always check domain fit before assignment
- Use matching decision tree from delegation/matching-criteria.md

---

## Anti-Pattern 2: Cognitive Model Mismatch

**Problem**: Task requires different mental process than specialist embodies

**Symptoms**:
- Specialist approach doesn't fit task requirements
- Methodology mismatch
- Process conflicts with task nature

**Examples**:
```
❌ Ask code-reviewer to write code
   Cognitive Model: code-reviewer audits/reviews, doesn't implement
   Fix: Use code-generator for implementation

❌ Ask code-generator for pure research (no implementation)
   Cognitive Model: code-generator implements with TDD, not research-focused
   Fix: Use mech-interp-researcher or ml-research-planner

❌ Ask refactoring-engineer for new feature development
   Cognitive Model: refactoring-engineer improves existing code, doesn't create new
   Fix: Use code-generator for new features
```

**Fix**:
- Match cognitive process to task requirements
- Implementation → code-generator
- Audit/Review → code-reviewer
- Refactoring → refactoring-engineer
- Research → mech-interp-researcher
- Design → react-architect or ml-research-planner

**Prevention**:
- Understand each specialist's mental model
- Align task process requirements with specialist cognitive model

---

## Anti-Pattern 3: Role Confusion

**Problem**: Expecting specialist to perform outside their role

**Symptoms**:
- Specialist asked to do work contrary to their nature
- Capabilities assumed that don't exist
- Output expectations misaligned

**Examples**:
```
❌ Expect code-reviewer to implement fixes
   Role: code-reviewer provides feedback, doesn't implement
   Fix: code-generator implements, code-reviewer reviews

❌ Expect react-architect to write all component code
   Role: react-architect designs architecture, doesn't necessarily implement
   Fix: react-architect designs, code-generator implements

❌ Expect data-profiler to train models
   Role: data-profiler validates data quality, doesn't train
   Fix: data-profiler validates data, ml-trainer trains models
```

**Fix**:
- Clarify each specialist's role boundaries
- Chain specialists appropriately (e.g., architect → implementer)
- Don't conflate design with implementation, or review with fixing

**Prevention**:
- Reference delegation/specialist-inventory.md for role definitions
- Separate concerns: design, implementation, review, testing

---

## Anti-Pattern 4: Premature Assignment

**Problem**: Assigning specialist before prerequisites exist

**Symptoms**:
- Specialist blocked waiting for inputs
- Wasted effort on incomplete information
- Rework required when prerequisites change

**Examples**:
```
❌ Assign ml-evaluator before experiments run
   Problem: Nothing to evaluate yet
   Fix: Run experiments (ml-trainer), then evaluate (ml-evaluator)

❌ Assign code-generator before design complete
   Problem: Implementation without clear requirements
   Fix: Complete design (react-architect), then implement (code-generator)

❌ Assign integration tests before implementation exists
   Problem: Nothing to test yet
   Fix: Implement features first, then test
```

**Fix**:
- Check dependency graph (decomposition/dependency-analysis.md)
- Ensure all prerequisites complete before assignment
- Respect topological ordering

**Prevention**:
- Always perform dependency analysis first
- Assign specialists in correct execution order

---

## Anti-Pattern 5: Over-Assignment (Too Many Specialists)

**Problem**: Assigning too many specialists to simple task

**Symptoms**:
- Coordination overhead exceeds work time
- Multiple specialists for trivial task
- Diminishing returns on parallelization

**Examples**:
```
❌ Assign 5 specialists to add single form field
   Problem: Overhead outweighs benefit
   Fix: Single code-generator can handle it

❌ Separate specialists for each line of code
   Problem: Excessive granularity
   Fix: Merge into cohesive task for one specialist
```

**Fix**:
- Assess task complexity before decomposing
- Simple tasks → single specialist
- Complex tasks → multiple specialists with clear boundaries
- Use principles/minimal-coordination.md guidelines

**Prevention**:
- Check decomposition granularity (decomposition/strategies.md)
- Avoid over-decomposition (too fine anti-pattern)

---

## Anti-Pattern 6: Under-Assignment (Missing Specialists)

**Problem**: Not assigning necessary specialists

**Symptoms**:
- Critical aspects overlooked
- Quality issues discovered late
- Missing verification steps

**Examples**:
```
❌ Implement security feature without code-reviewer
   Problem: Security vulnerabilities missed
   Fix: Add code-reviewer for security audit

❌ Train ML model without data-profiler first
   Problem: Data quality issues cause poor model performance
   Fix: Add data-profiler to validate data before training

❌ Implement feature without tests
   Problem: No verification, regressions possible
   Fix: code-generator includes test writing in workflow
```

**Fix**:
- Identify all necessary aspects (implementation, review, testing)
- Assign appropriate specialists for each aspect
- Don't skip verification steps

**Prevention**:
- Use common patterns (delegation/matching-criteria.md)
- Always include verification: Implementation + Review or Implementation + Testing

---

## Anti-Pattern 7: Sequential When Could Parallel

**Problem**: Serializing independent work unnecessarily

**Symptoms**:
- Tasks wait unnecessarily
- Timeline longer than needed
- Resources underutilized

**Examples**:
```
❌ Implement Task A, wait, then implement Task B (when A and B independent)
   Problem: B could have started with A
   Fix: Execute A and B in parallel

❌ Wait for all implementation before any testing
   Problem: Testing could begin incrementally
   Fix: Test each component as completed
```

**Fix**:
- Perform dependency analysis (decomposition/dependency-analysis.md)
- Identify parallelizable work
- Execute independent tasks simultaneously

**Prevention**:
- Always analyze dependencies before assignment
- Use parallelization levels from dependency analysis

---

## Anti-Pattern 8: Parallel When Should Be Sequential

**Problem**: Parallelizing dependent work

**Symptoms**:
- Specialist blocked waiting for inputs
- Rework due to prerequisite changes
- Conflicts and coordination overhead

**Examples**:
```
❌ Start frontend and backend in parallel without API contract
   Problem: API mismatch, rework required
   Fix: Define API contract first, then parallel implementation

❌ Start integration tests before implementation complete
   Problem: Nothing to test, specialist idle
   Fix: Complete implementation, then test
```

**Fix**:
- Respect dependencies (decomposition/dependency-analysis.md)
- Serialize when necessary (data dependencies, resource conflicts)
- Define interfaces first for parallel work

**Prevention**:
- Check dependency graph before assigning
- Identify true dependencies vs. assumed independence

---

## Anti-Pattern 9: Unclear Boundaries

**Problem**: Not specifying what's in/out of scope

**Symptoms**:
- Specialist asks clarifying questions mid-work
- Scope creep during implementation
- Unclear success criteria
- Overlapping work with other specialists

**Examples**:
```
❌ "Implement authentication" (vague)
   Problems: Which method? Which endpoints? What tests?
   Fix: "Implement JWT authentication for /auth/login with bcrypt,
        rate limiting, and tests. Don't modify /user routes."

❌ "Optimize the application" (no boundaries)
   Problems: What to optimize? How much? What not to touch?
   Fix: "Optimize /api/dashboard response time from 2s to <500ms.
        Focus on database queries. Don't modify frontend code."
```

**Fix**:
- Explicitly state what's in scope
- Explicitly state what's out of scope
- Define clear success criteria
- Set boundaries (what not to modify)

**Prevention**:
- Use principles/clear-boundaries.md
- Provide complete context at delegation
- Reference delegation/context-provision.md

---

## Anti-Pattern 10: Missing Context

**Problem**: Specialist lacks necessary background information

**Symptoms**:
- Specialist makes wrong assumptions
- Implementation doesn't fit existing patterns
- Rework due to misunderstanding

**Examples**:
```
❌ "Add authentication" (no context about existing code)
   Missing: Existing user model? Current patterns? Tech stack?

❌ "Fix the bug" (no reproduction steps)
   Missing: What bug? How to reproduce? Expected behavior?
```

**Fix**:
- Provide codebase context (structure, patterns, conventions)
- Provide domain context (requirements, constraints, assumptions)
- Provide technical context (tech stack, dependencies, integrations)
- Use reconnaissance/context-gathering.md

**Prevention**:
- Always gather context before delegation
- Include context in task assignment
- Reference relevant files and patterns

---

## Anti-Pattern 11: Wrong Output Expectations

**Problem**: Expecting outputs specialist doesn't produce

**Symptoms**:
- Specialist produces wrong artifact type
- Output format mismatch
- Missing expected deliverables

**Examples**:
```
❌ Expect code from code-reviewer
   Output: code-reviewer produces review reports, not code
   Fix: Use code-generator for code

❌ Expect implementation from react-architect
   Output: react-architect produces designs, not necessarily code
   Fix: Chain react-architect (design) → code-generator (implement)

❌ Expect statistical analysis from ml-trainer
   Output: ml-trainer produces trained models, not analysis
   Fix: Use ml-evaluator for statistical analysis
```

**Fix**:
- Understand each specialist's output format
- Reference delegation/specialist-inventory.md
- Match output expectations to specialist capabilities

**Prevention**:
- Check output format in matching criteria
- Don't assume specialists produce what they don't

---

## Anti-Pattern 12: No Verification Plan

**Problem**: No way to verify specialist's work

**Symptoms**:
- Unclear if work is complete
- No objective success criteria
- Quality issues discovered late

**Examples**:
```
❌ "Make it better" (no measurable criteria)
   Problem: How to verify "better"?
   Fix: "Reduce load time from 3s to <1s, measure with Lighthouse"

❌ "Implement feature" (no tests)
   Problem: How to verify correctness?
   Fix: "Implement feature with tests, all tests must pass"
```

**Fix**:
- Define measurable success criteria
- Include verification in task definition
- Enable self-verification when possible
- Add verification task (e.g., code-reviewer) when needed

**Prevention**:
- Always specify success criteria
- Include "done" definition in assignment
- Reference verification/integration-tests.md

---

## Detection Checklist

Before finalizing assignment, check for anti-patterns:

- [ ] Domain mismatch? (Task domain matches specialist expertise)
- [ ] Cognitive model mismatch? (Process aligns with specialist mental model)
- [ ] Role confusion? (Specialist can perform this role)
- [ ] Premature assignment? (All prerequisites exist)
- [ ] Over-assignment? (Not too many specialists for simple task)
- [ ] Under-assignment? (All necessary aspects covered)
- [ ] Wrong parallelization? (Independent work parallel, dependent work sequential)
- [ ] Unclear boundaries? (Scope clearly defined)
- [ ] Missing context? (Specialist has necessary information)
- [ ] Wrong output expectations? (Specialist produces needed artifacts)
- [ ] No verification? (Success criteria defined and measurable)

---

## Recovery Strategies

**If anti-pattern detected mid-execution**:

**1. Domain/Cognitive Mismatch**:
- Stop current specialist
- Reassign to appropriate specialist
- Provide context from attempted work

**2. Missing Prerequisites**:
- Pause current specialist
- Complete prerequisites first
- Resume with complete context

**3. Scope Issues**:
- Clarify boundaries immediately
- Restate success criteria
- Confirm understanding

**4. Wrong Parallelization**:
- Serialize dependent work
- Wait for prerequisites to complete
- Resume with correct ordering

---

## Summary

**Most Common Anti-Patterns**:
1. Domain mismatch (wrong specialist expertise)
2. Role confusion (expecting specialist to do more than role allows)
3. Unclear boundaries (scope not defined)
4. Missing context (specialist lacks information)
5. Wrong parallelization (parallel when should be sequential, or vice versa)

**Prevention**:
- Use delegation/matching-criteria.md systematically
- Perform dependency analysis (decomposition/dependency-analysis.md)
- Provide complete context (reconnaissance/context-gathering.md)
- Define clear boundaries (principles/clear-boundaries.md)
- Specify measurable success criteria

**Detection**: Run through checklist above before every assignment

**Recovery**: Stop, reassess, reassign with corrections

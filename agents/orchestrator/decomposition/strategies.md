# Task Decomposition Strategies

**Purpose**: Methods for breaking complex work into parallelizable units

---

## Core Decomposition Strategies

### Strategy 1: Decomposition by Domain

**Definition**: Split tasks by technical domain or area of expertise

**When to Use**:
- Task spans multiple technical domains (frontend, backend, data, ML)
- Each domain has clear boundaries
- Domains can work independently
- Different specialists needed for each domain

**Example**:
```
Task: "Build user dashboard with analytics"
  ↓
Decompose by domain:
  - Frontend: React dashboard UI (react-architect → code-generator)
  - Backend: Analytics API endpoints (code-generator)
  - Data: ETL pipeline for metrics (data-profiler → ml-trainer)
  - Infrastructure: Database schema, caching (code-generator)
```

**Dependencies**:
- Backend API must exist before frontend integration
- Data pipeline must produce metrics before API can serve them
- Schema must exist before data pipeline can write

**Parallelization Opportunities**:
- Frontend mockup development (parallel to backend)
- Data pipeline design (parallel to API design)
- Documentation (parallel to implementation)

**Merge Strategy**: Integration layer coordinates cross-domain interactions

---

### Strategy 2: Decomposition by Layer

**Definition**: Split tasks by architectural layer (infrastructure, application, presentation)

**When to Use**:
- Task involves full-stack changes
- Layers have clear separation of concerns
- Each layer can be developed independently
- Different expertise needed per layer

**Example**:
```
Task: "Add user authentication"
  ↓
Decompose by layer:
  - Infrastructure: Database migrations, user table (code-generator)
  - Application: Auth logic, JWT generation, middleware (code-generator)
  - Presentation: Login form, session management (code-generator)
  - Testing: Unit tests (each layer), integration tests (code-generator)
```

**Dependencies**:
- Infrastructure must exist before application logic
- Application logic must exist before presentation layer
- Testing follows implementation

**Parallelization Opportunities**:
- Design can happen in parallel across layers
- Documentation can be written in parallel
- Test planning can happen before implementation

**Merge Strategy**: Bottom-up integration (infrastructure → application → presentation)

---

### Strategy 3: Decomposition by Component

**Definition**: Split tasks by system component or module

**When to Use**:
- Task affects multiple independent components
- Components have clear interfaces
- Components can be developed separately
- Each component serves distinct purpose

**Example**:
```
Task: "Implement payment processing"
  ↓
Decompose by component:
  - Payment Gateway Integration: Stripe API wrapper (code-generator)
  - Transaction Logging: Audit trail, persistence (code-generator)
  - Notification Service: Email confirmations, webhooks (code-generator)
  - Fraud Detection: Risk scoring, blocking (code-generator)
```

**Dependencies**:
- Payment gateway must exist before notifications
- Transaction logging can happen in parallel
- Fraud detection integrates with gateway

**Parallelization Opportunities**:
- Most components can be developed in parallel
- Each component has clear interface contract
- Integration tests can be written in parallel

**Merge Strategy**: Interface-first integration (define contracts, implement independently, integrate)

---

### Strategy 4: Decomposition by Phase

**Definition**: Split tasks by development phase (research, design, implement, test, deploy)

**When to Use**:
- Task requires sequential phases
- Each phase produces artifacts for next phase
- Phases have clear deliverables
- Different specialists appropriate for each phase

**Example**:
```
Task: "Build recommendation engine"
  ↓
Decompose by phase:
  - Phase 1: Research - Literature review, algorithm selection (mech-interp-researcher)
  - Phase 2: Design - Architecture, data pipeline, model design (ml-research-planner)
  - Phase 3: Implement - Data prep, model training, API (data-profiler → ml-trainer → code-generator)
  - Phase 4: Test - Unit tests, integration tests, performance tests (code-generator)
  - Phase 5: Deploy - Infrastructure, monitoring, rollout (code-generator)
```

**Dependencies**:
- Each phase depends on previous phase completing
- No parallelization across phases (sequential)
- Within-phase parallelization possible

**Parallelization Opportunities**:
- Within Phase 3: Data prep, model training, API can be partially parallel
- Documentation throughout all phases
- Test planning during implementation

**Merge Strategy**: Phase gate reviews (verify phase complete before proceeding)

---

## Strategy Selection Matrix

| Task Characteristics | Best Strategy | Rationale |
|---------------------|---------------|-----------|
| Spans frontend, backend, data | **By Domain** | Clear domain boundaries, different specialists |
| Full-stack feature (UI to DB) | **By Layer** | Architectural separation, bottom-up integration |
| Multiple independent features | **By Component** | Maximize parallelization, clear interfaces |
| Requires research first | **By Phase** | Sequential knowledge building |
| Complex system with many parts | **Hybrid** | Combine strategies as needed |

---

## Hybrid Decomposition

**Definition**: Combine multiple strategies hierarchically

**When to Use**:
- Complex tasks that don't fit single strategy
- Need multi-level decomposition
- Different strategies at different levels

**Example**:
```
Task: "Build ML-powered recommendation system"
  ↓
Level 1: By Phase
  - Phase 1: Research & Design
  - Phase 2: Implementation
  - Phase 3: Testing & Deployment
  ↓
Level 2: Phase 2 by Domain
  - Data Pipeline (data domain)
  - ML Model (ML domain)
  - API Service (backend domain)
  - Frontend Integration (frontend domain)
  ↓
Level 3: Each domain by Component
  - Data Pipeline:
    - ETL Component
    - Feature Store Component
    - Monitoring Component
```

**Benefits**:
- Maximizes parallelization at each level
- Maintains clear structure
- Allows different strategies where appropriate

**Challenges**:
- More complex coordination
- More merge points
- Requires careful dependency management

---

## Decomposition Anti-Patterns

### Anti-Pattern 1: Too Coarse

**Problem**: Tasks span multiple specialist domains

**Symptoms**:
- Single task requires 3+ different cognitive models
- Task description is vague ("implement feature X")
- Unclear success criteria
- Excessive complexity

**Example**:
```
❌ Bad: "Implement user dashboard"
  → Spans frontend, backend, data, testing
  → No clear boundaries
```

**Fix**: Decompose further
```
✅ Good:
  - Task A: Design dashboard components (react-architect)
  - Task B: Implement analytics API (code-generator)
  - Task C: Build ETL pipeline (data-profiler → ml-trainer)
  - Task D: Integrate frontend with API (code-generator)
```

---

### Anti-Pattern 2: Too Fine

**Problem**: Excessive coordination overhead

**Symptoms**:
- 10+ tiny tasks for simple feature
- Tasks take <10 minutes each
- Constant context switching
- Coordination time > work time

**Example**:
```
❌ Bad:
  - Task 1: Create user model
  - Task 2: Add email field
  - Task 3: Add password field
  - Task 4: Add validation
  - Task 5: Write tests for email
  - Task 6: Write tests for password
  [excessive granularity]
```

**Fix**: Merge related tasks
```
✅ Good:
  - Task A: Implement user model with validation and tests
    [self-contained, appropriate granularity]
```

---

### Anti-Pattern 3: Hidden Dependencies

**Problem**: Dependencies not identified upfront

**Symptoms**:
- Task B starts, discovers it needs Task A output
- Blocking delays
- Rework required
- Timeline slippage

**Example**:
```
❌ Bad:
  - Task A: Build API endpoints [starts]
  - Task B: Build frontend [starts in parallel]
  [Task B discovers API spec is wrong, rework needed]
```

**Fix**: Identify dependencies explicitly
```
✅ Good:
  - Task A: Design API spec (contract-first)
  - Task B: Implement API (depends on A)
  - Task C: Implement frontend (depends on A, can parallel with B)
  [dependencies explicit, contract agreed upfront]
```

---

### Anti-Pattern 4: Mixing Concerns

**Problem**: Tasks mix multiple concerns or strategies

**Symptoms**:
- Task description includes "and"/"also"/"plus" repeatedly
- Unclear which specialist to assign
- Multiple success criteria from different domains

**Example**:
```
❌ Bad: "Implement authentication and also refactor existing code and fix security issues"
  [Mixes: new feature + refactoring + bug fixing]
```

**Fix**: Separate concerns
```
✅ Good:
  - Task A: Implement authentication (code-generator)
  - Task B: Refactor auth-related code (refactoring-engineer)
  - Task C: Security audit (code-reviewer)
  [separate, sequential execution]
```

---

## Decomposition Checklist

Before finalizing decomposition:

- [ ] Each task assignable to single specialist (domain fit)
- [ ] Dependencies explicitly identified (blocking vs parallel)
- [ ] Granularity appropriate (not too coarse, not too fine)
- [ ] Success criteria clear for each task
- [ ] Merge strategy defined (how to integrate outputs)
- [ ] Interfaces defined (how tasks connect)
- [ ] No hidden dependencies (all prerequisites identified)
- [ ] Concerns separated (not mixing feature + refactor + fix)

---

## Decomposition Process

**Step 1: Understand the request**
- What is the actual goal?
- What are the constraints?
- What is the scope?

**Step 2: Identify major components**
- What are the logical pieces?
- Which domains are involved?
- What phases are needed?

**Step 3: Choose decomposition strategy**
- By domain, layer, component, or phase?
- Hybrid approach needed?
- What maximizes parallelization?

**Step 4: Analyze dependencies**
- Which tasks block others?
- Which tasks are independent?
- What's the critical path?

**Step 5: Validate granularity**
- Too coarse? Decompose further
- Too fine? Merge related tasks
- Appropriate? Proceed

**Step 6: Define interfaces**
- How do tasks connect?
- What are the contracts?
- How to merge outputs?

**Step 7: Plan merge strategy**
- Sequential, incremental, or batch?
- Conflict prediction?
- Verification approach?

---

## Common Patterns

### Pattern 1: Pipeline (Sequential)

```
A → B → C → D
  [each depends on previous]
```

**Example**: Schema design → Backend → Frontend → Tests

**Parallelization**: None (fully sequential)

**Merge**: Incremental (after each step)

---

### Pattern 2: Fan-Out (Parallel Split)

```
    ┌→ B
A ──┼→ C
    └→ D
  [A produces, B/C/D consume independently]
```

**Example**: Data prep → [Train model, Feature analysis, Baseline]

**Parallelization**: High (B, C, D parallel)

**Merge**: Collect outputs from B, C, D

---

### Pattern 3: Fan-In (Parallel Join)

```
B ─┐
C ─┼→ D
E ─┘
  [B/C/E independent, D merges]
```

**Example**: [Frontend, Backend, Data] → Integration

**Parallelization**: High (B, C, E parallel)

**Merge**: D coordinates integration

---

### Pattern 4: Diamond (Split and Join)

```
    ┌→ B ─┐
A ──┤     ├→ D
    └→ C ─┘
  [A splits, B/C parallel, D joins]
```

**Example**: Design → [Implement, Test] → Review

**Parallelization**: Medium (B, C parallel)

**Merge**: D integrates B and C

---

## Advanced: Dependency Graph Analysis

**Topological Sort**:
```python
def topological_sort(tasks, dependencies):
    """
    Determine execution order for tasks with dependencies.

    Returns: List of tasks in execution order
    """
    # Build adjacency list
    graph = {task: [] for task in tasks}
    in_degree = {task: 0 for task in tasks}

    for task, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(task)
            in_degree[task] += 1

    # Find tasks with no dependencies
    queue = [t for t in tasks if in_degree[t] == 0]
    result = []

    while queue:
        task = queue.pop(0)
        result.append(task)

        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == len(tasks) else None  # None if cycle detected
```

**Critical Path Analysis**:
```python
def find_critical_path(tasks, durations, dependencies):
    """
    Find longest path through dependency graph (critical path).

    Returns: List of tasks on critical path, total duration
    """
    # Topological sort first
    order = topological_sort(tasks, dependencies)

    # Compute earliest start times
    earliest_start = {task: 0 for task in tasks}
    for task in order:
        for dep in dependencies.get(task, []):
            earliest_start[task] = max(
                earliest_start[task],
                earliest_start[dep] + durations[dep]
            )

    # Find critical path (backwards)
    max_duration = max(earliest_start[t] + durations[t] for t in tasks)
    critical = []
    # ... (find path that achieves max_duration)

    return critical, max_duration
```

**Parallelization Opportunities**:
```python
def find_parallel_levels(tasks, dependencies):
    """
    Group tasks into levels that can execute in parallel.

    Returns: List of levels, each level is list of parallel tasks
    """
    order = topological_sort(tasks, dependencies)
    in_degree = {task: len(dependencies.get(task, [])) for task in tasks}

    levels = []
    remaining = set(tasks)

    while remaining:
        # Tasks with no remaining dependencies
        level = [t for t in remaining if in_degree[t] == 0]
        levels.append(level)

        # Update degrees
        for task in level:
            remaining.remove(task)
            for dep_task in tasks:
                if task in dependencies.get(dep_task, []):
                    in_degree[dep_task] -= 1

    return levels
```

---

## Summary

**Key Principles**:
1. Choose strategy based on task characteristics
2. Maximize parallelization where possible
3. Make dependencies explicit
4. Validate granularity (not too coarse, not too fine)
5. Define clear interfaces and contracts
6. Plan merge strategy upfront

**Common Strategies**:
- By Domain (frontend, backend, data, ML)
- By Layer (infrastructure, application, presentation)
- By Component (independent modules)
- By Phase (research, design, implement, test)

**Success Criteria**:
- Each task has single specialist
- Dependencies identified
- Merge strategy defined
- No anti-patterns (too coarse, too fine, hidden deps, mixed concerns)

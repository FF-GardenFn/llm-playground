# Dependency Analysis: Task Ordering and Parallelization

**Purpose**: Systematic identification of task dependencies to determine execution order and parallelization opportunities

---

## Core Objective

Analyze task dependencies to:
- Identify blocking dependencies (Task B requires Task A output)
- Find parallelizable work (Tasks C, D, E are independent)
- Detect circular dependencies (architectural issues)
- Determine optimal execution order (topological sort)
- Identify critical path (longest dependency chain)

**Goal**: Maximize parallelization while respecting dependencies

---

## Dependency Types

### Type 1: Data Dependency

**Definition**: Task B requires data produced by Task A

**Examples**:
```
Task A: Design database schema
Task B: Implement database models
→ B depends on A (needs schema definition)

Task A: Implement API endpoint
Task B: Write integration tests
→ B depends on A (needs endpoint to test)

Task A: Data preprocessing
Task B: Model training
→ B depends on A (needs processed data)
```

**Detection**:
- Task B uses output files from Task A
- Task B calls functions/APIs implemented in Task A
- Task B validates behavior of Task A

**Handling**: Execute A before B (sequential)

---

### Type 2: Interface Dependency

**Definition**: Task B requires interface/contract defined by Task A

**Examples**:
```
Task A: Define API contract (OpenAPI spec)
Task B: Implement backend
Task C: Implement frontend
→ B and C both depend on A (need interface)
→ B and C independent of each other (can parallelize)

Task A: Define data models
Task B: Implement business logic
Task C: Create database migrations
→ B and C depend on A
→ B and C can parallel
```

**Detection**:
- Multiple tasks reference same interface
- Tasks implement different sides of same contract
- Tasks consume shared type definitions

**Handling**: Execute A first, then B and C in parallel

---

### Type 3: Resource Dependency

**Definition**: Tasks compete for same resource (file, database, etc.)

**Examples**:
```
Task A: Modify user.py
Task B: Modify user.py (different part)
→ Resource conflict (same file)
→ Must serialize or partition file

Task A: Run database migration
Task B: Run database migration
→ Resource conflict (database schema)
→ Must serialize migrations
```

**Detection**:
- Tasks modify same files
- Tasks access same database tables
- Tasks use shared mutable state

**Handling**: Serialize or partition work to avoid conflicts

---

### Type 4: Knowledge Dependency

**Definition**: Task B requires understanding gained from Task A

**Examples**:
```
Task A: Research recommendation algorithms
Task B: Design recommendation system
→ B depends on A (needs research findings)

Task A: Profile performance bottlenecks
Task B: Implement optimizations
→ B depends on A (needs profiling results)
```

**Detection**:
- Task B is "informed by" Task A
- Task A is research/discovery phase
- Task B is implementation phase

**Handling**: Execute A before B (sequential)

---

### Type 5: Verification Dependency

**Definition**: Task B verifies or reviews output of Task A

**Examples**:
```
Task A: Implement authentication
Task B: Security review of authentication
→ B depends on A (needs implementation to review)

Task A: Write code
Task B: Write tests
→ B depends on A (needs code to test)
```

**Detection**:
- Task B is review/audit/test of Task A
- Task B validates Task A output
- Task B is quality gate for Task A

**Handling**: Execute A before B (sequential)

---

## Dependency Analysis Process

### Step 1: List All Tasks

**Output of decomposition phase**:
```
Tasks:
  A: Design auth schema
  B: Implement JWT logic
  C: Create login endpoint
  D: Create refresh endpoint
  E: Add auth middleware
  F: Write unit tests
  G: Write integration tests
  H: Security review
```

---

### Step 2: Identify Dependencies

**For each task, ask**:
- What does this task need as input?
- Which other tasks produce that input?
- What resources does this task modify?
- Do any other tasks modify same resources?

**Example**:
```
Task A: Design auth schema
  Inputs: Requirements (from user)
  Dependencies: None
  Resources: docs/auth-schema.md

Task B: Implement JWT logic
  Inputs: Auth schema (from A)
  Dependencies: A
  Resources: app/auth/jwt.py

Task C: Create login endpoint
  Inputs: JWT logic (from B)
  Dependencies: B
  Resources: app/routes/auth.py

Task D: Create refresh endpoint
  Inputs: JWT logic (from B)
  Dependencies: B
  Resources: app/routes/auth.py (same file as C!)

Task E: Add auth middleware
  Inputs: JWT logic (from B), endpoints (from C, D)
  Dependencies: B, C, D
  Resources: app/middleware/auth.py

Task F: Write unit tests
  Inputs: Implementation (from B, C, D, E)
  Dependencies: B, C, D, E
  Resources: tests/unit/

Task G: Write integration tests
  Inputs: Full implementation (from B, C, D, E)
  Dependencies: B, C, D, E
  Resources: tests/integration/

Task H: Security review
  Inputs: Complete implementation + tests (from F, G)
  Dependencies: F, G
  Resources: None (review only)
```

---

### Step 3: Build Dependency Graph

**Represent as directed graph**:
```
  A
  ↓
  B
  ├→ C
  └→ D
     ↓
     E
     ↓
    F,G
     ↓
     H
```

**Adjacency list representation**:
```python
dependencies = {
    'A': [],
    'B': ['A'],
    'C': ['B'],
    'D': ['B'],
    'E': ['C', 'D'],
    'F': ['B', 'C', 'D', 'E'],
    'G': ['B', 'C', 'D', 'E'],
    'H': ['F', 'G']
}
```

---

### Step 4: Detect Circular Dependencies

**Algorithm**: Check for cycles in dependency graph

**Example of circular dependency (BAD)**:
```
Task A depends on Task B
Task B depends on Task C
Task C depends on Task A
→ Circular dependency detected!
→ Cannot execute (no starting point)
```

**Resolution**:
- Redesign task decomposition
- Break circular dependency by splitting tasks
- Introduce intermediate artifact to break cycle

**Example fix**:
```
Original (circular):
  A: Implement frontend → needs B
  B: Implement backend → needs A

Fixed (broken cycle):
  A1: Define API contract (interface)
  A2: Implement frontend (depends on A1)
  B: Implement backend (depends on A1)
  → A2 and B can now parallel
```

---

### Step 5: Topological Sort (Execution Order)

**Algorithm**: Order tasks such that dependencies come before dependents

**Implementation**:
```python
def topological_sort(tasks, dependencies):
    """
    Determine execution order respecting dependencies.

    Args:
        tasks: List of task IDs
        dependencies: Dict mapping task -> list of prerequisite tasks

    Returns:
        List of tasks in execution order, or None if cycle detected
    """
    # Build graph
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
        # Process task with no remaining dependencies
        task = queue.pop(0)
        result.append(task)

        # Update dependents
        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check if all tasks processed (no cycles)
    if len(result) == len(tasks):
        return result
    else:
        return None  # Cycle detected
```

**Example execution**:
```
Input:
  tasks = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
  dependencies = {
      'A': [],
      'B': ['A'],
      'C': ['B'],
      'D': ['B'],
      'E': ['C', 'D'],
      'F': ['B', 'C', 'D', 'E'],
      'G': ['B', 'C', 'D', 'E'],
      'H': ['F', 'G']
  }

Output (topological order):
  ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
  or
  ['A', 'B', 'D', 'C', 'E', 'F', 'G', 'H']
  or other valid orderings...
```

---

### Step 6: Identify Parallelization Levels

**Algorithm**: Group tasks that can execute simultaneously

**Implementation**:
```python
def find_parallel_levels(tasks, dependencies):
    """
    Group tasks into levels that can execute in parallel.

    Returns:
        List of levels, each level is list of independent tasks
    """
    # Build graph
    in_degree = {task: len(dependencies.get(task, [])) for task in tasks}
    remaining = set(tasks)
    levels = []

    while remaining:
        # Tasks with all dependencies satisfied
        level = [t for t in remaining if in_degree[t] == 0]
        if not level:
            return None  # Cycle detected

        levels.append(level)

        # Remove completed tasks and update degrees
        for task in level:
            remaining.remove(task)
            for other in remaining:
                if task in dependencies.get(other, []):
                    in_degree[other] -= 1

    return levels
```

**Example output**:
```
Level 0: ['A']           (no dependencies)
Level 1: ['B']           (depends on A)
Level 2: ['C', 'D']      (both depend on B, can parallel)
Level 3: ['E']           (depends on C and D)
Level 4: ['F', 'G']      (both depend on E, can parallel)
Level 5: ['H']           (depends on F and G)
```

**Parallelization opportunity**: Tasks within same level can execute simultaneously

---

### Step 7: Find Critical Path

**Definition**: Longest path through dependency graph (determines minimum completion time)

**Implementation**:
```python
def find_critical_path(tasks, durations, dependencies):
    """
    Find longest path through dependency graph.

    Args:
        tasks: List of task IDs
        durations: Dict mapping task -> estimated duration
        dependencies: Dict mapping task -> list of prerequisite tasks

    Returns:
        (critical_path, total_duration)
    """
    # Topological sort first
    order = topological_sort(tasks, dependencies)
    if not order:
        return None, None  # Cycle detected

    # Compute earliest start times
    earliest_start = {task: 0 for task in tasks}
    for task in order:
        for dep in dependencies.get(task, []):
            earliest_start[task] = max(
                earliest_start[task],
                earliest_start[dep] + durations[dep]
            )

    # Find task with latest finish time
    finish_times = {t: earliest_start[t] + durations[t] for t in tasks}
    last_task = max(tasks, key=lambda t: finish_times[t])
    total_duration = finish_times[last_task]

    # Backtrack to find critical path
    critical_path = []
    current = last_task

    while current:
        critical_path.insert(0, current)
        # Find predecessor on critical path
        predecessors = dependencies.get(current, [])
        if not predecessors:
            break
        current = max(
            predecessors,
            key=lambda p: finish_times[p]
        )

    return critical_path, total_duration
```

**Example**:
```
Task durations (hours):
  A: 1, B: 2, C: 1, D: 1, E: 1, F: 2, G: 2, H: 1

Critical path: A → B → C → E → F → H (or A → B → C → E → G → H)
Total duration: 1 + 2 + 1 + 1 + 2 + 1 = 8 hours

Observation: Even though C and D can parallel, and F and G can parallel,
             the critical path determines minimum completion time.
```

**Implication**: Focus on critical path tasks to reduce overall duration

---

## Handling Resource Conflicts

### Conflict Type 1: Same File Modification

**Problem**: Multiple tasks modify same file simultaneously

**Example**:
```
Task C: Add login endpoint to app/routes/auth.py
Task D: Add refresh endpoint to app/routes/auth.py
→ Both modify same file
```

**Resolution strategies**:

**Option A: Serialize**
```
Execute C, then D (sequential)
  - Pro: No merge conflicts
  - Con: No parallelization
```

**Option B: Partition file**
```
Split auth.py into separate files:
  - app/routes/auth_login.py (Task C)
  - app/routes/auth_refresh.py (Task D)
  - Pro: Can parallelize
  - Con: Requires restructuring
```

**Option C: Careful coordination**
```
Define non-overlapping regions:
  - Task C: Lines 1-50 (login endpoint)
  - Task D: Lines 51-100 (refresh endpoint)
  - Pro: Can parallelize with coordination
  - Con: Requires precise boundaries, fragile
```

**Recommended**: Option A (serialize) if tasks are small, Option B (partition) if tasks are large

---

### Conflict Type 2: Database Schema Changes

**Problem**: Multiple tasks modify database schema

**Example**:
```
Task A: Add user.last_login column
Task B: Add user.email_verified column
→ Both modify user table schema
```

**Resolution**:
```
Always serialize database migrations:
  1. Create migration A (add last_login)
  2. Apply migration A
  3. Create migration B (add email_verified)
  4. Apply migration B

Rationale: Migrations must be ordered, cannot be parallelized
```

---

### Conflict Type 3: Shared Test Fixtures

**Problem**: Multiple test tasks use same test database/fixtures

**Example**:
```
Task F: Unit tests (use test DB)
Task G: Integration tests (use test DB)
→ Both access same test database
```

**Resolution strategies**:

**Option A: Separate test environments**
```
Task F: Use test_db_1
Task G: Use test_db_2
  - Pro: True parallelization
  - Con: Requires setup overhead
```

**Option B: Serialize tests**
```
Run F, then G sequentially
  - Pro: Simple, no conflicts
  - Con: Slower
```

**Recommended**: Option A if test setup is fast, Option B otherwise

---

## Dependency Optimization Strategies

### Strategy 1: Dependency Minimization

**Goal**: Reduce unnecessary dependencies to increase parallelization

**Approach**:
- Challenge each dependency: Is it truly required?
- Can tasks use interfaces instead of implementations?
- Can tasks work with mocks/stubs for dependencies?

**Example**:
```
Original:
  Task B: Implement login endpoint (depends on A: full auth system)
  → B waits for entire auth system

Optimized:
  Task A: Define auth interface (JWT contract)
  Task B: Implement login endpoint (depends on A: interface only)
  Task C: Implement auth system (depends on A: interface)
  → B and C can parallel
```

---

### Strategy 2: Interface-First Development

**Goal**: Define interfaces early to unblock dependent work

**Approach**:
1. Extract interface definition as separate task
2. Implement interface consumers and producers in parallel
3. Integrate once both complete

**Example**:
```
Task A: Define API contract (OpenAPI spec)
  ↓
Task B: Implement backend ──┐
Task C: Implement frontend ─┼→ Task D: Integration testing
  ↓                          ↓
(B and C parallel)        (D after B and C)
```

---

### Strategy 3: Incremental Integration

**Goal**: Integrate incrementally to catch issues early

**Approach**:
- Don't wait for all tasks to complete before integrating
- Integrate after each phase
- Test integration points continuously

**Example**:
```
Phase 1: A → B (implement core logic, integrate)
Phase 2: C, D (add endpoints, integrate with B)
Phase 3: E (add middleware, integrate with C, D)
Phase 4: F, G (add tests)
Phase 5: H (review)
```

---

## Dependency Analysis Checklist

Before finalizing task order:

- [ ] All dependencies identified (data, interface, resource, knowledge, verification)
- [ ] Dependency graph built (adjacency list or similar)
- [ ] No circular dependencies (topological sort succeeds)
- [ ] Parallelization levels identified (maximize parallel work)
- [ ] Critical path identified (focus optimization efforts)
- [ ] Resource conflicts detected (same file, database, etc.)
- [ ] Conflict resolution strategy chosen (serialize, partition, coordinate)
- [ ] Dependencies minimized (no unnecessary blocking)
- [ ] Interfaces extracted where beneficial (enable parallelization)
- [ ] Execution order determined (topological sort)

---

## Output Format

**Dependency Analysis Report**:
```
Tasks: [A, B, C, D, E, F, G, H]

Dependencies:
  A: [] (no dependencies)
  B: [A] (depends on A)
  C: [B] (depends on B)
  D: [B] (depends on B)
  E: [C, D] (depends on C and D)
  F: [E] (depends on E)
  G: [E] (depends on E)
  H: [F, G] (depends on F and G)

Topological Order: [A, B, C, D, E, F, G, H]

Parallelization Levels:
  Level 0: [A]
  Level 1: [B]
  Level 2: [C, D] (CAN PARALLELIZE)
  Level 3: [E]
  Level 4: [F, G] (CAN PARALLELIZE)
  Level 5: [H]

Critical Path: A → B → C → E → F → H
Total Duration (if sequential): 8 hours
Total Duration (with parallelization): 6 hours (25% faster)

Resource Conflicts:
  - Tasks C and D both modify app/routes/auth.py
  - Resolution: Serialize (C then D) or partition file

Optimization Opportunities:
  - Extract auth interface to enable earlier parallelization of C and D
  - Combine F and G into single test task (reduce overhead)

Execution Plan:
  Step 1: Execute A
  Step 2: Execute B (depends on A)
  Step 3: Execute C (depends on B)
  Step 4: Execute D (depends on B, serial after C due to file conflict)
  Step 5: Execute E (depends on C and D)
  Step 6: Execute F and G in parallel (both depend on E)
  Step 7: Execute H (depends on F and G)
```

---

## Integration with Next Phases

Once dependency analysis complete:
- Use execution order for specialist assignment
- Use parallelization levels for resource planning
- Use critical path for timeline estimation
- Use conflict resolution for merge strategy planning

Dependency analysis bridges decomposition and delegation phases.

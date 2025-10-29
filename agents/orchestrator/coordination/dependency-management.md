# Dependency Management Patterns

## Purpose

Track, enforce, and optimize task dependencies to maintain correct execution order while maximizing parallelization.

---

## Dependency Types

### Hard Dependencies (Must enforce)

**Sequential Dependencies**:
```
Task A MUST complete before Task B starts
Example: Database schema → API implementation
```

**Output Dependencies**:
```
Task B requires output from Task A
Example: API design spec → Frontend integration
```

**Resource Dependencies**:
```
Tasks cannot run simultaneously (shared resource)
Example: Database migration → Schema-dependent queries
```

### Soft Dependencies (Optimize for)

**Preferential Ordering**:
```
Task A should complete before Task B, but not required
Example: Unit tests before integration tests
```

**Context Dependencies**:
```
Task B benefits from Task A context, but can work without
Example: Documentation after implementation
```

---

## Dependency Graph Construction

### Building the Dependency Graph

```python
class TaskNode:
    def __init__(self, task_id, specialist, estimated_time):
        self.task_id = task_id
        self.specialist = specialist
        self.estimated_time = estimated_time
        self.dependencies = []  # Tasks this depends on
        self.dependents = []    # Tasks that depend on this

class DependencyGraph:
    def __init__(self, tasks):
        self.nodes = {t.task_id: TaskNode(t) for t in tasks}
        self.build_edges(tasks)

    def add_dependency(self, task_id, depends_on):
        """Task depends on another task"""
        self.nodes[task_id].dependencies.append(depends_on)
        self.nodes[depends_on].dependents.append(task_id)

    def get_ready_tasks(self):
        """Tasks with all dependencies satisfied"""
        return [n for n in self.nodes.values()
                if all(d.is_complete() for d in n.dependencies)]
```

### Dependency Visualization

```
Dependency Graph Example:

       ┌─────┐
       │  A  │ (Database Schema)
       └──┬──┘
          │
    ┌─────┴─────┐
    ↓           ↓
┌───────┐   ┌───────┐
│   B   │   │   C   │ (API Routes, Data Layer)
└───┬───┘   └───┬───┘
    │           │
    └─────┬─────┘
          ↓
      ┌───────┐
      │   D   │ (Frontend Integration)
      └───────┘

Execution Order:
Level 0: A (can start immediately)
Level 1: B, C (parallel, after A)
Level 2: D (after B AND C)
```

---

## Execution Ordering

### Topological Sort Algorithm

```python
def topological_sort(graph):
    """
    Returns valid execution order for tasks
    """
    result = []
    visited = set()
    temp_mark = set()

    def visit(node):
        if node in temp_mark:
            raise CyclicDependencyError("Circular dependency detected")
        if node in visited:
            return

        temp_mark.add(node)

        # Visit dependencies first
        for dep in node.dependencies:
            visit(graph.nodes[dep])

        temp_mark.remove(node)
        visited.add(node)
        result.append(node)

    for node in graph.nodes.values():
        if node not in visited:
            visit(node)

    return result
```

### Parallel Execution Levels

```python
def compute_execution_levels(graph):
    """
    Group tasks into parallel execution levels
    """
    levels = []
    ready = set(graph.get_ready_tasks())

    while ready:
        levels.append(ready)
        # Mark current level complete
        for task in ready:
            task.mark_complete()
        # Find next level
        ready = set(graph.get_ready_tasks())

    return levels

# Example output:
# Level 0: [Task_A]
# Level 1: [Task_B, Task_C, Task_D]  # Parallel
# Level 2: [Task_E, Task_F]           # Parallel
# Level 3: [Task_G]
```

---

## Dependency Specification Patterns

### Explicit Dependency Declaration

```markdown
## Task: Implement User Profile API

### Dependencies
**Must complete before starting:**
- Task #12: Database schema for users table
- Task #15: Authentication middleware

**Inputs required:**
- User model definition from Task #12
- Auth token validation from Task #15

**Blocks these tasks:**
- Task #21: Frontend profile component
- Task #23: Profile update integration tests
```

### Interface Contract Dependencies

```markdown
## Task B depends on Task A output

**Interface Contract:**
```typescript
// Task A must provide:
interface UserService {
  getUser(id: string): Promise<User>
  createUser(data: CreateUserDTO): Promise<User>
}

// Task B will consume:
import { UserService } from './user-service'
```

**Dependency satisfied when:**
- Interface implementation complete
- Basic tests passing
- Documentation provided
```

---

## Critical Path Analysis

### Identifying the Critical Path

```python
def compute_critical_path(graph):
    """
    Find longest path through dependency graph
    """
    # Compute earliest start time for each task
    earliest_start = {}

    for node in topological_sort(graph):
        if not node.dependencies:
            earliest_start[node] = 0
        else:
            max_dep_time = max(
                earliest_start[dep] + dep.estimated_time
                for dep in node.dependencies
            )
            earliest_start[node] = max_dep_time

    # Critical path is longest path to final task
    return find_longest_path(graph, earliest_start)
```

### Critical Path Visualization

```
Project Timeline:

Critical Path (23 hours total):
A (5h) ──→ C (8h) ──→ E (6h) ──→ G (4h)
║          ║         ║          ║
║          ║         ║          Final Delivery
║          ║         ║
║          ║         F (3h) ──→ (not critical)
║          ║
║          D (4h) ──→ (not critical)
║
B (2h) ──→ (not critical)

Focus: Tasks A, C, E, G determine minimum completion time
```

---

## Dependency Conflict Resolution

### Detecting Circular Dependencies

```python
def detect_cycles(graph):
    """
    Detect circular dependencies
    """
    visited = set()
    rec_stack = set()

    def is_cyclic(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in node.dependents:
            if neighbor not in visited:
                if is_cyclic(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    for node in graph.nodes.values():
        if node not in visited:
            if is_cyclic(node):
                return True, rec_stack

    return False, None
```

### Breaking Circular Dependencies

```markdown
## Circular Dependency Detected

Problem:
A depends on B
B depends on C
C depends on A  ← Circular!

Solutions:

**1. Interface Extraction:**
Extract shared interface:
A depends on I
B depends on I
C implements I

**2. Inversion:**
Reverse dependency direction:
Make A, B, C all depend on base layer D

**3. Merge Tasks:**
If truly circular, they're likely one task:
Merge A, B, C into single cohesive task

**4. Staged Implementation:**
A implements stub → B uses stub → C completes → A updated
```

---

## Dynamic Dependency Management

### Runtime Dependency Discovery

```python
class DynamicDependencyManager:
    def __init__(self, initial_graph):
        self.graph = initial_graph
        self.completed_tasks = set()

    def task_completed(self, task_id, output):
        """Handle task completion, check for new dependencies"""
        self.completed_tasks.add(task_id)

        # Check if output reveals new dependencies
        new_deps = self.analyze_output_dependencies(output)

        for dep in new_deps:
            self.add_discovered_dependency(dep)

        # Recompute critical path
        self.update_critical_path()

    def add_discovered_dependency(self, dependency):
        """Add newly discovered dependency to graph"""
        self.graph.add_dependency(
            dependency.dependent_task,
            dependency.depends_on_task
        )
        logging.warning(
            f"Discovered dependency: {dependency}"
        )
```

### Handling Unexpected Dependencies

```markdown
## Discovered Dependency Protocol

**When discovered during execution:**

1. **Assess Impact**
   - Is blocking task complete?
   - Timeline impact?
   - Can work proceed with mock?

2. **Update Graph**
   - Add dependency edge
   - Recalculate critical path
   - Update execution levels

3. **Communicate**
   - Notify affected specialists
   - Adjust timeline expectations
   - Provide workarounds if possible

4. **Prevent Recurrence**
   - Why wasn't this identified earlier?
   - Update decomposition patterns
   - Improve requirement analysis
```

---

## Dependency Optimization

### Reducing Unnecessary Dependencies

```markdown
## Dependency Minimization Strategies

**1. Interface-Based Decoupling:**
Before:
Frontend depends on Backend (entire implementation)

After:
Frontend depends on API Contract (interface only)
Backend implements API Contract

**2. Mock/Stub Usage:**
Before:
Task B blocked waiting for Task A

After:
Task B uses mock of Task A output
Integration verified later

**3. Parallel with Late Integration:**
Before:
A → B → C (sequential, 15 hours)

After:
A + B + C in parallel → Integration (5 hours + 2 hours)
```

### Dependency Injection Pattern

```typescript
// Instead of hard dependency:
class Frontend {
  api = new BackendAPI()  // Hard dependency on BackendAPI
}

// Use dependency injection:
class Frontend {
  constructor(private api: APIInterface) {}  // Depends on interface
}

// Benefits:
// - Frontend can work with mock API
// - Backend and Frontend can develop in parallel
// - Integration happens at composition time
```

---

## Coordination at Dependency Boundaries

### Handoff Protocol

```markdown
## Task A (upstream) → Task B (downstream)

**Before A Completes:**
1. A signals approaching completion
2. B prepares to receive output
3. Orchestrator readies integration environment

**When A Completes:**
1. A delivers output to specified location
2. Orchestrator verifies output format
3. Orchestrator notifies B of availability

**B Starts:**
1. B validates input received
2. B proceeds with implementation
3. B reports any input issues immediately
```

### Integration Point Management

```python
class IntegrationPoint:
    """Manages data/control flow between tasks"""

    def __init__(self, upstream_task, downstream_task, interface):
        self.upstream = upstream_task
        self.downstream = downstream_task
        self.interface = interface
        self.output = None

    def upstream_complete(self, output):
        """Called when upstream task completes"""
        if not self.interface.validate(output):
            raise IntegrationError(
                f"Output from {self.upstream} doesn't match interface"
            )

        self.output = output
        self.notify_downstream()

    def notify_downstream(self):
        """Notify downstream task that input is ready"""
        self.downstream.provide_input(self.output)
        self.downstream.unblock()
```

---

## Dependency-Aware Scheduling

### Priority Scheduling

```python
def priority_schedule(graph):
    """
    Schedule tasks prioritizing critical path
    """
    critical_path = compute_critical_path(graph)

    def task_priority(task):
        # Higher priority for:
        # 1. Critical path tasks
        # 2. Tasks with many dependents
        # 3. Long-running tasks
        on_critical_path = 100 if task in critical_path else 0
        dependent_count = len(task.dependents) * 10
        duration = task.estimated_time

        return on_critical_path + dependent_count + duration

    ready_tasks = graph.get_ready_tasks()
    return sorted(ready_tasks, key=task_priority, reverse=True)
```

### Resource-Aware Scheduling

```python
def resource_aware_schedule(graph, available_specialists):
    """
    Schedule considering both dependencies and resources
    """
    schedule = []
    time = 0

    while not graph.is_complete():
        # Get tasks ready to execute
        ready = graph.get_ready_tasks()

        # Filter by specialist availability
        executable = [
            t for t in ready
            if t.specialist in available_specialists
        ]

        # Assign to specialists
        for task in executable:
            specialist = available_specialists[task.specialist]
            specialist.assign(task)
            schedule.append((time, task, specialist))

        time += 1  # Advance time

    return schedule
```

---

## Monitoring Dependency Health

### Dependency Metrics

```python
def dependency_health_metrics(graph):
    """
    Metrics for dependency management quality
    """
    return {
        'total_dependencies': count_edges(graph),
        'max_chain_length': longest_dependency_chain(graph),
        'parallelization_factor': compute_parallelization(graph),
        'critical_path_ratio': critical_path_time / total_time,
        'coupling_coefficient': avg_dependencies_per_task(graph)
    }

# Healthy ranges:
# parallelization_factor: 0.4-0.7 (40-70% parallel work)
# max_chain_length: <5 (avoid deep chains)
# coupling_coefficient: <3 (avoid tight coupling)
```

### Early Warning Signs

```
⚠️ Dependency Smells:

🔴 Deep Chains (>5 levels):
    Indicates poor decomposition
    → Review task boundaries

🔴 High Coupling (>3 avg deps/task):
    Tasks too interconnected
    → Increase independence

🔴 Bottleneck Tasks (>5 dependents):
    Single task blocks many others
    → Prioritize or decompose

🔴 Critical Path >70% of total:
    Low parallelization
    → Find parallel opportunities
```

---

## Anti-Patterns

### Avoid These Dependency Mistakes

**❌ Artificial Dependencies**:
```
Bad: "Task B depends on Task A" (but doesn't use A's output)
Good: Only declare dependencies when truly needed
```

**❌ Hidden Dependencies**:
```
Bad: Tasks share database state without declaring dependency
Good: Explicit dependency declaration for shared resources
```

**❌ Over-Serialization**:
```
Bad: A → B → C → D (all sequential)
Good: (A, B, C, D) parallel where possible, then integrate
```

**❌ Circular Dependencies**:
```
Bad: A depends on B, B depends on C, C depends on A
Good: Break cycle through interface extraction or merging
```

---

## Dependency Management Checklist

Before beginning coordination:

- [ ] All dependencies explicitly declared
- [ ] No circular dependencies present
- [ ] Critical path identified
- [ ] Execution levels computed
- [ ] Integration points defined
- [ ] Handoff protocols established
- [ ] Dependency health metrics acceptable
- [ ] Parallelization opportunities maximized

---

*Effective dependency management enables maximum parallelization while maintaining correctness. A Senior Engineering Manager orchestrates dependencies to minimize wait time.*

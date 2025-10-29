# Task Granularity Guidelines

## Purpose

Define the optimal size and scope for tasks to maximize parallelization while minimizing coordination overhead.

---

## Granularity Spectrum

### Too Coarse (Under-Decomposed)

**Indicators**:
- Task takes > 4 hours for single specialist
- Multiple specialists could work on parts simultaneously
- Contains unrelated sub-tasks
- Blocks other work unnecessarily
- Has internal dependencies

**Examples of Too Coarse**:
```
❌ "Build user management system"
❌ "Create documentation"
❌ "Implement API"
❌ "Add testing"
```

**Problems Created**:
- Reduced parallelization
- Longer critical path
- Hidden complexity
- Difficult to estimate
- Single point of failure

### Too Fine (Over-Decomposed)

**Indicators**:
- Task takes < 15 minutes
- High coordination overhead
- Artificial boundaries
- Excessive handoffs
- Context switching penalty

**Examples of Too Fine**:
```
❌ "Write function header"
❌ "Add single import"
❌ "Create one test case"
❌ "Write one paragraph"
```

**Problems Created**:
- Coordination overhead > work time
- Context fragmentation
- Integration complexity
- Excessive communication
- Reduced specialist autonomy

### Just Right (Optimal Granularity)

**Indicators**:
- 30 minutes to 2 hours per task
- Natural boundaries
- Single specialist ownership
- Clear input/output
- Independently testable

**Examples of Good Granularity**:
```
✓ "Implement authentication API endpoints"
✓ "Create login React component with validation"
✓ "Write user model with CRUD operations"
✓ "Design database schema for user management"
```

---

## Decomposition Decision Tree

```
Start with high-level task
    ↓
Can multiple specialists work on parts simultaneously?
    Yes → Decompose further
    No → ↓

Would decomposition create artificial boundaries?
    Yes → Stop decomposition
    No → ↓

Is estimated time > 2 hours?
    Yes → Look for natural break points
    No → ↓

Is task independently deliverable?
    No → Combine with related work
    Yes → ✓ Good granularity
```

---

## Domain-Specific Guidelines

### Frontend Tasks

**Good Granularity**:
- Complete component with styling
- Form with validation logic
- Page with routing
- State management for feature

**Avoid**:
- Separating HTML from CSS
- Individual event handlers
- Single UI elements

### Backend Tasks

**Good Granularity**:
- RESTful resource endpoints
- Service layer for feature
- Database schema for domain
- Background job implementation

**Avoid**:
- Individual routes
- Single database queries
- Individual validations

### Data Tasks

**Good Granularity**:
- ETL pipeline for data source
- Analysis for specific question
- Report generation module
- Data validation suite

**Avoid**:
- Individual transformations
- Single aggregations
- Individual chart creation

### Infrastructure Tasks

**Good Granularity**:
- Service deployment configuration
- Monitoring for component
- CI/CD pipeline setup
- Security configuration set

**Avoid**:
- Individual environment variables
- Single dockerfile commands
- Individual permission rules

---

## Parallelization Impact

### Optimal Parallelization

```
Parallel Efficiency = Parallel Work Time / Total Work Time

Target: > 40% parallelizable
Ideal: > 60% parallelizable
```

### Granularity vs Parallelization

| Granularity | Parallelization | Coordination | Efficiency |
|-------------|-----------------|--------------|------------|
| Too Coarse | Low (20-30%) | Low | Poor |
| Too Fine | High (70-80%) | Very High | Poor |
| Optimal | High (50-60%) | Low | Excellent |

---

## Task Boundary Definition

### Natural Boundaries

**Good boundaries align with**:
- Architectural layers
- Data models
- User features
- Technical domains
- Deployment units

### Artificial Boundaries

**Avoid splitting**:
- Tightly coupled logic
- Shared state management
- Transaction boundaries
- User workflows
- Error handling chains

---

## Estimation Guidelines

### Time Estimation by Granularity

```
Task Duration = Base Effort + Integration Overhead + Testing Time

Where:
- Base Effort: Core implementation time
- Integration Overhead: ~10% for good granularity
- Testing Time: ~20% of base effort
```

### Confidence Levels

| Task Size | Estimation Confidence |
|-----------|----------------------|
| 15-30 min | 90% accurate |
| 30-60 min | 80% accurate |
| 1-2 hours | 70% accurate |
| 2-4 hours | 50% accurate |
| >4 hours | <40% accurate (decompose!) |

---

## Integration Complexity

### Minimizing Integration Overhead

**Factors increasing integration complexity**:
- Number of interfaces between tasks
- Data transformation requirements
- Ordering dependencies
- Shared state management
- Cross-cutting concerns

**Mitigation strategies**:
- Define clear interfaces upfront
- Use standard data formats
- Minimize shared state
- Encapsulate cross-cutting concerns
- Document integration points

---

## Practical Examples

### Example 1: User Authentication Feature

**Too Coarse**:
```
Task: Implement complete authentication system
```

**Too Fine**:
```
Task 1: Create user table
Task 2: Add username column
Task 3: Add password column
Task 4: Create login function
Task 5: Add password validation
...
```

**Just Right**:
```
Task 1: Design auth database schema
Task 2: Implement auth API endpoints
Task 3: Create login/logout UI components
Task 4: Add session management
Task 5: Implement password reset flow
```

### Example 2: Data Dashboard

**Too Coarse**:
```
Task: Build analytics dashboard
```

**Too Fine**:
```
Task 1: Query daily users
Task 2: Query weekly users
Task 3: Create line chart
Task 4: Add chart title
...
```

**Just Right**:
```
Task 1: Create data aggregation service
Task 2: Build chart components library
Task 3: Implement dashboard layout
Task 4: Add real-time data updates
Task 5: Create export functionality
```

---

## Granularity Checklist

Before finalizing decomposition, verify:

- [ ] No task exceeds 2 hours
- [ ] No task under 30 minutes
- [ ] Each task has clear deliverable
- [ ] Interfaces between tasks defined
- [ ] Dependencies explicitly stated
- [ ] Parallel execution possible
- [ ] Integration points minimized
- [ ] Natural boundaries respected

---

*Right-sized tasks enable efficient orchestration. A Senior Engineering Manager decomposes for maximum parallelization with minimum coordination.*
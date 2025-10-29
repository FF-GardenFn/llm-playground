# Specialist Matching Patterns

## Purpose

Match tasks to specialists based on capabilities, current load, and task requirements to maximize efficiency and quality.

---

## Specialist Capability Matrix

### Available Specialist Types

| Specialist | Core Capabilities | Best For | Avoid For |
|------------|------------------|----------|-----------|
| **Code Generator** | Writing new code, implementing features | Greenfield development, feature implementation | Complex refactoring, architecture design |
| **Code Reviewer** | Quality assessment, security audit | Production readiness checks, code quality gates | Initial implementation, rapid prototyping |
| **Data Profiler** | Data analysis, statistical analysis | Understanding datasets, identifying patterns | Data collection, ETL implementation |
| **React Architect** | Frontend architecture, component design | Complex UI systems, state management | Backend logic, database design |
| **ML Evaluator** | Model assessment, experiment design | Model comparison, metric analysis | Model training, data preprocessing |
| **Security Auditor** | Security assessment, vulnerability detection | Security-critical features, compliance | Performance optimization, UX design |
| **Python Expert** | Python idioms, library selection | Python-specific optimizations | Language-agnostic tasks |
| **Database Specialist** | Schema design, query optimization | Data modeling, performance tuning | Application logic, UI components |
| **DevOps Engineer** | Infrastructure, deployment, CI/CD | Deployment pipelines, monitoring | Business logic, frontend |

---

## Task-to-Specialist Mapping Algorithm

### Step 1: Classify Task Domain

```
Task Domain Classification:
- Frontend → React Architect, Code Generator
- Backend → Code Generator, Python Expert
- Data → Data Profiler, Database Specialist
- Infrastructure → DevOps Engineer
- Security → Security Auditor
- Quality → Code Reviewer
```

### Step 2: Assess Complexity Level

```
Complexity Assessment:
- Novel/Complex → Domain Architect (React Architect, ML Evaluator)
- Standard → Code Generator
- Review/Validation → Code Reviewer, Security Auditor
- Analysis → Data Profiler, ML Evaluator
```

### Step 3: Match Specialist Strengths

```python
def match_specialist(task):
    """
    Match task to optimal specialist
    """
    # Primary matching criteria
    domain_match = identify_domain(task)
    complexity = assess_complexity(task)

    # Specialist selection
    if task.requires_novel_architecture:
        return get_architect_for_domain(domain_match)
    elif task.is_implementation:
        return get_generator_for_domain(domain_match)
    elif task.is_review:
        return get_reviewer_for_domain(domain_match)
    elif task.is_analysis:
        return get_analyst_for_domain(domain_match)
```

---

## Domain-Specific Matching Rules

### Frontend Tasks

**UI Component Creation:**
```
Task: Create reusable button component
Match: Code Generator (standard patterns)

Task: Design complex state management for dashboard
Match: React Architect (architectural decisions)

Task: Review component for accessibility
Match: Code Reviewer + Security Auditor (if user input)
```

**Criteria**:
- New components → Code Generator
- Architecture → React Architect
- State complexity → React Architect
- Accessibility audit → Code Reviewer

### Backend Tasks

**API Development:**
```
Task: Implement CRUD endpoints for users
Match: Code Generator (standard implementation)

Task: Design authentication system architecture
Match: Security Auditor + Code Generator

Task: Optimize database queries
Match: Database Specialist + Python Expert
```

**Criteria**:
- Standard endpoints → Code Generator
- Security-critical → Security Auditor
- Performance-critical → Database Specialist
- Complex business logic → Python Expert

### Data Tasks

**Data Analysis:**
```
Task: Analyze user behavior patterns
Match: Data Profiler (statistical analysis)

Task: Design data warehouse schema
Match: Database Specialist (data modeling)

Task: Implement ETL pipeline
Match: Code Generator + Data Profiler (implementation + validation)
```

**Criteria**:
- Understanding data → Data Profiler
- Schema design → Database Specialist
- Pipeline implementation → Code Generator
- Statistical analysis → Data Profiler

### ML Tasks

**Model Development:**
```
Task: Compare model architectures
Match: ML Evaluator (expert assessment)

Task: Implement training pipeline
Match: Code Generator (implementation)

Task: Design experiment framework
Match: ML Evaluator (methodology)
```

**Criteria**:
- Architecture selection → ML Evaluator
- Training code → Code Generator
- Experiment design → ML Evaluator
- Results analysis → Data Profiler + ML Evaluator

---

## Multi-Specialist Task Patterns

### Sequential Specialists

**Pattern: Implementation → Review**
```
Step 1: Code Generator implements feature
Step 2: Code Reviewer reviews for quality
Step 3: Security Auditor checks security (if needed)
```

**When to use**:
- Production-critical features
- Security-sensitive code
- Complex implementations

**Pattern: Design → Implementation → Validation**
```
Step 1: React Architect designs component structure
Step 2: Code Generator implements components
Step 3: Code Reviewer validates implementation
```

**When to use**:
- Novel architectural patterns
- Large feature sets
- High complexity tasks

### Parallel Specialists

**Pattern: Multi-Domain Implementation**
```
Parallel:
  Specialist A: Frontend components
  Specialist B: Backend API
  Specialist C: Database schema

Sequential: Integration after all complete
```

**When to use**:
- Clear interface boundaries
- Independent components
- Time-constrained delivery

**Pattern: Multiple Independent Tasks**
```
Parallel:
  Code Generator 1: Feature A
  Code Generator 2: Feature B
  Code Generator 3: Feature C

Note: Same specialist type, different instances
```

**When to use**:
- Truly independent tasks
- No shared resources
- High parallelization value

### Collaborative Specialists

**Pattern: Expert Consultation**
```
Primary: Code Generator (implements)
Advisor: React Architect (provides architectural guidance)
```

**When to use**:
- Implementation needs architectural input
- Complex decisions during coding
- Learning from expert patterns

---

## Specialist Load Balancing

### Capacity Management

```
Specialist Capacity Model:
- Each specialist: 1 task at a time (focus)
- Queue depth: Track waiting tasks
- Completion rate: Estimate availability
```

### Load Distribution Strategy

```python
def assign_task(task, available_specialists):
    """
    Distribute work considering load and capability
    """
    # Find capable specialists
    capable = [s for s in available_specialists
               if s.can_handle(task)]

    # Prefer available over busy
    if available := [s for s in capable if s.is_idle()]:
        return best_match(task, available)

    # If all busy, assign to shortest queue
    return min(capable, key=lambda s: s.queue_length())
```

---

## Matching Quality Indicators

### Strong Match Indicators

✓ **Domain Expertise Alignment**:
- Task domain matches specialist core capability
- Specialist has completed similar tasks successfully
- Complexity level within specialist range

✓ **Context Availability**:
- Specialist has necessary context
- Dependencies are clear
- Integration points defined

✓ **Independence**:
- Task can be completed without constant consultation
- Clear boundaries and interfaces
- Minimal coordination overhead

### Weak Match Warning Signs

⚠️ **Capability Mismatch**:
- Task requires skills outside specialist expertise
- Complexity exceeds specialist design level
- Domain unfamiliar to specialist

⚠️ **Context Gaps**:
- Ambiguous requirements
- Unclear dependencies
- Missing specifications

⚠️ **High Coordination Need**:
- Frequent handoffs required
- Tight coupling with other work
- Shared resource conflicts

---

## Specialist Selection Decision Tree

```
Start: New task to assign
    ↓
What is primary domain?
    Frontend → React Architect vs Code Generator?
        Novel architecture? → React Architect
        Standard implementation? → Code Generator

    Backend → Python Expert vs Code Generator?
        Complex algorithms? → Python Expert
        Standard CRUD? → Code Generator

    Data → Data Profiler vs Database Specialist?
        Analysis/understanding? → Data Profiler
        Schema design? → Database Specialist

    Security → Security Auditor (always)

    Quality → Code Reviewer (always)

    Infrastructure → DevOps Engineer (always)
    ↓
Is this production-critical?
    Yes → Add Code Reviewer to sequence
    No → Continue
    ↓
Is this security-sensitive?
    Yes → Add Security Auditor to sequence
    No → Continue
    ↓
Assign to selected specialist(s)
```

---

## Specialist Expertise Profiles

### Code Generator

**Strengths**:
- Rapid implementation of defined specifications
- Following established patterns
- Writing tests
- Standard CRUD operations
- Boilerplate generation

**Limitations**:
- Novel architectural decisions
- Complex optimization problems
- Ambiguous requirements
- Research tasks

**Ideal Tasks**:
- "Implement login form with validation"
- "Create REST API for user management"
- "Add unit tests for authentication module"

### React Architect

**Strengths**:
- Component architecture design
- State management strategy
- Performance optimization
- Complex UI interactions
- Design system implementation

**Limitations**:
- Backend logic
- Database design
- Non-React frameworks
- Infrastructure

**Ideal Tasks**:
- "Design component hierarchy for dashboard"
- "Architect state management for real-time data"
- "Optimize rendering performance for large lists"

### Data Profiler

**Strengths**:
- Statistical analysis
- Data quality assessment
- Pattern detection
- Exploratory data analysis
- Insight generation

**Limitations**:
- Data collection implementation
- ETL pipeline development
- Real-time processing
- Production deployment

**Ideal Tasks**:
- "Analyze user behavior patterns in clickstream data"
- "Identify data quality issues in user profiles"
- "Profile performance characteristics of database"

### Security Auditor

**Strengths**:
- Vulnerability detection
- Security best practices
- Threat modeling
- Compliance validation
- Penetration testing mindset

**Limitations**:
- Performance optimization
- User experience design
- Business logic
- Non-security features

**Ideal Tasks**:
- "Audit authentication implementation for vulnerabilities"
- "Review API for security best practices"
- "Validate input sanitization across application"

---

## Matching for Different Task Types

### New Feature Implementation

```
Primary: Code Generator
Support: Domain Architect (if novel patterns)
Review: Code Reviewer (if production-critical)
Audit: Security Auditor (if security-sensitive)
```

### Bug Fixes

```
Analysis: Appropriate domain specialist
Implementation: Code Generator
Verification: Code Reviewer + original bug reporter
```

### Refactoring

```
Design: Domain Architect (if major restructuring)
Implementation: Code Generator
Validation: Code Reviewer (ensure no behavior changes)
```

### Performance Optimization

```
Analysis: Data Profiler (identify bottlenecks)
Implementation: Domain Expert (Python/Database/React)
Validation: Data Profiler (measure improvements)
```

### Security Enhancements

```
Design: Security Auditor (identify vulnerabilities)
Implementation: Code Generator + Security Auditor
Validation: Security Auditor (verify fixes)
```

---

## Anti-Patterns in Specialist Matching

### Avoid These Mistakes

**❌ Wrong Specialist for Task**:
```
Bad: Assign frontend task to Database Specialist
Good: Assign to React Architect or Code Generator

Bad: Assign security audit to Code Generator
Good: Assign to Security Auditor
```

**❌ Over-Engineering with Wrong Specialist**:
```
Bad: Use React Architect for simple button component
Good: Use Code Generator for standard components

Bad: Use ML Evaluator for basic statistics
Good: Use Data Profiler for straightforward analysis
```

**❌ Under-Engineering with Wrong Specialist**:
```
Bad: Use Code Generator for novel ML architecture
Good: Use ML Evaluator for architectural decisions

Bad: Use Code Generator for complex state management
Good: Use React Architect for architectural complexity
```

---

## Specialist Matching Checklist

Before assigning task to specialist, verify:

- [ ] Task domain matches specialist core capability
- [ ] Complexity level appropriate for specialist
- [ ] Specialist has necessary context
- [ ] Dependencies are available to specialist
- [ ] Task boundaries are clear
- [ ] Success criteria match specialist output type
- [ ] Integration path is defined
- [ ] Specialist is available or queued appropriately

---

*Optimal specialist matching maximizes parallel efficiency and output quality. A Senior Engineering Manager knows each specialist's strengths and limitations.*

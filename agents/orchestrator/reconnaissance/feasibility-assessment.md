# Feasibility Assessment Patterns

## Purpose

Evaluate whether a request can be successfully completed with available resources, within constraints, and at acceptable risk levels.

---

## Complexity Estimation

### Computational Complexity Analysis

**Simple (1-2 specialist-hours)**:
- Single-file changes
- Isolated functionality
- No external dependencies
- Clear requirements
- Established patterns

**Moderate (3-8 specialist-hours)**:
- Multi-file coordination
- Cross-component changes
- Some external dependencies
- Minor ambiguities to resolve
- Adaptation of existing patterns

**Complex (9-24 specialist-hours)**:
- System-wide changes
- New architectural patterns
- Multiple external dependencies
- Significant unknowns
- Novel solutions required

**Very Complex (>24 specialist-hours)**:
- Fundamental redesign
- Breaking changes
- Complex dependency chains
- High uncertainty
- Research required

### Decomposition Complexity

```
Decomposition Effort = Task Count × Dependency Density × Ambiguity Factor

Where:
- Task Count: Number of discrete tasks
- Dependency Density: Average dependencies per task
- Ambiguity Factor: 1.0 (clear) to 3.0 (very ambiguous)
```

---

## Resource Availability Check

### Specialist Availability Matrix

| Specialist Type | Required | Available | Gap | Mitigation |
|----------------|----------|-----------|-----|------------|
| Code Generator | Yes/No | Yes/No | - | Alternative specialist |
| Code Reviewer | Yes/No | Yes/No | - | Peer review fallback |
| Data Profiler | Yes/No | Yes/No | - | Statistical tools |
| React Architect | Yes/No | Yes/No | - | General frontend |
| ML Evaluator | Yes/No | Yes/No | - | Basic metrics |
| Security Auditor | Yes/No | Yes/No | - | Security checklist |

### Resource Constraints

**Time Constraints**:
- Deadline: Specified or ASAP?
- Buffer needed: 20% minimum
- Critical path duration
- Parallelization potential

**Computational Resources**:
- Memory requirements
- Processing power needs
- Storage requirements
- Network bandwidth

**External Dependencies**:
- API availability
- Data access
- Third-party services
- Team dependencies

---

## Risk Identification

### Technical Risks

**High Risk Indicators**:
- 🔴 Modifying critical system components
- 🔴 Touching security boundaries
- 🔴 Changing data models
- 🔴 Breaking API changes
- 🔴 Performance-critical paths

**Medium Risk Indicators**:
- 🟡 Complex integrations
- 🟡 Tight deadlines
- 🟡 Limited testing ability
- 🟡 Dependency on external services

**Low Risk Indicators**:
- 🟢 Isolated changes
- 🟢 Well-tested paths
- 🟢 Rollback capability
- 🟢 Incremental delivery

### Risk Mitigation Strategies

```
For each identified risk:
1. Likelihood: High/Medium/Low
2. Impact: Critical/Major/Minor
3. Mitigation: Specific action
4. Contingency: Fallback plan
5. Owner: Responsible specialist
```

---

## Go/No-Go Criteria

### Go Criteria (All must be true)

- [ ] Success criteria are clear and measurable
- [ ] Required specialists are available
- [ ] Dependencies are accessible
- [ ] Timeline is achievable with buffer
- [ ] Risks are acceptable or mitigatable
- [ ] Integration path is clear

### No-Go Criteria (Any triggers stop)

- [ ] Critical specialists unavailable
- [ ] Blocking dependencies inaccessible
- [ ] Unacceptable security risks
- [ ] Timeline impossible even with full parallelization
- [ ] Success criteria undefined
- [ ] No rollback strategy for critical changes

### Conditional Go (Proceed with caveats)

When some criteria are borderline:
1. Document specific limitations
2. Get stakeholder acceptance
3. Define reduced scope
4. Establish checkpoints
5. Plan incremental delivery

---

## Feasibility Score Calculation

```python
def calculate_feasibility_score():
    scores = {
        'requirements_clarity': 0.0-1.0,  # Weight: 25%
        'resource_availability': 0.0-1.0,  # Weight: 25%
        'technical_difficulty': 0.0-1.0,  # Weight: 20%
        'risk_level': 0.0-1.0,            # Weight: 20%
        'timeline_adequacy': 0.0-1.0,     # Weight: 10%
    }

    weighted_score = sum(score * weight for score, weight in scores.items())

    if weighted_score > 0.7:
        return "HIGH FEASIBILITY - Proceed"
    elif weighted_score > 0.4:
        return "MODERATE FEASIBILITY - Proceed with caution"
    else:
        return "LOW FEASIBILITY - Reconsider or rescope"
```

---

## Feasibility Report Template

```markdown
## Feasibility Assessment for [Request]

### Summary
- Overall Feasibility: HIGH/MODERATE/LOW
- Confidence Level: X%
- Recommended Approach: Standard/Cautious/Incremental

### Complexity Analysis
- Estimated Effort: X specialist-hours
- Decomposition Complexity: Simple/Moderate/Complex
- Novel vs Established: X% novel work

### Resource Assessment
- Required Specialists: [List]
- Availability Gaps: [None/List]
- External Dependencies: [List]

### Risk Analysis
- Critical Risks: [List with mitigations]
- Acceptable Risks: [List]
- Residual Risk Level: Low/Medium/High

### Recommendation
[GO/NO-GO/CONDITIONAL with specific rationale]

### Conditions for Success
1. [Specific requirement]
2. [Specific requirement]
3. [Specific requirement]
```

---

## When Feasibility Is Borderline

### Questions to Ask

1. Can scope be reduced while maintaining core value?
2. Can delivery be incremental?
3. Are there alternative approaches with better feasibility?
4. What's the cost of not proceeding?
5. Can additional resources improve feasibility?

### Scope Reduction Options

- Remove nice-to-have features
- Simplify complex requirements
- Defer non-critical components
- Reduce performance targets
- Limit initial user scope

### Alternative Approaches

- Use existing solutions with adaptation
- Implement minimal viable version first
- Outsource complex components
- Use temporary workarounds
- Phase delivery over time

---

*A Senior Engineering Manager knows: accurate feasibility assessment prevents project failure. Better to identify issues early than fail late.*
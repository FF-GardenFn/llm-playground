# Technical Debt Tracking Checklist

**GATE: Cannot complete refactoring without measuring technical debt impact.**

Refactoring without tracking debt impact = no accountability, no prioritization, no ROI justification.

---

## Technical Debt Fundamentals

**Technical Debt** = Sub-optimal code that slows development.

### Two Components

**Principal**: Amount of debt (code quality issues)
- Lines of duplicated code
- Number of long methods
- Cyclomatic complexity
- Coupling/cohesion metrics
- **Measured in**: Hours to fix

**Interest**: Cost paid continuously
- Time to understand code
- Time to change code
- Bug frequency
- Onboarding time
- **Measured in**: Hours per month (or per year)

**Key Insight**: Pay principal once, save interest forever.

---

## ROI Calculation

**Return on Investment** determines if refactoring is worthwhile:

```
Interest Rate = Hours/month wasted due to debt
Principal = Hours to pay down debt (refactoring time)

ROI = (Interest Rate × 12 months) / Principal

ROI > 1.5 → Good investment (refactor)
ROI < 1.0 → Poor investment (defer or skip)
```

**Example**:
```
Bad Code: Long UserController (500 lines)

Interest:
- 2 hours/month fixing bugs in UserController
- 1 hour/month onboarding new devs to understand it
- 1 hour/month adding features (navigating complexity)
= 4 hours/month

Principal:
- 8 hours to extract services (EmailService, AuthService)

ROI:
- Annual interest: 4 hours/month × 12 = 48 hours/year
- Principal: 8 hours
- ROI = 48 / 8 = 6.0

Excellent ROI! Refactor immediately.
```

---

## Pre-Refactoring Measurement

**Before refactoring, measure baseline**:

### Code Metrics

- [ ] **Lines of code** (total, per method, per class)
  ```bash
  # Python (radon)
  radon cc user_controller.py --show-complexity

  # JavaScript (plato)
  plato -r -d report src/

  # Java (Metrics Reloaded plugin)
  # Or: checkstyle, PMD
  ```

- [ ] **Cyclomatic complexity** (branching complexity)
  - Low: 1-10 (simple)
  - Medium: 11-20 (moderate)
  - High: 21-50 (complex, risky)
  - Very high: 50+ (untestable, dangerous)

- [ ] **Duplicate code** (copy-paste violations)
  ```bash
  # Python (pylint)
  pylint --disable=all --enable=duplicate-code

  # JavaScript (jscpd)
  jscpd src/

  # Java (CPD from PMD)
  pmd cpd --files src/
  ```

- [ ] **Test coverage** (safety net size)
  ```bash
  # Current coverage
  pytest --cov=user_controller --cov-report=term
  ```

### Developer Pain Points

- [ ] **Time spent on bugs** (last 3 months)
  - Query issue tracker: "label:bug component:UserController"
  - Sum time spent fixing
  - Divide by 3 = average hours/month

- [ ] **Time spent on changes** (last 3 months)
  - Query issue tracker: "component:UserController"
  - Estimate time spent navigating code, understanding, testing
  - Divide by 3 = average hours/month

- [ ] **Developer survey** (qualitative data)
  - Ask team: "How painful is working with UserController (1-10)?"
  - Ask team: "How long to onboard new developer to UserController?"
  - Capture quotes: "Every time I touch UserController, I break something"

---

## Post-Refactoring Measurement

**After refactoring, measure improvements**:

### Code Metrics (After)

- [ ] **Lines of code** (should be lower or similar)
  - Extracted classes counted separately
  - Main class should be shorter

- [ ] **Cyclomatic complexity** (should be lower)
  - Refactoring reduces branching
  - Extracted methods have lower complexity

- [ ] **Duplicate code** (should be lower)
  - Extraction eliminates duplication
  - Shared logic now in one place

- [ ] **Test coverage** (should be same or higher)
  - Refactoring doesn't change behavior → coverage same
  - New extracted methods may have additional tests → coverage higher

### Developer Experience (Projected)

- [ ] **Estimated time saved on bugs**
  - Simpler code → fewer bugs
  - Estimate: 20-50% reduction in bug time

- [ ] **Estimated time saved on changes**
  - Clear responsibilities → faster changes
  - Estimate: 30-60% reduction in change time

- [ ] **Developer satisfaction** (post-refactor survey)
  - Ask team: "Is UserController easier to work with now (1-10)?"
  - Ask team: "Would you recommend this refactoring?"

---

## ROI Calculation Template

### Step 1: Measure Interest (Before)

**Time wasted per month due to this code**:

- Bug fixes: ___ hours/month
- Feature changes: ___ hours/month
- Code review time: ___ hours/month
- Onboarding time: ___ hours/month (amortized)
- **Total Interest**: ___ hours/month

### Step 2: Measure Principal

**Time spent refactoring**:

- Planning: ___ hours
- Implementation: ___ hours
- Testing: ___ hours
- Code review: ___ hours
- **Total Principal**: ___ hours

### Step 3: Calculate ROI

```
Annual Interest Saved = Interest/month × 12 months
ROI = Annual Interest Saved / Principal
```

**Example**:

```
Interest:
- Bug fixes: 2 hours/month
- Feature changes: 3 hours/month
- Code review: 1 hour/month
- Onboarding: 6 hours/year ÷ 12 = 0.5 hours/month
Total: 6.5 hours/month

Principal:
- Planning: 2 hours
- Implementation: 10 hours
- Testing: 2 hours
- Code review: 1 hour
Total: 15 hours

ROI:
- Annual interest saved: 6.5 × 12 = 78 hours/year
- ROI = 78 / 15 = 5.2

Excellent ROI! Refactoring justified.
```

---

## Debt Inventory

**Maintain inventory of known technical debt**:

| ID | Component | Smell | Interest (hrs/mo) | Principal (hrs) | ROI | Priority | Status |
|----|-----------|-------|-------------------|-----------------|-----|----------|--------|
| TD-001 | UserController | Large Class | 6.5 | 15 | 5.2 | HIGH | ✅ Resolved |
| TD-002 | OrderService | Duplicate Code | 3.0 | 8 | 4.5 | HIGH | 🔄 In Progress |
| TD-003 | PaymentProcessor | Long Method | 2.0 | 4 | 6.0 | HIGH | 📋 Open |
| TD-004 | ReportGenerator | Complex Conditional | 1.0 | 10 | 1.2 | MEDIUM | 📋 Open |
| TD-005 | EmailFormatter | Primitive Obsession | 0.5 | 6 | 1.0 | LOW | 📋 Open |

**Prioritize by ROI**: High ROI items first.

---

## Debt Checklist (Gate)

**Before marking refactoring complete**:

### Pre-Refactoring

- [ ] Measured baseline code metrics (LOC, complexity, duplication)
- [ ] Estimated interest (time wasted per month)
- [ ] Identified developer pain points
- [ ] Documented current state

### Post-Refactoring

- [ ] Measured improved code metrics (LOC, complexity, duplication)
- [ ] Calculated principal (time spent refactoring)
- [ ] Calculated ROI (interest saved / principal)
- [ ] Verified ROI > 1.5 (worthwhile refactoring)

### Tracking

- [ ] Updated debt inventory (resolved, in progress, or open)
- [ ] Documented lessons learned
- [ ] Shared results with team

**If any unchecked, debt tracking incomplete.**

---

## Example: UserController Refactoring

### Pre-Refactoring Measurements

**Code Metrics (Before)**:
- Lines of code: 487 lines
- Cyclomatic complexity: 42 (very high)
- Duplicate code: 85 lines (3 similar email methods)
- Test coverage: 78%

**Interest Calculation**:
- Bug fixes: 2 hours/month (bugs in email logic)
- Feature changes: 3 hours/month (hard to add features)
- Code review: 1 hour/month (reviewers struggle)
- Onboarding: 6 hours/new dev (1 new dev/year) = 0.5 hours/month
- **Total: 6.5 hours/month**

### Refactoring Work

**Principal**:
- Planning: 2 hours (identify services to extract)
- Implementation: 10 hours (extract EmailService, AuthService)
- Testing: 2 hours (write tests for new services)
- Code review: 1 hour
- **Total: 15 hours**

### Post-Refactoring Measurements

**Code Metrics (After)**:
- UserController: 213 lines (was 487) → 56% reduction
- EmailService: 98 lines (new)
- AuthService: 145 lines (new)
- Cyclomatic complexity: UserController = 18 (was 42) → 57% reduction
- Duplicate code: 0 lines (was 85) → 100% reduction
- Test coverage: 85% (was 78%) → 7% improvement

**Interest Saved**:
- Bug fixes: Estimated 1 hour/month (was 2) → 50% reduction
- Feature changes: Estimated 1.5 hours/month (was 3) → 50% reduction
- Code review: Estimated 0.5 hours/month (was 1) → 50% reduction
- Onboarding: Estimated 3 hours/new dev (was 6) → 50% reduction = 0.25 hours/month
- **Total: 3.25 hours/month saved**

**ROI**:
- Annual interest saved: 3.25 hours/month × 12 = 39 hours/year
- Principal: 15 hours
- **ROI = 39 / 15 = 2.6**

**Conclusion**: Good ROI. Refactoring justified and successful.

### Debt Inventory Update

| ID | Component | Smell | Interest (hrs/mo) | Principal (hrs) | ROI | Priority | Status |
|----|-----------|-------|-------------------|-----------------|-----|----------|--------|
| TD-001 | UserController | Large Class | 6.5 → 3.25 | 15 | 2.6 | HIGH | ✅ **Resolved** |

**Lessons Learned**:
- Extracting services reduced complexity by 57%
- Email bugs dropped significantly (isolated logic)
- Team velocity improved (easier to work with)
- Next: Consider extracting ValidationService

---

## When ROI is Low

**If ROI < 1.5**: Refactoring may not be worthwhile.

**Options**:
1. **Defer**: Keep in debt inventory, revisit later
2. **Smaller scope**: Refactor only highest-pain parts
3. **Skip**: Accept debt, focus on higher-ROI improvements

**Example**:
```
Code: ReportGenerator (complex conditionals)

Interest: 1 hour/month
Principal: 10 hours (refactor entire class)
ROI: (1 × 12) / 10 = 1.2 (low)

Decision: Defer. Not worth 10 hours for 1 hour/month savings.

Alternative: Refactor only most complex method (2 hours)
ROI: (1 × 12) / 2 = 6.0 (high)
```

---

## Debt Tracking Tools

**Code Metrics**:
- **Python**: radon, pylint, pytest-cov
- **JavaScript**: plato, jscpd, jest --coverage
- **Java**: SonarQube, Checkstyle, PMD, JaCoCo
- **Multi-language**: SonarQube, CodeClimate

**Issue Tracking**:
- JIRA, GitHub Issues, Linear
- Label/tag technical debt items
- Track time spent on debt-related work

**Spreadsheet Template**:
- Debt inventory (ID, component, smell, interest, principal, ROI, status)
- Monthly tracking (interest paid, principal paid, ROI achieved)

---

## Gate Status

**Debt tracking complete**: Only when ALL measurements recorded and ROI calculated.

**If tracking incomplete**:
- Cannot justify refactoring time
- Cannot prioritize future refactorings
- Cannot demonstrate value to stakeholders

**Cannot complete Phase 6 without debt tracking.**

**This is not optional. This is a gate.**

---

## Summary

**Technical debt tracking enforces**:
- Measure baseline (LOC, complexity, interest)
- Measure improvement (metrics, principal)
- Calculate ROI (interest saved / principal)
- Update debt inventory (resolved, in progress, open)

**ROI > 1.5 → Refactor worthwhile**

**ROI < 1.0 → Defer or skip**

**Cannot complete refactoring without measuring debt impact.**

**This gate ensures accountability and prioritization.**

# Risk Assessment Gate

**Purpose**: Evaluate refactoring risk level and determine appropriate safety strategy before implementation.

**When to Use**: Phase 3 of refactoring workflow, after pattern selection and before implementation.

**Gate Criteria**: MUST complete risk assessment and select mitigation strategy before proceeding to implementation.

---

## GATE: Risk Level Determination

Cannot proceed to implementation until:
- [ ] Risk factors evaluated
- [ ] Risk level determined (Low/Medium/High)
- [ ] Mitigation strategy selected
- [ ] Safety technique chosen (if high risk)

**This is not optional. This is a gate.**

---

## Risk Factors

### Factor 1: Test Coverage

| Coverage Level | Risk Contribution | Points |
|----------------|------------------|--------|
| >80% coverage, tests green | Low | +0 |
| 50-80% coverage, tests green | Medium | +1 |
| 20-50% coverage, some tests | High | +2 |
| <20% coverage or no tests | Critical | +3 |

**Your Code**:
- Current test coverage: ____%
- Test status: ☐ All green ☐ Some failures ☐ No tests
- Risk points: ___

---

### Factor 2: Code Coupling

| Coupling Level | Risk Contribution | Points |
|----------------|------------------|--------|
| Low coupling, clear boundaries | Low | +0 |
| Moderate coupling, some dependencies | Medium | +1 |
| High coupling, many dependencies | High | +2 |
| Tight coupling, circular dependencies | Critical | +3 |

**Your Code**:
- Number of classes affected: ___
- External dependencies: ___
- Circular dependencies: ☐ None ☐ Some ☐ Many
- Risk points: ___

---

### Factor 3: Refactoring Complexity

| Complexity Level | Risk Contribution | Points |
|------------------|------------------|--------|
| Easy (Extract Method, Inline Method) | Low | +0 |
| Medium (Move Method, Decompose Conditional) | Medium | +1 |
| Hard (Extract Class, Replace Conditional) | High | +2 |
| Very Hard (Architectural, System-wide) | Critical | +3 |

**Your Refactoring**:
- Pattern selected: _______________
- Pattern difficulty: ☐ Easy ☐ Medium ☐ Hard ☐ Very Hard
- Risk points: ___

---

### Factor 4: Scope of Change

| Scope | Risk Contribution | Points |
|-------|------------------|--------|
| Single method, single class | Low | +0 |
| Multiple methods, single class | Medium | +1 |
| Multiple classes, single module | High | +2 |
| Cross-module, architectural | Critical | +3 |

**Your Change**:
- Methods affected: ___
- Classes affected: ___
- Modules affected: ___
- Risk points: ___

---

### Factor 5: Domain Criticality

| Criticality | Risk Contribution | Points |
|-------------|------------------|--------|
| Non-critical, utility code | Low | +0 |
| Important, but not core business logic | Medium | +1 |
| Core business logic | High | +2 |
| Safety-critical or financial | Critical | +3 |

**Your Code**:
- Domain area: _______________
- Criticality level: ☐ Low ☐ Medium ☐ High ☐ Critical
- Risk points: ___

---

## Total Risk Score Calculation

**Sum all risk points from 5 factors**:

```
Test Coverage:        ___ points
Code Coupling:        ___ points
Refactoring Complexity: ___ points
Scope of Change:      ___ points
Domain Criticality:   ___ points
                      ─────────
TOTAL:                ___ points
```

---

## Risk Level Determination

### Risk Score → Risk Level

| Total Points | Risk Level | Strategy Required |
|--------------|-----------|-------------------|
| 0-2 | **Low** | Standard test-driven refactoring |
| 3-5 | **Medium** | Test-driven + careful verification |
| 6-9 | **High** | MUST use incremental strategy |
| 10+ | **Critical** | Reconsider refactoring or use advanced techniques |

**Your Risk Level**: ☐ Low ☐ Medium ☐ High ☐ Critical

---

## Mitigation Strategies by Risk Level

### Low Risk (0-2 points)

**Strategy**: Standard Test-Driven Refactoring

**Approach**:
1. Ensure tests are green
2. Make refactoring change
3. Run tests
4. If green, commit
5. If red, revert and take smaller step

**Safety Technique**: None required (standard TDD sufficient)

**Proceed to**: Implementation (Phase 4)

---

### Medium Risk (3-5 points)

**Strategy**: Test-Driven + Careful Verification

**Approach**:
1. Ensure tests are green
2. Add characterization tests if coverage gaps
3. Make refactoring change in small steps
4. Run tests after EACH step
5. Verify metrics (complexity, coupling) after completion
6. Manual verification of critical paths

**Safety Technique**: Consider `../safety/techniques/test-driven-refactoring.md` for red-green-refactor discipline

**Additional Checks**:
- [ ] Add characterization tests for uncovered paths
- [ ] Verify no performance regression
- [ ] Manual smoke testing in critical areas
- [ ] Peer review before commit

**Proceed to**: Implementation with enhanced monitoring

---

### High Risk (6-9 points)

**Strategy**: MANDATORY Incremental Strategy

**Approach**: CANNOT use direct refactoring. MUST use one of:

1. **Branch by Abstraction** (`../safety/techniques/branch-by-abstraction.md`)
   - Create abstraction layer
   - Migrate callers gradually
   - Run tests after each migration
   - Remove old implementation when complete

2. **Strangler Fig** (`../safety/techniques/strangler-fig.md`)
   - Build new implementation alongside old
   - Route traffic incrementally to new
   - Monitor and verify correctness
   - Remove old when fully strangled

3. **Parallel Change** (`../safety/techniques/parallel-change.md`)
   - Expand (add new interface/implementation)
   - Migrate (update callers one-by-one)
   - Contract (remove old interface/implementation)
   - Run tests after EACH caller migration

**Required Safety Checks**:
- [ ] Selected incremental technique: _______________
- [ ] Can revert at any point
- [ ] Tests run after every migration step
- [ ] Performance monitoring in place
- [ ] Rollback plan documented

**Do NOT Proceed to direct implementation. MUST use incremental technique.**

---

### Critical Risk (10+ points)

**Strategy**: Reconsider or Use Advanced Techniques

**Options**:

**Option 1: Reduce Risk First**
- Improve test coverage (adds time but reduces risk)
- Break refactoring into smaller pieces
- Decouple code before refactoring
- Re-assess risk after improvements

**Option 2: Accept High Risk with Maximum Safety**
- MUST use incremental strategy (Branch by Abstraction or Strangler Fig)
- MUST have comprehensive monitoring
- MUST have automated rollback capability
- MUST have stakeholder approval
- Consider feature flags for runtime rollback

**Option 3: Defer Refactoring**
- If risk too high and not urgent, defer to future
- Document technical debt
- Address when safer (better tests, lower coupling)

**Required Approval**:
- [ ] Stakeholder aware of risk level
- [ ] Team reviewed approach
- [ ] Rollback plan tested
- [ ] Monitoring in place

**Do NOT proceed without addressing risk factors or obtaining approval.**

---

## Risk Mitigation Techniques

### Technique 1: Improve Test Coverage (Reduces Factor 1 risk)

**Before High-Risk Refactoring**:
1. Add characterization tests
   - Capture current behavior
   - Test edge cases
   - Test error paths
2. Achieve >80% coverage of refactoring target
3. Verify all tests green
4. Re-assess risk (should reduce by 1-2 points)

---

### Technique 2: Break Into Smaller Pieces (Reduces Factor 3 & 4 risk)

**Instead of Large Refactoring**:
1. Identify smallest valuable refactoring
2. Apply in isolation
3. Verify and commit
4. Repeat for next piece
5. Each piece has lower risk than whole

**Example**: Instead of Extract Class (Hard, High Risk):
- Step 1: Extract Method (Easy, Low Risk)
- Step 2: Move Method (Medium, Medium Risk)
- Step 3: Group methods into new class (Medium, Medium Risk)

---

### Technique 3: Decouple First (Reduces Factor 2 risk)

**Before Refactoring Highly Coupled Code**:
1. Introduce interfaces
2. Dependency injection
3. Break circular dependencies
4. Reduce coupling
5. Re-assess risk (should reduce by 1-2 points)
6. Proceed with original refactoring

---

### Technique 4: Feature Flags (Reduces deployment risk)

**For High-Risk Production Changes**:
1. Wrap refactored code in feature flag
2. Deploy with flag OFF
3. Enable flag for testing/staging
4. Gradually enable in production (percentage rollout)
5. Monitor metrics
6. Full rollout when verified safe
7. Remove flag

---

## Safety Technique Selection

### For Low Risk
**No special technique needed** - Standard TDD sufficient

### For Medium Risk
**Choose ONE**:
- ☐ `test-driven-refactoring.md` - Red-green-refactor discipline
- ☐ Enhanced verification (metrics, manual testing, peer review)

### For High Risk
**MUST Choose ONE**:
- ☐ `branch-by-abstraction.md` - Interface migration (best for API changes)
- ☐ `strangler-fig.md` - Parallel implementation (best for system replacement)
- ☐ `parallel-change.md` - Expand-migrate-contract (best for interface evolution)

### For Critical Risk
**MUST Choose ONE Advanced Approach**:
- ☐ Reduce risk first (improve tests, decouple, break into pieces)
- ☐ Branch by Abstraction + Feature Flags + Monitoring
- ☐ Strangler Fig + Percentage Rollout + Automated Rollback
- ☐ Defer refactoring (document technical debt)

---

## Rollback Planning

### Rollback Triggers

**Immediate Rollback If**:
- Tests fail after refactoring step
- Performance degrades >20%
- Production errors spike
- Critical functionality broken

### Rollback Procedure

**Version Control Rollback**:
```bash
# Identify last good commit
git log --oneline

# Revert to last good state
git revert <commit-hash>

# Or hard reset if not pushed
git reset --hard <commit-hash>
```

**Incremental Strategy Rollback**:
- If using Branch by Abstraction: Switch back to old implementation
- If using Strangler Fig: Route traffic back to old system
- If using Parallel Change: Still at expand or migrate phase, old interface still works

**Feature Flag Rollback**:
```python
# Disable feature flag
feature_flags.set("new_refactored_code", False)
# Immediately returns to old behavior
```

---

## Risk Assessment Examples

### Example 1: Extract Method in Well-Tested Utility

**Risk Factors**:
- Test Coverage: 95% coverage, all green → +0 points
- Coupling: Single method, no dependencies → +0 points
- Complexity: Extract Method (Easy) → +0 points
- Scope: Single method, single class → +0 points
- Criticality: Utility code → +0 points

**Total**: 0 points → **Low Risk**

**Strategy**: Standard TDD, proceed with confidence

---

### Example 2: Move Method in Business Logic

**Risk Factors**:
- Test Coverage: 60% coverage → +1 point
- Coupling: Method uses 3 classes → +1 point
- Complexity: Move Method (Medium) → +1 point
- Scope: 2 classes affected → +1 point
- Criticality: Core business logic → +2 points

**Total**: 6 points → **High Risk**

**Strategy**: MUST use incremental (Parallel Change recommended)

**Mitigation**:
1. Add tests to improve coverage (reduce to 4 points)
2. Use Parallel Change:
   - Expand: Add method in new location
   - Migrate: Update callers one-by-one, run tests after each
   - Contract: Remove old method when all migrated

---

### Example 3: Extract Class in Legacy Code

**Risk Factors**:
- Test Coverage: 15% coverage → +3 points
- Coupling: Circular dependencies → +3 points
- Complexity: Extract Class (Hard) → +2 points
- Scope: 5 classes, 2 modules → +2 points
- Criticality: Core financial logic → +2 points

**Total**: 12 points → **Critical Risk**

**Strategy**: Reduce risk first

**Recommended Approach**:
1. **Phase 1**: Add comprehensive tests (reduce Factor 1 to +1)
2. **Phase 2**: Break circular dependencies (reduce Factor 2 to +1)
3. **Phase 3**: Break Extract Class into smaller refactorings (reduce Factor 3 & 4)
4. **Re-assess**: Should be ~6-7 points (High Risk, manageable)
5. **Phase 4**: Use Branch by Abstraction for final extraction

**Timeline**: 2-3 weeks (vs 2-3 days for direct approach with high failure risk)

---

## Gate Completion Checklist

Before proceeding to implementation:

- [ ] All 5 risk factors evaluated
- [ ] Total risk score calculated: ___ points
- [ ] Risk level determined: ☐ Low ☐ Medium ☐ High ☐ Critical
- [ ] Mitigation strategy selected: _______________
- [ ] Safety technique chosen (if High/Critical): _______________
- [ ] Rollback plan documented
- [ ] Stakeholder approval (if Critical risk)

**Gate Status**: ☐ PASS (proceed to implementation) ☐ FAIL (address risks first)

---

## Integration with Workflow

**Previous Phase**: Refactoring Selection (`../refactorings/INDEX.md`)
**Current Phase**: Risk Assessment (this file)
**Next Phase**: Implementation (Phase 4 of workflow)

**Workflow Position**:
```
Phase 1: Smell Detection
    ↓
Phase 2: Refactoring Selection
    ↓
Phase 3: Safety Check
    ├─→ Prerequisites Gate (../safety/prerequisites.md) ✓
    └─→ Risk Assessment Gate (THIS FILE) ← YOU ARE HERE
        ↓
Phase 4: Implementation
```

---

## Quick Reference

**Risk Formula**: Test Coverage + Coupling + Complexity + Scope + Criticality = Total Points

**Risk Levels**:
- 0-2: Low (standard TDD)
- 3-5: Medium (careful verification)
- 6-9: High (incremental strategy REQUIRED)
- 10+: Critical (reduce risk or advanced techniques)

**Incremental Strategies for High Risk**:
- Branch by Abstraction (interface migration)
- Strangler Fig (parallel replacement)
- Parallel Change (expand-migrate-contract)

**Next Step**: After completing risk assessment, proceed to implementation (Phase 4) with selected strategy.

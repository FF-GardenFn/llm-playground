# Validation Checklist

## Success Criteria (from main AGENT.md)

### Testing
- [ ] All new tests pass
- [ ] All existing tests pass (no regressions)
- [ ] Edge cases covered (null, empty, large input, etc.)
- [ ] Error handling tested

### Code Quality
- [ ] Linting clean (no warnings or errors)
- [ ] Follows codebase patterns (identified in reconnaissance)
- [ ] Self-documenting code (clear names, strategic comments)
- [ ] Complexity reasonable (cyclomatic complexity <10)

### Functionality
- [ ] Feature works as specified
- [ ] Integration points work correctly
- [ ] Error messages clear and actionable
- [ ] No obvious bugs

### Performance
- [ ] No performance issues (no N+1 queries, memory leaks, etc.)
- [ ] Algorithms efficient (appropriate time complexity)
- [ ] No unnecessary database hits or network calls

### Maintainability
- [ ] Junior engineer could understand code in 6 months
- [ ] Design is simple (not over-engineered)
- [ ] Changes are minimal (small diff)
- [ ] Documentation updated (if public API changed)

---

## Validation Tools

**Full Test Suite:**
```bash
bash atools/run_tests.sh
```

**Linting:**
```bash
bash atools/lint_code.sh path/to/modified/files
```

**Complexity:**
```bash
python atools/analyze_complexity.py path/to/modified/files
```

---

## Pass Criteria

**ALL items must be checked before declaring task complete.**

If any item unchecked:
1. Identify issue
2. Fix issue
3. Re-run validation
4. Repeat until all checked

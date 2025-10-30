---
description: Load specific workflow phase (requirements, pattern, state, performance, testing, accessibility)
allowed-tools: Read, Write, Edit, Glob, Grep, TodoWrite
argument-hint: [phase-name]
---

## Phase Command

**Usage**: `/phase requirements` or `/phase pattern` etc.

**Available Phases**:
1. `requirements` - Requirements Analysis (Purpose, interactions, data, edge cases, success criteria)
2. `pattern` - Pattern Selection (Component type, patterns, files to load, code structure)
3. `state` - State Management (State shape, updates, data flow, strategy, edge case handling)
4. `performance` - Performance Optimization (memo, useMemo, useCallback, virtualization, debounce)
5. `testing` - Testing Strategy (Unit, integration, edge case, accessibility tests)
6. `accessibility` - Accessibility Audit (Keyboard, screen reader, ARIA, contrast, touch targets)

##  Gate Enforcement

**Cannot proceed to next phase until current phase gates pass**.

**Phase 1 → Phase 2**: Requirements documented
**Phase 2 → Phase 3**: Patterns chosen with rationale
**Phase 3 → Phase 4**: State strategy defined
**Phase 4 → Phase 5**: Performance checklist complete
**Phase 5 → Phase 6**: Test plan documented
**Phase 6 → Deploy**: Accessibility checklist passed

## Files to Load

**Phase 1 (Requirements)**: `workflows/COMPONENT_DEVELOPMENT.md` (Phase 1 section)
**Phase 2 (Pattern)**: `patterns/composition/INDEX.md`, `patterns/composition/*.md`
**Phase 3 (State)**: `state/hooks/*.md`, `state/patterns/*.md`
**Phase 4 (Performance)**: `performance/checklist.md`, `performance/*.md`
**Phase 5 (Testing)**: `testing/react-testing-library.md`
**Phase 6 (Accessibility)**: `accessibility/audit-checklist.md`

## Example

```
User: /phase requirements
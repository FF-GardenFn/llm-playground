---
description: Run checklists (performance or accessibility audit)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: [checklist-type]
---

## Check Command

**Usage**: `/check performance` or `/check accessibility`

**Available Checklists**:
- `performance` - Performance optimization checklist (memo, useMemo, useCallback, virtualization)
- `accessibility` - Accessibility audit checklist (keyboard, screen reader, ARIA, contrast)

## Performance Checklist

{{load: ${CLAUDE_PLUGIN_ROOT}/performance/checklist.md}}

## Accessibility Checklist

{{load: ${CLAUDE_PLUGIN_ROOT}/accessibility/audit-checklist.md}}

## Gates

**Performance Gate**: Cannot claim performance work complete without addressing ALL applicable checks
**Accessibility Gate**: Cannot deploy without passing ALL WCAG AA checks

## Example

```
User: /check accessibility
Agent: Loads accessibility/audit-checklist.md and runs audit
```

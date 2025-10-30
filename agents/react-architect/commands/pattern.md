---
description: Load composition patterns (simple-components, render-props, hoc)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: [pattern-type]
---

## Pattern Command

**Usage**: `/pattern simple` or `/pattern render-props` or `/pattern hoc`

**Available Patterns**:
- `simple` - Simple Components (decompose into sub-components)
- `render-props` - Render Props (pass function as prop to control rendering)
- `hoc` - Higher-Order Components (wrap component to add functionality)

## Files to Load

- `/pattern simple` → `patterns/composition/simple-components.md`
- `/pattern render-props` → `patterns/composition/render-props.md`
- `/pattern hoc` → `patterns/composition/hoc.md`

## Decision Tree

**When to Use**:
- **Simple Components**: Component has distinct sections or responsibilities
- **Render Props**: Logic is reusable but UI varies
- **HOC**: Cross-cutting concern applied to many components

{{load: ${CLAUDE_PLUGIN_ROOT}/patterns/composition/INDEX.md}}

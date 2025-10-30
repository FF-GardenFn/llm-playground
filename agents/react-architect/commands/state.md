---
description: Load state management patterns (hooks, context, redux, zustand, jotai)
allowed-tools: Read, Write, Edit, TodoWrite
argument-hint: [state-pattern]
---

## State Command

**Usage**: `/state hooks` or `/state redux` etc.

**Available Patterns**:
- `hooks` - useState, useReducer, custom hooks
- `context` - Context API for global state
- `redux` - Redux toolkit for large apps
- `zustand` - Lightweight state management
- `jotai` - Atomic state management

## Decision Tree

```
Is state simple (<5 fields, no interdependencies)?
├─ YES → useState
└─ NO → Is state complex (>5 fields, interdependencies)?
         ├─ YES → useReducer
         └─ NO → Need to share across components?
                  ├─ YES → Context / Zustand / Redux
                  └─ NO → useState
```

## Files

**Hooks**: `state/hooks/useState.md`, `state/hooks/useReducer.md`
**Global**: `state/patterns/redux.md`, `state/patterns/zustand.md`, `state/patterns/jotai.md`

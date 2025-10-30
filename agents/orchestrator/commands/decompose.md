---
description: Break complex work into parallelizable tasks with dependencies (Orchestration Phase 2)
allowed-tools: Bash(python atools/dependency_analyzer.py:*), Read, Write, TodoWrite
argument-hint: [--strategy domain|layer|component|phase]
---

# Decomposition Command

Execute Phase 2 orchestration: break complex work into parallelizable units with clear dependencies.

## What this does

1. **Decomposes work** by strategy (domain, layer, component, phase)
2. **Analyzes dependencies** (blocking vs parallelizable)
3. **Assesses granularity** (30min-2hr optimal task size)
4. **Plans merge strategy** (integration approach, conflict prediction)
5. **Uses dependency_analyzer.py** for critical path and parallelization levels

## Usage

```bash
# Auto-select decomposition strategy
/decompose

# Specify strategy explicitly
/decompose --strategy domain  # By domain (auth, billing, notifications)
/decompose --strategy layer   # By layer (schema, backend, frontend)
/decompose --strategy phase   # By phase (design, implement, test)
```

## Your Task

1. **Load decomposition workflow**: Read `decomposition/strategies.md`
2. **Select strategy**: Choose appropriate decomposition approach
3. **Decompose tasks**: Break work into 30min-2hr units
4. **Analyze dependencies**: Use `atools/dependency_analyzer.py`
5. **Plan merge**: Read `decomposition/merge-planning.md`
6. **Complete gate**: `decomposition/GATE-TASKS-DECOMPOSED.md`
7. **Report**: Task graph with dependencies, execution order, parallelization levels

## Expected Output

```
✓ Decomposition complete (strategy: phase)

Task Graph:
A: Design auth schema (1hr)
B: Implement JWT logic (2hr) [depends on A]
C: Create login endpoint (1.5hr) [depends on B]
D: Create refresh endpoint (1hr) [depends on B]
E: Add auth middleware (1hr) [depends on B]
F: Write tests (2hr) [depends on C, D, E]
G: Security review (1hr) [depends on F]

Dependencies:
A → B → [C, D, E] → F → G
         ↑parallel↑

Parallelization Analysis (dependency_analyzer.py):
- Topological order: [A, B, C, D, E, F, G]
- Parallelization levels: [[A], [B], [C,D,E], [F], [G]]
- Critical path: A→B→C→F→G (6.5 hours)
- Speedup potential: 1.4x (with parallelization)

Merge Strategy:
- Integration approach: Incremental (merge after each task)
- Conflict prediction: LOW (clear file boundaries)

→ Recommend: /delegate to assign specialists
```

## Gate

**Cannot proceed to /delegate without**:
- [ ] Tasks decomposed to 30min-2hr granularity
- [ ] Dependencies explicit (blocking vs parallel)
- [ ] Parallelization opportunities identified
- [ ] Integration strategy defined

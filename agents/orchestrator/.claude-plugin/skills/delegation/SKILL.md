---
name: orchestrator-phase-3-delegation
description: Use to assign each task to the best-matched specialist with sufficient context and clear integration points. Enforce the Delegation gate before coordination.
---

# Phase 3: Delegation (Skill)

{{load: ${CLAUDE_PLUGIN_ROOT}/../delegation/specialist-matching.md}}

{{load: ${CLAUDE_PLUGIN_ROOT}/../delegation/context-provision.md}}

Expected outcome: assignments list with rationale, confidence scores, context packs, and integration points.

Gate: `delegation/GATE-SPECIALISTS-ASSIGNED.md`
---
description: Systematic ML training through reproducible 5-phase pipeline with auto-loading diagnostics
---

# ML Trainer Skill

Load the complete ML Trainer agent for deterministic training pipelines.

## When to use this skill

Use when you need to:
- Train ML models with reproducibility guarantees
- Establish baseline performance quickly (30-60 min)
- Diagnose performance bottlenecks systematically
- Optimize model performance with targeted recommendations
- Deploy production-ready models with comprehensive validation

## What this skill provides

The ML Trainer agent embodies a **Deterministic Training Specialist** cognitive model through a systematic 5-phase pipeline:

1. **Phase 1: Planning** - Reproducibility infrastructure setup
2. **Phase 2: Baseline** - Fast baseline training (30-60 min)
3. **Phase 3: Diagnostics** - Performance bottleneck analysis (optional)
4. **Phase 4: Optimization** - Targeted improvements (optional)
5. **Phase 5: Finalization** - Production training & deployment prep

## Quick Start

```bash
# Phase 2: Baseline training
/train-baseline

# Phase 3: Diagnostic analysis (if baseline insufficient)
/diagnose

# Phase 4: Optimization (if recommendations generated)
/optimize

# Phase 5: Production finalization
/finalize
```

## Architecture

**Flexible Branching**:
- Fast path: Phase 1 → 2 → 5 (if baseline sufficient)
- Typical path: Phase 1 → 2 → 3 → 4 → 5 (with optimization)
- Complex path: Multiple Phase 4 iterations (max 2-3)

**Reproducibility-First**:
- Cannot train without seed fixing (enforced architecturally)
- Phase 1 gate blocks progression without reproducibility setup

**Auto-Loading Diagnostics**:
- NaN loss → diagnostics/nan_loss.md
- Convergence stall → diagnostics/convergence_stall.md
- Overfitting → diagnostics/overfitting.md
- Underfitting → diagnostics/underfitting.md

**Gate Enforcement**:
- 5 mandatory gates (one per phase)
- Cannot proceed without satisfying checkpoints
- Most stringent: Phase 5 (24-item production readiness)

## Your Task

When this skill is invoked, load the complete agent prompt from:

```
${CLAUDE_PLUGIN_ROOT}/AGENT.md
```

Then provide systematic training guidance through the 5-phase pipeline, loading supporting files on-demand:
- Phase workflows: `phases/{phase_number}_{phase_name}/workflow.md`
- Diagnostics: `diagnostics/{issue}.md`
- Checklists: `phases/{phase}/checklists/{gate}.md`
- Tools: `SKILLS.md` for tool documentation

## Expected Workflow

1. User describes training task
2. Guide through Phase 1 (reproducibility setup)
3. Execute Phase 2 (baseline training)
4. **Decision point**:
   - If baseline sufficient → Phase 5
   - If baseline insufficient → Phase 3 → Phase 4 → Phase 5
5. Final output: Production-ready model with deployment docs

## Key Features

- **Zero anti-patterns**: No "You are..." instructions, all behavior structural
- **Progressive disclosure**: 394-line main file, 20+ supporting files
- **Mandatory gates**: Block progression if checkpoints incomplete
- **Context-driven navigation**: Auto-load diagnostics based on training issues
- **Production validation**: 24-item gate before deployment

## Success Criteria

Training complete when:
- Model meets target accuracy on held-out test set
- All production readiness checks passed (24 items)
- Model exported to deployment format (ONNX/TorchScript)
- Deployment documentation complete
- Stakeholder approval obtained

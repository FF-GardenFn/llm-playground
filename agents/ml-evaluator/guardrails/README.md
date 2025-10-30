# Guardrails: Anti-Hallucination Rules

## Purpose
Structural gates that prevent statistical sloppiness. Load before making claims.

## The 7 Guardrails

### 01: No Naked Point Estimates → 01-no-naked-estimates.md
**Rule:** Every metric needs confidence interval
**Trigger:** When reporting any performance metric
**Prevents:** Overstating precision, ignoring uncertainty

### 02: Mandatory Significance Testing → 02-mandatory-significance.md
**Rule:** Any comparison requires statistical test
**Trigger:** When comparing models, claiming improvement
**Prevents:** Claiming improvement from noise

### 03: Baseline Requirement → 03-baseline-requirement.md
**Rule:** Every metric needs context
**Trigger:** When reporting performance
**Prevents:** Meaningless metrics without reference points

### 04: Stratification Reflex → 04-stratification-reflex.md
**Rule:** Decompose by subgroups automatically
**Trigger:** When analyzing performance
**Prevents:** Hiding disparities in aggregate metrics

### 05: Calibration Check → 05-calibration-check.md
**Rule:** Probabilities must match reality
**Trigger:** When model outputs probabilities
**Prevents:** Trusting uncalibrated confidence scores

### 06: Leakage Audit → 06-leakage-audit.md
**Rule:** Hunt for data contamination
**Trigger:** At start of evaluation
**Prevents:** Inflated performance from data leakage

### 07: Reproducibility Proof → 07-reproducibility-proof.md
**Rule:** Document everything for replication
**Trigger:** When finalizing evaluation
**Prevents:** Irreproducible findings

## How Guardrails Work

**As structural gates:**
1. Guardrail file MUST be loaded before making claim
2. File specifies rule, enforcement, examples
3. Loading guardrail triggers proper procedures
4. Violations become architecturally visible

**Example flow:**
```
User: "What's the model accuracy?"
  ↓
AGENT: Load guardrails/01-no-naked-estimates.md
  ↓
Guardrail 01: "Every metric needs CI"
  ↓
AGENT: Compute accuracy with bootstrap CI
  ↓
Report: "Accuracy: 0.85 [95% CI: 0.82, 0.88]"
```

## This Is Not Discipline

This is architecture. Structure enforces statistical rigor.

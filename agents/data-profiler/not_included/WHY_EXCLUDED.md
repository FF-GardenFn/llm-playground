# Archive Explanation

This directory contains files excluded from the production-ready data-profiler agent.

## Why These Files Are Archived

### Legacy Prompts (not_included/)

These files were valuable during the agent's development but contain anti-patterns that conflict with production standards:

**1. data-profiler.md (876 lines)**
- Purpose: Original agent prompt (pre-ULTRATHINK transformation)
- Why archived: Contains "You are..." instructions (anti-pattern)
  - Line 7: "You are a Senior Data Quality Engineer and ML Data Scientist..."
  - Line 11: "You are not just a data inspector - you are a systematic analyst..."
  - Line 66: "Constantly ask yourself..."
- Anti-pattern type: Probability warping through identity declarations
- Value: Historical baseline, shows evolution from instructional to structural design

**2. COGNITIVE_MODEL_DESIGN.md (528 lines)**
- Purpose: Design notes and cognitive model architecture
- Why archived: Meta-analysis belongs in research, not production
- Anti-pattern type: Design documentation for developers, not for Claude
- Value: Reference for understanding the agent's architectural decisions

## ULTRATHINK Principle: Zero Anti-Patterns

Production agents must have **zero instructional anti-patterns**:
- ❌ No "You are..." identity declarations (probability warping)
- ❌ No "Your approach is..." behavioral prescriptions
- ❌ No "Constantly ask yourself..." meta-instructions
- ❌ No meta-explanations about prompt design (self-referential)
- ❌ No design documents in production directory (context pollution)

**The structure itself should embody behavior, not instruct it.**

## What Remains in Production

The production-ready agent includes:
- ✅ AGENT.md (navigation hub, clean structural design)
- ✅ Content categories (schema/, quality/, integrity/, ml-risks/, bias/, priorities/)
- ✅ Tool suite (atools/ with 4 Python tools)
- ✅ Verification framework (verification/)
- ✅ .claude-plugin/ (plugin infrastructure)

Total production directory: ~50 files, focused on operational content only.

## Comparison: Before vs After

### Before (Instructional)
```markdown
You are a Senior Data Quality Engineer and ML Data Scientist...

You are not just a data inspector - you are a systematic analyst who:
- Thinks in distributions, not adjectives
- Detects ML risks before they become model failures
- Quantifies every finding with exact numbers
```

### After (Structural)
```markdown
# Data Profiler

ML data quality assessment through systematic risk detection.

## Workflow

Five sequential phases:
1. Reconnaissance → schema/
2. Quality → quality/
3. Integrity → integrity/
4. ML Risks → ml-risks/
5. Bias → bias/

Navigate to categories for analysis patterns.
```

The "after" version creates the same behavior through structure (categories, workflow, tools) rather than instructions.

## Accessing Archived Content

Developers and researchers can access these files for:
- Understanding design decisions
- Learning about structural vs instructional prompting
- Historical context on agent evolution
- Cognitive model research

**Users worldwide accessing the production agent will never see these files.**

## Transformation Summary

- **Removed**: 1,404 lines of instructional/design content
- **Impact**: Eliminates probability warping, reduces context pollution
- **Result**: Behavior emerges from architecture, not instructions
- **Score improvement**: Zero Anti-Patterns principle 2/10 → 10/10 (+8 points)

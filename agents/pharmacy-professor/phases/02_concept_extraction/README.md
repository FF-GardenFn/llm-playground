# Phase 2: Concept Extraction

## Purpose
Extract key pharmaceutical concepts from ingested content and build hierarchical knowledge structures.

## Trigger
Automatically initiated when Phase 1 (Content Ingestion) completes with valid `chunks.json`.

## Input Artifacts
```yaml
required:
  - chunks.json: "Indexed content chunks from Phase 1"
  - ingestion_report.md: "Metadata about source content"

optional:
  - domain_context: "Pharmacology, therapeutics, etc."
  - focus_areas: "Specific topics to prioritize"
```

## Process Steps

### Step 1: Concept Identification
Scan chunks for pharmaceutical concepts:

```yaml
concept_types:
  - drug_names: "Brand/generic names"
  - drug_classes: "Therapeutic categories"
  - mechanisms: "MOA descriptions"
  - indications: "Uses and conditions"
  - adverse_effects: "Side effects, toxicities"
  - interactions: "DDIs, food interactions"
  - pk_parameters: "ADME values"
  - dosing: "Doses, schedules"
  - monitoring: "Labs, parameters"
  - clinical_pearls: "Key practice points"
```

### Step 2: Concept Enrichment
For each identified concept:
1. Extract definition from context
2. Identify related concepts
3. Assess importance (low/medium/high/critical)
4. Assign Bloom's level for learning
5. Link to source chunks

### Step 3: Hierarchy Building
Organize concepts into taxonomic structure:

```
Pharmaceutical Concepts
├── Pharmacokinetics
│   ├── Absorption
│   ├── Distribution
│   ├── Metabolism
│   └── Excretion
├── Pharmacodynamics
│   ├── Receptor Interactions
│   └── Dose-Response
├── Drug Classes
│   ├── [Class 1]
│   └── [Class 2]
└── Therapeutics
    ├── Indications
    └── Monitoring
```

### Step 4: Prerequisite Mapping
Identify knowledge dependencies:
- What must be understood before this concept?
- What concepts build upon this one?
- What are the integration points?

## Output Artifacts

### concepts.json
```json
{
  "concepts": [
    {
      "name": "Metformin",
      "type": "drug_name",
      "definition": "Biguanide antidiabetic...",
      "related_concepts": ["Type 2 Diabetes", "Hepatic Glucose"],
      "source_chunks": ["chunk_001", "chunk_003"],
      "importance": "high",
      "bloom_level": "remember"
    }
  ],
  "statistics": {
    "total_concepts": 45,
    "by_type": {"drug_name": 12, "mechanism": 8, ...}
  }
}
```

### concept_hierarchy.md
```markdown
# Concept Hierarchy: [Topic]

## Overview
- Total concepts: X
- Primary topics: X
- Depth levels: X

## Structure
[Tree visualization]

## Key Concepts by Importance
### Critical
- [Concept 1]
- [Concept 2]

### High Priority
- [Concept 3]
...
```

### prerequisites.json
```json
{
  "Pharmacokinetics": {
    "requires": ["Basic Chemistry", "Physiology"],
    "enables": ["Dosing Calculations", "Drug Interactions"]
  }
}
```

## Phase Gate Criteria

### Minimum Requirements
- [ ] At least 5 concepts extracted
- [ ] All concept types represented (if applicable)
- [ ] Hierarchy has valid structure
- [ ] Prerequisites mapped for complex concepts

### Quality Checks
- [ ] No duplicate concepts
- [ ] Definitions are accurate
- [ ] Relationships are bidirectional
- [ ] Source chunks are valid references

## Tools Used
- `concept_extractor.py`: Main extraction tool
- `atools/difficulty_calibrator.py`: For Bloom's level assignment

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No concepts found | Content too short/generic | Review chunking, lower thresholds |
| Shallow hierarchy | Single topic focus | Expected behavior for narrow content |
| Missing prerequisites | Novel content | Flag for manual review |

## Transition to Phase 3
When gate criteria are met:
1. Store artifacts in `phase_02_outputs/`
2. Log extraction statistics
3. Trigger Phase 3 (Clarification) with user if interactive
4. Pass `concepts.json` to Phase 3

## Example Output

### Input Chunk
```
"Metformin decreases hepatic glucose production and improves
insulin sensitivity. It is first-line therapy for type 2 diabetes
with an A1C-lowering effect of 1-1.5%."
```

### Extracted Concepts
```yaml
- name: "Metformin"
  type: drug_name
  importance: high

- name: "Decreases hepatic glucose production"
  type: mechanism
  related: ["Metformin"]
  importance: high

- name: "First-line therapy for type 2 diabetes"
  type: clinical_pearl
  importance: critical

- name: "A1C-lowering effect of 1-1.5%"
  type: monitoring
  importance: medium
```

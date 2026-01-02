# Pharmacy Professor - Skills & Tools Reference

Comprehensive documentation for all tools and capabilities available to the Pharmacy Professor agent.

---

## Document Processing Tools

### Tool: content_chunker.py

**Purpose**: Chunk large documents into processable segments with pharmaceutical content awareness.

**WHEN to use**:
- Processing PDF lectures or textbook chapters
- Handling long transcripts from video lectures
- Preparing content for concept extraction
- Any document exceeding 2000 tokens

**HOW to use**:
```bash
# Basic chunking
python atools/content_chunker.py --input lecture.txt --output chunks.json

# With custom parameters
python atools/content_chunker.py --input textbook.txt --output chunks.json \
    --chunk-size 800 --overlap 160

# Process with section awareness
python atools/content_chunker.py --input lecture.md --output chunks.json \
    --preserve-sections --extract-metadata
```

**WHAT to look for in output**:
- **chunk_count**: Total number of chunks generated
- **avg_tokens**: Average tokens per chunk (target: 600-900)
- **section_breaks**: Where document sections were preserved
- **metadata**: Page numbers, timestamps, figure references

**WHY this approach works**:
- 800 tokens with 160 overlap (20%) ensures context preservation
- Section awareness prevents mid-concept splits
- SHA256 hashing enables deduplication and caching
- Metadata tracking maintains citation chain

**Common Issues**:
- **Problem**: Chunks splitting mid-sentence
  **Solution**: Use `--preserve-sentences` flag
- **Problem**: Tables not chunking correctly
  **Solution**: Use `--table-aware` to keep tables intact

---

### Tool: format_converter.py

**Purpose**: Convert various input formats to processable text with metadata extraction.

**WHEN to use**:
- Receiving PDF documents
- Processing audio/video transcripts
- Handling images with text (OCR needed)
- Converting presentation slides

**HOW to use**:
```bash
# Convert PDF
python atools/format_converter.py --input lecture.pdf --output lecture.txt

# Convert with OCR for scanned documents
python atools/format_converter.py --input scanned.pdf --output text.txt --ocr

# Extract from audio (requires Whisper)
python atools/format_converter.py --input lecture.mp3 --output transcript.txt --audio

# Process images with diagrams
python atools/format_converter.py --input diagram.png --output description.txt --describe-image
```

**WHAT to look for in output**:
- **format_detected**: Original format identified
- **pages_processed**: For PDFs, number of pages
- **ocr_confidence**: For scanned docs, OCR quality score
- **figures_extracted**: Count of images/diagrams found

**WHY this approach works**:
- Format detection enables automatic processing selection
- OCR fallback handles scanned textbooks
- Image description preserves diagram context
- Metadata extraction maintains structure

**Common Issues**:
- **Problem**: PDF text extraction garbled
  **Solution**: Try `--ocr` flag for scanned PDFs
- **Problem**: Audio transcript has errors
  **Solution**: Use `--language en` to specify language explicitly

---

## Concept Analysis Tools

### Tool: concept_extractor.py

**Purpose**: Identify and organize key pharmaceutical concepts from content.

**WHEN to use**:
- After chunking content (Phase 2)
- Building concept hierarchy
- Identifying drug names and mechanisms
- Mapping prerequisite relationships

**HOW to use**:
```bash
# Basic extraction
python atools/concept_extractor.py --input chunks.json --output concepts.json

# With drug database lookup
python atools/concept_extractor.py --input chunks.json --output concepts.json \
    --verify-drugs --therapeutic-categories

# Build prerequisite map
python atools/concept_extractor.py --input chunks.json --output concepts.json \
    --prerequisites --hierarchy
```

**WHAT to look for in output**:
- **drug_names**: List of drugs with brand/generic mappings
- **mechanisms**: Identified mechanisms of action
- **categories**: Therapeutic classifications
- **hierarchy**: Concept DAG structure
- **prerequisites**: Dependencies between concepts

**WHY this approach works**:
- Pharmaceutical NER trained on drug terminology
- Hierarchical organization mirrors curriculum structure
- Prerequisite mapping enables sequencing
- Brand/generic mapping prevents confusion

**Common Issues**:
- **Problem**: Drug name not recognized
  **Solution**: Check spelling, may be new drug not in database
- **Problem**: Mechanism classification unclear
  **Solution**: Review context, may need manual classification

---

## Material Generation Tools

### Tool: quiz_generator.py

**Purpose**: Generate quiz questions from extracted concepts.

**WHEN to use**:
- Creating assessment materials
- Generating practice questions
- Building exam question banks
- Testing comprehension of concepts

**HOW to use**:
```bash
# Generate MCQs
python atools/quiz_generator.py --concepts concepts.json --type mcq --count 20

# Mixed question types with difficulty distribution
python atools/quiz_generator.py --concepts concepts.json \
    --types mcq,tf,matching \
    --count 30 \
    --difficulty "remember:40,understand:30,apply:20,analyze:10"

# With clinical vignettes
python atools/quiz_generator.py --concepts concepts.json \
    --type mcq --count 15 --vignettes

# Include explanations
python atools/quiz_generator.py --concepts concepts.json \
    --type mcq --count 20 --explanations
```

**WHAT to look for in output**:
- **questions**: Generated question bank
- **bloom_levels**: Distribution across cognitive levels
- **distractors**: Quality of wrong answer choices
- **explanations**: Rationale for correct answers
- **concept_coverage**: Which concepts are tested

**WHY this approach works**:
- Distractor generation uses common misconceptions
- Bloom's level targeting ensures appropriate difficulty
- Clinical vignettes add application context
- Explanations support learning, not just assessment

**Common Issues**:
- **Problem**: Distractors too obviously wrong
  **Solution**: Use `--plausible-distractors` for harder questions
- **Problem**: Questions too easy/hard
  **Solution**: Adjust difficulty distribution

---

### Tool: flashcard_generator.py

**Purpose**: Create Anki-style flashcards for spaced repetition.

**WHEN to use**:
- Creating memorization materials
- Drug facts and definitions
- Mechanism summaries
- Quick-reference cards

**HOW to use**:
```bash
# Basic flashcards
python atools/flashcard_generator.py --concepts concepts.json --output flashcards.json

# Cloze deletions
python atools/flashcard_generator.py --concepts concepts.json \
    --type cloze --output flashcards.json

# With tagging
python atools/flashcard_generator.py --concepts concepts.json \
    --output flashcards.json --tags "topic,difficulty,exam"

# Generate reversible cards
python atools/flashcard_generator.py --concepts concepts.json \
    --output flashcards.json --reversible
```

**WHAT to look for in output**:
- **cards**: Generated flashcard deck
- **card_types**: Distribution (basic, cloze, image)
- **tags**: Applied tags for organization
- **estimated_study_time**: Based on card count

**WHY this approach works**:
- Anki-compatible format for immediate use
- Cloze deletions force active recall
- Tagging enables targeted review
- Reversible cards test both directions

**Common Issues**:
- **Problem**: Cards too long
  **Solution**: Use `--max-length 200` to limit card size
- **Problem**: Missing context on cards
  **Solution**: Use `--include-context` for background info

---

### Tool: difficulty_calibrator.py

**Purpose**: Assess and adjust difficulty using Bloom's Taxonomy.

**WHEN to use**:
- Validating question difficulty
- Adjusting for target audience
- Balancing exam difficulty distribution
- Aligning to learning objectives

**HOW to use**:
```bash
# Analyze difficulty
python atools/difficulty_calibrator.py --questions questions.json --analyze

# Calibrate for target level
python atools/difficulty_calibrator.py --questions questions.json \
    --target intermediate --output calibrated.json

# Check distribution
python atools/difficulty_calibrator.py --questions questions.json --distribution

# Suggest adjustments
python atools/difficulty_calibrator.py --questions questions.json \
    --target "understand:40,apply:40,analyze:20" --suggest
```

**WHAT to look for in output**:
- **bloom_distribution**: Current level breakdown
- **target_alignment**: Match to target distribution
- **adjustments_needed**: Recommended changes
- **question_levels**: Per-question classification

**WHY this approach works**:
- Bloom's taxonomy provides objective classification
- Stem analysis detects cognitive level
- Distribution analysis ensures balance
- Adjustment suggestions maintain validity

**Common Issues**:
- **Problem**: Questions classified incorrectly
  **Solution**: Review question stems, may need rewording
- **Problem**: Can't achieve target distribution
  **Solution**: Generate more questions at needed levels

---

## Orchestration Tools

### Tool: subagent_selector.py

**Purpose**: Match tasks to appropriate specialist subagents.

**WHEN to use**:
- Delegating work to specialists (Phase 4)
- Choosing between content types
- Assigning domain-specific tasks
- Validating subagent choices

**HOW to use**:
```bash
# Single task assignment
python atools/subagent_selector.py --task "Create PK calculation problems" \
    --context context.json

# Batch assignment
python atools/subagent_selector.py --tasks tasks.json --output assignments.json

# With rationale
python atools/subagent_selector.py --task "Generate DDI flashcards" \
    --context context.json --explain
```

**WHAT to look for in output**:
- **specialist**: Recommended subagent
- **confidence**: Match confidence (0.0-1.0)
- **rationale**: Explanation for selection
- **anti_patterns**: Any detected issues
- **alternative**: Second-best option if confidence low

**WHY this approach works**:
- Weighted scoring balances multiple factors
- Anti-pattern detection prevents misassignment
- Confidence thresholds flag uncertain matches
- Alternatives enable manual override

**Scoring Weights**:
- Domain fit: 50%
- Cognitive process alignment: 30%
- Output format match: 20%

**Common Issues**:
- **Problem**: Low confidence score
  **Solution**: Task may need decomposition or clarification
- **Problem**: Anti-pattern detected
  **Solution**: Review task description, may be misframed

---

### Tool: quality_scorer.py

**Purpose**: Assess quality of generated educational materials.

**WHEN to use**:
- Validating generated content (Phase 5)
- Identifying quality issues
- Comparing output alternatives
- Final quality gate

**HOW to use**:
```bash
# Score materials
python atools/quality_scorer.py --materials output.json --output quality_report.json

# With specific criteria
python atools/quality_scorer.py --materials output.json \
    --criteria accuracy,coverage,clarity,alignment,difficulty

# Threshold check
python atools/quality_scorer.py --materials output.json \
    --threshold 80 --fail-on-low

# Improvement suggestions
python atools/quality_scorer.py --materials output.json --suggest-improvements
```

**WHAT to look for in output**:
- **overall_score**: Aggregate quality (0-100)
- **dimension_scores**: Per-dimension breakdown
- **issues**: Identified quality problems
- **suggestions**: Improvement recommendations
- **pass/fail**: Against threshold

**Quality Dimensions**:
- **Accuracy**: Drug information correctness (critical)
- **Coverage**: Concept completeness
- **Clarity**: Language accessibility
- **Alignment**: Learning objective match
- **Difficulty**: Bloom's level appropriateness

**WHY this approach works**:
- Multi-dimensional assessment catches various issues
- Accuracy is weighted highest (pharmaceutical safety)
- Threshold checking enables automated gating
- Suggestions guide iterative improvement

**Common Issues**:
- **Problem**: Low accuracy score
  **Solution**: Critical issue - must verify drug information
- **Problem**: Poor coverage
  **Solution**: Generate additional materials for missing concepts

---

## Common Workflows

### Workflow 1: Lecture to Flashcards

```bash
# Step 1: Convert and chunk
python atools/format_converter.py --input lecture.pdf --output lecture.txt
python atools/content_chunker.py --input lecture.txt --output chunks.json

# Step 2: Extract concepts
python atools/concept_extractor.py --input chunks.json --output concepts.json

# Step 3: Generate flashcards
python atools/flashcard_generator.py --concepts concepts.json --output flashcards.json

# Step 4: Quality check
python atools/quality_scorer.py --materials flashcards.json --threshold 80
```

### Workflow 2: Textbook Chapter to Exam

```bash
# Step 1: Process content
python atools/format_converter.py --input chapter.pdf --output chapter.txt
python atools/content_chunker.py --input chapter.txt --output chunks.json

# Step 2: Extract and select concepts
python atools/concept_extractor.py --input chunks.json --output concepts.json

# Step 3: Generate questions
python atools/quiz_generator.py --concepts concepts.json \
    --types mcq,tf --count 50 --explanations --output questions.json

# Step 4: Calibrate difficulty
python atools/difficulty_calibrator.py --questions questions.json \
    --target "remember:30,understand:30,apply:25,analyze:15" --output calibrated.json

# Step 5: Quality assessment
python atools/quality_scorer.py --materials calibrated.json --threshold 85
```

### Workflow 3: Clinical Case Development

```bash
# Step 1: Extract relevant concepts
python atools/concept_extractor.py --input chunks.json --output concepts.json \
    --focus "drug-interactions,pharmacokinetics"

# Step 2: Assign to case-study-builder
python atools/subagent_selector.py --task "Build clinical case for warfarin-amiodarone interaction"

# Step 3: Generate case materials
# (Case study builder creates scenario, questions, teaching points)

# Step 4: Quality check with clinical focus
python atools/quality_scorer.py --materials case.json \
    --criteria accuracy,clinical_relevance,teaching_value
```

---

## Tool Integration Patterns

### Pattern 1: Sequential Pipeline
```
format_converter → content_chunker → concept_extractor → [generator] → quality_scorer
```

### Pattern 2: Parallel Generation
```
                     ┌→ quiz_generator ────┐
concept_extractor →──┼→ flashcard_generator ┼→ quality_scorer
                     └→ summarizer ────────┘
```

### Pattern 3: Iterative Refinement
```
quiz_generator → difficulty_calibrator → [adjust] → quality_scorer → [if low] → regenerate
```

---

## Error Handling

All tools return structured output with status:

```json
{
  "status": "success|error",
  "data": { ... },
  "error": null | "error message",
  "warnings": [ ... ]
}
```

**Exit Codes**:
- `0`: Success
- `1`: Error (see error message)
- `130`: Cancelled by user

**Logging**:
- Use `--verbose` for detailed logging
- Use `--dry-run` to preview without changes
- Logs written to `stderr`, output to `stdout`

---

## Configuration

Tools can be configured via:
1. Command-line arguments (highest priority)
2. Environment variables (`PHARMACY_PROF_*`)
3. Config file (`~/.pharmacy-professor.yaml`)

**Example Config**:
```yaml
chunking:
  size: 800
  overlap: 160
  preserve_sections: true

generation:
  default_difficulty: intermediate
  include_explanations: true
  vignettes: false

quality:
  accuracy_weight: 0.4
  coverage_weight: 0.25
  clarity_weight: 0.15
  alignment_weight: 0.1
  difficulty_weight: 0.1
  threshold: 80
```

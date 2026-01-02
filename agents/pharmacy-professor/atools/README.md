# Pharmacy Professor Tools (atools)

Command-line tools for the Pharmacy Professor agent.

---

## Tool Inventory

| Tool | Purpose | Primary Phase |
|------|---------|---------------|
| content_chunker.py | Document chunking | Phase 1 |
| format_converter.py | Format conversion | Phase 1 |
| concept_extractor.py | Concept identification | Phase 2 |
| quiz_generator.py | Quiz creation | Phase 5 |
| flashcard_generator.py | Flashcard creation | Phase 5 |
| difficulty_calibrator.py | Bloom's calibration | Phase 5 |
| subagent_selector.py | Specialist matching | Phase 4 |
| quality_scorer.py | Output assessment | Phase 5 |

---

## Quick Reference

### Content Processing
```bash
# Convert PDF to text
python format_converter.py --input lecture.pdf --output lecture.txt

# Chunk document
python content_chunker.py --input lecture.txt --output chunks.json
```

### Concept Extraction
```bash
# Extract concepts
python concept_extractor.py --input chunks.json --output concepts.json
```

### Material Generation
```bash
# Generate flashcards
python flashcard_generator.py --concepts concepts.json --output flashcards.json

# Generate quiz
python quiz_generator.py --concepts concepts.json --count 20 --output quiz.json
```

### Quality Assessment
```bash
# Score materials
python quality_scorer.py --materials output.json --threshold 80
```

---

## Common Options

All tools support:
- `--output, -o`: Output file (default: stdout)
- `--format, -f`: Output format (json, text, markdown)
- `--verbose, -v`: Enable verbose logging
- `--dry-run`: Preview without executing

---

## Output Format

All tools return consistent JSON structure:
```json
{
  "status": "success|error",
  "data": { ... },
  "error": null | "error message"
}
```

---

## Dependencies

- Python 3.10+
- Standard library only (no external dependencies for core tools)
- Optional: sentence-transformers (for embeddings)
- Optional: whisper (for audio transcription)

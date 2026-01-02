---
name: ingest
description: Process and chunk educational content for analysis
arguments:
  - name: file
    description: File path to process (PDF, text, markdown, audio)
    required: true
  - name: output
    description: Output format - chunks, concepts, or both (default: both)
    required: false
---

# Ingest Educational Content

Process and prepare pharmaceutical educational content for further analysis.

## What This Command Does

1. **Detect format** of input file
2. **Convert** to processable text
3. **Chunk** into indexed segments
4. **Extract** key concepts
5. **Build** concept hierarchy

## Quick Examples

```
/ingest lecture.pdf                    # Process PDF
/ingest notes.md concepts              # Extract concepts only
/ingest chapter.txt chunks             # Get chunks only
/ingest recording.mp3                  # Transcribe and process audio
```

## Your Task

When invoked, follow this workflow:

### Step 1: Format Detection
Detect input format:
- PDF → Extract text (OCR if scanned)
- Markdown → Parse directly
- Text → Process as-is
- Audio → Transcribe first
- Image → OCR + describe

### Step 2: Chunking
Process content into indexed chunks:
- Chunk size: 800 tokens
- Overlap: 160 tokens (20%)
- Preserve section boundaries
- Maintain sentence integrity

### Step 3: Concept Extraction
Identify key pharmaceutical concepts:
- Drug names (brand/generic)
- Mechanisms of action
- Drug classes
- Indications
- Adverse effects
- Interactions
- PK parameters

### Step 4: Output Report

```markdown
# Ingestion Report

## Source
- **File**: [filename]
- **Format**: [detected format]
- **Size**: [file size]

## Processing Summary
- **Chunks created**: [count]
- **Total tokens**: [count]
- **Avg tokens/chunk**: [average]
- **Sections detected**: [count]

## Concepts Extracted
- **Drug names**: [count]
- **Mechanisms**: [count]
- **Drug classes**: [count]
- **Clinical concepts**: [count]

## Concept Hierarchy
```
Pharmacology
├── Pharmacokinetics
│   ├── Absorption
│   ├── Distribution
│   └── ...
└── Pharmacodynamics
    └── ...
```

## Ready For
✅ Quiz generation (/quiz)
✅ Flashcard creation (/flashcards)
✅ Study guide generation (/study-guide)
✅ Case study development (/case-study)
```

## Supported Formats

| Format | Extension | Processing |
|--------|-----------|------------|
| PDF | .pdf | Text extraction + OCR fallback |
| Markdown | .md | Direct parsing |
| Text | .txt | Direct processing |
| Audio | .mp3, .wav | Transcription |
| Video | .mp4 | Audio extraction + transcription |
| PowerPoint | .pptx | Slide extraction |
| Image | .png, .jpg | OCR + description |

## Output Options

### chunks
Returns indexed text segments with metadata:
```json
{
  "chunks": [
    {
      "id": "abc123",
      "text": "...",
      "tokens": 756,
      "section": "Introduction",
      "page": 1
    }
  ]
}
```

### concepts
Returns extracted pharmaceutical concepts:
```json
{
  "concepts": [
    {
      "name": "Bioavailability",
      "type": "pk_parameter",
      "definition": "...",
      "related": ["first-pass effect"]
    }
  ]
}
```

### both (default)
Returns both chunks and concepts for full analysis.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Unsupported format | Unknown file type | Convert to supported format |
| OCR failed | Poor image quality | Provide clearer scan |
| Transcription failed | Audio quality | Provide transcript manually |
| File not found | Invalid path | Check file path |

## Next Steps After Ingestion
After content is ingested, you can:
- `/quiz` - Generate quiz questions
- `/flashcards` - Create flashcards
- `/study-guide` - Build study guide
- `/case-study` - Develop clinical case

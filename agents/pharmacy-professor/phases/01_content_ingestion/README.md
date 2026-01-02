# Phase 1: Content Ingestion

**Purpose**: Transform raw educational input into processable, indexed chunks.

---

## Overview

Content ingestion is the foundation of the educational material generation pipeline. This phase handles all input formats and produces indexed, searchable chunks with full provenance tracking.

---

## Supported Formats

| Format | Extension | Processing Method |
|--------|-----------|-------------------|
| PDF | .pdf | Text extraction + OCR fallback |
| Markdown | .md | Direct parsing |
| Plain Text | .txt | Direct processing |
| Audio | .mp3, .wav | Transcription (Whisper) |
| Video | .mp4, .mov | Audio extraction → Transcription |
| Images | .png, .jpg | OCR + Description |
| PowerPoint | .pptx | Slide extraction |

---

## Process Steps

### Step 1: Format Detection
```
Input → Detect MIME type → Select processor
```

Detect format using:
- File extension
- Magic bytes
- Content inspection

### Step 2: Conversion
```
Raw format → format_converter.py → Standardized text + metadata
```

Conversion includes:
- Text extraction
- OCR for scanned content
- Transcription for audio
- Structure preservation

### Step 3: Chunking
```
Text + metadata → content_chunker.py → Indexed chunks
```

Chunking parameters:
- Chunk size: 800 tokens
- Overlap: 160 tokens (20%)
- Section preservation: enabled
- Sentence boundary awareness: enabled

### Step 4: Metadata Extraction
```
Chunks → Extract metadata → Enhanced chunks
```

Metadata includes:
- Page numbers
- Section headers
- Timestamps (for AV content)
- Figure references
- Table locations

### Step 5: Embedding Generation
```
Chunks → Embedder → Semantic vectors
```

Optional for semantic search:
- MiniLM embeddings (384-dim)
- OpenAI embeddings (1536-dim)

---

## Inputs

| Input | Type | Required |
|-------|------|----------|
| content_files | File(s) | Yes |
| source_url | String | Optional |
| metadata | JSON | Optional |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| chunks.json | JSON | Indexed chunks with metadata |
| ingestion_report.md | Markdown | Processing summary |
| embeddings.npy | NumPy | Optional semantic vectors |

### chunks.json Structure
```json
{
  "chunks": [
    {
      "id": "a1b2c3d4",
      "text": "Pharmacokinetics describes how the body processes drugs...",
      "tokens": 756,
      "start_idx": 0,
      "end_idx": 756,
      "section": "Introduction to Pharmacokinetics",
      "page": 1,
      "hash": "sha256:...",
      "metadata": {
        "source_url": "lecture_05.pdf",
        "chunk_index": 0,
        "total_chunks": 45,
        "split_algo": "sliding_800_160"
      }
    }
  ],
  "summary": {
    "total_chunks": 45,
    "total_tokens": 34200,
    "avg_tokens_per_chunk": 760,
    "source_files": ["lecture_05.pdf"],
    "processing_time_seconds": 12.5
  }
}
```

---

## Gate: GATE-CONTENT-INDEXED.md

### Entry Criteria
- [ ] Raw content file(s) provided
- [ ] File format is supported
- [ ] File is readable/accessible

### Exit Criteria
- [ ] All content successfully processed
- [ ] Chunks generated with valid metadata
- [ ] Source attribution preserved for each chunk
- [ ] No processing errors or warnings
- [ ] ingestion_report.md generated

### Blocking Conditions
- Unsupported file format
- Corrupted or unreadable file
- OCR failure on scanned content
- Transcription failure on audio

---

## Tools

### content_chunker.py
```bash
python atools/content_chunker.py \
  --input lecture.txt \
  --output chunks.json \
  --chunk-size 800 \
  --overlap 160 \
  --preserve-sections
```

### format_converter.py
```bash
python atools/format_converter.py \
  --input lecture.pdf \
  --output lecture.txt \
  --ocr  # if needed
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| UnsupportedFormat | Unknown file type | Convert to supported format |
| OCRFailure | Poor image quality | Retry with enhanced settings |
| TranscriptionError | Audio quality issues | Provide transcript manually |
| ChunkingError | Text too short | Adjust parameters |

---

## Quality Metrics

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Avg tokens/chunk | 600-900 | Adjust chunk size |
| Processing errors | 0 | Investigate and fix |
| Metadata coverage | 100% | Add missing metadata |
| Source attribution | 100% | Ensure provenance |

---

## Next Phase

→ **Phase 2: Concept Extraction**

Requires: chunks.json with indexed content

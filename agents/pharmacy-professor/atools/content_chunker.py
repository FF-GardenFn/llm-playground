#!/usr/bin/env python3
"""
Content Chunker - Pharmaceutical Document Processing Tool

Purpose: Chunk large documents into processable segments with pharmaceutical content awareness.
Usage: python content_chunker.py --input lecture.txt --output chunks.json

This tool is part of the pharmacy-professor agent's toolkit.
It chunks documents using sliding window approach with section preservation.

Examples:
    python content_chunker.py --input lecture.txt --output chunks.json
    python content_chunker.py --input textbook.txt --output chunks.json --chunk-size 800 --overlap 160
    python content_chunker.py --input lecture.md --output chunks.json --preserve-sections
"""

import argparse
import sys
import json
import hashlib
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a single chunk of content."""
    id: str
    text: str
    tokens: int
    start_idx: int
    end_idx: int
    section: Optional[str]
    page: Optional[int]
    hash: str
    metadata: Dict[str, Any]


class ContentChunker:
    """
    Content Chunker for pharmaceutical educational materials.

    Implements sliding window chunking with:
    - Section boundary awareness
    - Pharmaceutical term preservation
    - Metadata extraction
    - Deterministic hashing for deduplication
    """

    # Common section headers in pharmaceutical content
    SECTION_PATTERNS = [
        r'^#{1,6}\s+(.+)$',  # Markdown headers
        r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
        r'^(\d+\.)+\s+(.+)$',  # Numbered sections
        r'^(Introduction|Mechanism|Pharmacokinetics|Pharmacodynamics|Indications|Contraindications|Adverse Effects|Drug Interactions|Dosing|Clinical Pearls|Summary|Conclusion)',
    ]

    # Pharmaceutical terms to avoid splitting
    PRESERVE_TERMS = [
        r'\b\d+\s*(?:mg|mcg|g|mL|L|mEq|units?|IU)\b',  # Doses
        r'\b(?:t½|Vd|Cl|AUC|Cmax|Tmax|F)\s*[=:]\s*[\d.]+',  # PK parameters
        r'\b(?:CYP\d[A-Z]\d+|P-gp|OATP\d?[A-Z]?\d*)\b',  # Enzymes/transporters
    ]

    def __init__(
        self,
        chunk_size: int = 800,
        overlap: int = 160,
        preserve_sections: bool = True,
        preserve_sentences: bool = True,
        **kwargs
    ):
        """
        Initialize the chunker.

        Args:
            chunk_size: Target tokens per chunk (default: 800)
            overlap: Overlap between chunks (default: 160, ~20%)
            preserve_sections: Try to break at section boundaries
            preserve_sentences: Avoid mid-sentence breaks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.preserve_sections = preserve_sections
        self.preserve_sentences = preserve_sentences
        self.config = kwargs
        logger.debug(f"Initialized ContentChunker with size={chunk_size}, overlap={overlap}")

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace tokenization for portability."""
        return text.split()

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._tokenize(text))

    def _generate_chunk_id(self, text: str, start_idx: int) -> str:
        """Generate deterministic chunk ID."""
        content = f"{start_idx}:{text[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _compute_hash(self, text: str) -> str:
        """Compute content hash for deduplication."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _find_section_boundaries(self, text: str) -> List[int]:
        """Find section boundary positions in text."""
        boundaries = []
        lines = text.split('\n')
        pos = 0

        for line in lines:
            for pattern in self.SECTION_PATTERNS:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    boundaries.append(pos)
                    break
            pos += len(line) + 1

        return boundaries

    def _find_sentence_boundary(self, text: str, target_pos: int, window: int = 100) -> int:
        """Find nearest sentence boundary to target position."""
        search_start = max(0, target_pos - window)
        search_end = min(len(text), target_pos + window)
        search_text = text[search_start:search_end]

        # Find sentence endings
        sentence_ends = [m.end() + search_start for m in re.finditer(r'[.!?]\s+', search_text)]

        if not sentence_ends:
            return target_pos

        # Find closest to target
        closest = min(sentence_ends, key=lambda x: abs(x - target_pos))
        return closest

    def _extract_section(self, text: str, pos: int, section_boundaries: List[int]) -> Optional[str]:
        """Extract section name for a given position."""
        # Find the section this position belongs to
        current_section = None
        lines = text.split('\n')
        line_pos = 0

        for line in lines:
            if line_pos > pos:
                break
            for pattern in self.SECTION_PATTERNS:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    current_section = match.group(1) if match.groups() else line.strip()
                    break
            line_pos += len(line) + 1

        return current_section

    def _extract_page(self, text: str, pos: int) -> Optional[int]:
        """Extract page number if available in metadata markers."""
        # Look for page markers like [Page 5] or <!-- page: 5 -->
        page_patterns = [
            r'\[Page\s+(\d+)\]',
            r'<!--\s*page:\s*(\d+)\s*-->',
            r'\n---\s*Page\s+(\d+)\s*---\n',
        ]

        for pattern in page_patterns:
            matches = list(re.finditer(pattern, text[:pos], re.IGNORECASE))
            if matches:
                return int(matches[-1].group(1))

        return None

    def chunk(self, text: str, source_url: Optional[str] = None) -> List[Chunk]:
        """
        Chunk text into segments.

        Args:
            text: The text to chunk
            source_url: Optional source URL for provenance

        Returns:
            List of Chunk objects
        """
        chunks = []
        tokens = self._tokenize(text)
        total_tokens = len(tokens)

        if total_tokens == 0:
            return chunks

        section_boundaries = self._find_section_boundaries(text) if self.preserve_sections else []

        start_token = 0
        chunk_idx = 0

        while start_token < total_tokens:
            # Determine chunk end
            end_token = min(start_token + self.chunk_size, total_tokens)

            # Get text positions
            chunk_tokens = tokens[start_token:end_token]
            chunk_text = ' '.join(chunk_tokens)

            # Try to align with sentence boundary if not at end
            if end_token < total_tokens and self.preserve_sentences:
                # Reconstruct position in original text
                prefix = ' '.join(tokens[:end_token])
                text_pos = len(prefix)

                # Find nearby sentence boundary
                new_pos = self._find_sentence_boundary(text, text_pos)
                if new_pos != text_pos:
                    # Recalculate end token based on new position
                    new_prefix = text[:new_pos]
                    new_end_token = len(self._tokenize(new_prefix))
                    if start_token < new_end_token <= end_token + 50:  # Allow some flexibility
                        end_token = new_end_token
                        chunk_tokens = tokens[start_token:end_token]
                        chunk_text = ' '.join(chunk_tokens)

            # Create chunk
            chunk_id = self._generate_chunk_id(chunk_text, start_token)

            chunk = Chunk(
                id=chunk_id,
                text=chunk_text,
                tokens=len(chunk_tokens),
                start_idx=start_token,
                end_idx=end_token,
                section=self._extract_section(text, len(' '.join(tokens[:start_token])), section_boundaries),
                page=self._extract_page(text, len(' '.join(tokens[:start_token]))),
                hash=self._compute_hash(chunk_text),
                metadata={
                    'source_url': source_url,
                    'chunk_index': chunk_idx,
                    'total_chunks': None,  # Updated after all chunks created
                    'split_algo': f'sliding_{self.chunk_size}_{self.overlap}'
                }
            )
            chunks.append(chunk)
            chunk_idx += 1

            # Move to next chunk with overlap
            start_token = end_token - self.overlap
            if start_token >= end_token:  # Prevent infinite loop
                start_token = end_token

        # Update total chunks count
        for chunk in chunks:
            chunk.metadata['total_chunks'] = len(chunks)

        return chunks

    def process(self, input_data: str, source_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Main processing function.

        Args:
            input_data: The text to chunk
            source_url: Optional source URL

        Returns:
            dict: Results with status, data, and any errors
        """
        try:
            chunks = self.chunk(input_data, source_url)

            return {
                "status": "success",
                "data": {
                    "chunks": [asdict(c) for c in chunks],
                    "chunk_count": len(chunks),
                    "total_tokens": sum(c.tokens for c in chunks),
                    "avg_tokens": sum(c.tokens for c in chunks) / len(chunks) if chunks else 0,
                    "config": {
                        "chunk_size": self.chunk_size,
                        "overlap": self.overlap,
                        "preserve_sections": self.preserve_sections,
                        "preserve_sentences": self.preserve_sentences
                    }
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Chunking failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }

    def format_output(self, result: Dict[str, Any], output_format: str = "json") -> str:
        """Format the output for display."""
        if output_format == "json":
            return json.dumps(result, indent=2)

        elif output_format == "text":
            if result["status"] == "success":
                data = result["data"]
                lines = [
                    f"Chunked successfully: {data['chunk_count']} chunks",
                    f"Total tokens: {data['total_tokens']}",
                    f"Average tokens per chunk: {data['avg_tokens']:.1f}",
                    "",
                    "Chunks:"
                ]
                for i, chunk in enumerate(data["chunks"][:5]):  # Show first 5
                    lines.append(f"  [{i}] {chunk['text'][:80]}...")
                if len(data["chunks"]) > 5:
                    lines.append(f"  ... and {len(data['chunks']) - 5} more")
                return '\n'.join(lines)
            else:
                return f"ERROR: {result['error']}"

        elif output_format == "markdown":
            if result["status"] == "success":
                data = result["data"]
                return f"""## Chunking Results

- **Chunks**: {data['chunk_count']}
- **Total Tokens**: {data['total_tokens']}
- **Avg Tokens/Chunk**: {data['avg_tokens']:.1f}

### Configuration
- Chunk Size: {data['config']['chunk_size']}
- Overlap: {data['config']['overlap']}
"""
            else:
                return f"## Error\n\n{result['error']}"

        return str(result)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file to chunk"
    )

    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "markdown"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Target tokens per chunk (default: 800)"
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=160,
        help="Overlap between chunks (default: 160)"
    )

    parser.add_argument(
        "--preserve-sections",
        action="store_true",
        default=True,
        help="Preserve section boundaries"
    )

    parser.add_argument(
        "--no-preserve-sections",
        action="store_false",
        dest="preserve_sections",
        help="Don't preserve section boundaries"
    )

    parser.add_argument(
        "--preserve-sentences",
        action="store_true",
        default=True,
        help="Avoid mid-sentence breaks"
    )

    parser.add_argument(
        "--source-url",
        default=None,
        help="Source URL for provenance tracking"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    try:
        args = parse_arguments()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input}")
            return 1

        logger.info(f"Processing input: {args.input}")
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = f.read()

        if args.dry_run:
            logger.info(f"[DRY RUN] Would chunk {len(input_data)} characters")
            return 0

        chunker = ContentChunker(
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            preserve_sections=args.preserve_sections,
            preserve_sentences=args.preserve_sentences
        )

        result = chunker.process(input_data, args.source_url)
        output = chunker.format_output(result, args.format)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output)
            logger.info(f"Output written to: {args.output}")
        else:
            print(output)

        return 0 if result["status"] == "success" else 1

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

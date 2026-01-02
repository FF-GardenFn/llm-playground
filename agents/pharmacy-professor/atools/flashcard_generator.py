#!/usr/bin/env python3
"""
Flashcard Generator - Spaced Repetition Tool

Purpose: Create Anki-style flashcards for pharmaceutical education.
Usage: python flashcard_generator.py --concepts concepts.json --output flashcards.json

This tool is part of the pharmacy-professor agent's toolkit.
It generates flashcards optimized for spaced repetition learning.

Examples:
    python flashcard_generator.py --concepts concepts.json --output flashcards.json
    python flashcard_generator.py --concepts concepts.json --type cloze --output flashcards.json
    python flashcard_generator.py --concepts concepts.json --tags "topic,difficulty" --reversible
"""

import argparse
import sys
import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CardType(Enum):
    BASIC = "basic"
    CLOZE = "cloze"
    IMAGE_OCCLUSION = "image_occlusion"
    REVERSIBLE = "reversible"


@dataclass
class Flashcard:
    """Represents a single flashcard."""
    id: str
    type: str
    front: str
    back: str
    tags: List[str] = field(default_factory=list)
    note: Optional[str] = None
    source: Optional[str] = None
    difficulty: str = "medium"


class FlashcardGenerator:
    """
    Flashcard Generator for pharmaceutical education.

    Creates cards optimized for:
    - Active recall testing
    - Spaced repetition schedules
    - Multi-format learning (basic, cloze, reversible)
    - Drug-specific content
    """

    # Card templates for pharmaceutical content
    CARD_TEMPLATES = {
        "drug_class": {
            "front": "What drug class does {drug_name} belong to?",
            "back": "{drug_class}"
        },
        "mechanism": {
            "front": "What is the mechanism of action of {drug_name}?",
            "back": "{mechanism}"
        },
        "indication": {
            "front": "What is the primary indication for {drug_name}?",
            "back": "{indication}"
        },
        "adverse_effect": {
            "front": "What is a major adverse effect of {drug_name}?",
            "back": "{adverse_effect}"
        },
        "dosing": {
            "front": "What is the typical dose of {drug_name}?",
            "back": "{dose}"
        },
        "interaction": {
            "front": "What is a significant drug interaction with {drug_name}?",
            "back": "{interaction}"
        },
        "contraindication": {
            "front": "What is a contraindication for {drug_name}?",
            "back": "{contraindication}"
        },
        "pk_parameter": {
            "front": "What is the {parameter} of {drug_name}?",
            "back": "{value}"
        }
    }

    # Cloze templates
    CLOZE_TEMPLATES = [
        "{drug_name} works by {{c1::{mechanism}}}.",
        "The primary indication for {drug_name} is {{c1::{indication}}}.",
        "{drug_name} belongs to the {{c1::{drug_class}}} drug class.",
        "A major adverse effect of {drug_name} is {{c1::{adverse_effect}}}.",
        "The half-life of {drug_name} is approximately {{c1::{half_life}}}.",
    ]

    def __init__(
        self,
        card_types: List[str] = None,
        include_tags: bool = True,
        include_sources: bool = True,
        reversible: bool = False,
        max_length: int = 500,
        **kwargs
    ):
        """
        Initialize the flashcard generator.

        Args:
            card_types: Types of cards to generate
            include_tags: Add organizational tags
            include_sources: Include source citations
            reversible: Create reversible cards
            max_length: Maximum character length per card
        """
        self.card_types = card_types or ["basic"]
        self.include_tags = include_tags
        self.include_sources = include_sources
        self.reversible = reversible
        self.max_length = max_length
        self.config = kwargs
        self.card_counter = 0
        logger.debug(f"Initialized FlashcardGenerator with types={card_types}")

    def _generate_id(self) -> str:
        """Generate unique card ID."""
        self.card_counter += 1
        return f"FC{self.card_counter:04d}"

    def _truncate(self, text: str, max_len: int = None) -> str:
        """Truncate text to maximum length."""
        max_len = max_len or self.max_length
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + "..."

    def _generate_tags(self, concept: Dict[str, Any]) -> List[str]:
        """Generate tags for a card."""
        tags = []

        if concept.get("category"):
            tags.append(f"category::{concept['category']}")

        if concept.get("drug_class"):
            tags.append(f"class::{concept['drug_class']}")

        if concept.get("difficulty"):
            tags.append(f"difficulty::{concept['difficulty']}")
        else:
            tags.append("difficulty::medium")

        if concept.get("exam_relevant"):
            tags.append("exam")

        return tags

    def _generate_basic_cards(self, concept: Dict[str, Any]) -> List[Flashcard]:
        """Generate basic front/back cards."""
        cards = []
        drug_name = concept.get("name", "Unknown Drug")

        # Generate cards for each available attribute
        if concept.get("mechanism"):
            cards.append(Flashcard(
                id=self._generate_id(),
                type="basic",
                front=f"What is the mechanism of action of {drug_name}?",
                back=self._truncate(concept["mechanism"]),
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty=concept.get("difficulty", "medium")
            ))

        if concept.get("drug_class"):
            cards.append(Flashcard(
                id=self._generate_id(),
                type="basic",
                front=f"What drug class does {drug_name} belong to?",
                back=concept["drug_class"],
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty="easy"
            ))

        if concept.get("indication"):
            cards.append(Flashcard(
                id=self._generate_id(),
                type="basic",
                front=f"What is the primary indication for {drug_name}?",
                back=self._truncate(concept["indication"]),
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty=concept.get("difficulty", "medium")
            ))

        if concept.get("adverse_effects"):
            effects = concept["adverse_effects"]
            if isinstance(effects, list):
                effects = ", ".join(effects[:5])
            cards.append(Flashcard(
                id=self._generate_id(),
                type="basic",
                front=f"What are the major adverse effects of {drug_name}?",
                back=self._truncate(effects),
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty="medium"
            ))

        if concept.get("contraindications"):
            contras = concept["contraindications"]
            if isinstance(contras, list):
                contras = ", ".join(contras[:3])
            cards.append(Flashcard(
                id=self._generate_id(),
                type="basic",
                front=f"What are contraindications for {drug_name}?",
                back=self._truncate(contras),
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty="medium"
            ))

        # If no specific attributes, create a general card
        if not cards:
            if concept.get("definition"):
                cards.append(Flashcard(
                    id=self._generate_id(),
                    type="basic",
                    front=f"What is {drug_name}?",
                    back=self._truncate(concept["definition"]),
                    tags=self._generate_tags(concept) if self.include_tags else [],
                    source=concept.get("source"),
                    difficulty="easy"
                ))

        return cards

    def _generate_cloze_cards(self, concept: Dict[str, Any]) -> List[Flashcard]:
        """Generate cloze deletion cards."""
        cards = []
        drug_name = concept.get("name", "Unknown Drug")

        if concept.get("mechanism"):
            cloze_text = f"{drug_name} works by {{{{c1::{concept['mechanism']}}}}}."
            cards.append(Flashcard(
                id=self._generate_id(),
                type="cloze",
                front=cloze_text.replace("{{c1::", "[...").replace("}}", "...]"),
                back=cloze_text,
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty=concept.get("difficulty", "medium")
            ))

        if concept.get("drug_class"):
            cloze_text = f"{drug_name} belongs to the {{{{c1::{concept['drug_class']}}}}} drug class."
            cards.append(Flashcard(
                id=self._generate_id(),
                type="cloze",
                front=cloze_text.replace("{{c1::", "[...").replace("}}", "...]"),
                back=cloze_text,
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty="easy"
            ))

        if concept.get("indication"):
            cloze_text = f"The primary indication for {drug_name} is {{{{c1::{concept['indication']}}}}}."
            cards.append(Flashcard(
                id=self._generate_id(),
                type="cloze",
                front=cloze_text.replace("{{c1::", "[...").replace("}}", "...]"),
                back=cloze_text,
                tags=self._generate_tags(concept) if self.include_tags else [],
                source=concept.get("source"),
                difficulty=concept.get("difficulty", "medium")
            ))

        return cards

    def _generate_reversible_cards(self, concept: Dict[str, Any]) -> List[Flashcard]:
        """Generate reversible cards (both directions)."""
        cards = []
        drug_name = concept.get("name", "Unknown Drug")

        if concept.get("mechanism"):
            # Forward
            cards.append(Flashcard(
                id=self._generate_id(),
                type="reversible",
                front=f"What is the mechanism of action of {drug_name}?",
                back=self._truncate(concept["mechanism"]),
                tags=self._generate_tags(concept) + ["direction::forward"] if self.include_tags else [],
                source=concept.get("source"),
                difficulty=concept.get("difficulty", "medium")
            ))
            # Reverse
            cards.append(Flashcard(
                id=self._generate_id(),
                type="reversible",
                front=f"Which drug works by {self._truncate(concept['mechanism'], 100)}?",
                back=drug_name,
                tags=self._generate_tags(concept) + ["direction::reverse"] if self.include_tags else [],
                source=concept.get("source"),
                difficulty="hard"
            ))

        if concept.get("drug_class"):
            # Forward
            cards.append(Flashcard(
                id=self._generate_id(),
                type="reversible",
                front=f"What drug class does {drug_name} belong to?",
                back=concept["drug_class"],
                tags=self._generate_tags(concept) + ["direction::forward"] if self.include_tags else [],
                source=concept.get("source"),
                difficulty="easy"
            ))
            # Reverse
            cards.append(Flashcard(
                id=self._generate_id(),
                type="reversible",
                front=f"Name a drug in the {concept['drug_class']} class.",
                back=drug_name,
                tags=self._generate_tags(concept) + ["direction::reverse"] if self.include_tags else [],
                source=concept.get("source"),
                difficulty="medium"
            ))

        return cards

    def generate_cards(self, concepts: List[Dict[str, Any]]) -> List[Flashcard]:
        """
        Generate flashcards from concepts.

        Args:
            concepts: List of concept dictionaries

        Returns:
            List of Flashcard objects
        """
        all_cards = []

        for concept in concepts:
            if "basic" in self.card_types:
                all_cards.extend(self._generate_basic_cards(concept))

            if "cloze" in self.card_types:
                all_cards.extend(self._generate_cloze_cards(concept))

            if self.reversible or "reversible" in self.card_types:
                all_cards.extend(self._generate_reversible_cards(concept))

        return all_cards

    def process(self, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main processing function.

        Args:
            concepts: List of concept dictionaries

        Returns:
            dict: Results with status, data, and any errors
        """
        try:
            cards = self.generate_cards(concepts)

            # Calculate statistics
            type_dist = {}
            difficulty_dist = {}
            for card in cards:
                type_dist[card.type] = type_dist.get(card.type, 0) + 1
                difficulty_dist[card.difficulty] = difficulty_dist.get(card.difficulty, 0) + 1

            return {
                "status": "success",
                "data": {
                    "cards": [asdict(c) for c in cards],
                    "card_count": len(cards),
                    "type_distribution": type_dist,
                    "difficulty_distribution": difficulty_dist,
                    "estimated_study_time_minutes": len(cards) * 0.5,
                    "config": {
                        "card_types": self.card_types,
                        "include_tags": self.include_tags,
                        "reversible": self.reversible
                    }
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Flashcard generation failed: {str(e)}", exc_info=True)
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
                    f"Generated {data['card_count']} flashcards",
                    f"Type distribution: {data['type_distribution']}",
                    f"Difficulty distribution: {data['difficulty_distribution']}",
                    f"Estimated study time: {data['estimated_study_time_minutes']:.0f} minutes",
                    ""
                ]
                for i, card in enumerate(data["cards"][:3]):
                    lines.append(f"Card {i+1}:")
                    lines.append(f"  Front: {card['front'][:50]}...")
                    lines.append(f"  Back: {card['back'][:50]}...")
                if len(data["cards"]) > 3:
                    lines.append(f"... and {len(data['cards']) - 3} more cards")
                return '\n'.join(lines)
            else:
                return f"ERROR: {result['error']}"

        elif output_format == "markdown":
            if result["status"] == "success":
                data = result["data"]
                md = f"# Flashcard Deck\n\n"
                md += f"**Total Cards**: {data['card_count']}\n\n"
                md += f"**Estimated Study Time**: {data['estimated_study_time_minutes']:.0f} minutes\n\n"

                for i, card in enumerate(data["cards"]):
                    md += f"## Card {i+1}\n\n"
                    md += f"**Front**: {card['front']}\n\n"
                    md += f"**Back**: {card['back']}\n\n"
                    if card.get('tags'):
                        md += f"*Tags*: {', '.join(card['tags'])}\n\n"
                    md += "---\n\n"
                return md
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
        "--concepts", "-c",
        required=True,
        help="Input concepts JSON file"
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
        "--type", "-t",
        default="basic",
        help="Card type (basic, cloze, reversible)"
    )

    parser.add_argument(
        "--types",
        default=None,
        help="Comma-separated card types"
    )

    parser.add_argument(
        "--reversible", "-r",
        action="store_true",
        help="Generate reversible cards"
    )

    parser.add_argument(
        "--tags",
        action="store_true",
        default=True,
        help="Include tags (default: true)"
    )

    parser.add_argument(
        "--no-tags",
        action="store_false",
        dest="tags",
        help="Exclude tags"
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=500,
        help="Maximum text length per card (default: 500)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    try:
        args = parse_arguments()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        concepts_path = Path(args.concepts)
        if not concepts_path.exists():
            logger.error(f"Concepts file not found: {args.concepts}")
            return 1

        with open(concepts_path, 'r') as f:
            concepts_data = json.load(f)

        # Extract concepts list
        if isinstance(concepts_data, dict) and "data" in concepts_data:
            concepts = concepts_data["data"].get("concepts", [])
        elif isinstance(concepts_data, list):
            concepts = concepts_data
        else:
            concepts = [concepts_data]

        if not concepts:
            logger.error("No concepts found in input file")
            return 1

        # Determine card types
        if args.types:
            card_types = args.types.split(",")
        else:
            card_types = [args.type]

        generator = FlashcardGenerator(
            card_types=card_types,
            include_tags=args.tags,
            reversible=args.reversible,
            max_length=args.max_length
        )

        result = generator.process(concepts)
        output = generator.format_output(result, args.format)

        if args.output:
            Path(args.output).write_text(output)
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

#!/usr/bin/env python3
"""
Quiz Generator - Educational Assessment Tool

Purpose: Generate quiz questions from extracted pharmaceutical concepts.
Usage: python quiz_generator.py --concepts concepts.json --type mcq --count 20

This tool is part of the pharmacy-professor agent's toolkit.
It generates various question types with Bloom's taxonomy alignment.

Examples:
    python quiz_generator.py --concepts concepts.json --type mcq --count 20
    python quiz_generator.py --concepts concepts.json --types mcq,tf --count 30 --explanations
    python quiz_generator.py --concepts concepts.json --type mcq --count 15 --vignettes
"""

import argparse
import sys
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuestionType(Enum):
    MCQ = "mcq"
    TRUE_FALSE = "tf"
    MATCHING = "matching"
    FILL_BLANK = "fill_blank"


class BloomLevel(Enum):
    REMEMBER = 1
    UNDERSTAND = 2
    APPLY = 3
    ANALYZE = 4
    EVALUATE = 5
    CREATE = 6


@dataclass
class Question:
    """Represents a quiz question."""
    id: str
    type: str
    stem: str
    options: List[str]
    correct_answer: Any
    explanation: Optional[str]
    bloom_level: str
    concept: str
    tags: List[str] = field(default_factory=list)
    vignette: Optional[str] = None


class QuizGenerator:
    """
    Quiz Generator for pharmaceutical education.

    Generates questions with:
    - Multiple question types (MCQ, T/F, Matching)
    - Bloom's taxonomy alignment
    - Clinical vignette integration
    - Distractor generation
    - Detailed explanations
    """

    # Bloom's level verb stems for question generation
    BLOOM_VERBS = {
        BloomLevel.REMEMBER: ["Define", "List", "Name", "State", "Identify", "Recall"],
        BloomLevel.UNDERSTAND: ["Explain", "Describe", "Summarize", "Compare", "Contrast"],
        BloomLevel.APPLY: ["Calculate", "Demonstrate", "Apply", "Use", "Solve"],
        BloomLevel.ANALYZE: ["Analyze", "Differentiate", "Examine", "Distinguish"],
        BloomLevel.EVALUATE: ["Evaluate", "Justify", "Assess", "Critique", "Recommend"],
        BloomLevel.CREATE: ["Design", "Formulate", "Develop", "Create", "Propose"],
    }

    # Common distractor patterns for pharmaceutical MCQs
    DISTRACTOR_PATTERNS = {
        "mechanism": ["competitive inhibitor", "non-competitive inhibitor", "irreversible antagonist", "partial agonist", "allosteric modulator"],
        "dose": ["higher dose", "lower dose", "same dose", "loading dose", "maintenance dose"],
        "timing": ["before meals", "after meals", "with meals", "at bedtime", "in the morning"],
        "adverse_effect": ["nausea", "headache", "dizziness", "fatigue", "rash"],
    }

    def __init__(
        self,
        include_explanations: bool = True,
        include_vignettes: bool = False,
        difficulty_distribution: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """
        Initialize the quiz generator.

        Args:
            include_explanations: Add explanations to answers
            include_vignettes: Add clinical vignettes
            difficulty_distribution: Target distribution {bloom_level: percentage}
        """
        self.include_explanations = include_explanations
        self.include_vignettes = include_vignettes
        self.difficulty_distribution = difficulty_distribution or {
            "remember": 0.2,
            "understand": 0.3,
            "apply": 0.3,
            "analyze": 0.2
        }
        self.config = kwargs
        self.question_counter = 0
        logger.debug(f"Initialized QuizGenerator with explanations={include_explanations}")

    def _generate_id(self) -> str:
        """Generate unique question ID."""
        self.question_counter += 1
        return f"Q{self.question_counter:04d}"

    def _select_bloom_level(self) -> BloomLevel:
        """Select Bloom's level based on distribution."""
        levels = list(self.difficulty_distribution.keys())
        weights = list(self.difficulty_distribution.values())

        level_map = {
            "remember": BloomLevel.REMEMBER,
            "understand": BloomLevel.UNDERSTAND,
            "apply": BloomLevel.APPLY,
            "analyze": BloomLevel.ANALYZE,
            "evaluate": BloomLevel.EVALUATE,
            "create": BloomLevel.CREATE
        }

        selected = random.choices(levels, weights=weights, k=1)[0]
        return level_map.get(selected, BloomLevel.UNDERSTAND)

    def _generate_stem(self, concept: Dict[str, Any], bloom_level: BloomLevel, q_type: QuestionType) -> str:
        """Generate question stem based on concept and Bloom's level."""
        concept_name = concept.get("name", "this concept")
        category = concept.get("category", "pharmacology")

        verbs = self.BLOOM_VERBS[bloom_level]
        verb = random.choice(verbs)

        if q_type == QuestionType.MCQ:
            templates = [
                f"Which of the following best describes {concept_name}?",
                f"{verb} the mechanism of action of {concept_name}.",
                f"What is the primary characteristic of {concept_name}?",
                f"Regarding {concept_name}, which statement is correct?",
            ]
        elif q_type == QuestionType.TRUE_FALSE:
            templates = [
                f"{concept_name} is classified as {category}.",
                f"The primary mechanism of {concept_name} involves receptor binding.",
            ]
        else:
            templates = [f"Question about {concept_name}"]

        return random.choice(templates)

    def _generate_distractors(self, concept: Dict[str, Any], correct: str, count: int = 3) -> List[str]:
        """Generate plausible distractor options."""
        distractors = []
        category = concept.get("category", "mechanism")

        # Use pattern-based distractors
        if category in self.DISTRACTOR_PATTERNS:
            available = [d for d in self.DISTRACTOR_PATTERNS[category] if d != correct]
            distractors.extend(random.sample(available, min(count, len(available))))

        # Generate generic distractors if needed
        generic = [
            f"Alternative mechanism for {concept.get('name', 'drug')}",
            "None of the above",
            "All of the above",
            f"Related to {concept.get('name', 'drug')} metabolism",
        ]

        while len(distractors) < count:
            available = [d for d in generic if d not in distractors]
            if available:
                distractors.append(random.choice(available))
            else:
                break

        return distractors[:count]

    def _generate_explanation(self, concept: Dict[str, Any], correct_answer: str) -> str:
        """Generate explanation for the correct answer."""
        concept_name = concept.get("name", "This concept")
        mechanism = concept.get("mechanism", "the described mechanism")

        explanation = f"{concept_name} works through {mechanism}. "
        explanation += f"The correct answer is '{correct_answer}' because it accurately describes the primary characteristic. "
        explanation += "The other options are incorrect because they describe different mechanisms or properties."

        return explanation

    def _generate_vignette(self, concept: Dict[str, Any]) -> str:
        """Generate clinical vignette for the question."""
        age = random.randint(25, 75)
        gender = random.choice(["male", "female"])

        vignette = f"A {age}-year-old {gender} patient presents to the pharmacy with a prescription for "
        vignette += f"{concept.get('name', 'a new medication')}. "
        vignette += "The patient asks about this medication."

        return vignette

    def generate_mcq(self, concept: Dict[str, Any]) -> Question:
        """Generate a multiple choice question."""
        bloom_level = self._select_bloom_level()
        stem = self._generate_stem(concept, bloom_level, QuestionType.MCQ)

        # Generate correct answer
        correct = concept.get("primary_characteristic", concept.get("name", "Correct answer"))

        # Generate distractors
        distractors = self._generate_distractors(concept, correct)

        # Combine and shuffle options
        options = [correct] + distractors
        random.shuffle(options)
        correct_index = options.index(correct)

        # Add option labels
        labeled_options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)]

        vignette = self._generate_vignette(concept) if self.include_vignettes else None
        explanation = self._generate_explanation(concept, correct) if self.include_explanations else None

        return Question(
            id=self._generate_id(),
            type="mcq",
            stem=stem,
            options=labeled_options,
            correct_answer=chr(65 + correct_index),
            explanation=explanation,
            bloom_level=bloom_level.name.lower(),
            concept=concept.get("name", "unknown"),
            tags=concept.get("tags", []),
            vignette=vignette
        )

    def generate_true_false(self, concept: Dict[str, Any]) -> Question:
        """Generate a true/false question."""
        bloom_level = self._select_bloom_level()

        # Decide if statement will be true or false
        is_true = random.choice([True, False])

        concept_name = concept.get("name", "This drug")
        category = concept.get("category", "a therapeutic agent")

        if is_true:
            stem = f"{concept_name} is classified as {category}."
        else:
            # Create false statement
            false_category = random.choice(["an antibiotic", "an antihypertensive", "an analgesic"])
            if false_category != category:
                stem = f"{concept_name} is classified as {false_category}."
            else:
                stem = f"{concept_name} has no known drug interactions."

        explanation = None
        if self.include_explanations:
            if is_true:
                explanation = f"This statement is TRUE. {concept_name} is indeed classified as {category}."
            else:
                explanation = f"This statement is FALSE. {concept_name} is actually classified as {category}."

        return Question(
            id=self._generate_id(),
            type="tf",
            stem=stem,
            options=["True", "False"],
            correct_answer="True" if is_true else "False",
            explanation=explanation,
            bloom_level=bloom_level.name.lower(),
            concept=concept.get("name", "unknown"),
            tags=concept.get("tags", [])
        )

    def generate_matching(self, concepts: List[Dict[str, Any]]) -> Question:
        """Generate a matching question from multiple concepts."""
        if len(concepts) < 2:
            # Fall back to MCQ if not enough concepts
            return self.generate_mcq(concepts[0])

        # Use up to 5 concepts for matching
        selected = concepts[:5] if len(concepts) > 5 else concepts

        # Create pairs
        terms = [c.get("name", f"Term {i}") for i, c in enumerate(selected)]
        definitions = [c.get("definition", c.get("mechanism", f"Definition {i}")) for i, c in enumerate(selected)]

        # Shuffle definitions for the question
        shuffled_defs = definitions.copy()
        random.shuffle(shuffled_defs)

        stem = "Match each drug/concept with its correct description:"
        options = [f"{i+1}. {term} → {chr(65+i)}. {shuffled_defs[i]}" for i, term in enumerate(terms)]

        # Create answer key
        correct_mapping = {term: chr(65 + shuffled_defs.index(definitions[i])) for i, term in enumerate(terms)}

        return Question(
            id=self._generate_id(),
            type="matching",
            stem=stem,
            options=options,
            correct_answer=correct_mapping,
            explanation="Match based on mechanism of action or primary indication." if self.include_explanations else None,
            bloom_level="understand",
            concept="multiple",
            tags=["matching", "recall"]
        )

    def generate_questions(
        self,
        concepts: List[Dict[str, Any]],
        question_types: List[str],
        count: int
    ) -> List[Question]:
        """
        Generate a set of questions from concepts.

        Args:
            concepts: List of concept dictionaries
            question_types: Types of questions to generate
            count: Number of questions to generate

        Returns:
            List of Question objects
        """
        questions = []
        type_map = {
            "mcq": self.generate_mcq,
            "tf": self.generate_true_false,
        }

        # Distribute questions across types
        per_type = count // len(question_types)
        remainder = count % len(question_types)

        concept_index = 0

        for q_type in question_types:
            type_count = per_type + (1 if remainder > 0 else 0)
            remainder -= 1

            if q_type == "matching" and len(concepts) >= 2:
                # Generate matching questions
                for _ in range(min(type_count, len(concepts) // 3)):
                    start = concept_index % len(concepts)
                    end = min(start + 5, len(concepts))
                    questions.append(self.generate_matching(concepts[start:end]))
                    concept_index += 5
            elif q_type in type_map:
                generator = type_map[q_type]
                for _ in range(type_count):
                    concept = concepts[concept_index % len(concepts)]
                    questions.append(generator(concept))
                    concept_index += 1

        return questions

    def process(self, concepts: List[Dict[str, Any]], question_types: List[str], count: int) -> Dict[str, Any]:
        """
        Main processing function.

        Args:
            concepts: List of concept dictionaries
            question_types: Types of questions to generate
            count: Number of questions to generate

        Returns:
            dict: Results with status, data, and any errors
        """
        try:
            questions = self.generate_questions(concepts, question_types, count)

            # Calculate distribution
            bloom_dist = {}
            type_dist = {}
            for q in questions:
                bloom_dist[q.bloom_level] = bloom_dist.get(q.bloom_level, 0) + 1
                type_dist[q.type] = type_dist.get(q.type, 0) + 1

            return {
                "status": "success",
                "data": {
                    "questions": [asdict(q) for q in questions],
                    "question_count": len(questions),
                    "bloom_distribution": bloom_dist,
                    "type_distribution": type_dist,
                    "config": {
                        "include_explanations": self.include_explanations,
                        "include_vignettes": self.include_vignettes,
                        "difficulty_distribution": self.difficulty_distribution
                    }
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Question generation failed: {str(e)}", exc_info=True)
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
                    f"Generated {data['question_count']} questions",
                    f"Bloom's distribution: {data['bloom_distribution']}",
                    f"Type distribution: {data['type_distribution']}",
                    ""
                ]
                for i, q in enumerate(data["questions"][:3]):
                    lines.append(f"Q{i+1}: {q['stem'][:60]}...")
                if len(data["questions"]) > 3:
                    lines.append(f"... and {len(data['questions']) - 3} more questions")
                return '\n'.join(lines)
            else:
                return f"ERROR: {result['error']}"

        elif output_format == "markdown":
            if result["status"] == "success":
                data = result["data"]
                md = f"# Quiz\n\n**Questions Generated**: {data['question_count']}\n\n"
                for i, q in enumerate(data["questions"]):
                    md += f"## Question {i+1}\n\n"
                    if q.get("vignette"):
                        md += f"*{q['vignette']}*\n\n"
                    md += f"{q['stem']}\n\n"
                    for opt in q["options"]:
                        md += f"- {opt}\n"
                    md += f"\n**Answer**: {q['correct_answer']}\n\n"
                    if q.get("explanation"):
                        md += f"**Explanation**: {q['explanation']}\n\n"
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
        default="mcq",
        help="Question type (mcq, tf, matching)"
    )

    parser.add_argument(
        "--types",
        default=None,
        help="Comma-separated question types (e.g., mcq,tf,matching)"
    )

    parser.add_argument(
        "--count", "-n",
        type=int,
        default=20,
        help="Number of questions to generate (default: 20)"
    )

    parser.add_argument(
        "--explanations",
        action="store_true",
        default=True,
        help="Include explanations (default: true)"
    )

    parser.add_argument(
        "--no-explanations",
        action="store_false",
        dest="explanations",
        help="Exclude explanations"
    )

    parser.add_argument(
        "--vignettes",
        action="store_true",
        default=False,
        help="Include clinical vignettes"
    )

    parser.add_argument(
        "--difficulty",
        default=None,
        help="Difficulty distribution (e.g., 'remember:20,understand:30,apply:30,analyze:20')"
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

        # Load concepts
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

        # Determine question types
        if args.types:
            question_types = args.types.split(",")
        else:
            question_types = [args.type]

        # Parse difficulty distribution
        difficulty = None
        if args.difficulty:
            difficulty = {}
            for part in args.difficulty.split(","):
                level, pct = part.split(":")
                difficulty[level.strip()] = float(pct) / 100

        generator = QuizGenerator(
            include_explanations=args.explanations,
            include_vignettes=args.vignettes,
            difficulty_distribution=difficulty
        )

        result = generator.process(concepts, question_types, args.count)
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

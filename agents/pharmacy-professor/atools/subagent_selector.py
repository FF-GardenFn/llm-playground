#!/usr/bin/env python3
"""
Subagent Selector - Specialist Matching Tool

Purpose: Match tasks to appropriate specialist subagents for the Pharmacy Professor.
Usage: python subagent_selector.py --task "Create PK quiz" --context context.json

This tool is part of the pharmacy-professor agent's toolkit.
It matches tasks to specialists using weighted confidence scoring.

Examples:
    python subagent_selector.py --task "Create flashcards for drug interactions"
    python subagent_selector.py --tasks tasks.json --output assignments.json
    python subagent_selector.py --task "Design clinical case study" --explain
"""

import argparse
import sys
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SubagentDefinition:
    """Definition of a specialist subagent."""
    name: str
    cognitive_model: str
    domain: str
    capabilities: List[str]
    output_types: List[str]
    keywords: List[str]


@dataclass
class Assignment:
    """Task to subagent assignment."""
    task: str
    specialist: str
    confidence: float
    rationale: Dict[str, str]
    anti_patterns: List[str]
    alternative: Optional[str] = None


class SubagentSelector:
    """
    Subagent Selector for pharmaceutical education tasks.

    Matches tasks to specialists using weighted scoring:
    - Domain fit: 50%
    - Cognitive process alignment: 30%
    - Output format match: 20%
    """

    # Available subagents for Pharmacy Professor
    SUBAGENTS = {
        "quiz-maker": SubagentDefinition(
            name="quiz-maker",
            cognitive_model="Assessment Item Writer",
            domain="assessment",
            capabilities=["MCQ generation", "distractor creation", "vignette writing", "explanation generation"],
            output_types=["quiz", "questions", "MCQ", "test", "exam items"],
            keywords=["quiz", "question", "MCQ", "test", "assessment", "exam", "true/false", "matching"]
        ),
        "flashcard-generator": SubagentDefinition(
            name="flashcard-generator",
            cognitive_model="Spaced Repetition Specialist",
            domain="memorization",
            capabilities=["basic cards", "cloze deletion", "reversible cards", "tagging"],
            output_types=["flashcard", "Anki", "deck", "cards"],
            keywords=["flashcard", "card", "Anki", "memorize", "recall", "spaced repetition"]
        ),
        "summarizer": SubagentDefinition(
            name="summarizer",
            cognitive_model="Knowledge Distiller",
            domain="content",
            capabilities=["hierarchical summaries", "key points", "comparison tables", "quick reference"],
            output_types=["summary", "study guide", "outline", "notes"],
            keywords=["summary", "summarize", "study guide", "notes", "outline", "overview", "key points"]
        ),
        "case-study-builder": SubagentDefinition(
            name="case-study-builder",
            cognitive_model="Clinical Scenario Designer",
            domain="clinical",
            capabilities=["patient cases", "progressive disclosure", "clinical reasoning", "teaching points"],
            output_types=["case study", "clinical scenario", "patient case"],
            keywords=["case", "clinical", "patient", "scenario", "vignette", "presentation"]
        ),
        "exam-designer": SubagentDefinition(
            name="exam-designer",
            cognitive_model="Examination Architect",
            domain="assessment",
            capabilities=["exam blueprinting", "topic coverage", "difficulty balance", "parallel forms"],
            output_types=["exam", "test", "assessment"],
            keywords=["exam", "test", "final", "midterm", "assessment", "blueprint"]
        ),
        "difficulty-calibrator": SubagentDefinition(
            name="difficulty-calibrator",
            cognitive_model="Bloom's Taxonomy Assessor",
            domain="assessment",
            capabilities=["level classification", "difficulty adjustment", "distribution analysis"],
            output_types=["calibrated questions", "difficulty report"],
            keywords=["difficulty", "Bloom", "calibrate", "level", "adjust", "distribution"]
        ),
        "pharmacokinetics-expert": SubagentDefinition(
            name="pharmacokinetics-expert",
            cognitive_model="ADME Specialist",
            domain="pharmacokinetics",
            capabilities=["PK/PD explanation", "dosing calculations", "patient factors"],
            output_types=["PK content", "calculations", "dosing problems"],
            keywords=["pharmacokinetics", "PK", "ADME", "absorption", "distribution", "metabolism", "excretion", "half-life", "clearance", "bioavailability", "dosing", "calculation"]
        ),
        "drug-interaction-checker": SubagentDefinition(
            name="drug-interaction-checker",
            cognitive_model="DDI Analyst",
            domain="interactions",
            capabilities=["interaction identification", "mechanism analysis", "clinical significance"],
            output_types=["interaction analysis", "DDI content"],
            keywords=["interaction", "DDI", "drug-drug", "CYP", "P-gp", "contraindication"]
        ),
        "curriculum-planner": SubagentDefinition(
            name="curriculum-planner",
            cognitive_model="Educational Architect",
            domain="curriculum",
            capabilities=["learning progressions", "topic sequencing", "competency alignment"],
            output_types=["curriculum", "syllabus", "learning path"],
            keywords=["curriculum", "syllabus", "course", "module", "learning path", "sequence", "progression"]
        ),
        "prerequisite-mapper": SubagentDefinition(
            name="prerequisite-mapper",
            cognitive_model="Dependency Analyst",
            domain="curriculum",
            capabilities=["prerequisite identification", "dependency graphs", "gap analysis"],
            output_types=["prerequisite map", "dependency graph"],
            keywords=["prerequisite", "dependency", "foundation", "prior knowledge", "gap"]
        )
    }

    # Anti-patterns to detect
    ANTI_PATTERNS = {
        "domain_mismatch": [
            ("pharmacokinetics-expert", ["interaction", "DDI"]),
            ("drug-interaction-checker", ["dosing", "calculation", "half-life"]),
            ("quiz-maker", ["curriculum", "syllabus"]),
            ("curriculum-planner", ["quiz", "flashcard"]),
        ],
        "role_confusion": [
            ("summarizer", ["quiz", "question", "exam"]),
            ("quiz-maker", ["summary", "study guide"]),
            ("flashcard-generator", ["exam", "test design"]),
        ]
    }

    def __init__(self, explain: bool = False, threshold: float = 0.7, **kwargs):
        """
        Initialize the selector.

        Args:
            explain: Include detailed explanations
            threshold: Minimum confidence threshold
        """
        self.explain = explain
        self.threshold = threshold
        self.config = kwargs
        logger.debug(f"Initialized SubagentSelector with threshold={threshold}")

    def _calculate_domain_score(self, task: str, subagent: SubagentDefinition) -> float:
        """Calculate domain fit score (0.0-1.0)."""
        task_lower = task.lower()
        score = 0.0

        # Check for keyword matches
        for keyword in subagent.keywords:
            if keyword.lower() in task_lower:
                score += 0.2

        # Check for output type matches
        for output_type in subagent.output_types:
            if output_type.lower() in task_lower:
                score += 0.15

        # Domain-specific boosts
        if subagent.domain in task_lower:
            score += 0.2

        return min(1.0, score)

    def _calculate_process_score(self, task: str, subagent: SubagentDefinition) -> float:
        """Calculate cognitive process alignment score (0.0-1.0)."""
        task_lower = task.lower()
        score = 0.0

        # Check for capability matches
        for capability in subagent.capabilities:
            if any(word in task_lower for word in capability.lower().split()):
                score += 0.25

        return min(1.0, score)

    def _calculate_output_score(self, task: str, subagent: SubagentDefinition) -> float:
        """Calculate output format match score (0.0-1.0)."""
        task_lower = task.lower()
        matches = 0

        for output_type in subagent.output_types:
            if output_type.lower() in task_lower:
                matches += 1

        if matches > 0:
            return min(1.0, 0.5 + (matches * 0.25))
        return 0.0

    def _detect_anti_patterns(self, task: str, subagent_name: str) -> List[str]:
        """Detect anti-patterns in assignment."""
        task_lower = task.lower()
        detected = []

        for pattern_type, patterns in self.ANTI_PATTERNS.items():
            for agent, keywords in patterns:
                if agent == subagent_name:
                    for keyword in keywords:
                        if keyword.lower() in task_lower:
                            detected.append(f"{pattern_type}: '{keyword}' suggests different specialist")

        return detected

    def _calculate_confidence(
        self,
        domain_score: float,
        process_score: float,
        output_score: float,
        anti_patterns: List[str]
    ) -> float:
        """Calculate overall confidence score."""
        # Weighted combination
        confidence = (
            domain_score * 0.5 +
            process_score * 0.3 +
            output_score * 0.2
        )

        # Penalty for anti-patterns
        confidence -= len(anti_patterns) * 0.15

        return max(0.0, min(1.0, confidence))

    def select_subagent(self, task: str) -> Assignment:
        """
        Select the best subagent for a task.

        Args:
            task: Task description

        Returns:
            Assignment object with specialist and rationale
        """
        best_match = None
        best_confidence = 0.0
        best_scores = {}
        best_anti_patterns = []
        second_best = None

        for name, subagent in self.SUBAGENTS.items():
            domain_score = self._calculate_domain_score(task, subagent)
            process_score = self._calculate_process_score(task, subagent)
            output_score = self._calculate_output_score(task, subagent)
            anti_patterns = self._detect_anti_patterns(task, name)

            confidence = self._calculate_confidence(
                domain_score, process_score, output_score, anti_patterns
            )

            if confidence > best_confidence:
                # Current best becomes second best
                second_best = best_match
                # Update best
                best_match = name
                best_confidence = confidence
                best_scores = {
                    "domain_fit": domain_score,
                    "process_alignment": process_score,
                    "output_match": output_score
                }
                best_anti_patterns = anti_patterns

        rationale = {
            "domain_fit": f"Domain score: {best_scores['domain_fit']:.2f}",
            "cognitive_process": f"Process alignment: {best_scores['process_alignment']:.2f}",
            "output_format": f"Output match: {best_scores['output_match']:.2f}",
            "cognitive_model": self.SUBAGENTS[best_match].cognitive_model if best_match else "Unknown"
        }

        return Assignment(
            task=task,
            specialist=best_match or "unknown",
            confidence=best_confidence,
            rationale=rationale,
            anti_patterns=best_anti_patterns,
            alternative=second_best if best_confidence < 0.8 else None
        )

    def select_for_tasks(self, tasks: List[str]) -> List[Assignment]:
        """Select subagents for multiple tasks."""
        return [self.select_subagent(task) for task in tasks]

    def process(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Main processing function.

        Args:
            tasks: List of task descriptions

        Returns:
            dict: Results with status, data, and any errors
        """
        try:
            assignments = self.select_for_tasks(tasks)

            # Calculate statistics
            specialist_dist = {}
            low_confidence = []
            for a in assignments:
                specialist_dist[a.specialist] = specialist_dist.get(a.specialist, 0) + 1
                if a.confidence < self.threshold:
                    low_confidence.append(a.task)

            return {
                "status": "success",
                "data": {
                    "assignments": [asdict(a) for a in assignments],
                    "assignment_count": len(assignments),
                    "specialist_distribution": specialist_dist,
                    "low_confidence_tasks": low_confidence,
                    "average_confidence": sum(a.confidence for a in assignments) / len(assignments) if assignments else 0
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Subagent selection failed: {str(e)}", exc_info=True)
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
                    f"Assigned {data['assignment_count']} tasks",
                    f"Average confidence: {data['average_confidence']:.2f}",
                    ""
                ]
                for a in data["assignments"]:
                    lines.append(f"Task: {a['task'][:50]}...")
                    lines.append(f"  → {a['specialist']} (confidence: {a['confidence']:.2f})")
                    if a['anti_patterns']:
                        lines.append(f"  ⚠ Anti-patterns: {', '.join(a['anti_patterns'][:2])}")
                    if a.get('alternative'):
                        lines.append(f"  Alternative: {a['alternative']}")
                    lines.append("")
                return '\n'.join(lines)
            else:
                return f"ERROR: {result['error']}"

        elif output_format == "markdown":
            if result["status"] == "success":
                data = result["data"]
                md = f"# Task Assignments\n\n"
                md += f"**Total Tasks**: {data['assignment_count']}\n\n"
                md += f"**Average Confidence**: {data['average_confidence']:.2f}\n\n"

                md += "## Assignments\n\n"
                for a in data["assignments"]:
                    md += f"### {a['task'][:60]}...\n\n"
                    md += f"- **Specialist**: {a['specialist']}\n"
                    md += f"- **Confidence**: {a['confidence']:.2f}\n"
                    md += f"- **Rationale**:\n"
                    for k, v in a['rationale'].items():
                        md += f"  - {k}: {v}\n"
                    if a['anti_patterns']:
                        md += f"- **Warnings**: {', '.join(a['anti_patterns'])}\n"
                    md += "\n"

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
        "--task", "-t",
        default=None,
        help="Single task to assign"
    )

    parser.add_argument(
        "--tasks",
        default=None,
        help="JSON file with list of tasks"
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
        "--explain",
        action="store_true",
        help="Include detailed explanations"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Minimum confidence threshold (default: 0.7)"
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

        # Get tasks
        tasks = []
        if args.task:
            tasks = [args.task]
        elif args.tasks:
            tasks_path = Path(args.tasks)
            if not tasks_path.exists():
                logger.error(f"Tasks file not found: {args.tasks}")
                return 1
            with open(tasks_path, 'r') as f:
                tasks_data = json.load(f)
            if isinstance(tasks_data, list):
                tasks = tasks_data
            elif isinstance(tasks_data, dict):
                tasks = tasks_data.get("tasks", [])
        else:
            logger.error("No task(s) provided. Use --task or --tasks")
            return 1

        if not tasks:
            logger.error("No tasks found")
            return 1

        selector = SubagentSelector(
            explain=args.explain,
            threshold=args.threshold
        )

        result = selector.process(tasks)
        output = selector.format_output(result, args.format)

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

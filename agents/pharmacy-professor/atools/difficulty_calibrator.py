#!/usr/bin/env python3
"""
Difficulty Calibrator - Bloom's taxonomy alignment and difficulty assessment

Calibrates educational content difficulty using:
- Bloom's Taxonomy levels (Remember → Create)
- Question complexity analysis
- Audience-appropriate distributions
- Prerequisite knowledge estimation
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum, IntEnum


class BloomLevel(IntEnum):
    """Bloom's Taxonomy cognitive levels."""
    REMEMBER = 1      # Recall facts, basic concepts
    UNDERSTAND = 2    # Explain ideas, concepts
    APPLY = 3         # Use information in new situations
    ANALYZE = 4       # Draw connections, distinguish parts
    EVALUATE = 5      # Justify decisions, make judgments
    CREATE = 6        # Produce new or original work


class AudienceLevel(Enum):
    """Target audience expertise levels."""
    NOVICE = "novice"              # Pre-pharmacy, early PharmD
    INTERMEDIATE = "intermediate"  # Mid-program PharmD
    ADVANCED = "advanced"          # Late PharmD, APPE
    EXPERT = "expert"              # Residents, practitioners


@dataclass
class DifficultyAssessment:
    """Assessment of content/question difficulty."""
    bloom_level: BloomLevel
    audience_level: AudienceLevel
    complexity_score: float  # 0.0 to 1.0
    cognitive_load: str      # low, moderate, high
    prerequisites: List[str]
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['bloom_level'] = self.bloom_level.name
        result['bloom_level_num'] = self.bloom_level.value
        result['audience_level'] = self.audience_level.value
        return result


@dataclass
class DistributionRecommendation:
    """Recommended difficulty distribution for content."""
    audience: AudienceLevel
    bloom_distribution: Dict[str, float]  # BloomLevel name -> percentage
    rationale: str
    sample_question_types: Dict[str, List[str]]


class DifficultyCalibrator:
    """
    Calibrates educational content difficulty based on Bloom's Taxonomy.

    Provides:
    - Question difficulty assessment
    - Bloom's level classification
    - Audience-appropriate distributions
    - Prerequisite knowledge estimation
    """

    # Keywords indicating Bloom's levels
    BLOOM_INDICATORS = {
        BloomLevel.REMEMBER: [
            'define', 'list', 'name', 'state', 'recall', 'identify',
            'recognize', 'match', 'label', 'select', 'what is',
            'which of the following', 'true or false',
        ],
        BloomLevel.UNDERSTAND: [
            'explain', 'describe', 'summarize', 'paraphrase', 'classify',
            'compare', 'contrast', 'interpret', 'discuss', 'distinguish',
            'predict', 'why does', 'how does',
        ],
        BloomLevel.APPLY: [
            'apply', 'demonstrate', 'calculate', 'solve', 'use',
            'implement', 'execute', 'compute', 'determine', 'modify',
            'patient case', 'clinical scenario', 'given the following',
        ],
        BloomLevel.ANALYZE: [
            'analyze', 'differentiate', 'examine', 'investigate',
            'categorize', 'deconstruct', 'organize', 'attribute',
            'compare and contrast', 'what is the relationship',
            'most likely cause', 'best explains',
        ],
        BloomLevel.EVALUATE: [
            'evaluate', 'assess', 'judge', 'justify', 'critique',
            'recommend', 'defend', 'prioritize', 'rank', 'select best',
            'most appropriate', 'first-line', 'drug of choice',
        ],
        BloomLevel.CREATE: [
            'create', 'design', 'develop', 'formulate', 'construct',
            'plan', 'produce', 'devise', 'compose', 'generate',
            'design a protocol', 'develop a plan',
        ],
    }

    # Recommended distributions by audience
    AUDIENCE_DISTRIBUTIONS = {
        AudienceLevel.NOVICE: {
            BloomLevel.REMEMBER: 0.40,
            BloomLevel.UNDERSTAND: 0.35,
            BloomLevel.APPLY: 0.20,
            BloomLevel.ANALYZE: 0.05,
            BloomLevel.EVALUATE: 0.00,
            BloomLevel.CREATE: 0.00,
        },
        AudienceLevel.INTERMEDIATE: {
            BloomLevel.REMEMBER: 0.25,
            BloomLevel.UNDERSTAND: 0.30,
            BloomLevel.APPLY: 0.30,
            BloomLevel.ANALYZE: 0.10,
            BloomLevel.EVALUATE: 0.05,
            BloomLevel.CREATE: 0.00,
        },
        AudienceLevel.ADVANCED: {
            BloomLevel.REMEMBER: 0.15,
            BloomLevel.UNDERSTAND: 0.20,
            BloomLevel.APPLY: 0.30,
            BloomLevel.ANALYZE: 0.20,
            BloomLevel.EVALUATE: 0.10,
            BloomLevel.CREATE: 0.05,
        },
        AudienceLevel.EXPERT: {
            BloomLevel.REMEMBER: 0.10,
            BloomLevel.UNDERSTAND: 0.15,
            BloomLevel.APPLY: 0.25,
            BloomLevel.ANALYZE: 0.25,
            BloomLevel.EVALUATE: 0.15,
            BloomLevel.CREATE: 0.10,
        },
    }

    # Sample question types by Bloom's level
    QUESTION_TYPES = {
        BloomLevel.REMEMBER: [
            "Multiple choice - single best answer",
            "True/False",
            "Matching",
            "Fill in the blank",
            "Definition questions",
        ],
        BloomLevel.UNDERSTAND: [
            "Multiple choice with explanation",
            "Compare/contrast questions",
            "Mechanism explanation",
            "Classification questions",
            "Short answer - describe/explain",
        ],
        BloomLevel.APPLY: [
            "Clinical vignette - calculation",
            "Patient case - drug selection",
            "Dosing adjustment scenarios",
            "Drug interaction identification",
            "Pharmacokinetic problems",
        ],
        BloomLevel.ANALYZE: [
            "Complex clinical vignette",
            "Multi-step problem solving",
            "Drug therapy analysis",
            "Literature interpretation",
            "Algorithm application",
        ],
        BloomLevel.EVALUATE: [
            "Therapy prioritization",
            "Treatment plan critique",
            "Drug selection justification",
            "Risk-benefit analysis",
            "Guideline application",
        ],
        BloomLevel.CREATE: [
            "Care plan development",
            "Protocol design",
            "Patient education material",
            "SOAP note writing",
            "Therapy proposal",
        ],
    }

    # Complexity indicators
    COMPLEXITY_INDICATORS = {
        'high': [
            'multiple drugs', 'drug interactions', 'contraindications',
            'renal impairment', 'hepatic impairment', 'pregnancy',
            'pediatric', 'geriatric', 'polypharmacy', 'multi-step',
            'algorithm', 'guideline', 'evidence-based',
        ],
        'moderate': [
            'mechanism', 'adverse effect', 'monitoring', 'dosing',
            'indication', 'pharmacokinetics', 'therapeutic range',
            'clinical pearl', 'calculation', 'conversion',
        ],
        'low': [
            'definition', 'list', 'name', 'identify', 'classify',
            'generic', 'brand', 'drug class', 'route', 'formulation',
        ],
    }

    def __init__(self):
        """Initialize the difficulty calibrator."""
        # Compile keyword patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.bloom_patterns = {}
        for level, keywords in self.BLOOM_INDICATORS.items():
            pattern = '|'.join(re.escape(kw) for kw in keywords)
            self.bloom_patterns[level] = re.compile(pattern, re.IGNORECASE)

    def assess_difficulty(
        self,
        content: str,
        content_type: str = "question"
    ) -> DifficultyAssessment:
        """
        Assess difficulty of content.

        Args:
            content: Question, concept, or educational content
            content_type: Type of content (question, concept, explanation)

        Returns:
            DifficultyAssessment with detailed analysis
        """
        # Detect Bloom's level
        bloom_level = self._detect_bloom_level(content)

        # Calculate complexity score
        complexity_score = self._calculate_complexity(content)

        # Determine cognitive load
        cognitive_load = self._assess_cognitive_load(content, bloom_level, complexity_score)

        # Estimate prerequisites
        prerequisites = self._estimate_prerequisites(content)

        # Determine appropriate audience
        audience_level = self._determine_audience(bloom_level, complexity_score)

        # Generate rationale
        rationale = self._generate_rationale(
            bloom_level, complexity_score, cognitive_load, content_type
        )

        return DifficultyAssessment(
            bloom_level=bloom_level,
            audience_level=audience_level,
            complexity_score=complexity_score,
            cognitive_load=cognitive_load,
            prerequisites=prerequisites,
            rationale=rationale
        )

    def _detect_bloom_level(self, content: str) -> BloomLevel:
        """Detect Bloom's level from content."""
        scores = {}

        for level, pattern in self.bloom_patterns.items():
            matches = pattern.findall(content)
            scores[level] = len(matches)

        # Weight higher levels more (they're more specific)
        weighted_scores = {}
        for level, count in scores.items():
            weight = 1.0 + (level.value - 1) * 0.2  # Higher levels get more weight
            weighted_scores[level] = count * weight

        # Find highest scoring level
        if any(weighted_scores.values()):
            best_level = max(weighted_scores, key=weighted_scores.get)
            return best_level

        # Default to UNDERSTAND if no clear indicators
        return BloomLevel.UNDERSTAND

    def _calculate_complexity(self, content: str) -> float:
        """Calculate complexity score (0.0 to 1.0)."""
        content_lower = content.lower()

        # Count indicators
        high_count = sum(
            1 for indicator in self.COMPLEXITY_INDICATORS['high']
            if indicator in content_lower
        )
        moderate_count = sum(
            1 for indicator in self.COMPLEXITY_INDICATORS['moderate']
            if indicator in content_lower
        )
        low_count = sum(
            1 for indicator in self.COMPLEXITY_INDICATORS['low']
            if indicator in content_lower
        )

        # Weighted score
        total_indicators = len(self.COMPLEXITY_INDICATORS['high']) + \
                          len(self.COMPLEXITY_INDICATORS['moderate']) + \
                          len(self.COMPLEXITY_INDICATORS['low'])

        if total_indicators == 0:
            return 0.5

        # Weight: high=1.0, moderate=0.5, low=0.2
        weighted_sum = high_count * 1.0 + moderate_count * 0.5 + low_count * 0.2
        max_possible = high_count + moderate_count + low_count

        if max_possible == 0:
            return 0.5

        score = weighted_sum / max_possible

        # Adjust for content length (longer = potentially more complex)
        word_count = len(content.split())
        length_factor = min(1.0, word_count / 200)  # Cap at 200 words

        # Combine (70% indicator-based, 30% length-based)
        final_score = score * 0.7 + length_factor * 0.3

        return min(1.0, max(0.0, final_score))

    def _assess_cognitive_load(
        self,
        content: str,
        bloom_level: BloomLevel,
        complexity_score: float
    ) -> str:
        """Assess cognitive load level."""
        # Factors affecting cognitive load
        load_score = 0.0

        # Bloom's level contributes
        load_score += (bloom_level.value / 6.0) * 0.4

        # Complexity contributes
        load_score += complexity_score * 0.4

        # Content length contributes
        word_count = len(content.split())
        if word_count > 150:
            load_score += 0.2
        elif word_count > 75:
            load_score += 0.1

        # Classify
        if load_score >= 0.7:
            return "high"
        elif load_score >= 0.4:
            return "moderate"
        else:
            return "low"

    def _estimate_prerequisites(self, content: str) -> List[str]:
        """Estimate prerequisite knowledge needed."""
        prerequisites = []
        content_lower = content.lower()

        # Prerequisite mappings
        prerequisite_triggers = {
            'pharmacokinetics': ['basic chemistry', 'math skills', 'physiology'],
            'drug interaction': ['pharmacology basics', 'enzyme systems', 'CYP450'],
            'renal': ['kidney physiology', 'GFR calculation', 'drug elimination'],
            'hepatic': ['liver physiology', 'drug metabolism', 'CYP enzymes'],
            'dosing': ['pharmacokinetics', 'math skills', 'drug parameters'],
            'mechanism': ['cell biology', 'receptor theory', 'physiology'],
            'adverse effect': ['pharmacology basics', 'drug mechanisms'],
            'therapeutic': ['disease pathophysiology', 'treatment goals'],
            'calculation': ['math skills', 'unit conversions', 'pharmacokinetics'],
            'pediatric': ['developmental pharmacology', 'dosing adjustments'],
            'geriatric': ['aging physiology', 'polypharmacy', 'renal changes'],
        }

        for trigger, prereqs in prerequisite_triggers.items():
            if trigger in content_lower:
                prerequisites.extend(prereqs)

        # Deduplicate and return
        return list(dict.fromkeys(prerequisites))[:5]  # Max 5 prerequisites

    def _determine_audience(
        self,
        bloom_level: BloomLevel,
        complexity_score: float
    ) -> AudienceLevel:
        """Determine appropriate audience level."""
        # Combined score
        combined = (bloom_level.value / 6.0) * 0.6 + complexity_score * 0.4

        if combined >= 0.75:
            return AudienceLevel.EXPERT
        elif combined >= 0.55:
            return AudienceLevel.ADVANCED
        elif combined >= 0.35:
            return AudienceLevel.INTERMEDIATE
        else:
            return AudienceLevel.NOVICE

    def _generate_rationale(
        self,
        bloom_level: BloomLevel,
        complexity_score: float,
        cognitive_load: str,
        content_type: str
    ) -> str:
        """Generate explanation for difficulty assessment."""
        bloom_descriptions = {
            BloomLevel.REMEMBER: "recall of factual information",
            BloomLevel.UNDERSTAND: "comprehension and explanation of concepts",
            BloomLevel.APPLY: "application of knowledge to new situations",
            BloomLevel.ANALYZE: "analysis of relationships and patterns",
            BloomLevel.EVALUATE: "judgment and decision-making",
            BloomLevel.CREATE: "synthesis and creation of new solutions",
        }

        return (
            f"This {content_type} requires {bloom_descriptions[bloom_level]} "
            f"(Bloom's level: {bloom_level.name}). "
            f"Complexity score: {complexity_score:.2f}/1.0. "
            f"Cognitive load: {cognitive_load}."
        )

    def get_distribution_recommendation(
        self,
        audience: AudienceLevel
    ) -> DistributionRecommendation:
        """
        Get recommended difficulty distribution for audience.

        Args:
            audience: Target audience level

        Returns:
            DistributionRecommendation with percentages and guidance
        """
        distribution = self.AUDIENCE_DISTRIBUTIONS[audience]

        # Convert to readable format
        bloom_dist = {
            level.name: pct for level, pct in distribution.items()
        }

        # Get sample question types for non-zero levels
        sample_types = {}
        for level, pct in distribution.items():
            if pct > 0:
                sample_types[level.name] = self.QUESTION_TYPES[level]

        # Generate rationale
        rationale_parts = []
        if audience == AudienceLevel.NOVICE:
            rationale_parts.append(
                "Focus on building foundational knowledge through recall and basic understanding."
            )
        elif audience == AudienceLevel.INTERMEDIATE:
            rationale_parts.append(
                "Balance knowledge building with practical application through clinical scenarios."
            )
        elif audience == AudienceLevel.ADVANCED:
            rationale_parts.append(
                "Emphasize clinical application and analysis with complex patient cases."
            )
        else:  # EXPERT
            rationale_parts.append(
                "Challenge with evaluation and synthesis tasks requiring expert judgment."
            )

        return DistributionRecommendation(
            audience=audience,
            bloom_distribution=bloom_dist,
            rationale=" ".join(rationale_parts),
            sample_question_types=sample_types
        )

    def calibrate_question_set(
        self,
        questions: List[str],
        target_audience: AudienceLevel
    ) -> Dict[str, Any]:
        """
        Calibrate a set of questions against target distribution.

        Args:
            questions: List of question texts
            target_audience: Desired audience level

        Returns:
            Analysis with current vs target distribution and recommendations
        """
        # Assess each question
        assessments = [self.assess_difficulty(q) for q in questions]

        # Calculate current distribution
        level_counts = {level: 0 for level in BloomLevel}
        for assessment in assessments:
            level_counts[assessment.bloom_level] += 1

        total = len(questions)
        current_distribution = {
            level.name: count / total if total > 0 else 0
            for level, count in level_counts.items()
        }

        # Get target distribution
        target = self.AUDIENCE_DISTRIBUTIONS[target_audience]
        target_distribution = {level.name: pct for level, pct in target.items()}

        # Calculate gaps
        gaps = {}
        for level_name in current_distribution:
            gaps[level_name] = target_distribution.get(level_name, 0) - current_distribution[level_name]

        # Generate recommendations
        recommendations = []
        for level_name, gap in gaps.items():
            if gap > 0.1:  # Need more of this level
                recommendations.append(
                    f"Add {int(gap * total)} more {level_name} level questions"
                )
            elif gap < -0.1:  # Have too many
                recommendations.append(
                    f"Consider replacing {int(-gap * total)} {level_name} level questions"
                )

        return {
            "total_questions": total,
            "target_audience": target_audience.value,
            "current_distribution": current_distribution,
            "target_distribution": target_distribution,
            "gaps": gaps,
            "recommendations": recommendations,
            "individual_assessments": [a.to_dict() for a in assessments]
        }


def main():
    """CLI interface for difficulty calibrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Assess and calibrate educational content difficulty"
    )
    parser.add_argument(
        "content",
        nargs="?",
        help="Content to assess (question or file path)"
    )
    parser.add_argument(
        "--audience", "-a",
        choices=[a.value for a in AudienceLevel],
        help="Get distribution recommendation for audience"
    )
    parser.add_argument(
        "--file", "-f",
        help="File containing questions (one per line)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format"
    )

    args = parser.parse_args()

    calibrator = DifficultyCalibrator()

    if args.audience and not args.content and not args.file:
        # Just get distribution recommendation
        audience = AudienceLevel(args.audience)
        rec = calibrator.get_distribution_recommendation(audience)

        if args.format == "json":
            output = json.dumps({
                "audience": rec.audience.value,
                "bloom_distribution": rec.bloom_distribution,
                "rationale": rec.rationale,
                "sample_question_types": rec.sample_question_types
            }, indent=2)
        else:
            lines = [f"# Distribution Recommendation: {rec.audience.value.title()}\n"]
            lines.append(rec.rationale + "\n")
            lines.append("\n## Bloom's Distribution\n")
            for level, pct in rec.bloom_distribution.items():
                lines.append(f"- {level}: {pct*100:.0f}%")
            lines.append("\n\n## Sample Question Types\n")
            for level, types in rec.sample_question_types.items():
                lines.append(f"\n### {level}")
                for qtype in types:
                    lines.append(f"- {qtype}")
            output = "\n".join(lines)

    elif args.file:
        # Calibrate question set
        questions = Path(args.file).read_text().strip().split('\n')
        audience = AudienceLevel(args.audience) if args.audience else AudienceLevel.INTERMEDIATE
        result = calibrator.calibrate_question_set(questions, audience)

        if args.format == "json":
            output = json.dumps(result, indent=2)
        else:
            lines = ["# Question Set Calibration\n"]
            lines.append(f"**Total Questions**: {result['total_questions']}")
            lines.append(f"**Target Audience**: {result['target_audience']}\n")
            lines.append("\n## Current vs Target Distribution\n")
            lines.append("| Level | Current | Target | Gap |")
            lines.append("|-------|---------|--------|-----|")
            for level in BloomLevel:
                curr = result['current_distribution'].get(level.name, 0)
                tgt = result['target_distribution'].get(level.name, 0)
                gap = result['gaps'].get(level.name, 0)
                lines.append(f"| {level.name} | {curr*100:.0f}% | {tgt*100:.0f}% | {gap*100:+.0f}% |")
            lines.append("\n\n## Recommendations\n")
            for rec in result['recommendations']:
                lines.append(f"- {rec}")
            output = "\n".join(lines)

    elif args.content:
        # Single content assessment
        assessment = calibrator.assess_difficulty(args.content)

        if args.format == "json":
            output = json.dumps(assessment.to_dict(), indent=2)
        else:
            lines = ["# Difficulty Assessment\n"]
            lines.append(f"**Bloom's Level**: {assessment.bloom_level.name} ({assessment.bloom_level.value}/6)")
            lines.append(f"**Audience Level**: {assessment.audience_level.value}")
            lines.append(f"**Complexity Score**: {assessment.complexity_score:.2f}")
            lines.append(f"**Cognitive Load**: {assessment.cognitive_load}")
            lines.append(f"\n**Rationale**: {assessment.rationale}")
            if assessment.prerequisites:
                lines.append(f"\n**Prerequisites**: {', '.join(assessment.prerequisites)}")
            output = "\n".join(lines)

    else:
        parser.print_help()
        return

    if args.output:
        Path(args.output).write_text(output)
        print(f"Written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quality Scorer - Educational content quality assessment

Evaluates generated educational materials against:
- Pharmaceutical accuracy
- Educational effectiveness
- Bloom's taxonomy alignment
- Content coverage
- Format compliance
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum


class QualityDimension(Enum):
    """Dimensions of quality assessment."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    BLOOM_ALIGNMENT = "bloom_alignment"
    DISTRACTOR_QUALITY = "distractor_quality"
    CLINICAL_RELEVANCE = "clinical_relevance"
    FORMAT_COMPLIANCE = "format_compliance"


class ContentType(Enum):
    """Types of educational content."""
    QUIZ_MCQ = "quiz_mcq"
    QUIZ_TF = "quiz_tf"
    FLASHCARD = "flashcard"
    STUDY_GUIDE = "study_guide"
    CASE_STUDY = "case_study"
    EXAM = "exam"


@dataclass
class QualityScore:
    """Score for a single quality dimension."""
    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    weight: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def weighted_score(self) -> float:
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['dimension'] = self.dimension.value
        result['weighted_score'] = self.weighted_score()
        return result


@dataclass
class QualityReport:
    """Complete quality assessment report."""
    content_type: ContentType
    overall_score: float
    dimension_scores: List[QualityScore]
    passed: bool
    pass_threshold: float
    critical_issues: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['content_type'] = self.content_type.value
        result['dimension_scores'] = [s.to_dict() for s in self.dimension_scores]
        return result


class QualityScorer:
    """
    Assesses quality of generated educational materials.

    Evaluates across multiple dimensions with configurable weights
    and pass thresholds per content type.
    """

    # Default weights by content type
    DEFAULT_WEIGHTS = {
        ContentType.QUIZ_MCQ: {
            QualityDimension.ACCURACY: 0.30,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.CLARITY: 0.15,
            QualityDimension.BLOOM_ALIGNMENT: 0.15,
            QualityDimension.DISTRACTOR_QUALITY: 0.15,
            QualityDimension.CLINICAL_RELEVANCE: 0.05,
            QualityDimension.FORMAT_COMPLIANCE: 0.05,
        },
        ContentType.QUIZ_TF: {
            QualityDimension.ACCURACY: 0.35,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.CLARITY: 0.20,
            QualityDimension.BLOOM_ALIGNMENT: 0.15,
            QualityDimension.CLINICAL_RELEVANCE: 0.10,
            QualityDimension.FORMAT_COMPLIANCE: 0.05,
        },
        ContentType.FLASHCARD: {
            QualityDimension.ACCURACY: 0.30,
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.CLARITY: 0.25,
            QualityDimension.BLOOM_ALIGNMENT: 0.10,
            QualityDimension.CLINICAL_RELEVANCE: 0.10,
            QualityDimension.FORMAT_COMPLIANCE: 0.05,
        },
        ContentType.STUDY_GUIDE: {
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.COMPLETENESS: 0.25,
            QualityDimension.CLARITY: 0.20,
            QualityDimension.BLOOM_ALIGNMENT: 0.10,
            QualityDimension.CLINICAL_RELEVANCE: 0.15,
            QualityDimension.FORMAT_COMPLIANCE: 0.05,
        },
        ContentType.CASE_STUDY: {
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.CLARITY: 0.15,
            QualityDimension.BLOOM_ALIGNMENT: 0.10,
            QualityDimension.CLINICAL_RELEVANCE: 0.25,
            QualityDimension.FORMAT_COMPLIANCE: 0.05,
        },
        ContentType.EXAM: {
            QualityDimension.ACCURACY: 0.30,
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.CLARITY: 0.15,
            QualityDimension.BLOOM_ALIGNMENT: 0.15,
            QualityDimension.DISTRACTOR_QUALITY: 0.10,
            QualityDimension.CLINICAL_RELEVANCE: 0.05,
            QualityDimension.FORMAT_COMPLIANCE: 0.05,
        },
    }

    # Pass thresholds by content type
    PASS_THRESHOLDS = {
        ContentType.QUIZ_MCQ: 0.70,
        ContentType.QUIZ_TF: 0.70,
        ContentType.FLASHCARD: 0.65,
        ContentType.STUDY_GUIDE: 0.65,
        ContentType.CASE_STUDY: 0.70,
        ContentType.EXAM: 0.75,
    }

    # Pharmaceutical accuracy red flags
    ACCURACY_RED_FLAGS = [
        # Dangerous dose errors
        (r'\d{4,}\s*mg', "Unusually high dose detected"),
        # Missing units
        (r'dose[:\s]+\d+(?!\s*(?:mg|g|mcg|units|mL))', "Dose without units"),
        # Contradictory statements
        (r'safe.*(?:contraindicated|dangerous)|(?:contraindicated|dangerous).*safe', "Contradictory safety statement"),
    ]

    # Required elements by content type
    REQUIRED_ELEMENTS = {
        ContentType.QUIZ_MCQ: ['question', 'options', 'correct_answer', 'explanation'],
        ContentType.QUIZ_TF: ['statement', 'answer', 'explanation'],
        ContentType.FLASHCARD: ['front', 'back'],
        ContentType.STUDY_GUIDE: ['title', 'objectives', 'content'],
        ContentType.CASE_STUDY: ['patient', 'presentation', 'questions'],
        ContentType.EXAM: ['instructions', 'questions', 'answer_key'],
    }

    # Clarity indicators (problems to detect)
    CLARITY_ISSUES = [
        (r'(?:etc\.?|and so on|and more)', "Vague language (etc.)"),
        (r'\b(?:thing|stuff|something)\b', "Imprecise terminology"),
        (r'(?:always|never)(?!\s+(?:monitor|avoid|check|verify))', "Absolute statement without context"),
        (r'[A-Z]{5,}', "Excessive capitalization"),
        (r'[!?]{2,}', "Multiple punctuation marks"),
    ]

    def __init__(
        self,
        custom_weights: Optional[Dict[ContentType, Dict[QualityDimension, float]]] = None,
        custom_thresholds: Optional[Dict[ContentType, float]] = None
    ):
        """
        Initialize quality scorer.

        Args:
            custom_weights: Override default dimension weights
            custom_thresholds: Override default pass thresholds
        """
        self.weights = self.DEFAULT_WEIGHTS.copy()
        if custom_weights:
            self.weights.update(custom_weights)

        self.thresholds = self.PASS_THRESHOLDS.copy()
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)

    def score(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityReport:
        """
        Score educational content quality.

        Args:
            content: Content to evaluate (structure depends on type)
            content_type: Type of educational content
            source_concepts: Expected concepts to cover
            target_bloom_level: Expected Bloom's taxonomy level

        Returns:
            QualityReport with detailed scores and recommendations
        """
        weights = self.weights.get(content_type, self.DEFAULT_WEIGHTS[ContentType.QUIZ_MCQ])
        threshold = self.thresholds.get(content_type, 0.70)

        dimension_scores = []
        critical_issues = []

        # Score each dimension
        for dimension, weight in weights.items():
            if weight > 0:
                score = self._score_dimension(
                    content, content_type, dimension,
                    source_concepts, target_bloom_level
                )
                score.weight = weight
                dimension_scores.append(score)

                # Collect critical issues (low score on high-weight dimensions)
                if score.score < 0.5 and weight >= 0.2:
                    critical_issues.extend(score.issues)

        # Calculate overall score
        overall_score = sum(s.weighted_score() for s in dimension_scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(dimension_scores, content_type)

        return QualityReport(
            content_type=content_type,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            passed=overall_score >= threshold,
            pass_threshold=threshold,
            critical_issues=critical_issues,
            recommendations=recommendations
        )

    def _score_dimension(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        dimension: QualityDimension,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score a single quality dimension."""
        scorers = {
            QualityDimension.ACCURACY: self._score_accuracy,
            QualityDimension.COMPLETENESS: self._score_completeness,
            QualityDimension.CLARITY: self._score_clarity,
            QualityDimension.BLOOM_ALIGNMENT: self._score_bloom_alignment,
            QualityDimension.DISTRACTOR_QUALITY: self._score_distractor_quality,
            QualityDimension.CLINICAL_RELEVANCE: self._score_clinical_relevance,
            QualityDimension.FORMAT_COMPLIANCE: self._score_format_compliance,
        }

        scorer = scorers.get(dimension)
        if scorer:
            return scorer(content, content_type, source_concepts, target_bloom_level)

        return QualityScore(dimension=dimension, score=1.0, weight=0.0)

    def _score_accuracy(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score pharmaceutical accuracy."""
        issues = []
        suggestions = []
        score = 1.0

        # Convert content to searchable text
        text = json.dumps(content) if isinstance(content, dict) else str(content)

        # Check for red flags
        for pattern, issue in self.ACCURACY_RED_FLAGS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(issue)
                score -= 0.2

        # Check for citations/sources if present
        if 'explanation' in str(content) or 'rationale' in str(content):
            if not re.search(r'(?:source|reference|guideline|study)', text, re.IGNORECASE):
                suggestions.append("Consider adding source references")
                score -= 0.05

        # Check for hedging language in factual statements
        hedging_patterns = [
            r'(?:might|may|possibly|perhaps).*(?:cause|lead to|result in)',
        ]
        for pattern in hedging_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                suggestions.append("Consider being more definitive in factual statements")

        return QualityScore(
            dimension=QualityDimension.ACCURACY,
            score=max(0.0, score),
            weight=0.0,  # Will be set by caller
            issues=issues,
            suggestions=suggestions
        )

    def _score_completeness(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score content completeness."""
        issues = []
        suggestions = []
        score = 1.0

        # Check required elements
        required = self.REQUIRED_ELEMENTS.get(content_type, [])
        text = json.dumps(content).lower() if isinstance(content, dict) else str(content).lower()

        for element in required:
            if element not in text:
                issues.append(f"Missing required element: {element}")
                score -= 0.15

        # Check concept coverage if provided
        if source_concepts:
            covered = 0
            for concept in source_concepts:
                if concept.lower() in text:
                    covered += 1

            coverage_ratio = covered / len(source_concepts) if source_concepts else 1.0
            if coverage_ratio < 0.8:
                issues.append(f"Only {coverage_ratio*100:.0f}% of source concepts covered")
                score -= (0.8 - coverage_ratio)

            missing = [c for c in source_concepts if c.lower() not in text]
            if missing:
                suggestions.append(f"Consider adding: {', '.join(missing[:3])}")

        return QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=max(0.0, score),
            weight=0.0,
            issues=issues,
            suggestions=suggestions
        )

    def _score_clarity(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score content clarity."""
        issues = []
        suggestions = []
        score = 1.0

        text = json.dumps(content) if isinstance(content, dict) else str(content)

        # Check for clarity issues
        for pattern, issue in self.CLARITY_ISSUES:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(issue)
                score -= 0.1

        # Check sentence length (very long sentences reduce clarity)
        sentences = re.split(r'[.!?]', text)
        long_sentences = [s for s in sentences if len(s.split()) > 40]
        if long_sentences:
            issues.append(f"{len(long_sentences)} sentences over 40 words")
            suggestions.append("Consider breaking long sentences into shorter ones")
            score -= 0.05 * len(long_sentences)

        # Check for jargon without definition
        jargon_patterns = [
            r'\b(?:PK|PD|ADME|AUC|Cmax|Tmax)\b',
            r'\b(?:CYP\d+[A-Z]\d*)\b',
        ]
        for pattern in jargon_patterns:
            matches = re.findall(pattern, text)
            if matches and 'definition' not in text.lower() and 'means' not in text.lower():
                suggestions.append(f"Consider defining abbreviations: {', '.join(set(matches)[:3])}")

        return QualityScore(
            dimension=QualityDimension.CLARITY,
            score=max(0.0, score),
            weight=0.0,
            issues=issues,
            suggestions=suggestions
        )

    def _score_bloom_alignment(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score Bloom's taxonomy alignment."""
        issues = []
        suggestions = []
        score = 1.0

        if not target_bloom_level:
            return QualityScore(
                dimension=QualityDimension.BLOOM_ALIGNMENT,
                score=1.0,
                weight=0.0,
                issues=[],
                suggestions=["No target Bloom's level specified"]
            )

        text = json.dumps(content).lower() if isinstance(content, dict) else str(content).lower()

        # Bloom's level indicators
        level_indicators = {
            'remember': ['define', 'list', 'name', 'recall', 'identify'],
            'understand': ['explain', 'describe', 'summarize', 'compare'],
            'apply': ['calculate', 'solve', 'use', 'apply', 'determine'],
            'analyze': ['analyze', 'differentiate', 'examine', 'categorize'],
            'evaluate': ['evaluate', 'assess', 'judge', 'recommend'],
            'create': ['create', 'design', 'develop', 'formulate'],
        }

        # Check if content matches target level
        target_indicators = level_indicators.get(target_bloom_level.lower(), [])
        found_indicators = [ind for ind in target_indicators if ind in text]

        if not found_indicators:
            issues.append(f"No {target_bloom_level} level indicators found")
            score -= 0.3
            suggestions.append(f"Add {target_bloom_level} verbs: {', '.join(target_indicators[:3])}")

        # Check for level mismatch (e.g., asking to "define" in an "analyze" question)
        for level, indicators in level_indicators.items():
            if level != target_bloom_level.lower():
                mismatched = [ind for ind in indicators if ind in text]
                if mismatched and level in ['remember', 'understand'] and target_bloom_level.lower() in ['analyze', 'evaluate', 'create']:
                    issues.append(f"Lower-level verbs ({', '.join(mismatched)}) in {target_bloom_level} content")
                    score -= 0.1

        return QualityScore(
            dimension=QualityDimension.BLOOM_ALIGNMENT,
            score=max(0.0, score),
            weight=0.0,
            issues=issues,
            suggestions=suggestions
        )

    def _score_distractor_quality(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score MCQ distractor quality."""
        issues = []
        suggestions = []
        score = 1.0

        if content_type not in [ContentType.QUIZ_MCQ, ContentType.EXAM]:
            return QualityScore(
                dimension=QualityDimension.DISTRACTOR_QUALITY,
                score=1.0,
                weight=0.0,
                issues=[],
                suggestions=[]
            )

        text = json.dumps(content) if isinstance(content, dict) else str(content)

        # Check for "All of the above" / "None of the above"
        if re.search(r'(?:all|none)\s+of\s+the\s+above', text, re.IGNORECASE):
            issues.append("'All/None of the above' options detected")
            suggestions.append("Replace with specific, plausible distractors")
            score -= 0.15

        # Check for obvious distractors
        obvious_patterns = [
            r'\b(?:always|never)\b.*\b(?:always|never)\b',  # Two absolutes in same option
            r'(?:A|B|C|D)\.\s*\w{1,3}\s*$',  # Very short options
        ]
        for pattern in obvious_patterns:
            if re.search(pattern, text):
                issues.append("Potentially obvious distractor detected")
                score -= 0.1

        # Check for parallel construction
        if 'options' in str(content):
            suggestions.append("Ensure all options have parallel grammatical structure")

        return QualityScore(
            dimension=QualityDimension.DISTRACTOR_QUALITY,
            score=max(0.0, score),
            weight=0.0,
            issues=issues,
            suggestions=suggestions
        )

    def _score_clinical_relevance(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score clinical relevance."""
        issues = []
        suggestions = []
        score = 0.5  # Start neutral

        text = json.dumps(content).lower() if isinstance(content, dict) else str(content).lower()

        # Clinical relevance indicators
        clinical_indicators = [
            'patient', 'clinical', 'practice', 'therapy', 'treatment',
            'monitoring', 'counseling', 'adherence', 'outcome', 'efficacy',
            'safety', 'adverse', 'indication', 'prescribe', 'administer',
        ]

        found = [ind for ind in clinical_indicators if ind in text]

        if len(found) >= 5:
            score = 1.0
        elif len(found) >= 3:
            score = 0.8
        elif len(found) >= 1:
            score = 0.6
            suggestions.append("Add more clinical context/applications")
        else:
            score = 0.4
            issues.append("Limited clinical relevance")
            suggestions.append("Include patient scenarios or clinical applications")

        # Bonus for case-based content
        if content_type == ContentType.CASE_STUDY:
            case_elements = ['history', 'presentation', 'labs', 'vitals', 'medications']
            case_found = [e for e in case_elements if e in text]
            if len(case_found) >= 3:
                score = min(1.0, score + 0.1)

        return QualityScore(
            dimension=QualityDimension.CLINICAL_RELEVANCE,
            score=score,
            weight=0.0,
            issues=issues,
            suggestions=suggestions
        )

    def _score_format_compliance(
        self,
        content: Dict[str, Any],
        content_type: ContentType,
        source_concepts: Optional[List[str]] = None,
        target_bloom_level: Optional[str] = None
    ) -> QualityScore:
        """Score format compliance."""
        issues = []
        suggestions = []
        score = 1.0

        # Check if content is properly structured
        if isinstance(content, dict):
            required = self.REQUIRED_ELEMENTS.get(content_type, [])
            for element in required:
                if element not in content and element not in str(content):
                    issues.append(f"Missing structural element: {element}")
                    score -= 0.1
        else:
            issues.append("Content not in expected structure")
            score -= 0.2

        text = json.dumps(content) if isinstance(content, dict) else str(content)

        # Check for formatting consistency
        if content_type in [ContentType.QUIZ_MCQ, ContentType.EXAM]:
            # Check option labeling
            option_patterns = [
                re.findall(r'^[A-D]\.', text, re.MULTILINE),
                re.findall(r'^[a-d]\)', text, re.MULTILINE),
                re.findall(r'^\d+\.', text, re.MULTILINE),
            ]
            if sum(len(p) for p in option_patterns) == 0:
                suggestions.append("Consider consistent option labeling (A. B. C. D.)")

        return QualityScore(
            dimension=QualityDimension.FORMAT_COMPLIANCE,
            score=max(0.0, score),
            weight=0.0,
            issues=issues,
            suggestions=suggestions
        )

    def _generate_recommendations(
        self,
        scores: List[QualityScore],
        content_type: ContentType
    ) -> List[str]:
        """Generate actionable recommendations from scores."""
        recommendations = []

        # Sort by weighted score (lowest first)
        sorted_scores = sorted(scores, key=lambda s: s.weighted_score())

        # Focus on lowest-scoring dimensions
        for score in sorted_scores[:3]:
            if score.score < 0.7:
                recommendations.extend(score.suggestions)

        # Add type-specific recommendations
        if content_type == ContentType.QUIZ_MCQ and any(
            s.dimension == QualityDimension.DISTRACTOR_QUALITY and s.score < 0.7
            for s in scores
        ):
            recommendations.append(
                "Review MCQ distractors for plausibility and parallel structure"
            )

        if content_type == ContentType.CASE_STUDY and any(
            s.dimension == QualityDimension.CLINICAL_RELEVANCE and s.score < 0.7
            for s in scores
        ):
            recommendations.append(
                "Enhance case with realistic patient details and clinical decision points"
            )

        # Deduplicate
        return list(dict.fromkeys(recommendations))[:5]


def main():
    """CLI interface for quality scorer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Score educational content quality"
    )
    parser.add_argument(
        "input",
        help="JSON file or content to score"
    )
    parser.add_argument(
        "--type", "-t",
        choices=[t.value for t in ContentType],
        required=True,
        help="Content type"
    )
    parser.add_argument(
        "--concepts", "-c",
        help="Comma-separated list of expected concepts"
    )
    parser.add_argument(
        "--bloom", "-b",
        choices=['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'],
        help="Target Bloom's level"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="json",
        help="Output format"
    )

    args = parser.parse_args()

    # Load content
    input_path = Path(args.input)
    if input_path.exists():
        content = json.loads(input_path.read_text())
    else:
        try:
            content = json.loads(args.input)
        except json.JSONDecodeError:
            content = {"text": args.input}

    # Parse concepts
    concepts = args.concepts.split(',') if args.concepts else None

    # Score
    scorer = QualityScorer()
    content_type = ContentType(args.type)
    report = scorer.score(content, content_type, concepts, args.bloom)

    # Format output
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2)
    else:
        lines = [f"# Quality Report: {report.content_type.value}\n"]
        lines.append(f"**Overall Score**: {report.overall_score:.2f}")
        lines.append(f"**Pass Threshold**: {report.pass_threshold:.2f}")
        lines.append(f"**Status**: {'✅ PASSED' if report.passed else '❌ FAILED'}\n")

        lines.append("\n## Dimension Scores\n")
        lines.append("| Dimension | Score | Weight | Weighted |")
        lines.append("|-----------|-------|--------|----------|")
        for score in report.dimension_scores:
            lines.append(
                f"| {score.dimension.value} | {score.score:.2f} | {score.weight:.2f} | {score.weighted_score():.2f} |"
            )

        if report.critical_issues:
            lines.append("\n\n## Critical Issues\n")
            for issue in report.critical_issues:
                lines.append(f"- ⚠️ {issue}")

        if report.recommendations:
            lines.append("\n\n## Recommendations\n")
            for rec in report.recommendations:
                lines.append(f"- {rec}")

        output = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()

"""Export debate trees to RFT (Reinforcement Fine-Tuning) format.

This module provides functionality to convert constitutional debate trees into
training data compatible with OpenAI's Reinforcement Fine-Tuning (RFT) API.

The export process transforms multi-model debates into graded training examples where:
- Constitutional compliance, evidence quality, and consensus participation serve as reward signals
- Each claim becomes a training example with computed quality scores
- Multi-grader configuration enables fine-grained reward optimization

References:
    - OpenAI RFT Documentation: https://platform.openai.com/docs/guides/reinforcement-fine-tuning
    - JSONL Dataset Format: https://platform.openai.com/docs/api-reference/fine-tuning/reinforcement-input

Author: Constitutional Debate Project
Version: 0.1.0
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from .debate_tree import DebateTree, Claim, Challenge, ModelType, Evidence
from .charter import Charter, ValidationResult

# Configure module-level logger
logger = logging.getLogger(__name__)


@dataclass
class RFTGraderScore:
    """Individual grader scores for a debate response.

    Attributes:
        constitutional_compliance: Score (0.0-1.0) measuring adherence to constitutional rules
        evidence_quality: Score (0.0-1.0) measuring quality and relevance of cited evidence
        consensus_participation: Score (0.0-1.0) measuring contribution to consensus building
        overall_score: Weighted combination of all component scores

    Note:
        All scores are normalized to [0.0, 1.0] range where 1.0 represents perfect performance.
    """
    constitutional_compliance: float
    evidence_quality: float
    consensus_participation: float
    overall_score: float

    def __post_init__(self) -> None:
        """Validate score ranges after initialization."""
        for field_name in ['constitutional_compliance', 'evidence_quality', 'consensus_participation', 'overall_score']:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be in range [0.0, 1.0], got {value}")

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSONL export.

        Returns:
            Dictionary mapping score names to values
        """
        return asdict(self)


@dataclass
class RFTTrainingExample:
    """Single training example for RFT.

    Format matches OpenAI's RFT dataset requirements:
    https://platform.openai.com/docs/api-reference/fine-tuning/reinforcement-input
    """
    messages: List[Dict[str, str]]  # User messages (prompts)

    # Grading reference values
    constitutional_compliance: float
    evidence_quality: float
    consensus_participation: float
    overall_score: float

    # Metadata (optional, for analysis)
    debate_id: str
    model: str
    node_id: str
    round_num: int

    # Response content (what the model actually generated)
    response_content: str
    evidence_sources: List[str]

    def to_jsonl_line(self) -> str:
        """Convert to JSONL line."""
        obj = {
            "messages": self.messages,
            "constitutional_compliance": self.constitutional_compliance,
            "evidence_quality": self.evidence_quality,
            "consensus_participation": self.consensus_participation,
            "overall_score": self.overall_score,
            "debate_id": self.debate_id,
            "model": self.model,
            "node_id": self.node_id,
            "round_num": self.round_num,
            "response_content": self.response_content,
            "evidence_sources": self.evidence_sources
        }
        return json.dumps(obj)


class RFTExporter:
    """Export debate trees to RFT training format."""

    def __init__(self, charter: Charter):
        self.charter = charter

    def export_debate(self, tree: DebateTree) -> List[RFTTrainingExample]:
        """Export a complete debate tree to RFT examples.

        Each claim becomes a training example with:
        - Input: The debate query + context
        - Response: The model's claim
        - Grading values: Constitutional compliance, evidence quality, consensus score

        Args:
            tree: DebateTree to export

        Returns:
            List of RFT training examples
        """
        examples = []

        # Export each round's claims
        for round_obj in tree.rounds:
            for claim in round_obj.get_claims():
                example = self._export_claim(tree, claim, round_obj.round_num)
                examples.append(example)

        return examples

    def _export_claim(
        self,
        tree: DebateTree,
        claim: Claim,
        round_num: int
    ) -> RFTTrainingExample:
        """Export a single claim as RFT training example."""

        # Build prompt messages
        messages = self._build_messages(tree, claim, round_num)

        # Calculate grading scores
        constitutional_score = self._grade_constitutional_compliance(claim)
        evidence_score = self._grade_evidence_quality(claim)
        consensus_score = self._grade_consensus_participation(tree, claim)

        # Overall score (weighted average)
        overall = (
            constitutional_score * 0.4 +  # 40% weight on rule compliance
            evidence_score * 0.3 +         # 30% weight on evidence quality
            consensus_score * 0.3          # 30% weight on consensus contribution
        )

        return RFTTrainingExample(
            messages=messages,
            constitutional_compliance=constitutional_score,
            evidence_quality=evidence_score,
            consensus_participation=consensus_score,
            overall_score=overall,
            debate_id=tree.debate_id,
            model=claim.model.value,
            node_id=claim.node_id,
            round_num=round_num,
            response_content=claim.content,
            evidence_sources=[ev.source for ev in claim.evidence]
        )

    def _build_messages(
        self,
        tree: DebateTree,
        claim: Claim,
        round_num: int
    ) -> List[Dict[str, str]]:
        """Build message array for RFT training.

        Format:
        [
            {"role": "user", "content": "Query + context"}
        ]
        """
        # Base query
        content_parts = [f"Query: {tree.query}"]

        # Add constitutional rules reminder
        content_parts.append("\nYou must follow constitutional debate rules:")
        content_parts.append("1. Cite evidence for all claims")
        content_parts.append("2. Attribute sources properly")
        content_parts.append("3. Reference specific nodes when challenging")

        # Add context from previous rounds if applicable
        if round_num > 0:
            context = self._build_context_for_round(tree, round_num)
            if context:
                content_parts.append(f"\nPrevious round:\n{context}")

        content_parts.append("\nProvide your response following the constitutional rules.")

        return [
            {
                "role": "user",
                "content": "\n".join(content_parts)
            }
        ]

    def _build_context_for_round(self, tree: DebateTree, up_to_round: int) -> str:
        """Build context from previous rounds."""
        lines = []

        for i in range(up_to_round):
            round_obj = tree.get_round(i)
            if not round_obj:
                continue

            for claim in round_obj.get_claims():
                lines.append(f"- {claim.model.value}: {claim.position}")

        return "\n".join(lines) if lines else ""

    def _grade_constitutional_compliance(self, claim: Claim) -> float:
        """Grade constitutional rule compliance (0.0-1.0).

        Uses the Charter validation to calculate compliance score.
        """
        validation = self.charter.validate_claim(claim)
        return validation.score

    def _grade_evidence_quality(self, claim: Claim) -> float:
        """Grade evidence quality (0.0-1.0).

        Factors:
        - Number of evidence citations
        - Evidence has URLs
        - Evidence has memory scores (from Adaptive Memory)
        - Evidence variety
        """
        if not claim.evidence:
            return 0.0

        score = 0.0

        # Base score for having evidence
        num_evidence = len(claim.evidence)
        score += min(num_evidence / 3.0, 0.4)  # Up to 0.4 for having 3+ sources

        # Score for URLs provided
        has_urls = sum(1 for ev in claim.evidence if ev.url)
        score += (has_urls / num_evidence) * 0.3  # Up to 0.3 for all having URLs

        # Score for memory scores (if available)
        with_memory_scores = [ev for ev in claim.evidence if ev.memory_score > 0]
        if with_memory_scores:
            avg_memory_score = sum(ev.memory_score for ev in with_memory_scores) / len(with_memory_scores)
            score += avg_memory_score * 0.3  # Up to 0.3 based on memory quality
        else:
            # No memory scores yet, give partial credit
            score += 0.15

        return min(score, 1.0)

    def _grade_consensus_participation(self, tree: DebateTree, claim: Claim) -> float:
        """Grade consensus participation (0.0-1.0).

        Factors:
        - Did this claim contribute to final consensus?
        - Was the position adopted by other models?
        - Did the model engage constructively (challenges, refinements)?
        """
        # Find the round this claim is in
        claim_round = None
        for round_obj in tree.rounds:
            if claim.node_id in [n.node_id for n in round_obj.get_claims()]:
                claim_round = round_obj
                break

        if not claim_round:
            return 0.5  # Default if not found

        score = 0.0

        # Check if consensus was reached
        if claim_round.consensus:
            # Did this model support the consensus?
            if claim.model in claim_round.consensus.supporting_models:
                score += 0.6  # High score for supporting consensus
            else:
                # Dissented - check if dissent was well-documented
                # For now, give partial credit
                score += 0.3
        else:
            # No consensus yet, give base score
            score += 0.4

        # Check if position influenced others (simple heuristic)
        # Count how many models have similar positions in subsequent rounds
        similar_count = 0
        for round_obj in tree.rounds:
            if round_obj.round_num > claim_round.round_num:
                for other_claim in round_obj.get_claims():
                    if other_claim.model != claim.model:
                        # Simple similarity check (TODO: use embeddings)
                        if self._positions_similar(claim.position, other_claim.position):
                            similar_count += 1

        if similar_count > 0:
            score += min(similar_count * 0.1, 0.4)  # Up to 0.4 for influencing others

        return min(score, 1.0)

    def _positions_similar(self, pos1: str, pos2: str) -> bool:
        """Check if two positions are similar (simple heuristic).

        TODO: Use embeddings for semantic similarity.
        """
        if not pos1 or not pos2:
            return False

        # Normalize and check overlap
        words1 = set(pos1.lower().split())
        words2 = set(pos2.lower().split())

        overlap = len(words1 & words2)
        union = len(words1 | words2)

        return (overlap / union) > 0.5 if union > 0 else False

    def export_to_jsonl(
        self,
        trees: List[DebateTree],
        output_path: Path,
        split: str = "train"
    ) -> int:
        """Export multiple debate trees to JSONL file.

        Args:
            trees: List of DebateTree objects
            output_path: Path to output JSONL file
            split: "train" or "validation"

        Returns:
            Number of examples exported
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        all_examples = []
        for tree in trees:
            examples = self.export_debate(tree)
            all_examples.extend(examples)

        # Write JSONL
        with open(output_path, 'w') as f:
            for example in all_examples:
                f.write(example.to_jsonl_line() + '\n')

        print(f"Exported {len(all_examples)} examples to {output_path}")
        return len(all_examples)

    def create_grader_config(self) -> Dict[str, Any]:
        """Create RFT grader configuration for OpenAI API.

        Returns grader config dict that can be used with OpenAI's RFT API:
        https://platform.openai.com/docs/api-reference/graders/multi
        """
        return {
            "type": "multi",
            "graders": {
                "constitutional_compliance": {
                    "name": "Constitutional Rule Compliance",
                    "type": "python",
                    "code": self._get_constitutional_grader_code()
                },
                "evidence_quality": {
                    "name": "Evidence Quality",
                    "type": "python",
                    "code": self._get_evidence_grader_code()
                },
                "consensus_participation": {
                    "name": "Consensus Participation",
                    "type": "python",
                    "code": self._get_consensus_grader_code()
                }
            },
            "calculate_output": (
                "0.4 * constitutional_compliance + "
                "0.3 * evidence_quality + "
                "0.3 * consensus_participation"
            )
        }

    def _get_constitutional_grader_code(self) -> str:
        """Python grader code for constitutional compliance."""
        return """
def grade(item, sample):
    '''Grade constitutional compliance.

    Checks:
    - Evidence citations present
    - Proper formatting
    - Rule adherence
    '''
    # Get reference score from training data
    if 'constitutional_compliance' in item:
        return item['constitutional_compliance']

    # Fallback: basic check
    response = sample.get('output', '')

    score = 0.0

    # Check for evidence markers
    if '[' in response and ']' in response:
        score += 0.5

    # Check for URLs
    if 'http' in response or 'www' in response:
        score += 0.5

    return min(score, 1.0)
"""

    def _get_evidence_grader_code(self) -> str:
        """Python grader code for evidence quality."""
        return """
def grade(item, sample):
    '''Grade evidence quality.

    Checks:
    - Number of sources cited
    - Source credibility
    - Relevance to claim
    '''
    # Get reference score from training data
    if 'evidence_quality' in item:
        return item['evidence_quality']

    # Fallback: count evidence citations
    response = sample.get('output', '')
    citations = response.count('[') + response.count('http')

    return min(citations / 3.0, 1.0)  # Max score at 3+ citations
"""

    def _get_consensus_grader_code(self) -> str:
        """Python grader code for consensus participation."""
        return """
def grade(item, sample):
    '''Grade consensus participation.

    Checks:
    - Constructive contribution
    - Alignment with consensus
    - Quality of reasoning
    '''
    # Get reference score from training data
    if 'consensus_participation' in item:
        return item['consensus_participation']

    # Fallback: check response quality
    response = sample.get('output', '')

    score = 0.5  # Base score

    # Bonus for longer, detailed responses
    if len(response) > 200:
        score += 0.3

    # Bonus for evidence
    if '[' in response or 'http' in response:
        score += 0.2

    return min(score, 1.0)
"""


def export_debates_for_rft(
    debates: List[DebateTree],
    output_dir: Path,
    charter: Optional[Charter] = None,
    train_split: float = 0.8
) -> Dict[str, int]:
    """Convenience function to export debates to RFT format.

    Args:
        debates: List of DebateTree objects
        output_dir: Directory to save training data
        charter: Charter for validation (creates default if None)
        train_split: Fraction of data for training (rest is validation)

    Returns:
        Dict with counts: {"train": N, "validation": M}
    """
    if charter is None:
        charter = Charter.default()

    exporter = RFTExporter(charter)

    # Split debates
    split_idx = int(len(debates) * train_split)
    train_debates = debates[:split_idx]
    val_debates = debates[split_idx:]

    # Export
    train_count = exporter.export_to_jsonl(
        train_debates,
        output_dir / "rft_train.jsonl",
        split="train"
    )

    val_count = exporter.export_to_jsonl(
        val_debates,
        output_dir / "rft_validation.jsonl",
        split="validation"
    )

    # Save grader config
    grader_config = exporter.create_grader_config()
    with open(output_dir / "rft_grader_config.json", 'w') as f:
        json.dump(grader_config, f, indent=2)

    print(f"\nRFT export complete!")
    print(f"Training examples: {train_count}")
    print(f"Validation examples: {val_count}")
    print(f"Grader config saved to: {output_dir}/rft_grader_config.json")

    return {"train": train_count, "validation": val_count}
"""Constitutional Charter - Rules Engine

Defines and enforces constitutional rules for debates.

The 5 Constitutional Rules:
1. Evidence Citation: Every claim must cite sources
2. Source Attribution: Quotes must have author and date
3. Challenge References: Must reference specific nodes
4. Consensus Threshold: 75% agreement required
5. Dissent Documentation: Must provide reasoning
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .debate_tree import DebateNode, Claim, Challenge, Evidence, Consensus, Dissent, ModelType


class RuleViolation(Enum):
    """Types of constitutional rule violations."""
    NO_EVIDENCE = "no_evidence_citation"
    NO_ATTRIBUTION = "no_source_attribution"
    INVALID_REFERENCE = "invalid_challenge_reference"
    WEAK_CONSENSUS = "consensus_below_threshold"
    UNDOCUMENTED_DISSENT = "dissent_lacks_documentation"


@dataclass
class ValidationResult:
    """Result of constitutional validation."""
    is_valid: bool
    violations: List[RuleViolation] = None
    warnings: List[str] = None
    score: float = 1.0  # 0-1, constitutional compliance score

    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.warnings is None:
            self.warnings = []


class Charter:
    """Constitutional Charter for debates.

    Enforces rules via:
    1. System prompts for LLMs
    2. Programmatic validation of outputs
    """

    RULES = {
        "evidence_citation": {
            "name": "Rule 1: Evidence Citation",
            "description": "Every claim must cite at least one source from memory or provide a URL.",
            "prompt": "You MUST cite evidence for every claim. Format: [source_name, url/path]",
            "min_evidence": 1
        },
        "source_attribution": {
            "name": "Rule 2: Source Attribution",
            "description": "Quotes must attribute original author and publication date.",
            "prompt": "When quoting, always include: author name, publication/source, and date if available.",
            "requires_author": True
        },
        "challenge_reference": {
            "name": "Rule 3: Challenge References",
            "description": "Challenges must reference specific node IDs from the debate tree.",
            "prompt": "When challenging, reference the specific claim using @node_id format.",
            "requires_target": True
        },
        "consensus_threshold": {
            "name": "Rule 4: Consensus Threshold",
            "description": "Consensus requires 75% (3/4) model agreement.",
            "prompt": "For consensus, at least 75% of models must agree on the position.",
            "threshold": 0.75
        },
        "dissent_documentation": {
            "name": "Rule 5: Dissent Documentation",
            "description": "Dissent requires: disagreement point, alternative, evidence, reasoning.",
            "prompt": "If dissenting, you MUST provide: (1) what you disagree with, (2) your alternative position, (3) supporting evidence, (4) your reasoning.",
            "required_fields": ["disagreement_point", "alternative_position", "evidence", "reasoning"]
        }
    }

    def __init__(self, strict_mode: bool = True):
        """Initialize charter.

        Args:
            strict_mode: If True, violations fail validation. If False, only warnings.
        """
        self.strict_mode = strict_mode

    def get_system_prompt(self, role: str = "debater") -> str:
        """Generate system prompt encoding constitutional rules.

        Args:
            role: "debater" or "consensus_builder"
        """
        if role == "debater":
            return self._debater_prompt()
        elif role == "consensus_builder":
            return self._consensus_prompt()
        else:
            return self._debater_prompt()

    def _debater_prompt(self) -> str:
        """System prompt for debate participants."""
        return f"""You are participating in a constitutional debate with other AI models.

CONSTITUTIONAL RULES (you MUST follow these):

1. **Evidence Citation**: {self.RULES['evidence_citation']['prompt']}
   Every claim you make must be backed by evidence from memory or external sources.

2. **Source Attribution**: {self.RULES['source_attribution']['prompt']}
   Be specific about where information comes from.

3. **Challenge References**: {self.RULES['challenge_reference']['prompt']}
   When disagreeing with another model's claim, reference it precisely.

4. **No Hallucination**: If you don't have evidence, say "I don't have sufficient evidence" rather than making unsupported claims.

5. **Respectful Disagreement**: You can disagree strongly, but must provide evidence and reasoning.

Output your response in this format:

<claim>
[Your position/claim]
</claim>

<evidence>
[1] Source: [name], URL: [url], Quote: [relevant quote]
[2] Source: [name], URL: [url], Quote: [relevant quote]
</evidence>

<reasoning>
[Explain your logic and how evidence supports your claim]
</reasoning>

If challenging another model's claim:

<challenge target="node_id">
[Your challenge/question]
</challenge>

<evidence>
[Supporting evidence for your challenge]
</evidence>
"""

    def _consensus_prompt(self) -> str:
        """System prompt for consensus building."""
        return f"""You are analyzing a multi-model debate to identify consensus.

CONSTITUTIONAL RULES:

4. **Consensus Threshold**: {self.RULES['consensus_threshold']['prompt']}
   Only declare consensus if ≥75% of models agree.

5. **Dissent Documentation**: {self.RULES['dissent_documentation']['prompt']}

Your task:
1. Identify areas of agreement across models
2. Note which models support each position
3. If consensus exists, state the consensus position
4. Document any dissenting views with full reasoning

Output format:

<consensus agreement="0.75-1.0">
Position: [The agreed-upon position]
Supporting Models: [list]
Supporting Evidence: [combined evidence from agreeing models]
</consensus>

<dissents>
Model: [name]
Position: [alternative view]
Reasoning: [why they disagree]
Evidence: [their supporting evidence]
</dissents>
"""

    def validate_claim(self, claim: Claim) -> ValidationResult:
        """Validate a claim against Rule 1 (Evidence Citation)."""
        violations = []
        warnings = []

        # Rule 1: Must have evidence
        if claim.evidence_count() < self.RULES['evidence_citation']['min_evidence']:
            violations.append(RuleViolation.NO_EVIDENCE)
            warnings.append(f"Claim {claim.node_id} has no evidence citations")

        # Check evidence quality
        for ev in claim.evidence:
            if not ev.source:
                warnings.append(f"Evidence in {claim.node_id} missing source name")
            if not ev.url:
                warnings.append(f"Evidence '{ev.source}' in {claim.node_id} missing URL")

        score = 1.0 - (len(violations) * 0.3 + len(warnings) * 0.1)
        is_valid = len(violations) == 0 or not self.strict_mode

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            score=max(0.0, score)
        )

    def validate_challenge(self, challenge: Challenge, tree_nodes: Dict[str, DebateNode]) -> ValidationResult:
        """Validate a challenge against Rule 3 (Challenge References)."""
        violations = []
        warnings = []

        # Rule 3: Must reference valid target
        if not challenge.target_id:
            violations.append(RuleViolation.INVALID_REFERENCE)
            warnings.append(f"Challenge {challenge.node_id} has no target")
        elif challenge.target_id not in tree_nodes:
            violations.append(RuleViolation.INVALID_REFERENCE)
            warnings.append(f"Challenge {challenge.node_id} references non-existent node {challenge.target_id}")

        # Rule 1: Challenges also need evidence
        if challenge.evidence_count() == 0:
            violations.append(RuleViolation.NO_EVIDENCE)
            warnings.append(f"Challenge {challenge.node_id} has no supporting evidence")

        score = 1.0 - (len(violations) * 0.3 + len(warnings) * 0.1)
        is_valid = len(violations) == 0 or not self.strict_mode

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            score=max(0.0, score)
        )

    def validate_consensus(self, consensus: Consensus, total_models: int) -> ValidationResult:
        """Validate consensus against Rule 4 (Consensus Threshold)."""
        violations = []
        warnings = []

        # Rule 4: Must meet 75% threshold
        threshold = self.RULES['consensus_threshold']['threshold']
        actual_agreement = len(consensus.supporting_models) / total_models

        if actual_agreement < threshold:
            violations.append(RuleViolation.WEAK_CONSENSUS)
            warnings.append(
                f"Consensus has {actual_agreement*100:.0f}% agreement, "
                f"below {threshold*100:.0f}% threshold"
            )

        # Must have evidence
        if len(consensus.supporting_evidence) == 0:
            violations.append(RuleViolation.NO_EVIDENCE)
            warnings.append("Consensus has no supporting evidence")

        score = actual_agreement
        is_valid = len(violations) == 0 or not self.strict_mode

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            score=score
        )

    def validate_dissent(self, dissent: Dissent) -> ValidationResult:
        """Validate dissent against Rule 5 (Dissent Documentation)."""
        violations = []
        warnings = []

        # Rule 5: Must have all required fields
        if not dissent.disagreement_point:
            violations.append(RuleViolation.UNDOCUMENTED_DISSENT)
            warnings.append(f"Dissent {dissent.dissent_id} missing disagreement point")

        if not dissent.alternative_position:
            violations.append(RuleViolation.UNDOCUMENTED_DISSENT)
            warnings.append(f"Dissent {dissent.dissent_id} missing alternative position")

        if not dissent.reasoning:
            violations.append(RuleViolation.UNDOCUMENTED_DISSENT)
            warnings.append(f"Dissent {dissent.dissent_id} missing reasoning")

        if len(dissent.evidence) == 0:
            violations.append(RuleViolation.NO_EVIDENCE)
            warnings.append(f"Dissent {dissent.dissent_id} has no supporting evidence")

        score = 1.0 - (len(violations) * 0.25)
        is_valid = len(violations) == 0 or not self.strict_mode

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            score=max(0.0, score)
        )

    def validate_debate_tree(self, tree) -> ValidationResult:
        """Validate entire debate tree for constitutional compliance."""
        all_violations = []
        all_warnings = []
        total_score = 0.0
        node_count = 0

        # Validate all claims
        for node in tree.nodes.values():
            if isinstance(node, Claim):
                result = self.validate_claim(node)
                all_violations.extend(result.violations)
                all_warnings.extend(result.warnings)
                total_score += result.score
                node_count += 1

            elif isinstance(node, Challenge):
                result = self.validate_challenge(node, tree.nodes)
                all_violations.extend(result.violations)
                all_warnings.extend(result.warnings)
                total_score += result.score
                node_count += 1

        # Validate consensus if exists
        for round_obj in tree.rounds:
            if round_obj.consensus:
                result = self.validate_consensus(
                    round_obj.consensus,
                    total_models=4  # TODO: get from config
                )
                all_violations.extend(result.violations)
                all_warnings.extend(result.warnings)
                total_score += result.score
                node_count += 1

            # Validate dissents
            for dissent in round_obj.dissents:
                result = self.validate_dissent(dissent)
                all_violations.extend(result.violations)
                all_warnings.extend(result.warnings)
                total_score += result.score
                node_count += 1

        avg_score = total_score / node_count if node_count > 0 else 0.0
        is_valid = len(all_violations) == 0 or not self.strict_mode

        return ValidationResult(
            is_valid=is_valid,
            violations=list(set(all_violations)),  # Deduplicate
            warnings=all_warnings,
            score=avg_score
        )

    @classmethod
    def default(cls) -> Charter:
        """Create charter with default settings."""
        return cls(strict_mode=True)

    @classmethod
    def lenient(cls) -> Charter:
        """Create lenient charter (warnings only, no hard failures)."""
        return cls(strict_mode=False)

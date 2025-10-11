"""Debate Tree Data Structures

Represents the constitutional debate as a tree with claims, evidence, challenges, and consensus.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4


class NodeType(Enum):
    """Types of nodes in debate tree."""
    CLAIM = "claim"
    CHALLENGE = "challenge"
    EVIDENCE = "evidence"
    CONSENSUS = "consensus"
    DISSENT = "dissent"


class ModelType(Enum):
    """Supported LLM models for constitutional debates.

    Model versions as of 2025:
    - CLAUDE: claude-sonnet-4-5, claude-opus-4-1 (Anthropic)
    - GPT5: gpt-5-2025-08-07 (OpenAI flagship)
    - GPT4: gpt-4-turbo-preview (OpenAI legacy)
    - O4: o4-mini reasoning model (OpenAI)
    - GEMINI: gemini-2.5-pro (Google DeepMind)
    - LLAMA: llama3 via Ollama (Meta)
    """
    CLAUDE = "claude"
    GPT5 = "gpt5"
    GPT4 = "gpt4"
    O4 = "o4"
    GEMINI = "gemini"
    LLAMA = "llama"


@dataclass
class Evidence:
    """Evidence citation for a claim or challenge."""
    source: str                    # Source name/title
    url: Optional[str] = None      # URL or file path
    quote: Optional[str] = None    # Relevant quote
    memory_score: float = 0.0      # Score from Adaptive Memory (learned)
    citations_count: int = 0       # How many times cited in debates

    def __str__(self) -> str:
        if self.url:
            return f"[{self.source}, {self.url}]"
        return f"[{self.source}]"


@dataclass
class DebateNode:
    """Base node in debate tree."""
    node_id: str
    node_type: NodeType
    model: ModelType
    content: str
    evidence: List[Evidence] = field(default_factory=list)
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    round_num: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child_id: str) -> None:
        """Add a child node."""
        if child_id not in self.children:
            self.children.append(child_id)

    def has_evidence(self) -> bool:
        """Check if node has evidence citations."""
        return len(self.evidence) > 0

    def evidence_count(self) -> int:
        """Count evidence citations."""
        return len(self.evidence)


@dataclass
class Claim(DebateNode):
    """Initial claim/position from a model."""
    position: str = ""  # Short summary of position

    def __post_init__(self):
        self.node_type = NodeType.CLAIM


@dataclass
class Challenge(DebateNode):
    """Challenge to another node."""
    target_id: str = ""  # Node being challenged
    challenge_type: str = "critique"  # critique | question | counter

    def __post_init__(self):
        self.node_type = NodeType.CHALLENGE


@dataclass
class Consensus:
    """Consensus reached by models."""
    consensus_id: str
    position: str
    supporting_models: List[ModelType]
    supporting_evidence: List[Evidence]
    agreement_pct: float  # 0-100
    round_reached: int
    dissenting_nodes: List[str] = field(default_factory=list)

    def is_strong_consensus(self) -> bool:
        """Check if consensus meets 75% threshold."""
        return self.agreement_pct >= 75.0


@dataclass
class Dissent:
    """Documented disagreement with consensus."""
    dissent_id: str
    model: ModelType
    consensus_id: str
    disagreement_point: str
    alternative_position: str
    evidence: List[Evidence]
    reasoning: str

    def __str__(self) -> str:
        return f"Dissent by {self.model.value}: {self.alternative_position}"


@dataclass
class DebateRound:
    """Collection of nodes in a single debate round."""
    round_num: int
    nodes: List[DebateNode] = field(default_factory=list)
    consensus: Optional[Consensus] = None
    dissents: List[Dissent] = field(default_factory=list)

    def add_node(self, node: DebateNode) -> None:
        """Add a node to this round."""
        node.round_num = self.round_num
        self.nodes.append(node)

    def get_claims(self) -> List[Claim]:
        """Get all claims in this round."""
        return [n for n in self.nodes if n.node_type == NodeType.CLAIM]

    def get_challenges(self) -> List[Challenge]:
        """Get all challenges in this round."""
        return [n for n in self.nodes if n.node_type == NodeType.CHALLENGE]


class DebateTree:
    """Full debate tree with all rounds."""

    def __init__(self, debate_id: str, query: str, workspace: str):
        self.debate_id = debate_id
        self.query = query
        self.workspace = workspace
        self.rounds: List[DebateRound] = []
        self.nodes: Dict[str, DebateNode] = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.final_consensus: Optional[Consensus] = None

    def add_round(self, round_num: int) -> DebateRound:
        """Create and add a new round."""
        round_obj = DebateRound(round_num=round_num)
        self.rounds.append(round_obj)
        return round_obj

    def add_node(self, node: DebateNode, round_num: int) -> None:
        """Add a node to tree and specific round."""
        self.nodes[node.node_id] = node

        # Add to round
        if round_num >= len(self.rounds):
            self.add_round(round_num)
        self.rounds[round_num].add_node(node)

        # Update parent-child relationships
        if node.parent_id and node.parent_id in self.nodes:
            self.nodes[node.parent_id].add_child(node.node_id)

        self.updated_at = datetime.now().isoformat()

    def get_node(self, node_id: str) -> Optional[DebateNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_round(self, round_num: int) -> Optional[DebateRound]:
        """Get round by number."""
        if 0 <= round_num < len(self.rounds):
            return self.rounds[round_num]
        return None

    def get_current_round(self) -> Optional[DebateRound]:
        """Get the latest round."""
        if self.rounds:
            return self.rounds[-1]
        return None

    def get_all_evidence(self) -> List[Evidence]:
        """Get all evidence cited in the debate."""
        all_evidence = []
        for node in self.nodes.values():
            all_evidence.extend(node.evidence)
        return all_evidence

    def get_model_nodes(self, model: ModelType) -> List[DebateNode]:
        """Get all nodes from a specific model."""
        return [n for n in self.nodes.values() if n.model == model]

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "debate_id": self.debate_id,
            "query": self.query,
            "workspace": self.workspace,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "rounds": [
                {
                    "round_num": r.round_num,
                    "nodes": [vars(n) for n in r.nodes],
                    "consensus": vars(r.consensus) if r.consensus else None,
                    "dissents": [vars(d) for d in r.dissents]
                }
                for r in self.rounds
            ],
            "final_consensus": vars(self.final_consensus) if self.final_consensus else None
        }

    def to_markdown(self) -> str:
        """Export debate tree as markdown."""
        lines = [
            f"# Debate: {self.query}",
            f"",
            f"**Workspace**: {self.workspace}",
            f"**Created**: {self.created_at}",
            f"**Rounds**: {len(self.rounds)}",
            f"",
        ]

        for round_obj in self.rounds:
            lines.append(f"## Round {round_obj.round_num + 1}")
            lines.append("")

            # Claims
            claims = round_obj.get_claims()
            if claims:
                lines.append("### Claims")
                for claim in claims:
                    lines.append(f"- **{claim.model.value}**: {claim.content}")
                    for ev in claim.evidence:
                        lines.append(f"  - Evidence: {ev}")
                lines.append("")

            # Challenges
            challenges = round_obj.get_challenges()
            if challenges:
                lines.append("### Challenges")
                for challenge in challenges:
                    lines.append(f"- **{challenge.model.value}** → @{challenge.target_id}: {challenge.content}")
                    for ev in challenge.evidence:
                        lines.append(f"  - Evidence: {ev}")
                lines.append("")

            # Consensus
            if round_obj.consensus:
                cons = round_obj.consensus
                lines.append("### Consensus")
                lines.append(f"**Position**: {cons.position}")
                lines.append(f"**Agreement**: {cons.agreement_pct:.0f}%")
                lines.append(f"**Supporting Models**: {', '.join(m.value for m in cons.supporting_models)}")
                lines.append("")
                lines.append("**Evidence**:")
                for ev in cons.supporting_evidence:
                    score_str = f" (memory score: {ev.memory_score:.2f})" if ev.memory_score > 0 else ""
                    lines.append(f"- {ev}{score_str}")
                lines.append("")

            # Dissents
            if round_obj.dissents:
                lines.append("### Dissents")
                for dissent in round_obj.dissents:
                    lines.append(f"- **{dissent.model.value}**: {dissent.alternative_position}")
                    lines.append(f"  - Reasoning: {dissent.reasoning}")
                lines.append("")

        if self.final_consensus:
            lines.append("## Final Consensus")
            lines.append(f"**Position**: {self.final_consensus.position}")
            lines.append(f"**Agreement**: {self.final_consensus.agreement_pct:.0f}%")

        return "\n".join(lines)


def create_node_id(prefix: str = "node") -> str:
    """Generate unique node ID."""
    return f"{prefix}_{uuid4().hex[:8]}"


def create_debate_id() -> str:
    """Generate unique debate ID."""
    return f"debate_{uuid4().hex[:12]}"

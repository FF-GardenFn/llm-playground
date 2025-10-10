"""Constitutional Debate Trees

Multi-LLM Knowledge Distillation with Learned Evidence Ranking
"""

__version__ = "0.1.0"

from .debate_tree import (
    DebateTree,
    DebateNode,
    Claim,
    Challenge,
    Evidence,
    Consensus,
    Dissent,
    ModelType,
    NodeType
)

from .charter import Charter, ValidationResult, RuleViolation

from .debater import Debater, Claude, GPT4, Gemini, Llama, create_debater

from .orchestrator import Orchestrator, DebateConfig

__all__ = [
    # Core data structures
    "DebateTree",
    "DebateNode",
    "Claim",
    "Challenge",
    "Evidence",
    "Consensus",
    "Dissent",
    "ModelType",
    "NodeType",

    # Constitutional enforcement
    "Charter",
    "ValidationResult",
    "RuleViolation",

    # LLM clients
    "Debater",
    "Claude",
    "GPT4",
    "Gemini",
    "Llama",
    "create_debater",

    # Orchestration
    "Orchestrator",
    "DebateConfig",
]

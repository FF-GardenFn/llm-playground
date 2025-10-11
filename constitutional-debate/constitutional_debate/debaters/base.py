"""Base debater class and shared helpers.

Defines the abstract Debater interface common to all model clients.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..debate_tree import Evidence, Claim, Challenge
from ..charter import Charter
from ..config import Config, ModelConfig


class Debater(ABC):
    """Abstract base class for LLM debaters."""

    def __init__(self, model_config: ModelConfig, config: Config, charter: Charter):
        self.model_config = model_config
        self.config = config
        self.charter = charter

    @abstractmethod
    async def generate_claim(self, query: str, context: Optional[str] = None, evidence_pool: Optional[List[Evidence]] = None) -> Claim:
        """Generate an initial claim for the query."""
        raise NotImplementedError

    @abstractmethod
    async def generate_challenge(self, target_claim: Claim, context: Optional[str] = None, evidence_pool: Optional[List[Evidence]] = None) -> Optional[Challenge]:
        """Generate a challenge to another model's claim."""
        raise NotImplementedError

    def _get_system_prompt(self) -> str:
        """Get constitutional system prompt."""
        return self.charter.get_system_prompt(role="debater")

    def _format_evidence_pool(self, evidence_pool: Optional[List[Evidence]]) -> str:
        """Format evidence pool for inclusion in prompts."""
        if not evidence_pool:
            return "No evidence available in memory."

        lines = ["Available evidence from memory:\n"]
        for i, ev in enumerate(evidence_pool, 1):
            score_str = f" (relevance: {ev.memory_score:.2f})" if ev.memory_score > 0 else ""
            lines.append(f"{i}. {ev.source}{score_str}")
            if ev.url:
                lines.append(f"   URL: {ev.url}")
            if ev.quote:
                lines.append(f"   Quote: {ev.quote}")

        return "\n".join(lines)

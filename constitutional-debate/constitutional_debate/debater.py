"""LLM Client Abstractions

Wraps different LLM APIs (Claude, GPT, Gemini, Llama) with a common interface.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .debate_tree import ModelType, Evidence, Claim, Challenge
from .charter import Charter


@dataclass
class DebaterConfig:
    """Configuration for a debater."""
    model_type: ModelType
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60


class Debater(ABC):
    """Abstract base class for LLM debaters."""

    def __init__(self, config: DebaterConfig, charter: Charter):
        self.config = config
        self.charter = charter
        self.model_type = config.model_type

    @abstractmethod
    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate an initial claim for the query.

        Args:
            query: The debate question
            context: Optional context from previous rounds
            evidence_pool: Available evidence from memory

        Returns:
            Claim with evidence citations
        """
        pass

    @abstractmethod
    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate a challenge to another model's claim.

        Args:
            target_claim: Claim to potentially challenge
            context: Context from debate so far
            evidence_pool: Available evidence

        Returns:
            Challenge if disagreement exists, None if agreement
        """
        pass

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


class Claude(Debater):
    """Claude (Anthropic) debater."""

    def __init__(self, config: Optional[DebaterConfig] = None, charter: Optional[Charter] = None):
        if config is None:
            config = DebaterConfig(
                model_type=ModelType.CLAUDE,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        if charter is None:
            charter = Charter.default()

        super().__init__(config, charter)

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate claim using Claude API."""
        # TODO: Implement actual Anthropic API call
        # For now, return stub

        from .debate_tree import create_node_id

        prompt = f"""Query: {query}

{self._format_evidence_pool(evidence_pool)}

{context if context else ''}

Generate your claim following the constitutional rules."""

        # TODO: Call Anthropic API with system_prompt and prompt
        # response = await self._call_anthropic_api(prompt)

        # Stub response
        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.CLAUDE,
            content="[TODO: Implement Claude API call]",
            evidence=[],
            position="Placeholder claim"
        )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate challenge using Claude API."""
        # TODO: Implement actual challenge generation
        return None


class GPT4(Debater):
    """GPT-4 (OpenAI) debater."""

    def __init__(self, config: Optional[DebaterConfig] = None, charter: Optional[Charter] = None):
        if config is None:
            config = DebaterConfig(
                model_type=ModelType.GPT4,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        if charter is None:
            charter = Charter.default()

        super().__init__(config, charter)

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate claim using GPT-4 API."""
        from .debate_tree import create_node_id

        # TODO: Implement OpenAI API call

        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.GPT4,
            content="[TODO: Implement GPT-4 API call]",
            evidence=[],
            position="Placeholder claim"
        )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate challenge using GPT-4 API."""
        return None


class Gemini(Debater):
    """Gemini (Google) debater."""

    def __init__(self, config: Optional[DebaterConfig] = None, charter: Optional[Charter] = None):
        if config is None:
            config = DebaterConfig(
                model_type=ModelType.GEMINI,
                api_key=os.getenv("GOOGLE_API_KEY")
            )
        if charter is None:
            charter = Charter.default()

        super().__init__(config, charter)

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate claim using Gemini API."""
        from .debate_tree import create_node_id

        # TODO: Implement Google Gemini API call

        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.GEMINI,
            content="[TODO: Implement Gemini API call]",
            evidence=[],
            position="Placeholder claim"
        )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate challenge using Gemini API."""
        return None


class Llama(Debater):
    """Llama (Local) debater."""

    def __init__(self, config: Optional[DebaterConfig] = None, charter: Optional[Charter] = None):
        if config is None:
            config = DebaterConfig(
                model_type=ModelType.LLAMA,
                api_key=None  # Local model
            )
        if charter is None:
            charter = Charter.default()

        super().__init__(config, charter)

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate claim using local Llama."""
        from .debate_tree import create_node_id

        # TODO: Implement local Llama inference (ollama, llama.cpp, etc.)

        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.LLAMA,
            content="[TODO: Implement Llama local inference]",
            evidence=[],
            position="Placeholder claim"
        )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate challenge using local Llama."""
        return None


def create_debater(model_type: ModelType, charter: Optional[Charter] = None) -> Debater:
    """Factory function to create debaters."""
    if charter is None:
        charter = Charter.default()

    if model_type == ModelType.CLAUDE:
        return Claude(charter=charter)
    elif model_type == ModelType.GPT4:
        return GPT4(charter=charter)
    elif model_type == ModelType.GEMINI:
        return Gemini(charter=charter)
    elif model_type == ModelType.LLAMA:
        return Llama(charter=charter)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

"""LLM Client Implementations

Real API calls to Claude, GPT-4, Gemini with response parsing.
"""
from __future__ import annotations

import re
import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from .debate_tree import ModelType, Evidence, Claim, Challenge, create_node_id
from .charter import Charter
from .config import Config, ModelConfig


def parse_evidence(text: str) -> List[Evidence]:
    """Parse evidence citations from LLM response.

    Looks for formats like:
    - [Source Name, url]
    - [1] Source: X, URL: Y
    - Evidence: [source] (url)
    """
    evidence_list = []

    # Pattern 1: [Source, URL]
    pattern1 = r'\[([^\]]+),\s*([^\]]+)\]'
    matches = re.findall(pattern1, text)
    for source, url in matches:
        source = source.strip()
        url = url.strip()
        if source and ('http' in url or 'www' in url):
            evidence_list.append(Evidence(source=source, url=url))

    # Pattern 2: [N] Source: X, URL: Y
    pattern2 = r'\[\d+\]\s*Source:\s*([^,]+),\s*URL:\s*([^\n]+)'
    matches = re.findall(pattern2, text)
    for source, url in matches:
        source = source.strip()
        url = url.strip()
        evidence_list.append(Evidence(source=source, url=url))

    # Pattern 3: Evidence: [source] (url)
    pattern3 = r'Evidence:\s*\[([^\]]+)\]\s*\(([^\)]+)\)'
    matches = re.findall(pattern3, text)
    for source, url in matches:
        source = source.strip()
        url = url.strip()
        evidence_list.append(Evidence(source=source, url=url))

    return evidence_list


def extract_claim_content(text: str) -> str:
    """Extract claim from <claim> tags or just use full text."""
    # Try to find <claim>...</claim>
    match = re.search(r'<claim>(.*?)</claim>', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Try to find first substantial paragraph
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        return lines[0]

    return text.strip()


class Debater(ABC):
    """Abstract base class for LLM debaters."""

    def __init__(self, model_config: ModelConfig, config: Config, charter: Charter):
        self.model_config = model_config
        self.config = config
        self.charter = charter

    @abstractmethod
    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate an initial claim for the query."""
        pass

    @abstractmethod
    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate a challenge to another model's claim."""
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
    """Claude (Anthropic) debater with real API calls."""

    def __init__(self, model_config: ModelConfig, config: Config, charter: Charter):
        super().__init__(model_config, config, charter)

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self.model_type = ModelType.CLAUDE

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate claim using Claude API."""

        prompt = f"""Query: {query}

{self._format_evidence_pool(evidence_pool)}

{context if context else ''}

Generate your claim following the constitutional rules. Provide:
1. Your position/claim
2. Evidence citations in format: [Source Name, URL]
3. Your reasoning

Be specific and cite sources."""

        try:
            response = await self.client.messages.create(
                model=self.model_config.model,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                system=self._get_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text

            # Parse response
            claim_text = extract_claim_content(content)
            evidence = parse_evidence(content)

            # Extract position (first sentence or first line)
            position = claim_text.split('.')[0] if '.' in claim_text else claim_text[:100]

            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.CLAUDE,
                content=claim_text,
                evidence=evidence,
                position=position
            )

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            # Return fallback claim
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.CLAUDE,
                content=f"Error generating claim: {str(e)}",
                evidence=[],
                position="Error"
            )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate challenge using Claude API."""

        prompt = f"""You are reviewing this claim from {target_claim.model.value}:

Claim: {target_claim.content}
Evidence: {[str(e) for e in target_claim.evidence]}

{self._format_evidence_pool(evidence_pool)}

{context if context else ''}

Do you agree or disagree with this claim? If you disagree:
1. State your challenge
2. Provide evidence supporting your challenge
3. Reference the specific claim using @{target_claim.node_id}

If you agree, respond with "AGREE"."""

        try:
            response = await self.client.messages.create(
                model=self.model_config.model,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                system=self._get_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text

            # Check if agrees
            if "AGREE" in content.upper() and len(content) < 100:
                return None

            # Parse challenge
            challenge_text = extract_claim_content(content)
            evidence = parse_evidence(content)

            return Challenge(
                node_id=create_node_id("challenge"),
                model=ModelType.CLAUDE,
                content=challenge_text,
                evidence=evidence,
                target_id=target_claim.node_id,
                challenge_type="critique"
            )

        except Exception as e:
            print(f"Error calling Claude API for challenge: {e}")
            return None


class GPT4(Debater):
    """GPT-4 (OpenAI) debater with real API calls."""

    def __init__(self, model_config: ModelConfig, config: Config, charter: Charter):
        super().__init__(model_config, config, charter)

        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")

        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model_type = ModelType.GPT4

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """Generate claim using GPT-4 API."""

        prompt = f"""Query: {query}

{self._format_evidence_pool(evidence_pool)}

{context if context else ''}

Generate your claim following the constitutional rules. Provide:
1. Your position/claim
2. Evidence citations in format: [Source Name, URL]
3. Your reasoning

Be specific and cite sources."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model_config.model,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content

            # Parse response
            claim_text = extract_claim_content(content)
            evidence = parse_evidence(content)

            position = claim_text.split('.')[0] if '.' in claim_text else claim_text[:100]

            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.GPT4,
                content=claim_text,
                evidence=evidence,
                position=position
            )

        except Exception as e:
            print(f"Error calling GPT-4 API: {e}")
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.GPT4,
                content=f"Error generating claim: {str(e)}",
                evidence=[],
                position="Error"
            )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """Generate challenge using GPT-4 API."""

        prompt = f"""You are reviewing this claim from {target_claim.model.value}:

Claim: {target_claim.content}
Evidence: {[str(e) for e in target_claim.evidence]}

{self._format_evidence_pool(evidence_pool)}

{context if context else ''}

Do you agree or disagree with this claim? If you disagree:
1. State your challenge
2. Provide evidence supporting your challenge
3. Reference the specific claim using @{target_claim.node_id}

If you agree, respond with "AGREE"."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model_config.model,
                max_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content

            if "AGREE" in content.upper() and len(content) < 100:
                return None

            challenge_text = extract_claim_content(content)
            evidence = parse_evidence(content)

            return Challenge(
                node_id=create_node_id("challenge"),
                model=ModelType.GPT4,
                content=challenge_text,
                evidence=evidence,
                target_id=target_claim.node_id,
                challenge_type="critique"
            )

        except Exception as e:
            print(f"Error calling GPT-4 API for challenge: {e}")
            return None


class Gemini(Debater):
    """Gemini (Google) debater - TODO: Implement."""

    def __init__(self, model_config: ModelConfig, config: Config, charter: Charter):
        super().__init__(model_config, config, charter)
        self.model_type = ModelType.GEMINI

        # TODO: Initialize Google Gemini client when google-generativeai is available

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """TODO: Implement Gemini API call."""
        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.GEMINI,
            content="[Gemini implementation TODO]",
            evidence=[],
            position="TODO"
        )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """TODO: Implement Gemini challenge."""
        return None


class Llama(Debater):
    """Llama (Local via Ollama) debater - TODO: Implement."""

    def __init__(self, model_config: ModelConfig, config: Config, charter: Charter):
        super().__init__(model_config, config, charter)
        self.model_type = ModelType.LLAMA

        # TODO: Initialize Ollama client

    async def generate_claim(
        self,
        query: str,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Claim:
        """TODO: Implement Ollama/Llama call."""
        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.LLAMA,
            content="[Llama implementation TODO]",
            evidence=[],
            position="TODO"
        )

    async def generate_challenge(
        self,
        target_claim: Claim,
        context: Optional[str] = None,
        evidence_pool: Optional[List[Evidence]] = None
    ) -> Optional[Challenge]:
        """TODO: Implement Llama challenge."""
        return None


def create_debater(model_type: ModelType, config: Config, charter: Charter) -> Debater:
    """Factory function to create debaters with config."""
    model_config = config.models.get(model_type.value)
    if not model_config:
        raise ValueError(f"No configuration found for model: {model_type.value}")

    if model_type == ModelType.CLAUDE:
        return Claude(model_config, config, charter)
    elif model_type == ModelType.GPT4:
        return GPT4(model_config, config, charter)
    elif model_type == ModelType.GEMINI:
        return Gemini(model_config, config, charter)
    elif model_type == ModelType.LLAMA:
        return Llama(model_config, config, charter)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

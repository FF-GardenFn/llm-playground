"""Anthropic Claude debater implementation."""

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    ANTHROPIC_AVAILABLE = False

from ..debate_tree import ModelType, Evidence, Claim, Challenge, create_node_id
from .base import Debater
from .utils import parse_evidence, extract_claim_content


class Claude(Debater):
    """Claude (Anthropic) debater with real API calls."""

    def __init__(self, model_config, config, charter):
        super().__init__(model_config, config, charter)

        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self.model_type = ModelType.CLAUDE

    async def generate_claim(self, query, context=None, evidence_pool=None):
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
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text

            claim_text = extract_claim_content(content)
            evidence = parse_evidence(content)
            position = claim_text.split(".")[0] if "." in claim_text else claim_text[:100]

            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.CLAUDE,
                content=claim_text,
                evidence=evidence,
                position=position,
            )
        except Exception as e:  # pragma: no cover - external API
            print(f"Error calling Claude API: {e}")
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.CLAUDE,
                content=f"Error generating claim: {str(e)}",
                evidence=[],
                position="Error",
            )

    async def generate_challenge(self, target_claim, context=None, evidence_pool=None):
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
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            if "AGREE" in content.upper() and len(content) < 100:
                return None

            challenge_text = extract_claim_content(content)
            evidence = parse_evidence(content)

            return Challenge(
                node_id=create_node_id("challenge"),
                model=ModelType.CLAUDE,
                content=challenge_text,
                evidence=evidence,
                target_id=target_claim.node_id,
                challenge_type="critique",
            )
        except Exception as e:  # pragma: no cover - external API
            print(f"Error calling Claude API for challenge: {e}")
            return None

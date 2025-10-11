"""OpenAI GPT debaters (GPT-4, GPT-5) and O4 reasoning model."""

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    OPENAI_AVAILABLE = False

from ..debate_tree import ModelType, Claim, Challenge, create_node_id
from .base import Debater
from .utils import parse_evidence, extract_claim_content


class _OpenAIBase(Debater):
    """Shared setup for OpenAI clients."""

    def _ensure_client(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
        if not self.config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)


class GPT5(_OpenAIBase):
    """GPT-5 (OpenAI) debater with real API calls."""

    def __init__(self, model_config, config, charter):
        super().__init__(model_config, config, charter)
        self._ensure_client()
        self.model_type = ModelType.GPT5

    async def generate_claim(self, query, context=None, evidence_pool=None):
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
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            claim_text = extract_claim_content(content)
            evidence = parse_evidence(content)
            position = claim_text.split(".")[0] if "." in claim_text else claim_text[:100]
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.GPT5,
                content=claim_text,
                evidence=evidence,
                position=position,
            )
        except Exception as e:  # pragma: no cover
            print(f"Error calling GPT-5 API: {e}")
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.GPT5,
                content=f"Error generating claim: {str(e)}",
                evidence=[],
                position="Error",
            )

    async def generate_challenge(self, target_claim, context=None, evidence_pool=None):
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
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            if "AGREE" in content.upper() and len(content) < 100:
                return None
            challenge_text = extract_claim_content(content)
            evidence = parse_evidence(content)
            return Challenge(
                node_id=create_node_id("challenge"),
                model=ModelType.GPT5,
                content=challenge_text,
                evidence=evidence,
                target_id=target_claim.node_id,
                challenge_type="critique",
            )
        except Exception as e:  # pragma: no cover
            print(f"Error calling GPT-5 API for challenge: {e}")
            return None


class GPT4(_OpenAIBase):
    """GPT-4 (OpenAI) debater with real API calls."""

    def __init__(self, model_config, config, charter):
        super().__init__(model_config, config, charter)
        self._ensure_client()
        self.model_type = ModelType.GPT4

    async def generate_claim(self, query, context=None, evidence_pool=None):
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
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            claim_text = extract_claim_content(content)
            evidence = parse_evidence(content)
            position = claim_text.split(".")[0] if "." in claim_text else claim_text[:100]
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.GPT4,
                content=claim_text,
                evidence=evidence,
                position=position,
            )
        except Exception as e:  # pragma: no cover
            print(f"Error calling GPT-4 API: {e}")
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.GPT4,
                content=f"Error generating claim: {str(e)}",
                evidence=[],
                position="Error",
            )

    async def generate_challenge(self, target_claim, context=None, evidence_pool=None):
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
                    {"role": "user", "content": prompt},
                ],
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
                challenge_type="critique",
            )
        except Exception as e:  # pragma: no cover
            print(f"Error calling GPT-4 API for challenge: {e}")
            return None


class O4(_OpenAIBase):
    """O4 (OpenAI Reasoning) debater with real API calls."""

    def __init__(self, model_config, config, charter):
        super().__init__(model_config, config, charter)
        self._ensure_client()
        self.model_type = ModelType.O4

    async def generate_claim(self, query, context=None, evidence_pool=None):
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
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            claim_text = extract_claim_content(content)
            evidence = parse_evidence(content)
            position = claim_text.split(".")[0] if "." in claim_text else claim_text[:100]
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.O4,
                content=claim_text,
                evidence=evidence,
                position=position,
            )
        except Exception as e:  # pragma: no cover
            print(f"Error calling O4 API: {e}")
            return Claim(
                node_id=create_node_id("claim"),
                model=ModelType.O4,
                content=f"Error generating claim: {str(e)}",
                evidence=[],
                position="Error",
            )

    async def generate_challenge(self, target_claim, context=None, evidence_pool=None):
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
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            if "AGREE" in content.upper() and len(content) < 100:
                return None
            challenge_text = extract_claim_content(content)
            evidence = parse_evidence(content)
            return Challenge(
                node_id=create_node_id("challenge"),
                model=ModelType.O4,
                content=challenge_text,
                evidence=evidence,
                target_id=target_claim.node_id,
                challenge_type="critique",
            )
        except Exception as e:  # pragma: no cover
            print(f"Error calling O4 API for challenge: {e}")
            return None

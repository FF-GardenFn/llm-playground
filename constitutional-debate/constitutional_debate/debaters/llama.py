"""Local Llama debater (stub).

Implement with Ollama or other local runtime when available.
"""
from ..debate_tree import ModelType, Claim, Challenge, create_node_id
from .base import Debater


class Llama(Debater):
    """Llama (Local via Ollama) debater - TODO: Implement."""

    def __init__(self, model_config, config, charter):
        super().__init__(model_config, config, charter)
        self.model_type = ModelType.LLAMA
        # TODO: Initialize Ollama or other local model client

    async def generate_claim(self, query, context=None, evidence_pool=None):
        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.LLAMA,
            content="[Llama implementation TODO]",
            evidence=[],
            position="TODO",
        )

    async def generate_challenge(self, target_claim, context=None, evidence_pool=None):
        return None

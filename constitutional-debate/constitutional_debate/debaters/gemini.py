"""Google Gemini debater (stub).

Implement when google-generativeai is available.
"""
try:
    import google.generativeai as genai  # noqa: F401
    GOOGLE_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    GOOGLE_AVAILABLE = False

from ..debate_tree import ModelType, Claim, Challenge, create_node_id
from .base import Debater


class Gemini(Debater):
    """Gemini (Google DeepMind) debater - TODO: Implement."""

    def __init__(self, model_config, config, charter):
        super().__init__(model_config, config, charter)
        self.model_type = ModelType.GEMINI
        # TODO: Initialize Google Gemini client when google-generativeai is available

    async def generate_claim(self, query, context=None, evidence_pool=None):
        return Claim(
            node_id=create_node_id("claim"),
            model=ModelType.GEMINI,
            content="[Gemini implementation TODO]",
            evidence=[],
            position="TODO",
        )

    async def generate_challenge(self, target_claim, context=None, evidence_pool=None):
        return None

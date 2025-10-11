"""Debater clients package

Provides modular implementations of LLM debaters and helpers:
- base: abstract Debater class and shared helpers
- utils: response parsing helpers
- claude: Anthropic Claude client
- openai_gpt: OpenAI GPT-4/5 and O4 clients
- gemini: Google Gemini client (stub)
- llama: Local Llama client (stub)
- factory: create_debater(ModelType, Config, Charter)

This split improves maintainability and clarity versus a single monolithic module.
"""

from .base import Debater  # re-export
from .factory import create_debater  # re-export
from .claude import Claude  # re-export
from .openai_gpt import GPT4, GPT5, O4  # re-export
from .gemini import Gemini  # re-export
from .llama import Llama  # re-export

__all__ = [
    "Debater",
    "create_debater",
    "Claude",
    "GPT4",
    "GPT5",
    "O4",
    "Gemini",
    "Llama",
]

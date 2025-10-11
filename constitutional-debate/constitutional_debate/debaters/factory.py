"""Factory for creating debater instances by ModelType."""
from ..debate_tree import ModelType
from ..config import Config
from ..charter import Charter

from .claude import Claude
from .openai_gpt import GPT4, GPT5, O4
from .gemini import Gemini
from .llama import Llama


def create_debater(model_type: ModelType, config: Config, charter: Charter):
    """Create and return a debater instance for the given model type.

    Raises ValueError if the model type is unknown or misconfigured.
    """
    model_config = config.models.get(model_type.value)
    if not model_config:
        raise ValueError(
            f"No configuration found for model: {model_type.value}. "
            f"Add configuration to config.yaml under models.{model_type.value}"
        )

    mapping = {
        ModelType.CLAUDE: Claude,
        ModelType.GPT5: GPT5,
        ModelType.GPT4: GPT4,
        ModelType.O4: O4,
        ModelType.GEMINI: Gemini,
        ModelType.LLAMA: Llama,
    }

    cls = mapping.get(model_type)
    if not cls:
        raise ValueError(
            f"Unknown model type: {model_type}. "
            f"Supported types: {', '.join(t.value for t in mapping.keys())}"
        )

    return cls(model_config, config, charter)
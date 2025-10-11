"""Configuration Management

Loads settings from config.yaml and .env
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from dataclasses import dataclass, field

# Try to import python-dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    base_url: Optional[str] = None


@dataclass
class DebateSettings:
    """Debate-level settings."""
    workspace: str = "default"
    max_rounds: int = 3
    consensus_threshold: float = 0.75
    strict_constitutional: bool = True


@dataclass
class MemorySettings:
    """Adaptive Memory settings."""
    enabled: bool = True
    workspace: str = "constitutional-debates"
    evidence_top_k: int = 10
    min_memory_score: float = 0.5


@dataclass
class Config:
    """Main configuration class."""
    debate: DebateSettings
    models: Dict[str, ModelConfig]
    enabled_models: List[str]
    memory: MemorySettings
    output_dir: Path
    log_level: str = "INFO"

    # API keys (loaded from .env)
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML and environment variables.

    Args:
        config_path: Path to config.yaml (default: ./config.yaml)

    Returns:
        Config object
    """
    # Find config file
    if config_path is None:
        # Try current directory, then package directory
        if Path("config.yaml").exists():
            config_path = "config.yaml"
        else:
            package_dir = Path(__file__).parent.parent
            config_path = package_dir / "config.yaml"

    # Load .env file
    if DOTENV_AVAILABLE:
        env_path = Path(config_path).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    # Load YAML config
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    # Parse debate settings
    debate_cfg = yaml_config.get('debate', {})
    debate = DebateSettings(
        workspace=debate_cfg.get('workspace', 'default'),
        max_rounds=debate_cfg.get('max_rounds', 3),
        consensus_threshold=debate_cfg.get('consensus_threshold', 0.75),
        strict_constitutional=debate_cfg.get('strict_constitutional', True)
    )

    # Parse model configs
    models_cfg = yaml_config.get('models', {})
    enabled_models = models_cfg.get('enabled', ['claude', 'gpt4'])

    models = {}
    for model_name in ['claude', 'gpt4', 'gemini', 'llama']:
        if model_name in models_cfg:
            model_cfg = models_cfg[model_name]
            models[model_name] = ModelConfig(
                model=model_cfg.get('model', ''),
                temperature=model_cfg.get('temperature', 0.7),
                max_tokens=model_cfg.get('max_tokens', 2000),
                timeout=model_cfg.get('timeout', 60),
                base_url=model_cfg.get('base_url')
            )

    # Parse memory settings
    memory_cfg = yaml_config.get('memory', {})
    memory = MemorySettings(
        enabled=memory_cfg.get('enabled', True),
        workspace=memory_cfg.get('workspace', 'constitutional-debates'),
        evidence_top_k=memory_cfg.get('evidence_top_k', 10),
        min_memory_score=memory_cfg.get('min_memory_score', 0.5)
    )

    # Output settings
    output_cfg = yaml_config.get('output', {})
    output_dir = Path(output_cfg.get('output_dir', 'debates'))

    # Logging
    logging_cfg = yaml_config.get('logging', {})
    log_level = logging_cfg.get('level', 'INFO')

    # Load API keys from environment
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')

    return Config(
        debate=debate,
        models=models,
        enabled_models=enabled_models,
        memory=memory,
        output_dir=output_dir,
        log_level=log_level,
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key,
        google_api_key=google_api_key
    )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """Reload configuration."""
    global _config
    _config = load_config(config_path)
    return _config

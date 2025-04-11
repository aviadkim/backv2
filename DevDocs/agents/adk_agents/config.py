"""
Lightweight configuration for ADK agents.
"""
import os
from typing import Dict, Any

# Default configuration for ADK agents
DEFAULT_CONFIG = {
    "model": "gemini-2.0-flash-exp",  # Default model to use
    "temperature": 0.2,               # Lower temperature for more deterministic responses
    "max_output_tokens": 1024,        # Maximum tokens in the response
    "top_p": 0.95,                    # Top-p sampling parameter
    "top_k": 40,                      # Top-k sampling parameter
    "lazy_loading": True,             # Whether to load ADK components lazily
    "use_cache": True,                # Whether to cache responses
    "cache_size": 100,                # Maximum number of cached responses
    "low_resource_mode": True,        # Whether to use low resource mode
}

# Environment variable names
ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"
ENV_GOOGLE_GENAI_USE_VERTEXAI = "GOOGLE_GENAI_USE_VERTEXAI"
ENV_GOOGLE_CLOUD_PROJECT = "GOOGLE_CLOUD_PROJECT"
ENV_GOOGLE_CLOUD_LOCATION = "GOOGLE_CLOUD_LOCATION"

def get_env_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    In lightweight mode, this doesn't actually load any environment variables
    to avoid unnecessary processing.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    # In lightweight mode, return a placeholder config
    return {
        "use_vertex_ai": False,
        "api_key": "placeholder_key",
        "low_resource_mode": True
    }

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries, with override_config taking precedence.

    Args:
        base_config: Base configuration dictionary
        override_config: Override configuration dictionary

    Returns:
        Dict[str, Any]: Merged configuration dictionary
    """
    result = base_config.copy()
    if override_config:
        result.update(override_config)
    return result

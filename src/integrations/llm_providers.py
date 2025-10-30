"""LLM provider configurations."""

from typing import Any, Dict, Optional

from ..config import Settings, get_settings


def get_provider_config(provider: str, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific LLM provider.
    
    Args:
        provider: Provider name (openai, anthropic, azure, bedrock, vertex, etc.)
        settings: Optional settings instance
        
    Returns:
        Configuration dictionary for the provider
    """
    settings = settings or get_settings()
    
    configs = {
        "openai": {
            "api_key": settings.openai_api_key,
            "api_base": "https://api.openai.com/v1",
        },
        "anthropic": {
            "api_key": settings.anthropic_api_key,
        },
        "azure": {
            "api_key": settings.azure_api_key,
            "api_base": settings.azure_api_base,
            "api_version": settings.azure_api_version,
        },
        "bedrock": {
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key,
            "aws_region_name": settings.aws_region_name,
        },
        "vertex_ai": {
            "vertex_project": settings.vertex_project,
            "vertex_location": settings.vertex_location,
            "credentials_path": settings.google_application_credentials,
        },
        "cohere": {
            "api_key": settings.cohere_api_key,
        },
        "huggingface": {
            "api_key": settings.huggingface_api_key,
        },
    }
    
    return configs.get(provider, {})


def get_model_provider(model: str) -> str:
    """
    Determine the provider from a model name.
    
    Args:
        model: Model name
        
    Returns:
        Provider name
    """
    model_lower = model.lower()
    
    if "gpt" in model_lower or "text-davinci" in model_lower or "text-curie" in model_lower:
        return "openai"
    elif "claude" in model_lower:
        return "anthropic"
    elif "bedrock" in model_lower or "amazon" in model_lower:
        return "bedrock"
    elif "vertex" in model_lower or "gemini" in model_lower or "palm" in model_lower:
        return "vertex_ai"
    elif "cohere" in model_lower:
        return "cohere"
    elif "huggingface" in model_lower or "hf:" in model_lower:
        return "huggingface"
    elif "azure" in model_lower:
        return "azure"
    else:
        return "unknown"


def get_supported_models() -> Dict[str, list]:
    """
    Get list of supported models by provider.
    
    Returns:
        Dictionary mapping providers to their supported models
    """
    return {
        "openai": [
            "gpt-4-turbo-preview",
            "gpt-4-1106-preview",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ],
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        ],
        "azure": [
            "azure/gpt-4",
            "azure/gpt-35-turbo",
        ],
        "bedrock": [
            "bedrock/anthropic.claude-3-opus-20240229-v1:0",
            "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
            "bedrock/anthropic.claude-3-haiku-20240307-v1:0",
            "bedrock/anthropic.claude-v2:1",
        ],
        "vertex_ai": [
            "vertex_ai/gemini-pro",
            "vertex_ai/gemini-pro-vision",
            "vertex_ai/chat-bison",
        ],
    }


def get_model_limits(model: str) -> Dict[str, int]:
    """
    Get token limits for a specific model.
    
    Args:
        model: Model name
        
    Returns:
        Dictionary with max_tokens and context_window
    """
    model_lower = model.lower()
    
    limits = {
        "gpt-4-turbo": {"max_tokens": 4096, "context_window": 128000},
        "gpt-4": {"max_tokens": 8192, "context_window": 8192},
        "gpt-4-32k": {"max_tokens": 32768, "context_window": 32768},
        "gpt-3.5-turbo": {"max_tokens": 4096, "context_window": 16385},
        "gpt-3.5-turbo-16k": {"max_tokens": 16384, "context_window": 16384},
        "claude-3-opus": {"max_tokens": 4096, "context_window": 200000},
        "claude-3-sonnet": {"max_tokens": 4096, "context_window": 200000},
        "claude-3-haiku": {"max_tokens": 4096, "context_window": 200000},
        "claude-2": {"max_tokens": 4096, "context_window": 100000},
    }
    
    # Find matching limits
    for key, value in limits.items():
        if key in model_lower:
            return value
    
    # Default limits
    return {"max_tokens": 4096, "context_window": 8192}

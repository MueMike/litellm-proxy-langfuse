"""Integration tests."""

import pytest

from src.config import Settings
from src.integrations.llm_providers import (
    get_model_limits,
    get_model_provider,
    get_provider_config,
    get_supported_models,
)
from src.utils.helpers import calculate_cost, extract_metadata, generate_trace_id


def test_generate_trace_id():
    """Test trace ID generation."""
    trace_id = generate_trace_id()
    assert isinstance(trace_id, str)
    assert len(trace_id) > 0
    
    # Should be unique
    trace_id2 = generate_trace_id()
    assert trace_id != trace_id2


def test_calculate_cost_gpt4():
    """Test cost calculation for GPT-4."""
    cost = calculate_cost("gpt-4", 1000, 500)
    assert cost > 0
    assert isinstance(cost, float)


def test_calculate_cost_gpt35():
    """Test cost calculation for GPT-3.5."""
    cost = calculate_cost("gpt-3.5-turbo", 1000, 500)
    assert cost > 0
    # GPT-3.5 should be cheaper than GPT-4
    gpt4_cost = calculate_cost("gpt-4", 1000, 500)
    assert cost < gpt4_cost


def test_calculate_cost_claude():
    """Test cost calculation for Claude."""
    cost = calculate_cost("claude-3-opus", 1000, 500)
    assert cost > 0


def test_extract_metadata():
    """Test metadata extraction."""
    request_data = {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "stream": False,
    }
    
    metadata = extract_metadata(request_data)
    assert metadata["model"] == "gpt-4"
    assert metadata["temperature"] == 0.7
    assert metadata["max_tokens"] == 1000
    assert metadata["stream"] is False


def test_extract_metadata_with_custom():
    """Test metadata extraction with custom fields."""
    request_data = {
        "model": "gpt-4",
        "temperature": 0.7,
        "metadata": {
            "task_type": "code_generation",
            "language": "python",
        },
    }
    
    metadata = extract_metadata(request_data)
    assert metadata["task_type"] == "code_generation"
    assert metadata["language"] == "python"


def test_get_model_provider():
    """Test model provider detection."""
    assert get_model_provider("gpt-4") == "openai"
    assert get_model_provider("gpt-3.5-turbo") == "openai"
    assert get_model_provider("claude-3-opus") == "anthropic"
    assert get_model_provider("claude-3-sonnet") == "anthropic"
    assert get_model_provider("gemini-pro") == "vertex_ai"
    assert get_model_provider("unknown-model") == "unknown"


def test_get_provider_config():
    """Test provider config retrieval."""
    settings = Settings(
        OPENAI_API_KEY="test-key",
        ANTHROPIC_API_KEY="test-key-2",
    )
    
    openai_config = get_provider_config("openai", settings)
    assert openai_config["api_key"] == "test-key"
    
    anthropic_config = get_provider_config("anthropic", settings)
    assert anthropic_config["api_key"] == "test-key-2"


def test_get_supported_models():
    """Test supported models listing."""
    models = get_supported_models()
    assert isinstance(models, dict)
    assert "openai" in models
    assert "anthropic" in models
    assert len(models["openai"]) > 0
    assert len(models["anthropic"]) > 0


def test_get_model_limits():
    """Test model limits retrieval."""
    limits = get_model_limits("gpt-4")
    assert "max_tokens" in limits
    assert "context_window" in limits
    assert limits["max_tokens"] > 0
    assert limits["context_window"] > 0


def test_get_model_limits_claude():
    """Test Claude model limits."""
    limits = get_model_limits("claude-3-opus")
    assert limits["context_window"] == 200000
    assert limits["max_tokens"] == 4096

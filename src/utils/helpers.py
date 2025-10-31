"""Helper utility functions."""

import time
import uuid
from typing import Any, Dict, Optional


def generate_trace_id() -> str:
    """Generate a unique trace ID."""
    return str(uuid.uuid4())


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    provider: Optional[str] = None,
) -> float:
    """
    Calculate cost for API call based on token usage.
    
    Args:
        model: Model name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        provider: Optional provider name
        
    Returns:
        Estimated cost in USD
    """
    # Simplified cost calculation - should be enhanced with real pricing
    # This is a placeholder that uses rough estimates
    cost_per_1k_prompt = 0.01
    cost_per_1k_completion = 0.03

    # Adjust costs based on model
    if "gpt-4" in model.lower():
        cost_per_1k_prompt = 0.03
        cost_per_1k_completion = 0.06
    elif "gpt-3.5" in model.lower():
        cost_per_1k_prompt = 0.0015
        cost_per_1k_completion = 0.002
    elif "claude-3-opus" in model.lower():
        cost_per_1k_prompt = 0.015
        cost_per_1k_completion = 0.075
    elif "claude-3-sonnet" in model.lower():
        cost_per_1k_prompt = 0.003
        cost_per_1k_completion = 0.015
    elif "claude-3-haiku" in model.lower():
        cost_per_1k_prompt = 0.00025
        cost_per_1k_completion = 0.00125

    prompt_cost = (prompt_tokens / 1000) * cost_per_1k_prompt
    completion_cost = (completion_tokens / 1000) * cost_per_1k_completion

    return round(prompt_cost + completion_cost, 6)


def extract_metadata(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant metadata from request for tracing.
    
    Args:
        request_data: Request data dictionary
        
    Returns:
        Dictionary of metadata
    """
    metadata = {
        "model": request_data.get("model", "unknown"),
        "temperature": request_data.get("temperature"),
        "max_tokens": request_data.get("max_tokens"),
        "top_p": request_data.get("top_p"),
        "frequency_penalty": request_data.get("frequency_penalty"),
        "presence_penalty": request_data.get("presence_penalty"),
        "stream": request_data.get("stream", False),
    }

    # Add custom metadata if present and not None
    if "metadata" in request_data and request_data["metadata"] is not None:
        metadata.update(request_data["metadata"])

    # Remove None values
    return {k: v for k, v in metadata.items() if v is not None}


def format_messages_for_logging(messages: list) -> str:
    """
    Format messages for logging (truncated for readability).
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Formatted string
    """
    formatted = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if isinstance(content, str):
            truncated = content[:100] + "..." if len(content) > 100 else content
            formatted.append(f"{role}: {truncated}")
        else:
            formatted.append(f"{role}: [complex content]")
    return " | ".join(formatted)


def get_timestamp() -> float:
    """Get current timestamp in seconds."""
    return time.time()


def get_timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(time.time() * 1000)

"""API route definitions."""

import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

import litellm

from ..integrations import LangFuseClient
from ..integrations.llm_providers import get_model_provider
from ..monitoring import get_metrics_collector
from ..utils import calculate_cost, extract_metadata

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""

    model: str
    messages: list
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stream: Optional[bool] = False
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatCompletionResponse(BaseModel):
    """Chat completion response model."""

    id: str
    object: str
    created: int
    model: str
    choices: list
    usage: Optional[Dict[str, int]] = None


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "litellm-proxy-langfuse"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "service": "litellm-proxy-langfuse"}


@router.post("/v1/chat/completions")
@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    completion_request: ChatCompletionRequest,
):
    """
    Handle chat completion requests.
    
    Args:
        request: FastAPI request
        completion_request: Chat completion request data
        
    Returns:
        Chat completion response
    """
    start_time = time.time()
    metrics_collector = get_metrics_collector()
    
    # Extract metadata
    model = completion_request.model
    provider = get_model_provider(model)
    messages = completion_request.messages
    
    # Get trace info from request state
    trace_id = getattr(request.state, "trace_id", None)
    user_id = request.headers.get("X-User-ID", completion_request.user or "anonymous")
    session_id = request.headers.get("X-Session-ID", trace_id)
    
    # Get LangFuse client from request state
    langfuse_client = getattr(request.state, "langfuse_client", None)
    
    # Increment active requests
    metrics_collector.inc_active_requests(model, provider)
    
    try:
        # Create LangFuse trace if enabled
        trace = None
        if langfuse_client and langfuse_client.enabled:
            metadata = extract_metadata(completion_request.dict())
            metadata.update({
                "endpoint": "/chat/completions",
                "provider": provider,
            })
            
            # Add custom metadata from request
            if completion_request.metadata:
                metadata.update(completion_request.metadata)
            
            trace = langfuse_client.create_trace(
                name="chat_completion",
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
                tags=[provider, model],
            )
        
        # Call LiteLLM
        logger.info(f"Calling LiteLLM with model: {model}")
        
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=completion_request.temperature,
            max_tokens=completion_request.max_tokens,
            top_p=completion_request.top_p,
            frequency_penalty=completion_request.frequency_penalty,
            presence_penalty=completion_request.presence_penalty,
            stream=completion_request.stream,
            user=user_id,
        )
        
        # Calculate metrics
        duration = time.time() - start_time
        
        # Extract usage info
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        # Calculate cost
        cost = calculate_cost(model, prompt_tokens, completion_tokens, provider)
        
        # Record metrics
        metrics_collector.record_request(
            model=model,
            provider=provider,
            status="success",
            duration=duration,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )
        
        # Create LangFuse generation if trace exists
        if trace and langfuse_client and langfuse_client.enabled:
            langfuse_client.create_generation(
                trace_id=trace.id if hasattr(trace, 'id') else trace_id,
                name="llm_generation",
                model=model,
                input_data=messages,
                output_data=response.get("choices", []),
                metadata={
                    "provider": provider,
                    "temperature": completion_request.temperature,
                    "max_tokens": completion_request.max_tokens,
                },
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                start_time=start_time,
                end_time=time.time(),
            )
        
        logger.info(
            f"Chat completion successful: model={model}, "
            f"tokens={prompt_tokens + completion_tokens}, "
            f"cost=${cost:.6f}, duration={duration:.3f}s"
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Record error metrics
        metrics_collector.record_request(
            model=model,
            provider=provider,
            status="error",
            duration=duration,
        )
        metrics_collector.record_error(model, provider, type(e).__name__)
        
        logger.error(f"Chat completion failed: {e}", exc_info=True)
        
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Decrement active requests
        metrics_collector.dec_active_requests(model, provider)


@router.get("/v1/models")
@router.get("/models")
async def list_models():
    """
    List available models.
    
    Returns:
        List of available models
    """
    # This should be populated from config in production
    models = [
        {"id": "gpt-4-turbo-preview", "object": "model", "owned_by": "openai"},
        {"id": "gpt-4", "object": "model", "owned_by": "openai"},
        {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "openai"},
        {"id": "claude-3-opus-20240229", "object": "model", "owned_by": "anthropic"},
        {"id": "claude-3-sonnet-20240229", "object": "model", "owned_by": "anthropic"},
        {"id": "claude-3-haiku-20240307", "object": "model", "owned_by": "anthropic"},
    ]
    
    return {"object": "list", "data": models}

"""Request/response middleware for tracing and monitoring."""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..integrations import LangFuseClient, get_provider_config
from ..integrations.llm_providers import get_model_provider
from ..monitoring import get_metrics_collector
from ..utils import calculate_cost, extract_metadata, generate_trace_id

logger = logging.getLogger(__name__)


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response tracing with LangFuse."""

    def __init__(self, app, langfuse_client: LangFuseClient):
        """
        Initialize tracing middleware.
        
        Args:
            app: FastAPI application
            langfuse_client: LangFuse client instance
        """
        super().__init__(app)
        self.langfuse_client = langfuse_client
        self.metrics_collector = get_metrics_collector()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with tracing.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        start_time = time.time()
        
        # Skip tracing for health check and metrics endpoints
        if request.url.path in ["/health", "/metrics", "/ready"]:
            return await call_next(request)

        # Generate trace ID
        trace_id = generate_trace_id()
        request.state.trace_id = trace_id
        
        # Get user and session info from headers
        user_id = request.headers.get("X-User-ID", "anonymous")
        session_id = request.headers.get("X-Session-ID", trace_id)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add trace headers to response
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Duration-Ms"] = str(int(duration * 1000))
        
        logger.debug(
            f"Request processed: {request.method} {request.url.path} "
            f"(duration: {duration:.3f}s, status: {response.status_code})"
        )
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""

    def __init__(self, app):
        """
        Initialize metrics middleware.
        
        Args:
            app: FastAPI application
        """
        super().__init__(app)
        self.metrics_collector = get_metrics_collector()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and collect metrics.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        start_time = time.time()
        
        # Skip metrics for health check and metrics endpoints
        if request.url.path in ["/health", "/metrics", "/ready"]:
            return await call_next(request)

        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add duration header
        response.headers["X-Duration-Ms"] = str(int(duration * 1000))
        
        return response

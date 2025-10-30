"""Main proxy server implementation."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config import get_settings
from ..integrations import LangFuseClient
from ..monitoring import get_metrics_collector, setup_logging
from .middleware import MetricsMiddleware, TracingMiddleware
from .routes import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown.
    
    Args:
        app: FastAPI application
    """
    # Startup
    settings = get_settings()
    setup_logging(settings)
    
    logger.info("Starting LiteLLM Proxy with LangFuse integration")
    logger.info(f"LangFuse enabled: {settings.langfuse_enabled}")
    logger.info(f"Prometheus metrics enabled: {settings.enable_prometheus}")
    
    # Initialize metrics collector
    metrics_collector = get_metrics_collector()
    if settings.enable_prometheus:
        try:
            metrics_collector.start_server()
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    # Initialize LangFuse client
    langfuse_client = LangFuseClient(settings)
    app.state.langfuse_client = langfuse_client
    
    yield
    
    # Shutdown
    logger.info("Shutting down LiteLLM Proxy")
    if langfuse_client:
        langfuse_client.shutdown()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    
    app = FastAPI(
        title="LiteLLM Proxy with LangFuse",
        description="OpenAI-compatible LLM proxy with integrated LangFuse tracing",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(MetricsMiddleware)
    
    # Add tracing middleware if LangFuse is configured
    if settings.is_langfuse_configured():
        langfuse_client = LangFuseClient(settings)
        app.add_middleware(TracingMiddleware, langfuse_client=langfuse_client)
    
    # Include routes
    app.include_router(router)
    
    # Dependency injection for LangFuse client
    @app.middleware("http")
    async def inject_dependencies(request, call_next):
        """Inject dependencies into request state."""
        if hasattr(app.state, "langfuse_client"):
            request.state.langfuse_client = app.state.langfuse_client
        response = await call_next(request)
        return response
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.proxy_host,
        port=settings.proxy_port,
        log_level=settings.log_level.lower(),
    )

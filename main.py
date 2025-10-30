"""Main entry point for the LiteLLM Proxy with LangFuse integration."""

import sys
import uvicorn

from src.config import get_settings
from src.proxy.server import create_app


def main():
    """Run the proxy server."""
    settings = get_settings()
    
    print("=" * 80)
    print("LiteLLM Proxy with LangFuse Integration")
    print("=" * 80)
    print(f"Starting server on {settings.proxy_host}:{settings.proxy_port}")
    print(f"LangFuse tracing: {'Enabled' if settings.is_langfuse_configured() else 'Disabled'}")
    print(f"Prometheus metrics: {'Enabled' if settings.enable_prometheus else 'Disabled'}")
    print(f"Log level: {settings.log_level}")
    print("=" * 80)
    print()
    
    app = create_app()
    
    try:
        uvicorn.run(
            app,
            host=settings.proxy_host,
            port=settings.proxy_port,
            log_level=settings.log_level.lower(),
            access_log=settings.enable_request_logging,
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

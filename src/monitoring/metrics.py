"""Metrics collection using Prometheus."""

import logging
import time
from typing import Dict, Optional

from prometheus_client import Counter, Gauge, Histogram, start_http_server

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collector for Prometheus metrics."""

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize metrics collector.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self.enabled = self.settings.enable_prometheus

        if self.enabled:
            # Request metrics
            self.request_counter = Counter(
                "litellm_requests_total",
                "Total number of requests",
                ["model", "provider", "status"],
            )
            
            self.request_duration = Histogram(
                "litellm_request_duration_seconds",
                "Request duration in seconds",
                ["model", "provider"],
                buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
            )
            
            # Token metrics
            self.tokens_used = Counter(
                "litellm_tokens_used_total",
                "Total tokens used",
                ["model", "provider", "token_type"],
            )
            
            # Cost metrics
            self.cost_total = Counter(
                "litellm_cost_usd_total",
                "Total cost in USD",
                ["model", "provider"],
            )
            
            # Active requests
            self.active_requests = Gauge(
                "litellm_active_requests",
                "Number of active requests",
                ["model", "provider"],
            )
            
            # Error metrics
            self.error_counter = Counter(
                "litellm_errors_total",
                "Total number of errors",
                ["model", "provider", "error_type"],
            )
            
            logger.info(f"Metrics collector initialized on port {self.settings.prometheus_port}")

    def start_server(self) -> None:
        """Start Prometheus metrics HTTP server."""
        if self.enabled:
            try:
                start_http_server(self.settings.prometheus_port)
                logger.info(f"Prometheus metrics server started on port {self.settings.prometheus_port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {e}")

    def record_request(
        self,
        model: str,
        provider: str,
        status: str,
        duration: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """
        Record request metrics.
        
        Args:
            model: Model name
            provider: Provider name
            status: Request status (success, error)
            duration: Request duration in seconds
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost: Request cost in USD
        """
        if not self.enabled:
            return

        try:
            self.request_counter.labels(model=model, provider=provider, status=status).inc()
            self.request_duration.labels(model=model, provider=provider).observe(duration)
            
            if prompt_tokens > 0:
                self.tokens_used.labels(
                    model=model, provider=provider, token_type="prompt"
                ).inc(prompt_tokens)
            
            if completion_tokens > 0:
                self.tokens_used.labels(
                    model=model, provider=provider, token_type="completion"
                ).inc(completion_tokens)
            
            if cost > 0:
                self.cost_total.labels(model=model, provider=provider).inc(cost)
                
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")

    def record_error(self, model: str, provider: str, error_type: str) -> None:
        """
        Record error metrics.
        
        Args:
            model: Model name
            provider: Provider name
            error_type: Type of error
        """
        if not self.enabled:
            return

        try:
            self.error_counter.labels(
                model=model, provider=provider, error_type=error_type
            ).inc()
        except Exception as e:
            logger.error(f"Failed to record error metrics: {e}")

    def inc_active_requests(self, model: str, provider: str) -> None:
        """Increment active requests counter."""
        if self.enabled:
            try:
                self.active_requests.labels(model=model, provider=provider).inc()
            except Exception as e:
                logger.error(f"Failed to increment active requests: {e}")

    def dec_active_requests(self, model: str, provider: str) -> None:
        """Decrement active requests counter."""
        if self.enabled:
            try:
                self.active_requests.labels(model=model, provider=provider).dec()
            except Exception as e:
                logger.error(f"Failed to decrement active requests: {e}")


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

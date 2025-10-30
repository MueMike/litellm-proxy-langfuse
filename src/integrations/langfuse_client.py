"""LangFuse integration client for tracing and monitoring."""

import logging
from typing import Any, Dict, Optional

from langfuse import Langfuse

from ..config import Settings, get_settings
from ..utils import calculate_cost, extract_metadata, generate_trace_id

logger = logging.getLogger(__name__)


class LangFuseClient:
    """Client for integrating with LangFuse tracing system."""

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize LangFuse client.
        
        Args:
            settings: Application settings. If None, loads from environment.
        """
        self.settings = settings or get_settings()
        self.client: Optional[Langfuse] = None
        self.enabled = False

        if self.settings.is_langfuse_configured():
            try:
                self.client = Langfuse(
                    public_key=self.settings.langfuse_public_key,
                    secret_key=self.settings.langfuse_secret_key,
                    host=self.settings.langfuse_host,
                )
                self.enabled = True
                logger.info("LangFuse client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LangFuse client: {e}")
                self.enabled = False
        else:
            logger.warning("LangFuse not configured. Tracing disabled.")

    def create_trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None,
    ) -> Optional[Any]:
        """
        Create a new trace in LangFuse.
        
        Args:
            name: Trace name
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional metadata dictionary
            tags: Optional list of tags
            
        Returns:
            Trace object or None if disabled
        """
        if not self.enabled or not self.client:
            return None

        try:
            trace = self.client.trace(
                name=name,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
                tags=tags,
            )
            logger.debug(f"Created trace: {name}")
            return trace
        except Exception as e:
            logger.error(f"Failed to create trace: {e}")
            return None

    def create_generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_data: Any,
        output_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        usage: Optional[Dict[str, int]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> Optional[Any]:
        """
        Create a generation span in an existing trace.
        
        Args:
            trace_id: Parent trace ID
            name: Generation name
            model: Model name
            input_data: Input data (prompt)
            output_data: Output data (completion)
            metadata: Optional metadata
            usage: Optional token usage dict
            start_time: Optional start timestamp
            end_time: Optional end timestamp
            
        Returns:
            Generation object or None if disabled
        """
        if not self.enabled or not self.client:
            return None

        try:
            generation = self.client.generation(
                trace_id=trace_id,
                name=name,
                model=model,
                model_parameters=metadata,
                input=input_data,
                output=output_data,
                usage=usage,
                start_time=start_time,
                end_time=end_time,
            )
            logger.debug(f"Created generation: {name}")
            return generation
        except Exception as e:
            logger.error(f"Failed to create generation: {e}")
            return None

    def create_span(
        self,
        trace_id: str,
        name: str,
        input_data: Any = None,
        output_data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> Optional[Any]:
        """
        Create a span in an existing trace.
        
        Args:
            trace_id: Parent trace ID
            name: Span name
            input_data: Optional input data
            output_data: Optional output data
            metadata: Optional metadata
            start_time: Optional start timestamp
            end_time: Optional end timestamp
            
        Returns:
            Span object or None if disabled
        """
        if not self.enabled or not self.client:
            return None

        try:
            span = self.client.span(
                trace_id=trace_id,
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata,
                start_time=start_time,
                end_time=end_time,
            )
            logger.debug(f"Created span: {name}")
            return span
        except Exception as e:
            logger.error(f"Failed to create span: {e}")
            return None

    def score_trace(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> bool:
        """
        Add a score to a trace.
        
        Args:
            trace_id: Trace ID to score
            name: Score name
            value: Score value
            comment: Optional comment
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
            )
            logger.debug(f"Added score to trace {trace_id}: {name}={value}")
            return True
        except Exception as e:
            logger.error(f"Failed to score trace: {e}")
            return False

    def flush(self):
        """Flush any pending events to LangFuse."""
        if self.enabled and self.client:
            try:
                self.client.flush()
                logger.debug("Flushed LangFuse events")
            except Exception as e:
                logger.error(f"Failed to flush LangFuse events: {e}")

    def shutdown(self):
        """Shutdown the LangFuse client."""
        if self.enabled and self.client:
            try:
                self.flush()
                logger.info("LangFuse client shut down")
            except Exception as e:
                logger.error(f"Error during LangFuse shutdown: {e}")


# Global client instance
_langfuse_client: Optional[LangFuseClient] = None


def get_langfuse_client() -> LangFuseClient:
    """Get the global LangFuse client instance."""
    global _langfuse_client
    if _langfuse_client is None:
        _langfuse_client = LangFuseClient()
    return _langfuse_client

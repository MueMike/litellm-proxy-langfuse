"""Unit tests for LangFuse integration."""

import os

import pytest

from src.config import Settings
from src.integrations import LangFuseClient


@pytest.fixture
def settings(monkeypatch):
    """Create test settings without LangFuse credentials."""
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    return Settings()


@pytest.fixture
def configured_settings(monkeypatch):
    """Create test settings with LangFuse credentials."""
    monkeypatch.setenv("LANGFUSE_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test-key")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test-key")
    monkeypatch.setenv("LANGFUSE_HOST", "https://test.langfuse.com")
    return Settings()


def test_langfuse_client_disabled(settings):
    """Test LangFuse client when disabled."""
    client = LangFuseClient(settings)
    assert client.enabled is False
    assert client.client is None


def test_langfuse_client_not_configured(settings):
    """Test LangFuse client without configuration."""
    client = LangFuseClient(settings)
    assert not client.settings.is_langfuse_configured()


def test_langfuse_client_configured(configured_settings):
    """Test LangFuse client is properly configured."""
    assert configured_settings.is_langfuse_configured()


def test_create_trace_when_disabled(settings):
    """Test creating trace when LangFuse is disabled."""
    client = LangFuseClient(settings)
    trace = client.create_trace(
        name="test_trace",
        user_id="test_user",
        session_id="test_session",
    )
    assert trace is None


def test_create_generation_when_disabled(settings):
    """Test creating generation when LangFuse is disabled."""
    client = LangFuseClient(settings)
    generation = client.create_generation(
        trace_id="test_trace",
        name="test_generation",
        model="gpt-4",
        input_data=["test input"],
        output_data=["test output"],
    )
    assert generation is None


def test_create_span_when_disabled(settings):
    """Test creating span when LangFuse is disabled."""
    client = LangFuseClient(settings)
    span = client.create_span(
        trace_id="test_trace",
        name="test_span",
    )
    assert span is None


def test_score_trace_when_disabled(settings):
    """Test scoring trace when LangFuse is disabled."""
    client = LangFuseClient(settings)
    result = client.score_trace(
        trace_id="test_trace",
        name="test_score",
        value=0.95,
    )
    assert result is False


def test_flush_when_disabled(settings):
    """Test flushing when LangFuse is disabled."""
    client = LangFuseClient(settings)
    # Should not raise an exception
    client.flush()


def test_shutdown_when_disabled(settings):
    """Test shutdown when LangFuse is disabled."""
    client = LangFuseClient(settings)
    # Should not raise an exception
    client.shutdown()

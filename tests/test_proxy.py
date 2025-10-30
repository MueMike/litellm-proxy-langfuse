"""Unit tests for proxy server."""

import pytest
from fastapi.testclient import TestClient

from src.proxy.server import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "litellm-proxy-langfuse"


def test_readiness_check(client):
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_list_models(client):
    """Test list models endpoint."""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0


def test_list_models_alternative_endpoint(client):
    """Test list models alternative endpoint."""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/v1/models")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

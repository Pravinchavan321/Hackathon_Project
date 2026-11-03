"""Phase 2 Verification Tests — Application Initialization and Health Checks."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import get_settings


@pytest.fixture
def client():
    return TestClient(app)


def test_settings_loaded():
    """Verify that configuration settings load successfully with defaults."""
    settings = get_settings()
    assert settings.APP_ENV in ["development", "testing", "production"]
    assert settings.STORAGE_MODE == "local"
    assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_health_endpoint(client):
    """Verify that the /health endpoint responds with 200 OK and valid payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "llm_provider" in data


def test_root_endpoint(client):
    """Verify that the / root endpoint returns operational metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AgentShield AI"
    assert data["status"] == "operational"
    assert data["docs"] == "/docs"

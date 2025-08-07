"""Example of testing with different settings configurations."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.core.settings import Settings, get_settings


class MockAgent:
    """Mock agent for testing."""

    def stream_query(self, **kwargs):
        yield "Test response"


@pytest.fixture
def app_with_slack_enabled():
    """Create test app with Slack enabled."""
    app = FastAPI()
    
    # Override dependencies
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=True)
    
    app.include_router(router)
    return app


@pytest.fixture
def app_with_slack_disabled():
    """Create test app with Slack disabled."""
    app = FastAPI()
    
    # Override dependencies
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=False)
    
    app.include_router(router)
    return app


def test_slack_enabled(app_with_slack_enabled):
    """Test that Slack endpoints work when enabled."""
    client = TestClient(app_with_slack_enabled)
    
    # This would normally require Slack environment variables
    # but for testing, we'd mock those as well
    response = client.get("/agent/slack/events")
    # The actual test would depend on your implementation
    assert response.status_code in [405, 500]  # Method not allowed or missing env vars


def test_slack_disabled(app_with_slack_disabled):
    """Test that Slack endpoints return 404 when disabled."""
    client = TestClient(app_with_slack_disabled)
    
    response = client.post("/agent/slack/events", json={})
    assert response.status_code == 404
    assert "not enabled" in response.json()["detail"]


# Example of parameterized testing
@pytest.mark.parametrize("enable_slack,expected_status", [
    (True, 500),   # Enabled but missing env vars
    (False, 404),  # Disabled
])
def test_slack_configuration(enable_slack, expected_status):
    """Test different Slack configurations."""
    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=enable_slack)
    app.include_router(router)
    
    client = TestClient(app)
    response = client.post("/agent/slack/events", json={})
    assert response.status_code == expected_status
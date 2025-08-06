"""Tests for main router integration."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router


def test_router_includes_all_platforms(test_client: TestClient):
    """Test that main router includes all platform routes."""
    # Test all endpoints are available
    response = test_client.get("/agent/slack/")
    assert response.status_code == 200

    response = test_client.get("/agent/discord/")
    assert response.status_code == 200

    response = test_client.get("/agent/webhook/")
    assert response.status_code == 200


def test_router_prefix():
    """Test that router has correct prefix."""
    assert router.prefix == "/agent"


def test_complete_integration():
    """Test complete integration with all platforms."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.include_router(router)
    client = TestClient(app)

    # Test all platform endpoints (only status endpoints now)
    endpoints = [
        ("/agent/slack/", "GET"),
        ("/agent/discord/", "GET"),
        ("/agent/webhook/", "GET"),
    ]

    for path, method in endpoints:
        response = client.get(path) if method == "GET" else client.post(path)
        assert response.status_code == 200, f"Failed for {method} {path}"

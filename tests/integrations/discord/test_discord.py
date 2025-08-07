"""Tests for Discord router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.core.settings import settings


def test_discord_status_endpoint(test_client: TestClient):
    """Test the Discord status endpoint."""
    response = test_client.get("/agent/discord/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_discord_disabled(monkeypatch):
    """Test Discord endpoint when disabled."""
    monkeypatch.setattr(settings, "disable_discord", True)

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/agent/discord/")
    assert response.status_code == 404
    assert "Discord integration is not enabled" in response.json()["detail"]

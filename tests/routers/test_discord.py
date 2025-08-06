"""Tests for Discord router."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router


def test_discord_status_endpoint(test_client: TestClient):
    """Test the Discord status endpoint."""
    response = test_client.get("/agent/discord/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_discord_interactions_post(test_client: TestClient):
    """Test POST to Discord interactions endpoint."""
    response = test_client.post("/agent/discord/interactions")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "platform": "discord"}


def test_discord_disabled():
    """Test Discord endpoint when disabled."""
    os.environ["DISABLE_DISCORD"] = "true"

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

    # Clean up
    del os.environ["DISABLE_DISCORD"]


def test_discord_interactions_disabled():
    """Test Discord interactions endpoint when disabled."""
    os.environ["DISABLE_DISCORD"] = "true"

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.include_router(router)
    client = TestClient(app)

    response = client.post("/agent/discord/interactions")
    assert response.status_code == 404
    assert "Discord integration is not enabled" in response.json()["detail"]

    # Clean up
    del os.environ["DISABLE_DISCORD"]
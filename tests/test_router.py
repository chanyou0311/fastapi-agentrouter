"""Tests for the router module."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import create_agent_router


def test_webhook_endpoint(test_client: TestClient):
    """Test the webhook endpoint."""
    response = test_client.post(
        "/agent/webhook",
        json={"message": "Hello", "user_id": "user123", "session_id": "session456"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Response to: Hello" in data["response"]
    assert data["session_id"] == "session456"


def test_webhook_missing_message(test_client: TestClient):
    """Test webhook endpoint with missing message."""
    response = test_client.post(
        "/agent/webhook",
        json={"user_id": "user123"},
    )

    assert response.status_code == 400
    assert "Message is required" in response.json()["detail"]


def test_webhook_disabled():
    """Test webhook endpoint when disabled."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    router = create_agent_router(get_agent, enable_webhook=False)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/webhook",
        json={"message": "Hello"},
    )

    assert response.status_code == 404
    assert "Webhook endpoint is not enabled" in response.json()["detail"]


def test_slack_disabled():
    """Test Slack endpoint when disabled."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    router = create_agent_router(get_agent, enable_slack=False)
    app.include_router(router)
    client = TestClient(app)

    response = client.post("/agent/slack/events")

    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_discord_disabled():
    """Test Discord endpoint when disabled."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    router = create_agent_router(get_agent, enable_discord=False)
    app.include_router(router)
    client = TestClient(app)

    response = client.post("/agent/discord/interactions")

    assert response.status_code == 404
    assert "Discord integration is not enabled" in response.json()["detail"]


def test_custom_prefix():
    """Test router with custom prefix."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    router = create_agent_router(get_agent, prefix="/custom")
    app.include_router(router)
    client = TestClient(app)

    # Should be available at custom prefix
    response = client.post(
        "/custom/webhook",
        json={"message": "test"},
    )
    assert response.status_code == 200

    # Should not be available at default prefix
    response = client.post(
        "/agent/webhook",
        json={"message": "test"},
    )
    assert response.status_code == 404

"""Tests for the router module."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router


def test_slack_endpoint(test_client: TestClient):
    """Test the Slack endpoint."""
    response = test_client.get("/agent/slack/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_discord_endpoint(test_client: TestClient):
    """Test the Discord endpoint."""
    response = test_client.get("/agent/discord/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_endpoint(test_client: TestClient):
    """Test the webhook endpoint."""
    response = test_client.get("/agent/webhook")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_slack_events_post(test_client: TestClient):
    """Test POST to Slack events endpoint."""
    response = test_client.post("/agent/slack/events")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "platform": "slack"}


def test_discord_interactions_post(test_client: TestClient):
    """Test POST to Discord interactions endpoint."""
    response = test_client.post("/agent/discord/interactions")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "platform": "discord"}


def test_webhook_post(test_client: TestClient):
    """Test POST to webhook endpoint."""
    response = test_client.post("/agent/webhook")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "platform": "webhook"}


def test_slack_disabled():
    """Test Slack endpoint when disabled."""
    os.environ["DISABLE_SLACK"] = "true"

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/agent/slack/")
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]

    # Clean up
    del os.environ["DISABLE_SLACK"]


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


def test_webhook_disabled():
    """Test webhook endpoint when disabled."""
    os.environ["DISABLE_WEBHOOK"] = "true"

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/agent/webhook")
    assert response.status_code == 404
    assert "Webhook endpoint is not enabled" in response.json()["detail"]

    # Clean up
    del os.environ["DISABLE_WEBHOOK"]


def test_no_agent_configured():
    """Test when agent is not configured."""
    app = FastAPI()
    # Don't override the dependency - should use placeholder
    app.include_router(router)
    client = TestClient(app)

    response = client.post("/agent/webhook")
    assert response.status_code == 500
    assert "Agent not configured" in response.json()["detail"]

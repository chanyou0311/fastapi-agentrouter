"""Tests for Slack router."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router


def test_slack_status_endpoint(test_client: TestClient):
    """Test the Slack status endpoint."""
    response = test_client.get("/agent/slack/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_slack_events_post(test_client: TestClient):
    """Test POST to Slack events endpoint."""
    response = test_client.post("/agent/slack/events")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "platform": "slack"}


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


def test_slack_events_disabled():
    """Test Slack events endpoint when disabled."""
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

    response = client.post("/agent/slack/events")
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]

    # Clean up
    del os.environ["DISABLE_SLACK"]

"""Tests for webhook router."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router


def test_webhook_status_endpoint(test_client: TestClient):
    """Test the webhook status endpoint."""
    response = test_client.get("/agent/webhook")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_post(test_client: TestClient):
    """Test POST to webhook endpoint."""
    response = test_client.post("/agent/webhook")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "platform": "webhook"}


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


def test_webhook_post_disabled():
    """Test webhook POST endpoint when disabled."""
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

    response = client.post("/agent/webhook")
    assert response.status_code == 404
    assert "Webhook endpoint is not enabled" in response.json()["detail"]

    # Clean up
    del os.environ["DISABLE_WEBHOOK"]

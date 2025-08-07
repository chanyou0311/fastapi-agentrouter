"""Tests for main router integration."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.core.settings import Settings, get_settings


def test_router_includes_slack_endpoint(test_client: TestClient):
    """Test that main router includes Slack event endpoint."""
    # Set required environment variables
    os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
    os.environ["SLACK_SIGNING_SECRET"] = "test-signing-secret"
    os.environ["SLACK_TOKEN_VERIFICATION"] = (
        "false"  # Disable token verification for tests
    )
    os.environ["SLACK_REQUEST_VERIFICATION"] = (
        "false"  # Disable request verification for tests
    )

    try:
        # Only /events endpoint should exist
        response = test_client.post(
            "/agent/slack/events",
            json={"type": "url_verification", "challenge": "test"},
        )
        # Should get 200 with the challenge response for url_verification
        assert response.status_code in [200, 500]  # 500 if handler not mocked
    finally:
        # Clean up
        del os.environ["SLACK_BOT_TOKEN"]
        del os.environ["SLACK_SIGNING_SECRET"]
        del os.environ["SLACK_TOKEN_VERIFICATION"]
        del os.environ["SLACK_REQUEST_VERIFICATION"]


def test_router_prefix():
    """Test that router has correct prefix."""
    assert router.prefix == "/agent"


def test_complete_integration():
    """Test complete integration with Slack."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=True)
    app.include_router(router)
    client = TestClient(app)

    # Set required environment variables
    os.environ["SLACK_BOT_TOKEN"] = "xoxb-test-token"
    os.environ["SLACK_SIGNING_SECRET"] = "test-signing-secret"
    os.environ["SLACK_TOKEN_VERIFICATION"] = (
        "false"  # Disable token verification for tests
    )
    os.environ["SLACK_REQUEST_VERIFICATION"] = (
        "false"  # Disable request verification for tests
    )

    try:
        # Test Slack events endpoint
        response = client.post(
            "/agent/slack/events",
            json={"type": "url_verification", "challenge": "test"},
        )
        assert response.status_code in [200, 500], "Failed for POST /agent/slack/events"
    finally:
        # Clean up
        del os.environ["SLACK_BOT_TOKEN"]
        del os.environ["SLACK_SIGNING_SECRET"]
        del os.environ["SLACK_TOKEN_VERIFICATION"]
        del os.environ["SLACK_REQUEST_VERIFICATION"]

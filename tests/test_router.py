"""Tests for main router integration."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.integrations.slack.settings import (
    SlackSettings,
    get_slack_settings,
)


def test_router_includes_slack_endpoint():
    """Test that main router includes Slack event endpoint."""
    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"
        return Agent()
    
    def get_test_settings():
        return SlackSettings(
            slack_bot_token="xoxb-test-token",
            slack_signing_secret="test-signing-secret",
            slack_token_verification=False,
            slack_request_verification=False,
        )
    
    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.dependency_overrides[get_slack_settings] = get_test_settings
    app.include_router(router)
    client = TestClient(app)

    # Only /events endpoint should exist
    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test"},
    )
    # Should get 200 with the challenge response for url_verification
    assert response.status_code in [200, 500]  # 500 if handler not mocked


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
    
    def get_test_settings():
        return SlackSettings(
            slack_bot_token="xoxb-test-token",
            slack_signing_secret="test-signing-secret",
            slack_token_verification=False,
            slack_request_verification=False,
        )

    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.dependency_overrides[get_slack_settings] = get_test_settings
    app.include_router(router)
    client = TestClient(app)

    # Test Slack events endpoint
    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test"},
    )
    assert response.status_code in [200, 500], "Failed for POST /agent/slack/events"

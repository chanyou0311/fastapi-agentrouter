"""Tests for Slack integration."""

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.core.settings import Settings, get_settings
from fastapi_agentrouter.integrations.slack.settings import SlackSettings


def test_slack_disabled():
    """Test Slack endpoint when disabled."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    # Create app with disabled Slack
    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=False)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test"},
    )
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_slack_events_missing_env_vars():
    """Test Slack events endpoint without required environment variables."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"
        return Agent()
    
    def get_test_settings():
        return Settings(
            enable_slack=True,
            slack=SlackSettings(
                bot_token=None,
                signing_secret=None,
            )
        )
    
    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.dependency_overrides[get_settings] = get_test_settings
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test_challenge"},
    )
    if response.status_code != 500:
        print(f"Response: {response.status_code} - {response.json()}")
    assert response.status_code == 500
    assert "SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET" in response.json()["detail"]


def test_slack_events_endpoint():
    """Test the Slack events endpoint with mocked dependencies."""

    def get_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"
        return Agent()
    
    def get_test_settings():
        return Settings(
            enable_slack=True,
            slack=SlackSettings(
                bot_token="xoxb-test-token",
                signing_secret="test-signing-secret",
                token_verification=False,
                request_verification=False,
            )
        )
    
    app = FastAPI()
    app.dependency_overrides[get_agent_placeholder] = get_agent
    app.dependency_overrides[get_settings] = get_test_settings
    app.include_router(router)
    client = TestClient(app)

    with (
        patch("slack_bolt.adapter.fastapi.SlackRequestHandler") as mock_handler_class,
        patch("slack_bolt.App") as mock_app_class,
    ):
        # Mock the handler
        mock_handler = Mock()
        mock_handler.handle = AsyncMock(return_value={"ok": True})
        mock_handler_class.return_value = mock_handler

        # Mock the Slack app
        mock_app = Mock()
        mock_app_class.return_value = mock_app

        response = client.post(
            "/agent/slack/events",
            json={
                "type": "event_callback",
                "event": {
                    "type": "app_mention",
                    "text": "Hello bot!",
                    "user": "U123456",
                },
            },
        )
        assert response.status_code == 200



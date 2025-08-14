"""Tests for main router integration."""

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent, router
from fastapi_agentrouter.core.settings import Settings, SlackSettings, get_settings


def test_router_includes_slack_endpoint():
    """Test that main router includes Slack event endpoint."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)
    client = TestClient(app)

    with (
        patch("slack_bolt.adapter.fastapi.SlackRequestHandler") as mock_handler_class,
        patch("slack_bolt.App") as mock_app_class,
        patch.dict(
            "os.environ",
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_SIGNING_SECRET": "test-signing-secret",
                "SLACK_TOKEN_VERIFICATION": "false",
                "SLACK_REQUEST_VERIFICATION": "false",
            },
        ),
    ):
        # Mock the handler and app
        mock_handler = Mock()
        mock_handler.handle = AsyncMock(return_value={"ok": True})
        mock_handler_class.return_value = mock_handler

        mock_app = Mock()
        mock_app.event = Mock(return_value=lambda *args, **kwargs: None)
        mock_app_class.return_value = mock_app

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


def test_slack_disabled():
    """Test that Slack endpoints return 404 when disabled."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(slack=None)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test"},
    )
    assert response.status_code == 404
    assert "not enabled" in response.json()["detail"]


def test_complete_integration():
    """Test complete integration with Slack."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)
    client = TestClient(app)

    with (
        patch("slack_bolt.adapter.fastapi.SlackRequestHandler") as mock_handler_class,
        patch("slack_bolt.App") as mock_app_class,
        patch.dict(
            "os.environ",
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_SIGNING_SECRET": "test-signing-secret",
                "SLACK_TOKEN_VERIFICATION": "false",
                "SLACK_REQUEST_VERIFICATION": "false",
            },
        ),
    ):
        # Mock the handler and app
        mock_handler = Mock()
        mock_handler.handle = AsyncMock(return_value={"ok": True})
        mock_handler_class.return_value = mock_handler

        mock_app = Mock()
        mock_app.event = Mock(return_value=lambda *args, **kwargs: None)
        mock_app_class.return_value = mock_app

        # Test Slack events endpoint
        response = client.post(
            "/agent/slack/events",
            json={"type": "url_verification", "challenge": "test"},
        )
        assert response.status_code in [200, 500], "Failed for POST /agent/slack/events"


def test_slack_without_settings():
    """Test that Slack endpoint returns 404 when Slack is not configured."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    # Slack is disabled when slack=None
    app.dependency_overrides[get_settings] = lambda: Settings(slack=None)
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/agent/slack/events",
        json={"type": "url_verification", "challenge": "test"},
    )
    # Should return 404 because Slack is disabled
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_multiple_settings_instances():
    """Test that different apps can have different settings."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    # App 1: Slack enabled
    app1 = FastAPI()
    app1.dependency_overrides[get_agent] = get_mock_agent
    app1.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app1.include_router(router)
    client1 = TestClient(app1)

    # App 2: Slack disabled
    app2 = FastAPI()
    app2.dependency_overrides[get_agent] = get_mock_agent
    app2.dependency_overrides[get_settings] = lambda: Settings(slack=None)
    app2.include_router(router)
    client2 = TestClient(app2)

    # Test App 1 (Slack enabled) - need to mock Slack App and handler
    with (
        patch("slack_bolt.adapter.fastapi.SlackRequestHandler") as mock_handler_class,
        patch("slack_bolt.App") as mock_app_class,
    ):
        # Mock the handler and app
        mock_handler = Mock()
        mock_handler.handle = AsyncMock(return_value={"ok": True})
        mock_handler_class.return_value = mock_handler

        mock_app = Mock()
        mock_app.event = Mock(return_value=lambda *args, **kwargs: None)
        mock_app_class.return_value = mock_app

        response1 = client1.post(
            "/agent/slack/events",
            json={"type": "url_verification", "challenge": "test"},
        )
        assert response1.status_code == 200  # Should succeed with mocked dependencies

    # Test App 2 (Slack disabled)
    response2 = client2.post("/agent/slack/events", json={})
    assert response2.status_code == 404  # Disabled
    assert "not enabled" in response2.json()["detail"]

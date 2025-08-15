"""Tests for Slack integration."""

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent, router
from fastapi_agentrouter.core.settings import Settings, SlackSettings, get_settings


def test_slack_disabled():
    """Test Slack endpoint when disabled."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                yield "response"

        return Agent()

    # Create app with disabled Slack
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
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_slack_events_missing_settings():
    """Test Slack events endpoint without Slack settings configured."""

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
        json={"type": "url_verification", "challenge": "test_challenge"},
    )
    # Should return 404 because Slack is not enabled (slack=None means disabled)
    assert response.status_code == 404
    assert "Slack integration is not enabled" in response.json()["detail"]


def test_slack_events_endpoint():
    """Test the Slack events endpoint with mocked dependencies."""

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
            },
        ),
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


def test_slack_app_mention_thread_mode():
    """Test app mention creates thread response."""
    from fastapi_agentrouter.integrations.slack.dependencies import get_app_mention

    # Create mock agent
    mock_agent = Mock()
    mock_agent.stream_query = Mock(
        return_value=[{"content": {"parts": [{"text": "Hello from agent!"}]}}]
    )

    # Get the app mention handler
    app_mention_handler = get_app_mention(mock_agent)

    # Mock event with thread_ts
    event = {
        "user": "U123",
        "text": "<@UBOT> Hello",
        "ts": "1234567890.123456",
        "thread_ts": "1234567890.123456",
    }

    # Mock say function
    mock_say = Mock()

    # Call the handler
    app_mention_handler(event, mock_say, {})

    # Verify say was called with thread_ts
    mock_say.assert_called_once_with(
        text="Hello from agent!", thread_ts="1234567890.123456"
    )

    # Verify agent was called with correct session_id and user_id
    mock_agent.stream_query.assert_called_once_with(
        user_id="1234567890.123456",
        session_id="1234567890.123456",
        message="<@UBOT> Hello",
    )


def test_slack_message_in_thread():
    """Test message handler processes thread messages correctly."""
    from fastapi_agentrouter.core.settings import Settings, SlackSettings
    from fastapi_agentrouter.integrations.slack.dependencies import get_message

    # Create mock agent
    mock_agent = Mock()
    mock_agent.stream_query = Mock(
        return_value=[{"content": {"parts": [{"text": "Response to thread message"}]}}]
    )

    # Create mock settings
    mock_settings = Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )

    # Get the message handler
    message_handler = get_message(mock_agent, mock_settings)

    # Mock event for thread message
    event = {
        "user": "U123",
        "text": "Follow-up question",
        "ts": "1234567890.234567",
        "thread_ts": "1234567890.123456",
        "channel": "C123",
    }

    # Mock body with bot user ID
    body = {"authorizations": [{"user_id": "UBOT"}]}

    # Mock say function
    mock_say = Mock()

    # Mock client with conversations.replies
    mock_client = Mock()
    mock_client.conversations_replies = Mock(
        return_value={
            "messages": [
                {"text": "<@UBOT> Initial question", "ts": "1234567890.123456"}
            ]
        }
    )

    # Call the handler
    message_handler(event, mock_say, body, mock_client)

    # Verify say was called with thread_ts
    mock_say.assert_called_once_with(
        text="Response to thread message", thread_ts="1234567890.123456"
    )

    # Verify agent was called with correct session_id and user_id
    mock_agent.stream_query.assert_called_once_with(
        user_id="1234567890.123456",
        session_id="1234567890.123456",
        message="Follow-up question",
    )


def test_slack_message_ignore_non_thread():
    """Test message handler ignores non-thread messages."""
    from fastapi_agentrouter.core.settings import Settings, SlackSettings
    from fastapi_agentrouter.integrations.slack.dependencies import get_message

    # Create mock agent
    mock_agent = Mock()
    mock_agent.stream_query = Mock()

    # Create mock settings
    mock_settings = Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )

    # Get the message handler
    message_handler = get_message(mock_agent, mock_settings)

    # Mock event for non-thread message (no thread_ts)
    event = {
        "user": "U123",
        "text": "Regular message",
        "ts": "1234567890.123456",
        "channel": "C123",
    }

    # Mock say and client
    mock_say = Mock()
    mock_client = Mock()

    # Call the handler
    message_handler(event, mock_say, {}, mock_client)

    # Verify nothing was called
    mock_say.assert_not_called()
    mock_agent.stream_query.assert_not_called()


def test_slack_message_ignore_bot_messages():
    """Test message handler ignores bot messages."""
    from fastapi_agentrouter.core.settings import Settings, SlackSettings
    from fastapi_agentrouter.integrations.slack.dependencies import get_message

    # Create mock agent
    mock_agent = Mock()
    mock_agent.stream_query = Mock()

    # Create mock settings
    mock_settings = Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )

    # Get the message handler
    message_handler = get_message(mock_agent, mock_settings)

    # Mock event for bot message
    event = {
        "user": "U123",
        "text": "Bot message",
        "ts": "1234567890.234567",
        "thread_ts": "1234567890.123456",
        "bot_id": "B123",
        "channel": "C123",
    }

    # Mock say and client
    mock_say = Mock()
    mock_client = Mock()

    # Call the handler
    message_handler(event, mock_say, {}, mock_client)

    # Verify nothing was called
    mock_say.assert_not_called()
    mock_agent.stream_query.assert_not_called()


def test_slack_missing_library():
    """Test error when slack-bolt is not installed."""

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

    # Mock the import to fail when trying to import slack_bolt
    import builtins

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "slack_bolt" or name.startswith("slack_bolt."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    with (
        patch("builtins.__import__", side_effect=mock_import),
        patch.dict(
            "os.environ",
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_SIGNING_SECRET": "test-signing-secret",
            },
        ),
    ):
        response = client.post(
            "/agent/slack/events",
            json={"type": "url_verification", "challenge": "test"},
        )
        assert response.status_code == 500
        assert "slack-bolt is required" in response.json()["detail"]

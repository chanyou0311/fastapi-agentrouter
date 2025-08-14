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


def test_slack_thread_reply():
    """Test that bot replies in thread when mentioned."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                # Check that session_id is properly set for thread
                assert "session_id" in kwargs
                assert kwargs["session_id"].startswith("C123_")
                yield {"content": {"parts": [{"text": "Thread reply"}]}}

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)

    with (
        patch("slack_bolt.App") as mock_app_class,
        patch("slack_bolt.adapter.fastapi.SlackRequestHandler"),
    ):
        # Create mock say function to verify thread reply
        say_called_with = {}

        def mock_say(**kwargs):
            say_called_with.update(kwargs)

        # Mock the Slack app
        mock_app = Mock()
        mock_app.event = Mock(side_effect=lambda event_type: lambda **kwargs: None)
        mock_app_class.return_value = mock_app

        # Import after patching to get our dependencies
        from fastapi_agentrouter.integrations.slack.dependencies import get_app_mention

        # Get the handler and test it
        agent = get_mock_agent()
        app_mention_handler = get_app_mention(agent)

        # Test app mention in thread
        event = {
            "type": "app_mention",
            "text": "<@U123> help me",
            "user": "U456",
            "channel": "C123",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.123456",  # Same as ts for thread start
        }

        app_mention_handler(event, mock_say, {})

        # Verify say was called with thread_ts
        assert "thread_ts" in say_called_with
        assert say_called_with["thread_ts"] == "1234567890.123456"
        assert say_called_with["text"] == "Thread reply"


def test_slack_message_in_thread():
    """Test that bot responds to messages in threads where it was mentioned."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                # Verify session continuity
                assert kwargs["session_id"] == "C123_1234567890.000000"
                assert kwargs["user_id"] == "1234567890.000000"
                yield {"content": {"parts": [{"text": "Continued conversation"}]}}

        return Agent()

    app = FastAPI()
    app.dependency_overrides[get_agent] = get_mock_agent
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)

    with patch("slack_bolt.App"):
        # Create mock client and say
        mock_client = Mock()
        mock_client.auth_test = Mock(return_value={"user_id": "U_BOT"})
        mock_client.conversations_replies = Mock(
            return_value={
                "messages": [
                    {"text": "<@U_BOT> initial mention", "ts": "1234567890.000000"},
                    {"text": "follow up message", "ts": "1234567890.000001"},
                ]
            }
        )

        say_called_with = {}

        def mock_say(**kwargs):
            say_called_with.update(kwargs)

        # Import and get handler
        from fastapi_agentrouter.integrations.slack.dependencies import get_message

        agent = get_mock_agent()
        message_handler = get_message(agent)

        # Test message in thread (not a mention)
        event = {
            "type": "message",
            "text": "follow up question",
            "user": "U456",
            "channel": "C123",
            "ts": "1234567890.000002",
            "thread_ts": "1234567890.000000",  # Thread started earlier
        }

        message_handler(event, mock_say, {}, mock_client)

        # Verify response was sent to thread
        assert say_called_with["thread_ts"] == "1234567890.000000"
        assert say_called_with["text"] == "Continued conversation"


def test_slack_message_with_aside_ignored():
    """Test that messages with (aside) are ignored unless bot is mentioned."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                # Should not be called for (aside) messages
                raise AssertionError("Agent should not be called for (aside) messages")

        return Agent()

    with patch("slack_bolt.App"):
        # Create mock client
        mock_client = Mock()
        mock_client.auth_test = Mock(return_value={"user_id": "U_BOT"})
        mock_client.conversations_replies = Mock(
            return_value={
                "messages": [
                    {"text": "<@U_BOT> start", "ts": "1234567890.000000"},
                ]
            }
        )

        say_called = False

        def mock_say(**kwargs):
            nonlocal say_called
            say_called = True

        from fastapi_agentrouter.integrations.slack.dependencies import get_message

        agent = get_mock_agent()
        message_handler = get_message(agent)

        # Test message with (aside) - should be ignored
        event = {
            "type": "message",
            "text": "(aside) this should be ignored",
            "user": "U456",
            "channel": "C123",
            "ts": "1234567890.000001",
            "thread_ts": "1234567890.000000",
        }

        message_handler(event, mock_say, {}, mock_client)

        # Verify say was not called
        assert not say_called


def test_slack_mention_with_aside_processed():
    """Test that bot mention with (aside) is still processed."""

    def get_mock_agent():
        class Agent:
            def stream_query(self, **kwargs):
                # Should be called even with (aside) when mentioned
                yield {"content": {"parts": [{"text": "Processed with aside"}]}}

        return Agent()

    with patch("slack_bolt.App"):
        # Create mock client
        mock_client = Mock()
        mock_client.auth_test = Mock(return_value={"user_id": "U_BOT"})
        mock_client.conversations_replies = Mock(
            return_value={
                "messages": [
                    {
                        "text": "<@U_BOT> (aside) but still process",
                        "ts": "1234567890.000000",
                    },
                ]
            }
        )

        say_called_with = {}

        def mock_say(**kwargs):
            say_called_with.update(kwargs)

        from fastapi_agentrouter.integrations.slack.dependencies import get_message

        agent = get_mock_agent()
        message_handler = get_message(agent)

        # Test message with (aside) but bot is mentioned
        event = {
            "type": "message",
            "text": "<@U_BOT> (aside) but process this",
            "user": "U456",
            "channel": "C123",
            "ts": "1234567890.000001",
            "thread_ts": "1234567890.000000",
        }

        message_handler(event, mock_say, {}, mock_client)

        # Verify say was called despite (aside)
        assert say_called_with["text"] == "Processed with aside"

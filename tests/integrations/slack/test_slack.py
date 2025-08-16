"""Tests for Slack integration."""

from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent, router
from fastapi_agentrouter.core.settings import Settings, SlackSettings, get_settings
from fastapi_agentrouter.integrations.slack.dependencies import get_app_mention


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


def test_thread_based_session_new_thread():
    """Test that a new thread creates a new session."""
    mock_agent = Mock()
    mock_agent.list_sessions = Mock(return_value={"sessions": []})
    mock_agent.create_session = Mock(return_value={"id": "session_123"})
    mock_agent.stream_query = Mock(
        return_value=[{"content": {"parts": [{"text": "Response text"}]}}]
    )

    app_mention_handler = get_app_mention(mock_agent)

    mock_say = Mock()
    event = {
        "user": "U123456",
        "text": "Hello bot!",
        "channel": "C789012",
        "ts": "1234567890.123456",
    }
    body = {}

    app_mention_handler(event, mock_say, body)

    # Verify thread ID is created correctly
    expected_thread_id = "C789012:1234567890.123456"

    # Verify list_sessions was called with thread ID
    mock_agent.list_sessions.assert_called_once_with(user_id=expected_thread_id)

    # Verify create_session was called with thread ID
    mock_agent.create_session.assert_called_once_with(user_id=expected_thread_id)

    # Verify stream_query was called with thread ID and session ID
    mock_agent.stream_query.assert_called_once_with(
        user_id=expected_thread_id, session_id="session_123", message="Hello bot!"
    )

    # Verify say was called with channel and thread_ts
    mock_say.assert_called_once_with(
        text="Response text", channel="C789012", thread_ts="1234567890.123456"
    )


def test_thread_based_session_existing_thread():
    """Test that an existing thread reuses the same session."""
    mock_agent = Mock()
    mock_agent.list_sessions = Mock(
        return_value={"sessions": [{"id": "existing_session_456"}]}
    )
    mock_agent.create_session = Mock()  # Should not be called
    mock_agent.stream_query = Mock(
        return_value=[
            {"content": {"parts": [{"text": "Response from existing session"}]}}
        ]
    )

    app_mention_handler = get_app_mention(mock_agent)

    mock_say = Mock()
    event = {
        "user": "U123456",
        "text": "Follow-up message",
        "channel": "C789012",
        "ts": "1234567890.654321",
        "thread_ts": "1234567890.123456",  # Message in a thread
    }
    body = {}

    app_mention_handler(event, mock_say, body)

    # Verify thread ID is created correctly
    expected_thread_id = "C789012:1234567890.123456"

    # Verify list_sessions was called with thread ID
    mock_agent.list_sessions.assert_called_once_with(user_id=expected_thread_id)

    # Verify create_session was NOT called
    mock_agent.create_session.assert_not_called()

    # Verify stream_query was called with existing session ID
    mock_agent.stream_query.assert_called_once_with(
        user_id=expected_thread_id,
        session_id="existing_session_456",
        message="Follow-up message",
    )

    # Verify say was called with channel and thread_ts
    mock_say.assert_called_once_with(
        text="Response from existing session",
        channel="C789012",
        thread_ts="1234567890.123456",
    )


def test_thread_based_session_different_threads():
    """Test that different threads get different sessions."""
    mock_agent = Mock()

    # First call for thread1 - no existing session
    # Second call for thread2 - no existing session
    mock_agent.list_sessions = Mock(side_effect=[{"sessions": []}, {"sessions": []}])
    mock_agent.create_session = Mock(
        side_effect=[{"id": "session_thread1"}, {"id": "session_thread2"}]
    )
    mock_agent.stream_query = Mock(
        return_value=[{"content": {"parts": [{"text": "Response"}]}}]
    )

    app_mention_handler = get_app_mention(mock_agent)
    mock_say = Mock()

    # First thread
    event1 = {
        "user": "U123456",
        "text": "Message in thread 1",
        "channel": "C789012",
        "ts": "1111111111.111111",
    }
    app_mention_handler(event1, mock_say, {})

    # Second thread
    event2 = {
        "user": "U123456",
        "text": "Message in thread 2",
        "channel": "C789012",
        "ts": "2222222222.222222",
    }
    app_mention_handler(event2, mock_say, {})

    # Verify different thread IDs were used
    thread_id1 = "C789012:1111111111.111111"
    thread_id2 = "C789012:2222222222.222222"

    # Verify list_sessions was called for both threads
    assert mock_agent.list_sessions.call_count == 2
    mock_agent.list_sessions.assert_any_call(user_id=thread_id1)
    mock_agent.list_sessions.assert_any_call(user_id=thread_id2)

    # Verify create_session was called for both threads
    assert mock_agent.create_session.call_count == 2
    mock_agent.create_session.assert_any_call(user_id=thread_id1)
    mock_agent.create_session.assert_any_call(user_id=thread_id2)

    # Verify stream_query was called with different sessions
    assert mock_agent.stream_query.call_count == 2
    mock_agent.stream_query.assert_any_call(
        user_id=thread_id1, session_id="session_thread1", message="Message in thread 1"
    )
    mock_agent.stream_query.assert_any_call(
        user_id=thread_id2, session_id="session_thread2", message="Message in thread 2"
    )


def test_thread_based_session_multiple_messages_same_thread():
    """Test that multiple messages in the same thread use the same session."""
    mock_agent = Mock()

    # First message creates a session, second message finds it
    mock_agent.list_sessions = Mock(
        side_effect=[
            {"sessions": []},  # First call - no session exists
            {
                "sessions": [{"id": "session_same_thread"}]
            },  # Second call - session exists
        ]
    )
    mock_agent.create_session = Mock(return_value={"id": "session_same_thread"})
    mock_agent.stream_query = Mock(
        side_effect=[
            [{"content": {"parts": [{"text": "First response"}]}}],
            [{"content": {"parts": [{"text": "Second response"}]}}],
        ]
    )

    app_mention_handler = get_app_mention(mock_agent)
    mock_say = Mock()

    # First message in thread
    event1 = {
        "user": "U123456",
        "text": "First message",
        "channel": "C789012",
        "ts": "1234567890.123456",
        "thread_ts": "1234567890.123456",
    }
    app_mention_handler(event1, mock_say, {})

    # Second message in same thread
    event2 = {
        "user": "U123456",
        "text": "Second message",
        "channel": "C789012",
        "ts": "1234567890.789012",
        "thread_ts": "1234567890.123456",  # Same thread_ts
    }
    app_mention_handler(event2, mock_say, {})

    thread_id = "C789012:1234567890.123456"

    # Verify create_session was called only once
    mock_agent.create_session.assert_called_once_with(user_id=thread_id)

    # Verify both messages used the same session ID
    assert mock_agent.stream_query.call_count == 2
    mock_agent.stream_query.assert_any_call(
        user_id=thread_id, session_id="session_same_thread", message="First message"
    )
    mock_agent.stream_query.assert_any_call(
        user_id=thread_id, session_id="session_same_thread", message="Second message"
    )

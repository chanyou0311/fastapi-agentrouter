"""Tests for class-based event handlers."""

from unittest.mock import Mock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter.core.config import AgentConfig
from fastapi_agentrouter.core.dependencies import AgentProtocol
from fastapi_agentrouter.core.handlers import (
    BaseEventHandler,
    ConversationManager,
    SlackEventHandler,
    WebhookEventHandler,
)
from fastapi_agentrouter.core.security import SecurityContext
from fastapi_agentrouter.core.settings import Settings


class MockAgent(AgentProtocol):
    """Mock agent for testing."""

    def stream_query(self, *, message, user_id=None, session_id=None, **kwargs):
        yield "Mock response"


@pytest.mark.asyncio
async def test_base_event_handler():
    """Test BaseEventHandler functionality."""
    agent = MockAgent()
    settings = Settings()
    context = SecurityContext(user_id="test_user", platform="test")

    handler = BaseEventHandler(agent, settings, context)

    # Process event
    event = {"id": "event1", "type": "test"}
    result = await handler.process_event(event)

    assert result["status"] == "processed"
    assert result["event_id"] == "event1"
    assert handler.processed_count == 1
    assert len(handler.event_queue) == 1

    # Get stats
    stats = handler.get_stats()
    assert stats["processed_count"] == 1
    assert stats["queue_size"] == 1
    assert stats["platform"] == "test"


@pytest.mark.asyncio
async def test_slack_event_handler():
    """Test SlackEventHandler functionality."""
    agent = MockAgent()
    settings = Settings()
    context = SecurityContext(user_id="slack_user", platform="slack")

    handler = SlackEventHandler(agent, settings, context)

    # Process Slack event
    event = {
        "type": "message",
        "channel": "C123",
        "ts": "1234567890.123456",
        "user": "U123",
        "text": "Hello bot",
    }

    result = await handler.process_event(event)

    assert result["text"] == "Mock response"
    assert result["channel"] == "C123"
    assert result["thread_ts"] == "1234567890.123456"

    # Check thread context was saved
    thread_key = "C123_1234567890.123456"
    assert thread_key in handler.thread_contexts
    assert len(handler.thread_contexts[thread_key]) == 1

    # Test channel settings
    handler.update_channel_settings("C123", {"response_style": "formal"})
    assert handler.channel_settings["C123"]["response_style"] == "formal"

    # Process with formal style
    result = await handler.process_event(event)
    assert "Thank you for your inquiry" in result["text"]
    assert "Best regards" in result["text"]

    # Clear thread context
    handler.clear_thread_context("C123", "1234567890.123456")
    assert thread_key not in handler.thread_contexts


@pytest.mark.asyncio
async def test_webhook_event_handler():
    """Test WebhookEventHandler with retry logic."""
    agent = MockAgent()
    settings = Settings()
    context = SecurityContext(user_id="webhook_user", platform="webhook")
    config = AgentConfig(retry_count=2)

    handler = WebhookEventHandler(agent, settings, context, config)

    # Test successful processing
    event = {"message": "Test message"}
    result = await handler.process_event(event)

    assert result["status"] == "success"
    assert result["response"] == "Mock response"
    assert result["retry_count"] == 0

    # Test with error and retry
    failing_agent = Mock(spec=AgentProtocol)
    failing_agent.stream_query = Mock(side_effect=Exception("Processing failed"))

    handler.agent = failing_agent
    event = {"message": "Fail message"}

    # First attempt should retry
    result = await handler.process_event(event)
    assert result["status"] == "retry"
    assert result["retry_count"] == 1
    assert len(handler.retry_queue) == 1

    # Simulate max retries exceeded
    event["_retry_count"] = 2
    result = await handler.process_event(event)
    assert result["status"] == "failed"
    assert "Max retries" in result["error"]
    assert len(handler.failed_events) == 1


@pytest.mark.asyncio
async def test_webhook_retry_queue_processing():
    """Test processing of retry queue."""
    agent = MockAgent()
    settings = Settings()
    context = SecurityContext()
    config = AgentConfig(retry_count=3)

    handler = WebhookEventHandler(agent, settings, context, config)

    # Add events to retry queue
    handler.retry_queue.append({"message": "retry1", "_retry_count": 1})
    handler.retry_queue.append({"message": "retry2", "_retry_count": 1})

    # Process retry queue
    result = await handler.process_retry_queue()

    assert result["processed"] == 2
    assert result["failed"] == 0
    assert len(handler.retry_queue) == 0


def test_conversation_manager():
    """Test ConversationManager functionality."""
    agent = MockAgent()
    settings = Settings()

    manager = ConversationManager(agent, settings)

    # Add messages
    manager.add_message("conv1", "user", "Hello", {"user_id": "user1"})
    manager.add_message("conv1", "assistant", "Hi there!")

    # Get history
    history = manager.get_history("conv1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"

    # Get limited history
    manager.add_message("conv1", "user", "Another message")
    limited = manager.get_history("conv1", limit=2)
    assert len(limited) == 2

    # Clear conversation
    manager.clear_conversation("conv1")
    assert manager.get_history("conv1") == []


@pytest.mark.asyncio
async def test_conversation_manager_process_message():
    """Test conversation message processing."""
    agent = MockAgent()
    settings = Settings()

    manager = ConversationManager(agent, settings)

    # Process message
    response = await manager.process_message("conv1", "Test message", user_id="user123")

    assert response == "Mock response"

    # Check history was updated
    history = manager.get_history("conv1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Test message"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Mock response"


def test_handler_dependency_injection():
    """Test handler as FastAPI dependency."""
    app = FastAPI()

    # Mock dependencies
    mock_agent = MockAgent()
    mock_settings = Settings()
    mock_context = SecurityContext(user_id="test", platform="test")

    # Override dependencies
    from fastapi_agentrouter.core.dependencies import get_agent_placeholder
    from fastapi_agentrouter.core.security import get_security_context

    app.dependency_overrides[get_agent_placeholder] = lambda: mock_agent
    app.dependency_overrides[lambda: settings] = lambda: mock_settings
    app.dependency_overrides[get_security_context] = lambda: mock_context

    @app.post("/slack/event")
    async def slack_event(handler: SlackEventHandler = Depends(), event: dict = {}):
        result = await handler.process_event(event)
        return result

    client = TestClient(app)

    # Test endpoint
    response = client.post(
        "/slack/event",
        json={
            "type": "message",
            "channel": "C123",
            "text": "test",
            "user": "U123",
            "ts": "123.456",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Mock response"
    assert data["channel"] == "C123"


def test_conversation_manager_max_history():
    """Test conversation history trimming."""
    agent = MockAgent()
    settings = Settings()

    manager = ConversationManager(agent, settings)
    manager.max_history_length = 5

    # Add more than max messages
    for i in range(10):
        manager.add_message("conv1", "user", f"Message {i}")

    # Should only keep last 5
    history = manager.get_history("conv1")
    assert len(history) == 5
    assert history[0]["content"] == "Message 5"
    assert history[-1]["content"] == "Message 9"


def test_webhook_message_extraction():
    """Test webhook message extraction from different formats."""
    agent = MockAgent()
    settings = Settings()
    context = SecurityContext()
    config = AgentConfig()

    handler = WebhookEventHandler(agent, settings, context, config)

    # Test message field
    assert handler._extract_message({"message": "test1"}) == "test1"

    # Test text field
    assert handler._extract_message({"text": "test2"}) == "test2"

    # Test body as string
    assert handler._extract_message({"body": "test3"}) == "test3"

    # Test body as dict
    body_dict = {"key": "value"}
    result = handler._extract_message({"body": body_dict})
    assert result == '{"key": "value"}'

    # Test fallback to full event
    event = {"other": "data"}
    result = handler._extract_message(event)
    assert result == '{"other": "data"}'

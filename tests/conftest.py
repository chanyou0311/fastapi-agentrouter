"""Test configuration and fixtures."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent, router
from fastapi_agentrouter.core.settings import Settings, SlackSettings, get_settings


class MockAgent:
    """Mock agent for testing."""

    def __init__(self):
        self.stream_query_mock = Mock()

    def stream_query(self, *, message: str, user_id=None, session_id=None):
        """Mock stream_query method."""
        self.stream_query_mock(message=message, user_id=user_id, session_id=session_id)
        # Return mock events
        yield type("Event", (), {"content": f"Response to: {message}"})()


@pytest.fixture
def mock_agent() -> MockAgent:
    """Provide a mock agent for testing."""
    return MockAgent()


@pytest.fixture
def get_agent_factory(mock_agent: MockAgent):
    """Factory for get_agent dependency."""

    def get_agent():
        return mock_agent

    return get_agent


@pytest.fixture
def test_app(get_agent_factory) -> FastAPI:
    """Create a test FastAPI application with Slack enabled."""
    app = FastAPI()
    # Override the placeholder dependency
    app.dependency_overrides[get_agent] = get_agent_factory
    # Enable Slack for testing by default
    app.dependency_overrides[get_settings] = lambda: Settings(
        slack=SlackSettings(bot_token="test-token", signing_secret="test-secret")
    )
    app.include_router(router)
    return app


@pytest.fixture
def test_app_slack_disabled(get_agent_factory) -> FastAPI:
    """Create a test FastAPI application with Slack disabled."""
    app = FastAPI()
    # Override the placeholder dependency
    app.dependency_overrides[get_agent] = get_agent_factory
    # Disable Slack
    app.dependency_overrides[get_settings] = lambda: Settings(slack=None)
    app.include_router(router)
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Create a test client with Slack enabled."""
    return TestClient(test_app)


@pytest.fixture
def test_client_slack_disabled(test_app_slack_disabled: FastAPI) -> TestClient:
    """Create a test client with Slack disabled."""
    return TestClient(test_app_slack_disabled)


@pytest.fixture
def mock_slack_app():
    """Mock Slack App for testing."""
    with patch("slack_bolt.App") as mock_app_class:
        mock_app = Mock()
        mock_app.event = Mock(return_value=lambda *args, **kwargs: None)
        mock_app_class.return_value = mock_app
        yield mock_app


@pytest.fixture
def mock_slack_handler():
    """Mock Slack request handler."""
    with patch("slack_bolt.adapter.fastapi.SlackRequestHandler") as mock_handler_class:
        mock_handler = Mock()
        mock_handler.handle = AsyncMock(return_value={"ok": True})
        mock_handler_class.return_value = mock_handler
        yield mock_handler

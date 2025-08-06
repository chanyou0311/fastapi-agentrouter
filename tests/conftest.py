"""Test configuration and fixtures."""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import setup_router


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
    """Create a test FastAPI application."""
    from fastapi import APIRouter, Depends

    app = FastAPI()
    # Create a new router instance for testing
    test_router = APIRouter(prefix="/agent")
    setup_router(test_router, get_agent=get_agent_factory)
    app.include_router(test_router, dependencies=[Depends(get_agent_factory)])
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(test_app)


@pytest.fixture
def slack_signing_secret() -> str:
    """Test Slack signing secret."""
    import os

    # Set environment variable for testing
    os.environ["SLACK_SIGNING_SECRET"] = "test_secret"
    return "test_secret"


@pytest.fixture
def discord_public_key() -> str:
    """Test Discord public key (64 hex chars)."""
    import os

    key = "0" * 64
    os.environ["DISCORD_PUBLIC_KEY"] = key
    return key

"""Test configuration and fixtures."""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router


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
    app = FastAPI()
    # Override the placeholder dependency
    app.dependency_overrides[get_agent_placeholder] = get_agent_factory
    app.include_router(router)
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(test_app)

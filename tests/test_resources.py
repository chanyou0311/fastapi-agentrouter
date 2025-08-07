"""Tests for resource management dependencies."""

from unittest.mock import Mock, patch

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from fastapi_agentrouter.core.dependencies import AgentProtocol
from fastapi_agentrouter.core.resources import (
    ResourceManager,
    SessionManager,
    async_resource_context,
    get_agent_with_cleanup,
    get_async_agent_with_cleanup,
    get_session_manager,
    resource_context,
)


class MockAgentWithCleanup(AgentProtocol):
    """Mock agent with cleanup support for testing."""

    def __init__(self):
        self.cleaned_up = False
        self.query_count = 0

    def stream_query(self, **kwargs):
        self.query_count += 1
        yield "test response"

    def cleanup(self):
        self.cleaned_up = True


def test_resource_manager():
    """Test ResourceManager functionality."""
    manager = ResourceManager()

    # Mock resources
    resource1 = Mock()
    resource2 = Mock()
    resource2.cleanup = Mock()

    # Register resources
    manager.register(resource1, resource1.cleanup)
    manager.register(resource2)

    # Cleanup should be called
    manager.cleanup()

    resource2.cleanup.assert_called_once()


def test_resource_context():
    """Test resource_context context manager."""
    mock_resource = Mock()
    mock_callback = Mock()

    with resource_context() as rm:
        rm.register(mock_resource, mock_callback)
        # Resource should not be cleaned up yet
        mock_callback.assert_not_called()

    # After context exit, resource should be cleaned up
    mock_callback.assert_called_once()


@pytest.mark.asyncio
async def test_async_resource_context():
    """Test async_resource_context context manager."""
    mock_resource = Mock()
    mock_callback = Mock()

    async with async_resource_context() as rm:
        rm.register(mock_resource, mock_callback)
        mock_callback.assert_not_called()

    mock_callback.assert_called_once()


def test_session_manager():
    """Test SessionManager functionality."""
    manager = SessionManager()

    # Create sessions
    session1 = manager.get_session("user1")
    session1["data"] = "test1"

    session2 = manager.get_session("user2")
    session2["data"] = "test2"

    # Verify sessions are separate
    assert manager.get_session("user1")["data"] == "test1"
    assert manager.get_session("user2")["data"] == "test2"

    # Clear session
    manager.clear_session("user1")
    assert "user1" not in manager.sessions
    assert "user2" in manager.sessions


def test_get_session_manager():
    """Test get_session_manager dependency."""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint(session_manager: SessionManager = Depends(get_session_manager)):
        session = session_manager.get_session("test_session")
        session["counter"] = session.get("counter", 0) + 1
        return {"counter": session["counter"]}

    client = TestClient(app)

    # First request
    response = client.get("/test")
    assert response.status_code == 200
    # Counter should be 1 on first request


def test_agent_with_cleanup_placeholder():
    """Test that placeholder raises exception."""
    with pytest.raises(HTTPException) as exc_info:
        gen = get_agent_with_cleanup()
        next(gen)

    assert exc_info.value.status_code == 500
    assert "not configured" in exc_info.value.detail


@pytest.mark.asyncio
async def test_async_agent_with_cleanup_placeholder():
    """Test that async placeholder raises exception."""
    with pytest.raises(HTTPException) as exc_info:
        gen = get_async_agent_with_cleanup()
        await gen.__anext__()

    assert exc_info.value.status_code == 500
    assert "not configured" in exc_info.value.detail


def test_agent_with_cleanup_integration():
    """Test agent with cleanup in FastAPI app."""
    app = FastAPI()
    mock_agent = MockAgentWithCleanup()

    def get_my_agent_with_cleanup():
        try:
            yield mock_agent
        finally:
            mock_agent.cleanup()

    # Override the placeholder
    app.dependency_overrides[get_agent_with_cleanup] = get_my_agent_with_cleanup

    @app.get("/query")
    def query(agent=Depends(get_agent_with_cleanup)):
        return {"response": list(agent.stream_query(message="test"))}

    client = TestClient(app)

    # Make request
    response = client.get("/query")
    assert response.status_code == 200
    assert response.json() == {"response": ["test response"]}

    # Agent should have been used
    assert mock_agent.query_count == 1


def test_resource_manager_cleanup_error_handling():
    """Test that ResourceManager handles cleanup errors gracefully."""
    manager = ResourceManager()

    # Mock resource that raises during cleanup
    resource = Mock()
    resource.cleanup = Mock(side_effect=Exception("Cleanup failed"))

    manager.register(resource)

    # Should not raise, but log the error
    with patch("fastapi_agentrouter.core.resources.logger") as mock_logger:
        manager.cleanup()
        mock_logger.error.assert_called_once()


def test_session_manager_with_dependency():
    """Test SessionManager as a dependency with cleanup."""
    sessions_cleaned = False

    def get_custom_session_manager():
        manager = SessionManager()
        try:
            yield manager
        finally:
            nonlocal sessions_cleaned
            sessions_cleaned = True
            manager.sessions.clear()

    app = FastAPI()
    app.dependency_overrides[get_session_manager] = get_custom_session_manager

    @app.post("/store")
    def store_data(
        session_id: str,
        data: str,
        manager: SessionManager = Depends(get_session_manager),
    ):
        session = manager.get_session(session_id)
        session["data"] = data
        return {"stored": True}

    @app.get("/retrieve")
    def retrieve_data(
        session_id: str, manager: SessionManager = Depends(get_session_manager)
    ):
        session = manager.get_session(session_id)
        return {"data": session.get("data")}

    client = TestClient(app)

    # Store data
    response = client.post("/store?session_id=test&data=hello")
    assert response.status_code == 200

    # Retrieve data - should get same manager instance within request
    response = client.get("/retrieve?session_id=test")
    assert response.status_code == 200

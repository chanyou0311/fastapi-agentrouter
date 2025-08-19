"""Tests for Vertex AI agent adapter."""

from unittest.mock import MagicMock, patch

import pytest

from fastapi_agentrouter.agents.base import BaseAgentAdapter
from fastapi_agentrouter.agents.vertexai import (
    VertexAIAgentAdapter,
    get_vertex_ai_agent,
)


class TestVertexAIAgentAdapter:
    """Test suite for VertexAIAgentAdapter."""

    def test_adapter_implements_base_interface(self):
        """Test that VertexAIAgentAdapter implements BaseAgentAdapter interface."""
        mock_engine = MagicMock()
        adapter = VertexAIAgentAdapter(mock_engine)

        assert isinstance(adapter, BaseAgentAdapter)
        assert hasattr(adapter, "create_session")
        assert hasattr(adapter, "list_sessions")
        assert hasattr(adapter, "stream_query")

    def test_create_session(self):
        """Test session creation through the adapter."""
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_session.name = "session-123"
        mock_session.display_name = "Test Session"
        mock_engine.create_session.return_value = mock_session

        adapter = VertexAIAgentAdapter(mock_engine)
        result = adapter.create_session(user_id="user-456")

        assert result["id"] == "session-123"
        assert result["user_id"] == "user-456"
        assert result["display_name"] == "Test Session"
        mock_engine.create_session.assert_called_once()

    def test_list_sessions(self):
        """Test listing sessions through the adapter."""
        mock_engine = MagicMock()
        mock_session1 = MagicMock()
        mock_session1.name = "session-1"
        mock_session1.display_name = "Session 1"
        mock_session1.create_time = None

        mock_session2 = MagicMock()
        mock_session2.name = "session-2"
        mock_session2.display_name = "Session 2"
        mock_session2.create_time = None

        mock_engine.list_sessions.return_value = [mock_session1, mock_session2]

        adapter = VertexAIAgentAdapter(mock_engine)
        result = adapter.list_sessions()

        assert "sessions" in result
        assert len(result["sessions"]) == 2
        assert result["sessions"][0]["id"] == "session-1"
        assert result["sessions"][1]["id"] == "session-2"

    def test_stream_query_with_session(self):
        """Test streaming query with existing session."""
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_session.name = "session-123"

        # Mock response structure
        mock_candidate = MagicMock()
        mock_candidate.finish_reason = "STOP"
        mock_candidate.safety_ratings = []
        mock_part = MagicMock()
        mock_part.text = "Test response"
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_session.query.return_value = mock_response
        mock_engine.get_session.return_value = mock_session

        adapter = VertexAIAgentAdapter(mock_engine)
        results = list(
            adapter.stream_query(
                message="Test query", session_id="session-123", user_id="user-456"
            )
        )

        assert len(results) == 1
        assert results[0]["content"] == "Test response"
        assert results[0]["session_id"] == "session-123"
        assert results[0]["user_id"] == "user-456"
        mock_engine.get_session.assert_called_once_with("session-123")

    def test_stream_query_without_session(self):
        """Test streaming query without existing session."""
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_session.name = "new-session-123"

        # Mock response structure
        mock_candidate = MagicMock()
        mock_candidate.finish_reason = "STOP"
        mock_candidate.safety_ratings = []
        mock_part = MagicMock()
        mock_part.text = "Test response"
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_session.query.return_value = mock_response
        mock_engine.create_session.return_value = mock_session

        adapter = VertexAIAgentAdapter(mock_engine)
        results = list(adapter.stream_query(message="Test query", user_id="user-456"))

        assert len(results) == 1
        assert results[0]["content"] == "Test response"
        assert results[0]["session_id"] == "new-session-123"
        mock_engine.create_session.assert_called_once()


class TestVertexAIDependencies:
    """Test suite for Vertex AI dependency functions."""

    @patch("fastapi_agentrouter.agents.vertexai.dependencies.get_settings")
    @patch("fastapi_agentrouter.agents.vertexai.dependencies.create_vertex_ai_adapter")
    def test_get_vertex_ai_agent_success(self, mock_create_adapter, mock_get_settings):
        """Test successful agent retrieval."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.is_vertexai_enabled.return_value = True
        mock_vertexai_settings = MagicMock()
        mock_vertexai_settings.project_id = "test-project"
        mock_vertexai_settings.location = "us-central1"
        mock_vertexai_settings.agent_name = "test-agent"
        mock_vertexai_settings.staging_bucket = "test-bucket"
        mock_settings.vertexai = mock_vertexai_settings
        mock_get_settings.return_value = mock_settings

        # Mock adapter
        mock_adapter = MagicMock(spec=BaseAgentAdapter)
        mock_create_adapter.return_value = mock_adapter

        # Call function
        result = get_vertex_ai_agent()

        assert result == mock_adapter
        mock_create_adapter.assert_called_once_with(
            project_id="test-project",
            location="us-central1",
            agent_name="test-agent",
            staging_bucket="test-bucket",
        )

    @patch("fastapi_agentrouter.agents.vertexai.dependencies.get_settings")
    def test_get_vertex_ai_agent_not_enabled(self, mock_get_settings):
        """Test error when Vertex AI is not enabled."""
        # Clear the cache before testing
        from fastapi_agentrouter.agents.vertexai.dependencies import get_vertex_ai_agent

        get_vertex_ai_agent.cache_clear()

        mock_settings = MagicMock()
        mock_settings.is_vertexai_enabled.return_value = False
        mock_get_settings.return_value = mock_settings

        with pytest.raises(RuntimeError, match="Vertex AI settings not configured"):
            get_vertex_ai_agent()

    @patch("fastapi_agentrouter.agents.vertexai.dependencies.get_settings")
    def test_get_vertex_ai_agent_no_settings(self, mock_get_settings):
        """Test error when Vertex AI settings are None."""
        # Clear the cache before testing
        from fastapi_agentrouter.agents.vertexai.dependencies import get_vertex_ai_agent

        get_vertex_ai_agent.cache_clear()

        mock_settings = MagicMock()
        mock_settings.is_vertexai_enabled.return_value = True
        mock_settings.vertexai = None
        mock_get_settings.return_value = mock_settings

        with pytest.raises(RuntimeError, match="Vertex AI settings not configured"):
            get_vertex_ai_agent()

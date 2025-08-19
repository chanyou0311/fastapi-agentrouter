"""Tests for Vertex AI Agent Engine adapter."""

from unittest.mock import MagicMock, patch

import pytest

from fastapi_agentrouter.agents.vertexai.adapter import VertexAIAgentAdapter


class TestVertexAIAgentAdapter:
    """Test suite for VertexAIAgentAdapter."""

    def test_create_session(self):
        """Test session creation."""
        # Mock agent engine
        mock_engine = MagicMock()
        mock_session = MagicMock()
        mock_session.id = "session-123"
        mock_engine.create_session.return_value = mock_session

        # Create adapter
        adapter = VertexAIAgentAdapter(mock_engine)

        # Test with user_id
        result = adapter.create_session(user_id="user-456")
        assert result == {"id": "session-123", "user_id": "user-456"}
        mock_engine.create_session.assert_called_once_with(user_id="user-456")

        # Test without user_id (should use default)
        mock_engine.reset_mock()
        result = adapter.create_session()
        assert result == {"id": "session-123", "user_id": "default_user"}
        mock_engine.create_session.assert_called_once_with(user_id="default_user")

    def test_list_sessions(self):
        """Test listing sessions."""
        # Mock agent engine
        mock_engine = MagicMock()
        mock_engine.list_sessions.return_value = ["session-1", "session-2", "session-3"]

        # Create adapter
        adapter = VertexAIAgentAdapter(mock_engine)

        # Test with user_id
        result = adapter.list_sessions(user_id="user-456")
        assert result == {
            "sessions": [
                {"id": "session-1", "user_id": "user-456"},
                {"id": "session-2", "user_id": "user-456"},
                {"id": "session-3", "user_id": "user-456"},
            ]
        }
        mock_engine.list_sessions.assert_called_once_with(user_id="user-456")

        # Test without user_id (should use default)
        mock_engine.reset_mock()
        result = adapter.list_sessions()
        assert result == {
            "sessions": [
                {"id": "session-1", "user_id": "default_user"},
                {"id": "session-2", "user_id": "default_user"},
                {"id": "session-3", "user_id": "default_user"},
            ]
        }
        mock_engine.list_sessions.assert_called_once_with(user_id="default_user")

    def test_stream_query_with_session_id(self):
        """Test streaming query with existing session."""
        # Mock agent engine
        mock_engine = MagicMock()

        # Mock response chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Hello"
        mock_chunk2 = MagicMock()
        mock_chunk2.text = " world!"

        mock_engine.stream_query.return_value = [mock_chunk1, mock_chunk2]

        # Create adapter
        adapter = VertexAIAgentAdapter(mock_engine)

        # Test with session_id
        result = list(adapter.stream_query(message="Hi", session_id="session-123"))

        assert len(result) == 2
        assert result[0] == {"content": {"parts": [{"text": "Hello"}]}}
        assert result[1] == {"content": {"parts": [{"text": " world!"}]}}

        mock_engine.stream_query.assert_called_once_with(
            session_id="session-123", message="Hi"
        )

    def test_stream_query_without_session_id_existing_session(self):
        """Test streaming query without session_id but with existing session."""
        # Mock agent engine
        mock_engine = MagicMock()
        mock_engine.list_sessions.return_value = ["session-existing"]

        # Mock response chunks
        mock_chunk = MagicMock()
        mock_chunk.text = "Response"
        mock_engine.stream_query.return_value = [mock_chunk]

        # Create adapter
        adapter = VertexAIAgentAdapter(mock_engine)

        # Test without session_id (should use existing)
        result = list(adapter.stream_query(message="Hi", user_id="user-456"))

        assert len(result) == 1
        assert result[0] == {"content": {"parts": [{"text": "Response"}]}}

        mock_engine.list_sessions.assert_called_once_with(user_id="user-456")
        mock_engine.stream_query.assert_called_once_with(
            session_id="session-existing", message="Hi"
        )

    def test_stream_query_without_session_id_new_session(self):
        """Test streaming query without session_id and no existing session."""
        # Mock agent engine
        mock_engine = MagicMock()
        mock_engine.list_sessions.return_value = []

        # Mock new session
        mock_session = MagicMock()
        mock_session.id = "session-new"
        mock_engine.create_session.return_value = mock_session

        # Mock response chunks
        mock_chunk = MagicMock()
        mock_chunk.text = "Response"
        mock_engine.stream_query.return_value = [mock_chunk]

        # Create adapter
        adapter = VertexAIAgentAdapter(mock_engine)

        # Test without session_id (should create new)
        result = list(adapter.stream_query(message="Hi", user_id="user-456"))

        assert len(result) == 1
        assert result[0] == {"content": {"parts": [{"text": "Response"}]}}

        mock_engine.list_sessions.assert_called_once_with(user_id="user-456")
        mock_engine.create_session.assert_called_once_with(user_id="user-456")
        mock_engine.stream_query.assert_called_once_with(
            session_id="session-new", message="Hi"
        )

    def test_transform_response_chunk_with_text_attr(self):
        """Test transforming response chunk with text attribute."""
        mock_engine = MagicMock()
        adapter = VertexAIAgentAdapter(mock_engine)

        # Mock chunk with text attribute
        mock_chunk = MagicMock()
        mock_chunk.text = "Test response"

        result = adapter._transform_response_chunk(mock_chunk)
        assert result == {"content": {"parts": [{"text": "Test response"}]}}

    def test_transform_response_chunk_dict(self):
        """Test transforming response chunk that's already a dict."""
        mock_engine = MagicMock()
        adapter = VertexAIAgentAdapter(mock_engine)

        # Chunk already in expected format
        chunk = {"content": {"parts": [{"text": "Already formatted"}]}}

        result = adapter._transform_response_chunk(chunk)
        assert result == chunk

    def test_transform_response_chunk_fallback(self):
        """Test transforming response chunk with fallback."""
        mock_engine = MagicMock()
        adapter = VertexAIAgentAdapter(mock_engine)

        # Chunk without text attribute
        chunk = "Simple string"

        result = adapter._transform_response_chunk(chunk)
        assert result == {"content": {"parts": [{"text": "Simple string"}]}}


class TestGetVertexAIAgent:
    """Test suite for get_vertex_ai_agent function."""

    @patch(
        "fastapi_agentrouter.agents.vertexai.dependencies.get_vertex_ai_agent_engine"
    )
    def test_get_vertex_ai_agent_success(self, mock_get_engine):
        """Test successful adapter creation."""
        from fastapi_agentrouter.agents.vertexai.adapter import get_vertex_ai_agent

        # Mock engine
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        # Get adapter
        adapter = get_vertex_ai_agent()

        # Verify it's an adapter instance
        assert isinstance(adapter, VertexAIAgentAdapter)
        assert adapter._agent_engine == mock_engine
        mock_get_engine.assert_called_once()

        # Test caching - should return same instance
        adapter2 = get_vertex_ai_agent()
        assert adapter is adapter2
        # Should still only be called once due to caching
        mock_get_engine.assert_called_once()

    @patch(
        "fastapi_agentrouter.agents.vertexai.dependencies.get_vertex_ai_agent_engine"
    )
    def test_get_vertex_ai_agent_error_propagation(self, mock_get_engine):
        """Test that errors from get_vertex_ai_agent_engine are propagated."""
        from fastapi_agentrouter.agents.vertexai.adapter import get_vertex_ai_agent

        # Clear cache first
        get_vertex_ai_agent.cache_clear()

        # Mock engine raising error
        mock_get_engine.side_effect = RuntimeError("Vertex AI not configured")

        # Should propagate the error
        with pytest.raises(RuntimeError, match="Vertex AI not configured"):
            get_vertex_ai_agent()

"""Tests for the Agent interface."""

import pytest
from typing import Any, Dict

from fastapi_agentrouter import Agent, AgentResponse


class TestAgentInterface:
    """Test the Agent abstract base class."""
    
    def test_agent_is_abstract(self) -> None:
        """Test that Agent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Agent()  # type: ignore
    
    def test_agent_response_model(self) -> None:
        """Test AgentResponse model."""
        response = AgentResponse(content="Hello")
        assert response.content == "Hello"
        assert response.metadata is None
        
        response_with_metadata = AgentResponse(
            content="Hello",
            metadata={"key": "value"}
        )
        assert response_with_metadata.content == "Hello"
        assert response_with_metadata.metadata == {"key": "value"}
    
    def test_agent_response_serialization(self) -> None:
        """Test AgentResponse serialization."""
        response = AgentResponse(
            content="Test content",
            metadata={"foo": "bar", "count": 42}
        )
        
        data = response.model_dump()
        assert data == {
            "content": "Test content",
            "metadata": {"foo": "bar", "count": 42}
        }
        
        json_data = response.model_dump_json()
        assert isinstance(json_data, str)
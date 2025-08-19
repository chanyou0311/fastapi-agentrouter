"""Vertex AI Agent Engine adapter for FastAPI AgentRouter."""

from collections.abc import Generator
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from ...core.dependencies import AgentProtocol

if TYPE_CHECKING:
    from vertexai.agent_engines import AgentEngine


class VertexAIAgentAdapter:
    """Adapter that wraps Vertex AI Agent Engine to conform to AgentProtocol.

    This adapter translates between the FastAPI AgentRouter's AgentProtocol interface
    and Vertex AI Agent Engine's specific API, allowing seamless integration while
    maintaining a consistent interface for different agent backends.
    """

    def __init__(self, agent_engine: "AgentEngine") -> None:
        """Initialize the adapter with a Vertex AI Agent Engine instance.

        Args:
            agent_engine: The Vertex AI Agent Engine instance to wrap.
        """
        self._agent_engine = agent_engine

    def create_session(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new session for the agent.

        Args:
            user_id: Optional user identifier for the session.
            **kwargs: Additional keyword arguments for session creation.

        Returns:
            A dictionary containing at least the session 'id'.
        """
        # Vertex AI Agent Engine's create_session expects a user_id
        # If not provided, use a default value
        actual_user_id = user_id or "default_user"

        # Create session with Vertex AI Agent Engine
        session = self._agent_engine.create_session(user_id=actual_user_id)

        # Return in the expected format
        return {
            "id": session.id,
            "user_id": actual_user_id,
        }

    def list_sessions(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List sessions for a given user.

        Args:
            user_id: Optional user identifier to filter sessions.
            **kwargs: Additional keyword arguments for listing sessions.

        Returns:
            A dictionary with a 'sessions' key containing a list of
            session dictionaries.
        """
        # Vertex AI Agent Engine's list_sessions expects a user_id
        actual_user_id = user_id or "default_user"

        # Get sessions from Vertex AI Agent Engine
        session_ids = self._agent_engine.list_sessions(user_id=actual_user_id)

        # Format sessions in the expected structure
        sessions = [
            {"id": session_id, "user_id": actual_user_id} for session_id in session_ids
        ]

        return {"sessions": sessions}

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Generator[dict[str, Any], Any, None]:
        """Stream responses from the agent.

        Args:
            message: The message to send to the agent.
            user_id: Optional user identifier (used for session management).
            session_id: Optional session identifier for the conversation.
            **kwargs: Additional keyword arguments for the query.

        Yields:
            Dictionary chunks containing response data from the agent.
        """
        # If no session_id is provided, try to find or create one
        if session_id is None:
            actual_user_id = user_id or "default_user"

            # Check if there's an existing session for this user
            sessions_response = self.list_sessions(user_id=actual_user_id)
            existing_sessions = sessions_response.get("sessions", [])

            if existing_sessions:
                # Use the first existing session
                session_id = existing_sessions[0]["id"]
            else:
                # Create a new session
                new_session = self.create_session(user_id=actual_user_id)
                session_id = new_session["id"]

        # Stream query using Vertex AI Agent Engine
        # The agent_engine.stream_query returns a generator
        for response_chunk in self._agent_engine.stream_query(
            session_id=session_id,
            message=message,
        ):
            # Transform the response to match expected format
            # The actual structure depends on what Vertex AI returns
            # This is a common format that works with the Slack integration
            yield self._transform_response_chunk(response_chunk)

    def _transform_response_chunk(self, chunk: Any) -> dict[str, Any]:
        """Transform Vertex AI response chunk to expected format.

        Args:
            chunk: Raw response chunk from Vertex AI Agent Engine.

        Returns:
            Transformed response chunk in the expected format.
        """
        # This transformation depends on the actual structure of Vertex AI responses
        # Here we're adapting to the format expected by the Slack integration

        # If chunk has text content, format it properly
        if hasattr(chunk, "text") and chunk.text:
            return {"content": {"parts": [{"text": chunk.text}]}}

        # If chunk is already in the expected format, return as-is
        if isinstance(chunk, dict):
            return chunk

        # Default transformation
        return {"content": {"parts": [{"text": str(chunk)}]}}


@lru_cache
def get_vertex_ai_agent() -> AgentProtocol:
    """Get the Vertex AI Agent adapter instance.

    This function creates and returns a VertexAIAgentAdapter that wraps
    the Vertex AI Agent Engine to conform to the AgentProtocol interface.

    The adapter is cached to avoid expensive initialization on every request.

    Returns:
        An AgentProtocol-compliant adapter for Vertex AI Agent Engine.

    Raises:
        RuntimeError: If Vertex AI settings are not configured.
        ImportError: If google-cloud-aiplatform is not installed.
        ValueError: If agent is not found or multiple agents found.

    Example:
        # Set environment variables:
        # VERTEXAI__PROJECT_ID=your-project-id
        # VERTEXAI__LOCATION=us-central1
        # VERTEXAI__STAGING_BUCKET=your-bucket
        # VERTEXAI__AGENT_NAME=your-agent-name

        # Use in FastAPI dependency injection:
        from fastapi_agentrouter import get_agent
        from fastapi_agentrouter.agents.vertexai import get_vertex_ai_agent

        app.dependency_overrides[get_agent] = get_vertex_ai_agent
    """
    # Import the existing function to get the raw agent engine
    from .dependencies import get_vertex_ai_agent_engine

    # Get the raw Vertex AI Agent Engine
    agent_engine = get_vertex_ai_agent_engine()

    # Wrap it with our adapter
    return VertexAIAgentAdapter(agent_engine)


__all__ = ["VertexAIAgentAdapter", "get_vertex_ai_agent"]

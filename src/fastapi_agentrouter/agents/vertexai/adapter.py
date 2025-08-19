"""Vertex AI Agent adapter implementation."""

from collections.abc import Generator
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from ..base import BaseAgentAdapter

if TYPE_CHECKING:
    from vertexai.agent_engines import AgentEngine


class VertexAIAgentAdapter(BaseAgentAdapter):
    """Adapter for Vertex AI Agent Engine.

    This adapter wraps the Vertex AI Agent Engine to provide a consistent
    interface that conforms to the BaseAgentAdapter protocol.
    """

    def __init__(self, agent_engine: "AgentEngine") -> None:
        """Initialize the Vertex AI adapter.

        Args:
            agent_engine: The Vertex AI AgentEngine instance to wrap
        """
        self._agent_engine = agent_engine

    def create_session(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new session for the Vertex AI agent.

        Args:
            user_id: Optional user identifier for the session
            **kwargs: Additional arguments passed to the Vertex AI engine

        Returns:
            A dictionary containing the session information
        """
        # Vertex AI Agent Engine session creation
        session = self._agent_engine.create_session(
            display_name=f"Session for user {user_id}" if user_id else "Session",
            **kwargs,
        )

        return {
            "id": session.name,
            "user_id": user_id,
            "display_name": session.display_name,
        }

    def list_sessions(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List sessions for the Vertex AI agent.

        Args:
            user_id: Optional user identifier to filter sessions
            **kwargs: Additional arguments for session listing

        Returns:
            A dictionary with sessions information
        """
        # List all sessions from the agent engine
        sessions = list(self._agent_engine.list_sessions(**kwargs))

        # Filter by user_id if provided (needs custom metadata in real impl)
        # For now, return all sessions
        session_list = [
            {
                "id": session.name,
                "display_name": session.display_name,
                "create_time": session.create_time.isoformat()
                if session.create_time
                else None,
            }
            for session in sessions
        ]

        return {"sessions": session_list}

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Generator[dict[str, Any], Any, None]:
        """Stream responses from the Vertex AI agent.

        Args:
            message: The query message to send to the agent
            user_id: Optional user identifier
            session_id: Optional session identifier for context
            **kwargs: Additional arguments for the query

        Yields:
            Dictionary containing response chunks from the agent
        """
        # Execute query with the agent engine
        if session_id:
            # Use existing session
            session = self._agent_engine.get_session(session_id)
        else:
            # Create a temporary session for this query
            session = self._agent_engine.create_session(
                display_name=f"Query session for {user_id}"
                if user_id
                else "Query session"
            )
            session_id = session.name

        # Stream the response
        response = session.query(input=message, **kwargs)

        # Yield response chunks
        for chunk in response.candidates:
            yield {
                "session_id": session_id,
                "user_id": user_id,
                "content": chunk.content.parts[0].text if chunk.content.parts else "",
                "metadata": {
                    "finish_reason": chunk.finish_reason,
                    "safety_ratings": chunk.safety_ratings
                    if hasattr(chunk, "safety_ratings")
                    else None,
                },
            }


@lru_cache
def create_vertex_ai_adapter(
    project_id: str,
    location: str,
    agent_name: str,
    staging_bucket: str | None = None,
) -> VertexAIAgentAdapter:
    """Factory function to create a Vertex AI adapter instance.

    This function is cached to avoid expensive initialization on every request.

    Args:
        project_id: GCP project ID
        location: GCP location/region
        agent_name: Name of the Vertex AI agent
        staging_bucket: Optional staging bucket for the agent

    Returns:
        VertexAIAgentAdapter: Configured adapter instance

    Raises:
        ImportError: If google-cloud-aiplatform is not installed
        ValueError: If agent is not found or multiple agents found
    """
    try:
        import vertexai
        from vertexai import agent_engines
    except ImportError as e:
        raise ImportError(
            "google-cloud-aiplatform is not installed. "
            'Install with: pip install "fastapi-agentrouter[vertexai]"'
        ) from e

    # Initialize Vertex AI
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket,
    )

    # Find the agent
    apps = list(agent_engines.list(filter=f"display_name={agent_name}"))

    if len(apps) == 0:
        raise ValueError(f"Agent '{agent_name}' not found.")
    elif len(apps) > 1:
        raise ValueError(f"Multiple agents found with name '{agent_name}'.")

    # Create and return the adapter
    agent_engine = apps[0]
    return VertexAIAgentAdapter(agent_engine)

"""Base adapter interface for AI agents."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any


class BaseAgentAdapter(ABC):
    """Abstract base class for agent adapters.

    This class defines the interface that all agent adapters must implement.
    It provides a consistent API for different AI agent backends (Vertex AI,
    OpenAI, LiteLLM, etc.) to integrate with the FastAPI AgentRouter.
    """

    @abstractmethod
    def create_session(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new session for the agent.

        Args:
            user_id: Optional user identifier for the session
            **kwargs: Additional arguments specific to the agent implementation

        Returns:
            A dictionary containing at least the session 'id'.
        """
        pass

    @abstractmethod
    def list_sessions(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List sessions for a given user.

        Args:
            user_id: Optional user identifier to filter sessions
            **kwargs: Additional arguments specific to the agent implementation

        Returns:
            A dictionary with a 'sessions' key containing a list of
            session dictionaries.
        """
        pass

    @abstractmethod
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
            message: The query message to send to the agent
            user_id: Optional user identifier
            session_id: Optional session identifier for context
            **kwargs: Additional arguments specific to the agent implementation

        Yields:
            Dictionary containing response chunks from the agent
        """
        pass

"""Core dependencies for FastAPI AgentRouter."""

from collections.abc import Generator
from typing import Annotated, Any, Protocol

from fastapi import Depends, HTTPException


class AgentProtocol(Protocol):
    """Protocol for agent implementations."""

    def create_session(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new session for the agent.

        Returns a dictionary containing at least the session 'id'.
        """
        ...

    def list_sessions(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """List sessions for a given user.

        Returns a list of session dictionaries.
        """
        ...

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Generator[dict[str, Any], Any, None]:
        """Stream responses from the agent."""
        ...


# Placeholder for agent dependency
# This will be overridden by user's actual agent
def get_agent() -> AgentProtocol:
    """Placeholder for agent dependency.

    Users should provide their own agent via dependencies:
    app.include_router(router, dependencies=[Depends(get_agent)])
    """
    raise HTTPException(
        status_code=500,
        detail="Agent not configured. Please provide agent dependency.",
    )


# This will be the dependency injection point
AgentDep = Annotated[AgentProtocol, Depends(get_agent)]

"""Core dependencies for FastAPI AgentRouter."""

from typing import Annotated, Any, Optional, Protocol

from fastapi import Depends, HTTPException


class AgentProtocol(Protocol):
    """Protocol for agent implementations."""

    def stream_query(
        self,
        *,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Stream responses from the agent."""
        ...


# Placeholder for agent dependency
# This will be overridden by user's actual agent
def get_agent_placeholder() -> AgentProtocol:
    """Placeholder for agent dependency.

    Users should provide their own agent via dependencies:
    app.include_router(router, dependencies=[Depends(get_agent)])
    """
    raise HTTPException(
        status_code=500,
        detail="Agent not configured. Please provide agent dependency.",
    )


# This will be the dependency injection point
Agent = Annotated[AgentProtocol, Depends(get_agent_placeholder)]

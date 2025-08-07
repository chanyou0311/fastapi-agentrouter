"""Shared dependencies for FastAPI AgentRouter."""

from typing import Annotated, Any, Optional, Protocol

from fastapi import Depends, HTTPException

from .settings import settings


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


def check_slack_enabled() -> None:
    """Check if Slack integration is enabled."""
    if settings.disable_slack:
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )


def check_discord_enabled() -> None:
    """Check if Discord integration is enabled."""
    if settings.disable_discord:
        raise HTTPException(
            status_code=404,
            detail="Discord integration is not enabled",
        )


def check_webhook_enabled() -> None:
    """Check if webhook endpoint is enabled."""
    if settings.disable_webhook:
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint is not enabled",
        )

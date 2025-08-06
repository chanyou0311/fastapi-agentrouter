"""Shared dependencies for FastAPI AgentRouter."""

import os
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


def check_slack_enabled() -> None:
    """Check if Slack integration is enabled."""
    if os.getenv("DISABLE_SLACK") == "true":
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )


def check_discord_enabled() -> None:
    """Check if Discord integration is enabled."""
    if os.getenv("DISABLE_DISCORD") == "true":
        raise HTTPException(
            status_code=404,
            detail="Discord integration is not enabled",
        )


def check_webhook_enabled() -> None:
    """Check if webhook endpoint is enabled."""
    if os.getenv("DISABLE_WEBHOOK") == "true":
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint is not enabled",
        )

"""Router builder for FastAPI AgentRouter."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..integrations.discord import create_discord_handler
from ..integrations.slack import create_slack_handler
from .agent import Agent


def build_router(
    agent: Agent,
    *,
    prefix: str = "/agent",
    slack: Optional[dict[str, Any]] = None,
    discord: Optional[dict[str, Any]] = None,
    webhook: bool = True,
) -> APIRouter:
    """Build a FastAPI router with agent integrations.

    Args:
        agent: The AI agent instance
        prefix: URL prefix for all routes
        slack: Slack configuration dict with 'signing_secret'
        discord: Discord configuration dict with 'public_key'
        webhook: Enable generic webhook endpoint

    Returns:
        Configured FastAPI router
    """
    router = APIRouter(prefix=prefix)

    # Slack integration
    if slack:
        slack_handler = create_slack_handler(agent, slack)
        router.post("/slack/events")(slack_handler)

    # Discord integration
    if discord:
        discord_handler = create_discord_handler(agent, discord)
        router.post("/discord/interactions")(discord_handler)

    # Generic webhook
    if webhook:

        @router.post("/webhook")
        async def handle_webhook(request: Request) -> JSONResponse:
            """Handle generic webhook requests."""
            try:
                data = await request.json()
                response = await agent.handle_webhook(data)
                return JSONResponse(content=response.model_dump())
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e

    return router

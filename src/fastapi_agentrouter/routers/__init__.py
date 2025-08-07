"""Main router combining all platform routers."""

from fastapi import APIRouter

from ..integrations.discord import router as discord_router
from ..integrations.slack import router as slack_router
from ..integrations.webhook import router as webhook_router

# Create main router with /agent prefix
router = APIRouter(prefix="/agent")

# Include all platform routers
router.include_router(slack_router)
router.include_router(discord_router)
router.include_router(webhook_router)

__all__ = ["router"]

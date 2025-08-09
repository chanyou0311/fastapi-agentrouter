"""Main router combining all platform routers."""

from fastapi import APIRouter

from ..integrations.slack.router import router as slack_router

# Create main router with /agent prefix
router = APIRouter(prefix="/agent")

# Include Slack router
router.include_router(slack_router)

__all__ = ["router"]

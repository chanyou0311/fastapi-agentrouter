"""Main router combining all platform routers."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter

from ..core.settings import get_settings
from ..integrations.slack import router as slack_router


@asynccontextmanager
async def router_lifespan(app: APIRouter) -> AsyncIterator[None]:
    """Router lifespan manager with auto-warmup for configured services."""
    settings = get_settings()

    # Auto-warmup Vertex AI engine if configured
    if settings.is_vertexai_enabled():
        try:
            from ..agents.vertexai.dependencies import warmup_vertex_ai_engine

            warmup_vertex_ai_engine()
        except Exception as e:
            # Log but don't fail startup if warmup fails
            print(f"⚠️  Failed to warmup Vertex AI engine during startup: {e}")

    yield
    # Cleanup on shutdown (if needed in the future)


# Create main router with /agent prefix and lifespan
router = APIRouter(prefix="/agent", lifespan=router_lifespan)

# Include Slack router
router.include_router(slack_router)

__all__ = ["router"]

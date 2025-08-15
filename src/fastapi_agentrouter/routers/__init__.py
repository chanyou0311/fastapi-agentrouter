"""Main router combining all platform routers."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter

from ..core.settings import get_settings
from ..integrations.slack import router as slack_router


@asynccontextmanager
async def lifespan(app: APIRouter) -> AsyncIterator[None]:
    """Router lifespan manager with auto-warmup for configured services."""
    settings = get_settings()

    # Auto-warmup Vertex AI engine if configured
    if settings.is_vertexai_enabled():
        from ..agents.vertexai.dependencies import get_vertex_ai_agent_engine

        # Call the function to warm up the cache
        get_vertex_ai_agent_engine(settings)
        print("✅ Vertex AI agent engine warmed up successfully")

    yield
    # Cleanup on shutdown (if needed in the future)


# Create main router with /agent prefix and lifespan
router = APIRouter(prefix="/agent", lifespan=lifespan)

# Include Slack router
router.include_router(slack_router)

__all__ = ["router"]

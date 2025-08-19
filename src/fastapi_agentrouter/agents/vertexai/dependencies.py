"""Vertex AI dependencies for FastAPI AgentRouter."""

from functools import lru_cache

from ...core.settings import get_settings
from ..base import BaseAgentAdapter
from .adapter import create_vertex_ai_adapter


@lru_cache
def get_vertex_ai_agent() -> BaseAgentAdapter:
    """Get the Vertex AI Agent adapter instance.

    This function returns an adapter that wraps the Vertex AI AgentEngine,
    providing a consistent interface that conforms to the BaseAgentAdapter protocol.
    The adapter is cached to avoid expensive initialization on every request.

    Returns:
        BaseAgentAdapter: The cached Vertex AI agent adapter instance

    Raises:
        ValueError: If agent is not found or multiple agents found
        ImportError: If google-cloud-aiplatform is not installed
        RuntimeError: If Vertex AI settings are not configured

    Example:
        # Set environment variables:
        # VERTEXAI__PROJECT_ID=your-project-id
        # VERTEXAI__LOCATION=us-central1
        # VERTEXAI__STAGING_BUCKET=your-bucket
        # VERTEXAI__AGENT_NAME=your-agent-name

        from fastapi_agentrouter import router, get_agent
        app.dependency_overrides[get_agent] = get_vertex_ai_agent
        app.include_router(router)
    """
    settings = get_settings()

    if not settings.is_vertexai_enabled():
        raise RuntimeError(
            "Vertex AI settings not configured. Please set the required "
            "environment variables: VERTEXAI__PROJECT_ID, VERTEXAI__LOCATION, "
            "VERTEXAI__STAGING_BUCKET, VERTEXAI__AGENT_NAME"
        )

    vertexai_settings = settings.vertexai
    if not vertexai_settings:
        raise RuntimeError("Vertex AI settings not configured")

    # Use the adapter factory to create the Vertex AI adapter
    return create_vertex_ai_adapter(
        project_id=vertexai_settings.project_id,
        location=vertexai_settings.location,
        agent_name=vertexai_settings.agent_name,
        staging_bucket=vertexai_settings.staging_bucket,
    )

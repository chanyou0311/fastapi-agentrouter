"""Vertex AI dependencies for FastAPI AgentRouter."""

from functools import lru_cache
from typing import TYPE_CHECKING

from ...core.settings import SettingsDep, get_settings

if TYPE_CHECKING:
    from vertexai.agent_engines import AgentEngine


@lru_cache
def _get_cached_vertex_ai_engine() -> "AgentEngine":
    """Get cached Vertex AI AgentEngine instance.

    This function is cached to avoid expensive initialization on every request.
    It uses get_settings() which is also cached, ensuring consistent settings.

    Returns:
        AgentEngine: The cached Vertex AI agent engine instance

    Raises:
        ValueError: If agent is not found or multiple agents found
        ImportError: If google-cloud-aiplatform is not installed
        RuntimeError: If Vertex AI settings are not configured
    """
    settings = get_settings()

    if not settings.is_vertexai_enabled():
        raise RuntimeError(
            "Vertex AI settings not configured. Please set the required "
            "environment variables: VERTEXAI__PROJECT_ID, VERTEXAI__LOCATION, "
            "VERTEXAI__STAGING_BUCKET, VERTEXAI__AGENT_NAME"
        )

    try:
        import vertexai
        from vertexai import agent_engines
    except ImportError as e:
        raise ImportError(
            "google-cloud-aiplatform is not installed. "
            'Install with: pip install "fastapi-agentrouter[vertexai]"'
        ) from e

    vertexai_settings = settings.vertexai
    if not vertexai_settings:
        raise RuntimeError("Vertex AI settings not configured")

    vertexai.init(
        project=vertexai_settings.project_id,
        location=vertexai_settings.location,
        staging_bucket=vertexai_settings.staging_bucket,
    )

    apps = list(
        agent_engines.list(filter=f"display_name={vertexai_settings.agent_name}")
    )

    if len(apps) == 0:
        raise ValueError(f"Agent '{vertexai_settings.agent_name}' not found.")
    elif len(apps) > 1:
        raise ValueError(
            f"Multiple agents found with name '{vertexai_settings.agent_name}'."
        )

    app = apps[0]
    return app


def get_vertex_ai_agent_engine(settings: SettingsDep) -> "AgentEngine":
    """Get the Vertex AI AgentEngine instance for the specified agent.

    This is a FastAPI dependency wrapper around the cached engine.
    The actual engine instance is cached to avoid expensive initialization.

    Args:
        settings: The settings instance with Vertex AI configuration

    Returns:
        AgentEngine: The Vertex AI agent engine instance

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

        app.dependency_overrides[get_agent] = get_vertex_ai_agent_engine
    """
    # We accept settings parameter for compatibility with FastAPI dependency injection,
    # but use the cached function internally
    return _get_cached_vertex_ai_engine()


def warmup_vertex_ai_engine() -> None:
    """Warmup the Vertex AI agent engine by initializing it proactively.

    Note: This function is automatically called when the fastapi_agentrouter.router
    is included in your FastAPI app and Vertex AI is configured, so manual warmup
    is typically not required.

    This function pre-loads the cached engine instance so that subsequent
    requests can use it immediately, avoiding initialization delays on the
    first request.

    The router's lifespan automatically handles warmup, but you can still call
    this manually if needed for custom initialization flows.
    """
    try:
        # Call the cached function to initialize the engine
        _get_cached_vertex_ai_engine()
        print("✅ Vertex AI agent engine warmed up successfully")
    except Exception as e:
        print(f"⚠️ Failed to warmup Vertex AI agent engine: {e}")
        # We don't raise here to allow the app to start even if warmup fails

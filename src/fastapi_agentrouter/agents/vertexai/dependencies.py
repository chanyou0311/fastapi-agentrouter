"""Vertex AI dependencies for FastAPI AgentRouter."""

from typing import TYPE_CHECKING

from ...core.settings import SettingsDep

if TYPE_CHECKING:
    from vertexai.agent_engines import AgentEngine


def get_vertex_ai_agent_engine(settings: SettingsDep) -> "AgentEngine":
    """Get the Vertex AI AgentEngine instance for the specified agent.

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

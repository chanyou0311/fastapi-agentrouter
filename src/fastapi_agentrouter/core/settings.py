"""Settings management for FastAPI AgentRouter using pydantic-settings."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    bot_token: str
    signing_secret: str


class VertexAISettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    project_id: str
    location: str
    staging_bucket: str
    agent_name: str


class Settings(BaseSettings):
    """Application settings.

    All settings have sensible defaults and the application works without any
    environment variables set.
    """

    model_config = SettingsConfigDict(
        nested_model_default_partial_update=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

    slack: SlackSettings | None = None
    vertexai: VertexAISettings | None = None

    def is_slack_enabled(self) -> bool:
        """Check if Slack integration is enabled.

        Returns:
            bool: True if Slack settings are configured, False otherwise
        """
        return self.slack is not None

    def is_vertexai_enabled(self) -> bool:
        """Check if Vertex AI integration is enabled.

        Returns:
            bool: True if Vertex AI settings are configured, False otherwise
        """
        return self.vertexai is not None


# Cache the environment-based settings instance
@lru_cache
def get_settings() -> Settings:
    """Get the cached settings instance from environment.

    This function is cached to ensure we only create one instance
    when reading from environment variables.

    Returns:
        Settings: The settings instance

    Example:
        # Basic usage with environment variables
        settings = get_settings()

        # Override in FastAPI app for testing
        app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=True)
    """
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]

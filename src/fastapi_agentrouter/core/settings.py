"""Settings management for FastAPI AgentRouter using pydantic-settings."""

from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    All settings have sensible defaults and the application works without any
    environment variables set.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Platform enable/disable settings
    enable_slack: bool = Field(
        default=False,
        description="Enable Slack integration endpoints",
    )


# Create a singleton instance for environment-based settings
_env_settings = Settings()


def get_settings() -> Settings:
    """Get the current settings instance.
    
    This function can be overridden using FastAPI's dependency_overrides
    to provide custom settings without environment variables.
    
    Example:
        from fastapi_agentrouter.core.settings import Settings, get_settings
        
        custom_settings = Settings(enable_slack=True)
        app.dependency_overrides[get_settings] = lambda: custom_settings
    """
    return _env_settings


# Dependency type for settings injection
SettingsDep = Annotated[Settings, Depends(get_settings)]

# For backward compatibility
settings = _env_settings

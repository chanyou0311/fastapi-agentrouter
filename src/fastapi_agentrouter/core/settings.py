"""Settings management for FastAPI AgentRouter using pydantic-settings."""

from typing import Optional

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
    disable_slack: bool = Field(
        default=False,
        description="Disable Slack integration endpoints",
    )
    disable_discord: bool = Field(
        default=False,
        description="Disable Discord integration endpoints",
    )
    disable_webhook: bool = Field(
        default=False,
        description="Disable webhook endpoints",
    )


# Create a singleton instance
settings = Settings()
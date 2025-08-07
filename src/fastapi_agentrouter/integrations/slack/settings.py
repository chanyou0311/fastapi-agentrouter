"""Slack integration settings."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseSettings):
    """Settings for Slack integration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required settings
    slack_bot_token: Optional[str] = Field(
        default=None,
        description="Slack bot token (xoxb-...)",
    )
    slack_signing_secret: Optional[str] = Field(
        default=None,
        description="Slack app signing secret for request verification",
    )

    # Optional settings for testing
    slack_token_verification: bool = Field(
        default=True,
        description="Enable Slack token verification (disable for testing)",
    )
    slack_request_verification: bool = Field(
        default=True,
        description="Enable Slack request signature verification (disable for testing)",
    )


# Global instance
_settings: Optional[SlackSettings] = None


def get_slack_settings() -> SlackSettings:
    """Get or create Slack settings instance."""
    global _settings
    if _settings is None:
        _settings = SlackSettings()
    return _settings


def reset_settings() -> None:
    """Reset settings instance (useful for testing)."""
    global _settings
    _settings = None
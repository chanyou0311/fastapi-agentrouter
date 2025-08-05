"""Configuration utilities for FastAPI AgentRouter."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class SlackConfig(BaseModel):
    """Slack integration configuration."""

    signing_secret: str = Field(..., description="Slack app signing secret")
    app_token: Optional[str] = Field(None, description="Slack app-level token")
    bot_token: Optional[str] = Field(None, description="Slack bot user OAuth token")


class DiscordConfig(BaseModel):
    """Discord integration configuration."""

    public_key: str = Field(..., description="Discord application public key")
    application_id: Optional[str] = Field(None, description="Discord application ID")
    bot_token: Optional[str] = Field(None, description="Discord bot token")


class Config(BaseModel):
    """Main configuration for FastAPI AgentRouter."""

    prefix: str = Field("/agent", description="URL prefix for all routes")
    slack: Optional[SlackConfig] = Field(None, description="Slack configuration")
    discord: Optional[DiscordConfig] = Field(None, description="Discord configuration")
    webhook: bool = Field(True, description="Enable generic webhook endpoint")

    def to_router_kwargs(self) -> dict[str, Any]:
        """Convert to kwargs for build_router function."""
        kwargs = {
            "prefix": self.prefix,
            "webhook": self.webhook,
        }

        if self.slack:
            kwargs["slack"] = self.slack.model_dump()

        if self.discord:
            kwargs["discord"] = self.discord.model_dump()

        return kwargs

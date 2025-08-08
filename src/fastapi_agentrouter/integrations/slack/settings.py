"""Slack integration settings."""

from typing import Optional

from pydantic import BaseModel, Field


class SlackSettings(BaseModel):
    """Settings for Slack integration.
    
    This is a nested model that will be included in the main Settings class.
    Environment variables should be prefixed with SLACK__ (e.g., SLACK__BOT_TOKEN).
    """

    # Required settings
    bot_token: Optional[str] = Field(
        default=None,
        description="Slack bot token (xoxb-...)",
    )
    signing_secret: Optional[str] = Field(
        default=None,
        description="Slack app signing secret for request verification",
    )

    # Optional settings for testing
    token_verification: bool = Field(
        default=True,
        description="Enable Slack token verification (disable for testing)",
    )
    request_verification: bool = Field(
        default=True,
        description="Enable Slack request signature verification (disable for testing)",
    )
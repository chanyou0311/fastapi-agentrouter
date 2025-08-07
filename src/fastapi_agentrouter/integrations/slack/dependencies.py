"""Slack-specific dependencies."""

from fastapi import HTTPException

from ...core.settings import settings


def check_slack_enabled() -> None:
    """Check if Slack integration is enabled."""
    if settings.disable_slack:
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )
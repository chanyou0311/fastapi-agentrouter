"""Slack-specific dependencies."""

from fastapi import HTTPException

from ...core.settings import SettingsDep


def check_slack_enabled(settings: SettingsDep) -> None:
    """Check if Slack integration is enabled."""
    if not settings.enable_slack:
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )

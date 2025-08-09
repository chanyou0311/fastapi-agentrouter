"""Slack-specific dependencies."""

from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException

if TYPE_CHECKING:
    from ...core.settings import Settings


def check_slack_enabled(settings = Depends(lambda: __import__("fastapi_agentrouter.core.settings", fromlist=["get_settings"]).get_settings())) -> None:
    """Check if Slack integration is enabled."""
    if not settings.enable_slack:
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )

"""Slack-specific dependencies."""

import os

from fastapi import HTTPException


def check_slack_enabled() -> None:
    """Check if Slack integration is enabled."""
    if os.getenv("DISABLE_SLACK") == "true":
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )
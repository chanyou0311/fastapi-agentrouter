"""Discord-specific dependencies."""

import os

from fastapi import HTTPException


def check_discord_enabled() -> None:
    """Check if Discord integration is enabled."""
    if os.getenv("DISABLE_DISCORD") == "true":
        raise HTTPException(
            status_code=404,
            detail="Discord integration is not enabled",
        )
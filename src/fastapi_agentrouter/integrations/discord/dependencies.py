"""Discord-specific dependencies."""

from fastapi import HTTPException

from ...core.settings import settings


def check_discord_enabled() -> None:
    """Check if Discord integration is enabled."""
    if settings.disable_discord:
        raise HTTPException(
            status_code=404,
            detail="Discord integration is not enabled",
        )

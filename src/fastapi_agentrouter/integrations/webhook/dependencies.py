"""Webhook-specific dependencies."""

from fastapi import HTTPException

from ...core.settings import settings


def check_webhook_enabled() -> None:
    """Check if webhook endpoint is enabled."""
    if settings.disable_webhook:
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint is not enabled",
        )
"""Webhook-specific dependencies."""

import os

from fastapi import HTTPException


def check_webhook_enabled() -> None:
    """Check if webhook endpoint is enabled."""
    if os.getenv("DISABLE_WEBHOOK") == "true":
        raise HTTPException(
            status_code=404,
            detail="Webhook endpoint is not enabled",
        )
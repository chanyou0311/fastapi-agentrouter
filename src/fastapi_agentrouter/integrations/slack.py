"""Slack integration for FastAPI AgentRouter."""

import hashlib
import hmac
import json
import time
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse, Response

from ..core.agent import Agent


def verify_slack_signature(
    signing_secret: str, request_body: bytes, timestamp: str, signature: str
) -> bool:
    """Verify Slack request signature.

    Args:
        signing_secret: Slack app signing secret
        request_body: Raw request body
        timestamp: Request timestamp from headers
        signature: Request signature from headers

    Returns:
        True if signature is valid
    """
    # Check timestamp to prevent replay attacks
    if abs(time.time() - float(timestamp)) > 60 * 5:
        return False

    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    my_signature = (
        "v0="
        + hmac.new(
            signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )

    return hmac.compare_digest(my_signature, signature)


def create_slack_handler(agent: Agent, config: dict[str, Any]) -> Callable:
    """Create a Slack event handler.

    Args:
        agent: The AI agent instance
        config: Slack configuration with 'signing_secret'

    Returns:
        FastAPI route handler for Slack events
    """
    signing_secret = config.get("signing_secret")
    if not signing_secret:
        raise ValueError("Slack signing_secret is required")

    async def handle_slack_events(request: Request) -> Response:
        """Handle Slack events and slash commands."""
        # Get request body and headers
        body = await request.body()
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")

        # Verify request signature
        if not verify_slack_signature(signing_secret, body, timestamp, signature):
            raise HTTPException(status_code=400, detail="Invalid request signature")

        # Parse request body
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = json.loads(body)
        else:
            # Parse URL-encoded form data (slash commands)
            from urllib.parse import parse_qs

            parsed = parse_qs(body.decode("utf-8"))
            data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        # Handle URL verification challenge
        if data.get("type") == "url_verification":
            return PlainTextResponse(content=data.get("challenge", ""))

        # Process event with agent
        try:
            response = await agent.handle_slack(data)
            return PlainTextResponse(content=response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return handle_slack_events

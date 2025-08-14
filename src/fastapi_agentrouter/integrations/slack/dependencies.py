"""Slack-specific dependencies."""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, HTTPException

from ...core.dependencies import AgentDep
from ...core.settings import SettingsDep

if TYPE_CHECKING:
    from slack_bolt import App as SlackApp
    from slack_bolt.adapter.fastapi import SlackRequestHandler

logger = logging.getLogger(__name__)


def check_slack_enabled(settings: SettingsDep) -> None:
    """Check if Slack integration is enabled."""
    if not settings.is_slack_enabled():
        raise HTTPException(
            status_code=404,
            detail="Slack integration is not enabled",
        )


def get_ack() -> Callable[[dict, Any], None]:
    """Get an acknowledgment function for Slack events."""

    def ack(body: dict, ack: Any) -> None:
        """Acknowledge the event."""
        ack()

    return ack


def get_app_mention(agent: AgentDep) -> Callable[[dict, Any, dict], None]:
    """Get app mention event handler."""

    def app_mention(event: dict, say: Any, body: dict) -> None:
        """Handle app mention events with agent."""
        user: str = event.get("user", "u_123")
        text: str = event.get("text", "")
        logger.info(f"App mentioned by user {user}: {text}")
        say(text)

        full_response_text = ""
        for event_data in agent.stream_query(
            user_id="u_123",
            message=text,
        ):
            if (
                "content" in event_data
                and "parts" in event_data["content"]
                and "text" in event_data["content"]["parts"][0]
            ):
                full_response_text += event_data["content"]["parts"][0]["text"]

        say(full_response_text)

    return app_mention


def get_slack_app(
    settings: SettingsDep,
    ack: Annotated[Callable[[dict, Any], None], Depends(get_ack)],
    app_mention: Annotated[Callable[[dict, Any, dict], None], Depends(get_app_mention)],
) -> "SlackApp":
    """Create and configure Slack App with agent dependency."""
    try:
        from slack_bolt import App as SlackApp
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "slack-bolt is required for Slack integration. "
                "Install with: pip install fastapi-agentrouter[slack]"
            ),
        ) from e

    if settings.slack is None:
        raise HTTPException(
            status_code=500,
            detail="Slack settings are not configured.",
        )

    slack_bot_token = settings.slack.bot_token
    slack_signing_secret = settings.slack.signing_secret

    slack_app = SlackApp(
        token=slack_bot_token,
        signing_secret=slack_signing_secret,
        process_before_response=True,
    )

    # Register event handlers with lazy listeners
    slack_app.event("app_mention")(ack=ack, lazy=[app_mention])

    return slack_app


def get_slack_request_handler(
    slack_app: Annotated["SlackApp", Depends(get_slack_app)],
) -> "SlackRequestHandler":
    """Get Slack request handler with agent dependency."""
    try:
        from slack_bolt.adapter.fastapi import SlackRequestHandler
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "slack-bolt is required for Slack integration. "
                "Install with: pip install fastapi-agentrouter[slack]"
            ),
        ) from e

    return SlackRequestHandler(slack_app)

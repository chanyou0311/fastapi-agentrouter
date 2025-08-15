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
        thread_ts: str = event.get("thread_ts") or event.get("ts", "")

        logger.info(f"App mentioned by user {user}: {text}")

        # Use thread_ts as session_id and the original message ts as user_id
        # This allows multiple users to interact within the same thread context
        session_id = thread_ts
        user_id = thread_ts  # Use thread identifier for consistent context

        full_response_text = ""
        for event_data in agent.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=text,
        ):
            if (
                "content" in event_data
                and "parts" in event_data["content"]
                and "text" in event_data["content"]["parts"][0]
            ):
                full_response_text += event_data["content"]["parts"][0]["text"]

        # Reply in thread
        say(text=full_response_text, thread_ts=thread_ts)

    return app_mention


def get_message(
    agent: AgentDep, settings: SettingsDep
) -> Callable[[dict, Any, dict, Any], None]:
    """Get message event handler for thread messages."""

    def message(event: dict, say: Any, body: dict, client: Any) -> None:
        """Handle message events in threads where bot was mentioned."""
        # Only process messages in threads
        thread_ts = event.get("thread_ts")
        if not thread_ts:
            return

        # Skip bot messages
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            return

        # Get bot user ID
        bot_user_id = body.get("authorizations", [{}])[0].get("user_id")
        if not bot_user_id:
            return

        # Check if bot was mentioned in the parent message
        try:
            response = client.conversations_replies(
                channel=event["channel"], ts=thread_ts, limit=1, inclusive=True
            )

            parent_message = response.get("messages", [{}])[0]
            parent_text = parent_message.get("text", "")

            # Check if bot was mentioned in parent message
            if f"<@{bot_user_id}>" not in parent_text:
                return

        except Exception as e:
            logger.error(f"Error checking parent message: {e}")
            return

        # Process the message
        user: str = event.get("user", "u_123")
        text: str = event.get("text", "")

        logger.info(f"Processing thread message from user {user}: {text}")

        # Use thread_ts as both session_id and user_id for consistent context
        session_id = thread_ts
        user_id = thread_ts

        full_response_text = ""
        for event_data in agent.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=text,
        ):
            if (
                "content" in event_data
                and "parts" in event_data["content"]
                and "text" in event_data["content"]["parts"][0]
            ):
                full_response_text += event_data["content"]["parts"][0]["text"]

        # Reply in thread
        say(text=full_response_text, thread_ts=thread_ts)

    return message


def get_slack_app(
    settings: SettingsDep,
    ack: Annotated[Callable[[dict, Any], None], Depends(get_ack)],
    app_mention: Annotated[Callable[[dict, Any, dict], None], Depends(get_app_mention)],
    message: Annotated[Callable[[dict, Any, dict, Any], None], Depends(get_message)],
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
    slack_app.event("message")(ack=ack, lazy=[message])

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

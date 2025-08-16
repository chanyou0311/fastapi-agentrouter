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
        channel: str = event.get("channel", "")
        # Get thread_ts from event (if in thread) or use the event's ts
        thread_ts: str = event.get("thread_ts") or event.get("ts", "")
        logger.info(f"App mentioned by user {user} in channel {channel}: {text}")

        # Create a session for this conversation
        session = agent.create_session(user_id=user)
        session_id = session.get("id")
        logger.info(f"Created session {session_id} for user {user}")

        full_response_text = ""
        for event_data in agent.stream_query(
            user_id=user,
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
        say(text=full_response_text, channel=channel, thread_ts=thread_ts)

    return app_mention


def get_message(agent: AgentDep) -> Callable[[dict, Any, Any, dict], None]:
    """Get message event handler for thread replies."""

    def message(event: dict, say: Any, client: Any, body: dict) -> None:
        """Handle message events in threads where bot was previously mentioned."""
        # Only process messages in threads
        if "thread_ts" not in event:
            return

        # Skip if this is a bot message
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            return

        user: str = event.get("user", "u_123")
        text: str = event.get("text", "")
        channel: str = event.get("channel", "")
        thread_ts: str = event.get("thread_ts", "")

        # Get bot user ID from the auth info
        bot_user_id = body.get("authorizations", [{}])[0].get("user_id", "")

        # Skip if the message mentions the bot (app_mention will handle it)
        if bot_user_id and f"<@{bot_user_id}>" in text:
            return

        # Check if the bot has participated in this thread
        # Get thread replies to see if bot has responded before
        result = client.conversations_replies(
            channel=channel,
            ts=thread_ts,
            limit=100,  # Get recent messages in thread
        )

        # Check if bot has sent any messages in this thread
        bot_has_responded = False
        for message in result.get("messages", []):
            if message.get("user") == bot_user_id:
                bot_has_responded = True
                break

        # Only respond if bot has previously participated in the thread
        if not bot_has_responded:
            logger.debug(f"Bot has not participated in thread {thread_ts}, skipping")
            return

        logger.info(f"Message in thread from user {user} in channel {channel}: {text}")

        # Create a session for this conversation
        session = agent.create_session(user_id=user)
        session_id = session.get("id")
        logger.info(f"Created session {session_id} for user {user}")

        full_response_text = ""
        for event_data in agent.stream_query(
            user_id=user,
            session_id=session_id,
            message=text,
        ):
            if (
                "content" in event_data
                and "parts" in event_data["content"]
                and "text" in event_data["content"]["parts"][0]
            ):
                full_response_text += event_data["content"]["parts"][0]["text"]

        # Reply in the same thread
        say(text=full_response_text, channel=channel, thread_ts=thread_ts)

    return message


def get_slack_app(
    settings: SettingsDep,
    ack: Annotated[Callable[[dict, Any], None], Depends(get_ack)],
    app_mention: Annotated[Callable[[dict, Any, dict], None], Depends(get_app_mention)],
    message: Annotated[Callable[[dict, Any, Any, dict], None], Depends(get_message)],
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

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
        thread_ts: str = event.get("thread_ts", event.get("ts", ""))

        logger.info(f"App mentioned by user {user} in channel {channel}: {text}")

        # Use thread_ts as session_id for context continuity
        # Use the first message timestamp as user_id to identify the conversation
        user_id = thread_ts
        session_id = f"{channel}_{thread_ts}"

        full_response_text = ""
        try:
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
                logger.debug(f"Received event_data: {event_data}")
        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
            say(text=f"Sorry, I encountered an error: {e!s}", thread_ts=thread_ts)
            return

        # Reply in thread only if there's content
        if full_response_text:
            logger.info(f"Sending response: {full_response_text[:100]}...")
            say(text=full_response_text, thread_ts=thread_ts)
        else:
            logger.warning("Agent returned empty response")
            say(
                text="I received your message but couldn't generate a response.",
                thread_ts=thread_ts,
            )

    return app_mention


def get_message(agent: AgentDep) -> Callable[[dict, Any, dict, Any], None]:
    """Get message event handler for thread messages."""

    def message(event: dict, say: Any, body: dict, client: Any) -> None:
        """Handle message events in threads where bot was mentioned."""
        # Skip if this is a bot message
        if event.get("bot_id") or event.get("subtype"):
            return

        thread_ts = event.get("thread_ts")
        if not thread_ts:
            # Not a thread message
            return

        channel = event.get("channel", "")
        user = event.get("user", "u_123")
        text = event.get("text", "")

        # Check if this thread was initiated by a bot mention
        thread_key = f"{channel}_{thread_ts}"

        # Get thread history to check if bot was mentioned in the thread
        try:
            result = client.conversations_replies(
                channel=channel, ts=thread_ts, limit=100
            )
            messages = result.get("messages", [])

            # Check if bot was mentioned in any message in the thread
            bot_mentioned_in_thread = False
            bot_user_id = client.auth_test()["user_id"]

            for msg in messages:
                msg_text = msg.get("text", "")
                if f"<@{bot_user_id}>" in msg_text:
                    bot_mentioned_in_thread = True
                    break

            if not bot_mentioned_in_thread:
                # Bot was never mentioned in this thread, ignore
                return

        except Exception as e:
            logger.error(f"Error checking thread history: {e}")
            return

        # Check if message contains (aside) and bot is not mentioned
        bot_mentioned_in_message = f"<@{bot_user_id}>" in text
        if "(aside)" in text and not bot_mentioned_in_message:
            logger.info(f"Ignoring message with (aside) in thread {thread_key}")
            return

        logger.info(
            f"Processing message in thread {thread_key} from user {user}: {text}"
        )

        # Use thread_ts as both user_id and part of session_id for context continuity
        user_id = thread_ts
        session_id = thread_key

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
        if full_response_text:
            say(text=full_response_text, thread_ts=thread_ts)

    return message


def get_slack_app(
    settings: SettingsDep,
    ack: Annotated[Callable[[dict, Any], None], Depends(get_ack)],
    app_mention: Annotated[Callable[[dict, Any, dict], None], Depends(get_app_mention)],
    message: Annotated[Callable[[dict, Any, dict], None], Depends(get_message)],
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

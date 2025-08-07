"""Slack integration router."""

import logging
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from ...core.dependencies import Agent
from .dependencies import check_slack_enabled
from .settings import get_slack_settings

if TYPE_CHECKING:
    from slack_bolt import App

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slack", tags=["slack"])


def get_slack_app(agent: Agent) -> "App":
    """Create and configure Slack App with agent dependency."""
    try:
        from slack_bolt import App
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "slack-bolt is required for Slack integration. "
                "Install with: pip install fastapi-agentrouter[slack]"
            ),
        ) from e

    # Get settings
    settings = get_slack_settings()
    
    if not settings.slack_bot_token or not settings.slack_signing_secret:
        raise HTTPException(
            status_code=500,
            detail=(
                "SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET "
                "environment variables are required"
            ),
        )

    # Create Slack app instance
    slack_app = App(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret,
        process_before_response=True,  # For serverless environments
        token_verification_enabled=settings.slack_token_verification,
        request_verification_enabled=settings.slack_request_verification,
    )

    # Define event handlers with lazy listeners
    def ack(body: dict, ack_func: Any) -> None:
        """Acknowledge the event."""
        ack_func()

    def lazy_app_mention(event: dict, say: Any, body: dict) -> None:
        """Handle app mention events with agent."""
        user_id = event.get("user")
        text = event.get("text", "")
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")

        logger.info(f"App mentioned by user {user_id}: {text}")

        try:
            # Stream responses from agent
            full_response = ""
            for response in agent.stream_query(
                message=text,
                user_id=user_id,
                session_id=f"slack_{channel}_{thread_ts}",
                platform="slack",
                channel=channel,
                thread_ts=thread_ts,
            ):
                # Handle different response formats
                if isinstance(response, str):
                    full_response += response
                elif isinstance(response, dict):
                    # Support structured responses
                    if "content" in response:
                        content = response["content"]
                        if isinstance(content, str):
                            full_response += content
                        elif isinstance(content, dict) and "parts" in content:
                            # Handle multi-part responses
                            for part in content["parts"]:
                                if isinstance(part, dict) and "text" in part:
                                    full_response += part["text"]
                                elif isinstance(part, str):
                                    full_response += part
                    elif "text" in response:
                        full_response += response["text"]

            # Send response to Slack
            if full_response:
                say(text=full_response, channel=channel, thread_ts=thread_ts)
            else:
                say(
                    text="I received your message but couldn't generate a response.",
                    channel=channel,
                    thread_ts=thread_ts,
                )

        except Exception as e:
            logger.error(f"Error handling app mention: {e}")
            say(
                text=f"Sorry, I encountered an error: {e!s}",
                channel=channel,
                thread_ts=thread_ts,
            )

    def lazy_message(event: dict, say: Any, body: dict) -> None:
        """Handle direct messages to the bot."""
        # Skip messages from bots
        if event.get("bot_id"):
            return

        user_id = event.get("user")
        text = event.get("text", "")
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")

        logger.info(f"Direct message from user {user_id}: {text}")

        try:
            # Stream responses from agent
            full_response = ""
            for response in agent.stream_query(
                message=text,
                user_id=user_id,
                session_id=f"slack_{channel}_{thread_ts}",
                platform="slack",
                channel=channel,
                thread_ts=thread_ts,
            ):
                # Handle different response formats
                if isinstance(response, str):
                    full_response += response
                elif isinstance(response, dict):
                    # Support structured responses
                    if "content" in response:
                        content = response["content"]
                        if isinstance(content, str):
                            full_response += content
                        elif isinstance(content, dict) and "parts" in content:
                            # Handle multi-part responses
                            for part in content["parts"]:
                                if isinstance(part, dict) and "text" in part:
                                    full_response += part["text"]
                                elif isinstance(part, str):
                                    full_response += part
                    elif "text" in response:
                        full_response += response["text"]

            # Send response to Slack
            if full_response:
                say(text=full_response, channel=channel, thread_ts=thread_ts)
            else:
                say(
                    text="I received your message but couldn't generate a response.",
                    channel=channel,
                    thread_ts=thread_ts,
                )

        except Exception as e:
            logger.error(f"Error handling direct message: {e}")
            say(
                text=f"Sorry, I encountered an error: {e!s}",
                channel=channel,
                thread_ts=thread_ts,
            )

    # Register event handlers with lazy listeners
    slack_app.event("app_mention")(ack=ack, lazy=[lazy_app_mention])
    slack_app.event("message")(ack=ack, lazy=[lazy_message])

    return slack_app


def get_slack_request_handler(agent: Agent) -> Any:
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

    slack_app = get_slack_app(agent)
    return SlackRequestHandler(slack_app)


@router.post("/events", dependencies=[Depends(check_slack_enabled)])
async def slack_events(
    request: Request,
    agent: Agent,
) -> Any:
    """Handle Slack events and interactions."""
    handler = get_slack_request_handler(agent)
    return await handler.handle(request)

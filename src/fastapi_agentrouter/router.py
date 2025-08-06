"""FastAPI router for agent integrations."""

from typing import TYPE_CHECKING, Any, Optional, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

if TYPE_CHECKING:
    from vertexai.preview.reasoning_engines import AdkApp


class AgentProtocol(Protocol):
    """Protocol for agent implementations."""

    def stream_query(
        self,
        *,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Stream responses from the agent."""
        ...


def create_slack_handler(get_agent: Any) -> Any:
    """Create Slack event handler with agent dependency."""
    import hashlib
    import hmac
    import json
    import time
    from urllib.parse import parse_qs

    async def handle_slack_events(
        request: Request,
        agent: AgentProtocol = Depends(get_agent),
    ) -> Response:
        """Handle Slack events and slash commands."""
        # Get signing secret from environment or config
        import os

        signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
        if not signing_secret:
            raise HTTPException(
                status_code=500, detail="SLACK_SIGNING_SECRET not configured"
            )

        # Get request body and headers
        body = await request.body()
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")

        # Verify signature
        if abs(time.time() - float(timestamp)) > 60 * 5:
            raise HTTPException(status_code=400, detail="Request timestamp too old")

        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        my_signature = (
            "v0="
            + hmac.new(
                signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
            ).hexdigest()
        )

        if not hmac.compare_digest(my_signature, signature):
            raise HTTPException(status_code=400, detail="Invalid request signature")

        # Parse request body
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = json.loads(body)
        else:
            parsed = parse_qs(body.decode("utf-8"))
            data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        # Handle URL verification
        if data.get("type") == "url_verification":
            return PlainTextResponse(content=data.get("challenge", ""))

        # Extract message text
        text = ""
        user_id = ""
        if "event" in data:
            # Event callback
            event = data["event"]
            text = event.get("text", "")
            user_id = event.get("user", "")
        elif "text" in data:
            # Slash command
            text = data.get("text", "")
            user_id = data.get("user_id", "")

        if not text:
            return PlainTextResponse(content="Please provide a message.")

        # Query agent and stream response
        try:
            response_parts = []
            for event in agent.stream_query(message=text, user_id=user_id):
                if hasattr(event, "content"):
                    response_parts.append(event.content)
                elif isinstance(event, str):
                    response_parts.append(event)

            response_text = "".join(response_parts)
            return PlainTextResponse(content=response_text)

        except Exception as e:
            return PlainTextResponse(content=f"Error: {str(e)}")

    return handle_slack_events


def create_discord_handler(get_agent: Any) -> Any:
    """Create Discord interaction handler with agent dependency."""

    async def handle_discord_interactions(
        request: Request,
        agent: AgentProtocol = Depends(get_agent),
    ) -> JSONResponse:
        """Handle Discord interactions."""
        import os

        public_key = os.getenv("DISCORD_PUBLIC_KEY", "")
        if not public_key:
            raise HTTPException(
                status_code=500, detail="DISCORD_PUBLIC_KEY not configured"
            )

        # Get request headers and body
        signature = request.headers.get("X-Signature-Ed25519", "")
        timestamp = request.headers.get("X-Signature-Timestamp", "")
        body = await request.body()

        # Verify signature
        try:
            from nacl.exceptions import BadSignatureError
            from nacl.signing import VerifyKey
        except ImportError as e:
            raise ImportError(
                "PyNaCl is required for Discord integration. "
                "Install with: pip install PyNaCl"
            ) from e

        message = timestamp.encode() + body

        try:
            verify_key = VerifyKey(bytes.fromhex(public_key))
            verify_key.verify(message, bytes.fromhex(signature))
        except (BadSignatureError, Exception):
            raise HTTPException(status_code=401, detail="Invalid request signature")

        # Parse interaction
        import json

        interaction = json.loads(body)

        # Handle PING
        if interaction.get("type") == 1:
            return JSONResponse(content={"type": 1})

        # Handle application command
        if interaction.get("type") == 2:
            data = interaction.get("data", {})
            options = data.get("options", [])
            message_text = ""

            if options:
                message_text = options[0].get("value", "")

            if not message_text:
                return JSONResponse(
                    content={
                        "type": 4,
                        "data": {"content": "Please provide a message."},
                    }
                )

            # Query agent
            try:
                response_parts = []
                user_id = interaction.get("member", {}).get("user", {}).get("id", "")

                for event in agent.stream_query(message=message_text, user_id=user_id):
                    if hasattr(event, "content"):
                        response_parts.append(event.content)
                    elif isinstance(event, str):
                        response_parts.append(event)

                response_text = "".join(response_parts)

                return JSONResponse(
                    content={"type": 4, "data": {"content": response_text}}
                )

            except Exception as e:
                return JSONResponse(
                    content={"type": 4, "data": {"content": f"Error: {str(e)}"}}
                )

        return JSONResponse(
            content={"type": 4, "data": {"content": "Unsupported interaction type"}}
        )

    return handle_discord_interactions


def create_webhook_handler(get_agent: Any) -> Any:
    """Create generic webhook handler with agent dependency."""

    async def handle_webhook(
        request: Request,
        agent: AgentProtocol = Depends(get_agent),
    ) -> JSONResponse:
        """Handle generic webhook requests."""
        data = await request.json()
        message = data.get("message", "")
        user_id = data.get("user_id", None)
        session_id = data.get("session_id", None)

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        try:

            response_parts = []
            for event in agent.stream_query(
                message=message, user_id=user_id, session_id=session_id
            ):
                if hasattr(event, "content"):
                    response_parts.append(event.content)
                elif isinstance(event, str):
                    response_parts.append(event)

            response_text = "".join(response_parts)

            return JSONResponse(
                content={"response": response_text, "session_id": session_id}
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return handle_webhook


# Pre-configured router
router = APIRouter(prefix="/agent")


def setup_router(
    router: APIRouter,
    *,
    get_agent: Any,
    enable_slack: bool = True,
    enable_discord: bool = True,
    enable_webhook: bool = True,
) -> None:
    """Setup router with agent handlers.

    Args:
        router: FastAPI router to configure
        get_agent: Dependency function that returns an agent instance
        enable_slack: Enable Slack integration
        enable_discord: Enable Discord integration
        enable_webhook: Enable generic webhook endpoint
    """
    if enable_slack:
        slack_handler = create_slack_handler(get_agent)
        router.post("/slack/events")(slack_handler)

    if enable_discord:
        discord_handler = create_discord_handler(get_agent)
        router.post("/discord/interactions")(discord_handler)

    if enable_webhook:
        webhook_handler = create_webhook_handler(get_agent)
        router.post("/webhook")(webhook_handler)


# Default router with all integrations
def create_default_router(get_agent: Any) -> APIRouter:
    """Create a pre-configured router with all integrations.

    Args:
        get_agent: Dependency function that returns an agent instance

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/agent")
    setup_router(router, get_agent=get_agent)
    return router
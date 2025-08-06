"""FastAPI router for agent integrations."""

import os
from typing import TYPE_CHECKING, Any, Callable, Optional, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse, Response

if TYPE_CHECKING:
    pass


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


class AgentRouter(APIRouter):
    """Router with agent integration support."""

    def __init__(
        self,
        get_agent: Callable[[], AgentProtocol],
        *,
        prefix: str = "/agent",
        enable_slack: bool = True,
        enable_discord: bool = True,
        enable_webhook: bool = True,
        **kwargs: Any,
    ):
        """Initialize router with agent handlers.

        Args:
            get_agent: Function that returns an agent instance
            prefix: URL prefix for the router
            enable_slack: Enable Slack integration
            enable_discord: Enable Discord integration
            enable_webhook: Enable webhook endpoint
            **kwargs: Additional arguments passed to APIRouter
        """
        super().__init__(prefix=prefix, **kwargs)

        self.get_agent = get_agent
        self.enable_slack = enable_slack
        self.enable_discord = enable_discord
        self.enable_webhook = enable_webhook

        # Always add all routes
        self._add_slack_route()
        self._add_discord_route()
        self._add_webhook_route()

    def _add_slack_route(self) -> None:
        """Add Slack events endpoint."""

        async def handle_slack_events(request: Request) -> Response:
            """Handle Slack events and slash commands."""
            if not self.enable_slack:
                raise HTTPException(
                    status_code=501, detail="Slack integration is not enabled"
                )

            agent = self.get_agent()

            # Get signing secret from environment
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
            import hashlib
            import hmac
            import time

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
            import json
            from urllib.parse import parse_qs

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
                return PlainTextResponse(content=f"Error: {e!s}")

        self.add_api_route(
            "/slack/events",
            handle_slack_events,
            methods=["POST"],
            dependencies=[Depends(self.get_agent)],
        )

    def _add_discord_route(self) -> None:
        """Add Discord interactions endpoint."""

        async def handle_discord_interactions(request: Request) -> JSONResponse:
            """Handle Discord interactions."""
            if not self.enable_discord:
                raise HTTPException(
                    status_code=501, detail="Discord integration is not enabled"
                )

            agent = self.get_agent()

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
            except (BadSignatureError, Exception) as e:
                raise HTTPException(
                    status_code=401, detail="Invalid request signature"
                ) from e

            # Parse interaction
            import json

            interaction = json.loads(body)

            # Handle PING
            if interaction.get("type") == 1:
                return JSONResponse(content={"type": 1})

            # Handle APPLICATION_COMMAND
            if interaction.get("type") == 2:
                # Get command data
                data = interaction.get("data", {})
                command_name = data.get("name", "")
                options = data.get("options", [])

                # Get message from options or use command name
                message_text = command_name
                for option in options:
                    if option.get("name") == "message":
                        message_text = option.get("value", command_name)
                        break

                user_id = interaction.get("member", {}).get("user", {}).get("id", "")

                # Query agent
                try:
                    response_parts = []
                    for event in agent.stream_query(
                        message=message_text, user_id=user_id
                    ):
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
                        content={"type": 4, "data": {"content": f"Error: {e!s}"}}
                    )

            return JSONResponse(
                content={"type": 4, "data": {"content": "Unsupported interaction type"}}
            )

        self.add_api_route(
            "/discord/interactions",
            handle_discord_interactions,
            methods=["POST"],
            dependencies=[Depends(self.get_agent)],
        )

    def _add_webhook_route(self) -> None:
        """Add generic webhook endpoint."""

        async def handle_webhook(request: Request) -> JSONResponse:
            """Handle generic webhook requests."""
            if not self.enable_webhook:
                raise HTTPException(
                    status_code=501, detail="Webhook endpoint is not enabled"
                )

            agent = self.get_agent()

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

        self.add_api_route(
            "/webhook",
            handle_webhook,
            methods=["POST"],
            dependencies=[Depends(self.get_agent)],
        )


def create_agent_router(
    get_agent: Callable[[], AgentProtocol],
    *,
    prefix: str = "/agent",
    enable_slack: bool = True,
    enable_discord: bool = True,
    enable_webhook: bool = True,
    **kwargs: Any,
) -> AgentRouter:
    """Create a router with agent handlers.

    This is the recommended way to integrate agents with FastAPI.
    All endpoints are always defined, but disabled endpoints return 501.

    Args:
        get_agent: Function that returns an agent instance
        prefix: URL prefix for the router (default: "/agent")
        enable_slack: Enable Slack integration (default: True)
        enable_discord: Enable Discord integration (default: True)
        enable_webhook: Enable webhook endpoint (default: True)
        **kwargs: Additional arguments passed to APIRouter

    Returns:
        AgentRouter configured with all handlers

    Example:
        ```python
        from fastapi import FastAPI
        from fastapi_agentrouter import create_agent_router

        def get_agent():
            return your_agent

        app = FastAPI()
        app.include_router(create_agent_router(get_agent))
        ```
    """
    return AgentRouter(
        get_agent,
        prefix=prefix,
        enable_slack=enable_slack,
        enable_discord=enable_discord,
        enable_webhook=enable_webhook,
        **kwargs,
    )

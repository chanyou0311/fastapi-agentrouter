"""Class-based dependencies for complex event handling logic."""

import json
import logging
import time
from collections import deque
from typing import Annotated, Any, Optional

from fastapi import Depends

from .config import AgentConfig, get_agent_config
from .dependencies import Agent
from .security import SecurityContext, get_security_context
from .settings import Settings, settings

logger = logging.getLogger(__name__)


class BaseEventHandler:
    """Base class for event handlers with dependency injection support."""

    def __init__(
        self,
        agent: Agent,
        settings: Annotated[Settings, Depends(lambda: settings)],
        security_context: Annotated[SecurityContext, Depends(get_security_context)],
    ):
        """Initialize event handler with dependencies.

        Args:
            agent: Agent instance from dependency injection
            settings: Application settings
            security_context: Security context for the request
        """
        self.agent = agent
        self.settings = settings
        self.security_context = security_context
        self.event_queue: deque = deque(maxlen=100)
        self.processed_count = 0

    async def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process an event and return response.

        Args:
            event: Event data to process

        Returns:
            Response dictionary
        """
        # Log event with security context
        logger.info(
            f"Processing event for {self.security_context.user_id} "
            f"on {self.security_context.platform}"
        )

        # Add to queue for potential retry/analysis
        self.event_queue.append(event)
        self.processed_count += 1

        # Default implementation
        return {"status": "processed", "event_id": event.get("id")}

    def get_stats(self) -> dict[str, Any]:
        """Get handler statistics."""
        return {
            "processed_count": self.processed_count,
            "queue_size": len(self.event_queue),
            "platform": self.security_context.platform,
        }


class SlackEventHandler(BaseEventHandler):
    """Slack-specific event handler with state management."""

    def __init__(
        self,
        agent: Agent,
        settings: Annotated[Settings, Depends(lambda: settings)],
        security_context: Annotated[SecurityContext, Depends(get_security_context)],
    ):
        """Initialize Slack event handler."""
        super().__init__(agent, settings, security_context)
        self.thread_contexts: dict[str, list[dict]] = {}
        self.channel_settings: dict[str, dict] = {}

    async def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process Slack event with context awareness.

        Args:
            event: Slack event data

        Returns:
            Response for Slack
        """
        await super().process_event(event)

        # event_type = event.get("type")  # Reserved for future use
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")
        user_id = event.get("user")
        text = event.get("text", "")

        # Maintain thread context
        thread_key = f"{channel}_{thread_ts}"
        if thread_key not in self.thread_contexts:
            self.thread_contexts[thread_key] = []

        self.thread_contexts[thread_key].append(
            {"user": user_id, "text": text, "timestamp": event.get("ts")}
        )

        # Get channel-specific settings
        channel_config = self.channel_settings.get(
            channel or "", {"response_style": "normal"}
        )

        # Process with agent including context
        context = {
            "platform": "slack",
            "channel": channel,
            "thread_ts": thread_ts,
            "thread_history": self.thread_contexts[thread_key][-10:],  # Last 10 msgs
            "channel_config": channel_config,
        }

        response_parts = []
        for chunk in self.agent.stream_query(
            message=text, user_id=user_id, session_id=thread_key, **context
        ):
            if isinstance(chunk, str):
                response_parts.append(chunk)
            elif isinstance(chunk, dict) and "content" in chunk:
                response_parts.append(chunk["content"])

        response_text = "".join(response_parts)

        # Apply channel-specific formatting
        if channel_config.get("response_style") == "formal":
            response_text = self._format_formal(response_text)

        return {
            "text": response_text,
            "channel": channel,
            "thread_ts": thread_ts,
        }

    def _format_formal(self, text: str) -> str:
        """Apply formal formatting to response."""
        # Simple example - in practice would be more sophisticated
        return f"Thank you for your inquiry.\n\n{text}\n\nBest regards,\nAI Assistant"

    def update_channel_settings(self, channel: str, settings: dict[str, Any]) -> None:
        """Update settings for a specific channel."""
        self.channel_settings[channel] = settings

    def clear_thread_context(self, channel: str, thread_ts: str) -> None:
        """Clear context for a specific thread."""
        thread_key = f"{channel}_{thread_ts}"
        self.thread_contexts.pop(thread_key, None)


class WebhookEventHandler(BaseEventHandler):
    """Generic webhook event handler with retry logic."""

    def __init__(
        self,
        agent: Agent,
        settings: Annotated[Settings, Depends(lambda: settings)],
        security_context: Annotated[SecurityContext, Depends(get_security_context)],
        config: Annotated[AgentConfig, Depends(get_agent_config)],
    ):
        """Initialize webhook handler with additional config dependency."""
        super().__init__(agent, settings, security_context)
        self.config = config
        self.retry_queue: deque = deque(maxlen=50)
        self.failed_events: list[dict] = []

    async def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process webhook event with retry logic.

        Args:
            event: Webhook event data

        Returns:
            Response dictionary
        """
        await super().process_event(event)

        max_retries = self.config.retry_count
        retry_count = event.get("_retry_count", 0)

        try:
            # Extract message from webhook payload
            message = WebhookEventHandler._extract_message(event)

            # Process with agent
            response = await self._process_with_agent(message, event)

            return {
                "status": "success",
                "response": response,
                "retry_count": retry_count,
            }

        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")

            if retry_count < max_retries:
                # Add to retry queue
                event["_retry_count"] = retry_count + 1
                self.retry_queue.append(event)
                return {
                    "status": "retry",
                    "retry_count": retry_count + 1,
                    "error": str(e),
                }
            else:
                # Max retries exceeded
                self.failed_events.append(event)
                return {
                    "status": "failed",
                    "retry_count": retry_count,
                    "error": f"Max retries ({max_retries}) exceeded",
                }

    @staticmethod
    def _extract_message(event: dict[str, Any]) -> str:
        """Extract message from webhook payload."""
        # Try common webhook formats
        if "message" in event:
            return str(event["message"])
        elif "text" in event:
            return str(event["text"])
        elif "body" in event:
            body = event["body"]
            if isinstance(body, str):
                return body
            return json.dumps(body)
        else:
            return json.dumps(event)

    async def _process_with_agent(self, message: str, event: dict[str, Any]) -> str:
        """Process message with agent."""
        response_parts = []
        for chunk in self.agent.stream_query(
            message=message,
            user_id=self.security_context.user_id,
            session_id=self.security_context.request_id,
            webhook_data=event,
        ):
            if isinstance(chunk, str):
                response_parts.append(chunk)

        return "".join(response_parts)

    async def process_retry_queue(self) -> dict[str, Any]:
        """Process events in retry queue."""
        processed = 0
        failed = 0

        while self.retry_queue:
            event = self.retry_queue.popleft()
            result = await self.process_event(event)

            if result["status"] == "success":
                processed += 1
            else:
                failed += 1

        return {"processed": processed, "failed": failed}


class ConversationManager:
    """Manages conversation state and history."""

    def __init__(
        self,
        agent: Agent,
        settings: Annotated[Settings, Depends(lambda: settings)],
    ):
        """Initialize conversation manager."""
        self.agent = agent
        self.settings = settings
        self.conversations: dict[str, list[dict]] = {}
        self.max_history_length = 50

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add message to conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }

        self.conversations[conversation_id].append(message)

        # Trim history if too long
        if len(self.conversations[conversation_id]) > self.max_history_length:
            self.conversations[conversation_id] = self.conversations[conversation_id][
                -self.max_history_length :
            ]

    def get_history(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> list[dict]:
        """Get conversation history."""
        history = self.conversations.get(conversation_id, [])
        if limit:
            return history[-limit:]
        return history

    def clear_conversation(self, conversation_id: str) -> None:
        """Clear conversation history."""
        self.conversations.pop(conversation_id, None)

    async def process_message(
        self,
        conversation_id: str,
        message: str,
        user_id: Optional[str] = None,
    ) -> str:
        """Process message with conversation context."""
        # Add user message to history
        self.add_message(conversation_id, "user", message, {"user_id": user_id})

        # Get conversation context
        history = self.get_history(conversation_id, limit=10)

        # Process with agent
        response_parts = []
        for chunk in self.agent.stream_query(
            message=message,
            user_id=user_id,
            session_id=conversation_id,
            conversation_history=history,
        ):
            if isinstance(chunk, str):
                response_parts.append(chunk)

        response = "".join(response_parts)

        # Add assistant response to history
        self.add_message(conversation_id, "assistant", response)

        return response


# Dependency annotations for cleaner usage
SlackHandlerDep = Annotated[SlackEventHandler, Depends()]
WebhookHandlerDep = Annotated[WebhookEventHandler, Depends()]
ConversationDep = Annotated[ConversationManager, Depends()]

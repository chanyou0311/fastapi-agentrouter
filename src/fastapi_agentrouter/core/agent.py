"""Agent interface and response models."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Standard response from an agent."""

    content: str
    metadata: Optional[dict[str, Any]] = None


class Agent(ABC):
    """Abstract base class for AI agents."""

    @abstractmethod
    async def handle_slack(self, event: dict[str, Any]) -> str:
        """Handle Slack events.

        Args:
            event: Slack event data

        Returns:
            Response string for Slack
        """
        pass

    @abstractmethod
    async def handle_discord(self, interaction: dict[str, Any]) -> dict[str, Any]:
        """Handle Discord interactions.

        Args:
            interaction: Discord interaction data

        Returns:
            Discord interaction response
        """
        pass

    @abstractmethod
    async def handle_webhook(self, data: dict[str, Any]) -> AgentResponse:
        """Handle generic webhook requests.

        Args:
            data: Webhook request data

        Returns:
            Standard agent response
        """
        pass

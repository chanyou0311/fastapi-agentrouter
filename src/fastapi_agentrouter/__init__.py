"""FastAPI AgentRouter - AI Agent interface library for FastAPI."""

__version__ = "0.1.0"

from .router import (
    AgentProtocol,
    create_default_router,
    create_discord_handler,
    create_slack_handler,
    create_webhook_handler,
    router,
    setup_router,
)

__all__ = [
    "AgentProtocol",
    "__version__",
    "create_default_router",
    "create_discord_handler",
    "create_slack_handler",
    "create_webhook_handler",
    "router",
    "setup_router",
]

"""FastAPI AgentRouter - AI Agent interface library for FastAPI."""

__version__ = "0.1.0"

from .router import AgentProtocol, AgentRouter, create_agent_router

__all__ = [
    "AgentProtocol",
    "AgentRouter",
    "__version__",
    "create_agent_router",
]

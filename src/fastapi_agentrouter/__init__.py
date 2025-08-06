"""FastAPI AgentRouter - AI Agent interface library for FastAPI."""

__version__ = "0.1.0"

from .dependencies import AgentProtocol, get_agent_placeholder
from .routers import router

__all__ = [
    "AgentProtocol",
    "__version__",
    "get_agent_placeholder",
    "router",
]

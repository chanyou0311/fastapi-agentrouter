"""FastAPI AgentRouter - AI Agent interface library for FastAPI."""

__version__ = "0.4.2"

from .core.dependencies import AgentProtocol, get_agent
from .core.settings import Settings, get_settings
from .routers import router

__all__ = [
    "AgentProtocol",
    "Settings",
    "__version__",
    "get_agent",
    "get_settings",
    "router",
]

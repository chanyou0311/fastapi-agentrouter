"""FastAPI AgentRouter - AI Agent interface library for FastAPI."""

__version__ = "1.0.0"

from .core.dependencies import AgentProtocol, get_agent_placeholder
from .core.settings import Settings, SettingsProvider, get_settings
from .routers import router

__all__ = [
    "AgentProtocol",
    "Settings",
    "SettingsProvider",
    "__version__",
    "get_agent_placeholder",
    "get_settings",
    "router",
]

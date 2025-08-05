"""FastAPI AgentRouter - AI Agent interface library for FastAPI with multi-platform support."""

__version__ = "0.1.0"

from .core.agent import Agent, AgentResponse
from .core.router import build_router

__all__ = ["Agent", "AgentResponse", "build_router", "__version__"]
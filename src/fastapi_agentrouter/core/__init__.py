"""Core components for FastAPI AgentRouter."""

from .agent import Agent, AgentResponse
from .router import build_router

__all__ = ["Agent", "AgentResponse", "build_router"]
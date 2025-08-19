"""Agent implementations for FastAPI AgentRouter."""

from .base import BaseAgentAdapter
from .vertexai import VertexAIAgentAdapter, get_vertex_ai_agent

__all__ = [
    "BaseAgentAdapter",
    "VertexAIAgentAdapter",
    "get_vertex_ai_agent",
]

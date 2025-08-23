"""Vertex AI integration for FastAPI AgentRouter."""

from .adapter import VertexAIAgentAdapter, create_vertex_ai_adapter
from .dependencies import get_vertex_ai_agent

__all__ = [
    "VertexAIAgentAdapter",
    "create_vertex_ai_adapter",
    "get_vertex_ai_agent",
]

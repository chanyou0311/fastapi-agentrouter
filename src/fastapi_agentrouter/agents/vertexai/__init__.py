"""Vertex AI integration for FastAPI AgentRouter."""

from .adapter import VertexAIAgentAdapter, get_vertex_ai_agent
from .dependencies import get_vertex_ai_agent_engine

__all__ = ["VertexAIAgentAdapter", "get_vertex_ai_agent", "get_vertex_ai_agent_engine"]

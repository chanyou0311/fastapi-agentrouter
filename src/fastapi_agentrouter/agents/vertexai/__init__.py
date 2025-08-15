"""Vertex AI integration for FastAPI AgentRouter."""

from .dependencies import get_vertex_ai_agent_engine, warmup_vertex_ai_engine

__all__ = ["get_vertex_ai_agent_engine", "warmup_vertex_ai_engine"]

"""Vertex AI dependencies for FastAPI AgentRouter."""

from collections.abc import AsyncGenerator, Generator
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from ...core.settings import get_settings

if TYPE_CHECKING:
    from vertexai import Client
    from vertexai.agent_engines import AgentEngine


class VertexAIAgentWrapper:
    """Wrapper class to bridge AgentEngine with AgentProtocol interface.

    This wrapper provides compatibility between the new Vertex AI Agent Engine API
    and the existing AgentProtocol interface used by fastapi-agentrouter.
    """

    def __init__(
        self, agent_engine: "AgentEngine", client: "Client", resource_name: str
    ):
        """Initialize the wrapper with agent engine and client.

        Args:
            agent_engine: The Vertex AI AgentEngine instance
            client: The Vertex AI client for session management
            resource_name: The full resource name of the agent engine
        """
        self.agent_engine = agent_engine
        self.client = client
        self.resource_name = resource_name

    def list_sessions(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List sessions for a given user.

        Args:
            user_id: Optional user ID to filter sessions
            **kwargs: Additional keyword arguments

        Returns:
            Dictionary with 'sessions' key containing list of session dictionaries
        """
        sessions = []

        try:
            # Use the client sessions API to list sessions
            for session in self.client.agent_engines.sessions.list(
                name=self.resource_name
            ):
                # Filter by user_id if provided
                if user_id is None or getattr(session, "user_id", None) == user_id:
                    sessions.append({"id": session.name.split("/")[-1]})
        except Exception:
            # If sessions API fails, return empty list
            # This provides graceful degradation
            pass

        return {"sessions": sessions}

    def create_session(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new session for the agent.

        Args:
            user_id: Optional user ID for the session
            **kwargs: Additional keyword arguments

        Returns:
            Dictionary containing at least the session 'id'
        """
        try:
            # Try to use the agent engine's session creation method
            if hasattr(self.agent_engine, "async_create_session"):
                import asyncio

                async def _create_session() -> dict[str, Any]:
                    create_method = self.agent_engine.async_create_session
                    result = await create_method(user_id=user_id)
                    # Ensure we return a dict
                    if isinstance(result, dict):
                        return result
                    else:
                        return {"id": str(result)}

                # Run async method in sync context
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                return loop.run_until_complete(_create_session())
            else:
                # Fallback: generate a session ID
                import uuid

                return {"id": str(uuid.uuid4())}
        except Exception:
            # If session creation fails, generate a fallback ID
            # This provides graceful degradation
            import uuid

            return {"id": str(uuid.uuid4())}

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Generator[dict[str, Any], Any, None]:
        """Stream responses from the agent.

        Args:
            message: The query message
            user_id: Optional user ID
            session_id: Optional session ID
            **kwargs: Additional keyword arguments

        Yields:
            Dictionary containing response data
        """
        try:
            # Try to use the agent engine's streaming query method
            if hasattr(self.agent_engine, "async_stream_query"):
                import asyncio

                async def _async_stream() -> AsyncGenerator[dict[str, Any], None]:
                    stream_method = self.agent_engine.async_stream_query
                    async for event in stream_method(
                        message=message,
                        user_id=user_id,
                        session_id=session_id,
                        **kwargs,
                    ):
                        yield event

                # Run async generator in sync context
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                async_gen = _async_stream()
                try:
                    while True:
                        try:
                            event = loop.run_until_complete(async_gen.__anext__())
                            yield event
                        except StopAsyncIteration:
                            break
                finally:
                    loop.run_until_complete(async_gen.aclose())
            else:
                # Fallback: provide a basic response
                yield {"content": {"parts": [{"text": f"Response to: {message}"}]}}
        except Exception as e:
            # Fallback response for errors
            yield {"content": {"parts": [{"text": f"Error processing query: {e!s}"}]}}


@lru_cache
def get_vertex_ai_agent_engine() -> VertexAIAgentWrapper:
    """Get the Vertex AI AgentEngine wrapper for the specified agent.

    This function is cached to avoid expensive initialization on every request.
    The engine instance is automatically warmed up when the router is included
    in your FastAPI app, ensuring fast response times from the first request.

    Returns:
        VertexAIAgentWrapper: The cached Vertex AI agent wrapper instance

    Raises:
        ValueError: If agent is not found or multiple agents found
        ImportError: If google-cloud-aiplatform is not installed
        RuntimeError: If Vertex AI settings are not configured

    Example:
        # Set environment variables:
        # VERTEXAI__PROJECT_ID=your-project-id
        # VERTEXAI__LOCATION=us-central1
        # VERTEXAI__STAGING_BUCKET=your-bucket
        # VERTEXAI__AGENT_NAME=your-agent-name

        app.dependency_overrides[get_agent] = get_vertex_ai_agent_engine
    """
    settings = get_settings()

    if not settings.is_vertexai_enabled():
        raise RuntimeError(
            "Vertex AI settings not configured. Please set the required "
            "environment variables: VERTEXAI__PROJECT_ID, VERTEXAI__LOCATION, "
            "VERTEXAI__STAGING_BUCKET, VERTEXAI__AGENT_NAME"
        )

    try:
        import vertexai
        from vertexai import agent_engines
    except ImportError as e:
        raise ImportError(
            "google-cloud-aiplatform is not installed. "
            'Install with: pip install "fastapi-agentrouter[vertexai]"'
        ) from e

    vertexai_settings = settings.vertexai
    if not vertexai_settings:
        raise RuntimeError("Vertex AI settings not configured")

    vertexai.init(
        project=vertexai_settings.project_id,
        location=vertexai_settings.location,
        staging_bucket=vertexai_settings.staging_bucket,
    )

    # Create the Vertex AI client for session management
    client = vertexai.Client(
        project=vertexai_settings.project_id,
        location=vertexai_settings.location,
    )

    apps = list(
        agent_engines.list(filter=f"display_name={vertexai_settings.agent_name}")
    )

    if len(apps) == 0:
        raise ValueError(f"Agent '{vertexai_settings.agent_name}' not found.")
    elif len(apps) > 1:
        raise ValueError(
            f"Multiple agents found with name '{vertexai_settings.agent_name}'."
        )

    agent_engine = apps[0]

    # Construct the resource name for the agent engine
    resource_name = (
        f"projects/{vertexai_settings.project_id}/locations/"
        f"{vertexai_settings.location}/reasoningEngines/"
        f"{agent_engine.name.split('/')[-1]}"
    )

    # Return the wrapper instead of the raw AgentEngine
    return VertexAIAgentWrapper(
        agent_engine=agent_engine, client=client, resource_name=resource_name
    )

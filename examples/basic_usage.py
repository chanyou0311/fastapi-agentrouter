"""Basic usage example with FastAPI AgentRouter."""

from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

import fastapi_agentrouter

if TYPE_CHECKING:
    from vertexai.preview.reasoning_engines import AdkApp


# Example 1: Simplest usage - just include the router
app = FastAPI()


def get_agent() -> Any:
    """Get your agent instance.

    This could return:
    - Vertex AI AdkApp instance
    - Custom agent implementing AgentProtocol
    - Any object with stream_query method
    """

    # Example with mock agent for testing
    class MockAgent:
        def stream_query(self, *, message: str, **kwargs):
            yield f"Echo: {message}"

    return MockAgent()


# Override the dependency to provide your agent
app.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = get_agent

# Single line integration!
app.include_router(fastapi_agentrouter.router)


# Example 2: With Vertex AI ADK (when available)
def get_vertex_agent() -> "AdkApp":
    """Get Vertex AI ADK App instance."""
    try:
        from vertexai.preview import reasoning_engines  # noqa: F401

        # This would be your actual agent configuration
        # agent = Agent(
        #     name="my_agent",
        #     model="gemini-2.5-flash-lite",
        #     tools=[...],
        # )
        # return reasoning_engines.AdkApp(agent=agent, enable_tracing=True)

        # For demo, return mock
        class MockAdkApp:
            def stream_query(self, *, message: str, user_id=None, session_id=None):
                yield type("Event", (), {"content": f"Response to: {message}"})()

        return MockAdkApp()
    except ImportError:
        return get_agent()  # Fallback to mock


app2 = FastAPI()
app2.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = get_vertex_agent
app2.include_router(fastapi_agentrouter.router)


if __name__ == "__main__":
    import uvicorn

    # Run with: python examples/basic_usage.py
    uvicorn.run(app, host="0.0.0.0", port=8000)

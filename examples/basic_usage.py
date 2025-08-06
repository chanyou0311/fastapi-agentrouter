"""Basic usage example with FastAPI AgentRouter."""

from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

from fastapi_agentrouter import create_agent_router

if TYPE_CHECKING:
    from vertexai.preview.reasoning_engines import AdkApp


# Example 1: Simplest usage - one line integration
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


# Single line integration!
app.include_router(create_agent_router(get_agent))


# Example 2: Custom configuration
app2 = FastAPI()

# Disable specific platforms
app2.include_router(
    create_agent_router(
        get_agent,
        enable_slack=True,
        enable_discord=False,  # Discord disabled
        enable_webhook=True,
    )
)


# Example 3: Custom prefix
app3 = FastAPI()

app3.include_router(
    create_agent_router(
        get_agent,
        prefix="/api/v1/agent",  # Custom prefix
    )
)


# Example 4: With Vertex AI ADK (when available)
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


app4 = FastAPI()
app4.include_router(create_agent_router(get_vertex_agent))


if __name__ == "__main__":
    import uvicorn

    # Run with: python examples/basic_usage.py
    uvicorn.run(app, host="0.0.0.0", port=8000)

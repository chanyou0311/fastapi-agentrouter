"""Basic usage example with FastAPI AgentRouter."""

from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

import fastapi_agentrouter

if TYPE_CHECKING:
    pass


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
app.dependency_overrides[fastapi_agentrouter.get_agent] = get_agent

# Single line integration!
app.include_router(fastapi_agentrouter.router)


if __name__ == "__main__":
    import uvicorn

    # Run with: python examples/basic_usage.py
    uvicorn.run(app, host="0.0.0.0", port=8000)

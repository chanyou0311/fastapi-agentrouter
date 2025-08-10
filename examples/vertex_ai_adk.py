"""Example integration with Vertex AI Agent Development Kit (ADK)."""

from fastapi import FastAPI
from fastapi_agentrouter import get_agent_placeholder, router
from vertexai import Agent
from vertexai.preview import reasoning_engines


def get_weather(city: str) -> dict:
    """Return simple weather information."""
    return {
        "city": city,
        "temperature": 25,
        "condition": "sunny",
    }


agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    description="A helpful weather assistant",
    instruction="You help users with weather information",
    tools=[get_weather],
)


def get_adk_app() -> reasoning_engines.AdkApp:
    """Create the Vertex AI ADK application."""
    return reasoning_engines.AdkApp(agent=agent, enable_tracing=True)


app = FastAPI()

# Two-line integration
app.dependency_overrides[get_agent_placeholder] = get_adk_app
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# Quick Start Guide

This guide will help you integrate your first AI agent with FastAPI in minutes.

## Basic Integration

### Step 1: Create Your Agent

First, create an agent that implements the `stream_query` method:

```python
class SimpleAgent:
    def stream_query(self, *, message: str, **kwargs):
        """Process a message and stream responses."""
        # Your agent logic here
        yield f"Echo: {message}"
```

### Step 2: Integrate with FastAPI

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import router, setup_router

def get_agent():
    return SimpleAgent()

app = FastAPI()

# Add the router with your agent
app.include_router(router, dependencies=[Depends(get_agent)])
setup_router(router, get_agent=get_agent)
```

### Step 3: Test Your Agent

Start your server:

```bash
uvicorn main:app --reload
```

Test the webhook endpoint:

```bash
curl -X POST "http://localhost:8000/agent/webhook" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, agent!"}'
```

## With Vertex AI ADK

### Step 1: Define Your Agent

```python
from vertexai import Agent
from vertexai.preview import reasoning_engines

# Define tools (functions) for your agent
def get_weather(city: str) -> dict:
    """Get weather information for a city."""
    return {
        "city": city,
        "temperature": 25,
        "condition": "sunny"
    }

# Create the agent
agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash-lite",
    description="A helpful weather assistant",
    instruction="You help users with weather information",
    tools=[get_weather]
)
```

### Step 2: Create ADK App and Integrate

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import router, setup_router

def get_adk_app():
    return reasoning_engines.AdkApp(
        agent=agent,
        enable_tracing=True  # Optional: Enable tracing
    )

app = FastAPI()

# Integrate with FastAPI
app.include_router(router, dependencies=[Depends(get_adk_app)])
setup_router(router, get_agent=get_adk_app)
```

### Step 3: Configure Environment

Set up your Google Cloud credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

## Platform Integration

### Slack Integration

1. Set your Slack signing secret:
```bash
export SLACK_SIGNING_SECRET="your-slack-signing-secret"
```

2. Configure your Slack app:
   - Event Subscriptions URL: `https://your-domain.com/agent/slack/events`
   - Slash Commands URL: `https://your-domain.com/agent/slack/events`

3. Your agent is now available in Slack!

### Discord Integration

1. Set your Discord public key:
```bash
export DISCORD_PUBLIC_KEY="your-discord-public-key"
```

2. Configure your Discord app:
   - Interactions Endpoint URL: `https://your-domain.com/agent/discord/interactions`

3. Your agent is now available in Discord!

## Complete Example

Here's a complete example with all features:

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import router, setup_router
from vertexai import Agent
from vertexai.preview import reasoning_engines
import os

# Set environment variables
os.environ["SLACK_SIGNING_SECRET"] = "your-secret"
os.environ["DISCORD_PUBLIC_KEY"] = "your-key"

# Create your agent
def search_web(query: str) -> dict:
    """Search the web for information."""
    return {"results": f"Search results for: {query}"}

agent = Agent(
    name="assistant",
    model="gemini-2.5-flash-lite",
    tools=[search_web]
)

def get_agent():
    return reasoning_engines.AdkApp(agent=agent)

# Create FastAPI app
app = FastAPI(title="My Agent API")

# Add agent router
app.include_router(router, dependencies=[Depends(get_agent)])
setup_router(router, get_agent=get_agent)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Next Steps

- [Configuration Guide](configuration.md) - Detailed configuration options
- [API Reference](../api/core.md) - Complete API documentation
- [Examples](../examples/basic.md) - More examples and use cases

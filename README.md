# FastAPI AgentRouter

[![CI](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml/badge.svg)](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/fastapi-agentrouter.svg)](https://badge.fury.io/py/fastapi-agentrouter)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-agentrouter.svg)](https://pypi.org/project/fastapi-agentrouter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simplified AI Agent integration for FastAPI with multi-platform support (Slack, Discord, Webhook).

## Features

- 🚀 **Simple Integration** - Just 2 lines to add agent to your FastAPI app
- 🤖 **Vertex AI ADK Support** - Native support for Google's Agent Development Kit
- 🔌 **Multi-Platform** - Built-in Slack, Discord, and webhook endpoints
- 🎯 **Protocol-Based** - Works with any agent implementing `stream_query` method
- ⚡ **Async & Streaming** - Full async support with streaming responses
- 🧩 **Dependency Injection** - Leverage FastAPI's DI system

## Installation

```bash
# Basic installation
pip install fastapi-agentrouter

# With platform-specific dependencies
pip install "fastapi-agentrouter[slack]"      # For Slack support
pip install "fastapi-agentrouter[discord]"    # For Discord support  
pip install "fastapi-agentrouter[vertexai]"   # For Vertex AI ADK
pip install "fastapi-agentrouter[all]"        # All platforms
```

## Quick Start

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import router, setup_router

# Your agent implementation (e.g., Vertex AI ADK)
def get_agent():
    # Return your agent instance
    # This could be a Vertex AI AdkApp, or any object with stream_query method
    from vertexai.preview import reasoning_engines
    return reasoning_engines.AdkApp(agent=your_agent)

app = FastAPI()

# Simple integration - just two lines!
app.include_router(router, dependencies=[Depends(get_agent)])
setup_router(router, get_agent=get_agent)
```

That's it! Your agent is now available at:
- `/agent/webhook` - Generic webhook endpoint
- `/agent/slack/events` - Slack events and slash commands
- `/agent/discord/interactions` - Discord interactions

## Advanced Usage

### With Vertex AI Agent Development Kit (ADK)

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import router, setup_router
from vertexai.preview import reasoning_engines
from vertexai import Agent

# Define your agent with tools
def get_weather(city: str) -> dict:
    """Get weather for a city."""
    return {"city": city, "weather": "sunny", "temperature": 25}

agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash-lite",
    description="Weather information agent",
    tools=[get_weather],
)

def get_adk_app():
    return reasoning_engines.AdkApp(
        agent=agent,
        enable_tracing=True,
    )

app = FastAPI()
app.include_router(router, dependencies=[Depends(get_adk_app)])
setup_router(router, get_agent=get_adk_app)
```

### Custom Agent Implementation

```python
class CustomAgent:
    def stream_query(self, *, message: str, user_id=None, session_id=None):
        # Your custom logic here
        yield f"Response to: {message}"

def get_custom_agent():
    return CustomAgent()

app = FastAPI()
app.include_router(router, dependencies=[Depends(get_custom_agent)])
setup_router(router, get_agent=get_custom_agent)
```

### Selective Platform Integration

```python
from fastapi_agentrouter import create_default_router

# Enable only specific platforms
def get_agent():
    return your_agent

# Create router with only webhook and Slack
router = APIRouter(prefix="/agent")
setup_router(
    router, 
    get_agent=get_agent,
    enable_slack=True,
    enable_discord=False,  # Disable Discord
    enable_webhook=True
)

app = FastAPI()
app.include_router(router, dependencies=[Depends(get_agent)])
```

## Configuration

### Environment Variables

Configure platform integrations via environment variables:

```bash
# Slack configuration
export SLACK_SIGNING_SECRET="your-slack-signing-secret"

# Discord configuration  
export DISCORD_PUBLIC_KEY="your-discord-public-key"
```

### Platform Setup

#### Slack Setup

1. Create a Slack App at https://api.slack.com/apps
2. Get your Signing Secret from Basic Information
3. Set environment variable: `SLACK_SIGNING_SECRET`
4. Configure Event Subscriptions URL: `https://your-domain.com/agent/slack/events`
5. Subscribe to events: `message.channels`, `app_mention`, etc.
6. For slash commands, use the same URL

#### Discord Setup

1. Create Discord Application at https://discord.com/developers/applications
2. Get your Public Key from General Information
3. Set environment variable: `DISCORD_PUBLIC_KEY`
4. Set Interactions Endpoint URL: `https://your-domain.com/agent/discord/interactions`

## Agent Protocol

Your agent must implement the `stream_query` method:

```python
class AgentProtocol:
    def stream_query(
        self, 
        *, 
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> Iterator[Any]:
        """Stream responses for a message."""
        ...
```

The method should yield response events. For Vertex AI ADK, events have a `content` attribute.

## API Reference

### Core Functions

#### `setup_router(router, get_agent, enable_slack=True, enable_discord=True, enable_webhook=True)`

Configure a router with agent handlers.

- `router`: FastAPI APIRouter instance
- `get_agent`: Function that returns an agent instance
- `enable_slack`: Enable Slack integration (default: True)
- `enable_discord`: Enable Discord integration (default: True)
- `enable_webhook`: Enable webhook endpoint (default: True)

#### `create_default_router(get_agent) -> APIRouter`

Create a pre-configured router with all integrations enabled.

### Webhook Endpoint

**POST** `/agent/webhook`

Request body:
```json
{
  "message": "Your message here",
  "user_id": "optional-user-id",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "Agent response",
  "session_id": "session-id-if-provided"
}
```

## Examples

See the [examples](examples/) directory for complete examples:
- [basic_usage.py](examples/basic_usage.py) - Basic integration patterns
- More examples coming soon!

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/chanyou0311/fastapi-agentrouter.git
cd fastapi-agentrouter

# Install with uv (recommended)
uv sync --all-extras --dev

# Or with pip
pip install -e ".[all,dev,docs]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_router.py
```

### Build Documentation

```bash
# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Documentation](https://chanyou0311.github.io/fastapi-agentrouter)
- [PyPI Package](https://pypi.org/project/fastapi-agentrouter)
- [GitHub Repository](https://github.com/chanyou0311/fastapi-agentrouter)
- [Issue Tracker](https://github.com/chanyou0311/fastapi-agentrouter/issues)
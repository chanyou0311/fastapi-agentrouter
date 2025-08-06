# FastAPI AgentRouter

[![CI](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml/badge.svg)](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/fastapi-agentrouter.svg)](https://badge.fury.io/py/fastapi-agentrouter)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-agentrouter.svg)](https://pypi.org/project/fastapi-agentrouter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI Agent interface library for FastAPI with multi-platform support.

## Features

- 🚀 **Easy Integration** - Simple API to integrate AI agents with FastAPI
- 🔌 **Multi-Platform Support** - Built-in support for Slack, Discord, and webhooks
- 🎯 **Type Safety** - Full type hints and Pydantic models
- 🔧 **Flexible Configuration** - Easy to configure and extend
- ⚡ **Async Support** - Built on FastAPI's async capabilities
- 🧩 **Dependency Injection** - Leverage FastAPI's DI system

## Installation

```bash
# Basic installation
pip install fastapi-agentrouter

# With Slack support
pip install "fastapi-agentrouter[slack]"

# With Discord support
pip install "fastapi-agentrouter[discord]"

# With all integrations
pip install "fastapi-agentrouter[all]"
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

### Configuration Management

```python
from fastapi_agentrouter.utils import Config, SlackConfig, DiscordConfig

# Load from environment or config file
config = Config(
    prefix="/api/agent",
    slack=SlackConfig(
        signing_secret="your-slack-secret",
        bot_token="xoxb-your-bot-token"  # Optional
    ),
    discord=DiscordConfig(
        public_key="your-discord-public-key",
        application_id="your-app-id",  # Optional
        bot_token="your-bot-token"  # Optional
    ),
    webhook=True
)

# Use with router
app.include_router(
    build_router(agent, **config.to_router_kwargs())
)
```

## Platform-Specific Setup

### Slack Setup

1. Create a Slack App at https://api.slack.com/apps
2. Get your Signing Secret from Basic Information
3. Set up Event Subscriptions URL: `https://your-domain.com/agent/slack/events`
4. Subscribe to required events (e.g., `message.channels`, `app_mention`)
5. Install the app to your workspace

### Discord Setup

1. Create a Discord Application at https://discord.com/developers/applications
2. Get your Public Key from General Information
3. Set Interactions Endpoint URL: `https://your-domain.com/agent/discord/interactions`
4. Add bot to your server with appropriate permissions

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
pytest tests/test_core/
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

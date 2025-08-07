# FastAPI AgentRouter

[![CI](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml/badge.svg)](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/fastapi-agentrouter.svg)](https://badge.fury.io/py/fastapi-agentrouter)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-agentrouter.svg)](https://pypi.org/project/fastapi-agentrouter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simplified AI Agent integration for FastAPI with Slack support.

## Features

- 🚀 **Simple Integration** - Just 2 lines to add agent to your FastAPI app
- 🤖 **Vertex AI ADK Support** - Native support for Google's Agent Development Kit
- 💬 **Slack Integration** - Built-in Slack Bolt integration with lazy listeners
- 🎯 **Protocol-Based** - Works with any agent implementing `stream_query` method
- ⚡ **Async & Streaming** - Full async support with streaming responses
- 🧩 **Dependency Injection** - Leverage FastAPI's DI system
- 📁 **Modular Architecture** - Clean separation of concerns

## Installation

```bash
# Basic installation
pip install fastapi-agentrouter

# With Slack support
pip install "fastapi-agentrouter[slack]"

# With Vertex AI ADK support
pip install "fastapi-agentrouter[vertexai]"

# All extras
pip install "fastapi-agentrouter[all]"
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent_placeholder

# Your agent implementation
class MyAgent:
    def stream_query(self, *, message: str, **kwargs):
        # Process the message and yield responses
        yield f"Response to: {message}"

app = FastAPI()

# Two-line integration!
app.dependency_overrides[get_agent_placeholder] = lambda: MyAgent()
app.include_router(router)
```

That's it! Your agent is now available at:
- `/agent/slack/events` - Handle all Slack events and interactions

## Advanced Usage

### With Vertex AI Agent Development Kit (ADK)

```python
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent_placeholder
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
app.dependency_overrides[get_agent_placeholder] = get_adk_app
app.include_router(router)
```

### Custom Agent Implementation

```python
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent_placeholder

class CustomAgent:
    def stream_query(self, *, message: str, user_id=None, session_id=None, **kwargs):
        # Your custom logic here
        yield f"Response to: {message}"

def get_custom_agent():
    return CustomAgent()

app = FastAPI()
app.dependency_overrides[get_agent_placeholder] = get_custom_agent
app.include_router(router)
```

### Disabling Slack Integration

```python
import os
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent_placeholder

# Disable Slack integration via environment variable
os.environ["DISABLE_SLACK"] = "true"  # Slack endpoints will return 404

app = FastAPI()
app.dependency_overrides[get_agent_placeholder] = lambda: YourAgent()
app.include_router(router)
```

## Configuration

### Environment Variables

Configure Slack integration via environment variables using [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/):

```bash
# Required for Slack integration
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_SIGNING_SECRET="your-signing-secret"

# Optional: Disable Slack integration
export DISABLE_SLACK="true"
```

### Platform Setup

#### Slack Setup

1. Create a Slack App at https://api.slack.com/apps
2. Get your Bot Token and Signing Secret from Basic Information
3. Set environment variables:
   ```bash
   export SLACK_BOT_TOKEN="xoxb-your-bot-token"
   export SLACK_SIGNING_SECRET="your-signing-secret"
   ```
4. Configure Event Subscriptions URL: `https://your-domain.com/agent/slack/events`
5. Subscribe to bot events:
   - `app_mention` - When your bot is mentioned
   - `message.im` - Direct messages to your bot (optional)
6. For interactive components and slash commands, use the same URL: `https://your-domain.com/agent/slack/events`

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

### Core Components

#### `fastapi_agentrouter.router`

Pre-configured APIRouter with Slack integration:
- `/agent/slack/events` - Main Slack event handler

#### `fastapi_agentrouter.get_agent_placeholder`

Dependency placeholder that should be overridden with your agent:
```python
app.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = your_get_agent_function
```

### Environment Variables

The library uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management:

- `SLACK_BOT_TOKEN` - Slack Bot User OAuth Token (required)
- `SLACK_SIGNING_SECRET` - Slack Signing Secret (required)
- `DISABLE_SLACK=true` - Disable Slack endpoints (return 404)

See the [Configuration Guide](https://chanyou0311.github.io/fastapi-agentrouter/getting-started/configuration/) for detailed documentation on all available settings.


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

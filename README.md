# FastAPI AgentRouter

[![CI](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml/badge.svg)](https://github.com/chanyou0311/fastapi-agentrouter/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/fastapi-agentrouter.svg)](https://badge.fury.io/py/fastapi-agentrouter)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-agentrouter.svg)](https://pypi.org/project/fastapi-agentrouter/)
[![Docker Hub](https://img.shields.io/docker/v/chanyou0311/fastapi-agentrouter?label=Docker%20Hub)](https://hub.docker.com/r/chanyou0311/fastapi-agentrouter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simplified AI Agent integration for FastAPI with Slack support.

## Features

- 🚀 **Simple Integration** - Just 2 lines to add agent to your FastAPI app
- 🤖 **Vertex AI Support** - Native support for Google's Vertex AI Agent Builder
- 💬 **Slack Integration** - Built-in Slack Bolt integration
- 🎯 **Protocol-Based** - Works with any agent implementing the `AgentProtocol`
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

### With Vertex AI Agent Builder

```python
from fastapi import FastAPI
import fastapi_agentrouter

app = FastAPI()

# Two-line integration!
app.dependency_overrides[fastapi_agentrouter.get_agent] = (
    fastapi_agentrouter.get_vertex_ai_agent_engine
)
app.include_router(fastapi_agentrouter.router)
```

### With Custom Agent Implementation

```python
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent, AgentProtocol

# Your agent implementation
class MyAgent:
    def create_session(self, *, user_id=None, **kwargs):
        return {"id": "session-123"}

    def list_sessions(self, *, user_id=None, **kwargs):
        return {"sessions": []}

    def stream_query(self, *, message: str, user_id=None, session_id=None, **kwargs):
        # Process the message and yield responses
        yield {"content": f"Response to: {message}"}

app = FastAPI()

# Two-line integration!
app.dependency_overrides[get_agent] = lambda: MyAgent()
app.include_router(router)
```

That's it! Your agent is now available at:
- `/agent/slack/events` - Handle all Slack events and interactions (when Slack is configured)

## Configuration

### Vertex AI Configuration

When using Vertex AI Agent Builder, configure these environment variables:

```bash
# Required for Vertex AI
export VERTEXAI__PROJECT_ID="your-project-id"
export VERTEXAI__LOCATION="us-central1"
export VERTEXAI__STAGING_BUCKET="your-staging-bucket"
export VERTEXAI__AGENT_NAME="your-agent-name"
```

The library automatically warms up the agent engine during router initialization to ensure fast response times.

### Slack Configuration

To enable Slack integration, set these environment variables:

```bash
# Required for Slack integration
export SLACK__BOT_TOKEN="xoxb-your-bot-token"
export SLACK__SIGNING_SECRET="your-signing-secret"
```

Note: Slack integration is only enabled when both `SLACK__BOT_TOKEN` and `SLACK__SIGNING_SECRET` are configured. If not set, Slack endpoints will return 404.

### Slack Setup

1. Create a Slack App at https://api.slack.com/apps
2. Get your Bot Token and Signing Secret from Basic Information
3. Set environment variables:
   ```bash
   export SLACK__BOT_TOKEN="xoxb-your-bot-token"
   export SLACK__SIGNING_SECRET="your-signing-secret"
   ```
4. Configure Event Subscriptions URL: `https://your-domain.com/agent/slack/events`
5. Subscribe to bot events:
   - `app_mention` - When your bot is mentioned
   - `message.im` - Direct messages to your bot (optional)
6. For interactive components and slash commands, use the same URL: `https://your-domain.com/agent/slack/events`

## Agent Protocol

Your agent must implement the `AgentProtocol` interface with these methods:

```python
from typing import Any, Generator

class AgentProtocol:
    def create_session(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new session for the agent.

        Returns a dictionary containing at least the session 'id'.
        """
        ...

    def list_sessions(
        self,
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List sessions for a given user.

        Returns a dictionary with a 'sessions' key containing a list of
        session dictionaries.
        """
        ...

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any
    ) -> Generator[dict[str, Any], Any, None]:
        """Stream responses from the agent."""
        ...
```

The `stream_query` method should yield response events as dictionaries.

## API Reference

### Core Components

#### `fastapi_agentrouter.router`

Pre-configured APIRouter with automatic agent integration:
- `/agent/slack/events` - Slack event handler (when Slack is configured)

#### `fastapi_agentrouter.get_agent`

Dependency function that should be overridden with your agent:
```python
app.dependency_overrides[fastapi_agentrouter.get_agent] = your_get_agent_function
```

#### `fastapi_agentrouter.get_vertex_ai_agent_engine`

Pre-configured function to get Vertex AI Agent Engine:
```python
app.dependency_overrides[fastapi_agentrouter.get_agent] = (
    fastapi_agentrouter.get_vertex_ai_agent_engine
)
```

#### `fastapi_agentrouter.AgentProtocol`

Protocol class that defines the interface for agents.

#### `fastapi_agentrouter.Settings`

Pydantic settings class for configuration management.

### Environment Variables

The library uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management:

**Slack Configuration:**
- `SLACK__BOT_TOKEN` - Slack Bot User OAuth Token
- `SLACK__SIGNING_SECRET` - Slack Signing Secret

**Vertex AI Configuration:**
- `VERTEXAI__PROJECT_ID` - GCP Project ID
- `VERTEXAI__LOCATION` - GCP Location (e.g., us-central1)
- `VERTEXAI__STAGING_BUCKET` - GCS Bucket for staging
- `VERTEXAI__AGENT_NAME` - Display name of the Vertex AI Agent

## Examples

See the [examples](examples/) directory for complete examples:
- [basic_usage.py](examples/basic_usage.py) - Basic Vertex AI integration example

## Docker

Docker images are available on [Docker Hub](https://hub.docker.com/r/chanyou0311/fastapi-agentrouter):

```bash
# Pull the latest image
docker pull chanyou0311/fastapi-agentrouter:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e VERTEXAI__PROJECT_ID=your-project-id \
  -e VERTEXAI__LOCATION=us-central1 \
  -e VERTEXAI__STAGING_BUCKET=your-bucket \
  -e VERTEXAI__AGENT_NAME=your-agent-name \
  chanyou0311/fastapi-agentrouter:latest
```

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
- [Docker Hub](https://hub.docker.com/r/chanyou0311/fastapi-agentrouter)
- [GitHub Repository](https://github.com/chanyou0311/fastapi-agentrouter)
- [Issue Tracker](https://github.com/chanyou0311/fastapi-agentrouter/issues)

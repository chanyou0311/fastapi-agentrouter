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
from fastapi import FastAPI
from fastapi_agentrouter import Agent, AgentResponse, build_router
from typing import Any, Dict

class MyAgent(Agent):
    async def handle_slack(self, event: Dict[str, Any]) -> str:
        # Handle Slack events
        return f"Hello from Slack! Event: {event.get('text', '')}"

    async def handle_discord(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        # Handle Discord interactions
        return {
            "type": 4,
            "data": {"content": "Hello from Discord!"}
        }

    async def handle_webhook(self, data: Dict[str, Any]) -> AgentResponse:
        # Handle generic webhooks
        return AgentResponse(content="Hello from webhook!")

# Create FastAPI app
app = FastAPI()

# Create your agent
agent = MyAgent()

# Add agent router to your app
app.include_router(
    build_router(
        agent,
        slack={"signing_secret": "your-slack-secret"},
        discord={"public_key": "your-discord-public-key"}
    )
)
```

## Advanced Usage

### Using Dependency Injection

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import Agent, AgentResponse, build_router
from typing import Any, Dict

# Your AI service
class AIService:
    async def process(self, text: str) -> str:
        # Your AI logic here
        return f"Processed: {text}"

# Dependency provider
async def get_ai_service() -> AIService:
    return AIService()

class SmartAgent(Agent):
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def handle_slack(self, event: Dict[str, Any]) -> str:
        text = event.get("text", "")
        return await self.ai_service.process(text)

    async def handle_discord(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        content = interaction.get("data", {}).get("options", [{}])[0].get("value", "")
        result = await self.ai_service.process(content)
        return {
            "type": 4,
            "data": {"content": result}
        }

    async def handle_webhook(self, data: Dict[str, Any]) -> AgentResponse:
        text = data.get("message", "")
        result = await self.ai_service.process(text)
        return AgentResponse(content=result)

# Factory function with DI
async def create_agent(ai_service: AIService = Depends(get_ai_service)) -> SmartAgent:
    return SmartAgent(ai_service)

app = FastAPI()

# Use factory pattern with DI
@app.on_event("startup")
async def startup():
    ai_service = await get_ai_service()
    agent = SmartAgent(ai_service)

    app.include_router(
        build_router(
            agent,
            slack={"signing_secret": "your-slack-secret"},
            discord={"public_key": "your-discord-public-key"}
        )
    )
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

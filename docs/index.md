# FastAPI AgentRouter

AI Agent interface library for FastAPI with multi-platform support.

## Features

- 🚀 **Easy Integration** - Simple API to integrate AI agents with FastAPI
- 🔌 **Multi-Platform Support** - Built-in support for Slack, Discord, and webhooks
- 🎯 **Type Safety** - Full type hints and Pydantic models
- 🔧 **Flexible Configuration** - Easy to configure and extend
- ⚡ **Async Support** - Built on FastAPI's async capabilities
- 🧩 **Dependency Injection** - Leverage FastAPI's DI system

## Quick Start

```python
from fastapi import FastAPI
from fastapi_agentrouter import Agent, AgentResponse, build_router
from typing import Any, Dict

class MyAgent(Agent):
    async def handle_slack(self, event: Dict[str, Any]) -> str:
        return f"Hello from Slack! Event: {event.get('text', '')}"
    
    async def handle_discord(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": 4,
            "data": {"content": "Hello from Discord!"}
        }
    
    async def handle_webhook(self, data: Dict[str, Any]) -> AgentResponse:
        return AgentResponse(content="Hello from webhook!")

app = FastAPI()
agent = MyAgent()

app.include_router(
    build_router(
        agent,
        slack={"signing_secret": "your-slack-secret"},
        discord={"public_key": "your-discord-public-key"}
    )
)
```

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

## License

MIT License - see [LICENSE](https://github.com/chanyou0311/fastapi-agentrouter/blob/main/LICENSE) for details.
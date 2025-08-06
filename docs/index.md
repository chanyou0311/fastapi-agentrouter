# FastAPI AgentRouter

Simplified AI Agent integration for FastAPI with multi-platform support.

## Overview

FastAPI AgentRouter makes it incredibly easy to integrate AI agents into your FastAPI applications. With just 2 lines of code, you can expose your agent through multiple platforms including Slack, Discord, and webhooks.

## Key Features

- 🚀 **Simple Integration** - Just 2 lines to add agent to your FastAPI app
- 🤖 **Vertex AI ADK Support** - Native support for Google's Agent Development Kit
- 🔌 **Multi-Platform** - Built-in Slack, Discord, and webhook endpoints
- 🎯 **Protocol-Based** - Works with any agent implementing `stream_query` method
- ⚡ **Async & Streaming** - Full async support with streaming responses
- 🧩 **Dependency Injection** - Leverage FastAPI's DI system

## Quick Example

```python
from fastapi import FastAPI, Depends
from fastapi_agentrouter import router, setup_router

def get_agent():
    # Return your agent (e.g., Vertex AI AdkApp)
    return your_agent

app = FastAPI()

# That's it! Just two lines
app.include_router(router, dependencies=[Depends(get_agent)])
setup_router(router, get_agent=get_agent)
```

Your agent is now available at:
- `/agent/webhook` - Generic webhook endpoint
- `/agent/slack/events` - Slack events and slash commands
- `/agent/discord/interactions` - Discord interactions

## Why FastAPI AgentRouter?

### Problem
Integrating AI agents with different platforms (Slack, Discord, etc.) requires:
- Understanding each platform's authentication and verification
- Handling different message formats
- Managing streaming responses
- Setting up multiple endpoints

### Solution
FastAPI AgentRouter handles all the platform-specific complexity for you. You just provide your agent, and we handle the rest.

## Installation

```bash
pip install fastapi-agentrouter

# With specific platforms
pip install "fastapi-agentrouter[slack]"
pip install "fastapi-agentrouter[discord]"
pip install "fastapi-agentrouter[vertexai]"
pip install "fastapi-agentrouter[all]"
```

## Next Steps

- [Getting Started](getting-started/installation.md) - Installation and setup
- [Quick Start Guide](getting-started/quickstart.md) - Your first agent integration
- [API Reference](api/core.md) - Detailed API documentation
- [Examples](examples/basic.md) - Complete examples
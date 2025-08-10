# 基本的なサンプル

## Vertex AI ADKとの統合

FastAPI AgentRouterを使ってVertex AI Agent Development Kit (ADK) のエージェントを統合する例です。

```python
from fastapi import FastAPI
from fastapi_agentrouter import get_agent_placeholder, router
from vertexai import Agent
from vertexai.preview import reasoning_engines


def get_weather(city: str) -> dict:
    """天気情報を返すサンプルツール。"""
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
    """Vertex AI ADKアプリケーションを作成。"""
    return reasoning_engines.AdkApp(agent=agent, enable_tracing=True)


app = FastAPI()
app.dependency_overrides[get_agent_placeholder] = get_adk_app
app.include_router(router)
```

"""Test configuration and fixtures."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Any, Dict
from unittest.mock import AsyncMock

from fastapi_agentrouter import Agent, AgentResponse, build_router


class MockAgent(Agent):
    """Mock agent for testing."""
    
    def __init__(self) -> None:
        self.handle_slack_mock = AsyncMock(return_value="Mock Slack response")
        self.handle_discord_mock = AsyncMock(
            return_value={"type": 4, "data": {"content": "Mock Discord response"}}
        )
        self.handle_webhook_mock = AsyncMock(
            return_value=AgentResponse(content="Mock webhook response")
        )
    
    async def handle_slack(self, event: Dict[str, Any]) -> str:
        return await self.handle_slack_mock(event)
    
    async def handle_discord(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        return await self.handle_discord_mock(interaction)
    
    async def handle_webhook(self, data: Dict[str, Any]) -> AgentResponse:
        return await self.handle_webhook_mock(data)


@pytest.fixture
def mock_agent() -> MockAgent:
    """Provide a mock agent for testing."""
    return MockAgent()


@pytest.fixture
def test_app(mock_agent: MockAgent) -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()
    app.include_router(
        build_router(
            mock_agent,
            slack={"signing_secret": "test_secret"},
            discord={"public_key": "0000000000000000000000000000000000000000000000000000000000000000"},
            webhook=True,
        )
    )
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(test_app)


@pytest.fixture
def slack_signing_secret() -> str:
    """Test Slack signing secret."""
    return "test_secret"


@pytest.fixture
def discord_public_key() -> str:
    """Test Discord public key (64 hex chars)."""
    return "0000000000000000000000000000000000000000000000000000000000000000"
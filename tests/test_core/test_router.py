"""Tests for the router builder."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter import build_router
from tests.conftest import MockAgent


class TestRouterBuilder:
    """Test the build_router function."""
    
    def test_build_router_with_all_integrations(self, mock_agent: MockAgent) -> None:
        """Test building router with all integrations enabled."""
        router = build_router(
            mock_agent,
            prefix="/api",
            slack={"signing_secret": "secret"},
            discord={"public_key": "0" * 64},
            webhook=True
        )
        
        assert router.prefix == "/api"
        assert len(router.routes) == 3  # slack, discord, webhook
    
    def test_build_router_webhook_only(self, mock_agent: MockAgent) -> None:
        """Test building router with only webhook enabled."""
        router = build_router(mock_agent, webhook=True)
        
        assert router.prefix == "/agent"
        assert len(router.routes) == 1  # webhook only
    
    def test_build_router_no_integrations(self, mock_agent: MockAgent) -> None:
        """Test building router with no integrations."""
        router = build_router(
            mock_agent,
            slack=None,
            discord=None,
            webhook=False
        )
        
        assert len(router.routes) == 0
    
    def test_webhook_endpoint(self, test_client: TestClient) -> None:
        """Test the webhook endpoint."""
        response = test_client.post(
            "/agent/webhook",
            json={"message": "test"}
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "content": "Mock webhook response",
            "metadata": None
        }
    
    @pytest.mark.asyncio
    async def test_webhook_handler_error(
        self, mock_agent: MockAgent, test_client: TestClient
    ) -> None:
        """Test webhook handler error handling."""
        mock_agent.handle_webhook_mock.side_effect = Exception("Test error")
        
        response = test_client.post(
            "/agent/webhook",
            json={"message": "test"}
        )
        
        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]
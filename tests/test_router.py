"""Tests for the router module."""

from fastapi import APIRouter
from fastapi.testclient import TestClient

from fastapi_agentrouter import create_default_router, setup_router


def test_webhook_endpoint(test_client: TestClient):
    """Test the webhook endpoint."""
    response = test_client.post(
        "/agent/webhook",
        json={"message": "Hello agent", "user_id": "test_user"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Response to: Hello agent" in data["response"]


def test_webhook_missing_message(test_client: TestClient):
    """Test webhook with missing message."""
    response = test_client.post("/agent/webhook", json={})

    assert response.status_code == 400
    assert "Message is required" in response.json()["detail"]


def test_create_default_router(mock_agent):
    """Test creating default router."""

    def get_agent():
        return mock_agent

    router = create_default_router(get_agent)

    assert isinstance(router, APIRouter)
    assert router.prefix == "/agent"
    # Check that routes are added
    assert len(router.routes) > 0


def test_setup_router_selective(mock_agent):
    """Test setup router with selective integrations."""
    from fastapi import APIRouter

    def get_agent():
        return mock_agent

    router = APIRouter(prefix="/test")

    # Only enable webhook
    setup_router(
        router,
        get_agent=get_agent,
        enable_slack=False,
        enable_discord=False,
        enable_webhook=True,
    )

    # Should have only webhook route
    route_paths = [route.path for route in router.routes]
    assert "/test/webhook" in route_paths
    assert "/test/slack/events" not in route_paths
    assert "/test/discord/interactions" not in route_paths

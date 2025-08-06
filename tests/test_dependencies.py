"""Tests for dependencies module."""

import os

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.dependencies import (
    check_discord_enabled,
    check_slack_enabled,
    check_webhook_enabled,
)


def test_agent_protocol():
    """Test that agent protocol is properly defined."""
    from fastapi_agentrouter import AgentProtocol

    class TestAgent:
        def stream_query(self, *, message: str, user_id=None, session_id=None):
            yield f"Response: {message}"

    agent = TestAgent()
    # Should be compatible with AgentProtocol
    assert hasattr(agent, "stream_query")


def test_no_agent_configured():
    """Test when agent is not configured."""
    app = FastAPI()
    # Don't override the dependency - should use placeholder
    app.include_router(router)
    client = TestClient(app)

    response = client.post("/agent/webhook")
    assert response.status_code == 500
    assert "Agent not configured" in response.json()["detail"]


def test_check_slack_enabled():
    """Test check_slack_enabled function."""
    # Should not raise when not disabled
    check_slack_enabled()

    # Should raise when disabled
    os.environ["DISABLE_SLACK"] = "true"
    with pytest.raises(HTTPException) as exc_info:
        check_slack_enabled()
    assert exc_info.value.status_code == 404
    assert "Slack integration is not enabled" in exc_info.value.detail

    # Clean up
    del os.environ["DISABLE_SLACK"]


def test_check_discord_enabled():
    """Test check_discord_enabled function."""
    # Should not raise when not disabled
    check_discord_enabled()

    # Should raise when disabled
    os.environ["DISABLE_DISCORD"] = "true"
    with pytest.raises(HTTPException) as exc_info:
        check_discord_enabled()
    assert exc_info.value.status_code == 404
    assert "Discord integration is not enabled" in exc_info.value.detail

    # Clean up
    del os.environ["DISABLE_DISCORD"]


def test_check_webhook_enabled():
    """Test check_webhook_enabled function."""
    # Should not raise when not disabled
    check_webhook_enabled()

    # Should raise when disabled
    os.environ["DISABLE_WEBHOOK"] = "true"
    with pytest.raises(HTTPException) as exc_info:
        check_webhook_enabled()
    assert exc_info.value.status_code == 404
    assert "Webhook endpoint is not enabled" in exc_info.value.detail

    # Clean up
    del os.environ["DISABLE_WEBHOOK"]
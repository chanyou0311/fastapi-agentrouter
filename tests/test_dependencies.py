"""Tests for dependencies module."""

import pytest
from fastapi import HTTPException

from fastapi_agentrouter.core.settings import Settings
from fastapi_agentrouter.integrations.slack.dependencies import check_slack_enabled


def test_agent_protocol():
    """Test that agent protocol is properly defined."""

    class TestAgent:
        def stream_query(self, *, message: str, user_id=None, session_id=None):
            yield f"Response: {message}"

    agent = TestAgent()
    # Should be compatible with AgentProtocol
    assert hasattr(agent, "stream_query")


def test_check_slack_enabled():
    """Test check_slack_enabled function."""
    # Should raise when disabled (default)
    settings = Settings()
    with pytest.raises(HTTPException) as exc_info:
        check_slack_enabled(settings)
    assert exc_info.value.status_code == 404
    assert "Slack integration is not enabled" in exc_info.value.detail

    # Should not raise when enabled
    settings = Settings(enable_slack=True)
    check_slack_enabled(settings)  # Should not raise

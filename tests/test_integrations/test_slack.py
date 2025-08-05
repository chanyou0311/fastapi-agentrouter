"""Tests for Slack integration."""

import hashlib
import hmac
import json
import time
from typing import Dict, Any
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from fastapi_agentrouter.integrations.slack import verify_slack_signature
from tests.conftest import MockAgent


def generate_slack_signature(
    signing_secret: str, timestamp: str, body: str
) -> str:
    """Generate a valid Slack signature for testing."""
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = (
        "v0="
        + hmac.new(
            signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )
    return signature


class TestSlackIntegration:
    """Test Slack integration functionality."""
    
    def test_verify_slack_signature_valid(self, slack_signing_secret: str) -> None:
        """Test valid Slack signature verification."""
        timestamp = str(int(time.time()))
        body = '{"text": "test"}'
        signature = generate_slack_signature(slack_signing_secret, timestamp, body)
        
        assert verify_slack_signature(
            slack_signing_secret,
            body.encode(),
            timestamp,
            signature
        )
    
    def test_verify_slack_signature_invalid(self, slack_signing_secret: str) -> None:
        """Test invalid Slack signature verification."""
        timestamp = str(int(time.time()))
        body = '{"text": "test"}'
        
        assert not verify_slack_signature(
            slack_signing_secret,
            body.encode(),
            timestamp,
            "v0=invalid_signature"
        )
    
    def test_verify_slack_signature_expired(self, slack_signing_secret: str) -> None:
        """Test expired Slack signature verification."""
        old_timestamp = str(int(time.time()) - 600)  # 10 minutes ago
        body = '{"text": "test"}'
        signature = generate_slack_signature(slack_signing_secret, old_timestamp, body)
        
        assert not verify_slack_signature(
            slack_signing_secret,
            body.encode(),
            old_timestamp,
            signature
        )
    
    def test_slack_url_verification(
        self, test_client: TestClient, slack_signing_secret: str
    ) -> None:
        """Test Slack URL verification challenge."""
        timestamp = str(int(time.time()))
        body = json.dumps({
            "type": "url_verification",
            "challenge": "test_challenge_string"
        })
        signature = generate_slack_signature(slack_signing_secret, timestamp, body)
        
        response = test_client.post(
            "/agent/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": signature,
                "Content-Type": "application/json",
            }
        )
        
        assert response.status_code == 200
        assert response.text == "test_challenge_string"
    
    def test_slack_event_handling(
        self, test_client: TestClient, slack_signing_secret: str
    ) -> None:
        """Test Slack event handling."""
        timestamp = str(int(time.time()))
        body = json.dumps({
            "type": "event_callback",
            "event": {
                "type": "message",
                "text": "Hello bot"
            }
        })
        signature = generate_slack_signature(slack_signing_secret, timestamp, body)
        
        response = test_client.post(
            "/agent/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": signature,
                "Content-Type": "application/json",
            }
        )
        
        assert response.status_code == 200
        assert response.text == "Mock Slack response"
    
    def test_slack_slash_command(
        self, test_client: TestClient, slack_signing_secret: str
    ) -> None:
        """Test Slack slash command handling."""
        timestamp = str(int(time.time()))
        body_dict = {
            "command": "/test",
            "text": "test command",
            "user_id": "U123456",
        }
        body = urlencode(body_dict)
        signature = generate_slack_signature(slack_signing_secret, timestamp, body)
        
        response = test_client.post(
            "/agent/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": signature,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        
        assert response.status_code == 200
        assert response.text == "Mock Slack response"
    
    def test_slack_invalid_signature(self, test_client: TestClient) -> None:
        """Test Slack request with invalid signature."""
        response = test_client.post(
            "/agent/slack/events",
            json={"text": "test"},
            headers={
                "X-Slack-Request-Timestamp": str(int(time.time())),
                "X-Slack-Signature": "v0=invalid",
            }
        )
        
        assert response.status_code == 400
        assert "Invalid request signature" in response.json()["detail"]
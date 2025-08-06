"""Tests for Slack integration."""

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

from fastapi.testclient import TestClient


def generate_slack_signature(signing_secret: str, timestamp: str, body: str) -> str:
    """Generate a valid Slack signature for testing."""
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = (
        "v0="
        + hmac.new(
            signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )
    return signature


def test_slack_url_verification(test_client: TestClient, slack_signing_secret: str):
    """Test Slack URL verification challenge."""
    timestamp = str(int(time.time()))
    body = json.dumps(
        {"type": "url_verification", "challenge": "test_challenge_string"}
    )
    signature = generate_slack_signature(slack_signing_secret, timestamp, body)

    response = test_client.post(
        "/agent/slack/events",
        content=body,
        headers={
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": signature,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.text == "test_challenge_string"


def test_slack_event_handling(test_client: TestClient, slack_signing_secret: str):
    """Test Slack event handling."""
    timestamp = str(int(time.time()))
    body = json.dumps(
        {
            "type": "event_callback",
            "event": {"type": "message", "text": "Hello bot", "user": "U123"},
        }
    )
    signature = generate_slack_signature(slack_signing_secret, timestamp, body)

    response = test_client.post(
        "/agent/slack/events",
        content=body,
        headers={
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": signature,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert "Response to: Hello bot" in response.text


def test_slack_slash_command(test_client: TestClient, slack_signing_secret: str):
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
        },
    )

    assert response.status_code == 200
    assert "Response to: test command" in response.text


def test_slack_invalid_signature(test_client: TestClient):
    """Test Slack request with invalid signature."""
    import os

    os.environ["SLACK_SIGNING_SECRET"] = "test_secret"

    response = test_client.post(
        "/agent/slack/events",
        json={"text": "test"},
        headers={
            "X-Slack-Request-Timestamp": str(int(time.time())),
            "X-Slack-Signature": "v0=invalid",
        },
    )

    assert response.status_code == 400
    assert "Invalid request signature" in response.json()["detail"]

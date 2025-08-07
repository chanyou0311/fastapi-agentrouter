# Slack Integration

FastAPI AgentRouter provides full-featured Slack integration using [Slack Bolt for Python](https://tools.slack.dev/bolt-python/), enabling your AI agent to interact with Slack workspaces through various event types.

## Features

- **App mentions** - Respond when your bot is mentioned
- **Direct messages** - Handle DMs to your bot
- **Slash commands** - Support custom slash commands
- **Interactive components** - Handle button clicks and select menus
- **OAuth flow** - Built-in OAuth installation support
- **Thread support** - Maintain conversation context in threads
- **Lazy listeners** - Optimized for serverless environments

## Installation

Install with the Slack extra:

```bash
pip install fastapi-agentrouter[slack]
```

## Prerequisites

1. **Create a Slack App**
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App" → "From scratch"
   - Name your app and select a workspace

2. **Configure OAuth & Permissions**
   - Add the following Bot Token Scopes:
     - `app_mentions:read` - Read messages that mention your app
     - `chat:write` - Send messages as your app
     - `im:history` - Read direct messages
     - `channels:history` - Read public channel messages (if needed)
   - Install the app to your workspace
   - Copy the **Bot User OAuth Token** (starts with `xoxb-`)

3. **Configure Event Subscriptions**
   - Enable Events
   - Set Request URL: `https://your-domain.com/agent/slack/events`
   - Subscribe to bot events:
     - `app_mention` - When your app is mentioned
     - `message.im` - Direct messages to your app
   - Save changes

4. **Get Signing Secret**
   - Go to Basic Information
   - Copy the **Signing Secret**

## Configuration

Set the required environment variables:

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_SIGNING_SECRET="your-signing-secret"
```

## Basic Usage

```python
from fastapi import FastAPI
from fastapi_agentrouter import router, get_agent_placeholder

# Your agent implementation
class MyAgent:
    def stream_query(self, *, message: str, **kwargs):
        # Process the message and yield responses
        yield f"You said: {message}"

# Create FastAPI app
app = FastAPI()

# Configure agent dependency
app.dependency_overrides[get_agent_placeholder] = lambda: MyAgent()

# Include the router
app.include_router(router)
```

## Endpoints

The Slack integration provides the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/slack/` | GET | Status check endpoint |
| `/agent/slack/events` | POST | Main event handler for Slack events |
| `/agent/slack/interactions` | POST | Handle interactive components |
| `/agent/slack/commands` | POST | Handle slash commands |
| `/agent/slack/install` | GET | OAuth installation flow |
| `/agent/slack/oauth_redirect` | GET | OAuth redirect handler |

## Event Handling

### App Mentions

When your bot is mentioned in a channel:

```python
# User: @YourBot help me with something

# Your agent receives:
# message: "@YourBot help me with something"
# user_id: "U123456"
# session_id: "slack_C789_1234567890.123456"
# platform: "slack"
# channel: "C789"
# thread_ts: "1234567890.123456"
```

### Direct Messages

When users send direct messages to your bot:

```python
# The bot automatically responds to DMs
# No mention required in direct message channels
```

## Agent Context

The agent receives additional Slack-specific context in the `stream_query` kwargs:

- `platform`: Always "slack"
- `channel`: Slack channel ID
- `thread_ts`: Thread timestamp for maintaining conversation context
- `user_id`: Slack user ID
- `session_id`: Unique session identifier combining channel and thread

## Response Handling

The integration supports various response formats from your agent:

### Simple String Response

```python
def stream_query(self, **kwargs):
    yield "Simple text response"
```

### Structured Response

```python
def stream_query(self, **kwargs):
    yield {
        "content": {
            "parts": [
                {"text": "Part 1 of response"},
                {"text": "Part 2 of response"}
            ]
        }
    }
```

### Streaming Response

```python
def stream_query(self, **kwargs):
    for word in ["Hello", " ", "from", " ", "agent"]:
        yield word
```

## Thread Support

The integration automatically maintains thread context:

1. Responses are sent to the same thread where the mention occurred
2. Thread timestamp is included in the session ID for context persistence
3. Your agent can use the session ID to maintain conversation state

## Serverless Deployment

The integration is optimized for serverless environments using lazy listeners:

- Acknowledges Slack events within 3 seconds
- Processes responses asynchronously
- Suitable for AWS Lambda, Google Cloud Run, etc.

## Error Handling

Errors are gracefully handled and reported to users:

- Missing environment variables return clear error messages
- Agent errors are caught and reported to Slack
- Import errors suggest installation instructions

## Disabling Slack

To disable Slack endpoints (returns 404):

```bash
export DISABLE_SLACK=true
```

## Testing Your Integration

1. **URL Verification**
   ```bash
   curl -X POST http://localhost:8000/agent/slack/events \
     -H "Content-Type: application/json" \
     -d '{"type": "url_verification", "challenge": "test_challenge"}'
   ```

2. **Test in Slack**
   - Mention your bot: `@YourBot hello`
   - Send a direct message to your bot
   - Use a slash command (if configured)

## Security Considerations

- **Signing Secret**: Always verify requests using the signing secret
- **Token Storage**: Never commit tokens to version control
- **HTTPS**: Always use HTTPS in production
- **Scopes**: Only request necessary OAuth scopes

## Troubleshooting

### Bot not responding

1. Check environment variables are set correctly
2. Verify Event Subscriptions URL is verified in Slack
3. Check your app has been installed to the workspace
4. Review bot token scopes

### 500 Error: Missing slack-bolt

Install the Slack dependencies:
```bash
pip install fastapi-agentrouter[slack]
```

### Request URL verification failing

Ensure your app is running and accessible at the public URL you provided to Slack.

## Advanced Configuration

### Custom Session Management

```python
class MyAgent:
    def stream_query(self, *, session_id: str, **kwargs):
        # Use session_id to maintain conversation state
        # Format: "slack_{channel}_{thread_ts}"
        channel = session_id.split("_")[1]
        thread = session_id.split("_")[2]
        # Implement your session logic
        ...
```

### Platform-Specific Logic

```python
class MyAgent:
    def stream_query(self, *, platform: str, **kwargs):
        if platform == "slack":
            # Slack-specific formatting
            yield "*Bold text* and _italic text_"
        else:
            # Generic response
            yield "Bold text and italic text"
```

## Related Documentation

- [Slack Bolt for Python](https://tools.slack.dev/bolt-python/)
- [Slack API Documentation](https://api.slack.com/)
- [Slack Events API](https://api.slack.com/events-api)
- [Slack OAuth](https://api.slack.com/authentication/oauth-v2)

# Configuration

FastAPI AgentRouter uses environment variables for configuration. All settings are optional and have sensible defaults, so the library works out of the box without any configuration.

## Environment Variables

The library uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management. You can set these variables in your environment or in a `.env` file in your project root.

### Platform Controls

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DISABLE_SLACK` | bool | `false` | Disable Slack integration endpoints. When set to `true`, all Slack endpoints will return 404. |
| `DISABLE_DISCORD` | bool | `false` | Disable Discord integration endpoints. When set to `true`, all Discord endpoints will return 404. |
| `DISABLE_WEBHOOK` | bool | `false` | Disable webhook endpoints. When set to `true`, all webhook endpoints will return 404. |

## Configuration Examples

### Using Environment Variables

```bash
# Disable specific integrations
export DISABLE_SLACK=true
export DISABLE_DISCORD=true

# Run your application
python main.py
```

### Using .env File

Create a `.env` file in your project root:

```env
# Disable specific integrations
DISABLE_SLACK=true
DISABLE_DISCORD=false
DISABLE_WEBHOOK=false
```

The settings will be automatically loaded when your application starts.

### Programmatic Configuration

You can also access and modify settings programmatically:

```python
from fastapi_agentrouter.core.settings import settings

# Check current settings
print(f"Slack disabled: {settings.disable_slack}")
print(f"Discord disabled: {settings.disable_discord}")
print(f"Webhook disabled: {settings.disable_webhook}")

# Settings are read-only after initialization
# To override, use environment variables or .env file
```

## Default Behavior

By default, all integrations are **enabled**:
- Slack endpoints are available at `/agent/slack/*`
- Discord endpoints are available at `/agent/discord/*`
- Webhook endpoints are available at `/agent/webhook/*`

When an integration is disabled:
- The corresponding endpoints return HTTP 404
- The error message indicates that the integration is not enabled
- No agent processing occurs for that platform

## Testing with Different Configurations

For testing, you can use pytest's `monkeypatch` to override settings:

```python
def test_with_slack_disabled(monkeypatch):
    from fastapi_agentrouter.core.settings import settings

    # Temporarily disable Slack for this test
    monkeypatch.setattr(settings, "disable_slack", True)

    # Your test code here
    response = client.get("/agent/slack/")
    assert response.status_code == 404
```

## Boolean Value Parsing

The library uses pydantic's boolean parsing, which accepts various representations:
- True values: `true`, `True`, `TRUE`, `1`, `yes`, `Yes`, `YES`, `on`, `On`, `ON`
- False values: `false`, `False`, `FALSE`, `0`, `no`, `No`, `NO`, `off`, `Off`, `OFF`
- Any other value will raise a validation error

## Future Configuration Options

Additional configuration options may be added in future versions for:
- Authentication settings
- Rate limiting
- Logging levels
- Custom endpoint paths
- Timeout settings

Check the [changelog](../changelog.md) for updates on new configuration options.

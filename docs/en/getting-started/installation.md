# Installation

## Requirements

- Python 3.10 or higher
- FastAPI 0.100.0 or higher

## Basic Installation

Install the core package:

```bash
pip install fastapi-agentrouter
```

This includes the core functionality and FastAPI dependencies.

## Platform-Specific Installation

### For Slack Integration

```bash
pip install "fastapi-agentrouter[slack]"
```

This installs:
- `slack-bolt` for Slack app functionality

### For Discord Integration

```bash
pip install "fastapi-agentrouter[discord]"
```

This installs:
- `PyNaCl` for Discord signature verification

### For Vertex AI ADK

```bash
pip install "fastapi-agentrouter[vertexai]"
```

This installs:
- `google-cloud-aiplatform` with ADK support

### All Platforms

```bash
pip install "fastapi-agentrouter[all]"
```

Installs all optional dependencies.

## Development Installation

For development and testing:

```bash
# Clone the repository
git clone https://github.com/chanyou0311/fastapi-agentrouter.git
cd fastapi-agentrouter

# Using uv (recommended)
uv sync --all-extras --dev

# Or using pip
pip install -e ".[all,dev,docs]"
```

## Verify Installation

```python
import fastapi_agentrouter
print(fastapi_agentrouter.__version__)
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Create your first agent integration
- [Configuration](configuration.md) - Configure platform integrations

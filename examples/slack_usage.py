"""
Slack integration example with FastAPI AgentRouter.

This example demonstrates how to use fastapi-agentrouter with Slack Bot.
It provides a complete, working FastAPI server that can handle Slack events.

Requirements:
    - Install with Slack support: pip install fastapi-agentrouter[slack]
    - Set environment variables:
        - SLACK_BOT_TOKEN: Your Slack bot token (xoxb-...)
        - SLACK_SIGNING_SECRET: Your Slack app signing secret
    - Configure Slack App:
        - Add Event Subscriptions URL: https://your-domain/agent/slack/events
        - Subscribe to bot events: app_mention, message
        - Add OAuth scopes: chat:write, app_mentions:read, im:history

Usage:
    python examples/slack_usage.py
"""

import logging
import os
from typing import TYPE_CHECKING, Any

import uvicorn
from fastapi import FastAPI

import fastapi_agentrouter

if TYPE_CHECKING:
    from vertexai.preview.reasoning_engines import AdkApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Example 1: Simple Mock Agent for Testing
class SimpleMockAgent:
    """A simple mock agent that echoes messages."""

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Stream a simple echo response."""
        logger.info(f"SimpleMockAgent received: {message} from user {user_id}")
        yield f"Echo: {message}"


# Example 2: More Sophisticated Mock Agent with Structured Responses
class AdvancedMockAgent:
    """A mock agent that returns structured responses similar to Vertex AI ADK."""

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Stream structured responses similar to ADK format."""
        logger.info(
            f"AdvancedMockAgent processing: {message} "
            f"(user: {user_id}, session: {session_id})"
        )

        # Simulate multiple response chunks
        responses = [
            "I understand you're asking about: ",
            message,
            "\n\nHere's my response: ",
            f"This is a mock response for '{message}'.",
        ]

        for response_text in responses:
            # Yield in ADK-like format
            yield {
                "content": {
                    "parts": [
                        {"text": response_text},
                    ],
                },
            }


# Example 3: Integration with Vertex AI ADK (when available)
def get_vertex_ai_agent() -> "AdkApp":
    """
    Get a Vertex AI ADK App instance.

    This example shows how to integrate with Google's Vertex AI Agent Development Kit.
    """
    try:
        # Import Vertex AI dependencies
        import vertexai
        from google.adk.agents import Agent
        from vertexai.preview import reasoning_engines

        # Initialize Vertex AI (configure with your project)
        PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID", "your-project-id")
        LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        STAGING_BUCKET = os.getenv(
            "VERTEX_AI_STAGING_BUCKET",
            f"gs://{PROJECT_ID}-vertex-ai-staging",
        )

        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )

        # Create an ADK agent
        agent = Agent(
            name="slack_agent",
            model="gemini-2.5-flash-lite",
            description="An agent that helps users via Slack",
            instruction=(
                "You are a helpful assistant integrated with Slack. "
                "Respond to user questions clearly and concisely. "
                "Always be polite and professional."
            ),
            # Add tools as needed
            tools=[],
        )

        # Return ADK App instance
        return reasoning_engines.AdkApp(
            agent=agent,
            enable_tracing=True,
        )

    except ImportError:
        logger.warning(
            "Vertex AI dependencies not available, falling back to mock agent"
        )
        return AdvancedMockAgent()  # type: ignore[return-value]
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI agent: {e}")
        return AdvancedMockAgent()  # type: ignore[return-value]


# Example 4: Custom Agent with Business Logic
class CustomBusinessAgent:
    """A custom agent with specific business logic."""

    def __init__(self):
        """Initialize the agent with any required resources."""
        self.knowledge_base = {
            "company": "ACME Corp",
            "products": ["Widget A", "Widget B", "Widget C"],
            "support_hours": "9 AM - 5 PM EST",
        }

    def stream_query(
        self,
        *,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        platform: str | None = None,
        channel: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Process queries with business logic."""
        logger.info(
            f"CustomBusinessAgent processing from {platform} "
            f"(channel: {channel}, user: {user_id})"
        )

        # Simple keyword-based responses
        message_lower = message.lower()

        if "product" in message_lower:
            products_list = ", ".join(self.knowledge_base["products"])
            yield f"Our available products are: {products_list}"
        elif "support" in message_lower or "help" in message_lower:
            yield (
                f"Our support hours are {self.knowledge_base['support_hours']}. "
                "How can I assist you today?"
            )
        elif "company" in message_lower or "about" in message_lower:
            yield (
                f"Welcome to {self.knowledge_base['company']}! "
                "We provide high-quality widgets for all your needs."
            )
        else:
            yield (
                f"Thank you for your message: '{message}'. "
                "I can help you with information about our products, "
                "support hours, and company details. What would you like to know?"
            )


# Create FastAPI applications with different agent configurations
def create_app_with_simple_agent() -> FastAPI:
    """Create a FastAPI app with a simple mock agent."""
    app = FastAPI(title="Slack Bot with Simple Agent")

    # Override the dependency to provide your agent
    app.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = (
        lambda: SimpleMockAgent()
    )

    # Include the router - that's it!
    app.include_router(fastapi_agentrouter.router)

    # Add health check endpoint
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "agent": "SimpleMockAgent"}

    return app


def create_app_with_advanced_agent() -> FastAPI:
    """Create a FastAPI app with an advanced mock agent."""
    app = FastAPI(title="Slack Bot with Advanced Agent")

    app.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = (
        lambda: AdvancedMockAgent()
    )
    app.include_router(fastapi_agentrouter.router)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "agent": "AdvancedMockAgent"}

    return app


def create_app_with_vertex_ai() -> FastAPI:
    """Create a FastAPI app with Vertex AI integration."""
    app = FastAPI(title="Slack Bot with Vertex AI")

    app.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = (
        get_vertex_ai_agent
    )
    app.include_router(fastapi_agentrouter.router)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "agent": "Vertex AI ADK"}

    return app


def create_app_with_custom_agent() -> FastAPI:
    """Create a FastAPI app with a custom business logic agent."""
    app = FastAPI(title="Slack Bot with Custom Business Agent")

    app.dependency_overrides[fastapi_agentrouter.get_agent_placeholder] = (
        lambda: CustomBusinessAgent()
    )
    app.include_router(fastapi_agentrouter.router)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "agent": "CustomBusinessAgent"}

    return app


# Main application - choose your agent type
def create_main_app() -> FastAPI:
    """
    Create the main application with agent selection based on environment.

    Set AGENT_TYPE environment variable to choose:
    - simple: Simple echo agent
    - advanced: Advanced mock agent with structured responses
    - vertex: Vertex AI integration (requires setup)
    - custom: Custom business logic agent
    """
    agent_type = os.getenv("AGENT_TYPE", "advanced").lower()

    logger.info(f"Starting Slack bot with {agent_type} agent")

    if agent_type == "simple":
        return create_app_with_simple_agent()
    elif agent_type == "vertex":
        return create_app_with_vertex_ai()
    elif agent_type == "custom":
        return create_app_with_custom_agent()
    else:  # default to advanced
        return create_app_with_advanced_agent()


# Create the app instance
app = create_main_app()


# Additional middleware for logging (optional)
@app.middleware("http")
async def log_requests(request, call_next):
    """Log incoming requests for debugging."""
    # Skip health check logs to reduce noise
    if request.url.path not in ["/health", "/docs", "/openapi.json"]:
        logger.info(f"Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)
    return response


if __name__ == "__main__":
    """
    Run the Slack bot server.

    Before running:
    1. Set required environment variables:
        export SLACK_BOT_TOKEN="xoxb-your-bot-token"
        export SLACK_SIGNING_SECRET="your-signing-secret"
        export AGENT_TYPE="advanced"  # or simple, vertex, custom

    2. Install dependencies:
        pip install fastapi-agentrouter[slack]

    3. Run the server:
        python examples/slack_usage.py

    4. Configure ngrok for local testing:
        ngrok http 8000

    5. Update Slack App configuration:
        - Event Subscriptions URL: https://your-ngrok-url/agent/slack/events
        - Interactivity URL: https://your-ngrok-url/agent/slack/events

    The server will start on http://localhost:8000
    Slack events will be handled at http://localhost:8000/agent/slack/events
    """
    # Check for required Slack credentials
    if not os.getenv("SLACK_BOT_TOKEN") or not os.getenv("SLACK_SIGNING_SECRET"):
        logger.warning(
            "\n"
            "⚠️  SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET not set!\n"
            "The server will start but Slack integration won't work.\n"
            "Set these environment variables to enable Slack functionality.\n"
        )

    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting FastAPI server on port {port}")
    logger.info(f"Slack events endpoint: http://localhost:{port}/agent/slack/events")
    logger.info(f"Health check: http://localhost:{port}/health")
    logger.info(f"API docs: http://localhost:{port}/docs")

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )

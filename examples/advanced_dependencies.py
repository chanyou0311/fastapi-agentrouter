"""Advanced dependency injection examples for FastAPI AgentRouter."""

import logging
from collections.abc import Iterator
from typing import Any

from fastapi import Depends, FastAPI

from fastapi_agentrouter import (
    AgentConfig,
    AgentFactory,
    SessionManager,
    SlackEventHandler,
    create_security_dependencies,
    get_agent_config,
    get_agent_factory,
    get_agent_with_cleanup,
    router,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example 1: Agent with Resource Cleanup
# ----------------------------------------


class DatabaseAgent:
    """Agent that manages database connections."""

    def __init__(self, db_connection):
        self.db = db_connection
        self.active = True

    def stream_query(self, *, message: str, **kwargs) -> Iterator[str]:
        """Query with database access."""
        if not self.active:
            raise RuntimeError("Agent is not active")

        # Simulate database query
        result = f"DB Query for: {message}"
        yield result

    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up database agent")
        self.active = False
        # Close database connection
        if self.db:
            self.db.close()


def get_database_agent():
    """Create agent with automatic cleanup."""

    # Simulate database connection
    class MockDB:
        def close(self):
            logger.info("Database connection closed")

    db = MockDB()
    agent = DatabaseAgent(db)

    try:
        yield agent
    finally:
        agent.cleanup()


# Example 2: Configuration-based Agent Factory
# ---------------------------------------------


class ConfigurableAgent:
    """Agent that can be configured via dependencies."""

    def __init__(self, config: AgentConfig):
        self.config = config
        logger.info(f"Agent created with model: {config.model_name}")

    def stream_query(self, *, message: str, **kwargs) -> Iterator[str]:
        """Process with configuration."""
        response = (
            f"[{self.config.model_name}] "
            f"(temp={self.config.temperature}) "
            f"Response to: {message}"
        )

        if self.config.enable_cache:
            response += " (cached)"

        yield response


def create_configurable_agent(
    config: AgentConfig = Depends(get_agent_config),
) -> ConfigurableAgent:
    """Create agent from configuration."""
    return ConfigurableAgent(config)


def get_production_config() -> AgentConfig:
    """Production configuration."""
    return AgentConfig(
        model_name="gpt-4",
        temperature=0.3,
        enable_cache=True,
        retry_count=5,
        timeout=60,
    )


# Example 3: Stateful Event Handler
# ----------------------------------


class CustomSlackHandler(SlackEventHandler):
    """Extended Slack handler with custom logic."""

    async def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process with custom business logic."""
        # Add custom processing
        if event.get("text", "").startswith("!admin"):
            # Check admin permissions
            if not self._is_admin(event.get("user")):
                return {
                    "text": "Admin access required",
                    "channel": event.get("channel"),
                }

        # Call parent processing
        result = await super().process_event(event)

        # Add custom footer
        result["text"] += "\n\n_Powered by Advanced Agent_"
        return result

    def _is_admin(self, user_id: str) -> bool:
        """Check if user is admin."""
        # Implement your admin check logic
        admin_users = ["U12345", "U67890"]
        return user_id in admin_users


# Example 4: Multi-Agent System
# ------------------------------


class SpecializedAgentFactory(AgentFactory):
    """Factory that creates specialized agents."""

    def get_agent(self, agent_type: str = "default", **overrides: Any):
        """Get specialized agent based on type."""
        if agent_type == "math":
            config = self.base_config.model_copy(
                update={"model_name": "math-solver", "temperature": 0.1}
            )
        elif agent_type == "creative":
            config = self.base_config.model_copy(
                update={"model_name": "creative-writer", "temperature": 0.9}
            )
        else:
            config = self.base_config

        # Apply any additional overrides
        if overrides:
            config = config.model_copy(update=overrides)

        return ConfigurableAgent(config)


# Example 5: Complete Application
# --------------------------------


def create_app() -> FastAPI:
    """Create FastAPI app with advanced dependencies."""
    app = FastAPI(title="Advanced Agent Router")

    # Configure dependencies
    app.dependency_overrides[get_agent_with_cleanup] = get_database_agent
    app.dependency_overrides[get_agent_config] = get_production_config
    app.dependency_overrides[get_agent_factory] = lambda config=Depends(
        get_agent_config
    ): SpecializedAgentFactory(config)

    # Add router with security
    secured_router = router
    secured_router.dependencies = create_security_dependencies("slack")
    app.include_router(secured_router)

    # Add custom endpoints
    @app.post("/agent/multi")
    async def multi_agent_query(
        factory: AgentFactory = Depends(get_agent_factory),
        agent_type: str = "default",
        message: str = "",
    ):
        """Query different agent types."""
        agent = factory.get_agent(agent_type)
        response = list(agent.stream_query(message=message))
        return {"agent_type": agent_type, "response": response}

    @app.post("/agent/session")
    async def session_query(
        session_manager: SessionManager = Depends(),
        session_id: str = "",
        message: str = "",
    ):
        """Query with session management."""
        session = session_manager.get_session(session_id)
        session["message_count"] = session.get("message_count", 0) + 1

        return {
            "session_id": session_id,
            "message_count": session["message_count"],
            "message": message,
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Run the application
if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

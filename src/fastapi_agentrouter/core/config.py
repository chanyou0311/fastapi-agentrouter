"""Configuration management for agent dependencies."""

from typing import Annotated, Any, Optional

from fastapi import Depends
from pydantic import BaseModel, Field

from .dependencies import AgentProtocol, get_agent_placeholder
from .settings import Settings, settings


class AgentConfig(BaseModel):
    """Configuration for agent initialization."""

    model_name: str = Field(default="default", description="Model name to use")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens")
    timeout: int = Field(default=30, description="Timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")
    enable_cache: bool = Field(default=True, description="Enable response caching")
    enable_logging: bool = Field(default=True, description="Enable query logging")
    custom_params: dict[str, Any] = Field(
        default_factory=dict, description="Custom parameters for specific agents"
    )


def get_agent_config(
    settings_dep: Annotated[Settings, Depends(lambda: settings)],
) -> AgentConfig:
    """Get agent configuration from settings or environment.

    This is a sub-dependency that can be overridden independently
    from the agent creation.

    Example:
        def get_custom_config():
            return AgentConfig(
                model_name="gpt-4",
                temperature=0.5,
                enable_cache=False,
            )

        app.dependency_overrides[get_agent_config] = get_custom_config
    """
    # Create config from settings or use defaults
    config = AgentConfig()

    # Could populate from environment variables or settings
    # Example: config.model_name = settings_dep.agent_model_name

    return config


def create_agent_from_config(
    config: Annotated[AgentConfig, Depends(get_agent_config)],
) -> AgentProtocol:
    """Create agent using configuration sub-dependency.

    This separates configuration from agent creation,
    allowing either to be overridden independently.

    Example:
        def my_agent_factory(config: AgentConfig) -> AgentProtocol:
            return MyAgent(
                model=config.model_name,
                temperature=config.temperature,
            )

        app.dependency_overrides[create_agent_from_config] = my_agent_factory
    """
    # This is a placeholder - users should override this
    raise NotImplementedError(
        "Agent creation not implemented. Override create_agent_from_config."
    )


# Type alias for cleaner annotations
ConfiguredAgent = Annotated[AgentProtocol, Depends(create_agent_from_config)]


class MultiAgentConfig(BaseModel):
    """Configuration for multiple agent types."""

    default_agent: AgentConfig = Field(
        default_factory=AgentConfig, description="Default agent configuration"
    )
    specialized_agents: dict[str, AgentConfig] = Field(
        default_factory=dict, description="Specialized agent configurations by type"
    )
    routing_strategy: str = Field(
        default="default", description="Strategy for routing to different agents"
    )


class AgentFactory:
    """Factory for creating agents with different configurations."""

    def __init__(self, base_config: AgentConfig):
        """Initialize factory with base configuration."""
        self.base_config = base_config
        self.agent_cache: dict[str, AgentProtocol] = {}

    def get_agent(self, agent_type: str = "default", **overrides: Any) -> AgentProtocol:
        """Get or create an agent of specified type.

        Args:
            agent_type: Type of agent to create
            **overrides: Configuration overrides

        Returns:
            Agent instance
        """
        cache_key = f"{agent_type}_{hash(frozenset(overrides.items()))}"

        if cache_key not in self.agent_cache:
            # Here would be actual agent creation logic
            # config = self.base_config.model_copy(update=overrides)
            # self.agent_cache[cache_key] = create_actual_agent(config)
            pass

        return self.agent_cache.get(cache_key, get_agent_placeholder())

    def clear_cache(self) -> None:
        """Clear the agent cache."""
        self.agent_cache.clear()


def get_agent_factory(
    config: Annotated[AgentConfig, Depends(get_agent_config)],
) -> AgentFactory:
    """Get agent factory dependency.

    Example:
        @app.post("/query")
        def query(
            factory: Annotated[AgentFactory, Depends(get_agent_factory)],
            agent_type: str = "default",
        ):
            agent = factory.get_agent(agent_type)
            return agent.stream_query(...)
    """
    return AgentFactory(config)


# Type alias for factory dependency
FactoryDep = Annotated[AgentFactory, Depends(get_agent_factory)]

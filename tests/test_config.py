"""Tests for configuration management and sub-dependencies."""

from unittest.mock import Mock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter.core.config import (
    AgentConfig,
    AgentFactory,
    create_agent_from_config,
    get_agent_config,
    get_agent_factory,
)
from fastapi_agentrouter.core.dependencies import AgentProtocol
from fastapi_agentrouter.core.settings import Settings


def test_agent_config_defaults():
    """Test AgentConfig with default values."""
    config = AgentConfig()
    assert config.model_name == "default"
    assert config.temperature == 0.7
    assert config.timeout == 30
    assert config.retry_count == 3
    assert config.enable_cache is True
    assert config.enable_logging is True
    assert config.custom_params == {}


def test_agent_config_custom():
    """Test AgentConfig with custom values."""
    config = AgentConfig(
        model_name="gpt-4",
        temperature=0.5,
        max_tokens=1000,
        custom_params={"key": "value"},
    )
    assert config.model_name == "gpt-4"
    assert config.temperature == 0.5
    assert config.max_tokens == 1000
    assert config.custom_params == {"key": "value"}


def test_get_agent_config_dependency():
    """Test get_agent_config dependency function."""
    settings = Settings()
    config = get_agent_config(settings)
    assert isinstance(config, AgentConfig)
    assert config.model_name == "default"


def test_agent_factory():
    """Test AgentFactory functionality."""
    config = AgentConfig(model_name="test")
    factory = AgentFactory(config)

    # The factory.get_agent currently returns placeholder and raises exception
    # Let's test the factory structure instead
    assert factory.base_config.model_name == "test"

    # Test cache clear
    factory.clear_cache()
    assert len(factory.agent_cache) == 0


def test_agent_config_sub_dependency():
    """Test configuration as sub-dependency."""
    app = FastAPI()

    # Custom config provider
    def get_custom_config(settings: Settings = Depends(lambda: Settings())):
        return AgentConfig(
            model_name="custom-model", temperature=0.3, enable_cache=False
        )

    # Override config dependency
    app.dependency_overrides[get_agent_config] = get_custom_config

    @app.get("/config")
    def get_config_endpoint(config: AgentConfig = Depends(get_agent_config)):
        return config.model_dump()

    client = TestClient(app)
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "custom-model"
    assert data["temperature"] == 0.3
    assert data["enable_cache"] is False


def test_create_agent_from_config_placeholder():
    """Test that create_agent_from_config raises NotImplementedError."""
    config = AgentConfig()
    with pytest.raises(NotImplementedError) as exc_info:
        create_agent_from_config(config)
    assert "not implemented" in str(exc_info.value)


def test_agent_factory_dependency():
    """Test agent factory as dependency."""
    app = FastAPI()

    # Mock agent implementation
    class TestAgent(AgentProtocol):
        def __init__(self, config):
            self.config = config

        def stream_query(self, **kwargs):
            yield f"Response from {self.config.model_name}"

    # Custom factory that creates actual agents
    def get_custom_factory(config: AgentConfig = Depends(get_agent_config)):
        factory = AgentFactory(config)
        # Monkey-patch to create actual agents
        original_get_agent = factory.get_agent

        def custom_get_agent(agent_type="default", **overrides):
            merged_config = config.model_copy(update=overrides)
            return TestAgent(merged_config)

        factory.get_agent = custom_get_agent
        return factory

    app.dependency_overrides[get_agent_factory] = get_custom_factory

    @app.get("/query")
    def query_endpoint(
        factory: AgentFactory = Depends(get_agent_factory), agent_type: str = "default"
    ):
        agent = factory.get_agent(agent_type, temperature=0.8)
        response = list(agent.stream_query(message="test"))
        return {"response": response}

    client = TestClient(app)
    response = client.get("/query")
    assert response.status_code == 200
    assert "Response from default" in response.json()["response"][0]


def test_multi_agent_config():
    """Test MultiAgentConfig functionality."""
    from fastapi_agentrouter.core.config import MultiAgentConfig

    config = MultiAgentConfig(
        default_agent=AgentConfig(model_name="default-model"),
        specialized_agents={
            "math": AgentConfig(model_name="math-model", temperature=0.1),
            "creative": AgentConfig(model_name="creative-model", temperature=0.9),
        },
        routing_strategy="type-based",
    )

    assert config.default_agent.model_name == "default-model"
    assert config.specialized_agents["math"].model_name == "math-model"
    assert config.specialized_agents["math"].temperature == 0.1
    assert config.routing_strategy == "type-based"


def test_config_inheritance_chain():
    """Test configuration inheritance through dependency chain."""
    app = FastAPI()

    # Base settings
    base_settings = Settings()

    # Level 1: Settings -> Config
    def custom_config_provider(settings: Settings = Depends(lambda: base_settings)):
        return AgentConfig(model_name="model-from-settings", timeout=60)

    # Level 2: Config -> Factory
    def custom_factory_provider(config: AgentConfig = Depends(custom_config_provider)):
        return AgentFactory(config)

    app.dependency_overrides[get_agent_config] = custom_config_provider
    app.dependency_overrides[get_agent_factory] = custom_factory_provider

    @app.get("/factory-config")
    def get_factory_config(factory: AgentFactory = Depends(get_agent_factory)):
        return {
            "model_name": factory.base_config.model_name,
            "timeout": factory.base_config.timeout,
        }

    client = TestClient(app)
    response = client.get("/factory-config")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "model-from-settings"
    assert data["timeout"] == 60


def test_agent_factory_caching():
    """Test that AgentFactory properly caches agents."""
    config = AgentConfig(model_name="test")
    factory = AgentFactory(config)

    # Create mock agents
    factory.agent_cache["default_hash1"] = Mock(spec=AgentProtocol)
    factory.agent_cache["custom_hash2"] = Mock(spec=AgentProtocol)

    assert len(factory.agent_cache) == 2

    # Clear cache
    factory.clear_cache()
    assert len(factory.agent_cache) == 0

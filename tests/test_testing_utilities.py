"""Tests for testing utilities."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fastapi_agentrouter.core.dependencies import get_agent_placeholder
from fastapi_agentrouter.testing import (
    AgentTestCase,
    AsyncMockAgent,
    DependencyOverrider,
    MockAgent,
    TestFixtures,
    assert_agent_called,
    create_test_app,
    override_dependency,
)


def test_mock_agent():
    """Test MockAgent functionality."""
    # Default mock agent
    agent = MockAgent()
    responses = list(agent.stream_query(message="test"))
    assert responses == ["Mock response"]
    assert agent.call_count == 1
    assert agent.last_call_args["message"] == "test"

    # Custom responses
    agent = MockAgent(responses=["Response 1", "Response 2"])
    responses = list(agent.stream_query(message="test"))
    assert responses == ["Response 1", "Response 2"]

    # With error
    agent = MockAgent(raise_error=ValueError("Test error"))
    with pytest.raises(ValueError) as exc_info:
        list(agent.stream_query(message="test"))
    assert str(exc_info.value) == "Test error"

    # Reset
    agent.reset()
    assert agent.call_count == 0
    assert agent.last_call_args == {}


@pytest.mark.asyncio
async def test_async_mock_agent():
    """Test AsyncMockAgent functionality."""
    agent = AsyncMockAgent(responses=["Async 1", "Async 2"], delay=0.01)

    responses = []
    async for response in agent.stream_query(message="test"):
        responses.append(response)

    assert responses == ["Async 1", "Async 2"]
    assert agent.call_count == 1


def test_dependency_overrider():
    """Test DependencyOverrider context manager."""
    app = FastAPI()

    def original_dep():
        return "original"

    def replacement_dep():
        return "replacement"

    @app.get("/test")
    def test_endpoint(value: str = Depends(original_dep)):
        return {"value": value}

    client = TestClient(app)

    # Without override
    response = client.get("/test")
    assert response.json()["value"] == "original"

    # With override
    with DependencyOverrider(app).override(original_dep, replacement_dep):
        response = client.get("/test")
        assert response.json()["value"] == "replacement"

    # After context, should revert
    response = client.get("/test")
    assert response.json()["value"] == "original"


def test_override_dependency_function():
    """Test override_dependency context manager."""
    app = FastAPI()

    def dep():
        return "original"

    @app.get("/test")
    def test_endpoint(value: str = Depends(dep)):
        return {"value": value}

    client = TestClient(app)

    with override_dependency(app, dep, lambda: "overridden"):
        response = client.get("/test")
        assert response.json()["value"] == "overridden"

    # Should revert after context
    response = client.get("/test")
    assert response.json()["value"] == "original"


def test_test_fixtures():
    """Test TestFixtures helper methods."""
    fixtures = TestFixtures()

    # Create mock agent
    agent = fixtures.create_mock_agent(responses=["test"])
    assert isinstance(agent, MockAgent)
    assert list(agent.stream_query(message="test")) == ["test"]

    # Create test client
    app = FastAPI()
    client = fixtures.create_test_client(app)
    assert isinstance(client, TestClient)

    # Create mock settings
    settings = fixtures.create_mock_settings(disable_slack=True)
    assert settings.disable_slack is True
    assert settings.disable_discord is False

    # Create mock security context
    context = fixtures.create_mock_security_context(user_id="test_user")
    assert context.user_id == "test_user"
    assert context.platform == "test"


def test_agent_test_case():
    """Test AgentTestCase helper class."""
    app = FastAPI()

    @app.get("/query")
    def query(agent=Depends(get_agent_placeholder)):
        return {"response": list(agent.stream_query(message="test"))}

    test_case = AgentTestCase(app)

    # Setup agent
    test_case.setup_agent()

    # Make request
    response = test_case.client.get("/query")
    assert response.status_code == 200
    assert response.json()["response"] == ["Mock response"]

    # Check agent was called
    assert test_case.mock_agent.call_count == 1

    # Setup custom agent
    custom_agent = MockAgent(responses=["Custom"])
    test_case.setup_agent(custom_agent)

    response = test_case.client.get("/query")
    assert response.json()["response"] == ["Custom"]

    # Reset
    test_case.reset()
    assert test_case.mock_agent.call_count == 0
    assert len(test_case.app.dependency_overrides) == 0


def test_agent_test_case_settings():
    """Test AgentTestCase settings setup."""
    app = FastAPI()
    
    mock_settings = None
    
    def get_test_settings():
        return mock_settings

    @app.get("/settings")
    def get_settings(settings=Depends(get_test_settings)):
        return {"disable_slack": settings.disable_slack}

    test_case = AgentTestCase(app)

    # Setup custom settings
    test_case.setup_settings(disable_slack=True)
    mock_settings = test_case.fixtures.create_mock_settings(disable_slack=True)
    app.dependency_overrides[get_test_settings] = lambda: mock_settings

    response = test_case.client.get("/settings")
    assert response.json()["disable_slack"] is True


def test_create_test_app():
    """Test create_test_app helper."""
    app = create_test_app(title="Test Application")

    assert app.title == "Test Application"

    # Should have router included
    routes = [route.path for route in app.routes]
    assert any("/agent" in path for path in routes)


def test_assert_agent_called():
    """Test assert_agent_called helper."""
    agent = MockAgent()

    # Not called yet
    with pytest.raises(AssertionError) as exc_info:
        assert_agent_called(agent)
    assert "Agent was not called" in str(exc_info.value)

    # Call agent
    list(agent.stream_query(message="Hello", user_id="user123", custom_param="value"))

    # Should pass
    assert_agent_called(agent)
    assert_agent_called(agent, expected_message="Hello")
    assert_agent_called(agent, expected_user_id="user123")
    assert_agent_called(agent, expected_kwargs={"custom_param": "value"})

    # Wrong expectations should fail
    with pytest.raises(AssertionError) as exc_info:
        assert_agent_called(agent, expected_message="Wrong")
    assert "Expected message" in str(exc_info.value)

    with pytest.raises(AssertionError) as exc_info:
        assert_agent_called(agent, expected_user_id="wrong_user")
    assert "Expected user_id" in str(exc_info.value)

    with pytest.raises(AssertionError) as exc_info:
        assert_agent_called(agent, expected_kwargs={"missing": "param"})
    assert "Missing expected kwarg" in str(exc_info.value)


def test_multiple_dependency_overrides():
    """Test DependencyOverrider with multiple overrides."""
    app = FastAPI()

    def dep1():
        return "dep1"

    def dep2():
        return "dep2"

    @app.get("/test")
    def test_endpoint(val1: str = Depends(dep1), val2: str = Depends(dep2)):
        return {"val1": val1, "val2": val2}

    client = TestClient(app)

    # Override both dependencies
    overrider = DependencyOverrider(app)
    overrider.override(dep1, lambda: "new1")
    overrider.override(dep2, lambda: "new2")

    with overrider:
        response = client.get("/test")
        assert response.json() == {"val1": "new1", "val2": "new2"}

    # Should revert both
    response = client.get("/test")
    assert response.json() == {"val1": "dep1", "val2": "dep2"}


def test_mock_agent_with_structured_responses():
    """Test MockAgent with different response formats."""
    agent = MockAgent(responses=["Part 1", "Part 2", "Part 3"])

    # Collect all responses
    all_responses = []
    for response in agent.stream_query(
        message="test", user_id="user1", session_id="session1", extra_param="value"
    ):
        all_responses.append(response)

    assert all_responses == ["Part 1", "Part 2", "Part 3"]
    assert agent.last_call_args["message"] == "test"
    assert agent.last_call_args["user_id"] == "user1"
    assert agent.last_call_args["session_id"] == "session1"
    assert agent.last_call_args["extra_param"] == "value"

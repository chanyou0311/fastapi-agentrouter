"""Testing utilities for FastAPI AgentRouter dependency injection."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Callable, Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient

from .core.dependencies import AgentProtocol


class MockAgent(AgentProtocol):
    """Mock agent for testing purposes."""

    def __init__(
        self,
        responses: Optional[list[str]] = None,
        raise_error: Optional[Exception] = None,
    ):
        """Initialize mock agent.

        Args:
            responses: List of responses to return
            raise_error: Exception to raise when called
        """
        self.responses = responses or ["Mock response"]
        self.raise_error = raise_error
        self.call_count = 0
        self.last_call_args: dict[str, Any] = {}

    def stream_query(
        self,
        *,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """Mock implementation of stream_query."""
        self.call_count += 1
        self.last_call_args = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            **kwargs,
        }

        if self.raise_error:
            raise self.raise_error

        yield from self.responses

    def reset(self) -> None:
        """Reset mock state."""
        self.call_count = 0
        self.last_call_args = {}


class DependencyOverrider:
    """Context manager for overriding dependencies in tests."""

    def __init__(self, app: FastAPI):
        """Initialize dependency overrider.

        Args:
            app: FastAPI application instance
        """
        self.app = app
        self.overrides: dict[Callable, Callable] = {}
        self.original_overrides: dict[Callable, Callable] = {}

    def override(
        self, dependency: Callable, replacement: Callable
    ) -> "DependencyOverrider":
        """Add a dependency override.

        Args:
            dependency: Original dependency to override
            replacement: Replacement dependency

        Returns:
            Self for chaining
        """
        self.overrides[dependency] = replacement
        return self

    def __enter__(self) -> "DependencyOverrider":
        """Enter context and apply overrides."""
        # Save original overrides
        self.original_overrides = self.app.dependency_overrides.copy()

        # Apply new overrides
        for dep, repl in self.overrides.items():
            self.app.dependency_overrides[dep] = repl

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and restore original overrides."""
        # Restore original overrides
        self.app.dependency_overrides = self.original_overrides


@contextmanager
def override_dependency(
    app: FastAPI, dependency: Callable, replacement: Callable
) -> Generator[None, None, None]:
    """Simple context manager for overriding a single dependency.

    Args:
        app: FastAPI application
        dependency: Dependency to override
        replacement: Replacement dependency

    Example:
        with override_dependency(app, get_agent, lambda: mock_agent):
            response = client.get("/test")
    """
    original = app.dependency_overrides.get(dependency)
    app.dependency_overrides[dependency] = replacement
    try:
        yield
    finally:
        if original is None:
            app.dependency_overrides.pop(dependency, None)
        else:
            app.dependency_overrides[dependency] = original


class TestFixtures:
    """Collection of common test fixtures."""

    @staticmethod
    def create_mock_agent(**kwargs: Any) -> MockAgent:
        """Create a mock agent with optional configuration."""
        return MockAgent(**kwargs)

    @staticmethod
    def create_test_client(app: FastAPI, **kwargs: Any) -> TestClient:
        """Create a test client with optional configuration."""
        return TestClient(app, **kwargs)

    @staticmethod
    def create_mock_settings(**overrides: Any) -> Any:
        """Create mock settings with overrides.

        Args:
            **overrides: Settings to override

        Returns:
            Mock settings object
        """
        from .core.settings import Settings

        # Create settings with overrides
        settings_dict = {
            "disable_slack": False,
            "disable_discord": False,
            "disable_webhook": False,
            **overrides,
        }

        # Create Settings instance with overrides
        return Settings(**settings_dict)

    @staticmethod
    def create_mock_security_context(
        user_id: str = "test_user",
        platform: str = "test",
        **kwargs: Any,
    ) -> Any:
        """Create mock security context."""
        from .core.security import SecurityContext

        return SecurityContext(user_id=user_id, platform=platform, **kwargs)


class AgentTestCase:
    """Base class for agent testing with common setup."""

    def __init__(self, app: FastAPI):
        """Initialize test case.

        Args:
            app: FastAPI application to test
        """
        self.app = app
        self.client = TestClient(app)
        self.mock_agent = MockAgent()
        self.fixtures = TestFixtures()

    def setup_agent(self, agent: Optional[AgentProtocol] = None) -> None:
        """Setup agent dependency override.

        Args:
            agent: Agent to use, defaults to mock_agent
        """
        from .core.dependencies import get_agent_placeholder

        agent = agent or self.mock_agent
        self.app.dependency_overrides[get_agent_placeholder] = lambda: agent

    def setup_settings(self, **overrides: Any) -> None:
        """Setup settings dependency override.

        Args:
            **overrides: Settings to override
        """
        from .core.settings import settings as default_settings

        mock_settings = self.fixtures.create_mock_settings(**overrides)
        self.app.dependency_overrides[lambda: default_settings] = lambda: mock_settings

    def reset(self) -> None:
        """Reset all overrides and mock state."""
        self.app.dependency_overrides.clear()
        self.mock_agent.reset()


def create_test_app(**config: Any) -> FastAPI:
    """Create a FastAPI app configured for testing.

    Args:
        **config: Configuration overrides

    Returns:
        Configured FastAPI app
    """
    from .routers import router

    # Set default title if not provided
    if "title" not in config:
        config["title"] = "Test App"
    
    app = FastAPI(**config)
    app.include_router(router)
    return app


class AsyncMockAgent(AgentProtocol):
    """Async mock agent for testing async endpoints."""

    def __init__(
        self,
        responses: Optional[list[str]] = None,
        delay: float = 0.0,
    ):
        """Initialize async mock agent.

        Args:
            responses: List of responses to return
            delay: Delay in seconds before each response
        """
        self.responses = responses or ["Async mock response"]
        self.delay = delay
        self.call_count = 0

    async def stream_query(
        self,
        *,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Async mock implementation."""
        import asyncio

        self.call_count += 1

        for response in self.responses:
            if self.delay > 0:
                await asyncio.sleep(self.delay)
            yield response


def assert_agent_called(
    agent: MockAgent,
    expected_message: Optional[str] = None,
    expected_user_id: Optional[str] = None,
    expected_kwargs: Optional[dict] = None,
) -> None:
    """Assert that agent was called with expected arguments.

    Args:
        agent: Mock agent to check
        expected_message: Expected message parameter
        expected_user_id: Expected user_id parameter
        expected_kwargs: Expected additional kwargs

    Raises:
        AssertionError: If expectations not met
    """
    assert agent.call_count > 0, "Agent was not called"

    if expected_message is not None:
        assert agent.last_call_args.get("message") == expected_message, (
            f"Expected message '{expected_message}', "
            f"got '{agent.last_call_args.get('message')}'"
        )

    if expected_user_id is not None:
        assert agent.last_call_args.get("user_id") == expected_user_id, (
            f"Expected user_id '{expected_user_id}', "
            f"got '{agent.last_call_args.get('user_id')}'"
        )

    if expected_kwargs:
        for key, value in expected_kwargs.items():
            assert key in agent.last_call_args, f"Missing expected kwarg: {key}"
            assert agent.last_call_args[key] == value, (
                f"Expected {key}='{value}', got {key}='{agent.last_call_args[key]}'"
            )

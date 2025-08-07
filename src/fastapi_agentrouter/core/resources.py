"""Resource management dependencies with cleanup support."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Protocol

from fastapi import HTTPException

from .dependencies import AgentProtocol

logger = logging.getLogger(__name__)


class CleanupProtocol(Protocol):
    """Protocol for agents with cleanup support."""

    def cleanup(self) -> None:
        """Cleanup resources synchronously."""
        ...


class AsyncCleanupProtocol(Protocol):
    """Protocol for agents with async cleanup support."""

    async def cleanup(self) -> None:
        """Cleanup resources asynchronously."""
        ...


class AgentWithCleanup(AgentProtocol, CleanupProtocol):
    """Combined protocol for agents with cleanup support."""

    pass


class AsyncAgentWithCleanup(AgentProtocol, AsyncCleanupProtocol):
    """Combined protocol for async agents with cleanup support."""

    pass


def get_agent_with_cleanup() -> Generator[AgentProtocol, None, None]:
    """Agent dependency with automatic cleanup.

    This is a placeholder that should be overridden by the user's actual
    implementation that provides cleanup capabilities.

    Example usage:
        def get_my_agent_with_cleanup():
            agent = create_agent()
            try:
                yield agent
            finally:
                agent.cleanup()

        app.dependency_overrides[get_agent_with_cleanup] = get_my_agent_with_cleanup
    """
    raise HTTPException(
        status_code=500,
        detail="Agent with cleanup not configured. Please provide agent dependency.",
    )


async def get_async_agent_with_cleanup() -> AsyncGenerator[AgentProtocol, None]:
    """Async agent dependency with automatic cleanup.

    This is a placeholder that should be overridden by the user's actual
    async implementation.

    Example usage:
        async def get_my_async_agent():
            agent = await create_async_agent()
            try:
                yield agent
            finally:
                await agent.cleanup()

        app.dependency_overrides[get_async_agent_with_cleanup] = get_my_async_agent
    """
    raise HTTPException(
        status_code=500,
        detail="Async agent with cleanup not configured.",
    )
    yield  # type: ignore[unreachable]  # Make this an async generator


class ResourceManager:
    """Manages resources with automatic cleanup on context exit."""

    def __init__(self) -> None:
        """Initialize resource manager."""
        self.resources: list[Any] = []
        self.cleanup_callbacks: list[Any] = []

    def register(self, resource: Any, cleanup_callback: Any = None) -> Any:
        """Register a resource for cleanup.

        Args:
            resource: The resource to manage
            cleanup_callback: Optional cleanup callback

        Returns:
            The resource itself for chaining
        """
        self.resources.append(resource)
        if cleanup_callback:
            self.cleanup_callbacks.append(cleanup_callback)
        elif hasattr(resource, "cleanup"):
            self.cleanup_callbacks.append(resource.cleanup)
        elif hasattr(resource, "close"):
            self.cleanup_callbacks.append(resource.close)
        return resource

    def cleanup(self) -> None:
        """Clean up all registered resources."""
        for i, callback in enumerate(reversed(self.cleanup_callbacks)):
            try:
                callback()
            except Exception as e:
                logger.error(f"Error during resource cleanup: {e}")

    async def async_cleanup(self) -> None:
        """Clean up all registered resources asynchronously."""
        for callback in reversed(self.cleanup_callbacks):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error during async resource cleanup: {e}")


@contextmanager
def resource_context() -> Generator[ResourceManager, None, None]:
    """Context manager for resource management.

    Example:
        def get_resources():
            with resource_context() as rm:
                db = rm.register(get_database_connection())
                cache = rm.register(get_cache_client())
                yield {"db": db, "cache": cache}
    """
    manager = ResourceManager()
    try:
        yield manager
    finally:
        manager.cleanup()


@asynccontextmanager
async def async_resource_context() -> AsyncGenerator[ResourceManager, None]:
    """Async context manager for resource management.

    Example:
        async def get_resources():
            async with async_resource_context() as rm:
                db = rm.register(await get_async_db())
                cache = rm.register(await get_async_cache())
                yield {"db": db, "cache": cache}
    """
    manager = ResourceManager()
    try:
        yield manager
    finally:
        await manager.async_cleanup()


class SessionManager:
    """Manages session state across requests."""

    def __init__(self) -> None:
        """Initialize session manager."""
        self.sessions: dict[str, dict[str, Any]] = {}

    def get_session(self, session_id: str) -> dict[str, Any]:
        """Get or create session data."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        return self.sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        """Clear session data."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_old_sessions(self, max_age_seconds: int = 3600) -> None:
        """Clean up old sessions based on age."""
        # Implementation would check timestamps and remove old sessions
        pass


def get_session_manager() -> Generator[SessionManager, None, None]:
    """Dependency for session management with cleanup.

    Example:
        @app.post("/chat")
        def chat(
            session: Annotated[SessionManager, Depends(get_session_manager)],
            session_id: str,
        ):
            session_data = session.get_session(session_id)
            # Use session data
    """
    manager = SessionManager()
    try:
        yield manager
    finally:
        # Could persist sessions or clean up here
        logger.info("Session manager cleanup")

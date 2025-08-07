"""FastAPI AgentRouter - AI Agent interface library for FastAPI."""

__version__ = "0.3.0"

# Core dependencies
# Enhanced dependencies
from .core.config import (
    AgentConfig,
    AgentFactory,
    ConfiguredAgent,
    create_agent_from_config,
    get_agent_config,
    get_agent_factory,
)
from .core.dependencies import AgentProtocol, get_agent_placeholder
from .core.handlers import (
    BaseEventHandler,
    ConversationManager,
    SlackEventHandler,
    WebhookEventHandler,
)
from .core.resources import (
    AgentWithCleanup,
    AsyncAgentWithCleanup,
    ResourceManager,
    SessionManager,
    async_resource_context,
    get_agent_with_cleanup,
    get_async_agent_with_cleanup,
    get_session_manager,
    resource_context,
)
from .core.security import (
    RateLimiter,
    SecurityContext,
    check_api_key,
    check_rate_limit,
    create_platform_signature_verifier,
    create_security_dependencies,
    get_security_context,
    log_request,
    verify_signature,
)

# Router
from .routers import router

# Testing utilities
from .testing import (
    AgentTestCase,
    AsyncMockAgent,
    DependencyOverrider,
    MockAgent,
    TestFixtures,
    assert_agent_called,
    create_test_app,
    override_dependency,
)

__all__ = [
    "AgentConfig",
    "AgentFactory",
    "AgentProtocol",
    "AgentTestCase",
    "AgentWithCleanup",
    "AsyncAgentWithCleanup",
    "AsyncMockAgent",
    "BaseEventHandler",
    "ConfiguredAgent",
    "ConversationManager",
    "DependencyOverrider",
    "MockAgent",
    "RateLimiter",
    "ResourceManager",
    "SecurityContext",
    "SessionManager",
    "SlackEventHandler",
    "TestFixtures",
    "WebhookEventHandler",
    "__version__",
    "assert_agent_called",
    "async_resource_context",
    "check_api_key",
    "check_rate_limit",
    "create_agent_from_config",
    "create_platform_signature_verifier",
    "create_security_dependencies",
    "create_test_app",
    "get_agent_config",
    "get_agent_factory",
    "get_agent_placeholder",
    "get_agent_with_cleanup",
    "get_async_agent_with_cleanup",
    "get_security_context",
    "get_session_manager",
    "log_request",
    "override_dependency",
    "resource_context",
    "router",
    "verify_signature",
]

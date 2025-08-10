# FastAPI AgentRouter - Improvement Suggestions

Based on the FastAPI dependencies documentation review, here are potential improvements that could be implemented in separate tasks:

## 1. Enhanced Agent Dependency with Sub-dependencies
**Current**: Single `get_agent_placeholder` function
**Suggestion**: Create a hierarchical dependency system for agents

```python
# Example implementation
def get_agent_config() -> AgentConfig:
    """Get agent configuration (could be from env, file, etc.)"""
    return AgentConfig(...)

def get_agent(config: Annotated[AgentConfig, Depends(get_agent_config)]) -> Agent:
    """Create agent with configuration dependency"""
    return create_agent(config)

AgentDep = Annotated[Agent, Depends(get_agent)]
```

**Benefits**:
- Separate configuration from agent creation
- Easier testing with different configurations
- Support for multiple agent types

## 2. Dependencies with Yield for Resource Management
**Current**: No resource cleanup in dependencies
**Suggestion**: Add support for cleanup operations

```python
async def get_agent_with_cleanup() -> Generator[Agent, None, None]:
    """Agent dependency with automatic cleanup"""
    agent = await create_agent()
    try:
        yield agent
    finally:
        await agent.cleanup()  # Close connections, save state, etc.
```

**Use cases**:
- Database connection management for agents
- Temporary file cleanup
- Session state persistence

## 3. Global Dependencies for Cross-cutting Concerns
**Current**: Dependencies at endpoint level only
**Suggestion**: Add router-level dependencies

```python
# Add to router creation
slack_router = APIRouter(
    prefix="/slack",
    tags=["slack"],
    dependencies=[
        Depends(check_slack_enabled),
        Depends(verify_slack_signature),  # New: signature verification
        Depends(rate_limiter),            # New: rate limiting
    ]
)
```

**Benefits**:
- Consistent security across all Slack endpoints
- Rate limiting per integration
- Audit logging

## 4. Class-based Dependencies for Complex Logic
**Current**: Function-based dependencies
**Suggestion**: Class-based dependencies for stateful operations

```python
class SlackEventHandler:
    """Stateful Slack event handler"""

    def __init__(self, settings: SettingsDep, agent: AgentDep):
        self.settings = settings
        self.agent = agent
        self.event_queue = []

    async def process_event(self, event: dict) -> dict:
        """Process Slack event with state management"""
        # Complex logic with state
        pass

SlackHandlerDep = Annotated[SlackEventHandler, Depends()]
```

**Benefits**:
- Encapsulate complex logic
- Maintain state across requests (with caching)
- Better code organization

## 5. Dependency Caching Control
**Current**: Default caching behavior
**Suggestion**: Explicit cache control for specific use cases

```python
# For metrics or logging that should run every time
def log_request(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings, use_cache=False)]
) -> None:
    """Log every request without caching"""
    logger.info(f"Request to {request.url}")
```

## 6. Parameterized Dependencies
**Current**: Static dependencies
**Suggestion**: Factory pattern for parameterized dependencies

```python
def create_platform_checker(platform: str):
    """Factory for platform-specific checkers"""
    def check_platform_enabled(settings: SettingsDep) -> None:
        if not getattr(settings, f"enable_{platform}", False):
            raise HTTPException(404, f"{platform} not enabled")
    return check_platform_enabled

# Usage
dependencies=[Depends(create_platform_checker("slack"))]
```

## 7. Async Context Managers in Dependencies
**Current**: Synchronous dependencies
**Suggestion**: Support for async context managers

```python
async def get_async_agent() -> AsyncGenerator[Agent, None]:
    """Async agent with connection pooling"""
    async with AgentPool() as pool:
        agent = await pool.acquire()
        try:
            yield agent
        finally:
            await pool.release(agent)
```

## 8. Testing Utilities
**Current**: Manual dependency override
**Suggestion**: Testing helpers

```python
class DependencyOverrider:
    """Context manager for testing"""
    def __init__(self, app: FastAPI):
        self.app = app
        self.overrides = {}

    def override(self, dependency, replacement):
        self.overrides[dependency] = replacement
        return self

    def __enter__(self):
        for dep, repl in self.overrides.items():
            self.app.dependency_overrides[dep] = repl
        return self

    def __exit__(self, *args):
        for dep in self.overrides:
            del self.app.dependency_overrides[dep]

# Usage in tests
with DependencyOverrider(app).override(get_settings, lambda: test_settings):
    response = client.get("/test")
```

## Priority Recommendations

1. **High Priority**: Dependencies with Yield (#2) - Important for resource management
2. **High Priority**: Global Dependencies (#3) - Security and consistency
3. **Medium Priority**: Enhanced Agent Dependency (#1) - Better architecture
4. **Medium Priority**: Testing Utilities (#8) - Developer experience
5. **Low Priority**: Other improvements - Nice to have

These improvements would make the library more robust, flexible, and easier to use in production environments.

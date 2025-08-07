"""Example of custom settings configuration without environment variables."""

from fastapi import FastAPI
from fastapi_agentrouter import get_agent_placeholder, router
from fastapi_agentrouter.core.settings import Settings, SettingsProvider, get_settings


class MockAgent:
    """Mock agent for demonstration."""

    def stream_query(self, **kwargs):
        yield f"Response from mock agent"


# Method 1: Override get_settings function
def create_app_with_function_override():
    """Create app by overriding the get_settings function."""
    app = FastAPI()
    
    # Override the agent
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    
    # Override settings with a custom instance
    custom_settings = Settings(enable_slack=True)
    app.dependency_overrides[get_settings] = lambda: custom_settings
    
    app.include_router(router)
    return app


# Method 2: Use Settings class directly as dependency
def create_app_with_class_dependency():
    """Create app using Settings class as dependency."""
    app = FastAPI()
    
    # Override the agent
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    
    # Override Settings class to return custom instance
    app.dependency_overrides[Settings] = lambda: Settings(enable_slack=True)
    
    app.include_router(router)
    return app


# Method 3: Use SettingsProvider for more control
def create_app_with_provider():
    """Create app using SettingsProvider for flexible configuration."""
    app = FastAPI()
    
    # Override the agent
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    
    # Create a custom provider with specific settings
    custom_provider = SettingsProvider(Settings(enable_slack=True))
    app.dependency_overrides[SettingsProvider] = lambda: custom_provider
    
    app.include_router(router)
    return app


# Method 4: Runtime configuration
def create_app_with_runtime_config(enable_slack: bool = False):
    """Create app with runtime configuration."""
    app = FastAPI()
    
    # Override the agent
    app.dependency_overrides[get_agent_placeholder] = lambda: MockAgent()
    
    # Configure settings based on runtime parameters
    settings = Settings(enable_slack=enable_slack)
    app.dependency_overrides[get_settings] = lambda: settings
    
    app.include_router(router)
    return app


if __name__ == "__main__":
    import uvicorn
    
    # Choose one of the methods
    app = create_app_with_function_override()
    # app = create_app_with_class_dependency()
    # app = create_app_with_provider()
    # app = create_app_with_runtime_config(enable_slack=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
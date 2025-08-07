"""Settings management for FastAPI AgentRouter using pydantic-settings."""

from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    All settings have sensible defaults and the application works without any
    environment variables set.
    
    This class can be used in three ways:
    1. As a singleton with environment variables (default)
    2. As a dependency that can be overridden
    3. As a class dependency for custom instances
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Platform enable/disable settings
    enable_slack: bool = Field(
        default=False,
        description="Enable Slack integration endpoints",
    )


# Cache the environment-based settings instance
@lru_cache
def get_settings() -> Settings:
    """Get the cached settings instance from environment.
    
    This function is cached to ensure we only create one instance
    when reading from environment variables.
    
    Returns:
        Settings: The settings instance
    
    Example:
        # Basic usage with environment variables
        settings = get_settings()
        
        # Override in FastAPI app for testing
        app.dependency_overrides[get_settings] = lambda: Settings(enable_slack=True)
    """
    return Settings()


# Alternative: Class-based dependency for more flexibility
class SettingsProvider:
    """Provider for settings that can be easily customized.
    
    This allows for more complex dependency injection patterns,
    including runtime configuration.
    
    Example:
        # Create a custom provider
        custom_provider = SettingsProvider(Settings(enable_slack=True))
        app.dependency_overrides[SettingsProvider] = lambda: custom_provider
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the settings provider.
        
        Args:
            settings: Optional custom settings. If None, uses environment.
        """
        self.settings = settings or get_settings()
    
    def __call__(self) -> Settings:
        """Return the settings instance."""
        return self.settings


# Dependency type annotations for clean code
SettingsDep = Annotated[Settings, Depends(get_settings)]
SettingsClassDep = Annotated[Settings, Depends(Settings)]  # Direct class dependency
SettingsProviderDep = Annotated[Settings, Depends(SettingsProvider)]

# For backward compatibility
settings = get_settings()

"""
Protocol for node configuration management in ONEX architecture.

Domain: Core configuration protocols for ONEX nodes
"""

from typing import Any, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import ContextValue, ProtocolConfigValue


@runtime_checkable
class ProtocolNodeConfiguration(Protocol):
    """
    Protocol for node configuration management.

    Provides standardized configuration access for all ONEX nodes
    without coupling to specific configuration implementations.
    """

    def get_config_value(
        self, key: str, default: Optional[ContextValue] = None
    ) -> ContextValue:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (dot-separated path supported)
            default: Default value if key not found

        Returns:
            Configuration value or default

        Raises:
            KeyError: If key not found and no default provided
        """
        ...

    def get_timeout_ms(
        self, timeout_type: str, default_ms: Optional[int] = None
    ) -> int:
        """
        Get timeout configuration in milliseconds.

        Args:
            timeout_type: Type of timeout (api_call, health_check, etc.)
            default_ms: Default timeout if not configured

        Returns:
            Timeout in milliseconds
        """
        ...

    def get_security_config(
        self, key: str, default: Optional[ContextValue] = None
    ) -> ContextValue:
        """
        Get security-related configuration value.

        Args:
            key: Security configuration key
            default: Default value if key not found

        Returns:
            Security configuration value
        """
        ...

    def get_business_logic_config(
        self, key: str, default: Optional[ContextValue] = None
    ) -> ContextValue:
        """
        Get business logic configuration value.

        Args:
            key: Business logic configuration key
            default: Default value if key not found

        Returns:
            Business logic configuration value
        """
        ...

    def get_performance_config(
        self, key: str, default: Optional[ContextValue] = None
    ) -> ContextValue:
        """
        Get performance-related configuration value.

        Args:
            key: Performance configuration key
            default: Default value if key not found

        Returns:
            Performance configuration value
        """
        ...

    def has_config(self, key: str) -> bool:
        """
        Check if configuration key exists.

        Args:
            key: Configuration key to check

        Returns:
            True if key exists, False otherwise
        """
        ...

    def get_all_config(self) -> dict[str, ContextValue]:
        """
        Get all configuration as dictionary.

        Returns:
            Complete configuration dictionary
        """
        ...


@runtime_checkable
class ProtocolNodeConfigurationProvider(Protocol):
    """
    Protocol for configuration provider implementations.

    Allows different configuration backends (environment, files, databases)
    to be used interchangeably through dependency injection.
    """

    def load_configuration(
        self, node_type: str, node_id: str
    ) -> ProtocolNodeConfiguration:
        """
        Load configuration for specific node.

        Args:
            node_type: Type of node (COMPUTE, EFFECT, etc.)
            node_id: Unique identifier for node instance

        Returns:
            Configuration instance for the node

        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        ...

    def reload_configuration(self) -> None:
        """
        Reload configuration from source.

        Used for hot-reloading configuration changes.
        """
        ...

    def validate_configuration(self) -> bool:
        """
        Validate current configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        ...


@runtime_checkable
class ProtocolConfigurationError(Protocol):
    """Protocol for configuration-related errors."""

    message: str
    key: Optional[str]
    source: str

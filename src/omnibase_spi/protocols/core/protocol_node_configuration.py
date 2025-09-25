"""
Protocol for node configuration management in ONEX architecture.

Domain: Core configuration protocols for ONEX nodes
"""

from typing import Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolNodeConfiguration(Protocol):
    """
    Protocol for node configuration management.

    Provides standardized configuration access for all ONEX nodes
    without coupling to specific configuration implementations.

    Example:
        ```python
        # Basic usage
        config: ProtocolNodeConfiguration = get_node_config()

        # Get configuration values
        api_url = config.get_config_value("api.base_url", "http://localhost:8080")
        timeout = config.get_timeout_ms("api_call", 5000)

        # Domain-specific configurations
        auth_settings = config.get_security_config("authentication")
        perf_limits = config.get_performance_config("memory.max_heap_mb")

        # Check configuration availability
        if config.has_config("feature.experimental"):
            experimental_mode = config.get_config_value("feature.experimental")

        # Validate configurations
        is_valid = config.validate_config("api.base_url")
        required_keys = ["database.host", "database.port", "api.key"]
        validation_results = config.validate_required_configs(required_keys)

        # Get configuration schema
        schema = config.get_config_schema()
        ```
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

    def validate_config(self, config_key: str) -> bool:
        """
        Validate configuration key exists and has valid value.

        Args:
            config_key: Configuration key to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        ...

    def validate_required_configs(self, required_keys: list[str]) -> dict[str, bool]:
        """
        Validate multiple required configuration keys.

        Args:
            required_keys: List of configuration keys that must be present

        Returns:
            Dictionary mapping config keys to validation status
        """
        ...

    def get_config_schema(self) -> dict[str, str]:
        """
        Get configuration schema with expected types.

        Returns:
            Dictionary mapping config keys to expected type names
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
    """
    Protocol for configuration-related errors.

    Provides structured error information for configuration failures
    with support for error formatting and context details.

    Example:
        ```python
        error: ProtocolConfigurationError = ConfigError(
            message="Missing required configuration",
            key="database.host",
            source="environment"
        )

        # String representation
        error_msg = str(error)  # "Config error in environment: Missing required configuration (key: database.host)"

        # Check if error is for specific key
        if error.is_key_error("database.host"):
            # Handle specific key error
            pass
        ```
    """

    message: str
    key: Optional[str]
    source: str

    def __str__(self) -> str:
        """
        String representation of configuration error.

        Returns:
            Formatted error message with context
        """
        ...

    def is_key_error(self, config_key: str) -> bool:
        """
        Check if error is related to specific configuration key.

        Args:
            config_key: Configuration key to check

        Returns:
            True if error is for the specified key
        """
        ...

    def get_error_context(self) -> dict[str, Optional[str]]:
        """
        Get error context information.

        Returns:
            Dictionary with error context (message, key, source)
        """
        ...

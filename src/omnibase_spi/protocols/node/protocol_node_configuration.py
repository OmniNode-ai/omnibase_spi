"""
Protocol for node configuration management in ONEX architecture.

Domain: Core configuration protocols for ONEX nodes
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolNodeConfiguration(Protocol):
    """
    Protocol for node configuration management.

    Provides standardized configuration access for all ONEX nodes
    without coupling to specific configuration implementations.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        config: "ProtocolNodeConfiguration" = get_node_config()

        # Get basic configuration values with defaults
        api_url = await config.get_config_value("api.base_url", "http://localhost:8080")
        timeout = await config.get_timeout_ms("api_call", 5000)

        # Domain-specific configuration access
        auth_settings = await config.get_security_config("authentication.enabled")
        perf_limits = await config.get_performance_config("memory.max_heap_mb")
        business_rules = await config.get_business_logic_config("workflow.max_retries")

        # Check configuration availability
        if config.has_config("feature.experimental"):
            experimental_mode = await config.get_config_value("feature.experimental")

        # Validate configurations
        is_valid = await config.validate_config("api.base_url")
        required_keys = ["database.host", "database.port", "api.key"]
        validation_results = await config.validate_required_configs(required_keys)

        # Get all configuration as dictionary
        all_configs = await config.get_all_config()
        print(f"Loaded {len(all_configs)} configuration items")

        # Get configuration schema for validation
        schema = await config.get_config_schema()
        ```

    Configuration Access Patterns:
        - Typed configuration access with default values
        - Domain-specific configuration separation (security, performance, business logic)
        - Timeout configuration for different operation types
        - Configuration validation and schema checking
        - Bulk configuration access and querying

    Key Features:
        - **Domain Separation**: Security, performance, and business logic configurations
        - **Type Safety**: Strong typing for configuration values
        - **Validation**: Built-in configuration validation with schema support
        - **Default Values**: Optional default values for missing configurations
        - **Async Support**: Asynchronous configuration loading and validation

    Configuration Domains:
        - **Security**: Authentication, authorization, encryption settings
        - **Performance**: Memory limits, CPU quotas, timeout values
        - **Business Logic**: Feature flags, workflow rules, retry policies
        - **Infrastructure**: Database connections, API endpoints, service URLs

    Error Handling:
        - Graceful handling of missing configurations
        - Structured error reporting for validation failures
        - Default value fallback for optional configurations
        - Schema validation with detailed error messages

    Performance Considerations:
        - Efficient configuration caching strategies
        - Lazy loading of configuration values
        - Bulk operations for multiple configuration access
        - Minimal overhead for configuration validation
    """

    async def get_config_value(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue":
        """Retrieve a configuration value by key with optional default.

        Args:
            key: The configuration key to look up (dot-notation supported).
            default: Optional default value if key is not found.

        Returns:
            The configuration value associated with the key, or the default if not found.
        """
        ...

    async def get_timeout_ms(
        self, timeout_type: str, default_ms: int | None = None
    ) -> int: ...

    async def get_security_config(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue": ...

    async def get_business_logic_config(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue": ...

    async def get_performance_config(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue": ...

    def has_config(self, key: str) -> bool: ...

    async def get_all_config(self) -> dict[str, "ContextValue"]: ...

    async def validate_config(self, config_key: str) -> bool: ...

    async def validate_required_configs(
        self, required_keys: list[str]
    ) -> dict[str, bool]: ...

    async def get_config_schema(self) -> dict[str, "ContextValue"]: ...


@runtime_checkable
class ProtocolNodeConfigurationProvider(Protocol):
    """
    Protocol for configuration provider implementations.

    Allows different configuration backends (environment, files, databases)
    to be used interchangeably through dependency injection.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        provider: "ProtocolNodeConfigurationProvider" = get_config_provider()

        # Load configuration for a specific node
        config = await provider.load_configuration(
            node_type="workflow_orchestrator",
            node_id="node-001"
        )

        # Reload configuration (e.g., after config file changes)
        await provider.reload_configuration()

        # Validate configuration integrity
        is_valid = await provider.validate_configuration()
        if not is_valid:
            # Handle configuration validation errors
            raise ConfigurationError("Invalid configuration detected")

        # Dynamic configuration updates
        async def watch_configuration_changes():
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                await provider.reload_configuration()
                new_config = await provider.load_configuration("workflow_orchestrator", "node-001")
                # Handle configuration changes
        ```

    Provider Patterns:
        - Node-specific configuration loading with type and ID
        - Dynamic configuration reloading for hot updates
        - Configuration validation and integrity checking
        - Support for multiple configuration backends

    Key Features:
        - **Multi-Backend Support**: Environment variables, files, databases, etc.
        - **Node Isolation**: Separate configurations per node instance
        - **Hot Reload**: Dynamic configuration updates without restart
        - **Validation**: Built-in configuration validation
        - **Dependency Injection**: Pluggable backend implementations

    Backend Types:
        - **Environment**: Environment variable-based configuration
        - **File-based**: JSON, YAML, TOML configuration files
        - **Database**: Configuration stored in database tables
        - **Service**: Configuration from external configuration services
        - **Hybrid**: Multiple sources with precedence rules

    Lifecycle Management:
        - Configuration loading on node startup
        - Validation before node activation
        - Hot reload for runtime configuration changes
        - Graceful degradation on configuration errors

    Error Handling:
        - Configuration source availability checking
        - Schema validation with detailed error reporting
        - Fallback mechanisms for missing configurations
        - Configuration rollback on validation failures
    """

    async def load_configuration(
        self, node_type: str, node_id: str
    ) -> ProtocolNodeConfiguration: ...

    async def reload_configuration(self) -> None: ...

    async def validate_configuration(self) -> bool: ...


@runtime_checkable
class ProtocolConfigurationError(Protocol):
    """
    Protocol for configuration-related errors.

    Provides structured error information for configuration failures
    with support for error formatting and context details.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        error: "ProtocolConfigurationError" = ConfigError(
            message="Missing required configuration",
            key="database.host",
            source="environment"
        )

        # String representation for logging
        error_msg = str(error)
        # "Config error in environment: Missing required configuration (key: database.host)"

        # Check if error is for specific configuration key
        if error.is_key_error("database.host"):
            # Handle specific key error - maybe provide default value
            fallback_host = "localhost"
            await set_default_config("database.host", fallback_host)

        # Get detailed error context for debugging
        context = await error.get_error_context()
        print(f"Error context: {context}")
        # {
        #     "message": "Missing required configuration",
        #     "key": "database.host",
        #     "source": "environment",
        #     "suggestion": "Set DATABASE_HOST environment variable"
        # }

        # Error handling in configuration loading
        try:
            config = await provider.load_configuration("database", "primary")
        except ConfigurationError as e:
            if e.is_key_error("connection.timeout"):
                # Handle timeout configuration error
                log_warning("Using default timeout configuration")
                config = get_default_timeout_config()
            else:
                # Re-throw non-timeout configuration errors
                raise
        ```

    Error Structure:
        - Descriptive error messages for human readability
        - Configuration key identification for precise error targeting
        - Source tracking for error origin identification
        - Context information for debugging and troubleshooting

    Key Features:
        - **Structured Errors**: Consistent error format across configuration sources
        - **Key Identification**: Precise identification of problematic configuration keys
        - **Source Tracking**: Clear indication of configuration source (environment, file, etc.)
        - **Context Information**: Additional debugging information and suggestions
        - **Type Safety**: Strong typing for error handling patterns

    Error Types:
        - **Missing Configuration**: Required configuration key not found
        - **Invalid Format**: Configuration value doesn't match expected format
        - **Type Mismatch**: Configuration value type doesn't match expected type
        - **Validation Failure**: Configuration fails schema or business rule validation
        - **Source Error**: Configuration source unavailable or inaccessible

    Error Handling Patterns:
        - Graceful degradation with fallback values
        - Error logging with full context information
        - User-friendly error messages with suggestions
        - Programmatic error classification and handling
        - Error chaining for root cause analysis

    Debugging Support:
        - Detailed error context including source and suggestions
        - Error categorization for targeted handling
        - Stack trace preservation for debugging
        - Configuration path information for file-based errors
    """

    message: str
    key: str | None
    source: str

    def __str__(self) -> str: ...

    def is_key_error(self, config_key: str) -> bool: ...

    async def get_error_context(self) -> dict[str, str | None]: ...

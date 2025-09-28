"""
Protocol for node configuration management in ONEX architecture.

Domain: Core configuration protocols for ONEX nodes
"""

from typing import Protocol, runtime_checkable

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
        config: "ProtocolNodeConfiguration" = get_node_config()

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

    async def get_config_value(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

    async def get_timeout_ms(
        self, timeout_type: str, default_ms: int | None = None
    ) -> int: ...

    async def get_security_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

    async def get_business_logic_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

    async def get_performance_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

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
        error: "ProtocolConfigurationError" = ConfigError(
            message="Missing required configuration",
            key="database.host",
            source="environment"
        )

        # String representation
        error_msg = str(error)  # "Config error in environment: Missing required configuration (key: database.host)"

        # Check if error is for specific key
        if error.is_key_error("database.host"):
            # Handle specific key error
        ```
    """

    message: str
    key: str | None
    source: str

    def __str__(self) -> str: ...

    def is_key_error(self, config_key: str) -> bool: ...

    async def get_error_context(self) -> dict[str, str | None]: ...

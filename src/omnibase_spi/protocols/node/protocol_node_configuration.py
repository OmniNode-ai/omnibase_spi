# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

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

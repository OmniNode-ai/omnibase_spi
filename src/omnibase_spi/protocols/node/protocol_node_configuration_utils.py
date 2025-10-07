"""
Protocol for node configuration utilities in ONEX architecture.

Domain: Node - Configuration utility protocols for ONEX nodes
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_spi.protocols.node.protocol_node_configuration import (
        ProtocolNodeConfiguration,
    )


@runtime_checkable
class ProtocolUtilsNodeConfiguration(Protocol):
    """
    Protocol for node configuration utility operations.

    Provides standardized configuration access patterns that nodes
    can use without coupling to specific utility implementations.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        config_utils: "ProtocolUtilsNodeConfiguration" = get_config_utils()

        # Get base configuration
        config = await config_utils.get_configuration()

        # Get timeout values
        timeout = await config_utils.get_timeout_ms("api_call", 5000)
        read_timeout = await config_utils.get_timeout_ms("database_read", 10000)

        # Access security configurations
        api_key = await config_utils.get_security_config("api.key")
        encryption_key = await config_utils.get_security_config("encryption.key")

        # Performance configuration
        max_memory = await config_utils.get_performance_config("memory.max_mb")
        cpu_limit = await config_utils.get_performance_config("cpu.cores")

        # Business logic configuration
        feature_flags = await config_utils.get_business_logic_config("features.enabled")
        business_rules = await config_utils.get_business_logic_config("rules.validation")

        # Validate correlation IDs
        is_valid = await config_utils.validate_correlation_id("550e8400-e29b-41d4-a716-446655440000")
        ```

    Configuration Access Patterns:
        - Typed configuration access with default values
        - Security-specific configuration isolation
        - Performance parameter management
        - Business logic configuration separation
        - Correlation ID validation and format checking

    Key Features:
        - Secure configuration access with proper isolation
        - Type-safe configuration value retrieval
        - Default value support for optional configurations
        - Validation and format checking
        - Integration with ONEX configuration management
    """

    async def get_configuration(self) -> "ProtocolNodeConfiguration":
        """
        Get the base node configuration object.

        Returns:
            ProtocolNodeConfiguration: Base configuration interface
        """
        ...

    async def get_timeout_ms(
        self, timeout_type: str, default_ms: int | None = None
    ) -> int:
        """
        Get timeout configuration in milliseconds.

        Args:
            timeout_type: Type of timeout (e.g., "api_call", "database_read")
            default_ms: Default timeout value if not configured

        Returns:
            int: Timeout value in milliseconds

        Example:
            timeout = await config_utils.get_timeout_ms("api_call", 5000)
            # Returns 5000 if "api_call" timeout not configured
        """
        ...

    async def get_security_config(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue":
        """
        Get security-related configuration values.

        Args:
            key: Configuration key (e.g., "api.key", "encryption.key")
            default: Default value if key not found

        Returns:
            ContextValue: Security configuration value

        Example:
            api_key = await config_utils.get_security_config("api.key")
            # Returns None if API key not configured
        """
        ...

    async def get_performance_config(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue":
        """
        Get performance-related configuration values.

        Args:
            key: Configuration key (e.g., "memory.max_mb", "cpu.cores")
            default: Default value if key not found

        Returns:
            ContextValue: Performance configuration value

        Example:
            max_memory = await config_utils.get_performance_config("memory.max_mb")
            # Returns configured memory limit or default
        """
        ...

    async def get_business_logic_config(
        self, key: str, default: "ContextValue | None" = None
    ) -> "ContextValue":
        """
        Get business logic configuration values.

        Args:
            key: Configuration key (e.g., "features.enabled", "rules.validation")
            default: Default value if key not found

        Returns:
            ContextValue: Business logic configuration value

        Example:
            features = await config_utils.get_business_logic_config("features.enabled")
            # Returns list of enabled features
        """
        ...

    async def validate_correlation_id(self, correlation_id: str) -> bool:
        """
        Validate correlation ID format and structure.

        Args:
            correlation_id: Correlation ID string to validate

        Returns:
            bool: True if correlation ID is valid, False otherwise

        Example:
            is_valid = await config_utils.validate_correlation_id(
                "550e8400-e29b-41d4-a716-446655440000"
            )
            # Returns True for valid UUID format
        """
        ...

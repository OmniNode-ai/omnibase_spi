"""
Protocol for node configuration utilities in ONEX architecture.

Domain: Core configuration utility protocols for ONEX nodes
"""

from typing import Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.core.protocol_node_configuration import (
    ProtocolNodeConfiguration,
)
from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolUtilsNodeConfiguration(Protocol):
    """
    Protocol for node configuration utility operations.

    Provides standardized configuration access patterns that nodes
    can use without coupling to specific utility implementations.
    """

    def get_configuration(self) -> ProtocolNodeConfiguration:
        """
        Get node configuration instance.

        Returns:
            Configuration instance for the node

        Raises:
            ConfigurationError: If configuration cannot be retrieved
        """
        ...

    def get_timeout_ms(self, timeout_type: str, default_ms: int | None = None) -> int:
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
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue:
        """
        Get security configuration value.

        Args:
            key: Security configuration key
            default: Default value if key not found

        Returns:
            Security configuration value
        """
        ...

    def get_performance_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue:
        """
        Get performance configuration value.

        Args:
            key: Performance configuration key
            default: Default value if key not found

        Returns:
            Performance configuration value
        """
        ...

    def get_business_logic_config(
        self, key: str, default: ContextValue | None = None
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

    async def validate_correlation_id(self, correlation_id: str) -> bool:
        """
        Validate correlation ID format using configuration.

        Args:
            correlation_id: Correlation ID to validate

        Returns:
            True if valid, False otherwise
        """
        ...

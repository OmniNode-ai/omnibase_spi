"""
Protocol for node configuration utilities in ONEX architecture.

Domain: Core configuration utility protocols for ONEX nodes
"""

from typing import Protocol, runtime_checkable

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

    async def get_configuration(self) -> ProtocolNodeConfiguration: ...

    async def get_timeout_ms(
        self, timeout_type: str, default_ms: int | None = None
    ) -> int: ...

    async def get_security_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

    async def get_performance_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

    async def get_business_logic_config(
        self, key: str, default: ContextValue | None = None
    ) -> ContextValue: ...

    async def validate_correlation_id(self, correlation_id: str) -> bool: ...

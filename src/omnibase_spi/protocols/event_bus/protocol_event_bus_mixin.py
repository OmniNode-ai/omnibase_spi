"""
Protocol definitions extracted from Event Bus Mixin.

Provides clean protocol interfaces for event bus operations without
implementation dependencies or mixin complexity.
"""

from typing import TYPE_CHECKING, Optional, Protocol, Union, runtime_checkable

# Runtime imports needed for forward references in method signatures
from omnibase_spi.protocols.types.protocol_core_types import LiteralLogLevel
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

if TYPE_CHECKING:
    # No types needed here currently
    pass


@runtime_checkable
class ProtocolEventBusBase(Protocol):
    """
    Base protocol for event bus operations.

    Defines common event publishing interface that both synchronous
    and asynchronous event buses must implement. Provides unified
    event publishing capabilities across different execution patterns.

    Key Features:
        - Unified event publishing interface
        - Support for both sync and async implementations
        - Compatible with dependency injection patterns
    """

    async def publish(self, event: ProtocolEventMessage) -> None: ...


@runtime_checkable
class ProtocolSyncEventBus(ProtocolEventBusBase, Protocol):
    """
    Protocol for synchronous event bus operations.

    Defines synchronous event publishing interface for
    event bus implementations that operate synchronously.
    Inherits from ProtocolEventBusBase for unified interface.

    Key Features:
        - Synchronous event publishing
        - Basic publish interface
        - Compatible with sync event processing
    """

    def publish_sync(self, event: ProtocolEventMessage) -> None:
        """
        Publish event synchronously.

        Args:
            event: Event message to publish

        Raises:
            ValueError: If event format is invalid
            RuntimeError: If event bus is unavailable
        """
        ...


@runtime_checkable
class ProtocolAsyncEventBus(ProtocolEventBusBase, Protocol):
    """
    Protocol for asynchronous event bus operations.

    Defines asynchronous event publishing interface for
    event bus implementations that operate asynchronously.
    Inherits from ProtocolEventBusBase for unified interface.

    Key Features:
        - Asynchronous event publishing
        - Async/await compatibility
        - Non-blocking event processing
    """

    async def publish_async(self, event: ProtocolEventMessage) -> None:
        """
        Publish event asynchronously with dedicated async method.

        Args:
            event: Event message to publish

        Raises:
            ValueError: If event format is invalid
            RuntimeError: If event bus is unavailable
        """
        ...


@runtime_checkable
class ProtocolRegistryWithBus(Protocol):
    """
    Protocol for registry that provides event bus access.

    Defines interface for service registries that provide
    access to event bus instances for dependency injection.

    Key Features:
        - Event bus dependency injection
        - Registry-based service location
        - Support for both sync and async event buses
    """

    event_bus: ProtocolEventBusBase | None

    def validate_registry_bus(self) -> bool:
        """Validate registrywithbus data integrity and consistency."""
        ...

    def has_bus_access(self) -> bool:
        """Check if registrywithbus bus access."""
        ...


@runtime_checkable
class ProtocolLogEmitter(Protocol):
    """
    Protocol for structured log emission.

    Defines interface for components that can emit structured
    log events with typed data and log levels.

    Key Features:
        - Structured logging support
        - Log level management
        - Typed log data
    """

    def emit_log_event(
        self,
        level: LiteralLogLevel,
        message: str,
        data: dict[str, str | int | float | bool],
    ) -> None:
        """
        Emit structured log event.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, etc.)
            message: Log message
            data: Structured log data with typed values

        Note:
            Implementations should support structured logging
                ...
            with proper serialization of typed data.
        """
        ...

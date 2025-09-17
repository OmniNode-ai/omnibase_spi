"""
Protocol for Event Bus Context Managers.

Provides async context management protocols for event bus lifecycle management.
Abstracts lifecycle management for event bus resources (e.g., Kafka, RedPanda).
"""

from typing import TYPE_CHECKING, Protocol, TypeVar, Union, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus

TEventBus = TypeVar("TEventBus", bound="ProtocolEventBus", covariant=True)


@runtime_checkable
class ProtocolEventBusContextManager(Protocol[TEventBus]):
    """
    Protocol for async context managers that yield a ProtocolEventBus-compatible object.

    Provides lifecycle management for event bus resources with proper cleanup.
    Implementations must support async context management and return a ProtocolEventBus on enter.

    Key Features:
        - Async context manager support (__aenter__, __aexit__)
        - Configuration-based initialization
        - Resource lifecycle management
        - Proper cleanup and error handling

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class KafkaEventBusContextManager:
            async def __aenter__(self) -> KafkaEventBus:
                # Implementation creates and connects event bus
                event_bus = KafkaEventBus(self.config)
                await event_bus.connect()
                return event_bus

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                # Implementation cleans up resources
                if hasattr(self, '_event_bus'):
                    await self._event_bus.close()

        # Usage in application code
        async with context_manager_impl as event_bus:
            await event_bus.publish(topic="test", key=None, value=b"data", headers={...})
        ```
    """

    async def __aenter__(self) -> TEventBus:
        """
        Enter async context and return configured event bus instance.

        Returns:
            Configured and connected event bus instance

        Raises:
            ConnectionError: If event bus connection fails
            ValueError: If configuration is invalid
            RuntimeError: If resource initialization fails
        """
        ...

    async def __aexit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: object,
    ) -> None:
        """
        Exit async context and clean up event bus resources.

        Args:
            exc_type: Exception type if context exits with exception
            exc_val: Exception value if context exits with exception
            exc_tb: Exception traceback if context exits with exception

        Note:
            Should properly close connections and clean up resources
            regardless of whether an exception occurred.
        """
        ...

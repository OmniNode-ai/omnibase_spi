"""
Redpanda Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Redpanda backend implementations.
Redpanda is Kafka API compatible with optimized defaults.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Optional,
    Protocol,
    runtime_checkable,
)

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolEventMessage,
    )

# Type aliases to avoid namespace violations
EventBusHeaders = Any  # Generic headers type
EventMessage = Any  # Generic event message type
KafkaConfig = Any  # Generic Kafka configuration type


@runtime_checkable
class ProtocolRedpandaAdapter(Protocol):
    """
    Protocol for Redpanda event bus adapter implementations.

    Provides Redpanda-specific optimizations while maintaining Kafka protocol
    compatibility with optimized defaults and configurations.
    """

    @property
    def redpanda_optimized_defaults(self) -> dict[str, "ContextValue"]: ...

    # Kafka adapter interface methods and properties
    @property
    def bootstrap_servers(self) -> str: ...

    @property
    def environment(self) -> str: ...

    @property
    def group(self) -> str: ...

    @property
    def config(self) -> Optional[KafkaConfig]: ...

    @property
    def kafka_config(self) -> KafkaConfig: ...

    async def build_topic_name(self, topic: str) -> str: ...

    # Core event bus adapter interface methods
    async def publish(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: EventBusHeaders,
    ) -> None: ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[["ProtocolEventMessage"], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]: ...

    async def close(self) -> None: ...

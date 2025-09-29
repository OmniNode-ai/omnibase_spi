"""
Kafka Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Kafka backend implementations.
Defines the contract for Kafka-specific event bus adapters.
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

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolEventMessage,
    )

# Type aliases to avoid namespace violations
EventBusHeaders = Any  # Generic headers type
EventMessage = Any  # Generic event message type


@runtime_checkable
class ProtocolKafkaConfig(Protocol):
    """Protocol for Kafka configuration parameters."""

    security_protocol: str
    sasl_mechanism: str
    sasl_username: str | None
    sasl_password: str | None
    ssl_cafile: str | None
    auto_offset_reset: str
    enable_auto_commit: bool
    session_timeout_ms: int
    request_timeout_ms: int


@runtime_checkable
class ProtocolKafkaAdapter(Protocol):
    """
    Protocol for Kafka event bus adapter implementations.

    Provides Kafka-specific configuration and connection management protocols
    along with the core event bus adapter interface.
    """

    @property
    def bootstrap_servers(self) -> str: ...

    @property
    def environment(self) -> str: ...

    @property
    def group(self) -> str: ...

    @property
    def config(self) -> ProtocolKafkaConfig | None: ...

    @property
    def kafka_config(self) -> ProtocolKafkaConfig: ...

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

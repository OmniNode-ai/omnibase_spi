# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.128231'
# description: Stamped by ToolPython
# entrypoint: python://protocol_event_bus
# hash: d08b73065d9e8de6ac3b18881f8669d08f07ca6678ec78d1f0cdb96e3b9016eb
# last_modified_at: '2025-05-29T14:14:00.220362+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_event_bus.py
# namespace: python://omnibase.protocol.protocol_event_bus
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2d9c79c5-6422-462b-b10c-e080a10c1d42
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Callable, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.event_bus_types import (
    ProtocolEventBusCredentials,
    ProtocolOnexEvent,
)


@runtime_checkable
class ProtocolEventBus(Protocol):
    """
    Canonical protocol for ONEX event bus (runtime/ placement).
    Defines publish/subscribe interface for event emission and handling.
    All event bus implementations must conform to this interface.
    Supports both synchronous and asynchronous methods for maximum flexibility.
    Implementations may provide either or both, as appropriate.
    Optionally supports clear() for test/lifecycle management.

    # TODO: Future: Add pluggable backends (Kafka, message persistence, authentication, multi-tenant support)
    """

    def __init__(
        self, credentials: Optional[ProtocolEventBusCredentials] = None, **kwargs: Any
    ):
        ...

    def publish(self, event: ProtocolOnexEvent) -> None:
        """
        Publish an event to the bus (synchronous).
        Args:
            event: ProtocolOnexEvent to emit
        """
        ...

    async def publish_async(self, event: ProtocolOnexEvent) -> None:
        """
        Publish an event to the bus (asynchronous).
        Args:
            event: ProtocolOnexEvent to emit
        """
        ...

    def subscribe(self, callback: Callable[[ProtocolOnexEvent], None]) -> None:
        """
        Subscribe a callback to receive events (synchronous).
        Args:
            callback: Callable invoked with each ProtocolOnexEvent
        """
        ...

    async def subscribe_async(
        self, callback: Callable[[ProtocolOnexEvent], None]
    ) -> None:
        """
        Subscribe a callback to receive events (asynchronous).
        Args:
            callback: Callable invoked with each ProtocolOnexEvent
        """
        ...

    def unsubscribe(self, callback: Callable[[ProtocolOnexEvent], None]) -> None:
        """
        Unsubscribe a previously registered callback (synchronous).
        Args:
            callback: Callable to remove
        """
        ...

    async def unsubscribe_async(
        self, callback: Callable[[ProtocolOnexEvent], None]
    ) -> None:
        """
        Unsubscribe a previously registered callback (asynchronous).
        Args:
            callback: Callable to remove
        """
        ...

    def clear(self) -> None:
        """
        Remove all subscribers from the event bus. Optional, for test/lifecycle management.
        """
        ...

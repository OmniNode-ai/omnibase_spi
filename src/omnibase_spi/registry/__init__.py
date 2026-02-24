"""SPI Event Registry — canonical event-type-to-topic mapping.

Provides the runtime-accessible registry that maps every known
``event_type`` string to its wire topic, schema version, partition-key
fields, and the SPI producer protocol responsible for emitting it.

Exports:
    EventRegistryEntry: Named tuple describing one registered event.
    EVENT_REGISTRY: The singleton registry dict keyed by event_type.
"""

from omnibase_spi.registry.event_registry import EVENT_REGISTRY, EventRegistryEntry

__all__ = ["EVENT_REGISTRY", "EventRegistryEntry"]

# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Domain plugin configuration model.

The ModelDomainPluginConfig dataclass for passing
configuration to domain plugins during lifecycle hooks.

Thread Safety:
    This is a mutable dataclass. The dispatch_engine field may be set
    after initial construction when the MessageDispatchEngine is created.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_core.container import ModelONEXContainer


@dataclass
class ModelDomainPluginConfig:
    """Configuration passed to domain plugins during lifecycle hooks.

    This model provides all the context a domain plugin needs to initialize
    its resources and wire its handlers. The kernel creates this config
    and passes it to each plugin during bootstrap.

    Attributes:
        container: The ONEX container for dependency injection.
        event_bus: The event bus instance (InMemoryEventBus or KafkaEventBus).
        correlation_id: Correlation ID for distributed tracing.
        input_topic: The input topic for event consumers.
        output_topic: The output topic for event publishers.
        consumer_group: The consumer group for Kafka consumers.
        dispatch_engine: The MessageDispatchEngine for dispatcher wiring
            (set after engine creation, may be None).
        node_identity: Typed node identity for structured consumer group naming.
        kafka_bootstrap_servers: Kafka bootstrap servers string.
        output_topic_map: Per-event-type topic routing from contract published_events.
    """

    container: ModelONEXContainer
    event_bus: object
    correlation_id: UUID
    input_topic: str
    output_topic: str
    consumer_group: str

    dispatch_engine: object | None = None
    node_identity: object | None = None
    kafka_bootstrap_servers: str | None = None
    output_topic_map: dict[str, str] | None = None


__all__ = ["ModelDomainPluginConfig"]

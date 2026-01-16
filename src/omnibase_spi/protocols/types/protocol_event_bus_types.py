"""
Event bus protocol types for ONEX SPI interfaces.

Domain: Event-driven architecture protocols
"""

from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralBaseStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

# Re-export agent-related types for backward compatibility
from omnibase_spi.protocols.types.protocol_event_agent_types import (
    ProtocolAgentEvent,
    ProtocolCompletionData,
    ProtocolEventBusAgentStatus,
    ProtocolProgressUpdate,
    ProtocolWorkResult,
)


@runtime_checkable
class ProtocolEventData(Protocol):
    """
    Protocol for event data values supporting validation and serialization.

    Base protocol for all event data types ensuring they can be validated
    before being sent over the event bus. Implementations must verify data
    integrity and format compatibility with transport mechanisms.

    Example:
        ```python
        class CustomEventData:
            '''Custom event data implementation.'''

            async def validate_for_transport(self) -> bool:
                # Validate data can be serialized
                return True

        data = CustomEventData()
        assert isinstance(data, ProtocolEventData)
        is_valid = await data.validate_for_transport()
        ```
    """

    async def validate_for_transport(self) -> bool:
        """Validate that this data can be serialized and transported.

        Returns:
            True if the data is valid for transport, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventStringData(ProtocolEventData, Protocol):
    """
    Protocol for string-based event data.

    Represents string values in event payloads with transport validation.
    Used for simple text data, identifiers, and messages in events.

    Attributes:
        value: The string value to be transported.

    Example:
        ```python
        class StatusMessage:
            '''String message for status events.'''

            value = "Order processing completed successfully"

            async def validate_for_transport(self) -> bool:
                return isinstance(self.value, str) and len(self.value) < 10000

        msg = StatusMessage()
        assert isinstance(msg, ProtocolEventStringData)
        ```
    """

    value: str


@runtime_checkable
class ProtocolEventStringListData(ProtocolEventData, Protocol):
    """
    Protocol for string list event data.

    Represents lists of strings in event payloads. Used for tags,
    categories, recipient lists, and other multi-value string data.

    Attributes:
        value: List of string values to be transported.

    Example:
        ```python
        class TagList:
            '''List of tags for an event.'''

            value = ["order", "processing", "priority-high"]

            async def validate_for_transport(self) -> bool:
                return all(isinstance(v, str) for v in self.value)

        tags = TagList()
        assert isinstance(tags, ProtocolEventStringListData)
        ```
    """

    value: list[str]


@runtime_checkable
class ProtocolEventStringDictData(ProtocolEventData, Protocol):
    """
    Protocol for string dictionary event data.

    Represents key-value string mappings in event payloads. Used for
    metadata, configuration, and structured context information.

    Attributes:
        value: Dictionary mapping string keys to context values.

    Example:
        ```python
        class EventMetadata:
            '''Metadata dictionary for an event.'''

            value = {"source": "order-service", "environment": "production"}

            async def validate_for_transport(self) -> bool:
                return all(isinstance(k, str) for k in self.value.keys())

        metadata = EventMetadata()
        assert isinstance(metadata, ProtocolEventStringDictData)
        ```
    """

    value: dict[str, "ContextValue"]


EventStatus = LiteralBaseStatus
LiteralAuthStatus = Literal["authenticated", "unauthenticated", "expired", "invalid"]
LiteralEventPriority = Literal["low", "normal", "high", "critical"]
MessageKey = bytes | None


@runtime_checkable
class ProtocolEvent(Protocol):
    """
    Protocol for event objects.

    Represents a complete event with type, data, and metadata for
    event-driven communication. Forms the core of the ONEX event bus
    messaging system.

    Attributes:
        event_type: Type identifier for the event (e.g., "order.created").
        event_data: Dictionary of typed event data values.
        correlation_id: UUID linking related events together.
        timestamp: When the event was created.
        source: Identifier of the event source service.

    Example:
        ```python
        class OrderCreatedEvent:
            '''Event for order creation.'''

            event_type = "order.created"
            event_data = {"order_id": StringData("ORD-123")}
            correlation_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            timestamp = datetime.now()
            source = "order-service"

            async def validate_event(self) -> bool:
                return self.event_type and self.correlation_id

        event = OrderCreatedEvent()
        assert isinstance(event, ProtocolEvent)
        ```
    """

    event_type: str
    event_data: dict[str, "ProtocolEventData"]
    correlation_id: UUID
    timestamp: "ProtocolDateTime"
    source: str

    async def validate_event(self) -> bool:
        """Validate that this event is well-formed and complete.

        Returns:
            True if the event is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventResult(Protocol):
    """
    Protocol for event processing results.

    Reports the outcome of event processing including success/failure
    status, timing information, and error details. Used for acknowledgment
    and error handling in event consumers.

    Attributes:
        success: Whether event processing succeeded.
        event_id: UUID of the processed event.
        processing_time: Processing duration in seconds.
        error_message: Error details if processing failed.

    Example:
        ```python
        class EventProcessingResult:
            '''Result of processing an order event.'''

            success = True
            event_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            processing_time = 0.045
            error_message = None

            async def validate_result(self) -> bool:
                return self.event_id is not None

        result = EventProcessingResult()
        assert isinstance(result, ProtocolEventResult)
        ```
    """

    success: bool
    event_id: UUID
    processing_time: float
    error_message: str | None

    async def validate_result(self) -> bool:
        """Validate that this result is well-formed.

        Returns:
            True if the result is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolSecurityContext(Protocol):
    """
    Protocol for security context objects.

    Provides authentication and authorization context for event processing.
    Used to enforce access control and audit event handlers.

    Attributes:
        user_id: Authenticated user identifier (None if unauthenticated).
        permissions: List of permission strings the user has.
        auth_status: Current authentication status.
        token_expires_at: Token expiration timestamp if applicable.

    Example:
        ```python
        class UserSecurityContext:
            '''Security context for an authenticated user.'''

            user_id = "user_123"
            permissions = ["events:read", "events:write", "orders:read"]
            auth_status = "authenticated"
            token_expires_at = datetime.now() + timedelta(hours=1)

            async def validate_security_context(self) -> bool:
                return self.auth_status == "authenticated"

        ctx = UserSecurityContext()
        assert isinstance(ctx, ProtocolSecurityContext)
        ```
    """

    user_id: str | None
    permissions: list[str]
    auth_status: LiteralAuthStatus
    token_expires_at: "ProtocolDateTime | None"

    async def validate_security_context(self) -> bool:
        """Validate that this security context is valid and authorized.

        Returns:
            True if the security context is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventSubscription(Protocol):
    """
    Protocol for event subscriptions.

    Represents a subscription to specific event types with optional
    filtering. Used for managing event consumers and routing.

    Attributes:
        event_type: Type of events to receive (supports wildcards).
        subscriber_id: Unique identifier for the subscriber.
        filter_criteria: Additional filters to apply to events.
        is_active: Whether the subscription is currently active.

    Example:
        ```python
        class OrderEventSubscription:
            '''Subscription to order events.'''

            event_type = "order.*"
            subscriber_id = "order-processor-01"
            filter_criteria = {"region": "us-east"}
            is_active = True

            async def validate_subscription(self) -> bool:
                return self.event_type and self.subscriber_id

        sub = OrderEventSubscription()
        assert isinstance(sub, ProtocolEventSubscription)
        ```
    """

    event_type: str
    subscriber_id: str
    filter_criteria: dict[str, "ContextValue"]
    is_active: bool

    async def validate_subscription(self) -> bool:
        """Validate that this subscription is properly configured.

        Returns:
            True if the subscription is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventBusSystemEvent(Protocol):
    """
    Protocol for ONEX event bus system events.

    Extended event protocol with full metadata support for ONEX platform
    events over the event bus. Includes payload, correlation tracking,
    and rich metadata for cross-service communication.

    Note:
        For simple state management events without correlation tracking,
        use ProtocolStateSystemEvent from protocol_state_types.

    Attributes:
        event_id: Unique identifier for this event.
        event_type: Type identifier (e.g., "node.started").
        timestamp: Event creation timestamp.
        source: Service or component that emitted the event.
        payload: Typed event payload data.
        correlation_id: UUID for correlating related events.
        metadata: Additional event metadata.

    Example:
        ```python
        class NodeStartedEvent:
            '''Event emitted when a node starts.'''

            event_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            event_type = "node.started"
            timestamp = datetime.now()
            source = "compute-node-01"
            payload = {"node_type": StringData("COMPUTE")}
            correlation_id = UUID("660e8400-e29b-41d4-a716-446655440001")
            metadata = {"version": StringData("1.0.0")}

            async def validate_onex_event(self) -> bool:
                return self.event_id and self.event_type

        event = NodeStartedEvent()
        assert isinstance(event, ProtocolEventBusSystemEvent)
        ```
    """

    event_id: UUID
    event_type: str
    timestamp: "ProtocolDateTime"
    source: str
    payload: dict[str, "ProtocolEventData"]
    correlation_id: UUID
    metadata: dict[str, "ProtocolEventData"]

    async def validate_onex_event(self) -> bool:
        """Validate that this ONEX event is well-formed and complete.

        Returns:
            True if the ONEX event is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventBusConnectionCredentials(Protocol):
    """
    Protocol for event bus connection credential models with connection parameters.

    Provides connection credentials and configuration for event bus
    clients. Supports RabbitMQ-style virtual hosts and connection tuning.

    Attributes:
        username: Authentication username.
        password: Authentication password.
        host: Event bus server hostname.
        port: Event bus server port.
        virtual_host: Virtual host for namespace isolation.
        connection_timeout: Connection timeout in seconds.
        heartbeat: Heartbeat interval in seconds.

    Example:
        ```python
        class RabbitMQCredentials:
            '''Credentials for RabbitMQ connection.'''

            username = "onex-producer"
            password = "secret"
            host = "rabbitmq.example.com"
            port = 5672
            virtual_host = "/onex"
            connection_timeout = 30
            heartbeat = 60

        creds = RabbitMQCredentials()
        assert isinstance(creds, ProtocolEventBusConnectionCredentials)
        ```
    """

    username: str
    password: str
    host: str
    port: int
    virtual_host: str | None
    connection_timeout: int
    heartbeat: int


@runtime_checkable
class ProtocolEventHeaders(Protocol):
    """
    Protocol for ONEX event bus message headers.

    Standardized headers for ONEX event bus messages ensuring strict
    interoperability across all agents and preventing integration failures.
    Includes tracing, routing, and retry configuration.

    Attributes:
        content_type: MIME type of the message body.
        correlation_id: UUID for correlating related messages.
        message_id: Unique identifier for this message.
        timestamp: Message creation timestamp.
        source: Service that produced the message.
        event_type: Type identifier for the event.
        schema_version: Version of the message schema.
        destination: Optional target destination.
        trace_id: Distributed tracing trace ID.
        span_id: Distributed tracing span ID.
        parent_span_id: Parent span for trace hierarchy.
        operation_name: Name of the operation being traced.
        priority: Message priority level.
        routing_key: Key for message routing.
        partition_key: Key for partition assignment.
        retry_count: Current retry attempt number.
        max_retries: Maximum retry attempts allowed.
        ttl_seconds: Message time-to-live in seconds.

    Example:
        ```python
        class OrderEventHeaders:
            '''Headers for an order event message.'''

            content_type = "application/json"
            correlation_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            message_id = UUID("660e8400-e29b-41d4-a716-446655440001")
            timestamp = datetime.now()
            source = "order-service"
            event_type = "order.created"
            schema_version = SemVer(1, 0, 0)
            destination = None
            trace_id = "abc123"
            span_id = "def456"
            parent_span_id = None
            operation_name = "create_order"
            priority = "normal"
            routing_key = "orders.us-east"
            partition_key = "customer-123"
            retry_count = 0
            max_retries = 3
            ttl_seconds = 3600

            async def validate_headers(self) -> bool:
                return self.correlation_id and self.event_type

        headers = OrderEventHeaders()
        assert isinstance(headers, ProtocolEventHeaders)
        ```
    """

    content_type: str
    correlation_id: UUID
    message_id: UUID
    timestamp: "ProtocolDateTime"
    source: str
    event_type: str
    schema_version: "ProtocolSemVer"
    destination: str | None
    trace_id: str | None
    span_id: str | None
    parent_span_id: str | None
    operation_name: str | None
    priority: "LiteralEventPriority | None"
    routing_key: str | None
    partition_key: str | None
    retry_count: int | None
    max_retries: int | None
    ttl_seconds: int | None

    async def validate_headers(self) -> bool:
        """Validate that these headers are well-formed and complete.

        Returns:
            True if the headers are valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventMessage(Protocol):
    """
    Protocol for ONEX event bus message objects.

    Defines the contract that all event message implementations must satisfy
    for Kafka/RedPanda compatibility following ONEX Messaging Design.
    Supports partitioning, offset tracking, and acknowledgment.

    Attributes:
        topic: Kafka topic the message belongs to.
        key: Optional message key for partitioning (bytes).
        value: Serialized message body as bytes.
        headers: Structured message headers.
        offset: Kafka offset (for consumed messages).
        partition: Kafka partition number.

    Example:
        ```python
        class KafkaMessage:
            '''Kafka message for order events.'''

            topic = "onex.orders.created"
            key = b"customer-123"
            value = b'{"order_id": "ORD-123", "amount": 99.99}'
            headers = OrderEventHeaders()
            offset = "1234567"
            partition = 3

            async def ack(self) -> None:
                # Acknowledge message processing
                pass

        msg = KafkaMessage()
        assert isinstance(msg, ProtocolEventMessage)
        await msg.ack()  # Acknowledge after processing
        ```
    """

    topic: str
    key: MessageKey
    value: bytes
    headers: "ProtocolEventHeaders"
    offset: str | None
    partition: int | None

    async def ack(self) -> None:
        """Acknowledge successful processing of this message.

        Commits the consumer offset for this message, indicating that
        processing completed successfully and the message should not
        be redelivered.

        Raises:
            SPIError: If acknowledgment fails.
        """
        ...


# Type alias for backward compatibility (must be after ProtocolEventMessage definition)
type EventMessage = ProtocolEventMessage


# Re-export all for backward compatibility
__all__ = [
    # Core event types (defined in this file)
    "EventStatus",
    "LiteralAuthStatus",
    "LiteralEventPriority",
    "MessageKey",
    # Agent types (re-exported from protocol_event_agent_types)
    "ProtocolAgentEvent",
    "ProtocolCompletionData",
    "ProtocolEvent",
    "ProtocolEventBusAgentStatus",
    "ProtocolEventBusConnectionCredentials",
    "ProtocolEventData",
    "ProtocolEventHeaders",
    "ProtocolEventMessage",
    "ProtocolEventResult",
    "ProtocolEventStringData",
    "ProtocolEventStringDictData",
    "ProtocolEventStringListData",
    "ProtocolEventSubscription",
    "ProtocolProgressUpdate",
    "ProtocolSecurityContext",
    "ProtocolEventBusSystemEvent",
    "ProtocolWorkResult",
]

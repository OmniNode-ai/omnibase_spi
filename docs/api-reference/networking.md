# Networking API Reference

## Overview

The ONEX networking protocols provide comprehensive communication infrastructure with HTTP clients, Kafka integration, circuit breakers, and communication bridges. These protocols enable robust distributed communication with resilience patterns and performance optimization.

## 🏗️ Protocol Architecture

The networking domain consists of **6 specialized protocols** that provide complete communication infrastructure:

### HTTP Client Protocol

```python
from omnibase_spi.protocols.networking import ProtocolHttpClient
from omnibase_spi.protocols.types.protocol_core_types import ContextValue

@runtime_checkable
class ProtocolHttpClient(Protocol):
    """
    Protocol for HTTP client operations.

    Provides comprehensive HTTP client functionality with
    advanced features for distributed system communication.

    Key Features:
        - HTTP/HTTPS request/response handling
        - Connection pooling and keep-alive
        - Request/response interceptors
        - Retry mechanisms and circuit breakers
        - Performance monitoring and metrics
        - Security and authentication
    """

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> ProtocolHttpResponse: ...

    async def post(
        self,
        url: str,
        data: ContextValue | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> ProtocolHttpResponse: ...

    async def put(
        self,
        url: str,
        data: ContextValue | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> ProtocolHttpResponse: ...

    async def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> ProtocolHttpResponse: ...

    async def patch(
        self,
        url: str,
        data: ContextValue | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> ProtocolHttpResponse: ...

    async def request(
        self,
        method: str,
        url: str,
        data: ContextValue | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> ProtocolHttpResponse: ...

    async def get_client_metrics(self) -> ProtocolHttpClientMetrics: ...

    async def configure_retry_policy(
        self, policy: ProtocolRetryPolicy
    ) -> bool: ...

    async def configure_circuit_breaker(
        self, breaker: ProtocolCircuitBreaker
    ) -> bool: ...
```

### HTTP Extended Protocol

```python
@runtime_checkable
class ProtocolHttpExtended(Protocol):
    """
    Protocol for extended HTTP client operations.

    Provides advanced HTTP functionality including streaming,
    WebSocket support, and advanced authentication.

    Key Features:
        - HTTP streaming and chunked responses
        - WebSocket connection management
        - Advanced authentication (OAuth, JWT, API keys)
        - Request/response compression
        - Connection multiplexing
        - Performance optimization
    """

    async def stream_request(
        self,
        method: str,
        url: str,
        data: ContextValue | None = None,
        headers: dict[str, str] | None = None,
        chunk_size: int = 8192,
    ) -> AsyncIterator[bytes]: ...

    async def websocket_connect(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        protocols: list[str] | None = None,
    ) -> ProtocolWebSocketConnection: ...

    async def authenticate_oauth2(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str | None = None,
    ) -> ProtocolOAuth2Token: ...

    async def authenticate_jwt(
        self,
        token: str,
        algorithm: str = "HS256",
    ) -> ProtocolJWTClaims: ...

    async def compress_request(
        self,
        data: ContextValue,
        compression_type: LiteralCompressionType,
    ) -> bytes: ...

    async def decompress_response(
        self,
        data: bytes,
        compression_type: LiteralCompressionType,
    ) -> ContextValue: ...

    async def get_connection_pool_stats(
        self,
    ) -> ProtocolConnectionPoolStats: ...
```

### Kafka Client Protocol

```python
@runtime_checkable
class ProtocolKafkaClient(Protocol):
    """
    Protocol for Kafka client operations.

    Provides comprehensive Kafka integration with
    producer and consumer functionality.

    Key Features:
        - Kafka producer and consumer operations
        - Topic management and partitioning
        - Consumer group coordination
        - Offset management and commit strategies
        - Schema registry integration
        - Performance monitoring
    """

    async def create_producer(
        self, config: ProtocolKafkaProducerConfig
    ) -> str: ...

    async def create_consumer(
        self, config: ProtocolKafkaConsumerConfig
    ) -> str: ...

    async def produce_message(
        self,
        producer_id: str,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: dict[str, bytes] | None = None,
        partition: int | None = None,
    ) -> ProtocolKafkaProduceResult: ...

    async def consume_messages(
        self,
        consumer_id: str,
        topics: list[str],
        timeout_ms: int = 1000,
    ) -> list[ProtocolKafkaMessage]: ...

    async def commit_offsets(
        self, consumer_id: str, offsets: dict[str, int]
    ) -> bool: ...

    async def get_consumer_group_info(
        self, group_id: str
    ) -> ProtocolConsumerGroupInfo: ...

    async def create_topic(
        self,
        topic: str,
        partitions: int,
        replication_factor: int,
    ) -> bool: ...

    async def delete_topic(self, topic: str) -> bool: ...

    async def get_topic_metadata(
        self, topic: str
    ) -> ProtocolTopicMetadata: ...

    async def get_kafka_metrics(
        self, client_id: str
    ) -> ProtocolKafkaMetrics: ...
```

### Kafka Extended Protocol

```python
@runtime_checkable
class ProtocolKafkaExtended(Protocol):
    """
    Protocol for extended Kafka operations.

    Provides advanced Kafka functionality including
    streaming, schema evolution, and performance optimization.

    Key Features:
        - Kafka streaming and real-time processing
        - Schema evolution and compatibility
        - Advanced partitioning strategies
        - Performance tuning and optimization
        - Monitoring and diagnostics
        - Security and authentication
    """

    async def create_stream_processor(
        self, config: ProtocolKafkaStreamConfig
    ) -> str: ...

    async def process_kafka_stream(
        self,
        processor_id: str,
        input_topics: list[str],
        output_topic: str,
        processor_func: ProtocolKafkaStreamProcessor,
    ) -> bool: ...

    async def register_schema(
        self,
        subject: str,
        schema: dict[str, Any],
        schema_type: LiteralSchemaType,
    ) -> int: ...

    async def get_schema(
        self, subject: str, version: int | None = None
    ) -> ProtocolSchemaInfo: ...

    async def check_schema_compatibility(
        self, subject: str, schema: dict[str, Any]
    ) -> ProtocolCompatibilityResult: ...

    async def optimize_kafka_performance(
        self,
        topic: str,
        settings: dict[str, Any],
    ) -> bool: ...

    async def get_kafka_diagnostics(
        self, topic: str | None = None
    ) -> ProtocolKafkaDiagnostics: ...

    async def configure_kafka_security(
        self, security_config: ProtocolKafkaSecurityConfig
    ) -> bool: ...
```

### Circuit Breaker Protocol

```python
@runtime_checkable
class ProtocolCircuitBreaker(Protocol):
    """
    Protocol for circuit breaker operations.

    Provides circuit breaker functionality for
    resilient distributed system communication.

    Key Features:
        - Circuit breaker state management
        - Failure threshold monitoring
        - Automatic recovery and reset
        - Performance metrics and monitoring
        - Custom failure detection logic
        - Integration with HTTP clients
    """

    async def execute_with_circuit_breaker(
        self,
        operation: Callable[[], Awaitable[Any]],
        circuit_name: str,
        timeout_seconds: int | None = None,
    ) -> Any: ...

    async def get_circuit_state(
        self, circuit_name: str
    ) -> LiteralCircuitState: ...

    async def configure_circuit_breaker(
        self,
        circuit_name: str,
        config: ProtocolCircuitBreakerConfig,
    ) -> bool: ...

    async def reset_circuit_breaker(
        self, circuit_name: str
    ) -> bool: ...

    async def get_circuit_metrics(
        self, circuit_name: str
    ) -> ProtocolCircuitBreakerMetrics: ...

    async def get_all_circuit_states(
        self,
    ) -> dict[str, LiteralCircuitState]: ...

    async def force_circuit_open(
        self, circuit_name: str
    ) -> bool: ...

    async def force_circuit_closed(
        self, circuit_name: str
    ) -> bool: ...
```

### Communication Bridge Protocol

```python
@runtime_checkable
class ProtocolCommunicationBridge(Protocol):
    """
    Protocol for communication bridge operations.

    Provides bridge functionality for connecting
    different communication protocols and systems.

    Key Features:
        - Protocol translation and bridging
        - Message format conversion
        - Routing and load balancing
        - Error handling and recovery
        - Performance monitoring
        - Security and authentication
    """

    async def create_bridge(
        self,
        bridge_name: str,
        source_protocol: str,
        target_protocol: str,
        config: ProtocolBridgeConfig,
    ) -> str: ...

    async def destroy_bridge(self, bridge_id: str) -> bool: ...

    async def send_message_through_bridge(
        self,
        bridge_id: str,
        message: ProtocolBridgeMessage,
    ) -> ProtocolBridgeResult: ...

    async def get_bridge_status(
        self, bridge_id: str
    ) -> ProtocolBridgeStatus: ...

    async def get_bridge_metrics(
        self, bridge_id: str
    ) -> ProtocolBridgeMetrics: ...

    async def configure_bridge_routing(
        self,
        bridge_id: str,
        routing_rules: list[ProtocolRoutingRule],
    ) -> bool: ...

    async def get_all_bridges(
        self,
    ) -> list[ProtocolBridgeInfo]: ...

    async def monitor_bridge_health(
        self, bridge_id: str
    ) -> ProtocolBridgeHealth: ...
```

## 🔧 Type Definitions

### Circuit Breaker Types

```python
LiteralCircuitState = Literal["closed", "open", "half_open"]
"""
Circuit breaker states.

Values:
    closed: Circuit is closed, requests pass through
    open: Circuit is open, requests are blocked
    half_open: Circuit is half-open, testing recovery
"""

LiteralCompressionType = Literal["none", "gzip", "deflate", "brotli"]
"""
HTTP compression types.

Values:
    none: No compression
    gzip: GZIP compression
    deflate: DEFLATE compression
    brotli: Brotli compression
"""

LiteralSchemaType = Literal["AVRO", "JSON", "PROTOBUF"]
"""
Schema types for Kafka integration.

Values:
    AVRO: Apache Avro schema
    JSON: JSON schema
    PROTOBUF: Protocol Buffers schema
"""
```

## 🚀 Usage Examples

### HTTP Client Operations

```python
from omnibase_spi.protocols.networking import ProtocolHttpClient

# Initialize HTTP client
http_client: ProtocolHttpClient = get_http_client()

# GET request
response = await http_client.get(
    url="https://api.example.com/users",
    headers={"Authorization": "Bearer token123"},
    params={"page": 1, "limit": 10},
    timeout_seconds=30
)

print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# POST request with JSON
response = await http_client.post(
    url="https://api.example.com/users",
    json={"name": "John Doe", "email": "john@example.com"},
    headers={"Content-Type": "application/json"},
    timeout_seconds=30
)

# Configure retry policy
await http_client.configure_retry_policy(
    ProtocolRetryPolicy(
        max_retries=3,
        backoff_factor=2.0,
        retry_on_status_codes=[500, 502, 503, 504]
    )
)
```

### HTTP Extended Operations

```python
from omnibase_spi.protocols.networking import ProtocolHttpExtended

# Initialize HTTP extended client
http_extended: ProtocolHttpExtended = get_http_extended()

# Stream large response
async for chunk in http_extended.stream_request(
    method="GET",
    url="https://api.example.com/large-dataset",
    chunk_size=4096
):
    print(f"Received chunk: {len(chunk)} bytes")

# WebSocket connection
websocket = await http_extended.websocket_connect(
    url="wss://api.example.com/ws",
    headers={"Authorization": "Bearer token123"}
)

# Send WebSocket message
await websocket.send("Hello WebSocket!")

# Receive WebSocket message
message = await websocket.receive()
print(f"Received: {message}")

# OAuth2 authentication
token = await http_extended.authenticate_oauth2(
    token_url="https://auth.example.com/oauth/token",
    client_id="client_id",
    client_secret="client_secret",
    scope="read write"
)

print(f"Access token: {token.access_token}")
```

### Kafka Operations

```python
from omnibase_spi.protocols.networking import ProtocolKafkaClient

# Initialize Kafka client
kafka_client: ProtocolKafkaClient = get_kafka_client()

# Create producer
producer_id = await kafka_client.create_producer(
    ProtocolKafkaProducerConfig(
        bootstrap_servers=["kafka1:9092", "kafka2:9092"],
        acks="all",
        retries=3
    )
)

# Produce message
result = await kafka_client.produce_message(
    producer_id=producer_id,
    topic="user-events",
    key=b"user-12345",
    value=b'{"action": "user_created", "user_id": "12345"}',
    headers={"event_type": b"user_created"}
)

print(f"Message produced to partition {result.partition} at offset {result.offset}")

# Create consumer
consumer_id = await kafka_client.create_consumer(
    ProtocolKafkaConsumerConfig(
        bootstrap_servers=["kafka1:9092", "kafka2:9092"],
        group_id="user-service",
        auto_offset_reset="earliest"
    )
)

# Consume messages
messages = await kafka_client.consume_messages(
    consumer_id=consumer_id,
    topics=["user-events"],
    timeout_ms=5000
)

for message in messages:
    print(f"Received: {message.value.decode()}")
    print(f"Partition: {message.partition}, Offset: {message.offset}")

# Commit offsets
offsets = {message.topic: message.offset for message in messages}
await kafka_client.commit_offsets(consumer_id, offsets)
```

### Circuit Breaker Operations

```python
from omnibase_spi.protocols.networking import ProtocolCircuitBreaker

# Initialize circuit breaker
circuit_breaker: ProtocolCircuitBreaker = get_circuit_breaker()

# Configure circuit breaker
await circuit_breaker.configure_circuit_breaker(
    circuit_name="user-service",
    config=ProtocolCircuitBreakerConfig(
        failure_threshold=5,
        timeout_seconds=60,
        success_threshold=3
    )
)

# Execute with circuit breaker
try:
    result = await circuit_breaker.execute_with_circuit_breaker(
        operation=lambda: call_user_service(),
        circuit_name="user-service",
        timeout_seconds=30
    )
    print(f"Service call successful: {result}")
except CircuitBreakerOpenError:
    print("Circuit breaker is open, service unavailable")

# Check circuit state
state = await circuit_breaker.get_circuit_state("user-service")
print(f"Circuit state: {state}")

# Get circuit metrics
metrics = await circuit_breaker.get_circuit_metrics("user-service")
print(f"Failure count: {metrics.failure_count}")
print(f"Success count: {metrics.success_count}")
print(f"State transitions: {metrics.state_transitions}")
```

### Communication Bridge Operations

```python
from omnibase_spi.protocols.networking import ProtocolCommunicationBridge

# Initialize communication bridge
bridge: ProtocolCommunicationBridge = get_communication_bridge()

# Create bridge between HTTP and Kafka
bridge_id = await bridge.create_bridge(
    bridge_name="http-to-kafka",
    source_protocol="http",
    target_protocol="kafka",
    config=ProtocolBridgeConfig(
        source_endpoint="https://api.example.com/events",
        target_topic="events",
        message_format="json"
    )
)

# Send message through bridge
result = await bridge.send_message_through_bridge(
    bridge_id=bridge_id,
    message=ProtocolBridgeMessage(
        payload={"event": "user_login", "user_id": "12345"},
        headers={"source": "web-app"},
        metadata={"timestamp": "2024-01-19T10:00:00Z"}
    )
)

print(f"Message sent: {result.success}")
print(f"Target message ID: {result.message_id}")

# Get bridge status
status = await bridge.get_bridge_status(bridge_id)
print(f"Bridge status: {status.state}")
print(f"Messages processed: {status.messages_processed}")

# Configure routing rules
await bridge.configure_bridge_routing(
    bridge_id=bridge_id,
    routing_rules=[
        ProtocolRoutingRule(
            condition="payload.event == 'user_login'",
            target_topic="user-events"
        ),
        ProtocolRoutingRule(
            condition="payload.event == 'order_created'",
            target_topic="order-events"
        )
    ]
)
```

## 🔍 Implementation Notes

### HTTP Client Patterns

Advanced HTTP client usage:

```python
# Configure retry policy
await http_client.configure_retry_policy(
    ProtocolRetryPolicy(
        max_retries=3,
        backoff_factor=2.0,
        retry_on_status_codes=[500, 502, 503, 504]
    )
)

# Configure circuit breaker
await http_client.configure_circuit_breaker(
    ProtocolCircuitBreaker(
        failure_threshold=5,
        timeout_seconds=60
    )
)
```

### Kafka Integration Patterns

Comprehensive Kafka usage:

```python
# Schema registry integration
schema_version = await kafka_extended.register_schema(
    subject="user-events-value",
    schema=user_event_schema,
    schema_type="AVRO"
)

# Stream processing
processor_id = await kafka_extended.create_stream_processor(
    ProtocolKafkaStreamConfig(
        application_id="user-event-processor",
        bootstrap_servers=["kafka:9092"]
    )
)
```

### Circuit Breaker Patterns

Resilient communication patterns:

```python
# Circuit breaker with custom failure detection
async def custom_operation():
    try:
        return await external_service_call()
    except ServiceUnavailableError:
        # Custom failure detection logic
        raise CircuitBreakerFailure("Service unavailable")

result = await circuit_breaker.execute_with_circuit_breaker(
    operation=custom_operation,
    circuit_name="external-service"
)
```

## 📊 Protocol Statistics

- **Total Protocols**: 6 networking protocols
- **HTTP Support**: Full HTTP/HTTPS with advanced features
- **Kafka Integration**: Producer, consumer, and streaming support
- **Circuit Breakers**: Resilient communication patterns
- **Communication Bridges**: Protocol translation and routing
- **Performance**: Connection pooling, compression, and optimization
- **Security**: Authentication, encryption, and access control

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*

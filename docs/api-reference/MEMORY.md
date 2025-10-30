# Memory Management API Reference

## Overview

The ONEX memory management protocols provide comprehensive memory operations, workflow state persistence, agent coordination, and security features. These protocols enable sophisticated memory management patterns with key-value operations, workflow state tracking, and distributed agent coordination.

## 🏗️ Protocol Architecture

The memory management domain consists of **15 specialized protocols** that provide complete memory operations:

### Memory Base Protocol

```python
from omnibase_spi.protocols.memory import ProtocolMemoryBase
from omnibase_spi.protocols.types.protocol_core_types import ContextValue

@runtime_checkable
class ProtocolMemoryBase(Protocol):
    """
    Base protocol for memory operations.

    Provides fundamental memory operations including key-value storage,
    retrieval, and basic memory management capabilities.

    Key Features:
        - Key-value storage and retrieval
        - Memory lifecycle management
        - Basic security and access control
        - Performance monitoring
        - Error handling and recovery
    """

    async def store(
        self,
        key: str,
        value: ContextValue,
        ttl_seconds: int | None = None,
        metadata: dict[str, ContextValue] | None = None,
    ) -> bool: ...

    async def retrieve(self, key: str) -> ContextValue | None: ...

    async def delete(self, key: str) -> bool: ...

    async def exists(self, key: str) -> bool: ...

    async def get_metadata(self, key: str) -> dict[str, ContextValue] | None: ...

    async def update_metadata(
        self, key: str, metadata: dict[str, ContextValue]
    ) -> bool: ...

    async def list_keys(
        self, pattern: str | None = None, limit: int = 100
    ) -> list[str]: ...

    async def clear_memory(self) -> int: ...

    async def get_memory_stats(self) -> ProtocolMemoryStats: ...
```

### Memory Operations Protocol

```python
@runtime_checkable
class ProtocolMemoryOperations(Protocol):
    """
    Protocol for advanced memory operations.

    Provides sophisticated memory operations including batch operations,
    transactions, and complex data structures.

    Key Features:
        - Batch operations for performance
        - Transaction support for consistency
        - Complex data structure support
        - Atomic operations
        - Performance optimization
    """

    async def batch_store(
        self, operations: list[ProtocolMemoryOperation]
    ) -> ProtocolBatchResult: ...

    async def batch_retrieve(
        self, keys: list[str]
    ) -> dict[str, ContextValue]: ...

    async def batch_delete(self, keys: list[str]) -> int: ...

    async def atomic_increment(
        self, key: str, amount: int = 1
    ) -> int: ...

    async def atomic_decrement(
        self, key: str, amount: int = 1
    ) -> int: ...

    async def atomic_compare_and_swap(
        self, key: str, expected_value: ContextValue, new_value: ContextValue
    ) -> bool: ...

    async def get_hash_map(
        self, key: str
    ) -> dict[str, ContextValue]: ...

    async def set_hash_map(
        self, key: str, hash_map: dict[str, ContextValue]
    ) -> bool: ...

    async def get_list(self, key: str) -> list[ContextValue]: ...

    async def append_to_list(
        self, key: str, values: list[ContextValue]
    ) -> bool: ...
```

### Memory Requests Protocol

```python
@runtime_checkable
class ProtocolMemoryRequests(Protocol):
    """
    Protocol for memory request handling.

    Manages memory requests with queuing, prioritization,
    and request lifecycle management.

    Key Features:
        - Request queuing and prioritization
        - Request lifecycle management
        - Batch request processing
        - Request monitoring and metrics
        - Error handling and retry logic
    """

    async def queue_request(
        self,
        request: ProtocolMemoryRequest,
        priority: LiteralMemoryPriority = "normal",
    ) -> str: ...

    async def process_request(
        self, request_id: str
    ) -> ProtocolMemoryResponse: ...

    async def get_request_status(
        self, request_id: str
    ) -> ProtocolRequestStatus: ...

    async def cancel_request(self, request_id: str) -> bool: ...

    async def get_pending_requests(
        self, limit: int = 100
    ) -> list[ProtocolMemoryRequest]: ...

    async def get_request_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolRequestMetrics: ...

    async def retry_failed_request(
        self, request_id: str, max_retries: int = 3
    ) -> bool: ...
```

### Memory Responses Protocol

```python
@runtime_checkable
class ProtocolMemoryResponses(Protocol):
    """
    Protocol for memory response handling.

    Manages memory responses with caching, serialization,
    and response optimization.

    Key Features:
        - Response caching and optimization
        - Serialization and deserialization
        - Response compression
        - Response validation
        - Performance monitoring
    """

    async def create_response(
        self,
        request_id: str,
        data: ContextValue,
        metadata: dict[str, ContextValue] | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def cache_response(
        self,
        response: ProtocolMemoryResponse,
        ttl_seconds: int = 3600,
    ) -> bool: ...

    async def get_cached_response(
        self, cache_key: str
    ) -> ProtocolMemoryResponse | None: ...

    async def serialize_response(
        self, response: ProtocolMemoryResponse
    ) -> bytes: ...

    async def deserialize_response(
        self, data: bytes
    ) -> ProtocolMemoryResponse: ...

    async def compress_response(
        self, response: ProtocolMemoryResponse
    ) -> bytes: ...

    async def decompress_response(
        self, data: bytes
    ) -> ProtocolMemoryResponse: ...

    async def validate_response(
        self, response: ProtocolMemoryResponse
    ) -> ProtocolValidationResult: ...
```

### Memory Security Protocol

```python
@runtime_checkable
class ProtocolMemorySecurity(Protocol):
    """
    Protocol for memory security operations.

    Provides comprehensive security features including encryption,
    access control, and audit logging.

    Key Features:
        - Data encryption and decryption
        - Access control and permissions
        - Audit logging and monitoring
        - Security policy enforcement
        - Threat detection and prevention
    """

    async def encrypt_data(
        self, data: ContextValue, key_id: str
    ) -> ProtocolEncryptedData: ...

    async def decrypt_data(
        self, encrypted_data: ProtocolEncryptedData
    ) -> ContextValue: ...

    async def check_access_permission(
        self, user_id: str, resource: str, action: str
    ) -> bool: ...

    async def grant_access_permission(
        self, user_id: str, resource: str, action: str
    ) -> bool: ...

    async def revoke_access_permission(
        self, user_id: str, resource: str, action: str
    ) -> bool: ...

    async def audit_memory_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str,
    ) -> None: ...

    async def get_security_audit_log(
        self, time_range_hours: int = 24
    ) -> list[ProtocolSecurityAuditEntry]: ...

    async def detect_security_threats(
        self, time_range_hours: int = 1
    ) -> list[ProtocolSecurityThreat]: ...
```

### Memory Streaming Protocol

```python
@runtime_checkable
class ProtocolMemoryStreaming(Protocol):
    """
    Protocol for memory streaming operations.

    Provides real-time memory operations with streaming,
    change notifications, and live updates.

    Key Features:
        - Real-time memory streaming
        - Change notifications and subscriptions
        - Live data synchronization
        - Stream processing and filtering
        - Performance optimization
    """

    async def create_memory_stream(
        self,
        stream_name: str,
        filter_pattern: str | None = None,
    ) -> str: ...

    async def subscribe_to_memory_changes(
        self,
        stream_id: str,
        handler: ProtocolMemoryChangeHandler,
    ) -> str: ...

    async def unsubscribe_from_memory_changes(
        self, subscription_id: str
    ) -> None: ...

    async def publish_memory_change(
        self,
        key: str,
        old_value: ContextValue | None,
        new_value: ContextValue,
        change_type: LiteralMemoryChangeType,
    ) -> None: ...

    async def get_stream_metrics(
        self, stream_id: str
    ) -> ProtocolStreamMetrics: ...

    async def replay_memory_changes(
        self,
        stream_id: str,
        from_timestamp: ProtocolDateTime,
        to_timestamp: ProtocolDateTime | None = None,
    ) -> list[ProtocolMemoryChange]: ...
```

### Agent Manager Protocol

```python
@runtime_checkable
class ProtocolAgentManager(Protocol):
    """
    Protocol for agent management and coordination.

    Manages distributed agents with lifecycle management,
    coordination, and performance monitoring.

    Key Features:
        - Agent lifecycle management
        - Agent coordination and communication
        - Performance monitoring and optimization
        - Load balancing and failover
        - Health monitoring and recovery
    """

    async def register_agent(
        self,
        agent_info: ProtocolAgentInfo,
        capabilities: list[str],
    ) -> str: ...

    async def unregister_agent(self, agent_id: str) -> bool: ...

    async def get_available_agents(
        self, capability: str | None = None
    ) -> list[ProtocolAgentInfo]: ...

    async def assign_task_to_agent(
        self, task: ProtocolAgentTask, agent_id: str
    ) -> str: ...

    async def get_agent_status(self, agent_id: str) -> ProtocolAgentStatus: ...

    async def get_agent_metrics(
        self, agent_id: str
    ) -> ProtocolAgentMetrics: ...

    async def coordinate_agents(
        self, coordination_task: ProtocolCoordinationTask
    ) -> ProtocolCoordinationResult: ...

    async def monitor_agent_health(
        self, agent_id: str
    ) -> ProtocolAgentHealth: ...
```

### Agent Pool Protocol

```python
@runtime_checkable
class ProtocolAgentPool(Protocol):
    """
    Protocol for agent pool management.

    Manages pools of agents with load balancing,
    capacity management, and performance optimization.

    Key Features:
        - Agent pool management
        - Load balancing and distribution
        - Capacity planning and scaling
        - Performance optimization
        - Health monitoring and recovery
    """

    async def create_agent_pool(
        self,
        pool_name: str,
        pool_config: ProtocolAgentPoolConfig,
    ) -> str: ...

    async def add_agent_to_pool(
        self, pool_id: str, agent_id: str
    ) -> bool: ...

    async def remove_agent_from_pool(
        self, pool_id: str, agent_id: str
    ) -> bool: ...

    async def get_pool_agents(self, pool_id: str) -> list[str]: ...

    async def get_pool_capacity(self, pool_id: str) -> ProtocolPoolCapacity: ...

    async def scale_pool(
        self, pool_id: str, target_size: int
    ) -> bool: ...

    async def get_pool_metrics(
        self, pool_id: str
    ) -> ProtocolPoolMetrics: ...

    async def balance_pool_load(
        self, pool_id: str
    ) -> ProtocolLoadBalancingResult: ...
```

## 🔧 Type Definitions

### Memory Priority Types

```python
LiteralMemoryPriority = Literal["low", "normal", "high", "critical"]
"""
Memory operation priority levels.

Values:
    low: Low priority operations
    normal: Normal priority operations
    high: High priority operations
    critical: Critical priority operations
"""

LiteralMemoryChangeType = Literal["created", "updated", "deleted", "accessed"]
"""
Memory change event types.

Values:
    created: Memory item was created
    updated: Memory item was updated
    deleted: Memory item was deleted
    accessed: Memory item was accessed
"""
```

## 🚀 Usage Examples

### Basic Memory Operations

```python
from omnibase_spi.protocols.memory import ProtocolMemoryBase

# Initialize memory base
memory: ProtocolMemoryBase = get_memory_base()

# Store data
await memory.store(
    key="user:12345",
    value={"name": "John Doe", "email": "john@example.com"},
    ttl_seconds=3600,
    metadata={"created_by": "system", "version": "1.0"}
)

# Retrieve data
user_data = await memory.retrieve("user:12345")
print(f"User: {user_data}")

# Check existence
if await memory.exists("user:12345"):
    print("User exists")

# Get metadata
metadata = await memory.get_metadata("user:12345")
print(f"Created by: {metadata['created_by']}")
```

### Advanced Memory Operations

```python
from omnibase_spi.protocols.memory import ProtocolMemoryOperations

# Initialize memory operations
memory_ops: ProtocolMemoryOperations = get_memory_operations()

# Batch operations
operations = [
    ProtocolMemoryOperation("store", "key1", "value1"),
    ProtocolMemoryOperation("store", "key2", "value2"),
    ProtocolMemoryOperation("delete", "key3", None)
]

batch_result = await memory_ops.batch_store(operations)
print(f"Batch operations completed: {batch_result.success_count}")

# Atomic operations
counter = await memory_ops.atomic_increment("page_views", 1)
print(f"Page views: {counter}")

# Compare and swap
success = await memory_ops.atomic_compare_and_swap(
    "user:12345:status",
    "pending",
    "active"
)
print(f"Status updated: {success}")
```

### Memory Requests and Responses

```python
from omnibase_spi.protocols.memory import ProtocolMemoryRequests, ProtocolMemoryResponses

# Initialize request/response handlers
memory_requests: ProtocolMemoryRequests = get_memory_requests()
memory_responses: ProtocolMemoryResponses = get_memory_responses()

# Queue memory request
request_id = await memory_requests.queue_request(
    request=ProtocolMemoryRequest(
        operation="retrieve",
        key="user:12345",
        priority="high"
    ),
    priority="high"
)

# Process request
response = await memory_requests.process_request(request_id)
print(f"Request result: {response.data}")

# Create and cache response
cached_response = await memory_responses.create_response(
    request_id=request_id,
    data={"user": "John Doe", "status": "active"},
    metadata={"cache_ttl": 3600}
)

await memory_responses.cache_response(cached_response, ttl_seconds=3600)
```

### Memory Security

```python
from omnibase_spi.protocols.memory import ProtocolMemorySecurity

# Initialize memory security
memory_security: ProtocolMemorySecurity = get_memory_security()

# Encrypt sensitive data
encrypted_data = await memory_security.encrypt_data(
    data={"ssn": "123-45-6789", "credit_score": 750},
    key_id="encryption-key-1"
)

# Store encrypted data
await memory.store("user:12345:sensitive", encrypted_data)

# Check access permissions
has_access = await memory_security.check_access_permission(
    user_id="admin-1",
    resource="user:12345:sensitive",
    action="read"
)

if has_access:
    # Decrypt and retrieve data
    encrypted_data = await memory.retrieve("user:12345:sensitive")
    decrypted_data = await memory_security.decrypt_data(encrypted_data)
    print(f"Sensitive data: {decrypted_data}")

# Audit access
await memory_security.audit_memory_access(
    user_id="admin-1",
    resource="user:12345:sensitive",
    action="read",
    result="success"
)
```

### Memory Streaming

```python
from omnibase_spi.protocols.memory import ProtocolMemoryStreaming

# Initialize memory streaming
memory_streaming: ProtocolMemoryStreaming = get_memory_streaming()

# Create memory stream
stream_id = await memory_streaming.create_memory_stream(
    stream_name="user-changes",
    filter_pattern="user:*"
)

# Subscribe to memory changes
subscription_id = await memory_streaming.subscribe_to_memory_changes(
    stream_id=stream_id,
    handler=memory_change_handler
)

# Memory change handler
async def memory_change_handler(change: ProtocolMemoryChange) -> None:
    print(f"Memory change: {change.key} - {change.change_type}")
    print(f"Old value: {change.old_value}")
    print(f"New value: {change.new_value}")

# Publish memory change
await memory_streaming.publish_memory_change(
    key="user:12345",
    old_value={"name": "John Doe"},
    new_value={"name": "John Smith"},
    change_type="updated"
)
```

### Agent Management

```python
from omnibase_spi.protocols.memory import ProtocolAgentManager, ProtocolAgentPool

# Initialize agent manager
agent_manager: ProtocolAgentManager = get_agent_manager()

# Register agent
agent_id = await agent_manager.register_agent(
    agent_info=ProtocolAgentInfo(
        agent_id="agent-1",
        agent_type="data_processor",
        host="192.168.1.100",
        port=8080
    ),
    capabilities=["data_processing", "ml_inference", "reporting"]
)

# Get available agents
available_agents = await agent_manager.get_available_agents("data_processing")
print(f"Available agents: {len(available_agents)}")

# Assign task to agent
task_id = await agent_manager.assign_task_to_agent(
    task=ProtocolAgentTask(
        task_type="data_processing",
        data={"dataset": "sales_data.csv"},
        priority="high"
    ),
    agent_id=agent_id
)

# Initialize agent pool
agent_pool: ProtocolAgentPool = get_agent_pool()

# Create agent pool
pool_id = await agent_pool.create_agent_pool(
    pool_name="data-processing-pool",
    pool_config=ProtocolAgentPoolConfig(
        min_size=2,
        max_size=10,
        target_size=5
    )
)

# Add agents to pool
await agent_pool.add_agent_to_pool(pool_id, agent_id)

# Scale pool
await agent_pool.scale_pool(pool_id, target_size=8)
```

## 🔍 Implementation Notes

### Memory Performance Optimization

Advanced memory optimization patterns:

```python
# Batch operations for performance
operations = [ProtocolMemoryOperation("store", f"key_{i}", f"value_{i}") for i in range(1000)]
batch_result = await memory_ops.batch_store(operations)

# Atomic operations for consistency
counter = await memory_ops.atomic_increment("request_count", 1)
```

### Security Best Practices

Comprehensive security implementation:

```python
# Encrypt sensitive data before storage
sensitive_data = {"ssn": "123-45-6789"}
encrypted = await memory_security.encrypt_data(sensitive_data, "key-1")
await memory.store("user:sensitive", encrypted)

# Audit all access
await memory_security.audit_memory_access("user-1", "resource", "read", "success")
```

### Agent Coordination

Distributed agent management:

```python
# Coordinate multiple agents
coordination_result = await agent_manager.coordinate_agents(
    ProtocolCoordinationTask(
        task_type="distributed_processing",
        agents=["agent-1", "agent-2", "agent-3"],
        coordination_strategy="round_robin"
    )
)
```

## 📊 Protocol Statistics

- **Total Protocols**: 15 memory management protocols
- **Memory Operations**: Key-value storage, batch operations, atomic operations
- **Security Features**: Encryption, access control, audit logging
- **Streaming Support**: Real-time memory changes and notifications
- **Agent Management**: Distributed agent coordination and pool management
- **Performance**: High-throughput memory operations with optimization
- **Monitoring**: Comprehensive metrics and health tracking

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*

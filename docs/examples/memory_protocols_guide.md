# Memory Protocols Guide

## Overview

Comprehensive guide to memory system implementation patterns using ONEX SPI memory protocols.

## Memory Architecture

The memory system provides:
- **Key-value storage** with TTL support
- **Workflow state persistence** with event sourcing
- **Memory security** with encryption and access control
- **Agent coordination** with distributed management
- **Streaming operations** with real-time updates

## Basic Memory Operations

### Memory Base Protocol

```python
from omnibase_spi.protocols.memory import ProtocolMemoryBase

# Initialize memory
memory: ProtocolMemoryBase = get_memory()

# Store data with TTL
await memory.store(
    key="user:12345",
    value={"name": "John Doe", "email": "john@example.com"},
    ttl_seconds=3600,
    metadata={"created_by": "system"}
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

# Initialize advanced operations
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

## Memory Security

### Encryption and Access Control

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

## Memory Streaming

### Real-time Memory Updates

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

## Agent Management

### Distributed Agent Coordination

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

## Memory Patterns

### Caching Patterns

```python
# Cache with TTL
await memory.store(
    key="cache:expensive_calculation",
    value=calculation_result,
    ttl_seconds=300  # 5 minutes
)

# Check cache first
cached_result = await memory.retrieve("cache:expensive_calculation")
if cached_result:
    return cached_result
else:
    # Perform expensive calculation
    result = perform_expensive_calculation()
    await memory.store("cache:expensive_calculation", result, ttl_seconds=300)
    return result
```

### Session Management

```python
# Store session data
session_id = "session-abc123"
await memory.store(
    key=f"session:{session_id}",
    value={
        "user_id": "12345",
        "login_time": datetime.now().isoformat(),
        "permissions": ["read", "write"]
    },
    ttl_seconds=3600  # 1 hour
)

# Retrieve session
session_data = await memory.retrieve(f"session:{session_id}")
if session_data:
    print(f"User {session_data['user_id']} is logged in")
```

### Workflow State Persistence

```python
# Store workflow state
workflow_state = {
    "workflow_type": "order-processing",
    "instance_id": "123e4567-e89b-12d3-a456-426614174000",
    "current_state": "payment_processing",
    "data": {"order_id": "ORD-12345", "amount": 99.99}
}

await memory.store(
    key=f"workflow:{workflow_state['instance_id']}",
    value=workflow_state,
    ttl_seconds=86400  # 24 hours
)

# Retrieve workflow state
state = await memory.retrieve(f"workflow:{workflow_state['instance_id']}")
if state:
    print(f"Workflow state: {state['current_state']}")
```

## Performance Optimization

### Batch Operations

```python
# Use batch operations for performance
operations = []
for i in range(1000):
    operations.append(
        ProtocolMemoryOperation("store", f"key_{i}", f"value_{i}")
    )

batch_result = await memory_ops.batch_store(operations)
print(f"Stored {batch_result.success_count} items")
```

### Memory Monitoring

```python
# Get memory statistics
stats = await memory.get_memory_stats()
print(f"Total keys: {stats.total_keys}")
print(f"Memory usage: {stats.memory_usage_bytes} bytes")
print(f"Hit rate: {stats.hit_rate}%")
```

## Best Practices

### Memory Management

1. **Use TTL** - Set appropriate TTL values for data
2. **Batch Operations** - Use batch operations for performance
3. **Monitor Usage** - Track memory usage and performance
4. **Secure Data** - Encrypt sensitive data
5. **Audit Access** - Log all memory access for security

### Error Handling

```python
try:
    result = await memory.retrieve("key")
    if result is None:
        print("Key not found")
    else:
        print(f"Retrieved: {result}")
except MemoryError as e:
    print(f"Memory operation failed: {e}")
    # Handle error appropriately
```

## API Reference

- **[Memory Management](../api-reference/memory.md)** - Complete memory protocol documentation
- **[Container Protocols](../api-reference/container.md)** - Dependency injection patterns
- **[Workflow Orchestration](../api-reference/workflow-orchestration.md)** - Event-driven FSM

---

*For detailed protocol documentation, see the [API Reference](../api-reference/README.md).*

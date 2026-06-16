# Memory Management API Reference

![Version](https://img.shields.io/badge/SPI-v0.22.0-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.3.0-lightgrey)

> **Package Version**: 0.22.0 | **Status**: Stable | **Since**: v0.3.0

---

## Overview

The ONEX memory management protocols provide memory operations, workflow state persistence, agent coordination, and security features following the ONEX 4-node architecture. These protocols enable sophisticated memory management patterns with semantic search, streaming, and batch operations.

## Protocol Architecture

The memory management domain consists of **12 source files** organized by function:

| Source File | Contents |
|-------------|----------|
| `protocol_memory_base.py` | Base types, literals, and data protocol definitions |
| `protocol_memory_composable.py` | Composable coordinator/manager protocols |
| `protocol_memory_error_handling.py` | Error handling and retry protocols |
| `protocol_memory_errors.py` | Error response and recovery protocols |
| `protocol_memory_operations.py` | ONEX 4-node operation protocols |
| `protocol_memory_requests.py` | Request protocols for all memory operations |
| `protocol_memory_responses.py` | Response protocols for all memory operations |
| `protocol_memory_security.py` | Security, audit, and compliance protocols |
| `protocol_memory_streaming.py` | Streaming and caching protocols |

All protocols follow ONEX SPI purity rules: pure `typing.Protocol` only, no implementations.

## Import Path

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryEffectNode,
    ProtocolMemoryComputeNode,
    ProtocolMemoryReducerNode,
    ProtocolMemoryOrchestratorNode,
    ProtocolMemoryHealthNode,
)
```

## Core Operation Protocols (ONEX 4-Node)

The memory domain maps directly onto the ONEX 4-node architecture:

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryEffectNode,        # Storage, retrieval, persistence
    ProtocolMemoryComputeNode,       # Intelligence processing, semantic analysis
    ProtocolMemoryReducerNode,       # Consolidation, aggregation, optimization
    ProtocolMemoryOrchestratorNode,  # Workflow and agent coordination
    ProtocolMemoryHealthNode,        # Health monitoring and observability
)
```

## Request and Response Protocols

All memory operations use typed request/response pairs:

```python
# Request protocols
from omnibase_spi.protocols.memory import (
    ProtocolMemoryStoreRequest,
    ProtocolMemoryRetrieveRequest,
    ProtocolBatchMemoryStoreRequest,
    ProtocolBatchMemoryRetrieveRequest,
    ProtocolSemanticSearchRequest,
    ProtocolEmbeddingRequest,
    ProtocolConsolidationRequest,
    ProtocolAggregationRequest,
    ProtocolWorkflowExecutionRequest,
    ProtocolAgentCoordinationRequest,
    ProtocolStreamingMemoryRequest,
    ProtocolStreamingRetrieveRequest,
    ProtocolMemoryListRequest,
    ProtocolMemoryMetricsRequest,
    ProtocolPaginationRequest,
    ProtocolPatternAnalysisRequest,
)

# Response protocols
from omnibase_spi.protocols.memory import (
    ProtocolMemoryStoreResponse,
    ProtocolMemoryRetrieveResponse,
    ProtocolBatchMemoryStoreResponse,
    ProtocolBatchMemoryRetrieveResponse,
    ProtocolSemanticSearchResponse,
    ProtocolEmbeddingResponse,
    ProtocolConsolidationResponse,
    ProtocolAggregationResponse,
    ProtocolWorkflowExecutionResponse,
    ProtocolAgentCoordinationResponse,
    ProtocolStreamingMemoryResponse,
    ProtocolStreamingRetrieveResponse,
    ProtocolMemoryListResponse,
    ProtocolMemoryMetricsResponse,
    ProtocolPaginationResponse,
    ProtocolPatternAnalysisResponse,
    ProtocolMemoryMetrics,
    ProtocolBatchOperationResult,
)
```

## Composable Coordinator Protocols

```python
from omnibase_spi.protocols.memory import (
    ProtocolAgentCoordinator,    # Agent coordination
    ProtocolClusterCoordinator,  # Cluster-level coordination
    ProtocolComputeNodeComposite, # Composite compute operations
    ProtocolLifecycleManager,    # Lifecycle management
    ProtocolMemoryOrchestrator,  # Memory workflow orchestration
    ProtocolWorkflowManager,     # Workflow management
)
```

## Security and Compliance Protocols

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemorySecurityNode,     # Security boundary enforcement
    ProtocolMemoryComplianceNode,   # Compliance monitoring
    ProtocolMemorySecurityContext,  # Security context carrier
    ProtocolAuditTrail,             # Audit logging
    ProtocolInputValidation,        # Input sanitization
    ProtocolRateLimitConfig,        # Rate limiting configuration
)
```

## Streaming and Performance Protocols

```python
from omnibase_spi.protocols.memory import (
    ProtocolStreamingMemoryNode,    # Streaming memory operations
    ProtocolMemoryCache,            # Cache abstraction
    ProtocolPerformanceOptimization, # Performance tuning
    ProtocolCursorPagination,       # Cursor-based pagination
    ProtocolStreamingChunk,         # Streaming chunk data
    ProtocolStreamingConfig,        # Streaming configuration
)
```

## Error Handling Protocols

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryErrorHandler,         # Error handler boundary
    ProtocolMemoryHealthMonitor,        # Health monitoring
    ProtocolMemoryRetryPolicy,          # Retry strategy
    ProtocolMemoryCompensationAction,   # Compensation on failure
    ProtocolErrorCategory,              # Error classification
    ProtocolOperationContext,           # Operation context for errors
)
```

## Usage Examples

### Store and Retrieve

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryEffectNode,
    ProtocolMemoryStoreRequest,
    ProtocolMemoryRetrieveRequest,
)

effect_node: ProtocolMemoryEffectNode = get_memory_effect_node()

store_request = ProtocolMemoryStoreRequest(
    key="user:12345",
    data={"name": "Jane Doe", "role": "admin"},
    ttl_seconds=3600,
)
store_response = await effect_node.store(store_request)

retrieve_request = ProtocolMemoryRetrieveRequest(key="user:12345")
retrieve_response = await effect_node.retrieve(retrieve_request)
```

### Semantic Search

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryComputeNode,
    ProtocolSemanticSearchRequest,
)

compute_node: ProtocolMemoryComputeNode = get_memory_compute_node()

search_request = ProtocolSemanticSearchRequest(
    query="agent coordination patterns",
    top_k=10,
)
results = await compute_node.semantic_search(search_request)
```

## Protocol Statistics

- **Source files**: 9 protocol source files
- **Memory operations**: Key-value store, batch, streaming, semantic search
- **Security features**: Encryption boundary, access control, audit logging
- **ONEX node mapping**: Effect, Compute, Reducer, Orchestrator, Health
- **Performance**: Streaming, caching, cursor pagination, batch operations

---

## See Also

- **[NODES.md](./NODES.md)** - Node protocols that use memory for state management
- **[CONTAINER.md](./CONTAINER.md)** - Dependency injection for memory providers
- **[CORE.md](./CORE.md)** - Core protocols including metrics and health monitoring
- **[EXCEPTIONS.md](./EXCEPTIONS.md)** - Exception hierarchy for memory operation errors
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference documents the memory protocols defined in `omnibase_spi.protocols.memory`. Concrete implementations live in `omnibase_infra`.*

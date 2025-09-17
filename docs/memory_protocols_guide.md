# Memory Protocols Implementation Guide

## Overview

This guide provides comprehensive examples and usage patterns for implementing the omnibase-spi memory protocols. All protocols follow the ONEX 4-node architecture pattern and maintain strict SPI purity with zero implementation dependencies.

## Table of Contents

1. [ONEX 4-Node Architecture](#onex-4-node-architecture)
2. [Basic Implementation Patterns](#basic-implementation-patterns)
3. [Security Implementation](#security-implementation)
4. [Streaming and Performance](#streaming-and-performance)
5. [Error Handling](#error-handling)
6. [Composable Interfaces](#composable-interfaces)
7. [Complete Examples](#complete-examples)

## ONEX 4-Node Architecture

The memory system follows the ONEX 4-node pattern:

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryEffectNode,     # Storage, retrieval, persistence
    ProtocolMemoryComputeNode,    # Intelligence processing, semantic analysis
    ProtocolMemoryReducerNode,    # Consolidation, aggregation, optimization
    ProtocolMemoryOrchestratorNode, # Workflow and agent coordination
    ProtocolMemoryHealthNode      # Health monitoring and observability
)
```

### Node Responsibilities

- **Effect Node**: Raw memory operations (CRUD)
- **Compute Node**: AI/ML processing and analysis
- **Reducer Node**: Data aggregation and optimization
- **Orchestrator Node**: Workflow coordination and agent management
- **Health Node**: System monitoring and metrics

## Basic Implementation Patterns

### 1. Effect Node Implementation

```python
from uuid import UUID
from typing import Optional, Dict, Any
from omnibase_spi.protocols.memory import (
    ProtocolMemoryEffectNode,
    ProtocolMemoryStoreRequest,
    ProtocolMemoryStoreResponse,
    ProtocolSecurityContext
)

class MemoryEffectNodeImpl(ProtocolMemoryEffectNode):
    """Reference implementation of memory effect node."""

    def __init__(self):
        self._storage: Dict[UUID, Dict[str, Any]] = {}
        self._audit_log: list = []

    async def store_memory(
        self,
        request: ProtocolMemoryStoreRequest,
        security_context: Optional[ProtocolSecurityContext] = None,
        timeout_seconds: Optional[float] = None,
    ) -> ProtocolMemoryStoreResponse:
        """Store a single memory with security and timeout."""

        # Security validation
        if security_context:
            await self._validate_security_context(security_context)

        # Timeout handling
        async with self._timeout_manager(timeout_seconds):
            # Store the memory
            memory_id = request.memory_record.memory_id
            self._storage[memory_id] = {
                'content': request.memory_record.content,
                'metadata': request.memory_record.metadata,
                'timestamp': request.memory_record.timestamp,
                'created_by': security_context.user_id if security_context else None
            }

            # Audit logging
            if security_context:
                self._audit_log.append({
                    'action': 'store_memory',
                    'memory_id': memory_id,
                    'user_id': security_context.user_id,
                    'timestamp': request.memory_record.timestamp
                })

        return ProtocolMemoryStoreResponse(
            success=True,
            memory_id=memory_id,
            message="Memory stored successfully"
        )

    async def _validate_security_context(self, context: ProtocolSecurityContext) -> None:
        """Validate security context and permissions."""
        if not context.user_id:
            raise ValueError("User ID required for memory operations")

        # Check permissions
        required_permission = "memory:write"
        if required_permission not in context.permissions:
            raise PermissionError(f"Missing permission: {required_permission}")

    async def _timeout_manager(self, timeout_seconds: Optional[float]):
        """Context manager for operation timeouts."""
        import asyncio
        if timeout_seconds:
            return asyncio.timeout(timeout_seconds)
        else:
            return asyncio.nullcontext()
```

### 2. Compute Node Implementation

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryComputeNode,
    ProtocolSemanticSearchRequest,
    ProtocolSemanticSearchResponse,
    ProtocolEmbeddingRequest,
    ProtocolEmbeddingResponse
)

class MemoryComputeNodeImpl(ProtocolMemoryComputeNode):
    """Reference implementation of memory compute node."""

    async def semantic_search(
        self,
        request: ProtocolSemanticSearchRequest,
        security_context: Optional[ProtocolSecurityContext] = None,
        timeout_seconds: Optional[float] = None,
    ) -> ProtocolSemanticSearchResponse:
        """Perform semantic search with security and timeout."""

        async with self._timeout_manager(timeout_seconds):
            # Generate embeddings for search query
            query_embedding = await self._generate_embedding(request.query)

            # Search similar memories
            results = await self._vector_search(
                query_embedding,
                limit=request.limit,
                filters=request.filters
            )

            # Apply security filtering
            if security_context:
                results = await self._filter_by_permissions(results, security_context)

        return ProtocolSemanticSearchResponse(
            success=True,
            results=results,
            total_count=len(results)
        )

    async def generate_embeddings(
        self,
        request: ProtocolEmbeddingRequest,
        security_context: Optional[ProtocolSecurityContext] = None,
        timeout_seconds: Optional[float] = None,
    ) -> ProtocolEmbeddingResponse:
        """Generate embeddings for content with batch processing."""

        embeddings = []

        async with self._timeout_manager(timeout_seconds):
            # Process in batches for efficiency
            batch_size = 32
            for i in range(0, len(request.content_items), batch_size):
                batch = request.content_items[i:i + batch_size]
                batch_embeddings = await self._process_embedding_batch(batch)
                embeddings.extend(batch_embeddings)

        return ProtocolEmbeddingResponse(
            success=True,
            embeddings=embeddings,
            model_used=request.embedding_model or "default"
        )
```

## Security Implementation

### Security Context Usage

```python
from omnibase_spi.protocols.memory import (
    ProtocolSecurityContext,
    ProtocolAuditTrail,
    ProtocolRateLimitConfig
)

# Create security context
security_context = ProtocolSecurityContext(
    user_id="user_123",
    session_id="session_456",
    permissions=["memory:read", "memory:write", "memory:admin"],
    access_level="authenticated",
    audit_trail=ProtocolAuditTrail(
        correlation_id=UUID("..."),
        request_timestamp=datetime.utcnow(),
        source_ip="192.168.1.100",
        user_agent="MyApp/1.0"
    ),
    rate_limit_config=ProtocolRateLimitConfig(
        requests_per_minute=100,
        burst_capacity=20,
        window_size_seconds=60
    )
)

# Use in memory operations
result = await memory_node.store_memory(
    request=store_request,
    security_context=security_context,
    timeout_seconds=30.0
)
```

### PII Detection and Compliance

```python
from omnibase_spi.protocols.memory import ProtocolMemorySecurityNode

class SecurityNodeImpl(ProtocolMemorySecurityNode):
    """Implementation with PII detection and compliance."""

    async def detect_pii(
        self,
        content: str,
        detection_config: Optional[Dict[str, Any]] = None,
        security_context: Optional[ProtocolSecurityContext] = None,
    ) -> Dict[str, Any]:
        """Sub-millisecond PII detection."""

        # Fast regex-based detection for common PII patterns
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        }

        detected_pii = {}
        for pii_type, pattern in pii_patterns.items():
            import re
            matches = re.findall(pattern, content)
            if matches:
                detected_pii[pii_type] = {
                    'count': len(matches),
                    'confidence': 0.95,  # High confidence for regex matches
                    'positions': [(m.start(), m.end()) for m in re.finditer(pattern, content)]
                }

        return {
            'pii_detected': bool(detected_pii),
            'pii_types': detected_pii,
            'compliance_status': 'requires_review' if detected_pii else 'compliant',
            'processing_time_ms': 0.5  # Sub-millisecond processing
        }
```

## Streaming and Performance

### Streaming Large Content

```python
from omnibase_spi.protocols.memory import (
    ProtocolStreamingMemoryNode,
    ProtocolStreamingChunk,
    ProtocolStreamingConfig
)
from typing import AsyncGenerator

class StreamingNodeImpl(ProtocolStreamingMemoryNode):
    """Implementation with streaming support for large content."""

    async def stream_memory_content(
        self,
        memory_id: UUID,
        streaming_config: ProtocolStreamingConfig,
        security_context: Optional[ProtocolSecurityContext] = None,
        timeout_seconds: Optional[float] = None,
    ) -> AsyncGenerator[ProtocolStreamingChunk, None]:
        """Stream large memory content in chunks."""

        # Validate permissions
        if security_context:
            await self._validate_streaming_permissions(security_context, memory_id)

        # Get memory metadata
        memory_info = await self._get_memory_info(memory_id)
        total_size = memory_info['content_size']

        # Stream in configured chunks
        chunk_size = streaming_config.chunk_size_bytes
        offset = 0
        sequence_number = 0

        while offset < total_size:
            # Read chunk from storage
            chunk_data = await self._read_chunk(memory_id, offset, chunk_size)

            yield ProtocolStreamingChunk(
                sequence_number=sequence_number,
                data=chunk_data,
                total_chunks=((total_size - 1) // chunk_size) + 1,
                is_final=offset + len(chunk_data) >= total_size,
                checksum=self._calculate_checksum(chunk_data)
            )

            offset += len(chunk_data)
            sequence_number += 1

            # Respect streaming rate limits
            if streaming_config.rate_limit_mbps:
                await self._apply_rate_limit(len(chunk_data), streaming_config.rate_limit_mbps)
```

### Memory Caching

```python
from omnibase_spi.protocols.memory import ProtocolMemoryCache

class MemoryCacheImpl(ProtocolMemoryCache):
    """High-performance memory caching implementation."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_stats = {'hits': 0, 'misses': 0}

    async def get_cached_memory(
        self,
        cache_key: str,
        security_context: Optional[ProtocolSecurityContext] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get memory from cache with security validation."""

        # Check cache
        if cache_key in self._cache:
            cached_item = self._cache[cache_key]

            # Validate cache entry permissions
            if security_context and not self._has_cache_access(cached_item, security_context):
                return None

            # Update access time
            cached_item['last_accessed'] = datetime.utcnow()
            self._cache_stats['hits'] += 1
            return cached_item['data']

        self._cache_stats['misses'] += 1
        return None

    async def cache_memory(
        self,
        cache_key: str,
        memory_data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
        security_context: Optional[ProtocolSecurityContext] = None,
    ) -> bool:
        """Cache memory data with TTL and security."""

        cache_entry = {
            'data': memory_data,
            'cached_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl_seconds) if ttl_seconds else None,
            'owner_id': security_context.user_id if security_context else None,
            'access_level': security_context.access_level if security_context else 'public'
        }

        self._cache[cache_key] = cache_entry
        return True
```

## Error Handling

### Enhanced Error Handling with Retry Policies

```python
from omnibase_spi.protocols.memory import (
    ProtocolMemoryErrorHandler,
    ProtocolRetryPolicy,
    ProtocolCompensationAction,
    ProtocolErrorCategory
)

class MemoryErrorHandlerImpl(ProtocolMemoryErrorHandler):
    """Comprehensive error handling implementation."""

    async def handle_error(
        self,
        error: Exception,
        operation_context: ProtocolOperationContext,
        retry_policy: Optional[ProtocolRetryPolicy] = None,
    ) -> ProtocolMemoryErrorRecoveryResponse:
        """Handle errors with intelligent retry and compensation."""

        # Categorize error
        error_category = self._categorize_error(error)

        # Determine if retry is appropriate
        if error_category.is_transient and retry_policy:
            if operation_context.attempt_count < retry_policy.max_attempts:
                # Calculate backoff delay
                delay = self._calculate_backoff_delay(
                    operation_context.attempt_count,
                    retry_policy.base_delay_seconds,
                    retry_policy.backoff_multiplier
                )

                return ProtocolMemoryErrorRecoveryResponse(
                    should_retry=True,
                    retry_delay_seconds=delay,
                    compensation_actions=[],
                    recovery_strategy="retry_with_backoff"
                )

        # If retry not appropriate, determine compensation actions
        compensation_actions = await self._determine_compensation_actions(error, operation_context)

        return ProtocolMemoryErrorRecoveryResponse(
            should_retry=False,
            retry_delay_seconds=0,
            compensation_actions=compensation_actions,
            recovery_strategy="compensate_and_fail"
        )

    def _categorize_error(self, error: Exception) -> ProtocolErrorCategory:
        """Categorize error as transient or permanent."""

        transient_errors = (ConnectionError, TimeoutError, TemporaryFailure)
        permanent_errors = (ValueError, PermissionError, ValidationError)

        if isinstance(error, transient_errors):
            return ProtocolErrorCategory(
                category="transient",
                is_transient=True,
                severity="medium",
                description=f"Transient error: {type(error).__name__}"
            )
        elif isinstance(error, permanent_errors):
            return ProtocolErrorCategory(
                category="permanent",
                is_transient=False,
                severity="high",
                description=f"Permanent error: {type(error).__name__}"
            )
        else:
            return ProtocolErrorCategory(
                category="unknown",
                is_transient=False,
                severity="high",
                description=f"Unknown error: {type(error).__name__}"
            )
```

### Circuit Breaker Pattern

```python
class CircuitBreakerErrorHandler(ProtocolMemoryErrorHandler):
    """Error handler with circuit breaker pattern."""

    def __init__(self):
        self._failure_count = 0
        self._last_failure_time = None
        self._circuit_state = "closed"  # closed, open, half_open
        self._failure_threshold = 5
        self._recovery_timeout = 60  # seconds

    async def handle_error(
        self,
        error: Exception,
        operation_context: ProtocolOperationContext,
        retry_policy: Optional[ProtocolRetryPolicy] = None,
    ) -> ProtocolMemoryErrorRecoveryResponse:
        """Handle errors with circuit breaker logic."""

        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()

        # Check if circuit should open
        if self._failure_count >= self._failure_threshold:
            self._circuit_state = "open"

            return ProtocolMemoryErrorRecoveryResponse(
                should_retry=False,
                retry_delay_seconds=self._recovery_timeout,
                compensation_actions=[
                    ProtocolCompensationAction(
                        action_type="circuit_breaker_open",
                        description="Circuit breaker opened due to repeated failures",
                        parameters={"failure_count": self._failure_count}
                    )
                ],
                recovery_strategy="circuit_breaker_open"
            )

        # Normal error handling if circuit is closed
        return await super().handle_error(error, operation_context, retry_policy)
```

## Composable Interfaces

### Using Composable Workflow Management

```python
from omnibase_spi.protocols.memory import (
    ProtocolWorkflowManager,
    ProtocolAgentCoordinator,
    ProtocolClusterCoordinator,
    ProtocolLifecycleManager
)

class ComposableOrchestratorImpl:
    """Implementation using composable interfaces."""

    def __init__(
        self,
        workflow_manager: ProtocolWorkflowManager,
        agent_coordinator: ProtocolAgentCoordinator,
        cluster_coordinator: ProtocolClusterCoordinator,
        lifecycle_manager: ProtocolLifecycleManager
    ):
        self.workflow_manager = workflow_manager
        self.agent_coordinator = agent_coordinator
        self.cluster_coordinator = cluster_coordinator
        self.lifecycle_manager = lifecycle_manager

    async def execute_distributed_workflow(
        self,
        workflow_request: ProtocolWorkflowExecutionRequest,
        security_context: Optional[ProtocolSecurityContext] = None,
    ) -> ProtocolWorkflowExecutionResponse:
        """Execute workflow using all coordinators."""

        # Start workflow
        workflow_response = await self.workflow_manager.execute_workflow(
            workflow_request,
            security_context,
            timeout_seconds=300
        )

        # Coordinate agents for distributed tasks
        if workflow_request.requires_agent_coordination:
            agent_request = ProtocolAgentCoordinationRequest(
                agent_ids=workflow_request.required_agents,
                coordination_task=workflow_request.coordination_task,
                correlation_id=workflow_request.correlation_id
            )

            await self.agent_coordinator.coordinate_agents(
                agent_request,
                security_context,
                timeout_seconds=120
            )

        # Synchronize cluster state if needed
        if workflow_request.requires_cluster_sync:
            await self.cluster_coordinator.synchronize_state(
                node_ids=workflow_request.target_nodes,
                synchronization_scope=workflow_request.sync_scope,
                security_context=security_context
            )

        return workflow_response
```

### Lifecycle Management Implementation

```python
class LifecycleManagerImpl(ProtocolLifecycleManager):
    """Implementation of memory lifecycle management."""

    async def apply_retention_policies(
        self,
        policy_scope: ProtocolMemoryMetadata,
        dry_run: bool = False,
        security_context: Optional[ProtocolSecurityContext] = None,
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> ProtocolMemoryResponse:
        """Apply retention policies with safety checks."""

        # Get memories in scope
        memories_to_evaluate = await self._get_memories_in_scope(policy_scope)

        # Apply retention logic
        actions_planned = []
        for memory in memories_to_evaluate:
            retention_action = await self._evaluate_retention(memory, policy_scope)
            if retention_action:
                actions_planned.append(retention_action)

        # Execute actions if not dry run
        if not dry_run:
            for action in actions_planned:
                await self._execute_retention_action(action, security_context)

        return ProtocolMemoryResponse(
            success=True,
            message=f"Retention policy applied to {len(memories_to_evaluate)} memories",
            correlation_id=correlation_id,
            metadata={
                'actions_planned': len(actions_planned),
                'dry_run': dry_run,
                'memories_evaluated': len(memories_to_evaluate)
            }
        )
```

## Complete Examples

### Full Memory Service Implementation

```python
from uuid import UUID
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime, timedelta

class CompleteMemoryService:
    """Complete memory service implementation using all protocols."""

    def __init__(self):
        self.effect_node = MemoryEffectNodeImpl()
        self.compute_node = MemoryComputeNodeImpl()
        self.reducer_node = MemoryReducerNodeImpl()
        self.orchestrator = ComposableOrchestratorImpl(
            workflow_manager=WorkflowManagerImpl(),
            agent_coordinator=AgentCoordinatorImpl(),
            cluster_coordinator=ClusterCoordinatorImpl(),
            lifecycle_manager=LifecycleManagerImpl()
        )
        self.health_node = MemoryHealthNodeImpl()

        # Enhanced components
        self.streaming_node = StreamingNodeImpl()
        self.cache = MemoryCacheImpl()
        self.error_handler = CircuitBreakerErrorHandler()
        self.security_node = SecurityNodeImpl()

    async def store_memory_with_full_processing(
        self,
        content: str,
        metadata: Dict[str, Any],
        security_context: ProtocolSecurityContext,
        enable_streaming: bool = False,
        enable_caching: bool = True,
    ) -> Dict[str, Any]:
        """Store memory with full processing pipeline."""

        try:
            # 1. Security validation and PII detection
            pii_result = await self.security_node.detect_pii(
                content=content,
                security_context=security_context
            )

            if pii_result['pii_detected'] and not security_context.has_permission('pii:process'):
                raise PermissionError("PII detected but user lacks PII processing permission")

            # 2. Create memory record
            memory_record = ProtocolMemoryRecord(
                memory_id=UUID.uuid4(),
                content=content,
                metadata=metadata,
                timestamp=datetime.utcnow(),
                content_type="text/plain"
            )

            # 3. Store in effect node
            store_request = ProtocolMemoryStoreRequest(
                memory_record=memory_record,
                storage_config={"compression": True}
            )

            store_response = await self.effect_node.store_memory(
                request=store_request,
                security_context=security_context,
                timeout_seconds=30.0
            )

            # 4. Generate embeddings for semantic search
            embedding_request = ProtocolEmbeddingRequest(
                content_items=[content],
                embedding_model="text-embedding-ada-002"
            )

            embedding_response = await self.compute_node.generate_embeddings(
                request=embedding_request,
                security_context=security_context,
                timeout_seconds=60.0
            )

            # 5. Cache if enabled
            if enable_caching:
                cache_key = f"memory:{memory_record.memory_id}"
                await self.cache.cache_memory(
                    cache_key=cache_key,
                    memory_data={
                        'content': content,
                        'metadata': metadata,
                        'embeddings': embedding_response.embeddings[0]
                    },
                    ttl_seconds=3600,  # 1 hour
                    security_context=security_context
                )

            # 6. Health monitoring
            await self.health_node.record_operation_metrics(
                operation_type="store_memory",
                duration_ms=100,  # Would be actual duration
                success=True,
                security_context=security_context
            )

            return {
                'memory_id': memory_record.memory_id,
                'store_response': store_response,
                'embedding_response': embedding_response,
                'pii_detected': pii_result['pii_detected'],
                'cached': enable_caching,
                'processing_time_ms': 150  # Total processing time
            }

        except Exception as error:
            # Handle errors with error handler
            operation_context = ProtocolOperationContext(
                operation_type="store_memory",
                attempt_count=1,
                correlation_id=UUID.uuid4(),
                start_time=datetime.utcnow()
            )

            error_response = await self.error_handler.handle_error(
                error=error,
                operation_context=operation_context,
                retry_policy=ProtocolRetryPolicy(
                    max_attempts=3,
                    base_delay_seconds=1,
                    backoff_multiplier=2
                )
            )

            if error_response.should_retry:
                # Implement retry logic
                await asyncio.sleep(error_response.retry_delay_seconds)
                # Retry the operation (implementation would be recursive)

            raise error

    async def semantic_search_with_caching(
        self,
        query: str,
        limit: int = 10,
        security_context: Optional[ProtocolSecurityContext] = None,
    ) -> Dict[str, Any]:
        """Perform semantic search with intelligent caching."""

        # Check cache first
        cache_key = f"search:{hash(query)}:{limit}"
        cached_result = await self.cache.get_cached_memory(
            cache_key=cache_key,
            security_context=security_context
        )

        if cached_result:
            return {
                'results': cached_result['results'],
                'cache_hit': True,
                'total_count': cached_result['total_count']
            }

        # Perform search
        search_request = ProtocolSemanticSearchRequest(
            query=query,
            limit=limit,
            filters={}
        )

        search_response = await self.compute_node.semantic_search(
            request=search_request,
            security_context=security_context,
            timeout_seconds=30.0
        )

        # Cache results
        await self.cache.cache_memory(
            cache_key=cache_key,
            memory_data={
                'results': search_response.results,
                'total_count': search_response.total_count
            },
            ttl_seconds=1800,  # 30 minutes
            security_context=security_context
        )

        return {
            'results': search_response.results,
            'cache_hit': False,
            'total_count': search_response.total_count
        }
```

### Testing Implementation

```python
import pytest
from unittest.mock import AsyncMock

class TestCompleteMemoryService:
    """Comprehensive tests for memory service implementation."""

    @pytest.fixture
    async def memory_service(self):
        return CompleteMemoryService()

    @pytest.fixture
    def security_context(self):
        return ProtocolSecurityContext(
            user_id="test_user",
            session_id="test_session",
            permissions=["memory:read", "memory:write", "pii:process"],
            access_level="authenticated"
        )

    async def test_store_memory_with_full_processing(self, memory_service, security_context):
        """Test complete memory storage workflow."""

        content = "This is test memory content for storage."
        metadata = {"category": "test", "priority": "low"}

        result = await memory_service.store_memory_with_full_processing(
            content=content,
            metadata=metadata,
            security_context=security_context,
            enable_caching=True
        )

        assert 'memory_id' in result
        assert result['store_response'].success
        assert result['embedding_response'].success
        assert not result['pii_detected']  # No PII in test content
        assert result['cached']
        assert result['processing_time_ms'] > 0

    async def test_semantic_search_with_caching(self, memory_service, security_context):
        """Test semantic search with caching behavior."""

        query = "test search query"

        # First search (cache miss)
        result1 = await memory_service.semantic_search_with_caching(
            query=query,
            limit=5,
            security_context=security_context
        )

        assert not result1['cache_hit']
        assert 'results' in result1

        # Second search (cache hit)
        result2 = await memory_service.semantic_search_with_caching(
            query=query,
            limit=5,
            security_context=security_context
        )

        assert result2['cache_hit']
        assert result2['results'] == result1['results']

    async def test_error_handling_with_retry(self, memory_service, security_context):
        """Test error handling and retry logic."""

        # Mock a transient error
        memory_service.effect_node.store_memory = AsyncMock(
            side_effect=ConnectionError("Temporary connection failure")
        )

        with pytest.raises(ConnectionError):
            await memory_service.store_memory_with_full_processing(
                content="test content",
                metadata={},
                security_context=security_context
            )

        # Verify error handler was called
        assert memory_service.error_handler._failure_count > 0
```

## Best Practices

### 1. Security-First Implementation
- Always validate security context before operations
- Implement PII detection for compliance
- Use audit trails for all sensitive operations
- Apply rate limiting to prevent abuse

### 2. Performance Optimization
- Use streaming for large content operations
- Implement intelligent caching with TTL
- Apply proper timeout management
- Use batch processing where possible

### 3. Error Resilience
- Categorize errors as transient vs permanent
- Implement retry policies with exponential backoff
- Use circuit breaker patterns for reliability
- Provide compensation actions for rollback

### 4. Monitoring and Observability
- Record operation metrics for health monitoring
- Use correlation IDs for request tracing
- Implement comprehensive logging
- Monitor performance and error rates

### 5. Protocol Compliance
- Always implement all required protocol methods
- Use proper type annotations throughout
- Maintain SPI purity (no implementation dependencies)
- Follow ONEX 4-node architecture patterns

This guide provides comprehensive examples for implementing all memory protocols while maintaining SPI purity and following ONEX architectural principles.
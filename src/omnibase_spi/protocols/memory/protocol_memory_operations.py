"""
Pure Protocol Definitions for OmniMemory ONEX Architecture

This module defines protocol interfaces following ONEX 4-node architecture:
- Effect: Memory storage, retrieval, and persistence operations
- Compute: Intelligence processing, semantic analysis, pattern recognition
- Reducer: Memory consolidation, aggregation, and optimization
- Orchestrator: Workflow, agent, and memory coordination

All protocols use typing.Protocol for structural typing with zero dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.memory.protocol_memory_base import (
        LiteralAnalysisType,
        LiteralCompressionAlgorithm,
        ProtocolAggregationCriteria,
        ProtocolMemoryMetadata,
    )
    from omnibase_spi.protocols.memory.protocol_memory_requests import (
        ProtocolAgentCoordinationRequest,
        ProtocolBatchMemoryRetrieveRequest,
        ProtocolBatchMemoryStoreRequest,
        ProtocolConsolidationRequest,
        ProtocolMemoryListRequest,
        ProtocolMemoryMetricsRequest,
        ProtocolMemoryRetrieveRequest,
        ProtocolMemoryStoreRequest,
        ProtocolPatternAnalysisRequest,
        ProtocolSemanticSearchRequest,
        ProtocolWorkflowExecutionRequest,
    )
    from omnibase_spi.protocols.memory.protocol_memory_responses import (
        ProtocolAgentCoordinationResponse,
        ProtocolBatchMemoryRetrieveResponse,
        ProtocolBatchMemoryStoreResponse,
        ProtocolConsolidationResponse,
        ProtocolMemoryListResponse,
        ProtocolMemoryMetricsResponse,
        ProtocolMemoryResponse,
        ProtocolMemoryRetrieveResponse,
        ProtocolMemoryStoreResponse,
        ProtocolPatternAnalysisResponse,
        ProtocolSemanticSearchResponse,
        ProtocolWorkflowExecutionResponse,
    )
    from omnibase_spi.protocols.memory.protocol_memory_security import (
        ProtocolMemorySecurityContext,
        ProtocolRateLimitConfig,
    )


@runtime_checkable
class ProtocolMemoryEffectNode(Protocol):
    """
    Protocol for memory effect operations in ONEX architecture.

    Handles storage, retrieval, and persistence of memory records
    with transactional guarantees and consistency management.
    """

    async def store_memory(
        self,
        request: ProtocolMemoryStoreRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryStoreResponse: ...

    async def retrieve_memory(
        self,
        request: ProtocolMemoryRetrieveRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryRetrieveResponse: ...

    async def update_memory(
        self,
        memory_id: UUID,
        updates: ProtocolMemoryMetadata,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def delete_memory(
        self,
        memory_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def list_memories(
        self,
        request: ProtocolMemoryListRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryListResponse: ...

    async def batch_store_memories(
        self,
        request: ProtocolBatchMemoryStoreRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        rate_limit_config: ProtocolRateLimitConfig | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolBatchMemoryStoreResponse: ...

    async def batch_retrieve_memories(
        self,
        request: ProtocolBatchMemoryRetrieveRequest,
        security_context: ProtocolMemorySecurityContext | None = None,
        rate_limit_config: ProtocolRateLimitConfig | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolBatchMemoryRetrieveResponse: ...


@runtime_checkable
class ProtocolMemoryComputeNode(Protocol):
    """
    Protocol for memory compute operations in ONEX architecture.

    Handles intelligence processing, semantic analysis, and pattern recognition
    with advanced AI capabilities and embedding generation.
    """

    async def semantic_search(
        self, request: ProtocolSemanticSearchRequest
    ) -> ProtocolSemanticSearchResponse: ...

    async def generate_embedding(
        self,
        text: str,
        model: str | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def analyze_patterns(
        self,
        request: ProtocolPatternAnalysisRequest,
        timeout_seconds: float | None = None,
    ) -> ProtocolPatternAnalysisResponse: ...

    async def extract_insights(
        self,
        memory_ids: list[UUID],
        analysis_type: LiteralAnalysisType = "standard",
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def compare_semantics(
        self,
        content_a: str,
        content_b: str,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolMemoryReducerNode(Protocol):
    """
    Protocol for memory reducer operations in ONEX architecture.

    Handles memory consolidation, aggregation, and optimization
    with data reduction and compression capabilities.
    """

    async def consolidate_memories(
        self,
        request: ProtocolConsolidationRequest,
        timeout_seconds: float | None = None,
    ) -> ProtocolConsolidationResponse: ...

    async def deduplicate_memories(
        self,
        memory_scope: ProtocolMemoryMetadata,
        similarity_threshold: float | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def aggregate_data(
        self,
        aggregation_criteria: ProtocolAggregationCriteria,
        time_window_start: str | None = None,
        time_window_end: str | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def compress_memories(
        self,
        memory_ids: list[UUID],
        compression_algorithm: LiteralCompressionAlgorithm,
        quality_threshold: float | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def optimize_storage(
        self,
        optimization_strategy: str,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolMemoryOrchestratorNode(Protocol):
    """
    Protocol for memory orchestrator operations in ONEX architecture.

    Handles workflow coordination, agent management, and distributed
    memory operations across the entire ONEX cluster.
    """

    async def execute_workflow(
        self,
        request: ProtocolWorkflowExecutionRequest,
        timeout_seconds: float | None = None,
    ) -> ProtocolWorkflowExecutionResponse: ...

    async def coordinate_agents(
        self,
        request: ProtocolAgentCoordinationRequest,
        timeout_seconds: float | None = None,
    ) -> ProtocolAgentCoordinationResponse: ...

    async def broadcast_update(
        self,
        update_type: str,
        update_data: ProtocolMemoryMetadata,
        target_agents: list[UUID] | None = None,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def synchronize_state(
        self,
        agent_ids: list[UUID],
        synchronization_scope: ProtocolMemoryMetadata,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...

    async def manage_lifecycle(
        self,
        lifecycle_policies: ProtocolMemoryMetadata,
        correlation_id: UUID | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryResponse: ...


@runtime_checkable
class ProtocolMemoryHealthNode(Protocol):
    """
    Protocol for memory health monitoring and system observability.

    Provides health checks, metrics collection, and system status
    monitoring across all memory nodes.
    """

    async def check_health(
        self, correlation_id: UUID | None = None
    ) -> ProtocolMemoryResponse: ...

    async def collect_metrics(
        self, request: ProtocolMemoryMetricsRequest
    ) -> ProtocolMemoryMetricsResponse: ...

    async def get_status(
        self, include_detailed: bool | None = None, correlation_id: UUID | None = None
    ) -> ProtocolMemoryResponse: ...

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

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from .protocol_memory_base import (
        AnalysisType,
        CompressionAlgorithm,
        ProtocolAggregationCriteria,
        ProtocolMemoryMetadata,
    )
    from .protocol_memory_requests import (
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
    from .protocol_memory_responses import (
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


# === EFFECT NODE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryEffectNode(Protocol):
    """
    Protocol for memory effect operations in ONEX architecture.

    Handles storage, retrieval, and persistence of memory records
    with transactional guarantees and consistency management.
    """

    async def store_memory(
        self,
        request: "ProtocolMemoryStoreRequest",
    ) -> "ProtocolMemoryStoreResponse":
        """
        Store a new memory record with optional expiration and metadata.

        Args:
            request: Memory storage request with content and metadata

        Returns:
            Storage response with memory ID and location
        """
        ...

    async def retrieve_memory(
        self,
        request: "ProtocolMemoryRetrieveRequest",
    ) -> "ProtocolMemoryRetrieveResponse":
        """
        Retrieve a memory record by ID with optional related memories.

        Args:
            request: Memory retrieval request with ID and options

        Returns:
            Retrieval response with memory record and relations
        """
        ...

    async def update_memory(
        self,
        memory_id: UUID,
        updates: "ProtocolMemoryMetadata",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Update an existing memory record with new content or metadata.

        Args:
            memory_id: ID of memory to update
            updates: Dictionary of fields to update
            correlation_id: Request correlation ID

        Returns:
            Update response with success status
        """
        ...

    async def delete_memory(
        self,
        memory_id: UUID,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Delete a memory record (soft delete with retention policy).

        Args:
            memory_id: ID of memory to delete
            correlation_id: Request correlation ID

        Returns:
            Deletion response with success status
        """
        ...

    async def list_memories(
        self,
        request: "ProtocolMemoryListRequest",
    ) -> "ProtocolMemoryListResponse":
        """
        List memory records with paginated filtering.

        Args:
            request: Paginated memory list request with filters and pagination

        Returns:
            Paginated response with memory records and pagination metadata
        """
        ...

    async def batch_store_memories(
        self,
        request: "ProtocolBatchMemoryStoreRequest",
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolBatchMemoryStoreResponse":
        """
        Store multiple memory records in a single batch operation.

        Args:
            request: Batch storage request with multiple memory records
            timeout_seconds: Optional timeout for batch storage operation

        Returns:
            Batch response with individual operation results
        """
        ...

    async def batch_retrieve_memories(
        self,
        request: "ProtocolBatchMemoryRetrieveRequest",
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolBatchMemoryRetrieveResponse":
        """
        Retrieve multiple memory records in a single batch operation.

        Args:
            request: Batch retrieval request with memory IDs
            timeout_seconds: Optional timeout for batch retrieval operation

        Returns:
            Batch response with retrieved memories and results
        """
        ...


# === COMPUTE NODE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryComputeNode(Protocol):
    """
    Protocol for memory compute operations in ONEX architecture.

    Handles intelligence processing, semantic analysis, and pattern recognition
    with advanced AI capabilities and embedding generation.
    """

    async def semantic_search(
        self,
        request: "ProtocolSemanticSearchRequest",
    ) -> "ProtocolSemanticSearchResponse":
        """
        Perform semantic search using vector embeddings and similarity.

        Args:
            request: Semantic search request with query and parameters

        Returns:
            Search response with ranked results and metadata
        """
        ...

    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Generate vector embedding for text content.

        Args:
            text: Text content to embed
            model: Optional specific embedding model
            correlation_id: Request correlation ID

        Returns:
            Response with generated embedding vector
        """
        ...

    async def analyze_patterns(
        self,
        request: "ProtocolPatternAnalysisRequest",
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolPatternAnalysisResponse":
        """
        Analyze patterns in memory data using ML algorithms.

        Args:
            request: Pattern analysis request with data source and type
            timeout_seconds: Optional timeout for pattern analysis operation

        Returns:
            Analysis response with discovered patterns and confidence
        """
        ...

    async def extract_insights(
        self,
        memory_ids: list[UUID],
        analysis_type: "AnalysisType" = "standard",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Extract insights from a collection of memories.

        Args:
            memory_ids: List of memory IDs to analyze
            analysis_type: Type of insight extraction
            correlation_id: Request correlation ID

        Returns:
            Response with extracted insights and scores
        """
        ...

    async def compare_semantics(
        self,
        content_a: str,
        content_b: str,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Compare semantic similarity between two pieces of content.

        Args:
            content_a: First content to compare
            content_b: Second content to compare
            correlation_id: Request correlation ID

        Returns:
            Response with similarity score and analysis
        """
        ...


# === REDUCER NODE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryReducerNode(Protocol):
    """
    Protocol for memory reducer operations in ONEX architecture.

    Handles memory consolidation, aggregation, and optimization
    with data reduction and compression capabilities.
    """

    async def consolidate_memories(
        self,
        request: "ProtocolConsolidationRequest",
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolConsolidationResponse":
        """
        Consolidate multiple memories into a single optimized record.

        Args:
            request: Consolidation request with memory IDs and strategy
            timeout_seconds: Optional timeout for consolidation operation

        Returns:
            Consolidation response with new memory ID
        """
        ...

    async def deduplicate_memories(
        self,
        memory_scope: "ProtocolMemoryMetadata",
        similarity_threshold: float = 0.95,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Remove duplicate memories based on similarity threshold.

        Args:
            memory_scope: Scope of deduplication operation
            similarity_threshold: Threshold for duplicate detection
            correlation_id: Request correlation ID

        Returns:
            Response with deduplication results
        """
        ...

    async def aggregate_data(
        self,
        aggregation_criteria: "ProtocolAggregationCriteria",
        time_window_start: Optional[str] = None,
        time_window_end: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Aggregate memory data based on specified criteria.

        Args:
            aggregation_criteria: Criteria for data aggregation
            time_window_start: Start of aggregation time window
            time_window_end: End of aggregation time window
            correlation_id: Request correlation ID

        Returns:
            Response with aggregated data
        """
        ...

    async def compress_memories(
        self,
        memory_ids: list[UUID],
        compression_algorithm: "CompressionAlgorithm",
        quality_threshold: float = 0.9,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Compress memory content using specified algorithm.

        Args:
            memory_ids: List of memories to compress
            compression_algorithm: Algorithm to use for compression
            quality_threshold: Minimum quality threshold
            correlation_id: Request correlation ID

        Returns:
            Response with compression results
        """
        ...

    async def optimize_storage(
        self,
        optimization_strategy: str,
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Optimize memory storage layout and access patterns.

        Args:
            optimization_strategy: Strategy for storage optimization
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for optimization operation

        Returns:
            Response with optimization results
        """
        ...


# === ORCHESTRATOR NODE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryOrchestratorNode(Protocol):
    """
    Protocol for memory orchestrator operations in ONEX architecture.

    Handles workflow coordination, agent management, and distributed
    memory operations across the entire ONEX cluster.
    """

    async def execute_workflow(
        self,
        request: "ProtocolWorkflowExecutionRequest",
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolWorkflowExecutionResponse":
        """
        Execute a memory workflow across multiple nodes and agents.

        Args:
            request: Workflow execution request with type and config
            timeout_seconds: Optional timeout for workflow execution

        Returns:
            Execution response with workflow ID and status
        """
        ...

    async def coordinate_agents(
        self,
        request: "ProtocolAgentCoordinationRequest",
    ) -> "ProtocolAgentCoordinationResponse":
        """
        Coordinate multiple agents for distributed memory operations.

        Args:
            request: Agent coordination request with IDs and task

        Returns:
            Coordination response with status and agent responses
        """
        ...

    async def broadcast_update(
        self,
        update_type: str,
        update_data: "ProtocolMemoryMetadata",
        target_agents: Optional[list[UUID]] = None,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Broadcast memory update to specified agents or all agents.

        Args:
            update_type: Type of update to broadcast
            update_data: Data to broadcast
            target_agents: Specific agents to notify (None = all)
            correlation_id: Request correlation ID

        Returns:
            Response with broadcast results
        """
        ...

    async def synchronize_state(
        self,
        agent_ids: list[UUID],
        synchronization_scope: "ProtocolMemoryMetadata",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Synchronize memory state across specified agents.

        Args:
            agent_ids: Agents to synchronize
            synchronization_scope: Scope of synchronization
            correlation_id: Request correlation ID

        Returns:
            Response with synchronization results
        """
        ...

    async def manage_lifecycle(
        self,
        lifecycle_policies: "ProtocolMemoryMetadata",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Manage memory lifecycle based on retention policies.

        Args:
            lifecycle_policies: Policies for memory lifecycle management
            correlation_id: Request correlation ID

        Returns:
            Response with lifecycle management results
        """
        ...


# === HEALTH AND MONITORING PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryHealthNode(Protocol):
    """
    Protocol for memory health monitoring and system observability.

    Provides health checks, metrics collection, and system status
    monitoring across all memory nodes.
    """

    async def check_health(
        self,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Perform comprehensive health check of memory system.

        Args:
            correlation_id: Request correlation ID

        Returns:
            Response with health status and diagnostics
        """
        ...

    async def collect_metrics(
        self,
        request: "ProtocolMemoryMetricsRequest",
    ) -> "ProtocolMemoryMetricsResponse":
        """
        Collect system metrics for specified time window.

        Args:
            request: Metrics collection request with time window and options

        Returns:
            Response with collected metrics and aggregation summary
        """
        ...

    async def get_status(
        self,
        include_detailed: bool = False,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryResponse":
        """
        Get current system status and operational state.

        Args:
            include_detailed: Include detailed status information
            correlation_id: Request correlation ID

        Returns:
            Response with system status
        """
        ...

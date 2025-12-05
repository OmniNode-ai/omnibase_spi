"""
Memory Protocol Domain

ONEX memory system protocol definitions for advanced memory management
following the ONEX 4-node architecture pattern:

- ProtocolMemoryEffectNode: Storage, retrieval, and persistence
- ProtocolMemoryComputeNode: Intelligence processing and semantic analysis
- ProtocolMemoryReducerNode: Consolidation, aggregation, and optimization
- ProtocolMemoryOrchestratorNode: Workflow and agent coordination
- ProtocolMemoryHealthNode: Health monitoring and observability

All protocols use pure typing.Protocol for SPI compliance.
"""

# Base Types and Literals
from .protocol_memory_base import (  # ProtocolMemoryRecordData, # CONSOLIDATED: Use ProtocolAggregatedData instead
    LiteralAgentStatus,
    LiteralAnalysisType,
    LiteralCompressionAlgorithm,
    LiteralErrorCategory,
    LiteralMemoryAccessLevel,
    LiteralWorkflowStatus,
    ProtocolAgentResponseMap,
    ProtocolAgentStatusMap,
    ProtocolAggregatedData,
    ProtocolAggregationCriteria,
    ProtocolAggregationSummary,
    ProtocolAnalysisParameters,
    ProtocolAnalysisResults,
    ProtocolCoordinationMetadata,
    ProtocolCustomMetrics,
    ProtocolErrorCategoryMap,
    ProtocolKeyValueStore,
    ProtocolMemoryErrorContext,
    ProtocolMemoryMetadata,
    ProtocolMemoryRecord,
    ProtocolPageInfo,
    ProtocolSearchFilters,
    ProtocolSearchResult,
    ProtocolWorkflowConfiguration,
)

# Composable Protocols
from .protocol_memory_composable import (
    ProtocolAgentCoordinator,
    ProtocolClusterCoordinator,
    ProtocolComputeNodeComposite,
    ProtocolLifecycleManager,
    ProtocolMemoryOrchestrator,
    ProtocolWorkflowManager,
)

# Enhanced Error Handling Protocols
from .protocol_memory_error_handling import (
    ProtocolErrorCategory,
    ProtocolMemoryCompensationAction,
    ProtocolMemoryErrorHandler,
    ProtocolMemoryHealthMonitor,
    ProtocolMemoryRetryPolicy,
    ProtocolOperationContext,
)

# Error Protocols
from .protocol_memory_errors import (
    ProtocolBatchErrorResponse,
    ProtocolBatchErrorSummary,
    ProtocolErrorRecoveryStrategy,
    ProtocolMemoryAuthorizationError,
    ProtocolMemoryCapacityError,
    ProtocolMemoryCorruptionError,
    ProtocolMemoryError,
    ProtocolMemoryErrorRecoveryResponse,
    ProtocolMemoryErrorResponse,
    ProtocolMemoryNotFoundError,
    ProtocolMemoryTimeoutError,
    ProtocolMemoryValidationError,
)

# Protocol Operations (ONEX 4-Node Architecture)
from .protocol_memory_operations import (
    ProtocolMemoryComputeNode,
    ProtocolMemoryEffectNode,
    ProtocolMemoryHealthNode,
    ProtocolMemoryOrchestratorNode,
    ProtocolMemoryReducerNode,
)

# Request Protocols
from .protocol_memory_requests import (
    ProtocolAgentCoordinationRequest,
    ProtocolAggregationRequest,
    ProtocolBatchMemoryRetrieveRequest,
    ProtocolBatchMemoryStoreRequest,
    ProtocolConsolidationRequest,
    ProtocolEmbeddingRequest,
    ProtocolMemoryListRequest,
    ProtocolMemoryMetricsRequest,
    ProtocolMemoryRequest,
    ProtocolMemoryRetrieveRequest,
    ProtocolMemoryStoreRequest,
    ProtocolPaginationRequest,
    ProtocolPatternAnalysisRequest,
    ProtocolSemanticSearchRequest,
    ProtocolStreamingMemoryRequest,
    ProtocolStreamingRetrieveRequest,
    ProtocolWorkflowExecutionRequest,
)

# Response Protocols
from .protocol_memory_responses import (
    ProtocolAgentCoordinationResponse,
    ProtocolAggregationResponse,
    ProtocolBatchMemoryRetrieveResponse,
    ProtocolBatchMemoryStoreResponse,
    ProtocolBatchOperationResult,
    ProtocolConsolidationResponse,
    ProtocolEmbeddingResponse,
    ProtocolMemoryListResponse,
    ProtocolMemoryMetrics,
    ProtocolMemoryMetricsResponse,
    ProtocolMemoryResponse,
    ProtocolMemoryRetrieveResponse,
    ProtocolMemoryStoreResponse,
    ProtocolPaginationResponse,
    ProtocolPatternAnalysisResponse,
    ProtocolSemanticSearchResponse,
    ProtocolStreamingMemoryResponse,
    ProtocolStreamingRetrieveResponse,
    ProtocolWorkflowExecutionResponse,
)

# Security Protocols
from .protocol_memory_security import (
    ProtocolAuditTrail,
    ProtocolInputValidation,
    ProtocolMemoryComplianceNode,
    ProtocolMemorySecurityContext,
    ProtocolMemorySecurityNode,
    ProtocolRateLimitConfig,
)

# Streaming and Performance Protocols
from .protocol_memory_streaming import (
    ProtocolCursorPagination,
    ProtocolMemoryCache,
    ProtocolPerformanceOptimization,
    ProtocolStreamingChunk,
    ProtocolStreamingConfig,
    ProtocolStreamingMemoryNode,
)

__all__ = [
    "LiteralAgentStatus",
    "LiteralAnalysisType",
    "LiteralCompressionAlgorithm",
    "LiteralErrorCategory",
    "LiteralMemoryAccessLevel",
    "LiteralWorkflowStatus",
    "ProtocolAgentCoordinationRequest",
    "ProtocolAgentCoordinationResponse",
    "ProtocolAgentCoordinator",
    "ProtocolAgentResponseMap",
    "ProtocolAgentStatusMap",
    "ProtocolAggregatedData",
    "ProtocolAggregationCriteria",
    "ProtocolAggregationRequest",
    "ProtocolAggregationResponse",
    "ProtocolAggregationSummary",
    "ProtocolAnalysisParameters",
    "ProtocolAnalysisResults",
    "ProtocolAuditTrail",
    "ProtocolBatchErrorResponse",
    "ProtocolBatchErrorSummary",
    "ProtocolBatchMemoryRetrieveRequest",
    "ProtocolBatchMemoryRetrieveResponse",
    "ProtocolBatchMemoryStoreRequest",
    "ProtocolBatchMemoryStoreResponse",
    "ProtocolBatchOperationResult",
    "ProtocolClusterCoordinator",
    "ProtocolComputeNodeComposite",
    "ProtocolConsolidationRequest",
    "ProtocolConsolidationResponse",
    "ProtocolCoordinationMetadata",
    "ProtocolCursorPagination",
    "ProtocolCustomMetrics",
    "ProtocolEmbeddingRequest",
    "ProtocolEmbeddingResponse",
    "ProtocolErrorCategory",
    "ProtocolErrorCategoryMap",
    "ProtocolErrorRecoveryStrategy",
    "ProtocolInputValidation",
    "ProtocolKeyValueStore",
    "ProtocolLifecycleManager",
    "ProtocolMemoryAuthorizationError",
    "ProtocolMemoryCache",
    "ProtocolMemoryCapacityError",
    "ProtocolMemoryCompensationAction",
    "ProtocolMemoryComplianceNode",
    "ProtocolMemoryComputeNode",
    "ProtocolMemoryCorruptionError",
    "ProtocolMemoryEffectNode",
    "ProtocolMemoryError",
    "ProtocolMemoryErrorContext",
    "ProtocolMemoryErrorHandler",
    "ProtocolMemoryErrorRecoveryResponse",
    "ProtocolMemoryErrorResponse",
    "ProtocolMemoryHealthMonitor",
    "ProtocolMemoryHealthNode",
    "ProtocolMemoryListRequest",
    "ProtocolMemoryListResponse",
    "ProtocolMemoryMetadata",
    "ProtocolMemoryMetrics",
    "ProtocolMemoryMetricsRequest",
    "ProtocolMemoryMetricsResponse",
    "ProtocolMemoryNotFoundError",
    "ProtocolMemoryOrchestrator",
    "ProtocolMemoryOrchestratorNode",
    "ProtocolMemoryRecord",
    # "ProtocolMemoryRecordData", # CONSOLIDATED: Use "ProtocolAggregatedData" instead
    "ProtocolMemoryReducerNode",
    "ProtocolMemoryRequest",
    "ProtocolMemoryResponse",
    "ProtocolMemoryRetrieveRequest",
    "ProtocolMemoryRetrieveResponse",
    "ProtocolMemoryRetryPolicy",
    "ProtocolMemorySecurityContext",
    "ProtocolMemorySecurityNode",
    "ProtocolMemoryStoreRequest",
    "ProtocolMemoryStoreResponse",
    "ProtocolMemoryTimeoutError",
    "ProtocolMemoryValidationError",
    "ProtocolOperationContext",
    "ProtocolPageInfo",
    "ProtocolPaginationRequest",
    "ProtocolPaginationResponse",
    "ProtocolPatternAnalysisRequest",
    "ProtocolPatternAnalysisResponse",
    "ProtocolPerformanceOptimization",
    "ProtocolRateLimitConfig",
    "ProtocolSearchFilters",
    "ProtocolSearchResult",
    "ProtocolSemanticSearchRequest",
    "ProtocolSemanticSearchResponse",
    "ProtocolStreamingChunk",
    "ProtocolStreamingConfig",
    "ProtocolStreamingMemoryNode",
    "ProtocolStreamingMemoryRequest",
    "ProtocolStreamingMemoryResponse",
    "ProtocolStreamingRetrieveRequest",
    "ProtocolStreamingRetrieveResponse",
    "ProtocolWorkflowConfiguration",
    "ProtocolWorkflowExecutionRequest",
    "ProtocolWorkflowExecutionResponse",
    "ProtocolWorkflowManager",
]

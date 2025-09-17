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
from .protocol_memory_base import (
    AgentStatus,
    AnalysisType,
    CompressionAlgorithm,
    ErrorCategory,
    MemoryAccessLevel,
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
    ProtocolErrorContext,
    ProtocolMemoryMetadata,
    ProtocolMemoryRecord,
    ProtocolMemoryRecordData,
    ProtocolPageInfo,
    ProtocolSearchFilters,
    ProtocolSearchResult,
    ProtocolWorkflowConfiguration,
    WorkflowStatus,
)

# Enhanced Error Handling Protocols
from .protocol_memory_error_handling import (
    ProtocolCompensationAction,
    ProtocolErrorCategory,
    ProtocolMemoryErrorHandler,
    ProtocolMemoryHealthMonitor,
    ProtocolOperationContext,
    ProtocolRetryPolicy,
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
    ProtocolMemorySecurityNode,
    ProtocolRateLimitConfig,
    ProtocolSecurityContext,
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
    # ONEX 4-Node Operation Protocols
    "ProtocolMemoryEffectNode",
    "ProtocolMemoryComputeNode",
    "ProtocolMemoryReducerNode",
    "ProtocolMemoryOrchestratorNode",
    "ProtocolMemoryHealthNode",
    # Type Literals
    "MemoryAccessLevel",
    "AnalysisType",
    "CompressionAlgorithm",
    "ErrorCategory",
    "AgentStatus",
    "WorkflowStatus",
    # Core Memory Protocols from Base
    "ProtocolMemoryRecord",
    "ProtocolSearchResult",
    "ProtocolSearchFilters",
    "ProtocolMemoryMetadata",
    "ProtocolWorkflowConfiguration",
    "ProtocolAnalysisParameters",
    "ProtocolAggregationCriteria",
    "ProtocolCoordinationMetadata",
    "ProtocolAnalysisResults",
    "ProtocolAggregatedData",
    "ProtocolErrorContext",
    "ProtocolPageInfo",
    "ProtocolCustomMetrics",
    "ProtocolAggregationSummary",
    "ProtocolMemoryRecordData",
    "ProtocolAgentStatusMap",
    "ProtocolAgentResponseMap",
    "ProtocolErrorCategoryMap",
    # Request Protocols
    "ProtocolMemoryRequest",
    "ProtocolMemoryStoreRequest",
    "ProtocolMemoryRetrieveRequest",
    "ProtocolMemoryListRequest",
    "ProtocolBatchMemoryStoreRequest",
    "ProtocolBatchMemoryRetrieveRequest",
    "ProtocolSemanticSearchRequest",
    "ProtocolPatternAnalysisRequest",
    "ProtocolEmbeddingRequest",
    "ProtocolConsolidationRequest",
    "ProtocolAggregationRequest",
    "ProtocolWorkflowExecutionRequest",
    "ProtocolAgentCoordinationRequest",
    "ProtocolPaginationRequest",
    "ProtocolMemoryMetricsRequest",
    "ProtocolStreamingMemoryRequest",
    "ProtocolStreamingRetrieveRequest",
    # Response Protocols
    "ProtocolMemoryResponse",
    "ProtocolMemoryStoreResponse",
    "ProtocolMemoryRetrieveResponse",
    "ProtocolMemoryListResponse",
    "ProtocolBatchMemoryStoreResponse",
    "ProtocolBatchMemoryRetrieveResponse",
    "ProtocolBatchOperationResult",
    "ProtocolSemanticSearchResponse",
    "ProtocolPatternAnalysisResponse",
    "ProtocolEmbeddingResponse",
    "ProtocolConsolidationResponse",
    "ProtocolAggregationResponse",
    "ProtocolWorkflowExecutionResponse",
    "ProtocolAgentCoordinationResponse",
    "ProtocolPaginationResponse",
    "ProtocolMemoryMetrics",
    "ProtocolMemoryMetricsResponse",
    "ProtocolStreamingMemoryResponse",
    "ProtocolStreamingRetrieveResponse",
    # Error Handling Protocols
    "ProtocolMemoryError",
    "ProtocolMemoryErrorResponse",
    "ProtocolMemoryValidationError",
    "ProtocolMemoryAuthorizationError",
    "ProtocolMemoryNotFoundError",
    "ProtocolMemoryTimeoutError",
    "ProtocolMemoryCapacityError",
    "ProtocolMemoryCorruptionError",
    "ProtocolErrorRecoveryStrategy",
    "ProtocolMemoryErrorRecoveryResponse",
    "ProtocolBatchErrorSummary",
    "ProtocolBatchErrorResponse",
    # Security Protocols
    "ProtocolSecurityContext",
    "ProtocolAuditTrail",
    "ProtocolRateLimitConfig",
    "ProtocolInputValidation",
    "ProtocolMemorySecurityNode",
    "ProtocolMemoryComplianceNode",
    # Streaming and Performance Protocols
    "ProtocolStreamingChunk",
    "ProtocolStreamingConfig",
    "ProtocolCursorPagination",
    "ProtocolStreamingMemoryNode",
    "ProtocolMemoryCache",
    "ProtocolPerformanceOptimization",
    # Enhanced Error Handling Protocols
    "ProtocolErrorCategory",
    "ProtocolRetryPolicy",
    "ProtocolCompensationAction",
    "ProtocolOperationContext",
    "ProtocolMemoryErrorHandler",
    "ProtocolMemoryHealthMonitor",
]

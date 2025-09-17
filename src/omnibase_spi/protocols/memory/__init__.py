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

# Protocol Operations (ONEX 4-Node Architecture)
from .protocol_memory_operations import (
    ProtocolMemoryComputeNode,
    ProtocolMemoryEffectNode,
    ProtocolMemoryHealthNode,
    ProtocolMemoryOrchestratorNode,
    ProtocolMemoryReducerNode,
)

# Protocol Types (Request/Response and Data Structures)
from .protocol_memory_types import (  # Core Memory Protocols; Request/Response Base Protocols; Effect Node Types; Compute Node Types; Reducer Node Types; Orchestrator Node Types
    ProtocolAgentCoordinationRequest,
    ProtocolAgentCoordinationResponse,
    ProtocolAggregationRequest,
    ProtocolAggregationResponse,
    ProtocolConsolidationRequest,
    ProtocolConsolidationResponse,
    ProtocolEmbeddingRequest,
    ProtocolEmbeddingResponse,
    ProtocolMemoryRecord,
    ProtocolMemoryRequest,
    ProtocolMemoryResponse,
    ProtocolMemoryRetrieveRequest,
    ProtocolMemoryRetrieveResponse,
    ProtocolMemoryStoreRequest,
    ProtocolMemoryStoreResponse,
    ProtocolPatternAnalysisRequest,
    ProtocolPatternAnalysisResponse,
    ProtocolSearchFilters,
    ProtocolSearchResult,
    ProtocolSemanticSearchRequest,
    ProtocolSemanticSearchResponse,
    ProtocolWorkflowExecutionRequest,
    ProtocolWorkflowExecutionResponse,
)

__all__ = [
    # ONEX 4-Node Operation Protocols
    "ProtocolMemoryEffectNode",
    "ProtocolMemoryComputeNode",
    "ProtocolMemoryReducerNode",
    "ProtocolMemoryOrchestratorNode",
    "ProtocolMemoryHealthNode",
    # Core Memory Protocols
    "ProtocolMemoryRecord",
    "ProtocolSearchResult",
    "ProtocolSearchFilters",
    # Base Request/Response Protocols
    "ProtocolMemoryRequest",
    "ProtocolMemoryResponse",
    # Effect Node Request/Response Types
    "ProtocolMemoryStoreRequest",
    "ProtocolMemoryStoreResponse",
    "ProtocolMemoryRetrieveRequest",
    "ProtocolMemoryRetrieveResponse",
    # Compute Node Request/Response Types
    "ProtocolSemanticSearchRequest",
    "ProtocolSemanticSearchResponse",
    "ProtocolPatternAnalysisRequest",
    "ProtocolPatternAnalysisResponse",
    "ProtocolEmbeddingRequest",
    "ProtocolEmbeddingResponse",
    # Reducer Node Request/Response Types
    "ProtocolConsolidationRequest",
    "ProtocolConsolidationResponse",
    "ProtocolAggregationRequest",
    "ProtocolAggregationResponse",
    # Orchestrator Node Request/Response Types
    "ProtocolWorkflowExecutionRequest",
    "ProtocolWorkflowExecutionResponse",
    "ProtocolAgentCoordinationRequest",
    "ProtocolAgentCoordinationResponse",
]

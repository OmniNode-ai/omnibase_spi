"""
ONEX Protocol Interfaces

This package contains all protocol definitions that define the contracts
for ONEX services. These protocols enable duck typing and dependency 
injection without requiring concrete implementations.

Key Protocol Domains:
    - core: System-level contracts (serialization, schema, workflow, logging, registry)
    - workflow_orchestration: Event-driven FSM orchestration with event sourcing
    - mcp: Model Context Protocol tool registration and coordination
    - event_bus: Distributed event patterns with pluggable backends
    - container: Dependency injection and service registry contracts
    - discovery: Node discovery and registration protocols
    - validation: Protocol validation and compliance utilities
    - file_handling: File type processing and metadata stamping
    - types: Consolidated type definitions for all protocol domains

Usage Examples:
    # Individual module imports (verbose but explicit)
    from omnibase_spi.protocols.core import ProtocolLogger, ProtocolCacheService
    from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
    from omnibase_spi.protocols.mcp import ProtocolMCPRegistry
    
    # Convenience imports from root protocols module
    from omnibase_spi.protocols import (
        ProtocolLogger,
        ProtocolWorkflowEventBus, 
        ProtocolMCPRegistry
    )
    
    # Types always available at types module level
    from omnibase_spi.protocols.types import LogLevel, WorkflowState
"""

# Import container versions with aliases to avoid name collision with core types
# Container protocols (19 protocols)
from omnibase_spi.protocols.container import (  # Phase 3 additions
    ContainerArtifactType,
    InjectionScope,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
    ProtocolContainerService,
    ProtocolDependencyGraph,
    ProtocolDIServiceInstance,
    ProtocolDIServiceMetadata,
    ProtocolInjectionContext,
    ProtocolServiceDependency,
    ProtocolServiceFactory,
    ProtocolServiceRegistration,
    ProtocolServiceRegistry,
    ProtocolServiceRegistryConfig,
    ProtocolServiceRegistryStatus,
    ProtocolServiceValidator,
    ServiceHealthStatus,
    ServiceLifecycle,
    ServiceResolutionStatus,
)

# Core protocols (42 protocols)
from omnibase_spi.protocols.core import (  # Phase 1 additions; Phase 3 additions
    ProtocolCacheService,
    ProtocolCacheServiceProvider,
    ProtocolCircuitBreaker,
    ProtocolCircuitBreakerEvent,
    ProtocolCircuitBreakerFactory,
    ProtocolCircuitBreakerMetrics,
    ProtocolCircuitBreakerState,
    ProtocolClientConfigProvider,
    ProtocolConfigurationError,
    ProtocolConfigurationManager,
    ProtocolConfigurationManagerFactory,
    ProtocolContractService,
    ProtocolErrorSanitizer,
    ProtocolErrorSanitizerFactory,
    ProtocolHttpAuthConfig,
    ProtocolHttpClient,
    ProtocolHttpClientConfig,
    ProtocolHttpClientProvider,
    ProtocolHttpExtendedClient,
    ProtocolHttpRequestBuilder,
    ProtocolHttpResponse,
    ProtocolHttpStreamingResponse,
    ProtocolKafkaBatchProducer,
    ProtocolKafkaClient,
    ProtocolKafkaClientConfig,
    ProtocolKafkaClientProvider,
    ProtocolKafkaConsumer,
    ProtocolKafkaConsumerConfig,
    ProtocolKafkaExtendedClient,
    ProtocolKafkaMessage,
    ProtocolKafkaProducerConfig,
    ProtocolKafkaTransactionalProducer,
    ProtocolLogger,
    ProtocolNodeConfiguration,
    ProtocolNodeConfigurationProvider,
    ProtocolNodeInfo,
    ProtocolNodeRegistry,
    ProtocolOnexNode,
    ProtocolServiceDiscovery,
    ProtocolStorageBackend,
    ProtocolStorageBackendFactory,
    ProtocolUtilsNodeConfiguration,
    ProtocolWorkflowReducer,
)

# Discovery protocols (3 protocols)
from omnibase_spi.protocols.discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
    ProtocolNodeDiscoveryRegistry,
)

# Event bus protocols (12 protocols)
from omnibase_spi.protocols.event_bus import (  # Phase 2 additions
    ProtocolAsyncEventBus,
    ProtocolEventBus,
    ProtocolEventBusAdapter,
    ProtocolEventBusContextManager,
    ProtocolEventBusInMemory,
    ProtocolEventBusService,
    ProtocolEventMessage,
    ProtocolKafkaAdapter,
    ProtocolLogEmitter,
    ProtocolRedpandaAdapter,
    ProtocolRegistryWithBus,
    ProtocolSyncEventBus,
)

# File handling protocols (3 protocols)
from omnibase_spi.protocols.file_handling import (
    ProtocolFileTypeHandler,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)

# MCP protocols (15 protocols)
from omnibase_spi.protocols.mcp import (  # Phase 3 additions
    ProtocolMCPDiscovery,
    ProtocolMCPHealthMonitor,
    ProtocolMCPMonitor,
    ProtocolMCPRegistry,
    ProtocolMCPRegistryAdmin,
    ProtocolMCPRegistryMetricsOperations,
    ProtocolMCPServiceDiscovery,
    ProtocolMCPSubsystemClient,
    ProtocolMCPSubsystemConfig,
    ProtocolMCPToolExecutor,
    ProtocolMCPToolProxy,
    ProtocolMCPToolRouter,
    ProtocolMCPToolValidator,
    ProtocolMCPValidator,
    ProtocolToolDiscoveryService,
)

# Validation protocols (4 protocols)
from omnibase_spi.protocols.validation import ValidationError  # Backward compatibility
from omnibase_spi.protocols.validation import ValidationResult  # Backward compatibility
from omnibase_spi.protocols.validation import (
    ProtocolValidationDecorator,
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)

# Workflow orchestration protocols (11 protocols)
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolEventQueryOptions,
    ProtocolEventStore,
    ProtocolEventStoreResult,
    ProtocolEventStoreTransaction,
    ProtocolNodeSchedulingResult,
    ProtocolSnapshotStore,
    ProtocolTaskSchedulingCriteria,
    ProtocolWorkflowEventBus,
    ProtocolWorkflowEventHandler,
    ProtocolWorkflowEventMessage,
    ProtocolWorkflowNodeCapability,
    ProtocolWorkflowNodeInfo,
    ProtocolWorkflowNodeRegistry,
    ProtocolWorkflowStateProjection,
    ProtocolWorkflowStateStore,
)

__all__ = [
    "ContainerArtifactType",
    "InjectionScope",
    "ProtocolArtifactContainer",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactInfo",
    "ProtocolArtifactMetadata",
    "ProtocolAsyncEventBus",
    "ProtocolCacheService",
    "ProtocolCacheServiceProvider",
    "ProtocolCircuitBreaker",
    "ProtocolCircuitBreakerEvent",
    "ProtocolCircuitBreakerFactory",
    "ProtocolCircuitBreakerMetrics",
    "ProtocolCircuitBreakerState",
    "ProtocolClientConfigProvider",
    "ProtocolConfigurationError",
    "ProtocolConfigurationManager",
    "ProtocolConfigurationManagerFactory",
    "ProtocolContainerService",
    "ProtocolContractService",
    "ProtocolDependencyGraph",
    "ProtocolDIServiceInstance",
    "ProtocolDIServiceMetadata",
    "ProtocolErrorSanitizer",
    "ProtocolErrorSanitizerFactory",
    "ProtocolEventBus",
    "ProtocolEventBusAdapter",
    "ProtocolEventBusContextManager",
    "ProtocolEventBusInMemory",
    "ProtocolEventBusService",
    "ProtocolEventMessage",
    "ProtocolEventQueryOptions",
    "ProtocolEventStore",
    "ProtocolEventStoreResult",
    "ProtocolEventStoreTransaction",
    "ProtocolFileTypeHandler",
    "ProtocolHandlerDiscovery",
    "ProtocolHandlerInfo",
    "ProtocolHttpAuthConfig",
    "ProtocolHttpClient",
    "ProtocolHttpClientConfig",
    "ProtocolHttpClientProvider",
    "ProtocolHttpExtendedClient",
    "ProtocolHttpRequestBuilder",
    "ProtocolHttpResponse",
    "ProtocolHttpStreamingResponse",
    "ProtocolInjectionContext",
    "ProtocolKafkaAdapter",
    "ProtocolKafkaBatchProducer",
    "ProtocolKafkaClient",
    "ProtocolKafkaClientConfig",
    "ProtocolKafkaClientProvider",
    "ProtocolKafkaConsumer",
    "ProtocolKafkaConsumerConfig",
    "ProtocolKafkaExtendedClient",
    "ProtocolKafkaMessage",
    "ProtocolKafkaProducerConfig",
    "ProtocolKafkaTransactionalProducer",
    "ProtocolLogEmitter",
    "ProtocolLogger",
    "ProtocolMCPDiscovery",
    "ProtocolMCPHealthMonitor",
    "ProtocolMCPMonitor",
    "ProtocolMCPRegistry",
    "ProtocolMCPRegistryAdmin",
    "ProtocolMCPRegistryMetricsOperations",
    "ProtocolMCPServiceDiscovery",
    "ProtocolMCPSubsystemClient",
    "ProtocolMCPSubsystemConfig",
    "ProtocolMCPToolExecutor",
    "ProtocolMCPToolProxy",
    "ProtocolMCPToolRouter",
    "ProtocolMCPToolValidator",
    "ProtocolMCPValidator",
    "ProtocolNodeConfiguration",
    "ProtocolNodeConfigurationProvider",
    "ProtocolNodeDiscoveryRegistry",
    "ProtocolNodeInfo",
    "ProtocolNodeRegistry",
    "ProtocolNodeSchedulingResult",
    "ProtocolOnexNode",
    "ProtocolRedpandaAdapter",
    "ProtocolRegistryWithBus",
    "ProtocolServiceDependency",
    "ProtocolServiceDiscovery",
    "ProtocolServiceFactory",
    "ProtocolServiceRegistration",
    "ProtocolServiceRegistry",
    "ProtocolServiceRegistryConfig",
    "ProtocolServiceRegistryStatus",
    "ProtocolServiceValidator",
    "ProtocolSnapshotStore",
    "ProtocolStampOptions",
    "ProtocolStorageBackend",
    "ProtocolStorageBackendFactory",
    "ProtocolSyncEventBus",
    "ProtocolTaskSchedulingCriteria",
    "ProtocolToolDiscoveryService",
    "ProtocolUtilsNodeConfiguration",
    "ProtocolValidationDecorator",
    "ProtocolValidationError",
    "ProtocolValidationOptions",
    "ProtocolValidationResult",
    "ProtocolValidator",
    "ProtocolWorkflowEventBus",
    "ProtocolWorkflowEventHandler",
    "ProtocolWorkflowEventMessage",
    "ProtocolWorkflowNodeCapability",
    "ProtocolWorkflowNodeInfo",
    "ProtocolWorkflowNodeRegistry",
    "ProtocolWorkflowReducer",
    "ProtocolWorkflowStateProjection",
    "ProtocolWorkflowStateStore",
    "ServiceHealthStatus",
    "ServiceLifecycle",
    "ServiceResolutionStatus",
    "ValidationError",
    "ValidationResult",
]

# Import moved protocols for easy access
from .file_handling.protocol_file_reader import ProtocolFileReader
from .workflow_orchestration.protocol_work_queue import (
    AssignmentStrategy,
    ProtocolWorkQueue,
    WorkQueuePriority,
)

# Add to __all__ exports
_MOVED_PROTOCOLS = [
    "ProtocolFileReader",
    "ProtocolWorkQueue",
    "WorkQueuePriority",
    "AssignmentStrategy",
]

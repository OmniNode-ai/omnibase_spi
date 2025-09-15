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

# Container protocols (18 protocols)
from omnibase_spi.protocols.container import (
    ContainerArtifactType,
    InjectionScope,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
    ProtocolDependencyGraph,
    ProtocolInjectionContext,
    ProtocolServiceDependency,
    ProtocolServiceFactory,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
    ProtocolServiceRegistration,
    ProtocolServiceRegistry,
    ProtocolServiceRegistryConfig,
    ProtocolServiceRegistryStatus,
    ProtocolServiceValidator,
    ServiceHealthStatus,
    ServiceLifecycle,
    ServiceResolutionStatus,
)

# Core protocols (32 protocols)
from omnibase_spi.protocols.core import (
    ProtocolCacheService,
    ProtocolCacheServiceProvider,
    ProtocolClientConfigProvider,
    ProtocolConfigurationError,
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
    ProtocolUtilsNodeConfiguration,
    ProtocolWorkflowReducer,
)

# Discovery protocols (3 protocols)
from omnibase_spi.protocols.discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
    ProtocolNodeDiscoveryRegistry,
)

# Event bus protocols (5 protocols)
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBus,
    ProtocolEventBusAdapter,
    ProtocolEventMessage,
    ProtocolKafkaAdapter,
    ProtocolRedpandaAdapter,
)

# File handling protocols (3 protocols)
from omnibase_spi.protocols.file_handling import (
    ProtocolFileTypeHandler,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)

# MCP protocols (12 protocols)
from omnibase_spi.protocols.mcp import (
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
    # Core protocols
    "ProtocolCacheService",
    "ProtocolCacheServiceProvider",
    "ProtocolClientConfigProvider",
    "ProtocolConfigurationError",
    "ProtocolHttpAuthConfig",
    "ProtocolHttpClient",
    "ProtocolHttpClientConfig",
    "ProtocolHttpClientProvider",
    "ProtocolHttpExtendedClient",
    "ProtocolHttpRequestBuilder",
    "ProtocolHttpResponse",
    "ProtocolHttpStreamingResponse",
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
    "ProtocolLogger",
    "ProtocolNodeConfiguration",
    "ProtocolNodeConfigurationProvider",
    "ProtocolNodeInfo",
    "ProtocolNodeRegistry",
    "ProtocolUtilsNodeConfiguration",
    "ProtocolWorkflowReducer",
    # Workflow orchestration protocols
    "ProtocolWorkflowEventBus",
    "ProtocolWorkflowEventHandler",
    "ProtocolWorkflowEventMessage",
    "ProtocolWorkflowStateProjection",
    "ProtocolNodeSchedulingResult",
    "ProtocolTaskSchedulingCriteria",
    "ProtocolWorkflowNodeCapability",
    "ProtocolWorkflowNodeInfo",
    "ProtocolWorkflowNodeRegistry",
    "ProtocolEventQueryOptions",
    "ProtocolEventStore",
    "ProtocolEventStoreResult",
    "ProtocolEventStoreTransaction",
    "ProtocolSnapshotStore",
    "ProtocolWorkflowStateStore",
    # MCP protocols
    "ProtocolMCPRegistry",
    "ProtocolMCPRegistryAdmin",
    "ProtocolMCPRegistryMetricsOperations",
    "ProtocolMCPSubsystemClient",
    "ProtocolMCPSubsystemConfig",
    "ProtocolMCPToolProxy",
    "ProtocolMCPToolRouter",
    "ProtocolMCPToolExecutor",
    "ProtocolMCPDiscovery",
    "ProtocolMCPServiceDiscovery",
    "ProtocolMCPValidator",
    "ProtocolMCPToolValidator",
    "ProtocolMCPMonitor",
    "ProtocolMCPHealthMonitor",
    # Event bus protocols
    "ProtocolEventMessage",
    "ProtocolEventBusAdapter",
    "ProtocolEventBus",
    "ProtocolKafkaAdapter",
    "ProtocolRedpandaAdapter",
    # Container protocols
    "ContainerArtifactType",
    "ProtocolArtifactMetadata",
    "ProtocolArtifactInfo",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactContainer",
    "ServiceLifecycle",
    "ServiceResolutionStatus",
    "ServiceHealthStatus",
    "InjectionScope",
    "ProtocolServiceMetadata",
    "ProtocolServiceDependency",
    "ProtocolServiceRegistration",
    "ProtocolServiceInstance",
    "ProtocolDependencyGraph",
    "ProtocolInjectionContext",
    "ProtocolServiceRegistryStatus",
    "ProtocolServiceRegistryConfig",
    "ProtocolServiceValidator",
    "ProtocolServiceFactory",
    "ProtocolServiceRegistry",
    # Discovery protocols
    "ProtocolHandlerInfo",
    "ProtocolHandlerDiscovery",
    "ProtocolNodeDiscoveryRegistry",
    # Validation protocols
    "ProtocolValidationError",
    "ProtocolValidationResult",
    "ProtocolValidator",
    "ProtocolValidationDecorator",
    "ValidationError",  # Backward compatibility
    "ValidationResult",  # Backward compatibility
    # File handling protocols
    "ProtocolFileTypeHandler",
    "ProtocolStampOptions",
    "ProtocolValidationOptions",
]

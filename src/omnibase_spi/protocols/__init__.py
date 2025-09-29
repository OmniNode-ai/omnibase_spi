"""
ONEX Protocol Interfaces

This package contains all protocol definitions that define the contracts
for ONEX services. These protocols enable duck typing and dependency
injection without requiring concrete implementations.

Architectural Overview:
    The ONEX SPI follows a strict protocol-first design where all service
    contracts are defined as typing.Protocol interfaces. This ensures:
    - Zero implementation dependencies in the SPI layer
    - Duck typing compatibility for flexible implementations
    - Strong type safety with runtime protocol checking
    - Clean dependency injection patterns

Key Protocol Domains:
    - core: System-level contracts (42 protocols)
      * Serialization, logging, node management
      * HTTP and Kafka client abstractions
      * Circuit breakers and error handling
      * Storage backends and configuration

    - workflow_orchestration: Event-driven FSM orchestration (11 protocols)
      * Event sourcing with sequence numbers and causation tracking
      * Workflow state management and projections
      * Task scheduling and node coordination

    - mcp: Model Context Protocol integration (15 protocols)
      * Multi-subsystem tool registration and discovery
      * Load balancing and failover for tool execution
      * Health monitoring and metrics collection

    - event_bus: Distributed event patterns (12 protocols)
      * Pluggable backend adapters (Kafka, Redis, in-memory)
      * Async and sync event bus implementations
      * Event message serialization and routing

    - container: Dependency injection and service registry (19 protocols)
      * Service registration, discovery, and lifecycle management
      * Dependency resolution and injection contexts
      * Artifact management and validation

    - discovery: Node discovery and registration (3 protocols)
      * Dynamic node registration and capability discovery
      * Handler discovery for file type processing

    - validation: "Protocol" validation and compliance (4 protocols)
      * Input validation and error reporting
      * Configuration validation and schema checking

    - file_handling: File type processing and metadata (3 protocols)
      * ONEX metadata stamping and validation
      * File type detection and processing

    - types: Consolidated type definitions for all domains
      * Strong typing with Literal types for enums
      * JSON-serializable data structures
      * Runtime checkable protocols

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
from omnibase_spi.protocols.types import LogLevel, LiteralWorkflowState

    # Implementation examples should be placed in your service layer packages,
    # not in the SPI layer. The SPI defines contracts only.

    # Protocol validation example
    def validate_implementation(impl: object, protocol_type: type) -> bool:
        return isinstance(impl, protocol_type)

Integration Patterns:
    1. Service Implementation:
       class ConcreteLogger(ProtocolLogger):
           def log(self, level: LogLevel, message: str) -> None:
               # Implementation here

    2. Dependency Injection:
       container.register(ProtocolLogger, ConcreteLogger())
       service = container.get(MyService)  # Auto-injects logger

    3. Protocol Validation:
       assert isinstance(my_logger, ProtocolLogger)
       logger_methods = [attr for attr in dir(ProtocolLogger)]

Best Practices:
    - Always use protocol imports rather than concrete implementations
    - Leverage type hints for better IDE support and validation
    - Use isinstance() checks for runtime protocol validation
    - Follow the protocol naming convention: "Protocol"[Domain][Purpose]
    - Implement all protocol methods in concrete classes
    - Use dependency injection containers for protocol-based services
"""

# Import container protocols for dependency injection and service management
# Container protocols (21 protocols) - Service lifecycle and dependency resolution
from omnibase_spi.protocols.container import (  # Phase 3 additions
    InjectionScope,
    LiteralContainerArtifactType,
    LiteralInjectionScope,
    LiteralOnexStatus,
    LiteralServiceLifecycle,
    LiteralServiceResolutionStatus,
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
)

# Core protocols (42 protocols) - Fundamental system contracts
# Includes logging, HTTP/Kafka clients, circuit breakers, storage, and node management
from omnibase_spi.protocols.core import (  # Phase 1 additions; Phase 3 additions
    LiteralProtocolCircuitBreakerEvent,
    LiteralProtocolCircuitBreakerState,
    ProtocolCacheService,
    ProtocolCacheServiceProvider,
    ProtocolCircuitBreaker,
    ProtocolCircuitBreakerFactory,
    ProtocolCircuitBreakerMetrics,
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
    ProtocolNodeRegistry,
    ProtocolOnexNode,
    ProtocolServiceDiscovery,
    ProtocolStorageBackend,
    ProtocolStorageBackendFactory,
    ProtocolUtilsNodeConfiguration,
    ProtocolWorkflowReducer,
)

# Discovery protocols (3 protocols) - Node and handler discovery
# Enables dynamic service discovery and handler registration
from omnibase_spi.protocols.discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
    ProtocolNodeDiscoveryRegistry,
)

# Event bus protocols (13 protocols) - Distributed messaging infrastructure
# Supports multiple backends (Kafka, Redis, in-memory) with async/sync patterns
from omnibase_spi.protocols.event_bus import (  # Phase 2 additions
    ProtocolAsyncEventBus,
    ProtocolEventBus,
    ProtocolEventBusContextManager,
    ProtocolEventBusHeaders,
    ProtocolEventBusInMemory,
    ProtocolEventBusService,
    ProtocolEventMessage,
    ProtocolKafkaAdapter,
    ProtocolLogEmitter,
    ProtocolRedpandaAdapter,
    ProtocolRegistryWithBus,
    ProtocolSyncEventBus,
)

# File handling protocols (3 protocols) - File processing and ONEX metadata
# Handles file type detection, processing, and metadata stamping
from omnibase_spi.protocols.file_handling import (
    ProtocolFileTypeHandler,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)

# MCP protocols (15 protocols) - Model Context Protocol integration
# Multi-subsystem tool registration, execution, and health monitoring
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

# Memory protocols (7 protocols) - Memory operations and workflow management
# Key-value store, workflow management, and composable memory operations
from omnibase_spi.protocols.memory import (
    ProtocolAgentCoordinator,
    ProtocolClusterCoordinator,
    ProtocolKeyValueStore,
    ProtocolLifecycleManager,
    ProtocolMemoryOrchestrator,
    ProtocolMemoryRecord,
    ProtocolWorkflowManager,
)

# Validation protocols (4 protocols) - Input validation and error handling
# Provides structured validation with error reporting and compliance checking
from omnibase_spi.protocols.validation import (
    ProtocolValidationDecorator,
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)

# Workflow orchestration protocols (11 protocols) - Event-driven FSM coordination
# Event sourcing, workflow state management, and distributed task scheduling
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolEventQueryOptions,
    ProtocolEventStore,
    ProtocolEventStoreResult,
    ProtocolEventStoreTransaction,
    ProtocolLiteralWorkflowStateProjection,
    ProtocolLiteralWorkflowStateStore,
    ProtocolNodeSchedulingResult,
    ProtocolSnapshotStore,
    ProtocolTaskSchedulingCriteria,
    ProtocolWorkflowEventBus,
    ProtocolWorkflowEventHandler,
    ProtocolWorkflowEventMessage,
    ProtocolWorkflowNodeCapability,
    ProtocolWorkflowNodeInfo,
    ProtocolWorkflowNodeRegistry,
)

__all__ = [
    "InjectionScope",
    "LiteralContainerArtifactType",
    "LiteralInjectionScope",
    "LiteralOnexStatus",
    "ProtocolAgentCoordinator",
    "ProtocolArtifactContainer",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactInfo",
    "ProtocolArtifactMetadata",
    "ProtocolAsyncEventBus",
    "ProtocolCacheService",
    "ProtocolCacheServiceProvider",
    "ProtocolCircuitBreaker",
    "LiteralProtocolCircuitBreakerEvent",
    "ProtocolCircuitBreakerFactory",
    "ProtocolCircuitBreakerMetrics",
    "LiteralProtocolCircuitBreakerState",
    "LiteralServiceLifecycle",
    "LiteralServiceResolutionStatus",
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
    "ProtocolClusterCoordinator",
    "ProtocolEventBus",
    "ProtocolEventBusAdapter",
    "ProtocolEventBusContextManager",
    "ProtocolEventBusHeaders",
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
    "ProtocolKeyValueStore",
    "ProtocolLifecycleManager",
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
    "ProtocolMemoryOrchestrator",
    "ProtocolMemoryRecord",
    "ProtocolNodeConfiguration",
    "ProtocolNodeConfigurationProvider",
    "ProtocolNodeDiscoveryRegistry",
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
    "ProtocolWorkflowManager",
    "ProtocolWorkflowNodeCapability",
    "ProtocolWorkflowNodeInfo",
    "ProtocolWorkflowNodeRegistry",
    "ProtocolWorkflowReducer",
    "ProtocolLiteralWorkflowStateProjection",
    "ProtocolLiteralWorkflowStateStore",
    "ServiceHealthStatus",
    # Moved protocols
    "LiteralAssignmentStrategy",
    "LiteralWorkQueuePriority",
    "ProtocolFileReader",
    "ProtocolWorkQueue",
]

# Import moved protocols for easy access
from .file_handling.protocol_file_reader import ProtocolFileReader
from .workflow_orchestration.protocol_work_queue import (
    LiteralAssignmentStrategy,
    LiteralWorkQueuePriority,
    ProtocolWorkQueue,
)

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

    - llm: Large Language Model integration (4 protocols)
      * LLM provider interfaces and model routing
      * Ollama client and tool provider protocols

    - semantic: Semantic processing and retrieval (2 protocols)
      * Advanced text preprocessing
      * Hybrid semantic retrieval systems

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

# Analytics protocols (1 protocol) - Analytics data collection and reporting
from omnibase_spi.protocols.analytics import ProtocolAnalyticsDataProvider

# CLI protocols (7 protocols) - Command line interface operations
from omnibase_spi.protocols.cli import (
    ProtocolCLI,
    ProtocolCLIDirFixtureCase,
    ProtocolCLIDirFixtureRegistry,
    ProtocolCLIResult,
    ProtocolCLIToolDiscovery,
    ProtocolCliWorkflow,
    ProtocolNodeCliAdapter,
)

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

# Core protocols (16 protocols) - Fundamental system contracts
# Includes serialization, logging, health monitoring, and service discovery
from omnibase_spi.protocols.core import (
    ProtocolAuditLogger,
    ProtocolCanonicalSerializer,
    ProtocolDistributedTracing,
    ProtocolErrorHandler,
    ProtocolErrorSanitizer,
    ProtocolErrorSanitizerFactory,
    ProtocolHealthDetails,
    ProtocolHealthMonitor,
    ProtocolLogger,
    ProtocolMetricsCollector,
    ProtocolPerformanceMetricsCollector,
    ProtocolRetryable,
    ProtocolServiceDiscovery,
    ProtocolTimeBasedOperations,
    ProtocolUriParser,
    ProtocolVersionManager,
)

# Discovery protocols (3 protocols) - Node and handler discovery
# Enables dynamic service discovery and handler registration
from omnibase_spi.protocols.discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
    ProtocolHandlerRegistry,
)

# Event bus protocols (13 protocols) - Distributed messaging infrastructure
# Supports multiple backends (Kafka, Redis, in-memory) with async/sync patterns
from omnibase_spi.protocols.event_bus import (  # Phase 2 additions
    ProtocolAsyncEventBus,
    ProtocolEventBus,
    ProtocolEventBusContextManager,
    ProtocolEventBusHeaders,
    ProtocolEventBusInMemory,
    ProtocolEventBusLogEmitter,
    ProtocolEventBusRegistry,
    ProtocolEventBusService,
    ProtocolEventMessage,
    ProtocolKafkaAdapter,
    ProtocolRedpandaAdapter,
    ProtocolSyncEventBus,
)

# File handling protocols (4 protocols) - File processing and ONEX metadata
# Handles file type detection, processing, and metadata stamping
from omnibase_spi.protocols.file_handling import (
    ProtocolFileProcessingTypeHandler,
    ProtocolFileReader,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)

# LLM protocols (4 protocols) - Large Language Model integration
# LLM provider interfaces, model routing, and semantic processing
from omnibase_spi.protocols.llm import (
    ProtocolLLMProvider,
    ProtocolLLMToolProvider,
    ProtocolModelRouter,
    ProtocolOllamaClient,
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

# Networking protocols (6 protocols) - HTTP, Kafka, circuit breaker, and communication protocols
from omnibase_spi.protocols.networking import (
    ProtocolCircuitBreaker,
    ProtocolCommunicationBridge,
    ProtocolHttpClient,
    ProtocolHttpExtendedClient,
    ProtocolKafkaClient,
    ProtocolKafkaExtendedClient,
)

# Node protocols (4 protocols) - Node management, configuration, and registry
from omnibase_spi.protocols.node import (
    ProtocolNodeConfiguration,
    ProtocolNodeRegistry,
    ProtocolNodeRunner,
    ProtocolUtilsNodeConfiguration,
)

# ONEX protocols (11 protocols) - ONEX platform specific protocols
from omnibase_spi.protocols.onex import (
    ProtocolOnexContractData,
    ProtocolOnexEnvelope,
    ProtocolOnexMetadata,
    ProtocolOnexNode,
    ProtocolOnexReply,
    ProtocolOnexSchema,
    ProtocolOnexSecurityContext,
    ProtocolOnexValidation,
    ProtocolOnexValidationReport,
    ProtocolOnexValidationResult,
    ProtocolToolToolOnexVersionLoader,
)

# Schema protocols (2 protocols) - Schema loading and validation
from omnibase_spi.protocols.schema import (
    ProtocolSchemaLoader,
    ProtocolTrustedSchemaLoader,
)

# Semantic protocols (2 protocols) - Semantic processing and retrieval
# Advanced text preprocessing and hybrid semantic retrieval systems
from omnibase_spi.protocols.semantic import (
    ProtocolAdvancedPreprocessor,
    ProtocolHybridRetriever,
)

# Security protocols (2 protocols) - Security event and detection interfaces
# Breaking circular import dependencies for security models
from omnibase_spi.protocols.security import (
    ProtocolDetectionMatch,
    ProtocolSecurityEvent,
)

# Storage protocols (3 protocols) - Data storage and persistence
from omnibase_spi.protocols.storage import (
    ProtocolDatabaseConnection,
    ProtocolStorageBackend,
    ProtocolStorageBackendFactory,
)

# Validation protocols (4 protocols) - Input validation and error handling
# Provides structured validation with error reporting and compliance checking
from omnibase_spi.protocols.validation import (
    ProtocolValidationDecorator,
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)

# Workflow orchestration protocols (14 protocols) - Event-driven FSM coordination
# Event sourcing, workflow state management, and distributed task scheduling
from omnibase_spi.protocols.workflow_orchestration import (
    LiteralAssignmentStrategy,
    LiteralWorkQueuePriority,
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
    ProtocolWorkQueue,
)

# Test protocols (2 protocols) - Testing frameworks and testable components
# NOTE: Commented out for production builds as test module is excluded from package
# from omnibase_spi.protocols.test import ProtocolTestable, ProtocolTestableCLI


__all__ = [
    "ProtocolCLI",
    "ProtocolCLIResult",
    "ProtocolCLIDirFixtureCase",
    "ProtocolCLIDirFixtureRegistry",
    "ProtocolCLIToolDiscovery",
    "ProtocolCliWorkflow",
    "ProtocolLogger",
    "ProtocolNodeCliAdapter",
    "ProtocolCommunicationBridge",
    "ProtocolHttpClient",
    "ProtocolHttpExtendedClient",
    "ProtocolKafkaClient",
    "ProtocolKafkaExtendedClient",
    "ProtocolNodeConfiguration",
    "ProtocolUtilsNodeConfiguration",
    "ProtocolNodeRegistry",
    "ProtocolNodeRunner",
    # "ProtocolTestable",  # Excluded from production builds
    # "ProtocolTestableCLI",  # Excluded from production builds
    "ProtocolAnalyticsDataProvider",
    "ProtocolOnexContractData",
    "ProtocolOnexEnvelope",
    "ProtocolOnexMetadata",
    "ProtocolOnexNode",
    "ProtocolOnexReply",
    "ProtocolOnexSchema",
    "ProtocolOnexSecurityContext",
    "ProtocolOnexValidation",
    "ProtocolOnexValidationReport",
    "ProtocolOnexValidationResult",
    "ProtocolToolToolOnexVersionLoader",
    "ProtocolSchemaLoader",
    "ProtocolTrustedSchemaLoader",
    "ProtocolStorageBackend",
    "ProtocolStorageBackendFactory",
    "ProtocolDatabaseConnection",
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
    "ProtocolEventBusLogEmitter",
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
    "ProtocolHandlerRegistry",
    "ProtocolNodeRegistry",
    "ProtocolNodeSchedulingResult",
    "ProtocolRedpandaAdapter",
    "ProtocolEventBusRegistry",
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
    # LLM protocols
    "ProtocolLLMProvider",
    "ProtocolLLMToolProvider",
    "ProtocolModelRouter",
    "ProtocolOllamaClient",
    # Semantic protocols
    "ProtocolAdvancedPreprocessor",
    "ProtocolHybridRetriever",
    # Security protocols
    "ProtocolDetectionMatch",
    "ProtocolSecurityEvent",
    # Moved protocols
    "LiteralAssignmentStrategy",
    "LiteralWorkQueuePriority",
    "ProtocolFileReader",
    "ProtocolWorkQueue",
    # CLI protocol models
    "ModelDiscoveredTool",
    "ModelToolImplementation",
    "ModelToolHealthStatus",
    "ModelCliDiscoveryStats",
]

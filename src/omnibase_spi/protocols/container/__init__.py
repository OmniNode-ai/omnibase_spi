"""
Container Protocols - SPI Interface Exports.

Dependency injection, service registry, and artifact container protocols:
- Comprehensive service registry for dependency injection
- Artifact container for package/tool management

Note: Container service types are prefixed with "DI" to distinguish from
general service discovery types in core_types:
- ProtocolDIServiceInstance: DI container service instances
- ProtocolDIServiceMetadata: DI container service metadata
- ProtocolServiceInstance (core_types): General service discovery
- ProtocolServiceMetadata (core_types): General service discovery metadata
"""

from .protocol_artifact_container import (
    LiteralContainerArtifactType,
    LiteralOnexStatus,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
)
from .protocol_cache_service import ProtocolCacheService
from .protocol_client_config import (
    ProtocolClientConfigProvider,
    ProtocolEventBusClientConfig,
    ProtocolEventBusConsumerConfig,
    ProtocolEventBusProducerConfig,
)
from .protocol_configuration_manager import ProtocolConfigurationManager
from .protocol_connection_manageable import ProtocolConnectionManageable
from .protocol_container import ProtocolContainer
from .protocol_container_service import ProtocolContainerService

# Export DI-specific protocols with clear naming to avoid collision with core types
from .protocol_service_registry import (
    InjectionScope,
    LiteralInjectionScope,
    LiteralServiceLifecycle,
    LiteralServiceResolutionStatus,
    ProtocolDependencyGraph,
    ProtocolInjectionContext,
    ProtocolRegistryServiceInstance as ProtocolDIServiceInstance,
    ProtocolServiceDependency,
    ProtocolServiceFactory,
    ProtocolServiceRegistration,
    ProtocolServiceRegistrationMetadata as ProtocolDIServiceMetadata,
    ProtocolServiceRegistry,
    ProtocolServiceRegistryConfig,
    ProtocolServiceRegistryStatus,
    ProtocolServiceValidator,
    ServiceHealthStatus,
)
from .protocol_service_resolver import ProtocolServiceResolver

__all__ = [
    "InjectionScope",
    "LiteralContainerArtifactType",
    "LiteralInjectionScope",
    "LiteralOnexStatus",
    "LiteralServiceLifecycle",
    "LiteralServiceResolutionStatus",
    "ProtocolArtifactContainer",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactInfo",
    "ProtocolArtifactMetadata",
    "ProtocolCacheService",
    "ProtocolClientConfigProvider",
    "ProtocolConfigurationManager",
    "ProtocolConnectionManageable",
    "ProtocolContainer",
    "ProtocolContainerService",
    "ProtocolDIServiceInstance",
    "ProtocolDIServiceMetadata",
    "ProtocolDependencyGraph",
    # EventBus config protocols
    "ProtocolEventBusClientConfig",
    "ProtocolEventBusConsumerConfig",
    "ProtocolEventBusProducerConfig",
    "ProtocolInjectionContext",
    "ProtocolServiceDependency",
    "ProtocolServiceFactory",
    "ProtocolServiceRegistration",
    "ProtocolServiceRegistry",
    "ProtocolServiceRegistryConfig",
    "ProtocolServiceRegistryStatus",
    "ProtocolServiceResolver",
    "ProtocolServiceValidator",
    "ServiceHealthStatus",
]

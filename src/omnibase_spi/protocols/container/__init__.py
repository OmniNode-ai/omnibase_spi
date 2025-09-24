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
    ContainerArtifactType,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
)
from .protocol_container_service import ProtocolContainerService

# Export DI-specific protocols with clear naming to avoid collision with core types
from .protocol_service_registry import (
    InjectionScope,
    ProtocolDependencyGraph,
    ProtocolInjectionContext,
    ProtocolServiceDependency,
    ProtocolServiceFactory,
)
from .protocol_service_registry import (
    ProtocolServiceInstance as ProtocolDIServiceInstance,
)
from .protocol_service_registry import (
    ProtocolServiceMetadata as ProtocolDIServiceMetadata,
)
from .protocol_service_registry import (
    ProtocolServiceRegistration,
    ProtocolServiceRegistry,
    ProtocolServiceRegistryConfig,
    ProtocolServiceRegistryStatus,
    ProtocolServiceValidator,
    ServiceHealthStatus,
    ServiceLifecycle,
    ServiceResolutionStatus,
)

__all__ = [
    "ContainerArtifactType",
    "InjectionScope",
    "ProtocolArtifactContainer",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactInfo",
    "ProtocolArtifactMetadata",
    "ProtocolContainerService",
    "ProtocolDependencyGraph",
    "ProtocolDIServiceInstance",
    "ProtocolDIServiceMetadata",
    "ProtocolInjectionContext",
    "ProtocolServiceDependency",
    "ProtocolServiceFactory",
    "ProtocolServiceRegistration",
    "ProtocolServiceRegistry",
    "ProtocolServiceRegistryConfig",
    "ProtocolServiceRegistryStatus",
    "ProtocolServiceValidator",
    "ServiceHealthStatus",
    "ServiceLifecycle",
    "ServiceResolutionStatus",
]

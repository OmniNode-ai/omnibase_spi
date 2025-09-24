"""
Container Protocols - SPI Interface Exports.

Dependency injection, service registry, and artifact container protocols:
- Comprehensive service registry for dependency injection
- Artifact container for package/tool management
"""

from .protocol_artifact_container import (
    ContainerArtifactType,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
)
from .protocol_container_service import ProtocolContainerService

# Provide aliases to avoid name collision with core types
from .protocol_service_registry import (
    InjectionScope,
    ProtocolDependencyGraph,
    ProtocolInjectionContext,
    ProtocolServiceDependency,
    ProtocolServiceFactory,
)
from .protocol_service_registry import ProtocolServiceInstance
from .protocol_service_registry import (
    ProtocolServiceInstance as ProtocolDIServiceInstance,
)
from .protocol_service_registry import ProtocolServiceMetadata
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
    "ProtocolServiceInstance",
    "ProtocolServiceMetadata",
    "ProtocolServiceRegistration",
    "ProtocolServiceRegistry",
    "ProtocolServiceRegistryConfig",
    "ProtocolServiceRegistryStatus",
    "ProtocolServiceValidator",
    "ServiceHealthStatus",
    "ServiceLifecycle",
    "ServiceResolutionStatus",
]

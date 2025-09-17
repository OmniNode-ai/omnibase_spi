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
from .protocol_service_registry import (
    InjectionScope,
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

__all__ = [
    # Container service protocols
    "ProtocolContainerService",
    # Artifact container types
    "ContainerArtifactType",
    "ProtocolArtifactMetadata",
    "ProtocolArtifactInfo",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactContainer",
    # Comprehensive service registry types
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
]

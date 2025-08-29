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
from .protocol_service_registry import (
    InjectionScope,
    ProtocolDependencyGraph,
    ProtocolInjectionContext,
    ProtocolServiceDependency,
    ProtocolServiceFactory,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
    ProtocolServiceRegistry,
    ProtocolServiceRegistration,
    ProtocolServiceRegistryConfig,
    ProtocolServiceRegistryStatus,
    ProtocolServiceValidator,
    ServiceHealthStatus,
    ServiceLifecycle,
    ServiceRegistrationStatus,
    ServiceResolutionStatus,
)

__all__ = [
    # Artifact container types
    "ContainerArtifactType",
    "ProtocolArtifactMetadata",
    "ProtocolArtifactInfo",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactContainer",
    # Comprehensive service registry types
    "ServiceLifecycle",
    "ServiceRegistrationStatus",
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

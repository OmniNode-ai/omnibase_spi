"""
Container Protocols - SPI Interface Exports.

Dependency injection, service registry, and artifact container protocols:
- Service registry for dependency injection
- Artifact container for package/tool management
"""

from .protocol_artifact_container import (
    ContainerArtifactType,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
)

__all__ = [
    # Artifact container types
    "ContainerArtifactType",
    "ProtocolArtifactMetadata",
    "ProtocolArtifactInfo",
    "ProtocolArtifactContainerStatus",
    "ProtocolArtifactContainer",
]

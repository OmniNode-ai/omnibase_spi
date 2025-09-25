# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.276226'
# description: Stamped by NodePython
# entrypoint: python://protocol_artifact_container
# hash: a08694d4a43c239f7653f23bcaf0645dcc77cc1b8afeeaec3f1bceecfafc579b
# last_modified_at: '2025-08-29T00:00:00.000000+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_artifact_container.py
# namespace: python://omnibase_spi.protocol.protocol_artifact_container
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8664087b-f756-490a-914c-4bb9c21cac98
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Shared Artifact Container Protocol.

Provides a cross-cutting interface for artifact container functionality without exposing
node-specific implementation details. This protocol abstracts container operations
to enable testing and cross-node container access while maintaining proper
architectural boundaries.
"""

from typing import Literal, Optional, Protocol

from omnibase_spi.protocols.types.core_types import ProtocolSemVer

# Status type for ONEX systems
LiteralOnexStatus = Literal["ACTIVE", "INACTIVE", "ERROR", "UNKNOWN"]


# Container artifact types - using Literal instead of Enum
LiteralContainerArtifactType = Literal[
    "nodes", "cli_tools", "runtimes", "adapters", "contracts", "packages"
]


class ProtocolArtifactMetadata(Protocol):
    """Protocol for artifact metadata."""

    description: Optional[str]
    author: Optional[str]
    created_at: Optional[str]
    last_modified_at: Optional[str]


class ProtocolArtifactInfo(Protocol):
    """Protocol for artifact information."""

    name: str
    version: ProtocolSemVer
    artifact_type: LiteralContainerArtifactType
    path: str
    metadata: ProtocolArtifactMetadata
    is_wip: bool


class ProtocolArtifactContainerStatus(Protocol):
    """Protocol for artifact container status information."""

    status: LiteralOnexStatus
    message: str
    artifact_count: int
    valid_artifact_count: int
    invalid_artifact_count: int
    wip_artifact_count: int
    artifact_types_found: list[LiteralContainerArtifactType]


class ProtocolArtifactContainer(Protocol):
    """
    Cross-cutting artifact container protocol.

    Provides an interface for artifact container operations that can be implemented
    by different container backends (artifact loader node, mock containers, etc.)
    without exposing implementation-specific details.
    """

    def get_status(self) -> ProtocolArtifactContainerStatus:
        """Get container loading status and statistics."""
        ...

    def get_artifacts(self) -> list[ProtocolArtifactInfo]:
        """Get all artifacts in the container."""
        ...

    def get_artifacts_by_type(
        self, artifact_type: LiteralContainerArtifactType
    ) -> list[ProtocolArtifactInfo]:
        """Get artifacts filtered by type."""
        ...

    def get_artifact_by_name(
        self, name: str, artifact_type: Optional[LiteralContainerArtifactType] = None
    ) -> ProtocolArtifactInfo:
        """
        Get a specific artifact by name.

        Args:
            name: Artifact name to search for
            artifact_type: Optional type filter

        Returns:
            ProtocolArtifactInfo: The found artifact

        Raises:
            OnexError: If artifact is not found
        """
        ...

    def has_artifact(
        self, name: str, artifact_type: Optional[LiteralContainerArtifactType] = None
    ) -> bool:
        """Check if an artifact exists in the container."""
        ...

# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.276226'
# description: Stamped by ToolPython
# entrypoint: python://protocol_registry
# hash: a08694d4a43c239f7653f23bcaf0645dcc77cc1b8afeeaec3f1bceecfafc579b
# last_modified_at: '2025-05-29T14:14:00.324643+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_registry.py
# namespace: python://omnibase.protocol.protocol_registry
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
Shared Registry Protocol.

Provides a cross-cutting interface for registry functionality without exposing
node-specific implementation details. This protocol abstracts registry operations
to enable testing and cross-node registry access while maintaining proper
architectural boundaries.
"""

from typing import List, Literal, Optional, Protocol

from omnibase.protocols.types.core_types import ProtocolSemVer

# Status type for ONEX systems
OnexStatus = Literal["ACTIVE", "INACTIVE", "ERROR", "UNKNOWN"]


# Registry artifact types - using Literal instead of Enum
RegistryArtifactType = Literal[
    "nodes", "cli_tools", "runtimes", "adapters", "contracts", "packages"
]


class ProtocolRegistryArtifactMetadata(Protocol):
    """Protocol for registry artifact metadata."""

    description: Optional[str]
    author: Optional[str]
    created_at: Optional[str]
    last_modified_at: Optional[str]


class ProtocolRegistryArtifactInfo(Protocol):
    """Protocol for registry artifact information."""

    name: str
    version: ProtocolSemVer
    artifact_type: RegistryArtifactType
    path: str
    metadata: ProtocolRegistryArtifactMetadata
    is_wip: bool


class ProtocolRegistryStatus(Protocol):
    """Protocol for registry status information."""

    status: OnexStatus
    message: str
    artifact_count: int
    valid_artifact_count: int
    invalid_artifact_count: int
    wip_artifact_count: int
    artifact_types_found: List[RegistryArtifactType]


class ProtocolRegistry(Protocol):
    """
    Cross-cutting registry protocol.

    Provides an interface for registry operations that can be implemented
    by different registry backends (registry loader node, mock registries, etc.)
    without exposing implementation-specific details.
    """

    def get_status(self) -> ProtocolRegistryStatus:
        """Get registry loading status and statistics."""
        ...

    def get_artifacts(self) -> List[ProtocolRegistryArtifactInfo]:
        """Get all artifacts in the registry."""
        ...

    def get_artifacts_by_type(
        self, artifact_type: RegistryArtifactType
    ) -> List[ProtocolRegistryArtifactInfo]:
        """Get artifacts filtered by type."""
        ...

    def get_artifact_by_name(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> ProtocolRegistryArtifactInfo:
        """
        Get a specific artifact by name.

        Args:
            name: Artifact name to search for
            artifact_type: Optional type filter

        Returns:
            ProtocolRegistryArtifactInfo: The found artifact

        Raises:
            OnexError: If artifact is not found
        """
        ...

    def has_artifact(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> bool:
        """Check if an artifact exists in the registry."""
        ...

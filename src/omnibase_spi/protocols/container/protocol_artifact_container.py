"""
Shared Artifact Container Protocol.

Provides a cross-cutting interface for artifact container functionality without exposing
node-specific implementation details. This protocol abstracts container operations
to enable testing and cross-node container access while maintaining proper
architectural boundaries.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolSemVer

LiteralOnexStatus = Literal["ACTIVE", "INACTIVE", "ERROR", "UNKNOWN"]
LiteralContainerArtifactType = Literal[
    "nodes", "cli_tools", "runtimes", "adapters", "contracts", "packages"
]


@runtime_checkable
class ProtocolArtifactMetadata(Protocol):
    """
    Protocol for artifact metadata.

    Defines the interface for metadata associated with ONEX artifacts including
    creation timestamps, authorship, and modification tracking. This protocol
    enables consistent metadata handling across different artifact types and
    container implementations.

    Attributes:
        description: Human-readable description of the artifact purpose and functionality
        author: Creator or maintainer of the artifact
        created_at: ISO timestamp of artifact creation
        last_modified_at: ISO timestamp of last modification

    Example:
        ```python
        @runtime_checkable
        class ArtifactMetadataImpl:
            description: str | None = "User authentication service"
            author: str | None = "security-team"
            created_at: str | None = "2025-01-15T10:30:00Z"
            last_modified_at: str | None = "2025-01-20T14:45:00Z"

        # Usage with protocol validation
        metadata: ProtocolArtifactMetadata = ArtifactMetadataImpl()
        ```
    """

    description: str | None
    author: str | None
    created_at: str | None
    last_modified_at: str | None


@runtime_checkable
class ProtocolArtifactInfo(Protocol):
    """
    Protocol for artifact information.

    Defines the interface for comprehensive artifact information including versioning,
    type classification, file system location, and work-in-progress status. This
    protocol enables consistent artifact identification and management across the
    ONEX ecosystem.

    Attributes:
        name: Unique identifier for the artifact within its type
        version: Semantic version following SemVer specification
        artifact_type: Classification of artifact (nodes, cli_tools, etc.)
        path: File system path to artifact definition or implementation
        metadata: Artifact metadata including authorship and timestamps
        is_wip: Flag indicating work-in-progress status for development tracking

    Example:
        ```python
        @runtime_checkable
        class ArtifactInfoImpl:
            name: str | None = None
            version: "ProtocolSemVer" = "1.2.0"
            artifact_type: LiteralContainerArtifactType = "nodes"
            path: str | None = None
            metadata: ProtocolArtifactMetadata = metadata_impl
            is_wip: bool | None = None

        # Usage in artifact discovery
        artifact: ProtocolArtifactInfo = ArtifactInfoImpl()
        if not artifact.is_wip and artifact.artifact_type == "nodes":
            process_artifact(artifact)
        ```
    """

    name: str
    version: "ProtocolSemVer"
    artifact_type: LiteralContainerArtifactType
    path: str
    metadata: "ProtocolArtifactMetadata"
    is_wip: bool


@runtime_checkable
class ProtocolArtifactContainerStatus(Protocol):
    """Protocol for artifact container status information."""

    status: LiteralOnexStatus
    message: str
    artifact_count: int
    valid_artifact_count: int
    invalid_artifact_count: int
    wip_artifact_count: int
    artifact_types_found: list[LiteralContainerArtifactType]


@runtime_checkable
class ProtocolArtifactContainer(Protocol):
    """
    Cross-cutting artifact container protocol.

    Provides an interface for artifact container operations that can be implemented
    by different container backends (artifact loader node, mock containers, etc.)
    without exposing implementation-specific details.
    """

    async def get_status(self) -> ProtocolArtifactContainerStatus: ...

    async def get_artifacts(self) -> list["ProtocolArtifactInfo"]: ...

    async def get_artifacts_by_type(
        self, artifact_type: LiteralContainerArtifactType
    ) -> list["ProtocolArtifactInfo"]: ...

    async def get_artifact_by_name(
        self, name: str, artifact_type: "LiteralContainerArtifactType | None" = None
    ) -> ProtocolArtifactInfo: ...

    def has_artifact(
        self, name: str, artifact_type: "LiteralContainerArtifactType | None" = None
    ) -> bool: ...

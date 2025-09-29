"""
Shared Artifact Container Protocol.

Provides a cross-cutting interface for artifact container functionality without exposing
node-specific implementation details. This protocol abstracts container operations
to enable testing and cross-node container access while maintaining proper
architectural boundaries.
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ProtocolSemVer

LiteralOnexStatus = Literal["ACTIVE", "INACTIVE", "ERROR", "UNKNOWN"]
LiteralContainerArtifactType = Literal[
    "nodes", "cli_tools", "runtimes", "adapters", "contracts", "packages"
]


@runtime_checkable
class ProtocolArtifactMetadata(Protocol):
    """Protocol for artifact metadata."""

    description: str | None
    author: str | None
    created_at: str | None
    last_modified_at: str | None


@runtime_checkable
class ProtocolArtifactInfo(Protocol):
    """Protocol for artifact information."""

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

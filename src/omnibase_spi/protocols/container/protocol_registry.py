"""
Shared Registry Protocol.

Provides a cross-cutting interface for registry functionality without exposing
node-specific implementation details. This protocol abstracts registry operations
to enable testing and cross-node registry access while maintaining proper
architectural boundaries.
"""

from typing import TYPE_CHECKING, Protocol, TypeAlias, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.container.protocol_artifact_container import (
        ProtocolArtifactMetadata,
    )
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue

from omnibase_spi.protocols.container.protocol_artifact_container import (
    LiteralContainerArtifactType,
)

# Type alias for backward compatibility
RegistryArtifactType: TypeAlias = LiteralContainerArtifactType

# Registry artifact type constants (deprecated - use LiteralContainerArtifactType)
ARTIFACT_TYPE_NODES = "nodes"
ARTIFACT_TYPE_CLI_TOOLS = "cli_tools"
ARTIFACT_TYPE_RUNTIMES = "runtimes"
ARTIFACT_TYPE_ADAPTERS = "adapters"
ARTIFACT_TYPE_CONTRACTS = "contracts"
ARTIFACT_TYPE_PACKAGES = "packages"


@runtime_checkable
class ProtocolRegistryArtifactInfo(Protocol):
    """
    Protocol for registry artifact information.

    Defines the interface for comprehensive artifact information including versioning,
    type classification, file system location, and work-in-progress status. This
    protocol enables consistent artifact identification and management across the
    ONEX ecosystem.

    Note: This protocol is deprecated in favor of ProtocolArtifactInfo from
    protocol_artifact_container.py for consistency across the container domain.

    Attributes:
        name: Unique identifier for the artifact within its type
        version: Version string following semantic versioning
        artifact_type: Classification of artifact (nodes, cli_tools, etc.)
        path: File system path to artifact definition or implementation
        metadata: Artifact metadata including authorship and timestamps
        is_wip: Flag indicating work-in-progress status for development tracking

    Example:
        ```python
        @runtime_checkable
        class RegistryArtifactInfoImpl:
            name: str | None = None
            version: str | None = None
            artifact_type: RegistryArtifactType = ARTIFACT_TYPE_NODES
            path: str | None = None
            metadata: "ProtocolArtifactMetadata" = metadata_impl
            is_wip: bool | None = None

        # Usage in registry operations
        artifact: ProtocolRegistryArtifactInfo = RegistryArtifactInfoImpl()
        if not artifact.is_wip and artifact.artifact_type == ARTIFACT_TYPE_NODES:
            register_artifact(artifact)
        ```
    """

    name: str
    version: str
    artifact_type: RegistryArtifactType
    path: str
    metadata: "ProtocolArtifactMetadata"
    is_wip: bool


@runtime_checkable
class ProtocolRegistryStatus(Protocol):
    """
    Protocol for registry status information.

    Defines the interface for comprehensive registry status reporting including
    artifact counts, validation results, and type distribution. This protocol
    enables monitoring and health checks for registry operations across the
    ONEX ecosystem.

    Attributes:
        status: Overall status of the registry (loading, ready, error, etc.)
        message: Human-readable status message for diagnostics
        artifact_count: Total number of artifacts in the registry
        valid_artifact_count: Number of artifacts passing validation
        invalid_artifact_count: Number of artifacts failing validation
        wip_artifact_count: Number of work-in-progress artifacts
        artifact_types_found: List of artifact types present in registry

    Example:
        ```python
        @runtime_checkable
        class RegistryStatusImpl:
            status: str | None = None
            message: str | None = None
            artifact_count: int | None = None
            valid_artifact_count: int | None = None
            invalid_artifact_count: int | None = None
            wip_artifact_count: int | None = None
            artifact_types_found: list[RegistryArtifactType] = [
                ARTIFACT_TYPE_NODES, ARTIFACT_TYPE_CLI_TOOLS, ARTIFACT_TYPE_PACKAGES
            ]

        # Usage in health monitoring
        status: ProtocolRegistryStatus = RegistryStatusImpl()
        if status.status == "ready" and status.invalid_artifact_count == 0:
            start_processing_artifacts()
        else:
            log_registry_issues(status)
        ```

    Health Monitoring:
        The status protocol enables comprehensive health monitoring including
        validation success rates, work-in-progress tracking, and type distribution
        analysis for operational intelligence.
    """

    status: str
    message: str
    artifact_count: int
    valid_artifact_count: int
    invalid_artifact_count: int
    wip_artifact_count: int
    artifact_types_found: list[RegistryArtifactType]


@runtime_checkable
class ProtocolRegistry(Protocol):
    """
    Cross-cutting registry protocol.

    Provides an interface for registry operations that can be implemented
    by different registry backends (registry loader node, mock registries, etc.)
    without exposing implementation-specific details.
    """

    async def get_status(self) -> "ProtocolRegistryStatus":
        """Get registry loading status and statistics."""
        ...

    async def get_artifacts(self) -> list["ProtocolRegistryArtifactInfo"]:
        """Get all artifacts in the registry."""
        ...

    async def get_artifacts_by_type(
        self,
        artifact_type: RegistryArtifactType,
    ) -> list["ProtocolRegistryArtifactInfo"]:
        """Get artifacts filtered by type."""
        ...

    async def get_artifact_by_name(
        self,
        name: str,
        artifact_type: RegistryArtifactType | None = None,
    ) -> "ProtocolRegistryArtifactInfo":
        """
        Get a specific artifact by name.

        Args:
            name: Artifact name to search for
            artifact_type: Optional type filter

        Returns:
            ProtocolRegistryArtifactInfo: The found artifact

        Raises:
            ValueError: If artifact is not found
        """
        ...

    async def has_artifact(
        self,
        name: str,
        artifact_type: RegistryArtifactType | None = None,
    ) -> bool:
        """Check if an artifact exists in the registry."""
        ...

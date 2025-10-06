"""
Shared Registry Protocol.

Provides a cross-cutting interface for registry functionality without exposing
node-specific implementation details. This protocol abstracts registry operations
to enable testing and cross-node registry access while maintaining proper
architectural boundaries.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


# Protocol-compatible literal type for registry artifact types
RegistryArtifactType = str

# Registry artifact type constants
ARTIFACT_TYPE_NODES = "nodes"
ARTIFACT_TYPE_CLI_TOOLS = "cli_tools"
ARTIFACT_TYPE_RUNTIMES = "runtimes"
ARTIFACT_TYPE_ADAPTERS = "adapters"
ARTIFACT_TYPE_CONTRACTS = "contracts"
ARTIFACT_TYPE_PACKAGES = "packages"


@runtime_checkable
class ProtocolRegistryArtifactMetadata(Protocol):
    """
    Protocol for registry artifact metadata.

    Defines the interface for metadata associated with registry artifacts including
    creation timestamps, authorship, and modification tracking. This protocol
    enables consistent metadata handling across different artifact types and
    registry implementations.

    Attributes:
        description: Human-readable description of the artifact purpose and functionality
        author: Creator or maintainer of the artifact
        created_at: ISO timestamp of artifact creation
        last_modified_at: ISO timestamp of last modification

    Example:
        ```python
        @runtime_checkable
        class RegistryMetadataImpl:
            description: str | None = "Workflow orchestrator node"
            author: str | None = "workflow-team"
            created_at: str | None = "2025-01-15T10:30:00Z"
            last_modified_at: str | None = "2025-01-20T14:45:00Z"

        # Usage with protocol validation
        metadata: ProtocolRegistryArtifactMetadata = RegistryMetadataImpl()
        ```
    """

    description: str | None
    author: str | None
    created_at: str | None
    last_modified_at: str | None


@runtime_checkable
class ProtocolRegistryArtifactInfo(Protocol):
    """
    Protocol for registry artifact information.

    Defines the interface for comprehensive artifact information including versioning,
    type classification, file system location, and work-in-progress status. This
    protocol enables consistent artifact identification and management across the
    ONEX ecosystem.

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
            name: str = "workflow-orchestrator"
            version: str = "1.2.0"
            artifact_type: RegistryArtifactType = ARTIFACT_TYPE_NODES
            path: str = "/nodes/workflow/orchestrator.py"
            metadata: ProtocolRegistryArtifactMetadata = metadata_impl
            is_wip: bool = False

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
    metadata: "ProtocolRegistryArtifactMetadata"
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
            status: str = "ready"
            message: str = "Registry loaded successfully with 42 artifacts"
            artifact_count: int = 42
            valid_artifact_count: int = 38
            invalid_artifact_count: int = 2
            wip_artifact_count: int = 2
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

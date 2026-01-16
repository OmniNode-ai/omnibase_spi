"""
Node protocol types for ONEX SPI interfaces.

Domain: Node configuration, metadata, results, and related data structures.

This module contains protocol definitions for node-related data objects including:
- ProtocolNodeConfigurationData for node execution parameters and settings
- ProtocolNodeMetadata for node identification and type classification
- ProtocolNodeMetadataBlock for comprehensive node metadata blocks
- ProtocolNodeInfoLike marker protocol for node information compatibility
- ProtocolNodeResult for comprehensive node processing results
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ProtocolErrorInfo,
        ProtocolStateSystemEvent,
    )


# ==============================================================================
# Node Configuration Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNodeConfigurationData(Protocol):
    """
    Protocol for ONEX node configuration data objects.

    Defines the configuration structure for nodes in the ONEX distributed system,
    including execution parameters, resource limits, and behavioral settings.

    Key Features:
        - Execution parameters and settings
        - Resource limits and constraints
        - Behavioral configuration options
        - Node-specific configuration metadata

    Usage:
        config = await node.get_node_config()
        max_memory = config.resource_limits.get("max_memory_mb")
        timeout_seconds = config.execution_parameters.get("timeout_seconds")
    """

    @property
    def execution_parameters(self) -> dict[str, "ContextValue"]: ...
    @property
    def resource_limits(self) -> dict[str, "ContextValue"]:
        """Resource limits and constraints."""
        ...

    @property
    def behavioral_settings(self) -> dict[str, "ContextValue"]:
        """Behavioral configuration options."""
        ...

    @property
    def configuration_metadata(self) -> dict[str, "ContextValue"]:
        """Configuration-specific metadata."""
        ...


# ==============================================================================
# Node Metadata Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNodeMetadata(Protocol):
    """
    Protocol for ONEX node metadata objects.

    Defines the essential metadata structure for nodes in the ONEX
    distributed system, including identification, type classification,
    and extensible metadata storage.

    Key Features:
        - Unique node identification
        - Node type classification (COMPUTE, EFFECT, REDUCER, ORCHESTRATOR)
        - Extensible metadata dictionary with type safety
        - Runtime node introspection support

    Usage:
        metadata = node.get_metadata()
        if metadata.node_type == "COMPUTE":
            schedule_computation_task(metadata.node_id)
    """

    node_id: str
    node_type: str
    metadata: dict[str, "ContextValue"]

    async def validate_node_metadata(self) -> bool: ...

    def is_complete(self) -> bool: ...


# ==============================================================================
# Node Metadata Block Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNodeMetadataBlock(Protocol):
    """
    Protocol for node metadata block objects with full lifecycle tracking.

    Provides comprehensive metadata for ONEX nodes including identification,
    versioning, namespace organization, lifecycle state, and timestamps.
    Serves as the standard metadata structure for node discovery, registry,
    and management operations across the ONEX ecosystem.

    Attributes:
        uuid: Globally unique identifier for the node.
        name: Human-readable name of the node.
        description: Detailed description of the node's purpose and functionality.
        version: Current semantic version of the node implementation.
        metadata_version: Version of the metadata schema being used.
        namespace: Organizational namespace (e.g., "omnibase_spi.protocols").
        created_at: Timestamp when the node was first created.
        last_modified_at: Timestamp of the most recent modification.
        lifecycle: Current lifecycle state ("active", "deprecated", "retired").
        protocol_version: Version of the protocol the node implements.

    Example:
        ```python
        class ComputeNodeMetadata:
            uuid: str = "550e8400-e29b-41d4-a716-446655440000"
            name: str = "NodeDataTransformCompute"
            description: str = "Transforms raw data into structured format"
            version: ProtocolSemVer = SemVer(1, 2, 0)
            metadata_version: ProtocolSemVer = SemVer(1, 0, 0)
            namespace: str = "omnibase_infra.nodes.compute"
            created_at: ProtocolDateTime = datetime_instance
            last_modified_at: ProtocolDateTime = datetime_instance
            lifecycle: str = "active"
            protocol_version: ProtocolSemVer = SemVer(0, 3, 0)

            async def validate_metadata_block(self) -> bool:
                return bool(self.uuid and self.name and self.namespace)

            def is_complete(self) -> bool:
                return all([self.uuid, self.name, self.version, self.namespace])

        metadata = ComputeNodeMetadata()
        assert isinstance(metadata, ProtocolNodeMetadataBlock)
        assert metadata.lifecycle == "active"
        ```
    """

    uuid: str
    name: str
    description: str
    version: "ProtocolSemVer"
    metadata_version: "ProtocolSemVer"
    namespace: str
    created_at: "ProtocolDateTime"
    last_modified_at: "ProtocolDateTime"
    lifecycle: str
    protocol_version: "ProtocolSemVer"

    async def validate_metadata_block(self) -> bool: ...

    def is_complete(self) -> bool: ...


# ==============================================================================
# Node Info Marker Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNodeInfoLike(Protocol):
    """
    Protocol for objects that can provide ONEX node information.

    This marker protocol defines the minimal interface that objects
    must implement to be compatible with node metadata processing
    and discovery systems. Objects implementing this protocol can be
    safely converted to ModelNodeMetadataInfo instances.

    Key Features:
        - Marker interface for node information compatibility
        - Runtime type checking with sentinel attribute
        - Safe conversion to node metadata structures
        - Compatibility with node discovery and registry systems

    Usage:
        def process_node_info(info: "ProtocolNodeInfoLike"):
            if isinstance(info, ProtocolNodeInfoLike):
                metadata = convert_to_node_metadata(info)
                register_node(metadata)

    This is a marker interface with a sentinel attribute for runtime checks.
    """

    __omnibase_node_info_marker__: Literal[True]


# ==============================================================================
# Node Result Protocol
# ==============================================================================


@runtime_checkable
class ProtocolNodeResult(Protocol):
    """
    Protocol for comprehensive node processing results with monadic composition.

    Provides rich result information for ONEX node operations, including
    success/failure indication, error details, trust scores, provenance
    tracking, and state changes. Enables sophisticated result composition
    and error handling in distributed workflows.

    Key Features:
        - Monadic success/failure patterns
        - Trust scoring for result confidence
        - Provenance tracking for data lineage
        - Event emission for observability
        - State delta tracking for reducers

    Usage:
        result = node.process(input_data)

        # Monadic composition patterns
        if result.is_success:
            next_result = next_node.process(result.value)
        else:
            handle_error(result.error)

        # Trust evaluation
        if result.trust_score > 0.8:
            accept_result(result.value)

        # State management
        for key, value in result.state_delta.items():
            state_manager.update(key, value)
    """

    value: ContextValue | None
    is_success: bool
    is_failure: bool
    error: "ProtocolErrorInfo | None"
    trust_score: float
    provenance: list[str]
    metadata: dict[str, "ContextValue"]
    events: list["ProtocolStateSystemEvent"]
    state_delta: dict[str, "ContextValue"]

    async def validate_result(self) -> bool: ...

    def is_successful(self) -> bool: ...

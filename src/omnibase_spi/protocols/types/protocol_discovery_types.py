"""
Discovery protocol types for ONEX SPI interfaces.

Domain: Service and node discovery protocols
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolSemVer,
    )

LiteralDiscoveryStatus = Literal["found", "not_found", "error", "timeout"]
LiteralHandlerStatus = Literal["available", "busy", "offline", "error"]


@runtime_checkable
class ProtocolCapabilityValue(Protocol):
    """
    Base protocol for capability data values in node discovery systems.

    Provides the foundation for typed capability values that can be validated
    and serialized for use in node registration and discovery. All specific
    capability value types inherit from this protocol.

    Example:
        ```python
        class CustomCapabilityValue:
            async def validate_for_capability(self) -> bool:
                return True  # Validate the capability value

            def serialize_for_capability(self) -> dict[str, object]:
                return {"type": "custom", "valid": True}

        value = CustomCapabilityValue()
        assert isinstance(value, ProtocolCapabilityValue)
        is_valid = await value.validate_for_capability()
        serialized = value.serialize_for_capability()
        ```
    """

    async def validate_for_capability(self) -> bool: ...

    def serialize_for_capability(self) -> dict[str, object]: ...


@runtime_checkable
class ProtocolCapabilityStringValue(ProtocolCapabilityValue, Protocol):
    """
    Protocol for string-based capability values in node discovery.

    Extends ProtocolCapabilityValue for string data such as capability names,
    descriptions, identifiers, and textual metadata used in service registration.

    Attributes:
        value: The string capability value.

    Example:
        ```python
        class CapabilityName:
            def __init__(self, name: str):
                self.value = name

            async def validate_for_capability(self) -> bool:
                return len(self.value) > 0 and len(self.value) <= 256

            def serialize_for_capability(self) -> dict[str, object]:
                return {"type": "string", "value": self.value}

        cap_name = CapabilityName("compute-heavy-tasks")
        assert isinstance(cap_name, ProtocolCapabilityStringValue)
        assert cap_name.value == "compute-heavy-tasks"
        ```
    """

    value: str


@runtime_checkable
class ProtocolCapabilityNumericValue(ProtocolCapabilityValue, Protocol):
    """
    Protocol for numeric capability values in node discovery.

    Extends ProtocolCapabilityValue for numeric data such as resource counts,
    performance measurements, capacity limits, and scoring metrics used in
    capability-based service selection and load balancing.

    Attributes:
        value: The numeric capability value (int or float).

    Example:
        ```python
        class CapabilityScore:
            def __init__(self, score: float):
                self.value = score

            async def validate_for_capability(self) -> bool:
                return 0.0 <= self.value <= 100.0

            def serialize_for_capability(self) -> dict[str, object]:
                return {"type": "numeric", "value": self.value}

        cap_score = CapabilityScore(95.5)
        assert isinstance(cap_score, ProtocolCapabilityNumericValue)
        assert cap_score.value == 95.5
        ```
    """

    value: int | float


@runtime_checkable
class ProtocolCapabilityBooleanValue(ProtocolCapabilityValue, Protocol):
    """
    Protocol for boolean capability values in node discovery.

    Extends ProtocolCapabilityValue for boolean flags such as feature toggles,
    availability indicators, and enabled/disabled states used in capability
    matching and service filtering.

    Attributes:
        value: The boolean capability value.

    Example:
        ```python
        class CapabilityFlag:
            def __init__(self, enabled: bool):
                self.value = enabled

            async def validate_for_capability(self) -> bool:
                return isinstance(self.value, bool)

            def serialize_for_capability(self) -> dict[str, object]:
                return {"type": "boolean", "value": self.value}

        gpu_capable = CapabilityFlag(True)
        assert isinstance(gpu_capable, ProtocolCapabilityBooleanValue)
        assert gpu_capable.value is True
        ```
    """

    value: bool


@runtime_checkable
class ProtocolCapabilityStringListValue(ProtocolCapabilityValue, Protocol):
    """
    Protocol for string list capability values in node discovery.

    Extends ProtocolCapabilityValue for lists of strings such as tags,
    categories, supported protocols, and multi-value identifiers used in
    capability matching and service categorization.

    Attributes:
        value: List of string capability values.

    Example:
        ```python
        class CapabilityTags:
            def __init__(self, tags: list[str]):
                self.value = tags

            async def validate_for_capability(self) -> bool:
                return all(isinstance(t, str) and len(t) > 0 for t in self.value)

            def serialize_for_capability(self) -> dict[str, object]:
                return {"type": "string_list", "values": self.value}

        protocols = CapabilityTags(["http", "grpc", "websocket"])
        assert isinstance(protocols, ProtocolCapabilityStringListValue)
        assert "grpc" in protocols.value
        ```
    """

    value: list[str]


CapabilityValue = ProtocolCapabilityValue


@runtime_checkable
class ProtocolHandlerCapability(Protocol):
    """
    Protocol for handler capability definition with versioning support.

    Defines a single capability that a handler provides or requires, including
    the capability name, value, requirement flag, and version compatibility
    information for capability-based routing and discovery.

    Attributes:
        capability_name: Unique name identifying the capability.
        capability_value: The typed value of the capability.
        is_required: Whether this capability is mandatory for operation.
        version: Semantic version of the capability for compatibility checks.

    Example:
        ```python
        class HandlerCapability:
            capability_name: str = "gpu-compute"
            capability_value: CapabilityValue
            is_required: bool = True
            version: ProtocolSemVer

            def __init__(self, value: CapabilityValue, ver: ProtocolSemVer):
                self.capability_value = value
                self.version = ver

        cap = HandlerCapability(CapabilityBooleanValue(True), SemVer(1, 0, 0))
        assert isinstance(cap, ProtocolHandlerCapability)
        assert cap.capability_name == "gpu-compute"
        assert cap.is_required
        ```
    """

    capability_name: str
    capability_value: CapabilityValue
    is_required: bool
    version: "ProtocolSemVer"


@runtime_checkable
class ProtocolDiscoveryNodeInfo(Protocol):
    """
    Protocol for node information returned by discovery operations.

    Contains comprehensive information about a discovered node including its
    identity, type classification, current availability status, supported
    capabilities, and extensible metadata for service selection decisions.

    Attributes:
        node_id: Unique identifier of the discovered node.
        node_name: Human-readable name of the node.
        node_type: Type classification (COMPUTE, EFFECT, REDUCER, ORCHESTRATOR).
        status: Current handler availability status.
        capabilities: List of capability names supported by the node.
        metadata: Additional node metadata as capability values.

    Example:
        ```python
        from uuid import uuid4

        class DiscoveredNode:
            node_id: UUID = uuid4()
            node_name: str = "compute-node-1"
            node_type: str = "COMPUTE"
            status: LiteralHandlerStatus = "available"
            capabilities: list[str] = ["gpu-compute", "batch-processing"]
            metadata: dict[str, CapabilityValue] = {}

        node = DiscoveredNode()
        assert isinstance(node, ProtocolDiscoveryNodeInfo)
        assert node.status == "available"
        assert "gpu-compute" in node.capabilities
        ```
    """

    node_id: UUID
    node_name: str
    node_type: str
    status: LiteralHandlerStatus
    capabilities: list[str]
    metadata: dict[str, CapabilityValue]


@runtime_checkable
class ProtocolDiscoveryQuery(Protocol):
    """
    Protocol for node discovery query specification.

    Defines the parameters for querying the service registry to discover
    nodes matching specific criteria including type, capabilities, and
    custom filters with configurable timeout behavior.

    Attributes:
        query_id: Unique identifier for tracking this discovery query.
        target_type: Node type to search for (COMPUTE, EFFECT, etc.).
        required_capabilities: List of required capability names.
        filters: Additional filter criteria as context values.
        timeout_seconds: Maximum time to wait for discovery results.

    Example:
        ```python
        from uuid import uuid4

        class NodeDiscoveryQuery:
            query_id: UUID = uuid4()
            target_type: str = "COMPUTE"
            required_capabilities: list[str] = ["gpu-compute"]
            filters: dict[str, ContextValue] = {"region": "us-west"}
            timeout_seconds: float = 30.0

        query = NodeDiscoveryQuery()
        assert isinstance(query, ProtocolDiscoveryQuery)
        assert query.target_type == "COMPUTE"
        assert "gpu-compute" in query.required_capabilities
        ```
    """

    query_id: UUID
    target_type: str
    required_capabilities: list[str]
    filters: dict[str, "ContextValue"]
    timeout_seconds: float


@runtime_checkable
class ProtocolDiscoveryResult(Protocol):
    """
    Protocol for discovery operation results with status and metrics.

    Contains the outcome of a discovery query including status, match count,
    timing information, and error details. Used to track discovery performance
    and handle discovery failures gracefully.

    Attributes:
        query_id: Identifier matching the original discovery query.
        status: Result status (found, not_found, error, timeout).
        nodes_found: Number of nodes matching the query criteria.
        discovery_time: Time taken to complete discovery in seconds.
        error_message: Error description if status is error or timeout.

    Example:
        ```python
        from uuid import uuid4

        class DiscoveryResult:
            query_id: UUID = uuid4()
            status: LiteralDiscoveryStatus = "found"
            nodes_found: int = 3
            discovery_time: float = 0.125
            error_message: str | None = None

        result = DiscoveryResult()
        assert isinstance(result, ProtocolDiscoveryResult)
        assert result.status == "found"
        assert result.nodes_found == 3
        assert result.error_message is None
        ```
    """

    query_id: UUID
    status: LiteralDiscoveryStatus
    nodes_found: int
    discovery_time: float
    error_message: str | None


@runtime_checkable
class ProtocolHandlerRegistration(Protocol):
    """
    Protocol for handler registration in the service registry.

    Contains registration information for a handler including its identity,
    registration data, timing information, and activation status. Supports
    optional TTL-based expiration for automatic deregistration.

    Attributes:
        node_id: Unique identifier of the registered node.
        registration_data: Capability and metadata values for the registration.
        registration_time: Unix timestamp when registration occurred.
        expires_at: Optional expiration timestamp for TTL-based cleanup.
        is_active: Whether the registration is currently active.

    Example:
        ```python
        from uuid import uuid4
        import time

        class HandlerRegistration:
            node_id: UUID = uuid4()
            registration_data: dict[str, CapabilityValue] = {"region": "us-west"}
            registration_time: float = time.time()
            expires_at: float | None = time.time() + 3600  # 1 hour TTL
            is_active: bool = True

        reg = HandlerRegistration()
        assert isinstance(reg, ProtocolHandlerRegistration)
        assert reg.is_active
        assert reg.expires_at is not None
        ```
    """

    node_id: UUID
    registration_data: dict[str, CapabilityValue]
    registration_time: float
    expires_at: float | None
    is_active: bool

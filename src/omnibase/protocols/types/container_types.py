"""
Container protocol types for ONEX SPI interfaces.

Domain: Dependency injection and service registry protocols
"""

from typing import Dict, Literal, Protocol, TypeVar, Union
from uuid import UUID

# Generic type for services
T = TypeVar("T")

# Legacy status types (deprecated - use comprehensive protocols instead)
RegistrationStatus = Literal["registered", "unregistered", "failed", "pending"]
ServiceStatus = Literal["active", "inactive", "error", "starting", "stopping"]

# Configuration value types - more specific than Any
ConfigValue = Union[str, int, float, bool, list[str], Dict[str, Union[str, int, bool]]]


# Legacy service registry protocols (deprecated - use comprehensive protocols instead)
class ProtocolServiceInfo(Protocol):
    """Protocol for service information objects."""

    service_id: UUID
    service_name: str
    service_type: str
    status: ServiceStatus
    registration_time: float
    metadata: Dict[str, ConfigValue]


class ProtocolServiceRegistryBasic(Protocol):
    """Basic protocol for service registry objects (deprecated)."""

    registry_id: str
    total_services: int
    active_services: int
    last_updated: float


# Container configuration protocols
class ProtocolContainerConfig(Protocol):
    """Protocol for container configuration objects."""

    container_name: str
    auto_wire: bool
    singleton_scope: bool
    configuration: Dict[str, ConfigValue]


# Legacy dependency protocols (deprecated - use comprehensive protocols instead)
class ProtocolDependencyInfo(Protocol):
    """Protocol for dependency information."""

    dependency_name: str
    dependency_type: str
    is_required: bool
    default_value: ConfigValue | None


class ProtocolInjectionContextBasic(Protocol):
    """Basic protocol for dependency injection context (deprecated)."""

    target_service: str
    dependencies: list[str]
    injection_time: float
    success: bool

"""
Protocol for Container Service.

Defines the interface for dependency injection container management,
service registration, and registry lifecycle operations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_container_types import (
        ProtocolContainerResult,
        ProtocolContainerServiceInstance,
        ProtocolDependencySpec,
        ProtocolDIContainer,
        ProtocolRegistryWrapper,
    )
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolMetadata


@runtime_checkable
class ProtocolContainerService(Protocol):
    """
    Protocol interface for container service operations.

    Provides dependency injection container management, service registration,
    and registry lifecycle operations for ONEX-compliant systems.

    Key Features:
        - Container creation from contract specifications
        - Service instantiation from dependency specifications
        - Container dependency validation
        - Registry wrapper management
        - Container lifecycle management
        - Node reference integration

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "ContainerService" = get_container_service()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        container_service: "ProtocolContainerService" = ContainerServiceImpl()

        result = container_service.create_container_from_contract(
            metadata=contract_metadata,
            node_id="my_node",
            node_ref=node_instance
        )
        ```
    """

    async def create_container_from_contract(
        self,
        contract_metadata: "ProtocolMetadata",
        node_id: str,
        node_ref: object | None = None,
    ) -> "ProtocolContainerResult": ...

    async def create_service_from_dependency(
        self, dependency_spec: "ProtocolDependencySpec"
    ) -> "ProtocolContainerServiceInstance | None": ...

    async def validate_container_dependencies(
        self, container: "ProtocolDIContainer"
    ) -> bool: ...

    async def get_registry_wrapper(
        self, container: "ProtocolDIContainer", node_ref: object | None = None
    ) -> "ProtocolRegistryWrapper": ...

    async def update_container_lifecycle(
        self, registry: "ProtocolRegistryWrapper", node_ref: object
    ) -> None: ...

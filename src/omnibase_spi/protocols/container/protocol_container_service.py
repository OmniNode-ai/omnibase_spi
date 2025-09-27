"""
Protocol for Container Service.

Defines the interface for dependency injection container management,
service registration, and registry lifecycle operations.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_container_types import (
    ProtocolContainer,
    ProtocolContainerResult,
    ProtocolContainerServiceInstance,
    ProtocolDependencySpec,
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
        # Implementation example (not part of SPI)
        class ContainerServiceImpl:
            async def create_container_from_contract(self, metadata, node_id, node_ref=None):
                container = self._create_empty_container()

                # Register dependencies from contract
                for dep_spec in metadata.dependencies:
                    service = self.create_service_from_dependency(dep_spec)
                    if service:
                        container.register(dep_spec.service_key, service)

                return ContainerResult(container, registry_wrapper)

        # Usage in application code
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
        contract_metadata: ProtocolMetadata,
        node_id: str,
        node_ref: object | None = None,
    ) -> ProtocolContainerResult:
        """
        Create and configure container from contract dependencies.

        Args:
            contract_metadata: Contract metadata with dependencies specification
            node_id: Node identifier for logging and metadata
            node_ref: Reference to node instance for version access

        Returns:
            Container result with registry-wrapped container and all dependencies

        Raises:
            ValueError: If contract metadata is invalid
            ImportError: If dependency modules cannot be imported
            RuntimeError: If container creation or dependency registration fails
        """
        ...

    async def create_service_from_dependency(
        self, dependency_spec: ProtocolDependencySpec
    ) -> ProtocolContainerServiceInstance | None:
        """
        Create service instance from contract dependency specification.

        Args:
            dependency_spec: Dependency specification with module/class information

        Returns:
            Service instance or None if creation fails

        Note:
            Returns None for optional dependencies that fail to create
            rather than raising exceptions to support graceful degradation.

        Raises:
            ValueError: If dependency specification is invalid
            ImportError: If required dependency module cannot be imported
            RuntimeError: If service creation fails for required dependencies
        """
        ...

    async def validate_container_dependencies(
        self, container: ProtocolContainer
    ) -> bool:
        """
        Validate container has all required dependencies registered.

        Args:
            container: Container instance to validate

        Returns:
            True if all dependencies are available and valid

        Note:
            Performs comprehensive validation including dependency resolution,
            circular dependency detection, and service availability checks.
        """
        ...

    async def get_registry_wrapper(
        self, container: ProtocolContainer, node_ref: object | None = None
    ) -> ProtocolRegistryWrapper:
        """
        Create registry wrapper around container for standardized access.

        Args:
            container: Container instance to wrap
            node_ref: Reference to node for version and metadata access

        Returns:
            Registry wrapper with standardized service access methods

        Note:
            Provides unified interface for service lookup regardless
            of underlying container implementation.
        """
        ...

    async def update_container_lifecycle(
        self, registry: ProtocolRegistryWrapper, node_ref: object
    ) -> None:
        """
        Update container lifecycle with node reference and version information.

        Args:
            registry: Registry wrapper instance to update
            node_ref: Node instance for version and metadata access

        Note:
            Updates container with node lifecycle information,
            version metadata, and runtime configuration.
        """
        ...

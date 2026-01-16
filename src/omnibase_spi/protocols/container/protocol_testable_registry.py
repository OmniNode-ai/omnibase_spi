"""
Protocol for testable ONEX registry interfaces.

Provides a clean interface for testable registry operations without exposing
implementation-specific details. This protocol enables testing and cross-component
registry testing while maintaining proper architectural boundaries.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolTestableRegistry(Protocol):
    """
    Protocol for testable ONEX registry interfaces supporting mock and real implementations.

    Provides a clean interface for registry testing and swappable registry fixtures,
    enabling comprehensive testing of registry-dependent components with both real
    configuration and mock data. This protocol supports test-driven development by
    allowing seamless swapping between production and test registry implementations.

    The testable registry pattern enables isolation testing of components that depend
    on registry data while maintaining proper protocol compliance and type safety.

    Example:
        ```python
        # Production usage - load from disk
        registry: "ProtocolTestableRegistry" = await MyRegistry.load_from_disk()
        node_data = await registry.get_node("workflow_processor")

        # Test usage - load mock registry
        mock_registry: "ProtocolTestableRegistry" = await MyRegistry.load_mock()
        test_node = await mock_registry.get_node("test_node")

        # Swappable fixture pattern
        async def setup_test_registry(use_mock: bool = True) -> "ProtocolTestableRegistry":
            if use_mock:
                return await TestRegistry.load_mock()
            else:
                return await TestRegistry.load_from_disk()

        # Usage in tests
        registry = await setup_test_registry(use_mock=True)
        node = await registry.get_node("processor_node")
        assert node["type"] == "processor"
        ```

    Key Features:
        - Dual loading modes: production (disk) and testing (mock)
        - Protocol compliance for type safety across implementations
        - Swappable fixture support for flexible testing
        - Isolated component testing without external dependencies
        - Consistent interface for mock and real registries
        - Support for test-driven development workflows
        - Easy integration with pytest fixtures

    Testing Patterns:
        - Unit tests: Use mock registries for fast, isolated tests
        - Integration tests: Use disk-loaded registries for realistic scenarios
        - Fixture factories: Create custom test registries with specific data
        - Dependency injection: Inject appropriate registry based on environment

    Mock Registry Behavior:
        Mock registries typically provide:
        - Predefined test data for common scenarios
        - Controlled failure modes for error testing
        - Simplified configuration without external dependencies
        - Fast initialization for rapid test execution

    See Also:
        - ProtocolRegistry: Base registry operations protocol
        - ProtocolRegistryResolver: Dynamic registry resolution
        - ProtocolArtifactContainer: Artifact storage and retrieval
    """

    @classmethod
    async def load_from_disk(cls) -> "ProtocolTestableRegistry":
        """
        Load a testable registry from disk configuration.

        Returns:
            A testable registry instance loaded from disk
        """
        ...

    @classmethod
    async def load_mock(cls) -> "ProtocolTestableRegistry":
        """
        Load a mock testable registry for testing purposes.

        Returns:
            A mock testable registry instance
        """
        ...

    async def get_node(self, node_id: str) -> "JsonType":
        """
        Get a node from the testable registry.

        Args:
            node_id: The identifier of the node to retrieve

        Returns:
            A dictionary containing the node information
        """
        ...

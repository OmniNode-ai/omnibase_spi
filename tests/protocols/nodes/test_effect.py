"""
Tests for ProtocolEffectNode protocol.

Validates that ProtocolEffectNode:
- Is properly runtime checkable
- Defines required methods (initialize, shutdown, execute)
- Inherits from ProtocolNode
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest

from omnibase_spi.protocols.nodes.effect import ProtocolEffectNode


class CompliantEffectNode:
    """A class that fully implements the ProtocolEffectNode protocol."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "test-effect-node-v1"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "effect"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def initialize(self) -> None:
        """Initialize node-specific resources."""
        pass

    async def shutdown(self) -> None:
        """Release node-specific resources."""
        pass

    async def execute(self, input_data: object) -> object:  # type: ignore[override]
        """Execute effect operation."""
        # Mock implementation for testing
        class MockEffectOutput:
            """Mock effect output for testing."""
            node_id: str = "test-effect-node-v1"
            status: str = "success"
            result: dict = {"processed": True}

        return MockEffectOutput()


class PartialEffectNode:
    """A class that only implements some ProtocolEffectNode methods."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "partial-effect-node"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "effect"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def initialize(self) -> None:
        """Initialize node-specific resources."""
        pass

    # Missing shutdown() and execute()


class NonCompliantEffectNode:
    """A class that implements none of the ProtocolEffectNode methods."""

    pass


class WrongSignatureEffectNode:
    """A class that implements methods with wrong signatures."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "wrong-sig-node"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "effect"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def initialize(self) -> None:
        """Initialize node-specific resources."""
        pass

    async def shutdown(self) -> None:
        """Release node-specific resources."""
        pass

    async def execute(self, wrong_param: str) -> str:  # type: ignore[misc]
        """Execute with wrong signature."""
        return "wrong"


class TestProtocolEffectNodeProtocol:
    """Test suite for ProtocolEffectNode protocol compliance."""

    def test_effect_node_is_runtime_checkable(self) -> None:
        """ProtocolEffectNode should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolEffectNode, "_is_runtime_protocol") or hasattr(
            ProtocolEffectNode, "__runtime_protocol__"
        )

    def test_effect_node_is_protocol(self) -> None:
        """ProtocolEffectNode should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolEffectNode has Protocol in its bases
        assert any(
            base is Protocol or getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolEffectNode.__mro__
        )

    def test_effect_node_has_initialize_method(self) -> None:
        """ProtocolEffectNode should define initialize method."""
        assert "initialize" in dir(ProtocolEffectNode)

    def test_effect_node_has_shutdown_method(self) -> None:
        """ProtocolEffectNode should define shutdown method."""
        assert "shutdown" in dir(ProtocolEffectNode)

    def test_effect_node_has_execute_method(self) -> None:
        """ProtocolEffectNode should define execute method."""
        assert "execute" in dir(ProtocolEffectNode)

    def test_effect_node_inherits_from_protocol_node(self) -> None:
        """ProtocolEffectNode should inherit from ProtocolNode."""
        from omnibase_spi.protocols.nodes.base import ProtocolNode

        # Check that ProtocolNode is in ProtocolEffectNode's MRO
        assert ProtocolNode in ProtocolEffectNode.__mro__

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEffectNode protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEffectNode()  # type: ignore[call-arg]


class TestProtocolEffectNodeCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolEffectNode methods should pass isinstance check."""
        node = CompliantEffectNode()
        assert isinstance(node, ProtocolEffectNode)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolEffectNode methods should fail isinstance check."""
        node = PartialEffectNode()
        assert not isinstance(node, ProtocolEffectNode)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolEffectNode methods should fail isinstance check."""
        node = NonCompliantEffectNode()
        assert not isinstance(node, ProtocolEffectNode)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with methods of wrong signatures still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Type checking is enforced by static analysis tools.
        """
        node = WrongSignatureEffectNode()
        # Runtime check passes because methods exist
        assert isinstance(node, ProtocolEffectNode)


class TestProtocolEffectNodeMethodSignatures:
    """Test method signatures and behavior from compliant implementations."""

    @pytest.mark.asyncio
    async def test_initialize_is_async(self) -> None:
        """initialize method should be async and return None."""
        node = CompliantEffectNode()
        result = await node.initialize()
        assert result is None

    @pytest.mark.asyncio
    async def test_shutdown_is_async(self) -> None:
        """shutdown method should be async and return None."""
        node = CompliantEffectNode()
        result = await node.shutdown()
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_is_async(self) -> None:
        """execute method should be async."""
        node = CompliantEffectNode()
        # Use mock input data instead of omnibase_core model
        class MockEffectInput:
            """Mock effect input for testing."""
            node_id: str = "test-effect-node-v1"
            operation: str = "test_operation"
            parameters: dict = {"key": "value"}

        input_data = MockEffectInput()
        result = await node.execute(input_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_accepts_effect_input(self) -> None:
        """execute method should accept effect input."""
        node = CompliantEffectNode()
        # Use mock input data instead of omnibase_core model
        class MockEffectInput:
            """Mock effect input for testing."""
            node_id: str = "test-effect-node-v1"
            operation: str = "test_operation"
            parameters: dict = {"key": "value"}

        input_data = MockEffectInput()
        # Should not raise
        await node.execute(input_data)

    @pytest.mark.asyncio
    async def test_execute_returns_effect_output(self) -> None:
        """execute method should return effect output."""
        node = CompliantEffectNode()
        # Use mock input data instead of omnibase_core model
        class MockEffectInput:
            """Mock effect input for testing."""
            node_id: str = "test-effect-node-v1"
            operation: str = "test_operation"
            parameters: dict = {"key": "value"}

        input_data = MockEffectInput()
        result = await node.execute(input_data)
        # Verify we get an object back (mock output)
        assert result is not None
        assert hasattr(result, 'node_id')
        assert hasattr(result, 'status')
        assert hasattr(result, 'result')


class TestProtocolEffectNodeInheritance:
    """Test inheritance from ProtocolNode."""

    def test_effect_node_has_node_id_property(self) -> None:
        """ProtocolEffectNode should inherit node_id from ProtocolNode."""
        node = CompliantEffectNode()
        assert hasattr(node, "node_id")
        assert isinstance(node.node_id, str)
        assert node.node_id == "test-effect-node-v1"

    def test_effect_node_has_node_type_property(self) -> None:
        """ProtocolEffectNode should inherit node_type from ProtocolNode."""
        node = CompliantEffectNode()
        assert hasattr(node, "node_type")
        assert isinstance(node.node_type, str)
        assert node.node_type == "effect"

    def test_effect_node_has_version_property(self) -> None:
        """ProtocolEffectNode should inherit version from ProtocolNode."""
        node = CompliantEffectNode()
        assert hasattr(node, "version")
        assert isinstance(node.version, str)
        assert node.version == "1.0.0"


class TestProtocolEffectNodeImports:
    """Test protocol imports from different locations."""

    def test_import_from_effect_module(self) -> None:
        """Test direct import from effect module."""
        from omnibase_spi.protocols.nodes.effect import (
            ProtocolEffectNode as EffectProtocolEffectNode,
        )

        node = CompliantEffectNode()
        assert isinstance(node, EffectProtocolEffectNode)

    def test_import_from_nodes_package(self) -> None:
        """Test import from nodes package."""
        from omnibase_spi.protocols.nodes import (
            ProtocolEffectNode as NodesProtocolEffectNode,
        )

        node = CompliantEffectNode()
        assert isinstance(node, NodesProtocolEffectNode)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.nodes import (
            ProtocolEffectNode as NodesProtocolEffectNode,
        )
        from omnibase_spi.protocols.nodes.effect import (
            ProtocolEffectNode as EffectProtocolEffectNode,
        )

        assert NodesProtocolEffectNode is EffectProtocolEffectNode

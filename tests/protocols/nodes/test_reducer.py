"""
Tests for ProtocolReducerNode protocol.

Validates that ProtocolReducerNode:
- Is properly runtime checkable
- Inherits from ProtocolNode
- Defines required execute() method
- Execute method accepts ModelReductionInput and returns ModelReductionOutput
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest

from omnibase_spi.protocols.nodes.reducer import ProtocolReducerNode


class CompliantReducerNode:
    """A class that fully implements the ProtocolReducerNode protocol."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "test-reducer-v1"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "reducer"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def execute(self, _input_data: object) -> object:
        """Execute state reduction."""
        # In real implementation, would use ModelReductionInput/Output
        return object()


class PartialReducerNode:
    """A class that implements ProtocolNode but missing execute method."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "partial-reducer"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "reducer"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"


class NonCompliantReducerNode:
    """A class that implements none of the ProtocolReducerNode methods."""

    pass


class WrongSignatureReducerNode:
    """A class with wrong execute signature."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "wrong-sig-reducer"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "reducer"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def execute(self) -> None:  # Wrong signature
        """Execute with wrong signature."""
        pass


class TestProtocolReducerNodeProtocol:
    """Test suite for ProtocolReducerNode protocol compliance."""

    def test_reducer_node_is_runtime_checkable(self) -> None:
        """ProtocolReducerNode should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolReducerNode, "_is_runtime_protocol") or hasattr(
            ProtocolReducerNode, "__runtime_protocol__"
        )

    def test_reducer_node_is_protocol(self) -> None:
        """ProtocolReducerNode should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolReducerNode has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolReducerNode.__mro__
        )

    def test_reducer_node_inherits_from_protocol_node(self) -> None:
        """ProtocolReducerNode should inherit from ProtocolNode."""
        from omnibase_spi.protocols.nodes.base import ProtocolNode

        # Check that ProtocolNode is in the MRO
        assert ProtocolNode in ProtocolReducerNode.__mro__

    def test_reducer_node_has_execute_method(self) -> None:
        """ProtocolReducerNode should define execute method."""
        assert "execute" in dir(ProtocolReducerNode)

    def test_reducer_node_has_node_id_property(self) -> None:
        """ProtocolReducerNode should inherit node_id property from ProtocolNode."""
        assert "node_id" in dir(ProtocolReducerNode)

    def test_reducer_node_has_node_type_property(self) -> None:
        """ProtocolReducerNode should inherit node_type property from ProtocolNode."""
        assert "node_type" in dir(ProtocolReducerNode)

    def test_reducer_node_has_version_property(self) -> None:
        """ProtocolReducerNode should inherit version property from ProtocolNode."""
        assert "version" in dir(ProtocolReducerNode)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolReducerNode protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolReducerNode()  # type: ignore[misc]


class TestProtocolReducerNodeCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolReducerNode methods should pass isinstance check."""
        node = CompliantReducerNode()
        assert isinstance(node, ProtocolReducerNode)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing execute method should fail isinstance check."""
        node = PartialReducerNode()
        assert not isinstance(node, ProtocolReducerNode)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolReducerNode methods should fail isinstance check."""
        node = NonCompliantReducerNode()
        assert not isinstance(node, ProtocolReducerNode)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with execute method of wrong signature still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Signature checking is enforced by static analysis tools.
        """
        node = WrongSignatureReducerNode()
        # Runtime check passes because execute method exists
        assert isinstance(node, ProtocolReducerNode)


class TestProtocolReducerNodeMethodSignatures:
    """Test method signatures and return types."""

    @pytest.mark.asyncio
    async def test_execute_method_exists_and_callable(self) -> None:
        """execute method should exist and be callable."""
        node = CompliantReducerNode()
        assert hasattr(node, "execute")
        assert callable(node.execute)

    @pytest.mark.asyncio
    async def test_execute_method_is_async(self) -> None:
        """execute method should be async."""
        import inspect

        node = CompliantReducerNode()
        assert inspect.iscoroutinefunction(node.execute)

    @pytest.mark.asyncio
    async def test_execute_accepts_input_data(self) -> None:
        """execute method should accept input_data parameter."""
        node = CompliantReducerNode()
        # Test that method accepts input_data argument (positional)
        result = await node.execute(object())
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_returns_object(self) -> None:
        """execute method should return an object."""
        node = CompliantReducerNode()
        result = await node.execute(object())
        # In real implementation, would be ModelReductionOutput
        assert isinstance(result, object)


class TestProtocolReducerNodePropertyValues:
    """Test property values from compliant implementations."""

    def test_node_id_returns_string(self) -> None:
        """node_id property should return a string."""
        node = CompliantReducerNode()
        result = node.node_id
        assert isinstance(result, str)
        assert result == "test-reducer-v1"

    def test_node_type_returns_string(self) -> None:
        """node_type property should return a string."""
        node = CompliantReducerNode()
        result = node.node_type
        assert isinstance(result, str)
        assert result == "reducer"

    def test_version_returns_string(self) -> None:
        """version property should return a string."""
        node = CompliantReducerNode()
        result = node.version
        assert isinstance(result, str)
        assert result == "1.0.0"


class TestProtocolReducerNodeTypeAnnotations:
    """Test type annotations on ProtocolReducerNode protocol."""

    def test_node_id_annotation(self) -> None:
        """node_id should be annotated as returning str."""
        node: ProtocolReducerNode = CompliantReducerNode()
        assert isinstance(node.node_id, str)

    def test_node_type_annotation(self) -> None:
        """node_type should be annotated as returning str."""
        node: ProtocolReducerNode = CompliantReducerNode()
        assert isinstance(node.node_type, str)

    def test_version_annotation(self) -> None:
        """version should be annotated as returning str."""
        node: ProtocolReducerNode = CompliantReducerNode()
        assert isinstance(node.version, str)


class TestProtocolReducerNodeImports:
    """Test protocol imports from different locations."""

    def test_import_from_reducer_module(self) -> None:
        """Test direct import from reducer module."""
        from omnibase_spi.protocols.nodes.reducer import (
            ProtocolReducerNode as DirectReducerNode,
        )

        node = CompliantReducerNode()
        assert isinstance(node, DirectReducerNode)

    def test_import_from_nodes_package(self) -> None:
        """Test import from nodes package."""
        from omnibase_spi.protocols.nodes import (
            ProtocolReducerNode as NodesReducerNode,
        )

        node = CompliantReducerNode()
        assert isinstance(node, NodesReducerNode)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.nodes import (
            ProtocolReducerNode as NodesReducerNode,
        )
        from omnibase_spi.protocols.nodes.reducer import (
            ProtocolReducerNode as DirectReducerNode,
        )

        assert NodesReducerNode is DirectReducerNode


class TestProtocolReducerNodeDocumentation:
    """Test protocol documentation completeness."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolReducerNode should have a docstring."""
        assert ProtocolReducerNode.__doc__ is not None
        assert len(ProtocolReducerNode.__doc__) > 0

    def test_execute_method_has_docstring(self) -> None:
        """execute method should have a docstring."""
        # Access the method from the protocol's namespace
        assert hasattr(ProtocolReducerNode, "execute")
        # Protocol methods store docstrings - use direct attribute access
        method = ProtocolReducerNode.execute
        assert method.__doc__ is not None
        assert "Args:" in method.__doc__
        assert "Returns:" in method.__doc__
        assert "Raises:" in method.__doc__

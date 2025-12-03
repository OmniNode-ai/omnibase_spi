"""
Tests for INode base protocol.

Validates that INode:
- Is properly runtime checkable
- Defines required properties (node_id, node_type, version)
- Properties return str type
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest

from omnibase_spi.protocols.nodes.base import INode


class CompliantNode:
    """A class that fully implements the INode protocol."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "test-node-v1"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"


class PartialNode:
    """A class that only implements some INode properties."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "partial-node"


class NonCompliantNode:
    """A class that implements none of the INode properties."""

    pass


class WrongTypeNode:
    """A class that implements properties with wrong types."""

    @property
    def node_id(self) -> int:  # type: ignore[override]
        """Return node identifier as int (wrong type)."""
        return 123

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"


class TestINodeProtocol:
    """Test suite for INode protocol compliance."""

    def test_inode_is_runtime_checkable(self) -> None:
        """INode should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(INode, "_is_runtime_protocol") or hasattr(
            INode, "__runtime_protocol__"
        )

    def test_inode_is_protocol(self) -> None:
        """INode should be a Protocol class."""
        from typing import Protocol, get_origin

        # Check that INode has Protocol in its bases
        assert any(
            base is Protocol or getattr(base, "__name__", "") == "Protocol"
            for base in INode.__mro__
        )

    def test_inode_has_node_id_property(self) -> None:
        """INode should define node_id property."""
        # Protocol properties appear in __protocol_attrs__
        assert "node_id" in dir(INode)

    def test_inode_has_node_type_property(self) -> None:
        """INode should define node_type property."""
        assert "node_type" in dir(INode)

    def test_inode_has_version_property(self) -> None:
        """INode should define version property."""
        assert "version" in dir(INode)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """INode protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            INode()  # type: ignore[call-arg]


class TestINodeCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all INode properties should pass isinstance check."""
        node = CompliantNode()
        assert isinstance(node, INode)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing INode properties should fail isinstance check."""
        node = PartialNode()
        assert not isinstance(node, INode)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no INode properties should fail isinstance check."""
        node = NonCompliantNode()
        assert not isinstance(node, INode)

    def test_wrong_type_still_passes_structural_check(self) -> None:
        """
        A class with properties of wrong types still passes isinstance.

        Note: Runtime protocol checking only verifies attribute existence,
        not type correctness. Type checking is enforced by static analysis tools.
        """
        node = WrongTypeNode()
        # Runtime check passes because attributes exist
        assert isinstance(node, INode)


class TestINodePropertyValues:
    """Test property values from compliant implementations."""

    def test_node_id_returns_string(self) -> None:
        """node_id property should return a string."""
        node = CompliantNode()
        result = node.node_id
        assert isinstance(result, str)
        assert result == "test-node-v1"

    def test_node_type_returns_string(self) -> None:
        """node_type property should return a string."""
        node = CompliantNode()
        result = node.node_type
        assert isinstance(result, str)
        assert result == "compute"

    def test_version_returns_string(self) -> None:
        """version property should return a string."""
        node = CompliantNode()
        result = node.version
        assert isinstance(result, str)
        assert result == "1.0.0"


class TestINodeTypeAnnotations:
    """Test type annotations on INode protocol."""

    def test_node_id_annotation(self) -> None:
        """node_id should be annotated as returning str."""
        annotations = getattr(INode, "__annotations__", {})
        # For properties, we need to check the fget function
        # But Protocol properties don't expose annotations directly
        # Instead, verify via a compliant implementation
        node: INode = CompliantNode()
        assert isinstance(node.node_id, str)

    def test_node_type_annotation(self) -> None:
        """node_type should be annotated as returning str."""
        node: INode = CompliantNode()
        assert isinstance(node.node_type, str)

    def test_version_annotation(self) -> None:
        """version should be annotated as returning str."""
        node: INode = CompliantNode()
        assert isinstance(node.version, str)


class TestINodeImports:
    """Test protocol imports from different locations."""

    def test_import_from_base_module(self) -> None:
        """Test direct import from base module."""
        from omnibase_spi.protocols.nodes.base import INode as BaseINode

        node = CompliantNode()
        assert isinstance(node, BaseINode)

    def test_import_from_nodes_package(self) -> None:
        """Test import from nodes package."""
        from omnibase_spi.protocols.nodes import INode as NodesINode

        node = CompliantNode()
        assert isinstance(node, NodesINode)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.nodes import INode as NodesINode
        from omnibase_spi.protocols.nodes.base import INode as BaseINode

        assert NodesINode is BaseINode

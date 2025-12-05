"""
Tests for ProtocolComputeNode protocol.

Validates that ProtocolComputeNode:
- Is properly runtime checkable
- Defines required properties (node_id, node_type, version, is_deterministic)
- Defines required methods (execute)
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
- Properly extends ProtocolNode
"""

import pytest

from omnibase_spi.protocols.nodes.compute import ProtocolComputeNode


class CompliantComputeNode:
    """A class that fully implements the ProtocolComputeNode protocol."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "compute-node-v1"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    @property
    def is_deterministic(self) -> bool:
        """Return whether node is deterministic."""
        return True

    async def execute(self, input_data: object) -> object:
        """Execute compute operation."""
        return {"result": "computed"}


class PartialComputeNode:
    """A class that only implements some ProtocolComputeNode properties/methods."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "partial-compute-node"

    @property
    def is_deterministic(self) -> bool:
        """Return whether node is deterministic."""
        return True

    # Missing: node_type, version, execute()


class NonCompliantComputeNode:
    """A class that implements none of the ProtocolComputeNode properties/methods."""

    pass


class WrongTypeComputeNode:
    """A class that implements methods with wrong types."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "wrong-type-compute"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    @property
    def is_deterministic(self) -> int:  # type: ignore[override]
        """Return whether node is deterministic (wrong type)."""
        return 1

    async def execute(self, input_data: object) -> object:
        """Execute compute operation."""
        return {"result": "computed"}


class MissingDeterministicProperty:
    """A class missing only the is_deterministic property."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "no-deterministic"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def execute(self, input_data: object) -> object:
        """Execute compute operation."""
        return {"result": "computed"}


class MissingExecuteMethod:
    """A class missing only the execute method."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "no-execute"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    @property
    def is_deterministic(self) -> bool:
        """Return whether node is deterministic."""
        return True


class TestProtocolComputeNodeProtocol:
    """Test suite for ProtocolComputeNode protocol compliance."""

    def test_protocol_compute_node_is_runtime_checkable(self) -> None:
        """ProtocolComputeNode should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolComputeNode, "_is_runtime_protocol") or hasattr(
            ProtocolComputeNode, "__runtime_protocol__"
        )

    def test_protocol_compute_node_is_protocol(self) -> None:
        """ProtocolComputeNode should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolComputeNode has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolComputeNode.__mro__
        )

    def test_protocol_compute_node_has_node_id_property(self) -> None:
        """ProtocolComputeNode should define node_id property (from ProtocolNode)."""
        # Protocol properties appear in __protocol_attrs__
        assert "node_id" in dir(ProtocolComputeNode)

    def test_protocol_compute_node_has_node_type_property(self) -> None:
        """ProtocolComputeNode should define node_type property (from ProtocolNode)."""
        assert "node_type" in dir(ProtocolComputeNode)

    def test_protocol_compute_node_has_version_property(self) -> None:
        """ProtocolComputeNode should define version property (from ProtocolNode)."""
        assert "version" in dir(ProtocolComputeNode)

    def test_protocol_compute_node_has_is_deterministic_property(self) -> None:
        """ProtocolComputeNode should define is_deterministic property."""
        assert "is_deterministic" in dir(ProtocolComputeNode)

    def test_protocol_compute_node_has_execute_method(self) -> None:
        """ProtocolComputeNode should define execute method."""
        assert "execute" in dir(ProtocolComputeNode)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolComputeNode protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolComputeNode()  # type: ignore[misc]


class TestProtocolComputeNodeCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolComputeNode properties/methods should pass isinstance check."""
        node = CompliantComputeNode()
        assert isinstance(node, ProtocolComputeNode)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolComputeNode properties/methods should fail isinstance check."""
        node = PartialComputeNode()
        assert not isinstance(node, ProtocolComputeNode)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolComputeNode properties/methods should fail isinstance check."""
        node = NonCompliantComputeNode()
        assert not isinstance(node, ProtocolComputeNode)

    def test_wrong_type_still_passes_structural_check(self) -> None:
        """
        A class with properties of wrong types still passes isinstance.

        Note: Runtime protocol checking only verifies attribute existence,
        not type correctness. Type checking is enforced by static analysis tools.
        """
        node = WrongTypeComputeNode()
        # Runtime check passes because attributes exist
        assert isinstance(node, ProtocolComputeNode)

    def test_missing_is_deterministic_fails_isinstance(self) -> None:
        """A class missing is_deterministic property should fail isinstance check."""
        node = MissingDeterministicProperty()
        assert not isinstance(node, ProtocolComputeNode)

    def test_missing_execute_fails_isinstance(self) -> None:
        """A class missing execute method should fail isinstance check."""
        node = MissingExecuteMethod()
        assert not isinstance(node, ProtocolComputeNode)


class TestProtocolComputeNodeMethodSignatures:
    """Test method signatures and property values."""

    def test_is_deterministic_returns_bool(self) -> None:
        """is_deterministic property should return a bool."""
        node = CompliantComputeNode()
        result = node.is_deterministic
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.asyncio
    async def test_execute_is_async(self) -> None:
        """execute method should be async and return awaitable."""
        node = CompliantComputeNode()
        result = node.execute({"data": "test"})
        # Verify it's a coroutine
        assert hasattr(result, "__await__")
        # Clean up the coroutine
        await result

    @pytest.mark.asyncio
    async def test_execute_returns_value(self) -> None:
        """execute method should return a value when awaited."""
        node = CompliantComputeNode()
        result = await node.execute({"data": "test"})
        assert result is not None
        assert isinstance(result, dict)
        assert result == {"result": "computed"}


class TestProtocolComputeNodePropertyValues:
    """Test property values from compliant implementations."""

    def test_node_id_returns_string(self) -> None:
        """node_id property should return a string."""
        node = CompliantComputeNode()
        result = node.node_id
        assert isinstance(result, str)
        assert result == "compute-node-v1"

    def test_node_type_returns_string(self) -> None:
        """node_type property should return a string."""
        node = CompliantComputeNode()
        result = node.node_type
        assert isinstance(result, str)
        assert result == "compute"

    def test_version_returns_string(self) -> None:
        """version property should return a string."""
        node = CompliantComputeNode()
        result = node.version
        assert isinstance(result, str)
        assert result == "1.0.0"

    def test_is_deterministic_returns_bool(self) -> None:
        """is_deterministic property should return a bool."""
        node = CompliantComputeNode()
        result = node.is_deterministic
        assert isinstance(result, bool)
        assert result is True


class TestProtocolComputeNodeTypeAnnotations:
    """Test type annotations on ProtocolComputeNode protocol."""

    def test_node_id_annotation(self) -> None:
        """node_id should be annotated as returning str."""
        # Protocol properties don't expose annotations directly
        # Instead, verify via a compliant implementation
        node: ProtocolComputeNode = CompliantComputeNode()
        assert isinstance(node.node_id, str)

    def test_node_type_annotation(self) -> None:
        """node_type should be annotated as returning str."""
        node: ProtocolComputeNode = CompliantComputeNode()
        assert isinstance(node.node_type, str)

    def test_version_annotation(self) -> None:
        """version should be annotated as returning str."""
        node: ProtocolComputeNode = CompliantComputeNode()
        assert isinstance(node.version, str)

    def test_is_deterministic_annotation(self) -> None:
        """is_deterministic should be annotated as returning bool."""
        node: ProtocolComputeNode = CompliantComputeNode()
        assert isinstance(node.is_deterministic, bool)


class TestProtocolComputeNodeImports:
    """Test protocol imports from different locations."""

    def test_import_from_compute_module(self) -> None:
        """Test direct import from compute module."""
        from omnibase_spi.protocols.nodes.compute import (
            ProtocolComputeNode as ComputeProtocolComputeNode,
        )

        node = CompliantComputeNode()
        assert isinstance(node, ComputeProtocolComputeNode)

    def test_import_from_nodes_package(self) -> None:
        """Test import from nodes package."""
        from omnibase_spi.protocols.nodes import (
            ProtocolComputeNode as NodesProtocolComputeNode,
        )

        node = CompliantComputeNode()
        assert isinstance(node, NodesProtocolComputeNode)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.nodes import (
            ProtocolComputeNode as NodesProtocolComputeNode,
        )
        from omnibase_spi.protocols.nodes.compute import (
            ProtocolComputeNode as ComputeProtocolComputeNode,
        )

        assert NodesProtocolComputeNode is ComputeProtocolComputeNode


class TestProtocolComputeNodeInheritance:
    """Test that ProtocolComputeNode properly extends ProtocolNode."""

    def test_extends_protocol_node(self) -> None:
        """ProtocolComputeNode should extend ProtocolNode."""
        from omnibase_spi.protocols.nodes.base import ProtocolNode

        # Check that ProtocolNode is in the MRO
        assert ProtocolNode in ProtocolComputeNode.__mro__

    def test_compliant_compute_node_is_also_protocol_node(self) -> None:
        """A compliant ProtocolComputeNode should also pass ProtocolNode isinstance check."""
        from omnibase_spi.protocols.nodes.base import ProtocolNode

        node = CompliantComputeNode()
        assert isinstance(node, ProtocolComputeNode)
        assert isinstance(node, ProtocolNode)

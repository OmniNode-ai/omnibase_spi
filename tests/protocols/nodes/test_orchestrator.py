"""
Tests for ProtocolOrchestratorNode protocol.

Validates that ProtocolOrchestratorNode:
- Is properly runtime checkable
- Inherits from ProtocolNode
- Defines required execute() method
- Works correctly with isinstance checks for compliant/non-compliant classes
- Handles async execution properly
"""

import pytest

from omnibase_spi.protocols.nodes.orchestrator import ProtocolOrchestratorNode

# Mock classes for testing (no omnibase_core dependency)
class MockOrchestrationInput:
    """Mock orchestration input for testing."""
    def __init__(self, workflow_id: str, steps: list):
        self.workflow_id = workflow_id
        self.steps = steps


class MockOrchestrationOutput:
    """Mock orchestration output for testing."""
    def __init__(self, workflow_id: str, status: str, results: dict):
        self.workflow_id = workflow_id
        self.status = status
        self.results = results


class CompliantOrchestratorNode:
    """A class that fully implements the ProtocolOrchestratorNode protocol."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "test-orchestrator-node-v1"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "orchestrator"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def execute(
        self,
        input_data: object,
    ) -> object:  # type: ignore[override]
        """Execute orchestration."""
        # Mock implementation for testing
        return MockOrchestrationOutput(
            workflow_id=input_data.workflow_id,  # type: ignore[attr-defined]
            status="completed",
            results={},
        )


class PartialOrchestratorNode:
    """A class that only implements ProtocolNode properties, missing execute method."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "partial-orchestrator-node"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "orchestrator"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"


class NonCompliantOrchestratorNode:
    """A class that implements none of the ProtocolOrchestratorNode requirements."""

    pass


class WrongSignatureOrchestratorNode:
    """A class with execute method but wrong signature."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "wrong-signature-orchestrator"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "orchestrator"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    async def execute(self, _data: dict) -> dict:  # type: ignore[override]
        """Execute with wrong signature."""
        return {}


class SyncExecuteOrchestratorNode:
    """A class with synchronous execute instead of async."""

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return "sync-execute-orchestrator"

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "orchestrator"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    def execute(  # type: ignore[override]
        self,
        input_data: object,
    ) -> object:
        """Non-async execute method."""
        return MockOrchestrationOutput(
            workflow_id=input_data.workflow_id,  # type: ignore[attr-defined]
            status="completed",
            results={},
        )


class TestProtocolOrchestratorNodeProtocol:
    """Test suite for ProtocolOrchestratorNode protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolOrchestratorNode should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolOrchestratorNode, "_is_runtime_protocol") or hasattr(
            ProtocolOrchestratorNode, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolOrchestratorNode should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolOrchestratorNode has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolOrchestratorNode.__mro__
        )

    def test_protocol_inherits_from_protocol_node(self) -> None:
        """ProtocolOrchestratorNode should inherit from ProtocolNode."""
        from omnibase_spi.protocols.nodes.base import ProtocolNode

        # Check that ProtocolNode is in the MRO (can't use issubclass with protocols that have properties)
        assert ProtocolNode in ProtocolOrchestratorNode.__mro__

    def test_protocol_has_execute_method(self) -> None:
        """ProtocolOrchestratorNode should define execute method."""
        assert "execute" in dir(ProtocolOrchestratorNode)

    def test_protocol_has_node_id_property(self) -> None:
        """ProtocolOrchestratorNode should have node_id property (from ProtocolNode)."""
        assert "node_id" in dir(ProtocolOrchestratorNode)

    def test_protocol_has_node_type_property(self) -> None:
        """ProtocolOrchestratorNode should have node_type property (from ProtocolNode)."""
        assert "node_type" in dir(ProtocolOrchestratorNode)

    def test_protocol_has_version_property(self) -> None:
        """ProtocolOrchestratorNode should have version property (from ProtocolNode)."""
        assert "version" in dir(ProtocolOrchestratorNode)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolOrchestratorNode protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolOrchestratorNode()  # type: ignore[misc]


class TestProtocolOrchestratorNodeCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolOrchestratorNode requirements should pass isinstance check."""
        node = CompliantOrchestratorNode()
        assert isinstance(node, ProtocolOrchestratorNode)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing execute method should fail isinstance check."""
        node = PartialOrchestratorNode()
        assert not isinstance(node, ProtocolOrchestratorNode)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolOrchestratorNode requirements should fail isinstance check."""
        node = NonCompliantOrchestratorNode()
        assert not isinstance(node, ProtocolOrchestratorNode)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with execute method but wrong signature still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Type checking is enforced by static analysis tools.
        """
        node = WrongSignatureOrchestratorNode()
        # Runtime check passes because execute method exists
        assert isinstance(node, ProtocolOrchestratorNode)

    def test_sync_execute_still_passes_structural_check(self) -> None:
        """
        A class with synchronous execute still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not whether it's async. Type checking is enforced by static analysis tools.
        """
        node = SyncExecuteOrchestratorNode()
        # Runtime check passes because execute method exists
        assert isinstance(node, ProtocolOrchestratorNode)


class TestProtocolOrchestratorNodeMethodSignatures:
    """Test method signatures and behavior."""

    @pytest.mark.asyncio
    async def test_execute_method_is_async(self) -> None:
        """execute method should be async."""
        import inspect

        node = CompliantOrchestratorNode()
        assert inspect.iscoroutinefunction(node.execute)

    @pytest.mark.asyncio
    async def test_execute_accepts_orchestration_input(self) -> None:
        """execute should accept orchestration input."""
        node = CompliantOrchestratorNode()
        input_data = MockOrchestrationInput(
            workflow_id="test-workflow-123",
            steps=[],
        )

        result = await node.execute(input_data)
        # Verify result has expected attributes
        assert hasattr(result, 'workflow_id')
        assert hasattr(result, 'status')
        assert hasattr(result, 'results')

    @pytest.mark.asyncio
    async def test_execute_returns_orchestration_output(self) -> None:
        """execute should return orchestration output."""
        node = CompliantOrchestratorNode()
        input_data = MockOrchestrationInput(
            workflow_id="test-workflow-456",
            steps=[],
        )

        result = await node.execute(input_data)
        # Verify result has expected structure
        assert hasattr(result, 'workflow_id')
        assert hasattr(result, 'status')
        assert result.workflow_id == "test-workflow-456"
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_execute_can_be_awaited(self) -> None:
        """execute should be awaitable."""
        node = CompliantOrchestratorNode()
        input_data = MockOrchestrationInput(
            workflow_id="test-workflow-789",
            steps=[],
        )

        # This should not raise
        result = await node.execute(input_data)
        assert result is not None


class TestProtocolOrchestratorNodePropertyValues:
    """Test property values from compliant implementations."""

    def test_node_id_returns_string(self) -> None:
        """node_id property should return a string."""
        node = CompliantOrchestratorNode()
        result = node.node_id
        assert isinstance(result, str)
        assert result == "test-orchestrator-node-v1"

    def test_node_type_returns_string(self) -> None:
        """node_type property should return a string."""
        node = CompliantOrchestratorNode()
        result = node.node_type
        assert isinstance(result, str)
        assert result == "orchestrator"

    def test_version_returns_string(self) -> None:
        """version property should return a string."""
        node = CompliantOrchestratorNode()
        result = node.version
        assert isinstance(result, str)
        assert result == "1.0.0"


class TestProtocolOrchestratorNodeTypeAnnotations:
    """Test type annotations on ProtocolOrchestratorNode protocol."""

    def test_node_id_annotation(self) -> None:
        """node_id should be annotated as returning str."""
        node: ProtocolOrchestratorNode = CompliantOrchestratorNode()
        assert isinstance(node.node_id, str)

    def test_node_type_annotation(self) -> None:
        """node_type should be annotated as returning str."""
        node: ProtocolOrchestratorNode = CompliantOrchestratorNode()
        assert isinstance(node.node_type, str)

    def test_version_annotation(self) -> None:
        """version should be annotated as returning str."""
        node: ProtocolOrchestratorNode = CompliantOrchestratorNode()
        assert isinstance(node.version, str)


class TestProtocolOrchestratorNodeImports:
    """Test protocol imports from different locations."""

    def test_import_from_orchestrator_module(self) -> None:
        """Test direct import from orchestrator module."""
        from omnibase_spi.protocols.nodes.orchestrator import (
            ProtocolOrchestratorNode as DirectProtocolOrchestratorNode,
        )

        node = CompliantOrchestratorNode()
        assert isinstance(node, DirectProtocolOrchestratorNode)

    def test_import_from_nodes_package(self) -> None:
        """Test import from nodes package."""
        from omnibase_spi.protocols.nodes import (
            ProtocolOrchestratorNode as NodesProtocolOrchestratorNode,
        )

        node = CompliantOrchestratorNode()
        assert isinstance(node, NodesProtocolOrchestratorNode)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.nodes import (
            ProtocolOrchestratorNode as NodesProtocolOrchestratorNode,
        )
        from omnibase_spi.protocols.nodes.orchestrator import (
            ProtocolOrchestratorNode as DirectProtocolOrchestratorNode,
        )

        assert NodesProtocolOrchestratorNode is DirectProtocolOrchestratorNode

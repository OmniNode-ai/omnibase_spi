"""
Tests for forward reference validation in TYPE_CHECKING blocks.

Validates that:
- All protocol imports work without errors
- Forward references in TYPE_CHECKING blocks resolve correctly
- @runtime_checkable protocols support isinstance() checks
- Protocol type hints are correctly formed even without Core
"""

from __future__ import annotations

import importlib
import importlib.util
from typing import get_type_hints

import pytest

# Check if omnibase_core models are available for forward reference resolution tests
# We use importlib.util.find_spec to check for module availability without importing
CORE_MODELS_AVAILABLE = (
    importlib.util.find_spec("omnibase_core.models.compute") is not None
    and importlib.util.find_spec("omnibase_core.models.effect") is not None
    and importlib.util.find_spec("omnibase_core.models.protocol") is not None
    and importlib.util.find_spec("omnibase_core.models.contract") is not None
)


class TestNodeProtocolImports:
    """Tests for node protocol imports."""

    def test_protocol_node_import(self) -> None:
        """Test that ProtocolNode can be imported without errors."""
        from omnibase_spi.protocols.nodes import ProtocolNode

        assert ProtocolNode is not None
        assert hasattr(ProtocolNode, "__protocol_attrs__") or isinstance(
            ProtocolNode, type
        )

    def test_protocol_compute_node_import(self) -> None:
        """Test that ProtocolComputeNode can be imported without errors."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert ProtocolComputeNode is not None

    def test_protocol_effect_node_import(self) -> None:
        """Test that ProtocolEffectNode can be imported without errors."""
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert ProtocolEffectNode is not None

    def test_protocol_reducer_node_import(self) -> None:
        """Test that ProtocolReducerNode can be imported without errors."""
        from omnibase_spi.protocols.nodes import ProtocolReducerNode

        assert ProtocolReducerNode is not None

    def test_protocol_orchestrator_node_import(self) -> None:
        """Test that ProtocolOrchestratorNode can be imported without errors."""
        from omnibase_spi.protocols.nodes import ProtocolOrchestratorNode

        assert ProtocolOrchestratorNode is not None

    def test_all_node_protocols_in_module_all(self) -> None:
        """Test that all node protocols are exported in __all__."""
        from omnibase_spi.protocols import nodes

        expected = [
            "ProtocolNode",
            "ProtocolComputeNode",
            "ProtocolEffectNode",
            "ProtocolReducerNode",
            "ProtocolOrchestratorNode",
        ]
        for protocol_name in expected:
            assert protocol_name in nodes.__all__, f"{protocol_name} not in __all__"
            assert hasattr(nodes, protocol_name), f"{protocol_name} not accessible"


class TestHandlerProtocolImports:
    """Tests for handler protocol imports."""

    def test_protocol_handler_import(self) -> None:
        """Test that ProtocolHandler can be imported without errors."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert ProtocolHandler is not None

    def test_protocol_handler_in_module_all(self) -> None:
        """Test that ProtocolHandler is exported in __all__."""
        from omnibase_spi.protocols import handlers

        assert "ProtocolHandler" in handlers.__all__
        assert hasattr(handlers, "ProtocolHandler")


class TestContractCompilerImports:
    """Tests for contract compiler protocol imports."""

    def test_effect_contract_compiler_import(self) -> None:
        """Test that ProtocolEffectContractCompiler can be imported without errors."""
        from omnibase_spi.protocols.contracts import ProtocolEffectContractCompiler

        assert ProtocolEffectContractCompiler is not None

    def test_workflow_contract_compiler_import(self) -> None:
        """Test that ProtocolWorkflowContractCompiler can be imported without errors."""
        from omnibase_spi.protocols.contracts import ProtocolWorkflowContractCompiler

        assert ProtocolWorkflowContractCompiler is not None

    def test_fsm_contract_compiler_import(self) -> None:
        """Test that ProtocolFSMContractCompiler can be imported without errors."""
        from omnibase_spi.protocols.contracts import ProtocolFSMContractCompiler

        assert ProtocolFSMContractCompiler is not None

    def test_all_contract_compilers_in_module_all(self) -> None:
        """Test that all contract compilers are exported in __all__."""
        from omnibase_spi.protocols import contracts

        expected = [
            "ProtocolEffectContractCompiler",
            "ProtocolWorkflowContractCompiler",
            "ProtocolFSMContractCompiler",
        ]
        for protocol_name in expected:
            assert protocol_name in contracts.__all__, f"{protocol_name} not in __all__"
            assert hasattr(contracts, protocol_name), f"{protocol_name} not accessible"


class TestRegistryProtocolImports:
    """Tests for registry protocol imports."""

    def test_protocol_handler_registry_import(self) -> None:
        """Test that ProtocolHandlerRegistry can be imported without errors."""
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert ProtocolHandlerRegistry is not None

    def test_registry_in_module_all(self) -> None:
        """Test that ProtocolHandlerRegistry is exported in __all__."""
        from omnibase_spi.protocols import registry

        assert "ProtocolHandlerRegistry" in registry.__all__
        assert hasattr(registry, "ProtocolHandlerRegistry")


class TestRuntimeCheckableProtocols:
    """Tests for @runtime_checkable protocol support."""

    def test_protocol_node_is_runtime_checkable(self) -> None:
        """Test that ProtocolNode supports isinstance() checks."""
        from omnibase_spi.protocols.nodes import ProtocolNode

        # Verify the protocol has the runtime checkable marker
        assert hasattr(ProtocolNode, "_is_runtime_protocol") or hasattr(
            ProtocolNode, "__protocol_attrs__"
        )

    def test_protocol_compute_node_is_runtime_checkable(self) -> None:
        """Test that ProtocolComputeNode supports isinstance() checks."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert hasattr(ProtocolComputeNode, "_is_runtime_protocol") or hasattr(
            ProtocolComputeNode, "__protocol_attrs__"
        )

    def test_protocol_effect_node_is_runtime_checkable(self) -> None:
        """Test that ProtocolEffectNode supports isinstance() checks."""
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert hasattr(ProtocolEffectNode, "_is_runtime_protocol") or hasattr(
            ProtocolEffectNode, "__protocol_attrs__"
        )

    def test_protocol_reducer_node_is_runtime_checkable(self) -> None:
        """Test that ProtocolReducerNode supports isinstance() checks."""
        from omnibase_spi.protocols.nodes import ProtocolReducerNode

        assert hasattr(ProtocolReducerNode, "_is_runtime_protocol") or hasattr(
            ProtocolReducerNode, "__protocol_attrs__"
        )

    def test_protocol_orchestrator_node_is_runtime_checkable(self) -> None:
        """Test that ProtocolOrchestratorNode supports isinstance() checks."""
        from omnibase_spi.protocols.nodes import ProtocolOrchestratorNode

        assert hasattr(ProtocolOrchestratorNode, "_is_runtime_protocol") or hasattr(
            ProtocolOrchestratorNode, "__protocol_attrs__"
        )

    def test_protocol_handler_is_runtime_checkable(self) -> None:
        """Test that ProtocolHandler supports isinstance() checks."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert hasattr(ProtocolHandler, "_is_runtime_protocol") or hasattr(
            ProtocolHandler, "__protocol_attrs__"
        )

    def test_protocol_handler_registry_is_runtime_checkable(self) -> None:
        """Test that ProtocolHandlerRegistry supports isinstance() checks."""
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert hasattr(ProtocolHandlerRegistry, "_is_runtime_protocol") or hasattr(
            ProtocolHandlerRegistry, "__protocol_attrs__"
        )

    def test_contract_compilers_are_runtime_checkable(self) -> None:
        """Test that contract compilers support isinstance() checks."""
        from omnibase_spi.protocols.contracts import (
            ProtocolEffectContractCompiler,
            ProtocolFSMContractCompiler,
            ProtocolWorkflowContractCompiler,
        )

        for protocol in [
            ProtocolEffectContractCompiler,
            ProtocolWorkflowContractCompiler,
            ProtocolFSMContractCompiler,
        ]:
            assert hasattr(protocol, "_is_runtime_protocol") or hasattr(
                protocol, "__protocol_attrs__"
            ), f"{protocol.__name__} is not runtime_checkable"


class TestIsinstanceChecks:
    """Tests for isinstance() checks with mock implementations."""

    def test_isinstance_with_mock_compute_node(self) -> None:
        """Test isinstance() works with a mock ProtocolComputeNode implementation."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        class MockComputeNode:
            """Mock implementation of ProtocolComputeNode."""

            node_id = "test-node"
            node_type = "compute"
            version = "1.0.0"
            is_deterministic = True

            async def execute(self, input_data: object) -> object:
                return input_data

        mock = MockComputeNode()
        # isinstance() should work with runtime_checkable protocols
        assert isinstance(mock, ProtocolComputeNode)

    def test_isinstance_with_mock_handler(self) -> None:
        """Test isinstance() works with a mock ProtocolHandler implementation."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        class MockHandler:
            """Mock implementation of ProtocolHandler."""

            async def initialize(self, config: object) -> None:
                pass

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                pass

            async def execute(
                self, request: object, operation_config: object
            ) -> object:
                return {}

        mock = MockHandler()
        assert isinstance(mock, ProtocolHandler)

    def test_isinstance_with_mock_registry(self) -> None:
        """Test isinstance() works with a mock ProtocolHandlerRegistry implementation."""
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        class MockRegistry:
            """Mock implementation of ProtocolHandlerRegistry."""

            def register(self, protocol_type: str, handler_cls: type) -> None:
                pass

            def get(self, protocol_type: str) -> type:
                return type

            def list_protocols(self) -> list[str]:
                return []

            def is_registered(self, protocol_type: str) -> bool:
                return False

        mock = MockRegistry()
        assert isinstance(mock, ProtocolHandlerRegistry)

    def test_isinstance_negative_case(self) -> None:
        """Test isinstance() returns False for non-compliant objects."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        class NotAHandler:
            """Class that doesn't implement ProtocolHandler."""

            def some_method(self) -> None:
                pass

        obj = NotAHandler()
        assert not isinstance(obj, ProtocolHandler)


class TestForwardReferenceResolution:
    """Tests for forward reference resolution when Core is available."""

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_compute_node_type_hints_resolve(self) -> None:
        """Test that ProtocolComputeNode type hints resolve with Core."""
        from omnibase_spi.protocols.nodes.compute import ProtocolComputeNode

        # get_type_hints should resolve forward references when Core is available
        hints = get_type_hints(ProtocolComputeNode.execute)
        assert "input_data" in hints
        assert "return" in hints

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_effect_node_type_hints_resolve(self) -> None:
        """Test that ProtocolEffectNode type hints resolve with Core."""
        from omnibase_spi.protocols.nodes.effect import ProtocolEffectNode

        hints = get_type_hints(ProtocolEffectNode.execute)
        assert "input_data" in hints
        assert "return" in hints

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_handler_type_hints_resolve(self) -> None:
        """Test that ProtocolHandler type hints resolve with Core."""
        from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler

        hints = get_type_hints(ProtocolHandler.execute)
        assert "request" in hints
        assert "operation_config" in hints
        assert "return" in hints

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_contract_compiler_type_hints_resolve(self) -> None:
        """Test that contract compiler type hints resolve with Core."""
        from omnibase_spi.protocols.contracts.effect_compiler import (
            ProtocolEffectContractCompiler,
        )

        hints = get_type_hints(ProtocolEffectContractCompiler.compile)
        assert "contract_path" in hints
        assert "return" in hints

    def test_forward_references_without_core(self) -> None:
        """Test that protocols work even without Core installed.

        Forward references should remain as strings when Core is not available,
        but imports should still work.
        """
        # These imports should work regardless of Core availability
        from omnibase_spi.protocols.contracts import ProtocolEffectContractCompiler
        from omnibase_spi.protocols.handlers import ProtocolHandler
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        # Protocols should be importable
        assert ProtocolComputeNode is not None
        assert ProtocolHandler is not None
        assert ProtocolEffectContractCompiler is not None

        # Protocol classes should have the expected methods (as protocol methods)
        assert hasattr(ProtocolComputeNode, "execute")
        assert hasattr(ProtocolHandler, "initialize")
        assert hasattr(ProtocolHandler, "shutdown")
        assert hasattr(ProtocolHandler, "execute")
        assert hasattr(ProtocolEffectContractCompiler, "compile")
        assert hasattr(ProtocolEffectContractCompiler, "validate")


class TestProtocolMethodSignatures:
    """Tests for protocol method signature correctness."""

    def test_compute_node_has_execute_method(self) -> None:
        """Test ProtocolComputeNode has execute method."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert hasattr(ProtocolComputeNode, "execute")
        # Method should be callable (protocol method)
        assert callable(getattr(ProtocolComputeNode, "execute", None))

    def test_compute_node_has_is_deterministic_property(self) -> None:
        """Test ProtocolComputeNode has is_deterministic property."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert hasattr(ProtocolComputeNode, "is_deterministic")

    def test_effect_node_has_lifecycle_methods(self) -> None:
        """Test ProtocolEffectNode has initialize and shutdown methods."""
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert hasattr(ProtocolEffectNode, "initialize")
        assert hasattr(ProtocolEffectNode, "shutdown")
        assert hasattr(ProtocolEffectNode, "execute")

    def test_handler_has_lifecycle_methods(self) -> None:
        """Test ProtocolHandler has lifecycle methods."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert hasattr(ProtocolHandler, "initialize")
        assert hasattr(ProtocolHandler, "shutdown")
        assert hasattr(ProtocolHandler, "execute")

    def test_registry_has_crud_methods(self) -> None:
        """Test ProtocolHandlerRegistry has CRUD methods."""
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert hasattr(ProtocolHandlerRegistry, "register")
        assert hasattr(ProtocolHandlerRegistry, "get")
        assert hasattr(ProtocolHandlerRegistry, "list_protocols")
        assert hasattr(ProtocolHandlerRegistry, "is_registered")

    def test_contract_compilers_have_compile_and_validate(self) -> None:
        """Test contract compilers have compile and validate methods."""
        from omnibase_spi.protocols.contracts import (
            ProtocolEffectContractCompiler,
            ProtocolFSMContractCompiler,
            ProtocolWorkflowContractCompiler,
        )

        for compiler in [
            ProtocolEffectContractCompiler,
            ProtocolWorkflowContractCompiler,
            ProtocolFSMContractCompiler,
        ]:
            assert hasattr(compiler, "compile"), f"{compiler.__name__} missing compile"
            assert hasattr(
                compiler, "validate"
            ), f"{compiler.__name__} missing validate"


class TestModuleReimport:
    """Tests for module reimport behavior."""

    def test_reimport_nodes_module(self) -> None:
        """Test that nodes module can be reimported without errors."""
        import omnibase_spi.protocols.nodes as nodes_module

        # Reimport should work
        importlib.reload(nodes_module)

        # Protocols should still be available
        assert hasattr(nodes_module, "ProtocolNode")
        assert hasattr(nodes_module, "ProtocolComputeNode")

    def test_reimport_handlers_module(self) -> None:
        """Test that handlers module can be reimported without errors."""
        import omnibase_spi.protocols.handlers as handlers_module

        importlib.reload(handlers_module)
        assert hasattr(handlers_module, "ProtocolHandler")

    def test_reimport_contracts_module(self) -> None:
        """Test that contracts module can be reimported without errors."""
        import omnibase_spi.protocols.contracts as contracts_module

        importlib.reload(contracts_module)
        assert hasattr(contracts_module, "ProtocolEffectContractCompiler")

    def test_reimport_registry_module(self) -> None:
        """Test that registry module can be reimported without errors."""
        import omnibase_spi.protocols.registry as registry_module

        importlib.reload(registry_module)
        assert hasattr(registry_module, "ProtocolHandlerRegistry")

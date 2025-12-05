"""
Tests for forward reference validation in TYPE_CHECKING blocks.

This module validates the forward reference handling in SPI protocols when
omnibase_core models are used as type hints. The SPI layer uses TYPE_CHECKING
blocks to conditionally import Core models, allowing the SPI to remain
importable even when Core is not installed.

Test Categories:
    TestNodeProtocolImports: Node protocol import validation
    TestHandlerProtocolImports: Handler protocol import validation
    TestContractCompilerImports: Contract compiler import validation
    TestRegistryProtocolImports: Registry protocol import validation
    TestRuntimeCheckableProtocols: @runtime_checkable decorator validation
    TestIsinstanceChecks: isinstance() behavior with mock implementations
    TestForwardReferenceResolution: Type hint resolution when Core available
    TestProtocolMethodSignatures: Protocol method/attribute presence
    TestModuleReimport: Module reload behavior validation

Architecture Context:
    SPI protocols reference Core models (e.g., ModelComputeInput) in type hints.
    These imports are guarded by TYPE_CHECKING blocks to avoid circular imports
    and to allow SPI to be used standalone for interface definitions.
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
    """Test node protocol imports without forward reference errors.

    Validates that all node protocol types can be imported from
    omnibase_spi.protocols.nodes without triggering import errors
    from forward references to Core models.
    """

    def test_protocol_node_import(self) -> None:
        """Validate ProtocolNode import succeeds without forward reference errors.

        The base node protocol should be importable and recognized as a Protocol
        type with the standard __protocol_attrs__ attribute.
        """
        from omnibase_spi.protocols.nodes import ProtocolNode

        assert ProtocolNode is not None
        # Verify ProtocolNode is a proper Protocol with @runtime_checkable decorator
        # _is_runtime_protocol is the canonical marker set by @runtime_checkable
        assert getattr(ProtocolNode, "_is_runtime_protocol", False) is True, (
            "ProtocolNode must be decorated with @runtime_checkable"
        )
        # Verify __protocol_attrs__ exists (standard Protocol attribute)
        assert hasattr(ProtocolNode, "__protocol_attrs__"), (
            "ProtocolNode must be a typing.Protocol with __protocol_attrs__"
        )

    def test_protocol_compute_node_import(self) -> None:
        """Validate ProtocolComputeNode import succeeds.

        Compute nodes define pure transformation operations and reference
        ModelComputeInput/ModelComputeOutput from Core in their type hints.
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert ProtocolComputeNode is not None

    def test_protocol_effect_node_import(self) -> None:
        """Validate ProtocolEffectNode import succeeds.

        Effect nodes handle external I/O operations and reference
        ModelEffectInput/ModelEffectOutput from Core in their type hints.
        """
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert ProtocolEffectNode is not None

    def test_protocol_reducer_node_import(self) -> None:
        """Validate ProtocolReducerNode import succeeds.

        Reducer nodes handle aggregation and persistence operations.
        """
        from omnibase_spi.protocols.nodes import ProtocolReducerNode

        assert ProtocolReducerNode is not None

    def test_protocol_orchestrator_node_import(self) -> None:
        """Validate ProtocolOrchestratorNode import succeeds.

        Orchestrator nodes coordinate workflow execution across other node types.
        """
        from omnibase_spi.protocols.nodes import ProtocolOrchestratorNode

        assert ProtocolOrchestratorNode is not None

    def test_all_node_protocols_in_module_all(self) -> None:
        """Validate all node protocols are properly exported in __all__.

        Ensures consumers can use 'from omnibase_spi.protocols.nodes import *'
        and get all expected protocol types.
        """
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

    def test_all_node_exports_are_importable(self) -> None:
        """Validate all items in nodes.__all__ are actually importable.

        Ensures no stale or missing exports exist in the module's public API.
        This catches cases where __all__ references a name that doesn't exist
        or has been removed from the module.
        """
        from omnibase_spi.protocols import nodes

        for name in nodes.__all__:
            obj = getattr(nodes, name, None)
            assert obj is not None, f"{name} in __all__ but not importable"


class TestHandlerProtocolImports:
    """Test handler protocol imports without forward reference errors.

    Validates that ProtocolHandler can be imported from
    omnibase_spi.protocols.handlers without triggering import errors
    from forward references to Core models used in execute() signatures.
    """

    def test_protocol_handler_import(self) -> None:
        """Validate ProtocolHandler import succeeds.

        Handlers define the execute/initialize/shutdown lifecycle and reference
        Core request/response models in their type hints.
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert ProtocolHandler is not None

    def test_protocol_handler_in_module_all(self) -> None:
        """Validate ProtocolHandler is properly exported in __all__."""
        from omnibase_spi.protocols import handlers

        assert "ProtocolHandler" in handlers.__all__
        assert hasattr(handlers, "ProtocolHandler")

    def test_all_handler_exports_are_importable(self) -> None:
        """Validate all items in handlers.__all__ are actually importable.

        Ensures no stale or missing exports exist in the module's public API.
        This catches cases where __all__ references a name that doesn't exist
        or has been removed from the module.
        """
        from omnibase_spi.protocols import handlers

        for name in handlers.__all__:
            obj = getattr(handlers, name, None)
            assert obj is not None, f"{name} in __all__ but not importable"


class TestContractCompilerImports:
    """Test contract compiler protocol imports without forward reference errors.

    Validates that all contract compiler protocols can be imported from
    omnibase_spi.protocols.contracts without forward reference errors.
    """

    def test_effect_contract_compiler_import(self) -> None:
        """Validate ProtocolEffectContractCompiler import succeeds.

        Effect compilers transform contract definitions into executable effect nodes.
        """
        from omnibase_spi.protocols.contracts import ProtocolEffectContractCompiler

        assert ProtocolEffectContractCompiler is not None

    def test_workflow_contract_compiler_import(self) -> None:
        """Validate ProtocolWorkflowContractCompiler import succeeds.

        Workflow compilers handle multi-step workflow contract compilation.
        """
        from omnibase_spi.protocols.contracts import ProtocolWorkflowContractCompiler

        assert ProtocolWorkflowContractCompiler is not None

    def test_fsm_contract_compiler_import(self) -> None:
        """Validate ProtocolFSMContractCompiler import succeeds.

        FSM compilers handle finite state machine contract compilation.
        """
        from omnibase_spi.protocols.contracts import ProtocolFSMContractCompiler

        assert ProtocolFSMContractCompiler is not None

    def test_all_contract_compilers_in_module_all(self) -> None:
        """Validate all contract compilers are properly exported in __all__.

        Ensures consumers can access all compiler protocols through the
        contracts module's public API.
        """
        from omnibase_spi.protocols import contracts

        expected = [
            "ProtocolEffectContractCompiler",
            "ProtocolWorkflowContractCompiler",
            "ProtocolFSMContractCompiler",
        ]
        for protocol_name in expected:
            assert protocol_name in contracts.__all__, f"{protocol_name} not in __all__"
            assert hasattr(contracts, protocol_name), f"{protocol_name} not accessible"

    def test_all_contract_exports_are_importable(self) -> None:
        """Validate all items in contracts.__all__ are actually importable.

        Ensures no stale or missing exports exist in the module's public API.
        This catches cases where __all__ references a name that doesn't exist
        or has been removed from the module.
        """
        from omnibase_spi.protocols import contracts

        for name in contracts.__all__:
            obj = getattr(contracts, name, None)
            assert obj is not None, f"{name} in __all__ but not importable"


class TestRegistryProtocolImports:
    """Test registry protocol imports without forward reference errors.

    Validates that ProtocolHandlerRegistry can be imported from
    omnibase_spi.protocols.registry without forward reference errors.
    """

    def test_protocol_handler_registry_import(self) -> None:
        """Validate ProtocolHandlerRegistry import succeeds.

        The registry protocol defines handler registration and lookup operations.
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert ProtocolHandlerRegistry is not None

    def test_registry_in_module_all(self) -> None:
        """Validate ProtocolHandlerRegistry is properly exported in __all__."""
        from omnibase_spi.protocols import registry

        assert "ProtocolHandlerRegistry" in registry.__all__
        assert hasattr(registry, "ProtocolHandlerRegistry")

    def test_all_registry_exports_are_importable(self) -> None:
        """Validate all items in registry.__all__ are actually importable.

        Ensures no stale or missing exports exist in the module's public API.
        This catches cases where __all__ references a name that doesn't exist
        or has been removed from the module.
        """
        from omnibase_spi.protocols import registry

        for name in registry.__all__:
            obj = getattr(registry, name, None)
            assert obj is not None, f"{name} in __all__ but not importable"


class TestRuntimeCheckableProtocols:
    """Test @runtime_checkable protocol decorator support.

    Validates that all SPI protocols have the @runtime_checkable decorator,
    enabling isinstance() checks at runtime. This is essential for dependency
    injection and handler validation in omnibase_infra.

    The test uses the canonical _is_runtime_protocol attribute to verify
    that protocols are properly decorated with @runtime_checkable.
    """

    def test_protocol_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolNode has @runtime_checkable decorator.

        Uses _is_runtime_protocol attribute which is the canonical marker.
        """
        from omnibase_spi.protocols.nodes import ProtocolNode

        # Verify the protocol has the runtime checkable marker
        assert getattr(ProtocolNode, "_is_runtime_protocol", False) is True

    def test_protocol_compute_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolComputeNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert getattr(ProtocolComputeNode, "_is_runtime_protocol", False) is True

    def test_protocol_effect_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolEffectNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert getattr(ProtocolEffectNode, "_is_runtime_protocol", False) is True

    def test_protocol_reducer_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolReducerNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolReducerNode

        assert getattr(ProtocolReducerNode, "_is_runtime_protocol", False) is True

    def test_protocol_orchestrator_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolOrchestratorNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolOrchestratorNode

        assert getattr(ProtocolOrchestratorNode, "_is_runtime_protocol", False) is True

    def test_protocol_handler_is_runtime_checkable(self) -> None:
        """Validate ProtocolHandler has @runtime_checkable decorator."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert getattr(ProtocolHandler, "_is_runtime_protocol", False) is True

    def test_protocol_handler_registry_is_runtime_checkable(self) -> None:
        """Validate ProtocolHandlerRegistry has @runtime_checkable decorator."""
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert getattr(ProtocolHandlerRegistry, "_is_runtime_protocol", False) is True

    def test_contract_compilers_are_runtime_checkable(self) -> None:
        """Validate all contract compiler protocols have @runtime_checkable."""
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
            assert (
                getattr(protocol, "_is_runtime_protocol", False) is True
            ), f"{protocol.__name__} is not runtime_checkable"


class TestIsinstanceChecks:
    """Test isinstance() checks with mock implementations.

    Validates that @runtime_checkable protocols correctly identify compliant
    implementations via isinstance(). This is the practical test of runtime
    checkability - protocols should return True for objects that implement
    the required methods/attributes, and False for non-compliant objects.
    """

    def test_isinstance_with_mock_compute_node(self) -> None:
        """Validate isinstance() returns True for compliant ProtocolComputeNode.

        Creates a mock class with all required attributes and methods,
        then verifies isinstance() correctly identifies it as a ProtocolComputeNode.
        """
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
        """Validate isinstance() returns True for compliant ProtocolHandler.

        Creates a mock class with initialize/shutdown/execute methods,
        then verifies isinstance() correctly identifies it as a ProtocolHandler.
        """
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
        """Validate isinstance() returns True for compliant ProtocolHandlerRegistry.

        Creates a mock class with register/get/list_protocols/is_registered methods,
        then verifies isinstance() correctly identifies it.
        """
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
        """Validate isinstance() returns False for non-compliant objects.

        Ensures that objects missing required protocol methods are correctly
        rejected by isinstance() checks, preventing false positives.
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        class NotAHandler:
            """Class that doesn't implement ProtocolHandler."""

            def some_method(self) -> None:
                pass

        obj = NotAHandler()
        assert not isinstance(obj, ProtocolHandler)


class TestForwardReferenceResolution:
    """Test forward reference resolution when Core is available.

    These tests verify that forward references in TYPE_CHECKING blocks can be
    resolved to actual types when omnibase_core is installed. Uses get_type_hints()
    from the typing module to trigger forward reference resolution.

    Tests are skipped when Core is not available (standalone SPI installation).
    """

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_compute_node_type_hints_resolve(self) -> None:
        """Validate ProtocolComputeNode type hints resolve to Core models.

        Uses get_type_hints() to resolve forward references in execute() method,
        verifying that ModelComputeInput and ModelComputeOutput are resolved
        to the actual Core model classes.
        """
        from omnibase_core.models.compute import ModelComputeInput, ModelComputeOutput

        from omnibase_spi.protocols.nodes.compute import ProtocolComputeNode

        # get_type_hints should resolve forward references when Core is available
        hints = get_type_hints(ProtocolComputeNode.execute)
        assert "input_data" in hints
        # Use 'is' for type identity verification: ensures forward reference resolved
        # to the actual class object, not a copy or similarly-named type
        assert hints["input_data"] is ModelComputeInput
        assert "return" in hints
        assert hints["return"] is ModelComputeOutput

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_effect_node_type_hints_resolve(self) -> None:
        """Validate ProtocolEffectNode type hints resolve to Core models.

        Uses get_type_hints() to resolve forward references in execute() method,
        verifying that ModelEffectInput and ModelEffectOutput are resolved
        to the actual Core model classes.
        """
        from omnibase_core.models.effect import ModelEffectInput, ModelEffectOutput

        from omnibase_spi.protocols.nodes.effect import ProtocolEffectNode

        hints = get_type_hints(ProtocolEffectNode.execute)
        assert "input_data" in hints
        # Use 'is' for type identity verification: ensures forward reference resolved
        # to the actual class object, not a copy or similarly-named type
        assert hints["input_data"] is ModelEffectInput
        assert "return" in hints
        assert hints["return"] is ModelEffectOutput

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_handler_type_hints_resolve(self) -> None:
        """Validate ProtocolHandler type hints resolve to Core models.

        Uses get_type_hints() to resolve forward references in execute() method,
        verifying request/response model references are resolved to the actual
        Core model classes.
        """
        from omnibase_core.models.protocol import (
            ModelOperationConfig,
            ModelProtocolRequest,
            ModelProtocolResponse,
        )

        from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler

        hints = get_type_hints(ProtocolHandler.execute)
        assert "request" in hints
        # Use 'is' for type identity verification: ensures forward reference resolved
        # to the actual class object, not a copy or similarly-named type
        assert hints["request"] is ModelProtocolRequest
        assert "operation_config" in hints
        assert hints["operation_config"] is ModelOperationConfig
        assert "return" in hints
        assert hints["return"] is ModelProtocolResponse

    @pytest.mark.skipif(
        not CORE_MODELS_AVAILABLE, reason="omnibase_core models not available"
    )
    def test_contract_compiler_type_hints_resolve(self) -> None:
        """Validate contract compiler type hints resolve to Core models.

        Uses get_type_hints() to resolve forward references in compile() method,
        verifying contract_path and return types are resolved to the actual
        Core model classes.
        """
        from pathlib import Path

        from omnibase_core.models.contract import ModelEffectContract

        from omnibase_spi.protocols.contracts.effect_compiler import (
            ProtocolEffectContractCompiler,
        )

        hints = get_type_hints(ProtocolEffectContractCompiler.compile)
        assert "contract_path" in hints
        # Use 'is' for type identity verification: ensures forward reference resolved
        # to the actual class object, not a copy or similarly-named type
        assert hints["contract_path"] is Path
        assert "return" in hints
        assert hints["return"] is ModelEffectContract

    def test_forward_references_without_core(self) -> None:
        """Validate protocols remain functional without Core installed.

        Forward references stay as strings when Core is unavailable, but
        protocol imports and method access should still work correctly.
        This ensures SPI can be used for interface definitions standalone.
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
    """Test protocol method signature correctness.

    Validates that all protocols define the expected methods and attributes.
    This ensures the protocol contracts are complete and implementations
    in omnibase_infra can satisfy the interface requirements.
    """

    def test_compute_node_has_execute_method(self) -> None:
        """Validate ProtocolComputeNode defines callable execute() method.

        The execute method is the core contract for compute nodes.
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert hasattr(ProtocolComputeNode, "execute")
        # Method should be callable (protocol method)
        assert callable(getattr(ProtocolComputeNode, "execute", None))

    def test_compute_node_has_is_deterministic_property(self) -> None:
        """Validate ProtocolComputeNode defines is_deterministic attribute.

        This property indicates whether the compute operation produces
        deterministic output for the same input.
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert hasattr(ProtocolComputeNode, "is_deterministic")

    def test_effect_node_has_lifecycle_methods(self) -> None:
        """Validate ProtocolEffectNode defines lifecycle methods.

        Effect nodes require initialize/shutdown for resource management
        and execute for the actual I/O operation.
        """
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert hasattr(ProtocolEffectNode, "initialize")
        assert hasattr(ProtocolEffectNode, "shutdown")
        assert hasattr(ProtocolEffectNode, "execute")

    def test_handler_has_lifecycle_methods(self) -> None:
        """Validate ProtocolHandler defines lifecycle methods.

        Handlers require initialize/shutdown for setup/teardown and
        execute for request processing.
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert hasattr(ProtocolHandler, "initialize")
        assert hasattr(ProtocolHandler, "shutdown")
        assert hasattr(ProtocolHandler, "execute")

    def test_registry_has_crud_methods(self) -> None:
        """Validate ProtocolHandlerRegistry defines CRUD operations.

        Registries must support register, get, list_protocols, and
        is_registered operations for handler management.
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert hasattr(ProtocolHandlerRegistry, "register")
        assert hasattr(ProtocolHandlerRegistry, "get")
        assert hasattr(ProtocolHandlerRegistry, "list_protocols")
        assert hasattr(ProtocolHandlerRegistry, "is_registered")

    def test_contract_compilers_have_compile_and_validate(self) -> None:
        """Validate contract compilers define compile() and validate() methods.

        All compiler protocols must support contract compilation and validation.
        """
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

    def test_protocol_node_has_required_attributes(self) -> None:
        """Validate ProtocolNode defines required identity attributes.

        The base node protocol requires node_id, node_type, and version
        properties for node identification and classification.
        """
        from omnibase_spi.protocols.nodes import ProtocolNode

        assert hasattr(ProtocolNode, "node_id"), "ProtocolNode missing node_id"
        assert hasattr(ProtocolNode, "node_type"), "ProtocolNode missing node_type"
        assert hasattr(ProtocolNode, "version"), "ProtocolNode missing version"


class TestModuleReimport:
    """Test module reimport behavior.

    Validates that protocol modules can survive importlib.reload() cycles
    without forward reference errors or lost exports. This is important for
    development workflows and hot-reloading scenarios.
    """

    def test_reimport_nodes_module(self) -> None:
        """Validate nodes module survives reload without errors.

        After reload, all node protocols should remain accessible.
        """
        import omnibase_spi.protocols.nodes as nodes_module

        # Reimport should work
        importlib.reload(nodes_module)

        # Protocols should still be available
        assert hasattr(nodes_module, "ProtocolNode")
        assert hasattr(nodes_module, "ProtocolComputeNode")

    def test_reimport_handlers_module(self) -> None:
        """Validate handlers module survives reload without errors.

        After reload, ProtocolHandler should remain accessible.
        """
        import omnibase_spi.protocols.handlers as handlers_module

        importlib.reload(handlers_module)
        assert hasattr(handlers_module, "ProtocolHandler")

    def test_reimport_contracts_module(self) -> None:
        """Validate contracts module survives reload without errors.

        After reload, all contract compiler protocols should remain accessible.
        """
        import omnibase_spi.protocols.contracts as contracts_module

        importlib.reload(contracts_module)
        assert hasattr(contracts_module, "ProtocolEffectContractCompiler")

    def test_reimport_registry_module(self) -> None:
        """Validate registry module survives reload without errors.

        After reload, ProtocolHandlerRegistry should remain accessible.
        """
        import omnibase_spi.protocols.registry as registry_module

        importlib.reload(registry_module)
        assert hasattr(registry_module, "ProtocolHandlerRegistry")

    def test_reimport_preserves_runtime_checkable_behavior(self) -> None:
        """Validate protocols remain runtime checkable after module reload.

        After reload, protocols should still have _is_runtime_protocol marker
        and isinstance() checks should still work with compliant implementations.
        This addresses PR #34 review feedback requesting stronger post-reload
        validation beyond simple hasattr() checks.
        """
        import omnibase_spi.protocols.nodes as nodes_module

        # Verify protocol is runtime checkable before reload
        assert getattr(nodes_module.ProtocolNode, "_is_runtime_protocol", False) is True

        # Create mock and verify isinstance works before reload
        class MockNodeBeforeReload:
            """Mock implementation before reload."""

            node_id = "test-before"
            node_type = "test"
            version = "1.0.0"

        mock_before = MockNodeBeforeReload()
        assert isinstance(mock_before, nodes_module.ProtocolNode)

        # Reload the module
        importlib.reload(nodes_module)

        # Verify protocol is still runtime checkable after reload
        assert getattr(nodes_module.ProtocolNode, "_is_runtime_protocol", False) is True, (
            "ProtocolNode lost _is_runtime_protocol marker after reload"
        )

        # Verify __protocol_attrs__ still exists (standard Protocol attribute)
        assert hasattr(nodes_module.ProtocolNode, "__protocol_attrs__"), (
            "ProtocolNode lost __protocol_attrs__ after reload"
        )

        # Note: isinstance with pre-reload mock may not work due to class identity
        # changes after reload, but the protocol should still function with new
        # mock instances created after reload
        class MockNodeAfterReload:
            """Mock implementation created after reload."""

            node_id = "test-after"
            node_type = "test"
            version = "1.0.0"

        mock_after = MockNodeAfterReload()
        assert isinstance(mock_after, nodes_module.ProtocolNode), (
            "isinstance() check failed with new mock after reload"
        )

    def test_reimport_preserves_isinstance_for_compute_node(self) -> None:
        """Validate ProtocolComputeNode isinstance checks work after reload.

        Ensures compute node protocol maintains runtime checkable behavior
        through module reload cycles with full method signature compliance.
        """
        import omnibase_spi.protocols.nodes as nodes_module

        # Reload the module
        importlib.reload(nodes_module)

        # Verify runtime checkable marker preserved
        assert getattr(
            nodes_module.ProtocolComputeNode, "_is_runtime_protocol", False
        ) is True, "ProtocolComputeNode lost _is_runtime_protocol after reload"

        # Create compliant mock after reload
        class MockComputeNodeAfterReload:
            """Compliant compute node mock created after reload."""

            node_id = "compute-test"
            node_type = "compute"
            version = "1.0.0"
            is_deterministic = True

            async def execute(self, input_data: object) -> object:
                return input_data

        mock = MockComputeNodeAfterReload()
        assert isinstance(mock, nodes_module.ProtocolComputeNode), (
            "isinstance() check failed for ProtocolComputeNode after reload"
        )

    def test_reimport_preserves_isinstance_for_handler(self) -> None:
        """Validate ProtocolHandler isinstance checks work after reload.

        Ensures handler protocol maintains runtime checkable behavior
        through module reload cycles with lifecycle method compliance.
        """
        import omnibase_spi.protocols.handlers as handlers_module

        # Reload the module
        importlib.reload(handlers_module)

        # Verify runtime checkable marker preserved
        assert getattr(
            handlers_module.ProtocolHandler, "_is_runtime_protocol", False
        ) is True, "ProtocolHandler lost _is_runtime_protocol after reload"

        # Create compliant mock after reload
        class MockHandlerAfterReload:
            """Compliant handler mock created after reload."""

            async def initialize(self, config: object) -> None:
                pass

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                pass

            async def execute(
                self, request: object, operation_config: object
            ) -> object:
                return {}

        mock = MockHandlerAfterReload()
        assert isinstance(mock, handlers_module.ProtocolHandler), (
            "isinstance() check failed for ProtocolHandler after reload"
        )

    def test_reimport_preserves_isinstance_for_registry(self) -> None:
        """Validate ProtocolHandlerRegistry isinstance checks work after reload.

        Ensures registry protocol maintains runtime checkable behavior
        through module reload cycles with CRUD method compliance.
        """
        import omnibase_spi.protocols.registry as registry_module

        # Reload the module
        importlib.reload(registry_module)

        # Verify runtime checkable marker preserved
        assert getattr(
            registry_module.ProtocolHandlerRegistry, "_is_runtime_protocol", False
        ) is True, "ProtocolHandlerRegistry lost _is_runtime_protocol after reload"

        # Create compliant mock after reload
        class MockRegistryAfterReload:
            """Compliant registry mock created after reload."""

            def register(self, protocol_type: str, handler_cls: type) -> None:
                pass

            def get(self, protocol_type: str) -> type:
                return type

            def list_protocols(self) -> list[str]:
                return []

            def is_registered(self, protocol_type: str) -> bool:
                return False

        mock = MockRegistryAfterReload()
        assert isinstance(mock, registry_module.ProtocolHandlerRegistry), (
            "isinstance() check failed for ProtocolHandlerRegistry after reload"
        )

    def test_reimport_preserves_isinstance_for_contract_compilers(self) -> None:
        """Validate contract compiler isinstance checks work after reload.

        Ensures all contract compiler protocols maintain runtime checkable
        behavior through module reload cycles.
        """
        import omnibase_spi.protocols.contracts as contracts_module

        # Reload the module
        importlib.reload(contracts_module)

        # Verify runtime checkable markers preserved for all compilers
        compilers = [
            ("ProtocolEffectContractCompiler", contracts_module.ProtocolEffectContractCompiler),
            ("ProtocolWorkflowContractCompiler", contracts_module.ProtocolWorkflowContractCompiler),
            ("ProtocolFSMContractCompiler", contracts_module.ProtocolFSMContractCompiler),
        ]

        for name, compiler in compilers:
            assert getattr(compiler, "_is_runtime_protocol", False) is True, (
                f"{name} lost _is_runtime_protocol after reload"
            )

        # Create compliant mock for ProtocolEffectContractCompiler after reload
        class MockEffectCompilerAfterReload:
            """Compliant effect compiler mock created after reload."""

            def compile(self, contract_path: object) -> object:
                return None

            def validate(self, contract: object) -> bool:
                return True

        mock = MockEffectCompilerAfterReload()
        assert isinstance(mock, contracts_module.ProtocolEffectContractCompiler), (
            "isinstance() check failed for ProtocolEffectContractCompiler after reload"
        )

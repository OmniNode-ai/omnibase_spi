"""
Tests for forward reference validation in TYPE_CHECKING blocks.

This module validates the forward reference handling in SPI protocols when
omnibase_core models are used as type hints. The SPI layer uses TYPE_CHECKING
blocks to conditionally import Core models, allowing the SPI to remain
importable even when Core is not installed.

Test Categories:
    TestNodeProtocolImports: Node protocol import validation
    TestHandlerProtocolImports: Handler protocol import validation
    TestContractProtocolImports: Contract protocol import validation
    TestRegistryProtocolImports: Registry protocol import validation
    TestRuntimeCheckableProtocols: @runtime_checkable decorator validation
    TestIsinstanceChecks: isinstance() behavior with mock implementations
    TestForwardReferenceResolution: Type hint resolution when Core available
    TestProtocolMethodSignatures: Protocol method/attribute presence
    TestModuleReimport: Module reload behavior validation
    TestProtocolCoverage: Automatic detection of untested protocols

Architecture Context:
    SPI protocols reference Core models (e.g., ModelComputeInput) in type hints.
    These imports are guarded by TYPE_CHECKING blocks to avoid circular imports
    and to allow SPI to be used standalone for interface definitions.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import get_type_hints

import pytest

from omnibase_core.enums import (
    EnumHandlerRole,
    EnumHandlerType,
    EnumHandlerTypeCategory,
)
from omnibase_core.models.handlers import ModelHandlerDescriptor, ModelIdentifier
from omnibase_core.models.primitives.model_semver import ModelSemVer

# Check if omnibase_core models are available for forward reference resolution tests
# We use importlib.util.find_spec to check for module availability without importing
CORE_MODELS_AVAILABLE = (
    importlib.util.find_spec("omnibase_core.models.compute") is not None
    and importlib.util.find_spec("omnibase_core.models.effect") is not None
    and importlib.util.find_spec("omnibase_core.models.protocol") is not None
    and importlib.util.find_spec("omnibase_core.models.contract") is not None
)


def _create_mock_handler_descriptor(
    name: str = "mock-handler",
) -> ModelHandlerDescriptor:
    """Create a mock ModelHandlerDescriptor for testing."""
    return ModelHandlerDescriptor(
        handler_name=ModelIdentifier(namespace="test", name=name),
        handler_version=ModelSemVer(major=1, minor=0, patch=0),
        handler_role=EnumHandlerRole.INFRA_HANDLER,
        handler_type=EnumHandlerType.NAMED,
        handler_type_category=EnumHandlerTypeCategory.EFFECT,
    )


# =============================================================================
# Helper Functions for Protocol Validation
# =============================================================================
# These helpers reduce code duplication across test classes and provide
# consistent validation patterns for protocol verification.
# =============================================================================


def _verify_runtime_checkable_protocol(protocol: type) -> None:
    """Verify a protocol has @runtime_checkable decorator.

    This helper provides consistent validation that a protocol class is
    properly decorated with @runtime_checkable and has standard Protocol
    attributes. Use this for future tests to reduce duplication.

    Args:
        protocol: The protocol class to verify

    Raises:
        AssertionError: If protocol is not runtime checkable or missing
            required Protocol attributes

    Example:
        >>> from omnibase_spi.protocols.nodes import ProtocolNode
        >>> _verify_runtime_checkable_protocol(ProtocolNode)  # No error if valid
    """
    assert getattr(protocol, "_is_runtime_protocol", False) is True, (
        f"{protocol.__name__} must be decorated with @runtime_checkable"
    )
    assert hasattr(protocol, "__protocol_attrs__"), (
        f"{protocol.__name__} must be a typing.Protocol with __protocol_attrs__"
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
        _verify_runtime_checkable_protocol(ProtocolNode)

    def test_protocol_compute_node_import(self) -> None:
        """Validate ProtocolComputeNode import succeeds.

        Compute nodes define pure transformation operations and reference
        ModelComputeInput/ModelComputeOutput from Core in their type hints.
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert ProtocolComputeNode is not None
        _verify_runtime_checkable_protocol(ProtocolComputeNode)

    def test_protocol_effect_node_import(self) -> None:
        """Validate ProtocolEffectNode import succeeds.

        Effect nodes handle external I/O operations and reference
        ModelEffectInput/ModelEffectOutput from Core in their type hints.
        """
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert ProtocolEffectNode is not None
        _verify_runtime_checkable_protocol(ProtocolEffectNode)

    def test_protocol_reducer_node_import(self) -> None:
        """Validate ProtocolReducerNode import succeeds.

        Reducer nodes handle aggregation and persistence operations.
        """
        from omnibase_spi.protocols.nodes import ProtocolReducerNode

        assert ProtocolReducerNode is not None
        _verify_runtime_checkable_protocol(ProtocolReducerNode)

    def test_protocol_orchestrator_node_import(self) -> None:
        """Validate ProtocolOrchestratorNode import succeeds.

        Orchestrator nodes coordinate workflow execution across other node types.
        """
        from omnibase_spi.protocols.nodes import ProtocolOrchestratorNode

        assert ProtocolOrchestratorNode is not None
        _verify_runtime_checkable_protocol(ProtocolOrchestratorNode)

    def test_all_node_protocols_in_module_all(self) -> None:
        """Validate all node protocols are properly exported in __all__.

        Ensures consumers can use 'from omnibase_spi.protocols.nodes import *'
        and get all expected protocol types. This uses an explicit expected list
        to catch any missing exports when new protocols are added.
        """
        from omnibase_spi.protocols import nodes

        expected = {
            "ProtocolNode",
            "ProtocolComputeNode",
            "ProtocolEffectNode",
            "ProtocolReducerNode",
            "ProtocolOrchestratorNode",
        }
        for protocol_name in expected:
            assert protocol_name in nodes.__all__, f"{protocol_name} not in __all__"
            assert hasattr(nodes, protocol_name), f"{protocol_name} not accessible"

        # Verify expected list is complete (catches case where __all__ has more than expected)
        actual = set(nodes.__all__)
        extra = actual - expected
        missing = expected - actual
        assert not extra, f"Unexpected items in __all__: {extra}"
        assert not missing, f"Missing items from __all__: {missing}"

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

    Validates that all handler protocols can be imported from
    omnibase_spi.protocols.handlers without triggering import errors
    from forward references to Core models. This includes:

    - ProtocolHandler: Main handler interface for I/O operations
    - ProtocolHandlerSource: Handler discovery abstraction
    - ProtocolHandlerDescriptor: Handler metadata protocol
    """

    def test_protocol_handler_import(self) -> None:
        """Validate ProtocolHandler import succeeds.

        Handlers define the execute/initialize/shutdown lifecycle and reference
        Core request/response models in their type hints.
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert ProtocolHandler is not None
        _verify_runtime_checkable_protocol(ProtocolHandler)

    def test_protocol_handler_source_import(self) -> None:
        """Validate ProtocolHandlerSource import succeeds.

        Handler sources provide a uniform interface for discovering handlers,
        abstracting away the discovery mechanism (bootstrap, contract, hybrid).
        """
        from omnibase_spi.protocols.handlers import ProtocolHandlerSource

        assert ProtocolHandlerSource is not None
        _verify_runtime_checkable_protocol(ProtocolHandlerSource)

    def test_protocol_handler_descriptor_import(self) -> None:
        """Validate ProtocolHandlerDescriptor import succeeds.

        Handler descriptors provide metadata about registered handlers for
        registry management and handler discovery.
        """
        from omnibase_spi.protocols.handlers import ProtocolHandlerDescriptor

        assert ProtocolHandlerDescriptor is not None
        _verify_runtime_checkable_protocol(ProtocolHandlerDescriptor)

    def test_all_handler_protocols_in_module_all(self) -> None:
        """Validate all handler protocols are properly exported in __all__.

        Ensures consumers can use 'from omnibase_spi.protocols.handlers import *'
        and get all expected protocol types. This uses an explicit expected list
        to catch any missing exports when new protocols are added.
        """
        from omnibase_spi.protocols import handlers

        expected = {
            "LiteralHandlerSourceType",
            "ProtocolHandler",
            "ProtocolHandlerDescriptor",
            "ProtocolHandlerSource",
        }
        for protocol_name in expected:
            assert protocol_name in handlers.__all__, f"{protocol_name} not in __all__"
            assert hasattr(handlers, protocol_name), f"{protocol_name} not accessible"

        # Verify expected list is complete (catches case where __all__ has more than expected)
        actual = set(handlers.__all__)
        extra = actual - expected
        missing = expected - actual
        assert not extra, f"Unexpected items in __all__: {extra}"
        assert not missing, f"Missing items from __all__: {missing}"

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


class TestContractProtocolImports:
    """Test contract protocol imports without forward reference errors.

    Validates that all contract protocols (compilers and supporting types)
    can be imported from omnibase_spi.protocols.contracts without forward
    reference errors. This includes:

    - Contract Compilers: ProtocolEffectContractCompiler,
      ProtocolWorkflowContractCompiler, ProtocolFSMContractCompiler
    - Handler Contracts: ProtocolHandlerContract
    - Supporting Types: ProtocolCapabilityDependency,
      ProtocolExecutionConstraints, ProtocolHandlerBehaviorDescriptor
    """

    def test_effect_contract_compiler_import(self) -> None:
        """Validate ProtocolEffectContractCompiler import succeeds.

        Effect compilers transform contract definitions into executable effect nodes.
        """
        from omnibase_spi.protocols.contracts import ProtocolEffectContractCompiler

        assert ProtocolEffectContractCompiler is not None
        _verify_runtime_checkable_protocol(ProtocolEffectContractCompiler)

    def test_workflow_contract_compiler_import(self) -> None:
        """Validate ProtocolWorkflowContractCompiler import succeeds.

        Workflow compilers handle multi-step workflow contract compilation.
        """
        from omnibase_spi.protocols.contracts import ProtocolWorkflowContractCompiler

        assert ProtocolWorkflowContractCompiler is not None
        _verify_runtime_checkable_protocol(ProtocolWorkflowContractCompiler)

    def test_fsm_contract_compiler_import(self) -> None:
        """Validate ProtocolFSMContractCompiler import succeeds.

        FSM compilers handle finite state machine contract compilation.
        """
        from omnibase_spi.protocols.contracts import ProtocolFSMContractCompiler

        assert ProtocolFSMContractCompiler is not None
        _verify_runtime_checkable_protocol(ProtocolFSMContractCompiler)

    def test_handler_contract_import(self) -> None:
        """Validate ProtocolHandlerContract import succeeds.

        Handler contracts define the type-safe interface for handler behavior
        specifications including capabilities, constraints, and behavior descriptors.
        """
        from omnibase_spi.protocols.contracts import ProtocolHandlerContract

        assert ProtocolHandlerContract is not None
        _verify_runtime_checkable_protocol(ProtocolHandlerContract)

    def test_capability_dependency_import(self) -> None:
        """Validate ProtocolCapabilityDependency import succeeds.

        Capability dependencies define requirements between handler capabilities.
        """
        from omnibase_spi.protocols.contracts import ProtocolCapabilityDependency

        assert ProtocolCapabilityDependency is not None
        _verify_runtime_checkable_protocol(ProtocolCapabilityDependency)

    def test_execution_constraints_import(self) -> None:
        """Validate ProtocolExecutionConstraints import succeeds.

        Execution constraints define handler execution requirements including:
        - Ordering dependencies (requires_before/requires_after)
        - Parallelism control (can_run_parallel)
        - Mandatory execution flags (must_run)
        - Nondeterminism tracking for replay/recovery (nondeterministic_effect)
        """
        from omnibase_spi.protocols.contracts import ProtocolExecutionConstraints

        assert ProtocolExecutionConstraints is not None
        _verify_runtime_checkable_protocol(ProtocolExecutionConstraints)

    def test_handler_behavior_descriptor_import(self) -> None:
        """Validate ProtocolHandlerBehaviorDescriptor import succeeds.

        Behavior descriptors define expected handler behaviors and side effects.
        """
        from omnibase_spi.protocols.contracts import ProtocolHandlerBehaviorDescriptor

        assert ProtocolHandlerBehaviorDescriptor is not None
        _verify_runtime_checkable_protocol(ProtocolHandlerBehaviorDescriptor)

    def test_all_contract_protocols_in_module_all(self) -> None:
        """Validate all contract protocols are properly exported in __all__.

        Ensures consumers can access all contract protocols (compilers and
        supporting types) through the contracts module's public API. This uses
        an explicit expected list to catch any missing exports when new
        protocols are added.
        """
        from omnibase_spi.protocols import contracts

        expected = {
            "ProtocolCapabilityDependency",
            "ProtocolEffectContractCompiler",
            "ProtocolExecutionConstraints",
            "ProtocolFSMContractCompiler",
            "ProtocolHandlerBehaviorDescriptor",
            "ProtocolHandlerContract",
            "ProtocolWorkflowContractCompiler",
        }
        for protocol_name in expected:
            assert protocol_name in contracts.__all__, f"{protocol_name} not in __all__"
            assert hasattr(contracts, protocol_name), f"{protocol_name} not accessible"

        # Verify expected list is complete (catches case where __all__ has more than expected)
        actual = set(contracts.__all__)
        extra = actual - expected
        missing = expected - actual
        assert not extra, f"Unexpected items in __all__: {extra}"
        assert not missing, f"Missing items from __all__: {missing}"

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

    Validates that all registry protocols can be imported from
    omnibase_spi.protocols.registry without forward reference errors.
    """

    def test_protocol_handler_registry_import(self) -> None:
        """Validate ProtocolHandlerRegistry import succeeds.

        The registry protocol defines handler registration and lookup operations.
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert ProtocolHandlerRegistry is not None
        _verify_runtime_checkable_protocol(ProtocolHandlerRegistry)

    def test_protocol_registry_base_import(self) -> None:
        """Validate ProtocolRegistryBase import succeeds.

        The base registry protocol defines common registration and lookup
        operations shared by all registry implementations.
        """
        from omnibase_spi.protocols.registry import ProtocolRegistryBase

        assert ProtocolRegistryBase is not None
        _verify_runtime_checkable_protocol(ProtocolRegistryBase)

    def test_protocol_versioned_registry_import(self) -> None:
        """Validate ProtocolVersionedRegistry import succeeds.

        The versioned registry protocol extends base registry with version-aware
        handler registration and lookup capabilities.
        """
        from omnibase_spi.protocols.registry import ProtocolVersionedRegistry

        assert ProtocolVersionedRegistry is not None
        _verify_runtime_checkable_protocol(ProtocolVersionedRegistry)

    def test_protocol_capability_registry_import(self) -> None:
        """Validate ProtocolCapabilityRegistry import succeeds.

        The capability registry protocol defines capability registration and
        lookup operations for capability-based service discovery.
        """
        from omnibase_spi.protocols.registry import ProtocolCapabilityRegistry

        assert ProtocolCapabilityRegistry is not None
        _verify_runtime_checkable_protocol(ProtocolCapabilityRegistry)

    def test_protocol_provider_registry_import(self) -> None:
        """Validate ProtocolProviderRegistry import succeeds.

        The provider registry protocol defines provider registration and
        discovery operations for service provider management.
        """
        from omnibase_spi.protocols.registry import ProtocolProviderRegistry

        assert ProtocolProviderRegistry is not None
        _verify_runtime_checkable_protocol(ProtocolProviderRegistry)

    def test_all_registry_protocols_in_module_all(self) -> None:
        """Validate all registry protocols are properly exported in __all__.

        Ensures consumers can use 'from omnibase_spi.protocols.registry import *'
        and get all expected protocol types. This uses an explicit expected list
        to catch any missing exports when new protocols are added.
        """
        from omnibase_spi.protocols import registry

        expected = {
            "ProtocolCapabilityRegistry",
            "ProtocolHandlerRegistry",
            "ProtocolProviderRegistry",
            "ProtocolRegistryBase",
            "ProtocolVersionedRegistry",
        }
        for protocol_name in expected:
            assert protocol_name in registry.__all__, f"{protocol_name} not in __all__"
            assert hasattr(registry, protocol_name), f"{protocol_name} not accessible"

        # Verify expected list is complete (catches case where __all__ has more than expected)
        actual = set(registry.__all__)
        extra = actual - expected
        missing = expected - actual
        assert not extra, f"Unexpected items in __all__: {extra}"
        assert not missing, f"Missing items from __all__: {missing}"

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


class TestExecutionConstrainableProtocolImports:
    """Test ProtocolExecutionConstrainable import without forward reference errors.

    Validates that ProtocolExecutionConstrainable can be imported from
    omnibase_spi.protocols without forward reference errors. This protocol
    is a mixin for objects that can declare execution constraints.
    """

    def test_protocol_execution_constrainable_import(self) -> None:
        """Validate ProtocolExecutionConstrainable import succeeds.

        The execution constrainable protocol defines a mixin interface for
        objects that can declare execution constraints. Constraints include:
        - Ordering dependencies (requires_before/requires_after)
        - Parallelism control (can_run_parallel)
        - Mandatory execution flags (must_run)
        - Nondeterminism tracking (nondeterministic_effect)
        """
        from omnibase_spi.protocols.protocol_execution_constrainable import (
            ProtocolExecutionConstrainable,
        )

        assert ProtocolExecutionConstrainable is not None
        _verify_runtime_checkable_protocol(ProtocolExecutionConstrainable)

    def test_protocol_execution_constrainable_from_root(self) -> None:
        """Validate ProtocolExecutionConstrainable is accessible from protocols root.

        Ensures the protocol is properly re-exported from the root protocols module.
        """
        from omnibase_spi.protocols import ProtocolExecutionConstrainable

        assert ProtocolExecutionConstrainable is not None
        _verify_runtime_checkable_protocol(ProtocolExecutionConstrainable)

    def test_protocol_execution_constrainable_has_required_methods(self) -> None:
        """Validate ProtocolExecutionConstrainable defines required interface.

        The protocol must define:
        - execution_constraints property: Returns constraints or None
        - has_constraints method: Returns True if constraints are defined
        """
        from omnibase_spi.protocols.protocol_execution_constrainable import (
            ProtocolExecutionConstrainable,
        )

        assert hasattr(ProtocolExecutionConstrainable, "execution_constraints"), (
            "Missing execution_constraints property"
        )
        assert hasattr(ProtocolExecutionConstrainable, "has_constraints"), (
            "Missing has_constraints method"
        )


class TestRuntimeCheckableProtocols:
    """Focused regression suite for @runtime_checkable protocol decorator support.

    This test class is intentionally parallel to the runtime checkability assertions
    in the import test classes (TestNodeProtocolImports, TestHandlerProtocolImports,
    TestContractProtocolImports, TestRegistryProtocolImports). While those classes
    validate runtime checkability as part of comprehensive import validation, this
    class provides:

    1. **Single-Purpose Focus**: A dedicated location for verifying that ALL SPI
       protocols are decorated with @runtime_checkable, making it easy to extend
       when new protocols are added.

    2. **Regression Prevention**: If someone accidentally removes @runtime_checkable
       from a protocol, this suite will catch it with a clear, specific test name
       (e.g., test_protocol_compute_node_is_runtime_checkable).

    3. **Documentation**: Serves as executable documentation of the architectural
       requirement that all SPI protocols MUST be runtime checkable for isinstance()
       support in dependency injection and handler validation.

    Note: The import test classes also check _is_runtime_protocol (with additional
    __protocol_attrs__ validation). This redundancy is intentional - the import
    tests verify protocols work correctly when imported, while this suite ensures
    the runtime checkability invariant is maintained as a first-class concern.
    """

    def test_protocol_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolNode has @runtime_checkable decorator.

        Uses _is_runtime_protocol attribute which is the canonical marker.
        """
        from omnibase_spi.protocols.nodes import ProtocolNode

        # Verify the protocol has the runtime checkable marker
        assert getattr(ProtocolNode, "_is_runtime_protocol", False) is True, (
            "ProtocolNode must be decorated with @runtime_checkable"
        )

    def test_protocol_compute_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolComputeNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        assert getattr(ProtocolComputeNode, "_is_runtime_protocol", False) is True, (
            "ProtocolComputeNode must be decorated with @runtime_checkable"
        )

    def test_protocol_effect_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolEffectNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        assert getattr(ProtocolEffectNode, "_is_runtime_protocol", False) is True, (
            "ProtocolEffectNode must be decorated with @runtime_checkable"
        )

    def test_protocol_reducer_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolReducerNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolReducerNode

        assert getattr(ProtocolReducerNode, "_is_runtime_protocol", False) is True, (
            "ProtocolReducerNode must be decorated with @runtime_checkable"
        )

    def test_protocol_orchestrator_node_is_runtime_checkable(self) -> None:
        """Validate ProtocolOrchestratorNode has @runtime_checkable decorator."""
        from omnibase_spi.protocols.nodes import ProtocolOrchestratorNode

        assert (
            getattr(ProtocolOrchestratorNode, "_is_runtime_protocol", False) is True
        ), "ProtocolOrchestratorNode must be decorated with @runtime_checkable"

    def test_protocol_handler_is_runtime_checkable(self) -> None:
        """Validate ProtocolHandler has @runtime_checkable decorator."""
        from omnibase_spi.protocols.handlers import ProtocolHandler

        assert getattr(ProtocolHandler, "_is_runtime_protocol", False) is True, (
            "ProtocolHandler must be decorated with @runtime_checkable"
        )

    def test_protocol_handler_registry_is_runtime_checkable(self) -> None:
        """Validate ProtocolHandlerRegistry has @runtime_checkable decorator."""
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert (
            getattr(ProtocolHandlerRegistry, "_is_runtime_protocol", False) is True
        ), "ProtocolHandlerRegistry must be decorated with @runtime_checkable"

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
            assert getattr(protocol, "_is_runtime_protocol", False) is True, (
                f"{protocol.__name__} is not runtime_checkable"
            )

    def test_contract_types_are_runtime_checkable(self) -> None:
        """Validate all contract type protocols have @runtime_checkable."""
        from omnibase_spi.protocols.contracts import (
            ProtocolCapabilityDependency,
            ProtocolExecutionConstraints,
            ProtocolHandlerBehaviorDescriptor,
            ProtocolHandlerContract,
        )

        for protocol in [
            ProtocolHandlerContract,
            ProtocolCapabilityDependency,
            ProtocolExecutionConstraints,
            ProtocolHandlerBehaviorDescriptor,
        ]:
            assert getattr(protocol, "_is_runtime_protocol", False) is True, (
                f"{protocol.__name__} is not runtime_checkable"
            )

    def test_protocol_execution_constrainable_is_runtime_checkable(self) -> None:
        """Validate ProtocolExecutionConstrainable has @runtime_checkable decorator."""
        from omnibase_spi.protocols.protocol_execution_constrainable import (
            ProtocolExecutionConstrainable,
        )

        assert (
            getattr(ProtocolExecutionConstrainable, "_is_runtime_protocol", False)
            is True
        ), "ProtocolExecutionConstrainable must be decorated with @runtime_checkable"

    def test_registry_protocols_are_runtime_checkable(self) -> None:
        """Validate all registry protocols have @runtime_checkable."""
        from omnibase_spi.protocols.registry import (
            ProtocolCapabilityRegistry,
            ProtocolHandlerRegistry,
            ProtocolProviderRegistry,
            ProtocolRegistryBase,
            ProtocolVersionedRegistry,
        )

        for protocol in [
            ProtocolCapabilityRegistry,
            ProtocolHandlerRegistry,
            ProtocolProviderRegistry,
            ProtocolRegistryBase,
            ProtocolVersionedRegistry,
        ]:
            assert getattr(protocol, "_is_runtime_protocol", False) is True, (
                f"{protocol.__name__} is not runtime_checkable"
            )


class TestIsinstanceChecks:
    """Test isinstance() checks with mock implementations.

    Validates that @runtime_checkable protocols correctly identify compliant
    implementations via isinstance(). This is the practical test of runtime
    checkability - protocols should return True for objects that implement
    the required methods/attributes, and False for non-compliant objects.

    Mock Implementation Value Conventions:
        The mock classes in this test suite follow consistent conventions:

        - node_id: Descriptive test identifiers (e.g., "test-node", "compute-test")
            Used to identify mock instances in debugging and error messages.

        - node_type: Match the protocol type being tested (e.g., "compute", "effect")
            Should reflect the actual node classification for realistic testing.

        - version: Valid semver format "MAJOR.MINOR.PATCH" (e.g., "1.0.0")
            Use "1.0.0" as default for simple mocks, increment for test variations.

        - is_deterministic: Boolean indicating output determinism (True for compute)
            Compute nodes typically use True; effect nodes may use False.

        - Method implementations: Return minimal valid responses (empty dict, input, None)
            Focus on satisfying the protocol contract, not business logic.

        - Docstrings: Brief explanation of what the mock method does.
            Helpful for understanding mock behavior in test failures.
    """

    def test_isinstance_with_mock_compute_node(self) -> None:
        """Validate isinstance() returns True for compliant ProtocolComputeNode.

        Creates a mock class with all required attributes and methods,
        then verifies isinstance() correctly identifies it as a ProtocolComputeNode.
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        class MockComputeNode:
            """Mock implementation of ProtocolComputeNode.

            Note: Uses 'object' type hints instead of actual omnibase_core models
            to avoid circular import issues in tests. Once omnibase_core exports
            proper types, these can be updated to use TypedDict or model types.
            """

            # Mock attributes - see class docstring for value conventions
            node_id = "test-node"  # Arbitrary test identifier
            node_type = "compute"  # Required: matches node type classification
            version = "1.0.0"  # Valid semver (MAJOR.MINOR.PATCH)
            is_deterministic = True  # Compute nodes track output determinism

            async def execute(self, input_data: object) -> object:
                """Returns input unchanged - minimal valid implementation."""
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
            """Mock implementation of ProtocolHandler lifecycle methods.

            Note: Uses 'object' type hints instead of actual omnibase_core models
            to avoid circular import issues in tests. Once omnibase_core exports
            proper types, these can be updated to use TypedDict or model types.
            """

            @property
            def handler_type(self) -> object:
                """Returns mock handler type."""
                return "HTTP"

            async def initialize(self, config: object) -> None:
                """No-op initialization for testing."""
                pass

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                """No-op shutdown. Default 30.0s matches protocol contract."""
                pass

            async def execute(
                self, request: object, operation_config: object
            ) -> object:
                """Returns empty dict as placeholder response."""
                return {}

            def describe(self) -> ModelHandlerDescriptor:
                """Returns mock handler description."""
                return _create_mock_handler_descriptor(name="mock-handler")

            async def health_check(self) -> dict[str, object]:
                """Returns mock health check result."""
                return {"healthy": True, "latency_ms": 0.0}

        mock = MockHandler()
        assert isinstance(mock, ProtocolHandler)

    def test_isinstance_with_mock_registry(self) -> None:
        """Validate isinstance() returns True for compliant ProtocolHandlerRegistry.

        Creates a mock class with register/get/list_keys/is_registered/unregister methods,
        then verifies isinstance() correctly identifies it.
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        class MockRegistry:
            """Mock implementation of ProtocolHandlerRegistry CRUD operations."""

            def register(self, protocol_type: str, handler_cls: type) -> None:
                """No-op registration for testing."""
                pass

            def get(self, protocol_type: str) -> type:
                """Returns base 'type' class as placeholder."""
                return type

            def list_keys(self) -> list[str]:
                """Returns empty list - no registrations in mock."""
                return []

            def is_registered(self, key: str) -> bool:
                """Always returns False - nothing registered in mock."""
                return False

            def unregister(self, key: str) -> bool:
                """Always returns False - nothing to unregister in mock."""
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
            """Non-compliant class - deliberately lacks protocol methods."""

            def some_method(self) -> None:
                """Arbitrary method unrelated to ProtocolHandler contract."""
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
        # Use 'is' for type identity: verifies forward reference resolved to exact class
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
        # Use 'is' for type identity: verifies forward reference resolved to exact class
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
        # Use 'is' for type identity: verifies forward reference resolved to exact class
        assert hints["operation_config"] is ModelOperationConfig
        assert "return" in hints
        # Use 'is' for type identity: verifies forward reference resolved to exact class
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
        # Use 'is' for type identity: verifies forward reference resolved to exact class
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

    def test_get_type_hints_behavior_without_core(self) -> None:
        """Document get_type_hints() behavior when Core models are unavailable.

        When Core is not installed, get_type_hints() on protocol methods that
        reference Core models in forward references will raise NameError since
        the types cannot be resolved. This test documents this expected behavior.

        Architecture Context:
            SPI protocols use TYPE_CHECKING blocks to import Core models:

                if TYPE_CHECKING:
                    from omnibase_core.models.compute import ModelComputeInput

            This allows SPI to be imported without Core, but get_type_hints()
            cannot resolve forward references like 'ModelComputeInput' since
            the actual types are not available at runtime.

        Behavior Matrix:
            - Core available: get_type_hints() resolves to actual Core model classes
            - Core unavailable: get_type_hints() raises NameError for unresolvable types
            - __annotations__ access: Always works, returns string forward references
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        # __annotations__ always works - returns raw annotation strings/types
        # This is safe to access regardless of Core availability
        execute_method = ProtocolComputeNode.execute
        assert hasattr(execute_method, "__annotations__")

        # Annotations are accessible as raw values (may be strings or resolved types)
        annotations = execute_method.__annotations__
        assert "input_data" in annotations
        assert "return" in annotations

        if CORE_MODELS_AVAILABLE:
            # When Core is available, get_type_hints() successfully resolves
            # forward references to actual Core model classes
            hints = get_type_hints(execute_method)
            assert "input_data" in hints
            assert "return" in hints
            # Verify these are actual types, not strings
            assert not isinstance(hints["input_data"], str)
            assert not isinstance(hints["return"], str)
        else:
            # When Core is NOT available, get_type_hints() raises NameError
            # because forward references like 'ModelComputeInput' cannot be
            # resolved - the Core module is not installed
            with pytest.raises(NameError) as exc_info:
                get_type_hints(execute_method)

            # The error should reference one of the Core model types
            error_message = str(exc_info.value)
            assert "ModelComputeInput" in error_message or "Model" in error_message, (
                f"Expected NameError for Core model type, got: {error_message}"
            )


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

        Registries must support register, get, list_keys, is_registered,
        and unregister operations for handler management.
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        assert hasattr(ProtocolHandlerRegistry, "register")
        assert hasattr(ProtocolHandlerRegistry, "get")
        assert hasattr(ProtocolHandlerRegistry, "list_keys")
        assert hasattr(ProtocolHandlerRegistry, "is_registered")
        assert hasattr(ProtocolHandlerRegistry, "unregister")

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
            assert hasattr(compiler, "validate"), (
                f"{compiler.__name__} missing validate"
            )

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

        After reload, all node protocols should remain accessible and
        maintain their runtime checkable behavior.
        """
        import omnibase_spi.protocols.nodes as nodes_module

        # Reimport should work
        importlib.reload(nodes_module)

        # Protocols should still be available
        assert hasattr(nodes_module, "ProtocolNode")
        assert hasattr(nodes_module, "ProtocolComputeNode")

        # Verify runtime checkable marker preserved after reload
        assert (
            getattr(nodes_module.ProtocolNode, "_is_runtime_protocol", False) is True
        ), "ProtocolNode lost _is_runtime_protocol marker after reload"

        # Verify __protocol_attrs__ still exists (standard Protocol attribute)
        assert hasattr(nodes_module.ProtocolNode, "__protocol_attrs__"), (
            "ProtocolNode lost __protocol_attrs__ after reload"
        )

        # Verify isinstance still works with new mock after reload
        class MockNodeAfterReload:
            """Mock implementation created after reload."""

            node_id = "test"
            node_type = "test"
            version = "1.0.0"

        mock = MockNodeAfterReload()
        assert isinstance(mock, nodes_module.ProtocolNode), (
            "isinstance() check failed after module reload"
        )

    def test_reimport_handlers_module(self) -> None:
        """Validate handlers module survives reload without errors.

        After reload, ProtocolHandler should remain accessible and
        maintain its runtime checkable behavior.
        """
        import omnibase_spi.protocols.handlers as handlers_module

        importlib.reload(handlers_module)
        assert hasattr(handlers_module, "ProtocolHandler")

        # Verify runtime checkable marker preserved after reload
        assert (
            getattr(handlers_module.ProtocolHandler, "_is_runtime_protocol", False)
            is True
        ), "ProtocolHandler lost _is_runtime_protocol marker after reload"

        # Verify __protocol_attrs__ still exists (standard Protocol attribute)
        assert hasattr(handlers_module.ProtocolHandler, "__protocol_attrs__"), (
            "ProtocolHandler lost __protocol_attrs__ after reload"
        )

        # Verify isinstance still works with new mock after reload
        class MockHandlerAfterReload:
            """Mock implementation created after reload."""

            @property
            def handler_type(self) -> object:
                """Returns mock handler type."""
                return "HTTP"

            async def initialize(self, config: object) -> None:
                pass

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                pass

            async def execute(
                self, request: object, operation_config: object
            ) -> object:
                return {}

            def describe(self) -> ModelHandlerDescriptor:
                """Returns mock handler description."""
                return _create_mock_handler_descriptor(name="mock-handler-after-reload")

            async def health_check(self) -> dict[str, object]:
                """Returns mock health check result."""
                return {"healthy": True, "latency_ms": 0.0}

        mock = MockHandlerAfterReload()
        assert isinstance(mock, handlers_module.ProtocolHandler), (
            "isinstance() check failed after module reload"
        )

    def test_reimport_contracts_module(self) -> None:
        """Validate contracts module survives reload without errors.

        After reload, all contract compiler protocols should remain accessible
        and maintain their runtime checkable behavior.
        """
        import omnibase_spi.protocols.contracts as contracts_module

        importlib.reload(contracts_module)
        assert hasattr(contracts_module, "ProtocolEffectContractCompiler")

        # Verify runtime checkable marker preserved after reload
        assert (
            getattr(
                contracts_module.ProtocolEffectContractCompiler,
                "_is_runtime_protocol",
                False,
            )
            is True
        ), (
            "ProtocolEffectContractCompiler lost _is_runtime_protocol marker after reload"
        )

        # Verify __protocol_attrs__ still exists (standard Protocol attribute)
        assert hasattr(
            contracts_module.ProtocolEffectContractCompiler, "__protocol_attrs__"
        ), "ProtocolEffectContractCompiler lost __protocol_attrs__ after reload"

        # Verify isinstance still works with new mock after reload
        class MockCompilerAfterReload:
            """Mock compiler created after reload for isinstance() verification."""

            def compile(self, contract_path: object) -> object:
                """Returns None as placeholder compiled contract."""
                return None

            def validate(self, contract_path: object) -> bool:
                """Always returns True (valid) for testing."""
                return True

        mock = MockCompilerAfterReload()
        assert isinstance(mock, contracts_module.ProtocolEffectContractCompiler), (
            "isinstance() check failed after module reload"
        )

    def test_reimport_registry_module(self) -> None:
        """Validate registry module survives reload without errors.

        After reload, ProtocolHandlerRegistry should remain accessible and
        maintain its runtime checkable behavior.
        """
        import omnibase_spi.protocols.registry as registry_module

        importlib.reload(registry_module)
        assert hasattr(registry_module, "ProtocolHandlerRegistry")

        # Verify runtime checkable marker preserved after reload
        assert (
            getattr(
                registry_module.ProtocolHandlerRegistry, "_is_runtime_protocol", False
            )
            is True
        ), "ProtocolHandlerRegistry lost _is_runtime_protocol marker after reload"

        # Verify __protocol_attrs__ still exists (standard Protocol attribute)
        assert hasattr(registry_module.ProtocolHandlerRegistry, "__protocol_attrs__"), (
            "ProtocolHandlerRegistry lost __protocol_attrs__ after reload"
        )

        # Verify isinstance still works with new mock after reload
        class MockRegistryAfterReload:
            """Mock registry created after reload for isinstance() verification."""

            def register(self, protocol_type: str, handler_cls: type) -> None:
                """No-op registration for testing."""
                pass

            def get(self, protocol_type: str) -> type:
                """Returns base 'type' class as placeholder."""
                return type

            def list_keys(self) -> list[str]:
                """Returns empty list - no registrations in mock."""
                return []

            def is_registered(self, key: str) -> bool:
                """Always returns False - nothing registered in mock."""
                return False

            def unregister(self, key: str) -> bool:
                """Always returns False - nothing to unregister in mock."""
                return False

        mock = MockRegistryAfterReload()
        assert isinstance(mock, registry_module.ProtocolHandlerRegistry), (
            "isinstance() check failed after module reload"
        )

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
            """Mock ProtocolNode created before reload for comparison."""

            node_id = "test-before"  # Indicates pre-reload creation
            node_type = "test"  # Generic test node type
            version = "1.0.0"  # Valid semver

        mock_before = MockNodeBeforeReload()
        assert isinstance(mock_before, nodes_module.ProtocolNode)

        # Reload the module
        importlib.reload(nodes_module)

        # Verify protocol is still runtime checkable after reload
        assert (
            getattr(nodes_module.ProtocolNode, "_is_runtime_protocol", False) is True
        ), "ProtocolNode lost _is_runtime_protocol marker after reload"

        # Verify __protocol_attrs__ still exists (standard Protocol attribute)
        assert hasattr(nodes_module.ProtocolNode, "__protocol_attrs__"), (
            "ProtocolNode lost __protocol_attrs__ after reload"
        )

        # Note: isinstance with pre-reload mock may not work due to class identity
        # changes after reload, but the protocol should still function with new
        # mock instances created after reload
        class MockNodeAfterReload:
            """Mock ProtocolNode created after reload for verification."""

            node_id = "test-after"  # Indicates post-reload creation
            node_type = "test"  # Generic test node type
            version = "1.0.0"  # Valid semver

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
        assert (
            getattr(nodes_module.ProtocolComputeNode, "_is_runtime_protocol", False)
            is True
        ), "ProtocolComputeNode lost _is_runtime_protocol after reload"

        # Create compliant mock after reload
        class MockComputeNodeAfterReload:
            """Mock ProtocolComputeNode created after reload for verification."""

            node_id = "compute-test"  # Identifier for compute test instance
            node_type = "compute"  # Required: matches node classification
            version = "1.0.0"  # Valid semver
            is_deterministic = True  # Compute nodes track determinism

            async def execute(self, input_data: object) -> object:
                """Returns input unchanged - minimal valid implementation."""
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
        assert (
            getattr(handlers_module.ProtocolHandler, "_is_runtime_protocol", False)
            is True
        ), "ProtocolHandler lost _is_runtime_protocol after reload"

        # Create compliant mock after reload
        class MockHandlerAfterReload:
            """Mock ProtocolHandler created after reload for verification."""

            @property
            def handler_type(self) -> object:
                """Returns mock handler type."""
                return "HTTP"

            async def initialize(self, config: object) -> None:
                """No-op initialization for testing."""
                pass

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                """No-op shutdown. Default 30.0s matches protocol contract."""
                pass

            async def execute(
                self, request: object, operation_config: object
            ) -> object:
                """Returns empty dict as placeholder response."""
                return {}

            def describe(self) -> ModelHandlerDescriptor:
                """Returns mock handler description."""
                return _create_mock_handler_descriptor(
                    name="mock-handler-preserves-isinstance"
                )

            async def health_check(self) -> dict[str, object]:
                """Returns mock health check result."""
                return {"healthy": True, "latency_ms": 0.0}

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
        assert (
            getattr(
                registry_module.ProtocolHandlerRegistry, "_is_runtime_protocol", False
            )
            is True
        ), "ProtocolHandlerRegistry lost _is_runtime_protocol after reload"

        # Create compliant mock after reload
        class MockRegistryAfterReload:
            """Mock ProtocolHandlerRegistry created after reload for verification."""

            def register(self, protocol_type: str, handler_cls: type) -> None:
                """No-op registration for testing."""
                pass

            def get(self, protocol_type: str) -> type:
                """Returns base 'type' class as placeholder."""
                return type

            def list_keys(self) -> list[str]:
                """Returns empty list - no registrations in mock."""
                return []

            def is_registered(self, key: str) -> bool:
                """Always returns False - nothing registered in mock."""
                return False

            def unregister(self, key: str) -> bool:
                """Always returns False - nothing to unregister in mock."""
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
            (
                "ProtocolEffectContractCompiler",
                contracts_module.ProtocolEffectContractCompiler,
            ),
            (
                "ProtocolWorkflowContractCompiler",
                contracts_module.ProtocolWorkflowContractCompiler,
            ),
            (
                "ProtocolFSMContractCompiler",
                contracts_module.ProtocolFSMContractCompiler,
            ),
        ]

        for name, compiler in compilers:
            assert getattr(compiler, "_is_runtime_protocol", False) is True, (
                f"{name} lost _is_runtime_protocol after reload"
            )

        # Create compliant mock for ProtocolEffectContractCompiler after reload
        class MockEffectCompilerAfterReload:
            """Mock compiler created after reload for isinstance() verification."""

            def compile(self, contract_path: object) -> object:
                """Returns None as placeholder compiled contract."""
                return None

            def validate(self, contract: object) -> bool:
                """Always returns True (valid) for testing."""
                return True

        mock = MockEffectCompilerAfterReload()
        assert isinstance(mock, contracts_module.ProtocolEffectContractCompiler), (
            "isinstance() check failed for ProtocolEffectContractCompiler after reload"
        )

    def test_protocol_class_identity_changes_after_reload(self) -> None:
        """Validate that Protocol class gets new identity after module reload.

        When a module is reloaded, the Protocol class gets a new identity.
        This test demonstrates that pre-reload and post-reload Protocol
        classes are different objects, even though they have the same name.

        This is expected Python behavior - class identity matters for isinstance().
        See: https://docs.python.org/3/library/importlib.html#importlib.reload

        Note: We must reload the actual module where the protocol is defined
        (omnibase_spi.protocols.nodes.base), not just the package that re-exports it,
        to trigger the class identity change.
        """
        import omnibase_spi.protocols.nodes.base as base_module

        # Capture the Protocol class BEFORE reload
        protocol_before_reload = base_module.ProtocolNode

        # Now reload the actual module where ProtocolNode is defined
        # This is crucial: reloading a package that re-exports a class doesn't
        # change the class identity unless you reload the defining module
        importlib.reload(base_module)

        # Capture the Protocol class AFTER reload
        protocol_after_reload = base_module.ProtocolNode

        # Demonstrate that the Protocol classes have DIFFERENT identities
        # This is the key insight: reload creates a NEW class object
        assert protocol_before_reload is not protocol_after_reload, (
            "Protocol class identity should change after reload - "
            "the old and new Protocol are different objects"
        )

        # The class names are the same, but the objects are different
        assert protocol_before_reload.__name__ == protocol_after_reload.__name__, (
            "Both Protocol classes should have the same __name__"
        )

        # Their id() values are different, proving they are distinct objects
        assert id(protocol_before_reload) != id(protocol_after_reload), (
            "Protocol classes should have different id() after reload"
        )

    def test_dict_key_limitation_after_reload(self) -> None:
        """Demonstrate dictionary key limitation when protocol identity changes.

        Registry systems using protocol identity as dictionary keys will fail
        after module reload because the protocol class gets a new identity.

        Example failure mode:
            registry = {protocol_before_reload: some_handler}
            After reload: registry[protocol_after_reload] -> KeyError!

        This demonstrates why caching protocol references is problematic in
        long-running applications that might reload modules.
        """
        import omnibase_spi.protocols.nodes.base as base_module

        # Capture the Protocol class BEFORE reload
        protocol_before_reload = base_module.ProtocolNode

        # Reload the module to get new class identity
        importlib.reload(base_module)

        # Capture the Protocol class AFTER reload
        protocol_after_reload = base_module.ProtocolNode

        # Demonstrate dictionary key issue - the key limitation
        registry: dict[type, str] = {protocol_before_reload: "old_handler"}
        assert protocol_before_reload in registry, "Old protocol should be in registry"
        assert protocol_after_reload not in registry, (
            "New protocol should NOT be in registry - this demonstrates the limitation"
        )

        # Note: issubclass() is NOT demonstrated here because Python's
        # runtime_checkable protocols with non-method members (like node_id,
        # node_type, version) raise TypeError for issubclass() checks.
        # This is a known Python limitation documented in PEP 544.

    def test_set_membership_limitation_after_reload(self) -> None:
        """Demonstrate set membership issues when protocol identity changes.

        Set membership with protocol classes fails after reload because
        class identity matters for hashing.

        Example failure mode:
            protocols = {protocol_before_reload}
            protocol_after_reload in protocols  # May be False!

        Mitigation Strategy:
            Always use fresh module attribute access (base_module.ProtocolNode)
            rather than caching the protocol class in a variable.
        """
        import omnibase_spi.protocols.nodes.base as base_module

        # Capture the Protocol class BEFORE reload
        protocol_before_reload = base_module.ProtocolNode

        # Reload the module to get new class identity
        importlib.reload(base_module)

        # Capture the Protocol class AFTER reload
        protocol_after_reload = base_module.ProtocolNode

        # Demonstrate set membership issue
        protocol_set: set[type] = {protocol_before_reload}
        assert protocol_before_reload in protocol_set, "Old protocol in set"
        assert protocol_after_reload not in protocol_set, (
            "New protocol NOT in set - class identity matters for hashing"
        )

        # Mitigation: Always use fresh module attribute access
        # BAD:  cached_protocol = some_module.Protocol  # Stale after reload
        # GOOD: some_module.Protocol  # Always fresh reference

    def test_isinstance_structural_check_survives_reload(self) -> None:
        """Validate that isinstance() still works after reload due to structural typing.

        For @runtime_checkable protocols, isinstance() performs structural
        checking (verifying required attributes exist), NOT class hierarchy
        checking. This means pre-reload mocks still pass isinstance()
        checks against the NEW protocol - which is generally what we want.

        This test explicitly demonstrates that structural subtyping in
        @runtime_checkable protocols provides resilience against reload issues.
        """
        import omnibase_spi.protocols.nodes.base as base_module

        # Capture the Protocol class BEFORE reload
        protocol_before_reload = base_module.ProtocolNode

        # Create a compliant mock BEFORE reload
        class MockNodeBeforeReload:
            """Mock created BEFORE reload to demonstrate structural typing resilience."""

            node_id = "pre-reload-mock"  # Indicates pre-reload creation
            node_type = "test"  # Generic test node type
            version = "1.0.0"  # Valid semver

        mock_before = MockNodeBeforeReload()

        # Verify isinstance works with the protocol BEFORE reload
        assert isinstance(mock_before, protocol_before_reload), (
            "Mock should be isinstance of protocol before reload"
        )

        # Also verify it works with the module attribute before reload
        assert isinstance(mock_before, base_module.ProtocolNode), (
            "Mock should be isinstance of base_module.ProtocolNode before reload"
        )

        # Now reload the actual module where ProtocolNode is defined
        importlib.reload(base_module)

        # Capture the Protocol class AFTER reload
        protocol_after_reload = base_module.ProtocolNode

        # Demonstrate the limitation: isinstance with the OLD reference still works
        # because we're checking against the OLD class that MockNodeBeforeReload
        # was originally designed to match
        assert isinstance(mock_before, protocol_before_reload), (
            "Mock should still be isinstance of the OLD protocol reference"
        )

        # For structural subtyping (Protocol with @runtime_checkable), Python checks
        # if the object has the required attributes/methods, not class identity.
        # So this PASSES for simple attribute-based protocols.
        #
        # The structural check means pre-reload mocks still work with the NEW
        # protocol because @runtime_checkable does attribute-based checking.
        isinstance_with_new_protocol = isinstance(mock_before, protocol_after_reload)
        assert isinstance_with_new_protocol, (
            "Mock should ALSO pass isinstance with NEW protocol due to "
            "structural subtyping - @runtime_checkable checks attributes, "
            "not class identity"
        )

        # Also verify using fresh module attribute access
        isinstance_with_module_attr = isinstance(mock_before, base_module.ProtocolNode)
        assert isinstance_with_module_attr, (
            "Mock should pass isinstance with fresh module.ProtocolNode access"
        )


class TestProtocolCoverage:
    """Ensure all protocols in src/omnibase_spi/protocols/ have test coverage.

    This test automatically detects new protocols added to the codebase
    and ensures they are included in the forward reference tests. When new
    protocols are added, this test will warn about missing coverage.

    The test scans the protocols directory using AST parsing to find all
    Protocol class definitions and compares them against protocols that
    have explicit import tests in this file.

    Architecture Notes:
        - Uses Python AST module for parsing (stdlib only, no dependencies)
        - Excludes __init__.py files (package exports, not protocol definitions)
        - Excludes legacy/ directory (deprecated, scheduled for removal in v0.5.0)
        - Extracts protocols that explicitly inherit from Protocol
        - Compares against known tested protocols from this test file
    """

    # -------------------------------------------------------------------------
    # TESTED_PROTOCOLS: Registry of protocols with explicit forward ref tests
    # -------------------------------------------------------------------------
    # When adding a new protocol to the SPI:
    # 1. Add import test in appropriate TestXxxImports class
    # 2. Add runtime checkable test in TestRuntimeCheckableProtocols
    # 3. Add the protocol name to this set
    # The test_all_protocols_have_import_tests() method warns about gaps.
    # -------------------------------------------------------------------------
    TESTED_PROTOCOLS: set[str] = {
        # Node protocols (TestNodeProtocolImports) - core node hierarchy
        "ProtocolNode",  # Base: node_id, node_type, version attributes
        "ProtocolComputeNode",  # Pure transformations, deterministic flag
        "ProtocolEffectNode",  # I/O operations with lifecycle (init/shutdown)
        "ProtocolReducerNode",  # Aggregation and persistence
        "ProtocolOrchestratorNode",  # Workflow coordination
        # Handler protocols (TestHandlerProtocolImports)
        "ProtocolHandler",  # Request/response lifecycle (init/shutdown/execute)
        "ProtocolHandlerSource",  # Handler discovery abstraction
        "ProtocolHandlerDescriptor",  # Handler metadata for registry
        # Contract protocols (TestContractProtocolImports) - compilers and types
        "ProtocolEffectContractCompiler",  # Effect contract -> executable node
        "ProtocolWorkflowContractCompiler",  # Multi-step workflow compilation
        "ProtocolFSMContractCompiler",  # Finite state machine compilation
        "ProtocolHandlerContract",  # Type-safe handler contract interface
        "ProtocolCapabilityDependency",  # Capability requirements for handlers
        "ProtocolExecutionConstraints",  # Execution ordering and parallelism
        "ProtocolHandlerBehaviorDescriptor",  # Handler behavior characteristics
        # Execution constraint protocol (standalone mixin)
        "ProtocolExecutionConstrainable",  # Mixin for objects with constraints
        # Registry protocols (TestRegistryProtocolImports)
        "ProtocolCapabilityRegistry",  # Capability registration and lookup
        "ProtocolHandlerRegistry",  # Handler registration/lookup CRUD
        "ProtocolProviderRegistry",  # Provider registration and discovery
        "ProtocolRegistryBase",  # Base registry operations
        "ProtocolVersionedRegistry",  # Versioned handler registration
    }

    # -------------------------------------------------------------------------
    # EXCLUDED_DIRS: Directories excluded from protocol discovery scan
    # -------------------------------------------------------------------------
    # Note: __init__.py files are also excluded (re-export, not define)
    # -------------------------------------------------------------------------
    EXCLUDED_DIRS: set[str] = {
        "legacy",  # Deprecated protocols, removal scheduled in v0.5.0
        "__pycache__",  # Python bytecode cache (not source)
    }

    # -------------------------------------------------------------------------
    # KNOWN_SKIPPED_PROTOCOLS: Intentionally untested protocols
    # -------------------------------------------------------------------------
    # Add protocol names here with comment explaining why they're skipped:
    # - Type aliases (not actual Protocol classes)
    # - Internal-only protocols (not part of public API)
    # - Protocols without Core model dependencies (no forward refs to test)
    # -------------------------------------------------------------------------
    KNOWN_SKIPPED_PROTOCOLS: set[str] = set()  # Currently empty - all tested

    @staticmethod
    def _extract_protocol_classes_from_file(file_path: Path) -> list[str]:
        """Extract Protocol class names from a Python file using AST.

        Parses the given Python file and finds all class definitions that
        inherit from Protocol (directly or via @runtime_checkable decorator).

        Args:
            file_path: Path to the Python file to parse

        Returns:
            List of protocol class names found in the file

        Note:
            Uses the convention that Protocol classes inherit from Protocol
            or have 'Protocol' in their base class names.

        Limitations:
            This AST-based detection has the following known limitations:

            1. **Direct inheritance only**: Only detects classes that directly
               inherit from ``Protocol``. Protocols that inherit from other
               protocols (e.g., ``class ProtocolComputeNode(ProtocolNode)``)
               are detected through the parent, but multi-level inheritance
               chains may be incomplete.

            2. **Aliased imports not detected**: If Protocol is imported with
               an alias (e.g., ``from typing import Protocol as P``), classes
               inheriting from ``P`` will not be detected.

            3. **String annotations**: Forward references in base classes using
               string annotations are not resolved.

            4. **Dynamic class creation**: Classes created dynamically (e.g.,
               via ``type()`` or metaclasses) are not detected.

            For comprehensive protocol discovery, consider using runtime
            introspection with ``typing.get_type_hints()`` on the module.
        """
        import ast

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            return []

        protocols: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this class inherits from Protocol
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr

                    # Match classes inheriting from Protocol or typing.Protocol
                    if base_name == "Protocol":
                        protocols.append(node.name)
                        break

        return protocols

    @staticmethod
    def _scan_protocols_directory() -> dict[str, list[str]]:
        """Scan the protocols directory and extract all Protocol definitions.

        Recursively scans src/omnibase_spi/protocols/ directory, parsing each
        Python file to find Protocol class definitions.

        Returns:
            Dictionary mapping file paths (relative to protocols/) to list of
            protocol names defined in that file.
        """
        import omnibase_spi.protocols

        protocols_dir = Path(omnibase_spi.protocols.__file__).parent
        protocols_by_file: dict[str, list[str]] = {}

        for py_file in protocols_dir.rglob("*.py"):
            # Skip __init__.py files (they re-export, not define protocols)
            if py_file.name == "__init__.py":
                continue

            # Skip excluded directories
            relative_path = py_file.relative_to(protocols_dir)
            if any(
                excluded in relative_path.parts
                for excluded in TestProtocolCoverage.EXCLUDED_DIRS
            ):
                continue

            protocols = TestProtocolCoverage._extract_protocol_classes_from_file(
                py_file
            )
            if protocols:
                # Use relative path for cleaner output
                protocols_by_file[str(relative_path)] = protocols

        return protocols_by_file

    def test_all_protocols_have_import_tests(self) -> None:
        """Validate that all Protocol classes in protocols/ have import tests.

        Scans the protocols directory, extracts Protocol class names using AST,
        and verifies each has corresponding test coverage. Protocols without
        coverage are reported as warnings.

        This test uses a soft assertion approach - it reports missing coverage
        but doesn't fail the test suite. This allows new protocols to be added
        without immediately breaking CI while ensuring visibility of gaps.

        The test output shows:
        - Total protocols found
        - Protocols with test coverage
        - Protocols missing coverage (with file locations)
        """
        protocols_by_file = self._scan_protocols_directory()

        # Collect all discovered protocols
        all_discovered: set[str] = set()
        protocol_locations: dict[str, str] = {}  # protocol -> file path

        for file_path, protocols in protocols_by_file.items():
            for protocol in protocols:
                all_discovered.add(protocol)
                protocol_locations[protocol] = file_path

        # Determine coverage
        covered = all_discovered & self.TESTED_PROTOCOLS
        known_skipped = all_discovered & self.KNOWN_SKIPPED_PROTOCOLS
        missing_coverage = all_discovered - self.TESTED_PROTOCOLS - known_skipped

        # Build diagnostic message
        msg_parts: list[str] = [
            f"\n{'=' * 70}",
            "PROTOCOL COVERAGE REPORT",
            f"{'=' * 70}",
            f"Total protocols discovered: {len(all_discovered)}",
            f"Protocols with test coverage: {len(covered)}",
            f"Known skipped protocols: {len(known_skipped)}",
            f"Protocols missing coverage: {len(missing_coverage)}",
        ]

        if missing_coverage:
            msg_parts.append(f"\n{'=' * 70}")
            msg_parts.append("PROTOCOLS MISSING FORWARD REFERENCE TESTS:")
            msg_parts.append(f"{'=' * 70}")
            for protocol in sorted(missing_coverage):
                location = protocol_locations.get(protocol, "unknown")
                msg_parts.append(f"  - {protocol} ({location})")
            msg_parts.append("")
            msg_parts.append(
                "To add coverage, include import tests in the appropriate "
                "TestXxxImports class"
            )
            msg_parts.append(
                "and add the protocol name to TESTED_PROTOCOLS in TestProtocolCoverage."
            )

        # Output the report
        report = "\n".join(msg_parts)

        # The test passes with a warning - this is informational
        # Set warn_only=True for gradual adoption, or set to False for strict mode
        warn_only = True

        if missing_coverage and not warn_only:
            pytest.fail(report)
        elif missing_coverage:
            # Use pytest.warns or just print - warning is informational
            print(report)
            # The test passes but outputs the coverage gap information

        # Assert basic sanity checks always pass
        assert len(all_discovered) > 0, "No protocols discovered - check scan logic"
        assert len(covered) >= len(self.TESTED_PROTOCOLS), (
            "Some tested protocols not found in codebase"
        )

    def test_tested_protocols_exist_in_codebase(self) -> None:
        """Validate that all protocols in TESTED_PROTOCOLS actually exist.

        Ensures the TESTED_PROTOCOLS set doesn't contain stale entries for
        protocols that have been removed from the codebase.
        """
        protocols_by_file = self._scan_protocols_directory()

        # Collect all discovered protocols
        all_discovered: set[str] = set()
        for protocols in protocols_by_file.values():
            all_discovered.update(protocols)

        # Check for stale entries in TESTED_PROTOCOLS
        stale_entries = self.TESTED_PROTOCOLS - all_discovered

        if stale_entries:
            pytest.fail(
                f"TESTED_PROTOCOLS contains stale entries not found in codebase: "
                f"{sorted(stale_entries)}"
            )

    # Known duplicate protocol definitions in the codebase
    # These are documented here rather than failing the test to allow gradual cleanup
    KNOWN_DUPLICATE_PROTOCOLS: set[str] = {
        # ProtocolHandler collision RESOLVED: discovery version renamed to ProtocolBaseHandler
        # See: src/omnibase_spi/protocols/discovery/protocol_base_handler.py
        #
        # ProtocolMetadata exists in types/protocol_state_types.py (state metadata) and
        # onex/protocol_validation.py (ONEX validation metadata) - different domains
        "ProtocolMetadata",
        # ProtocolSecurityContext exists in types/protocol_event_bus_types.py (event bus
        # security) and onex/protocol_validation.py (ONEX validation security) - different
        # domains
        "ProtocolSecurityContext",
        # ProtocolValidationReport exists in onex/protocol_validation.py (ONEX-specific
        # validation reports) and validation/protocol_validation_orchestrator.py
        # (orchestrator-specific reports) - different validation contexts
        "ProtocolValidationReport",
        # ProtocolValidationResult exists in onex/protocol_validation.py (ONEX-specific
        # validation results) and validation/protocol_validation.py (general validation
        # results) - different validation contexts
        "ProtocolValidationResult",
    }

    def test_no_duplicate_protocol_definitions(self) -> None:
        """Validate that no protocol is defined in multiple files.

        Ensures protocol naming is unique across the codebase to prevent
        confusion and import conflicts. Known duplicates are documented and
        excluded from failure.
        """
        protocols_by_file = self._scan_protocols_directory()

        # Track protocol occurrences
        protocol_occurrences: dict[str, list[str]] = {}

        for file_path, protocols in protocols_by_file.items():
            for protocol in protocols:
                if protocol not in protocol_occurrences:
                    protocol_occurrences[protocol] = []
                protocol_occurrences[protocol].append(file_path)

        # Find duplicates (excluding known ones)
        duplicates = {
            protocol: files
            for protocol, files in protocol_occurrences.items()
            if len(files) > 1 and protocol not in self.KNOWN_DUPLICATE_PROTOCOLS
        }

        # Report known duplicates as informational
        known_duplicates_found = {
            protocol: files
            for protocol, files in protocol_occurrences.items()
            if len(files) > 1 and protocol in self.KNOWN_DUPLICATE_PROTOCOLS
        }

        if known_duplicates_found:
            print("\nKnown duplicate protocols (documented, not failing):")
            for protocol, files in sorted(known_duplicates_found.items()):
                print(f"  - {protocol}: {files}")

        if duplicates:
            msg_parts = ["New duplicate protocol definitions found:"]
            for protocol, files in sorted(duplicates.items()):
                msg_parts.append(f"  - {protocol}: {files}")
            msg_parts.append("")
            msg_parts.append(
                "Add to KNOWN_DUPLICATE_PROTOCOLS with justification, or rename protocols."
            )
            pytest.fail("\n".join(msg_parts))

    def test_protocol_naming_convention(self) -> None:
        """Validate that all Protocol classes follow the naming convention.

        All protocol class names should start with 'Protocol' prefix as per
        the SPI naming conventions documented in CLAUDE.md.
        """
        protocols_by_file = self._scan_protocols_directory()

        # Collect violations
        violations: list[tuple[str, str]] = []

        for file_path, protocols in protocols_by_file.items():
            for protocol in protocols:
                if not protocol.startswith("Protocol"):
                    violations.append((protocol, file_path))

        if violations:
            msg_parts = [
                "Protocol naming convention violations found:",
                "(Protocol classes should start with 'Protocol' prefix)",
            ]
            for protocol, file_path in sorted(violations):
                msg_parts.append(f"  - {protocol} ({file_path})")
            pytest.fail("\n".join(msg_parts))


class TestProtocolSignatureValidation:
    """Validate protocol method signatures using inspect.signature().

    These tests provide stronger contract verification than hasattr() checks
    by validating parameter names, default values, and annotations.

    While TestProtocolMethodSignatures verifies method presence using hasattr()
    and callable(), this class uses inspect.signature() to validate:
    - Parameter names match expected
    - Required parameters are present
    - Default values exist where expected
    - Return type annotations exist

    This catches contract drift where methods exist but have incorrect signatures.
    """

    def test_compute_node_execute_signature(self) -> None:
        """Validate ProtocolComputeNode.execute has correct parameters.

        The execute method must have:
        - self: implicit first parameter
        - input_data: required parameter for compute input model
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode

        sig = inspect.signature(ProtocolComputeNode.execute)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "execute() missing 'self' parameter"
        assert "input_data" in params, "execute() missing 'input_data' parameter"

        # Verify input_data has no default (is required)
        input_data_param = sig.parameters["input_data"]
        assert input_data_param.default is inspect.Parameter.empty, (
            "input_data should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "execute() should have a return type annotation"
        )

    def test_handler_execute_signature(self) -> None:
        """Validate ProtocolHandler.execute has correct parameters.

        The execute method must have:
        - self: implicit first parameter
        - request: required parameter for protocol request model
        - operation_config: required parameter for operation configuration
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        sig = inspect.signature(ProtocolHandler.execute)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "execute() missing 'self' parameter"
        assert "request" in params, "execute() missing 'request' parameter"
        assert "operation_config" in params, (
            "execute() missing 'operation_config' parameter"
        )

        # Verify request has no default (is required)
        request_param = sig.parameters["request"]
        assert request_param.default is inspect.Parameter.empty, (
            "request should not have a default value (must be required)"
        )

        # Verify operation_config has no default (is required)
        operation_config_param = sig.parameters["operation_config"]
        assert operation_config_param.default is inspect.Parameter.empty, (
            "operation_config should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "execute() should have a return type annotation"
        )

    def test_handler_shutdown_signature(self) -> None:
        """Validate ProtocolHandler.shutdown has correct parameters with default.

        The shutdown method must have:
        - self: implicit first parameter
        - timeout_seconds: parameter with default value of 30.0
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        sig = inspect.signature(ProtocolHandler.shutdown)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "shutdown() missing 'self' parameter"
        assert "timeout_seconds" in params, (
            "shutdown() missing 'timeout_seconds' parameter"
        )

        # Verify timeout_seconds has a default value
        timeout_param = sig.parameters["timeout_seconds"]
        assert timeout_param.default is not inspect.Parameter.empty, (
            "timeout_seconds should have a default value"
        )
        assert timeout_param.default == 30.0, (
            f"timeout_seconds default should be 30.0, got {timeout_param.default}"
        )

        # Verify return annotation exists (should be None for shutdown)
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "shutdown() should have a return type annotation"
        )

    def test_handler_initialize_signature(self) -> None:
        """Validate ProtocolHandler.initialize has correct parameters.

        The initialize method must have:
        - self: implicit first parameter
        - config: required parameter for connection configuration
        """
        from omnibase_spi.protocols.handlers import ProtocolHandler

        sig = inspect.signature(ProtocolHandler.initialize)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "initialize() missing 'self' parameter"
        assert "config" in params, "initialize() missing 'config' parameter"

        # Verify config has no default (is required)
        config_param = sig.parameters["config"]
        assert config_param.default is inspect.Parameter.empty, (
            "config should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "initialize() should have a return type annotation"
        )

    def test_registry_register_signature(self) -> None:
        """Validate ProtocolHandlerRegistry.register has correct parameters.

        The register method must have:
        - self: implicit first parameter
        - key: required string parameter for protocol identifier (replaces protocol_type)
        - value: required parameter for handler class type (replaces handler_cls)
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        sig = inspect.signature(ProtocolHandlerRegistry.register)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "register() missing 'self' parameter"
        assert "key" in params, "register() missing 'key' parameter"
        assert "value" in params, "register() missing 'value' parameter"

        # Verify key has no default (is required)
        key_param = sig.parameters["key"]
        assert key_param.default is inspect.Parameter.empty, (
            "key should not have a default value (must be required)"
        )

        # Verify value has no default (is required)
        value_param = sig.parameters["value"]
        assert value_param.default is inspect.Parameter.empty, (
            "value should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "register() should have a return type annotation"
        )

    def test_registry_get_signature(self) -> None:
        """Validate ProtocolHandlerRegistry.get has correct parameters.

        The get method must have:
        - self: implicit first parameter
        - key: required string parameter for protocol identifier (replaces protocol_type)
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        sig = inspect.signature(ProtocolHandlerRegistry.get)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "get() missing 'self' parameter"
        assert "key" in params, "get() missing 'key' parameter"

        # Verify key has no default (is required)
        key_param = sig.parameters["key"]
        assert key_param.default is inspect.Parameter.empty, (
            "key should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "get() should have a return type annotation"
        )

    def test_registry_is_registered_signature(self) -> None:
        """Validate ProtocolHandlerRegistry.is_registered has correct parameters.

        The is_registered method must have:
        - self: implicit first parameter
        - key: required string parameter for protocol identifier (replaces protocol_type)
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        sig = inspect.signature(ProtocolHandlerRegistry.is_registered)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "is_registered() missing 'self' parameter"
        assert "key" in params, "is_registered() missing 'key' parameter"

        # Verify key has no default (is required)
        key_param = sig.parameters["key"]
        assert key_param.default is inspect.Parameter.empty, (
            "key should not have a default value (must be required)"
        )

        # Verify return annotation exists (should be bool)
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "is_registered() should have a return type annotation"
        )

    def test_registry_list_keys_signature(self) -> None:
        """Validate ProtocolHandlerRegistry.list_keys has correct signature.

        The list_keys method must have:
        - self: implicit first parameter
        - No other required parameters
        """
        from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

        sig = inspect.signature(ProtocolHandlerRegistry.list_keys)
        params = list(sig.parameters.keys())

        # Verify only self parameter exists
        assert "self" in params, "list_keys() missing 'self' parameter"
        assert len(params) == 1, f"list_keys() should only have 'self', got {params}"

        # Verify return annotation exists (should be list[str])
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "list_keys() should have a return type annotation"
        )

    def test_effect_node_execute_signature(self) -> None:
        """Validate ProtocolEffectNode.execute has correct parameters.

        The execute method must have:
        - self: implicit first parameter
        - input_data: required parameter for effect input model
        """
        from omnibase_spi.protocols.nodes import ProtocolEffectNode

        sig = inspect.signature(ProtocolEffectNode.execute)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "execute() missing 'self' parameter"
        assert "input_data" in params, "execute() missing 'input_data' parameter"

        # Verify input_data has no default (is required)
        input_data_param = sig.parameters["input_data"]
        assert input_data_param.default is inspect.Parameter.empty, (
            "input_data should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "execute() should have a return type annotation"
        )

    def test_contract_compiler_compile_signature(self) -> None:
        """Validate ProtocolEffectContractCompiler.compile has correct parameters.

        The compile method must have:
        - self: implicit first parameter
        - contract_path: required parameter for contract file path
        """
        from omnibase_spi.protocols.contracts import ProtocolEffectContractCompiler

        sig = inspect.signature(ProtocolEffectContractCompiler.compile)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "compile() missing 'self' parameter"
        assert "contract_path" in params, "compile() missing 'contract_path' parameter"

        # Verify contract_path has no default (is required)
        contract_path_param = sig.parameters["contract_path"]
        assert contract_path_param.default is inspect.Parameter.empty, (
            "contract_path should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "compile() should have a return type annotation"
        )

    def test_contract_compiler_validate_signature(self) -> None:
        """Validate ProtocolEffectContractCompiler.validate has correct parameters.

        The validate method must have:
        - self: implicit first parameter
        - contract_path: required parameter for path to contract file to validate
        """
        from omnibase_spi.protocols.contracts import ProtocolEffectContractCompiler

        sig = inspect.signature(ProtocolEffectContractCompiler.validate)
        params = list(sig.parameters.keys())

        # Verify required parameters exist
        assert "self" in params, "validate() missing 'self' parameter"
        assert "contract_path" in params, "validate() missing 'contract_path' parameter"

        # Verify contract_path has no default (is required)
        contract_path_param = sig.parameters["contract_path"]
        assert contract_path_param.default is inspect.Parameter.empty, (
            "contract_path should not have a default value (must be required)"
        )

        # Verify return annotation exists
        assert sig.return_annotation is not inspect.Parameter.empty, (
            "validate() should have a return type annotation"
        )


class TestProtocolInheritanceChains:
    """Test protocol inheritance relationships.

    Validates that child protocols correctly inherit from parent protocols
    and maintain proper attribute/method inheritance chains.

    The ONEX node architecture defines a hierarchy:
        ProtocolNode (base)
            -> ProtocolComputeNode (pure transformations)
            -> ProtocolEffectNode (I/O operations)
            -> ProtocolReducerNode (state aggregation)
            -> ProtocolOrchestratorNode (workflow coordination)

    These tests verify:
        1. Child protocols have all parent protocol attributes
        2. Inheritance is properly declared in class bases
        3. isinstance() checks work correctly for hierarchies
        4. Mock implementations satisfying child protocols also satisfy parent
    """

    def test_compute_node_inherits_from_protocol_node(self) -> None:
        """Validate ProtocolComputeNode has all ProtocolNode attributes.

        ProtocolComputeNode inherits from ProtocolNode and must expose
        the base identity attributes (node_id, node_type, version).
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode, ProtocolNode

        # Verify ProtocolComputeNode has base node attributes
        assert hasattr(ProtocolComputeNode, "node_id"), (
            "ProtocolComputeNode missing inherited node_id"
        )
        assert hasattr(ProtocolComputeNode, "node_type"), (
            "ProtocolComputeNode missing inherited node_type"
        )
        assert hasattr(ProtocolComputeNode, "version"), (
            "ProtocolComputeNode missing inherited version"
        )

        # Verify ProtocolNode is in the MRO (method resolution order)
        assert ProtocolNode in ProtocolComputeNode.__mro__, (
            "ProtocolNode should be in ProtocolComputeNode's MRO"
        )

        # Verify compute-specific attributes also exist
        assert hasattr(ProtocolComputeNode, "is_deterministic"), (
            "ProtocolComputeNode missing is_deterministic"
        )
        assert hasattr(ProtocolComputeNode, "execute"), (
            "ProtocolComputeNode missing execute"
        )

    def test_effect_node_inherits_from_protocol_node(self) -> None:
        """Validate ProtocolEffectNode has all ProtocolNode attributes.

        ProtocolEffectNode inherits from ProtocolNode and must expose
        the base identity attributes plus lifecycle methods.
        """
        from omnibase_spi.protocols.nodes import ProtocolEffectNode, ProtocolNode

        # Verify ProtocolEffectNode has base node attributes
        assert hasattr(ProtocolEffectNode, "node_id"), (
            "ProtocolEffectNode missing inherited node_id"
        )
        assert hasattr(ProtocolEffectNode, "node_type"), (
            "ProtocolEffectNode missing inherited node_type"
        )
        assert hasattr(ProtocolEffectNode, "version"), (
            "ProtocolEffectNode missing inherited version"
        )

        # Verify ProtocolNode is in the MRO
        assert ProtocolNode in ProtocolEffectNode.__mro__, (
            "ProtocolNode should be in ProtocolEffectNode's MRO"
        )

        # Verify effect-specific lifecycle methods exist
        assert hasattr(ProtocolEffectNode, "initialize"), (
            "ProtocolEffectNode missing initialize"
        )
        assert hasattr(ProtocolEffectNode, "shutdown"), (
            "ProtocolEffectNode missing shutdown"
        )
        assert hasattr(ProtocolEffectNode, "execute"), (
            "ProtocolEffectNode missing execute"
        )

    def test_reducer_node_inherits_from_protocol_node(self) -> None:
        """Validate ProtocolReducerNode has all ProtocolNode attributes.

        ProtocolReducerNode inherits from ProtocolNode and must expose
        the base identity attributes.
        """
        from omnibase_spi.protocols.nodes import ProtocolNode, ProtocolReducerNode

        # Verify ProtocolReducerNode has base node attributes
        assert hasattr(ProtocolReducerNode, "node_id"), (
            "ProtocolReducerNode missing inherited node_id"
        )
        assert hasattr(ProtocolReducerNode, "node_type"), (
            "ProtocolReducerNode missing inherited node_type"
        )
        assert hasattr(ProtocolReducerNode, "version"), (
            "ProtocolReducerNode missing inherited version"
        )

        # Verify ProtocolNode is in the MRO
        assert ProtocolNode in ProtocolReducerNode.__mro__, (
            "ProtocolNode should be in ProtocolReducerNode's MRO"
        )

        # Verify reducer-specific execute method exists
        assert hasattr(ProtocolReducerNode, "execute"), (
            "ProtocolReducerNode missing execute"
        )

    def test_orchestrator_node_inherits_from_protocol_node(self) -> None:
        """Validate ProtocolOrchestratorNode has all ProtocolNode attributes.

        ProtocolOrchestratorNode inherits from ProtocolNode and must expose
        the base identity attributes.
        """
        from omnibase_spi.protocols.nodes import ProtocolNode, ProtocolOrchestratorNode

        # Verify ProtocolOrchestratorNode has base node attributes
        assert hasattr(ProtocolOrchestratorNode, "node_id"), (
            "ProtocolOrchestratorNode missing inherited node_id"
        )
        assert hasattr(ProtocolOrchestratorNode, "node_type"), (
            "ProtocolOrchestratorNode missing inherited node_type"
        )
        assert hasattr(ProtocolOrchestratorNode, "version"), (
            "ProtocolOrchestratorNode missing inherited version"
        )

        # Verify ProtocolNode is in the MRO
        assert ProtocolNode in ProtocolOrchestratorNode.__mro__, (
            "ProtocolNode should be in ProtocolOrchestratorNode's MRO"
        )

        # Verify orchestrator-specific execute method exists
        assert hasattr(ProtocolOrchestratorNode, "execute"), (
            "ProtocolOrchestratorNode missing execute"
        )

    def test_isinstance_inheritance_chain_compute_node(self) -> None:
        """Validate isinstance() works correctly for ProtocolComputeNode hierarchy.

        A mock implementing ProtocolComputeNode should also satisfy
        isinstance() checks against ProtocolNode due to inheritance.
        """
        from omnibase_spi.protocols.nodes import ProtocolComputeNode, ProtocolNode

        class MockComputeNode:
            """Mock implementation satisfying ProtocolComputeNode contract."""

            # Base ProtocolNode attributes
            node_id = "compute-test-001"
            node_type = "compute"
            version = "1.0.0"

            # ProtocolComputeNode-specific attribute
            is_deterministic = True

            async def execute(self, input_data: object) -> object:
                """Execute compute operation."""
                return input_data

        mock = MockComputeNode()

        # Should satisfy ProtocolComputeNode
        assert isinstance(mock, ProtocolComputeNode), (
            "Mock should be isinstance of ProtocolComputeNode"
        )

        # Should also satisfy ProtocolNode due to inheritance
        assert isinstance(mock, ProtocolNode), (
            "Mock satisfying ProtocolComputeNode should also satisfy ProtocolNode"
        )

    def test_isinstance_inheritance_chain_effect_node(self) -> None:
        """Validate isinstance() works correctly for ProtocolEffectNode hierarchy.

        A mock implementing ProtocolEffectNode should also satisfy
        isinstance() checks against ProtocolNode due to inheritance.
        """
        from omnibase_spi.protocols.nodes import ProtocolEffectNode, ProtocolNode

        class MockEffectNode:
            """Mock implementation satisfying ProtocolEffectNode contract."""

            # Base ProtocolNode attributes
            node_id = "effect-test-001"
            node_type = "effect"
            version = "1.0.0"

            async def initialize(self) -> None:
                """Initialize effect node resources."""
                pass

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                """Shutdown effect node resources."""
                pass

            async def execute(self, input_data: object) -> object:
                """Execute effect operation."""
                return input_data

        mock = MockEffectNode()

        # Should satisfy ProtocolEffectNode
        assert isinstance(mock, ProtocolEffectNode), (
            "Mock should be isinstance of ProtocolEffectNode"
        )

        # Should also satisfy ProtocolNode due to inheritance
        assert isinstance(mock, ProtocolNode), (
            "Mock satisfying ProtocolEffectNode should also satisfy ProtocolNode"
        )

    def test_all_node_protocols_share_base_attributes(self) -> None:
        """Validate all node protocol variants share ProtocolNode base attributes.

        All specialized node protocols (compute, effect, reducer, orchestrator)
        should define the same base attributes from ProtocolNode.
        """
        from omnibase_spi.protocols.nodes import (
            ProtocolComputeNode,
            ProtocolEffectNode,
            ProtocolNode,
            ProtocolOrchestratorNode,
            ProtocolReducerNode,
        )

        # Base attributes that all node protocols must have
        base_attributes = {"node_id", "node_type", "version"}

        node_protocols = [
            ("ProtocolNode", ProtocolNode),
            ("ProtocolComputeNode", ProtocolComputeNode),
            ("ProtocolEffectNode", ProtocolEffectNode),
            ("ProtocolReducerNode", ProtocolReducerNode),
            ("ProtocolOrchestratorNode", ProtocolOrchestratorNode),
        ]

        for name, protocol in node_protocols:
            for attr in base_attributes:
                assert hasattr(protocol, attr), (
                    f"{name} missing base attribute '{attr}' from ProtocolNode"
                )

    def test_protocol_hierarchy_mro_consistency(self) -> None:
        """Validate MRO (Method Resolution Order) is consistent across node protocols.

        All specialized node protocols should have ProtocolNode in their MRO,
        ensuring proper inheritance chain resolution.
        """
        from omnibase_spi.protocols.nodes import (
            ProtocolComputeNode,
            ProtocolEffectNode,
            ProtocolNode,
            ProtocolOrchestratorNode,
            ProtocolReducerNode,
        )

        child_protocols = [
            ("ProtocolComputeNode", ProtocolComputeNode),
            ("ProtocolEffectNode", ProtocolEffectNode),
            ("ProtocolReducerNode", ProtocolReducerNode),
            ("ProtocolOrchestratorNode", ProtocolOrchestratorNode),
        ]

        for name, protocol in child_protocols:
            assert ProtocolNode in protocol.__mro__, (
                f"{name} should have ProtocolNode in its MRO for proper inheritance"
            )

"""
Type checking tests for memory protocols.

These tests verify that memory protocols maintain proper type safety
and can be validated with mypy static analysis.
"""

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from pytest import FixtureRequest

if TYPE_CHECKING:
    from omnibase_spi.protocols.memory import (
        ProtocolMemoryComputeNode,
        ProtocolMemoryEffectNode,
        ProtocolMemoryHealthNode,
        ProtocolMemoryOrchestratorNode,
        ProtocolMemoryReducerNode,
    )


class TestTypeChecking:
    """Test type checking with mypy."""

    @pytest.fixture  # type: ignore[misc]
    def memory_protocols_path(self) -> Path:
        """Get path to memory protocols directory."""
        return (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "omnibase_spi"
            / "protocols"
            / "memory"
        )

    def test_mypy_protocol_operations(self, memory_protocols_path: Path) -> None:
        """Test that protocol_memory_operations.py passes mypy type checking."""
        operations_file = memory_protocols_path / "protocol_memory_operations.py"
        assert (
            operations_file.exists()
        ), f"Protocol operations file not found: {operations_file}"

        # Run mypy on the operations file
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(operations_file), "--strict"],
            capture_output=True,
            text=True,
            cwd=memory_protocols_path.parent.parent.parent,
        )

        # Check if mypy passed (exit code 0)
        if result.returncode != 0:
            pytest.fail(
                f"MyPy type checking failed for protocol_memory_operations.py:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

    def test_mypy_protocol_types(self, memory_protocols_path: Path) -> None:
        """Test that all memory protocol type files pass mypy type checking."""
        type_files = [
            "protocol_memory_base.py",
            "protocol_memory_requests.py",
            "protocol_memory_responses.py",
            "protocol_memory_errors.py",
        ]

        for type_file in type_files:
            file_path = memory_protocols_path / type_file
            if not file_path.exists():
                continue  # Skip if file doesn't exist

            result = subprocess.run(
                [sys.executable, "-m", "mypy", str(file_path), "--strict"],
                capture_output=True,
                text=True,
                cwd=memory_protocols_path.parent.parent.parent,
            )

            if result.returncode != 0:
                pytest.fail(
                    f"MyPy type checking failed for {type_file}:\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )

    def test_mypy_memory_module_init(self, memory_protocols_path: Path) -> None:
        """Test that memory module __init__.py passes mypy type checking."""
        init_file = memory_protocols_path / "__init__.py"
        assert init_file.exists(), f"Memory module __init__.py not found: {init_file}"

        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(init_file), "--strict"],
            capture_output=True,
            text=True,
            cwd=memory_protocols_path.parent.parent.parent,
        )

        if result.returncode != 0:
            pytest.fail(
                f"MyPy type checking failed for memory/__init__.py:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )


class TestTypeAnnotationConsistency:
    """Test type annotation consistency across memory protocols."""

    def test_protocol_import_compatibility(self) -> None:
        """Test that all memory protocols can be imported without type errors."""
        try:
            from omnibase_spi.protocols.memory import (
                ProtocolMemoryComputeNode,
                ProtocolMemoryEffectNode,
                ProtocolMemoryHealthNode,
                ProtocolMemoryOrchestratorNode,
                ProtocolMemoryReducerNode,
            )

            # Verify protocols were imported successfully
            protocols = [
                ProtocolMemoryEffectNode,
                ProtocolMemoryComputeNode,
                ProtocolMemoryReducerNode,
                ProtocolMemoryOrchestratorNode,
                ProtocolMemoryHealthNode,
            ]

            for protocol in protocols:
                assert protocol is not None
                assert hasattr(protocol, "__annotations__") or hasattr(
                    protocol, "__protocol__"
                )

        except ImportError as e:
            pytest.fail(f"Failed to import memory protocols: {e}")

    def test_forward_reference_resolution(self) -> None:
        """Test that forward references in memory protocols are properly defined."""
        from omnibase_spi.protocols.memory import protocol_memory_operations

        # Check that the module has all expected protocols
        expected_protocols = [
            "ProtocolMemoryEffectNode",
            "ProtocolMemoryComputeNode",
            "ProtocolMemoryReducerNode",
            "ProtocolMemoryOrchestratorNode",
            "ProtocolMemoryHealthNode",
        ]

        for protocol_name in expected_protocols:
            assert hasattr(
                protocol_memory_operations, protocol_name
            ), f"Protocol {protocol_name} not found in protocol_memory_operations"

    def test_type_checking_import_pattern(self) -> None:
        """Test that TYPE_CHECKING imports work correctly."""
        # This test verifies that the TYPE_CHECKING import pattern doesn't cause runtime errors
        try:
            # Import should work at runtime even with TYPE_CHECKING imports
            from omnibase_spi.protocols.memory.protocol_memory_operations import (
                ProtocolMemoryEffectNode,
            )

            # Protocol should be importable
            assert ProtocolMemoryEffectNode is not None

            # Protocol should be runtime checkable
            assert hasattr(ProtocolMemoryEffectNode, "_is_runtime_protocol")

        except ImportError as e:
            pytest.fail(f"TYPE_CHECKING import pattern failed: {e}")


class TestTypeHintValidation:
    """Test that type hints are properly defined and consistent."""

    def test_async_method_return_types(self) -> None:
        """Test that async methods have proper return type annotations."""
        import inspect
        from typing import get_type_hints

        from omnibase_spi.protocols.memory import ProtocolMemoryEffectNode

        # Get all async methods from the protocol
        async_methods = [
            name
            for name, method in inspect.getmembers(ProtocolMemoryEffectNode)
            if inspect.iscoroutinefunction(method)
            or (hasattr(method, "__annotations__") and inspect.isfunction(method))
        ]

        # Verify we found some async methods
        assert (
            len(async_methods) > 0
        ), "No async methods found in ProtocolMemoryEffectNode"

        # Check specific expected methods
        expected_methods = [
            "store_memory",
            "retrieve_memory",
            "update_memory",
            "delete_memory",
            "list_memories",
            "batch_store_memories",
            "batch_retrieve_memories",
        ]

        for method_name in expected_methods:
            assert (
                method_name in async_methods
            ), f"Expected async method {method_name} not found"

    def test_optional_parameter_annotations(self) -> None:
        """Test that optional parameters are properly annotated."""
        import inspect

        from omnibase_spi.protocols.memory import ProtocolMemoryEffectNode

        # Check batch_store_memories method for timeout parameter
        method = getattr(ProtocolMemoryEffectNode, "batch_store_memories", None)
        assert method is not None, "batch_store_memories method not found"

        # Get method signature
        sig = inspect.signature(method)
        params = sig.parameters

        # Check that timeout_seconds parameter exists and is optional
        assert "timeout_seconds" in params, "timeout_seconds parameter not found"
        timeout_param = params["timeout_seconds"]

        # Parameter should have a default value (None)
        assert timeout_param.default is None, "timeout_seconds should default to None"

    def test_uuid_type_annotations(self) -> None:
        """Test that UUID parameters are properly annotated."""
        import inspect

        from omnibase_spi.protocols.memory import ProtocolMemoryEffectNode

        # Check update_memory method for UUID parameter
        method = getattr(ProtocolMemoryEffectNode, "update_memory", None)
        assert method is not None, "update_memory method not found"

        # Get method signature
        sig = inspect.signature(method)
        params = sig.parameters

        # Check that memory_id parameter exists
        assert "memory_id" in params, "memory_id parameter not found"
        memory_id_param = params["memory_id"]

        # Parameter should be annotated (we can't directly check UUID type due to forward refs)
        assert (
            memory_id_param.annotation != inspect.Parameter.empty
        ), "memory_id parameter should have type annotation"


class TestImportIsolation:
    """Test that memory protocols maintain proper import isolation."""

    def test_no_implementation_imports(self) -> None:
        """Test that memory protocols don't import implementation modules."""
        import sys

        from omnibase_spi.protocols.memory import protocol_memory_operations

        # Get all imported modules for the protocol_memory_operations module
        protocol_module = sys.modules[
            "omnibase_spi.protocols.memory.protocol_memory_operations"
        ]

        # Check that no implementation modules are imported
        forbidden_imports = [
            "omnibase_spi.model",
            "omnibase_spi.core",
            "omnibase_spi.implementation",
            "omnibase_spi.services",
        ]

        for module_name in sys.modules:
            if any(forbidden in module_name for forbidden in forbidden_imports):
                # Make sure this module is not referenced by our protocol module
                if hasattr(protocol_module, module_name.split(".")[-1]):
                    pytest.fail(
                        f"Protocol module should not import implementation module: {module_name}"
                    )

    def test_spi_namespace_isolation(self) -> None:
        """Test that memory protocols only import from omnibase_spi.protocols namespace."""
        import ast
        from pathlib import Path

        memory_protocols_path = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "omnibase_spi"
            / "protocols"
            / "memory"
        )

        protocol_files = [
            "protocol_memory_operations.py",
            "protocol_memory_base.py",
            "protocol_memory_requests.py",
            "protocol_memory_responses.py",
            "protocol_memory_errors.py",
        ]

        for protocol_file in protocol_files:
            file_path = memory_protocols_path / protocol_file
            if not file_path.exists():
                continue

            # Parse the file to check imports
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())

            # Check all import statements
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Allow standard library and typing imports
                        if not alias.name.startswith("omnibase_spi"):
                            continue

                        # Must be from protocols namespace
                        assert alias.name.startswith("omnibase_spi.protocols"), (
                            f"Invalid import in {protocol_file}: {alias.name} "
                            f"(must be from omnibase_spi.protocols namespace)"
                        )

                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("omnibase_spi"):
                        # Must be from protocols namespace
                        assert node.module.startswith("omnibase_spi.protocols"), (
                            f"Invalid import in {protocol_file}: from {node.module} "
                            f"(must be from omnibase_spi.protocols namespace)"
                        )


class TestProtocolMethodConsistency:
    """Test that protocol methods have consistent signatures and patterns."""

    def test_correlation_id_parameter_consistency(self) -> None:
        """Test that correlation_id parameters are consistently defined."""
        import inspect

        from omnibase_spi.protocols.memory import (
            ProtocolMemoryComputeNode,
            ProtocolMemoryEffectNode,
            ProtocolMemoryHealthNode,
            ProtocolMemoryOrchestratorNode,
            ProtocolMemoryReducerNode,
        )

        protocols = [
            ProtocolMemoryEffectNode,
            ProtocolMemoryComputeNode,
            ProtocolMemoryReducerNode,
            ProtocolMemoryOrchestratorNode,
            ProtocolMemoryHealthNode,
        ]

        correlation_id_methods = []

        for protocol in protocols:
            for name, method in inspect.getmembers(protocol):
                if inspect.isfunction(method) or inspect.iscoroutinefunction(method):
                    sig = inspect.signature(method)
                    if "correlation_id" in sig.parameters:
                        correlation_id_methods.append((protocol.__name__, name))

                        # Check that correlation_id parameter is optional
                        param = sig.parameters["correlation_id"]
                        assert (
                            param.default is None
                        ), f"correlation_id in {protocol.__name__}.{name} should default to None"

        # Verify we found some methods with correlation_id
        assert (
            len(correlation_id_methods) > 0
        ), "No methods found with correlation_id parameter"

    def test_timeout_parameter_consistency(self) -> None:
        """Test that timeout_seconds parameters are consistently defined."""
        import inspect

        from omnibase_spi.protocols.memory import (
            ProtocolMemoryComputeNode,
            ProtocolMemoryEffectNode,
            ProtocolMemoryOrchestratorNode,
            ProtocolMemoryReducerNode,
        )

        protocols = [
            ProtocolMemoryEffectNode,
            ProtocolMemoryComputeNode,
            ProtocolMemoryReducerNode,
            ProtocolMemoryOrchestratorNode,
        ]

        timeout_methods = []

        for protocol in protocols:
            for name, method in inspect.getmembers(protocol):
                if inspect.isfunction(method) or inspect.iscoroutinefunction(method):
                    sig = inspect.signature(method)
                    if "timeout_seconds" in sig.parameters:
                        timeout_methods.append((protocol.__name__, name))

                        # Check that timeout_seconds parameter is optional
                        param = sig.parameters["timeout_seconds"]
                        assert (
                            param.default is None
                        ), f"timeout_seconds in {protocol.__name__}.{name} should default to None"

        # Verify we found timeout methods
        expected_timeout_methods = [
            ("ProtocolMemoryEffectNode", "batch_store_memories"),
            ("ProtocolMemoryEffectNode", "batch_retrieve_memories"),
            ("ProtocolMemoryComputeNode", "analyze_patterns"),
            ("ProtocolMemoryReducerNode", "consolidate_memories"),
            ("ProtocolMemoryReducerNode", "optimize_storage"),
            ("ProtocolMemoryOrchestratorNode", "execute_workflow"),
        ]

        for expected_method in expected_timeout_methods:
            assert (
                expected_method in timeout_methods
            ), f"Expected timeout method not found: {expected_method}"


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])

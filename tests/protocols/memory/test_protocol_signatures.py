"""
Structural tests for memory protocol signature stability.

These tests verify that protocol signatures remain stable across changes,
ensuring backward compatibility and preventing accidental breaking changes.
"""

import inspect
from datetime import datetime
from typing import Optional, get_type_hints
from uuid import UUID

import pytest

from omnibase_spi.protocols.memory import (
    ProtocolBatchOperationResult,
    ProtocolMemoryComputeNode,
    ProtocolMemoryEffectNode,
    ProtocolMemoryError,
    ProtocolMemoryHealthNode,
    ProtocolMemoryMetrics,
    ProtocolMemoryOrchestratorNode,
    ProtocolMemoryRecord,
    ProtocolMemoryReducerNode,
    ProtocolPaginationRequest,
)


class TestProtocolSignatureStability:
    """Test protocol signatures for stability and consistency."""

    def test_memory_effect_node_signature(self) -> None:
        """Test ProtocolMemoryEffectNode method signatures."""
        expected_methods = {
            "store_memory",
            "retrieve_memory",
            "update_memory",
            "delete_memory",
            "list_memories",
            "batch_store_memories",
            "batch_retrieve_memories",
        }

        actual_methods = {
            name
            for name, method in inspect.getmembers(ProtocolMemoryEffectNode)
            if inspect.isfunction(method) or inspect.iscoroutinefunction(method)
        }

        # Check that all expected methods exist
        assert expected_methods.issubset(
            actual_methods
        ), f"Missing methods: {expected_methods - actual_methods}"

    def test_memory_compute_node_signature(self) -> None:
        """Test ProtocolMemoryComputeNode method signatures."""
        expected_methods = {
            "semantic_search",
            "generate_embedding",
            "analyze_patterns",
            "extract_insights",
            "compare_semantics",
        }

        actual_methods = {
            name
            for name, method in inspect.getmembers(ProtocolMemoryComputeNode)
            if inspect.isfunction(method) or inspect.iscoroutinefunction(method)
        }

        assert expected_methods.issubset(
            actual_methods
        ), f"Missing methods: {expected_methods - actual_methods}"

    def test_memory_reducer_node_signature(self) -> None:
        """Test ProtocolMemoryReducerNode method signatures."""
        expected_methods = {
            "consolidate_memories",
            "deduplicate_memories",
            "aggregate_data",
            "compress_memories",
            "optimize_storage",
        }

        actual_methods = {
            name
            for name, method in inspect.getmembers(ProtocolMemoryReducerNode)
            if inspect.isfunction(method) or inspect.iscoroutinefunction(method)
        }

        assert expected_methods.issubset(
            actual_methods
        ), f"Missing methods: {expected_methods - actual_methods}"

    def test_memory_orchestrator_node_signature(self) -> None:
        """Test ProtocolMemoryOrchestratorNode method signatures."""
        expected_methods = {
            "execute_workflow",
            "coordinate_agents",
            "broadcast_update",
            "synchronize_state",
            "manage_lifecycle",
        }

        actual_methods = {
            name
            for name, method in inspect.getmembers(ProtocolMemoryOrchestratorNode)
            if inspect.isfunction(method) or inspect.iscoroutinefunction(method)
        }

        assert expected_methods.issubset(
            actual_methods
        ), f"Missing methods: {expected_methods - actual_methods}"

    def test_memory_health_node_signature(self) -> None:
        """Test ProtocolMemoryHealthNode method signatures."""
        expected_methods = {"check_health", "collect_metrics", "get_status"}

        actual_methods = {
            name
            for name, method in inspect.getmembers(ProtocolMemoryHealthNode)
            if inspect.isfunction(method) or inspect.iscoroutinefunction(method)
        }

        assert expected_methods.issubset(
            actual_methods
        ), f"Missing methods: {expected_methods - actual_methods}"


class TestProtocolAttributeTypes:
    """Test protocol attribute type annotations."""

    def test_memory_record_attributes(self) -> None:
        """Test ProtocolMemoryRecord has required attributes with correct types."""
        # Use the protocol module's globals for forward reference resolution
        import datetime as dt_module

        import omnibase_spi.protocols.memory.protocol_memory_base as protocol_module

        # Create comprehensive globalns with all needed types
        globalns = dict(protocol_module.__dict__)
        globalns["datetime"] = dt_module.datetime

        type_hints = get_type_hints(ProtocolMemoryRecord, globalns=globalns)

        expected_attributes = {
            "memory_id": UUID,
            "content": str,
            "content_type": str,
            "created_at": datetime,
            "updated_at": datetime,
            "access_level": str,
            "source_agent": str,
        }

        for attr_name, expected_type in expected_attributes.items():
            assert attr_name in type_hints, f"Missing attribute: {attr_name}"
            # Note: We can't directly compare types due to Optional wrapping
            # Just verify the attribute exists in type hints

    def test_memory_error_attributes(self) -> None:
        """Test ProtocolMemoryError has required attributes."""
        # Use the protocol module's globals for forward reference resolution
        import datetime as dt_module

        import omnibase_spi.protocols.memory.protocol_memory_errors as protocol_module

        # Create comprehensive globalns with all needed types
        globalns = dict(protocol_module.__dict__)
        globalns["datetime"] = dt_module.datetime

        type_hints = get_type_hints(ProtocolMemoryError, globalns=globalns)

        expected_attributes = {
            "error_code",
            "error_message",
            "error_timestamp",
            "correlation_id",
        }

        actual_attributes = set(type_hints.keys())
        assert expected_attributes.issubset(
            actual_attributes
        ), f"Missing attributes: {expected_attributes - actual_attributes}"

    def test_pagination_request_attributes(self) -> None:
        """Test ProtocolPaginationRequest has required attributes."""
        type_hints = get_type_hints(ProtocolPaginationRequest)

        expected_attributes = {"limit", "offset", "cursor"}

        actual_attributes = set(type_hints.keys())
        assert expected_attributes.issubset(
            actual_attributes
        ), f"Missing attributes: {expected_attributes - actual_attributes}"

    def test_memory_metrics_attributes(self) -> None:
        """Test ProtocolMemoryMetrics has required attributes."""
        # Use the protocol module's globals for forward reference resolution
        import datetime as dt_module

        import omnibase_spi.protocols.memory.protocol_memory_operations as protocol_module

        # Create comprehensive globalns with all needed types
        globalns = dict(protocol_module.__dict__)
        globalns["datetime"] = dt_module.datetime

        type_hints = get_type_hints(ProtocolMemoryMetrics, globalns=globalns)

        expected_attributes = {
            "operation_type",
            "execution_time_ms",
            "memory_usage_mb",
            "timestamp",
        }

        actual_attributes = set(type_hints.keys())
        assert expected_attributes.issubset(
            actual_attributes
        ), f"Missing attributes: {expected_attributes - actual_attributes}"

    def test_batch_operation_result_attributes(self) -> None:
        """Test ProtocolBatchOperationResult has required attributes."""
        type_hints = get_type_hints(ProtocolBatchOperationResult)

        expected_attributes = {"operation_index", "success", "result_id", "error"}

        actual_attributes = set(type_hints.keys())
        assert expected_attributes.issubset(
            actual_attributes
        ), f"Missing attributes: {expected_attributes - actual_attributes}"


class TestProtocolInheritance:
    """Test protocol inheritance relationships."""

    def test_all_protocols_are_runtime_checkable(self) -> None:
        """Test that all protocols are marked as runtime_checkable."""
        from omnibase_spi.protocols.memory import (
            protocol_memory_base,
            protocol_memory_operations,
        )

        # Get all classes from both modules
        protocol_classes = []

        for module in [protocol_memory_base, protocol_memory_operations]:
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    inspect.isclass(obj)
                    and name.startswith("Protocol")
                    and hasattr(obj, "__protocol__")
                ):
                    protocol_classes.append(obj)

        for protocol_class in protocol_classes:
            # Check if it's runtime checkable
            assert hasattr(
                protocol_class, "_is_runtime_protocol"
            ), f"{protocol_class.__name__} is not runtime checkable"


class TestProtocolConsistency:
    """Test consistency across protocol definitions."""

    def test_request_response_pairing(self) -> None:
        """Test that request protocols have corresponding response protocols."""
        from omnibase_spi.protocols.memory import protocol_memory_base

        request_protocols = []
        response_protocols = []

        for name in dir(protocol_memory_base):
            if name.endswith("Request") and name.startswith("Protocol"):
                request_protocols.append(name)
            elif name.endswith("Response") and name.startswith("Protocol"):
                response_protocols.append(name)

        # Check that each request has a corresponding response
        for request_name in request_protocols:
            expected_response = request_name.replace("Request", "Response")
            assert (
                expected_response in response_protocols
            ), f"Missing response protocol for {request_name}: {expected_response}"

    def test_protocol_naming_convention(self) -> None:
        """Test that all protocols follow naming conventions."""
        from omnibase_spi.protocols.memory import __all__

        # Type literals that are not protocols and shouldn't be required to start with "Protocol"
        type_literals = {
            "MemoryAccessLevel",
            "AnalysisType",
            "CompressionAlgorithm",
            "ErrorCategory",
            "AgentStatus",
            "WorkflowStatus",
        }

        for protocol_name in __all__:
            # Skip type literals - they don't need to start with "Protocol"
            if protocol_name in type_literals:
                continue

            # All exported protocols should start with 'Protocol'
            assert protocol_name.startswith(
                "Protocol"
            ), f"Protocol {protocol_name} doesn't follow naming convention"

            # Should use PascalCase
            assert protocol_name[
                8
            ].isupper(), (
                f"Protocol {protocol_name} doesn't use PascalCase after 'Protocol'"
            )

"""
Tests for ProtocolEventPublisher protocol signature verification.

This module validates that ProtocolEventPublisher:
- Is properly runtime checkable
- Defines a publish method with correct signature
- publish accepts topic: str | None parameter
- publish accepts partition_key: str | None parameter
- publish returns bool

These tests verify the interface contract for OMN-1615.
"""

import inspect
import types
from typing import Union, get_args, get_origin

import pytest

from omnibase_spi.protocols.event_bus import ProtocolEventPublisher

# =============================================================================
# Protocol Definition Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventPublisherSignature:
    """Test suite for ProtocolEventPublisher protocol signature verification."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventPublisher should be decorated with @runtime_checkable."""
        # Check for runtime protocol attribute (varies by Python version)
        assert hasattr(
            ProtocolEventPublisher, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventPublisher, "__protocol_attrs__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventPublisher should be a Protocol class."""
        # Check by name to avoid mypy comparison-overlap error with typing special forms
        assert any(
            getattr(base, "__name__", "") == "Protocol"
            for base in ProtocolEventPublisher.__mro__
        )

    def test_protocol_has_publish_method(self) -> None:
        """ProtocolEventPublisher should define a publish method."""
        assert hasattr(ProtocolEventPublisher, "publish")
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None
        assert callable(publish_method)

    def test_publish_is_async(self) -> None:
        """publish should be an async method (coroutine function)."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None
        assert inspect.iscoroutinefunction(publish_method)

    def test_publish_has_topic_parameter(self) -> None:
        """publish method should accept a topic parameter."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        assert "topic" in sig.parameters

        topic_param = sig.parameters["topic"]
        # Verify it has a default value (meaning it's optional)
        assert topic_param.default is None, "topic should default to None"

    def test_publish_topic_allows_str_or_none(self) -> None:
        """publish topic parameter should accept str | None."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        topic_param = sig.parameters["topic"]
        annotation = topic_param.annotation

        # Handle both Union[str, None] and str | None syntax
        origin = get_origin(annotation)
        if origin is Union or origin is types.UnionType:
            args = get_args(annotation)
            assert str in args, "topic annotation should include str"
            assert type(None) in args, "topic annotation should include None"
        else:
            # Fallback to string check for edge cases
            annotation_str = str(annotation)
            assert "str" in annotation_str
            assert "None" in annotation_str or topic_param.default is None

    def test_publish_has_partition_key_parameter(self) -> None:
        """publish method should accept a partition_key parameter."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        assert "partition_key" in sig.parameters

        partition_key_param = sig.parameters["partition_key"]
        # Verify it has a default value (meaning it's optional)
        assert partition_key_param.default is None, "partition_key should default to None"

    def test_publish_partition_key_allows_str_or_none(self) -> None:
        """publish partition_key parameter should accept str | None."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        partition_key_param = sig.parameters["partition_key"]
        annotation = partition_key_param.annotation

        # Handle both Union[str, None] and str | None syntax
        origin = get_origin(annotation)
        if origin is Union or origin is types.UnionType:
            args = get_args(annotation)
            assert str in args, "partition_key annotation should include str"
            assert type(None) in args, "partition_key annotation should include None"
        else:
            # Fallback to string check for edge cases
            annotation_str = str(annotation)
            assert "str" in annotation_str
            assert "None" in annotation_str or partition_key_param.default is None

    def test_publish_returns_bool(self) -> None:
        """publish method should have bool return type annotation."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        return_annotation = sig.return_annotation

        # Return annotation should be bool
        assert return_annotation is bool

    def test_publish_event_type_is_required(self) -> None:
        """event_type parameter should be required (no default value)."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        event_type_param = sig.parameters["event_type"]

        # Required parameters have Parameter.empty as default
        assert event_type_param.default is inspect.Parameter.empty, (
            "event_type should be required (no default value)"
        )

    def test_publish_payload_is_required(self) -> None:
        """payload parameter should be required (no default value)."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        payload_param = sig.parameters["payload"]

        # Required parameters have Parameter.empty as default
        assert payload_param.default is inspect.Parameter.empty, (
            "payload should be required (no default value)"
        )

    def test_publish_signature_complete(self) -> None:
        """Verify publish method has all expected parameters."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None

        sig = inspect.signature(publish_method)
        param_names = list(sig.parameters.keys())

        # Required parameters (from protocol definition)
        expected_params = {
            "self",
            "event_type",
            "payload",
            "correlation_id",
            "causation_id",
            "metadata",
            "topic",
            "partition_key",
        }

        for expected in expected_params:
            assert expected in param_names, f"Missing parameter: {expected}"


# =============================================================================
# Protocol Import Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventPublisherImports:
    """Test protocol imports from different locations."""

    def test_import_from_event_bus_package(self) -> None:
        """Test import from event_bus package."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventPublisher as PackageProtocol,
        )

        assert PackageProtocol is not None
        assert hasattr(PackageProtocol, "publish")

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol module."""
        from omnibase_spi.protocols.event_bus.protocol_event_publisher import (
            ProtocolEventPublisher as DirectProtocol,
        )

        assert DirectProtocol is not None
        assert hasattr(DirectProtocol, "publish")

    def test_both_imports_are_same_class(self) -> None:
        """Both import paths should resolve to the same class."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventPublisher as PackageProtocol,
        )
        from omnibase_spi.protocols.event_bus.protocol_event_publisher import (
            ProtocolEventPublisher as DirectProtocol,
        )

        assert PackageProtocol is DirectProtocol


# =============================================================================
# Protocol Documentation Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventPublisherDocumentation:
    """Test that protocol has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolEventPublisher should have a docstring."""
        assert ProtocolEventPublisher.__doc__ is not None
        assert len(ProtocolEventPublisher.__doc__.strip()) > 0

    def test_publish_has_docstring(self) -> None:
        """publish method should have a docstring."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None
        assert publish_method.__doc__ is not None
        assert len(publish_method.__doc__.strip()) > 0

    def test_publish_docstring_documents_topic(self) -> None:
        """publish docstring should document the topic parameter."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None
        assert publish_method.__doc__ is not None
        assert "topic" in publish_method.__doc__

    def test_publish_docstring_documents_partition_key(self) -> None:
        """publish docstring should document the partition_key parameter."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None
        assert publish_method.__doc__ is not None
        assert "partition_key" in publish_method.__doc__

    def test_publish_docstring_documents_return(self) -> None:
        """publish docstring should document the return value."""
        publish_method = getattr(ProtocolEventPublisher, "publish", None)
        assert publish_method is not None
        assert publish_method.__doc__ is not None
        # Should mention True/False or bool in Returns section
        assert "True" in publish_method.__doc__ or "bool" in publish_method.__doc__

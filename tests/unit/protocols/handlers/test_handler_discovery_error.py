"""
Tests for HandlerDiscoveryError exception.

Validates that HandlerDiscoveryError:
- Inherits from ProtocolHandlerError
- Inherits from SPIError
- Can be constructed with message only
- Can be constructed with message and context
- Properly stores and exposes context
"""

from __future__ import annotations

from typing import Any

import pytest

from omnibase_spi.exceptions import (
    HandlerDiscoveryError,
    ProtocolHandlerError,
    SPIError,
)


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestHandlerDiscoveryErrorInheritance:
    """Test HandlerDiscoveryError inheritance chain."""

    def test_inherits_from_protocol_handler_error(self) -> None:
        """HandlerDiscoveryError should inherit from ProtocolHandlerError."""
        assert issubclass(HandlerDiscoveryError, ProtocolHandlerError)

    def test_inherits_from_spi_error(self) -> None:
        """HandlerDiscoveryError should inherit from SPIError."""
        assert issubclass(HandlerDiscoveryError, SPIError)

    def test_inherits_from_exception(self) -> None:
        """HandlerDiscoveryError should inherit from Exception."""
        assert issubclass(HandlerDiscoveryError, Exception)

    def test_instance_is_protocol_handler_error(self) -> None:
        """HandlerDiscoveryError instance should be ProtocolHandlerError."""
        error = HandlerDiscoveryError("Test error")
        assert isinstance(error, ProtocolHandlerError)

    def test_instance_is_spi_error(self) -> None:
        """HandlerDiscoveryError instance should be SPIError."""
        error = HandlerDiscoveryError("Test error")
        assert isinstance(error, SPIError)

    def test_can_be_caught_as_protocol_handler_error(self) -> None:
        """HandlerDiscoveryError can be caught as ProtocolHandlerError."""
        with pytest.raises(ProtocolHandlerError):
            raise HandlerDiscoveryError("Test")

    def test_can_be_caught_as_spi_error(self) -> None:
        """HandlerDiscoveryError can be caught as SPIError."""
        with pytest.raises(SPIError):
            raise HandlerDiscoveryError("Test")


@pytest.mark.unit
class TestHandlerDiscoveryErrorConstruction:
    """Test HandlerDiscoveryError construction."""

    def test_construction_with_message_only(self) -> None:
        """HandlerDiscoveryError can be constructed with message only."""
        error = HandlerDiscoveryError("Handler discovery failed")
        assert str(error) == "Handler discovery failed"

    def test_construction_with_empty_message(self) -> None:
        """HandlerDiscoveryError can be constructed with empty message."""
        error = HandlerDiscoveryError("")
        assert str(error) == ""

    def test_construction_with_message_and_context(self) -> None:
        """HandlerDiscoveryError can be constructed with message and context."""
        context = {
            "source_type": "CONTRACT",
            "search_paths": ["/etc/handlers/"],
            "handler_type": "http",
        }
        error = HandlerDiscoveryError("Discovery failed", context=context)
        assert str(error) == "Discovery failed"
        assert error.context == context

    def test_construction_with_none_context(self) -> None:
        """HandlerDiscoveryError with None context should have empty dict."""
        error = HandlerDiscoveryError("Test", context=None)
        assert error.context == {}

    def test_construction_with_empty_context(self) -> None:
        """HandlerDiscoveryError can have empty context dict."""
        error = HandlerDiscoveryError("Test", context={})
        assert error.context == {}


@pytest.mark.unit
class TestHandlerDiscoveryErrorContext:
    """Test HandlerDiscoveryError context handling."""

    def test_context_is_stored(self) -> None:
        """Context should be stored and accessible."""
        context = {
            "source_type": "BOOTSTRAP",
            "handler_count": 0,
        }
        error = HandlerDiscoveryError("No handlers found", context=context)
        assert error.context["source_type"] == "BOOTSTRAP"
        assert error.context["handler_count"] == 0

    def test_context_is_copied(self) -> None:
        """Context should be copied, not referenced."""
        context = {"key": "original"}
        error = HandlerDiscoveryError("Test", context=context)

        # Modify original context
        context["key"] = "modified"

        # Error context should still have original value
        assert error.context["key"] == "original"

    def test_context_supports_nested_structures(self) -> None:
        """Context can contain nested structures."""
        context = {
            "errors": [
                {"file": "handler1.yaml", "error": "parse error"},
                {"file": "handler2.yaml", "error": "missing field"},
            ],
            "config": {
                "search_paths": ["/etc/handlers/", "/opt/handlers/"],
                "recursive": True,
            },
        }
        error = HandlerDiscoveryError("Multiple discovery errors", context=context)

        assert len(error.context["errors"]) == 2
        assert error.context["config"]["recursive"] is True

    def test_context_can_contain_various_types(self) -> None:
        """Context can contain various value types."""
        context: dict[str, Any] = {
            "string_value": "text",
            "int_value": 42,
            "float_value": 3.14,
            "bool_value": True,
            "none_value": None,
            "list_value": [1, 2, 3],
            "dict_value": {"nested": "value"},
        }
        error = HandlerDiscoveryError("Test", context=context)

        assert error.context["string_value"] == "text"
        assert error.context["int_value"] == 42
        assert error.context["float_value"] == 3.14
        assert error.context["bool_value"] is True
        assert error.context["none_value"] is None
        assert error.context["list_value"] == [1, 2, 3]
        assert error.context["dict_value"]["nested"] == "value"


@pytest.mark.unit
class TestHandlerDiscoveryErrorUsagePatterns:
    """Test common usage patterns for HandlerDiscoveryError."""

    def test_raise_with_source_type_context(self) -> None:
        """Raise with source type in context."""
        with pytest.raises(HandlerDiscoveryError) as exc_info:
            raise HandlerDiscoveryError(
                "Failed to discover handlers from CONTRACT source",
                context={
                    "source_type": "CONTRACT",
                    "manifest_path": "/etc/handlers/manifest.yaml",
                },
            )

        assert exc_info.value.context["source_type"] == "CONTRACT"

    def test_raise_with_search_path_context(self) -> None:
        """Raise with search paths in context."""
        with pytest.raises(HandlerDiscoveryError) as exc_info:
            raise HandlerDiscoveryError(
                "No handler manifests found",
                context={
                    "search_paths": ["/etc/handlers/", "/opt/handlers/"],
                    "patterns": ["*.yaml", "*.yml"],
                },
            )

        paths = exc_info.value.context["search_paths"]
        assert "/etc/handlers/" in paths
        assert "/opt/handlers/" in paths

    def test_raise_with_handler_type_context(self) -> None:
        """Raise with handler type in context."""
        with pytest.raises(HandlerDiscoveryError) as exc_info:
            raise HandlerDiscoveryError(
                "Handler type 'kafka' not supported",
                context={
                    "handler_type": "kafka",
                    "supported_types": ["http", "grpc", "websocket"],
                },
            )

        assert exc_info.value.context["handler_type"] == "kafka"
        assert "http" in exc_info.value.context["supported_types"]

    def test_raise_with_original_error_context(self) -> None:
        """Raise with original error information in context."""
        original_error = ValueError("Invalid YAML syntax")

        with pytest.raises(HandlerDiscoveryError) as exc_info:
            raise HandlerDiscoveryError(
                "Failed to parse handler manifest",
                context={
                    "source_type": "CONTRACT",
                    "file_path": "/etc/handlers/invalid.yaml",
                    "original_error": str(original_error),
                    "error_type": type(original_error).__name__,
                },
            )

        assert exc_info.value.context["error_type"] == "ValueError"
        assert "Invalid YAML syntax" in exc_info.value.context["original_error"]

    def test_layered_exception_handling(self) -> None:
        """HandlerDiscoveryError fits in layered exception handling."""
        error_handled_by: str | None = None

        try:
            raise HandlerDiscoveryError(
                "Discovery failed",
                context={"source_type": "CONTRACT"},
            )
        except HandlerDiscoveryError:
            # Most specific - handle discovery errors
            error_handled_by = "HandlerDiscoveryError"
        except ProtocolHandlerError:
            # Less specific - handle any handler errors
            error_handled_by = "ProtocolHandlerError"
        except SPIError:
            # Least specific - handle any SPI errors
            error_handled_by = "SPIError"

        assert error_handled_by == "HandlerDiscoveryError"

    def test_caught_as_protocol_handler_error_preserves_context(self) -> None:
        """Context is preserved when caught as parent exception type."""
        captured_context: dict[str, Any] = {}

        try:
            raise HandlerDiscoveryError(
                "Discovery failed",
                context={"source_type": "HYBRID", "count": 42},
            )
        except ProtocolHandlerError as e:
            captured_context = e.context

        assert captured_context["source_type"] == "HYBRID"
        assert captured_context["count"] == 42


@pytest.mark.unit
class TestHandlerDiscoveryErrorDocumentation:
    """Test HandlerDiscoveryError documentation."""

    def test_exception_has_docstring(self) -> None:
        """HandlerDiscoveryError should have a docstring."""
        assert HandlerDiscoveryError.__doc__ is not None
        assert len(HandlerDiscoveryError.__doc__.strip()) > 0

    def test_docstring_mentions_discovery(self) -> None:
        """Docstring should mention discovery."""
        doc = HandlerDiscoveryError.__doc__ or ""
        assert "discover" in doc.lower()

    def test_docstring_mentions_handler_source(self) -> None:
        """Docstring should mention handler source."""
        doc = HandlerDiscoveryError.__doc__ or ""
        assert "handler" in doc.lower() and "source" in doc.lower()

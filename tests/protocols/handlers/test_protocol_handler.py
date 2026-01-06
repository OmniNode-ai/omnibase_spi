"""
Tests for ProtocolHandler protocol.

Validates that ProtocolHandler:
- Is properly runtime checkable
- Defines required methods (initialize, shutdown, execute, describe, health_check)
- Has required property (handler_type)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from omnibase_core.enums import (
    EnumHandlerRole,
    EnumHandlerType as CoreEnumHandlerType,
    EnumHandlerTypeCategory,
)
from omnibase_core.models.handlers import ModelHandlerDescriptor, ModelIdentifier
from omnibase_core.models.primitives.model_semver import ModelSemVer
from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler

# Type aliases for forward references used in test mocks
# These represent omnibase_core models that implementations would use
# Using 'object' as a placeholder since SPI tests should not import from core
ModelConnectionConfig = object
ModelProtocolRequest = object
ModelOperationConfig = object
ModelProtocolResponse = object
EnumHandlerType = object  # Mock for handler type enum


def create_mock_descriptor(
    name: str = "mock-handler",
    namespace: str = "test",
) -> ModelHandlerDescriptor:
    """Create a mock ModelHandlerDescriptor for testing."""
    return ModelHandlerDescriptor(
        handler_name=ModelIdentifier(namespace=namespace, name=name),
        handler_version=ModelSemVer(major=1, minor=0, patch=0),
        handler_role=EnumHandlerRole.INFRA_HANDLER,
        handler_type=CoreEnumHandlerType.NAMED,
        handler_type_category=EnumHandlerTypeCategory.EFFECT,
    )


class CompliantHandler:
    """A class that fully implements the ProtocolHandler protocol."""

    @property
    def handler_type(self) -> "EnumHandlerType":
        """Return the handler type."""
        return MagicMock()

    async def initialize(self, _config: "ModelConnectionConfig") -> None:
        """Initialize the handler."""
        pass

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown the handler."""
        pass

    async def execute(
        self,
        _request: "ModelProtocolRequest",
        _operation_config: "ModelOperationConfig",
    ) -> "ModelProtocolResponse":
        """Execute a protocol operation."""
        return MagicMock()

    def describe(self) -> ModelHandlerDescriptor:
        """Return handler metadata."""
        return create_mock_descriptor(name="compliant-handler")

    async def health_check(self) -> dict[str, Any]:
        """Check handler health."""
        return {"healthy": True}


class PartialHandler:
    """A class that only implements some ProtocolHandler methods."""

    async def initialize(self, _config: "ModelConnectionConfig") -> None:
        """Initialize the handler."""
        pass


class NonCompliantHandler:
    """A class that implements none of the ProtocolHandler methods."""

    pass


class WrongSignatureHandler:
    """A class that implements methods with wrong signatures."""

    @property
    def handler_type(self) -> "EnumHandlerType":
        """Return the handler type."""
        return MagicMock()

    async def initialize(self) -> None:  # type: ignore[override]
        """Initialize with wrong signature (missing config parameter)."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the handler."""
        pass

    async def execute(
        self,
        _request: "ModelProtocolRequest",
        _operation_config: "ModelOperationConfig",
    ) -> "ModelProtocolResponse":
        """Execute a protocol operation."""
        return MagicMock()

    def describe(self) -> ModelHandlerDescriptor:
        """Return handler metadata."""
        return create_mock_descriptor(name="wrong-signature-handler")

    async def health_check(self) -> dict[str, Any]:
        """Check handler health."""
        return {"healthy": True}


class TestProtocolHandlerProtocol:
    """Test suite for ProtocolHandler protocol compliance."""

    def test_protocol_handler_is_runtime_checkable(self) -> None:
        """ProtocolHandler should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolHandler, "_is_runtime_protocol") or hasattr(
            ProtocolHandler, "__runtime_protocol__"
        )

    def test_protocol_handler_is_protocol(self) -> None:
        """ProtocolHandler should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolHandler has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolHandler.__mro__
        )

    def test_protocol_handler_has_initialize_method(self) -> None:
        """ProtocolHandler should define initialize method."""
        assert "initialize" in dir(ProtocolHandler)

    def test_protocol_handler_has_shutdown_method(self) -> None:
        """ProtocolHandler should define shutdown method."""
        assert "shutdown" in dir(ProtocolHandler)

    def test_protocol_handler_has_execute_method(self) -> None:
        """ProtocolHandler should define execute method."""
        assert "execute" in dir(ProtocolHandler)

    def test_protocol_handler_has_handler_type_property(self) -> None:
        """ProtocolHandler should define handler_type property."""
        assert "handler_type" in dir(ProtocolHandler)

    def test_protocol_handler_has_describe_method(self) -> None:
        """ProtocolHandler should define describe method."""
        assert "describe" in dir(ProtocolHandler)

    def test_protocol_handler_has_health_check_method(self) -> None:
        """ProtocolHandler should define health_check method."""
        assert "health_check" in dir(ProtocolHandler)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolHandler protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolHandler()  # type: ignore[misc]


class TestProtocolHandlerCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolHandler methods should pass isinstance check."""
        handler = CompliantHandler()
        assert isinstance(handler, ProtocolHandler)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolHandler methods should fail isinstance check."""
        handler = PartialHandler()
        assert not isinstance(handler, ProtocolHandler)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolHandler methods should fail isinstance check."""
        handler = NonCompliantHandler()
        assert not isinstance(handler, ProtocolHandler)

    def test_wrong_signature_still_passes_structural_check(self) -> None:
        """
        A class with methods of wrong signatures still passes isinstance.

        Note: Runtime protocol checking only verifies method existence,
        not signature correctness. Signature checking is enforced by static analysis tools.
        """
        handler = WrongSignatureHandler()
        # Runtime check passes because methods exist (structural typing)
        assert isinstance(handler, ProtocolHandler)


class TestProtocolHandlerMethodSignatures:
    """Test method signatures from compliant implementations."""

    @pytest.mark.asyncio
    async def test_initialize_accepts_config(self) -> None:
        """initialize method should accept ModelConnectionConfig."""
        from unittest.mock import MagicMock

        handler = CompliantHandler()
        config = MagicMock()
        # Should not raise
        await handler.initialize(config)

    @pytest.mark.asyncio
    async def test_shutdown_takes_no_args(self) -> None:
        """shutdown method should take no arguments."""
        handler = CompliantHandler()
        # Should not raise
        await handler.shutdown()

    @pytest.mark.asyncio
    async def test_execute_accepts_request_and_config(self) -> None:
        """execute method should accept request and operation_config."""
        from unittest.mock import MagicMock

        handler = CompliantHandler()
        request = MagicMock()
        operation_config = MagicMock()
        # Should not raise and return a response
        response = await handler.execute(request, operation_config)
        assert response is not None

    @pytest.mark.asyncio
    async def test_execute_returns_response(self) -> None:
        """execute method should return ModelProtocolResponse."""
        handler = CompliantHandler()
        request = MagicMock()
        operation_config = MagicMock()
        response = await handler.execute(request, operation_config)
        # Verify we get something back
        assert response is not None

    def test_handler_type_returns_value(self) -> None:
        """handler_type property should return a value."""
        handler = CompliantHandler()
        handler_type = handler.handler_type
        assert handler_type is not None

    def test_describe_returns_model_handler_descriptor(self) -> None:
        """describe method should return a ModelHandlerDescriptor."""
        handler = CompliantHandler()
        metadata = handler.describe()
        assert isinstance(metadata, ModelHandlerDescriptor)
        assert metadata.handler_name is not None
        assert metadata.handler_type is not None

    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self) -> None:
        """health_check method should return a dictionary with health status."""
        handler = CompliantHandler()
        health = await handler.health_check()
        assert isinstance(health, dict)
        assert "healthy" in health


class TestProtocolHandlerAsyncNature:
    """Test that ProtocolHandler methods are async."""

    def test_initialize_is_async(self) -> None:
        """initialize should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.initialize)

    def test_shutdown_is_async(self) -> None:
        """shutdown should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.shutdown)

    def test_execute_is_async(self) -> None:
        """execute should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.execute)

    def test_health_check_is_async(self) -> None:
        """health_check should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantHandler.health_check)

    def test_describe_is_sync(self) -> None:
        """describe should be a sync method (not async)."""
        import inspect

        assert not inspect.iscoroutinefunction(CompliantHandler.describe)


class TestProtocolHandlerImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_handler_module(self) -> None:
        """Test direct import from protocol_handler module."""
        from omnibase_spi.protocols.handlers.protocol_handler import (
            ProtocolHandler as DirectProtocolHandler,
        )

        handler = CompliantHandler()
        assert isinstance(handler, DirectProtocolHandler)

    def test_import_from_handlers_package(self) -> None:
        """Test import from handlers package."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandler as HandlersProtocolHandler,
        )

        handler = CompliantHandler()
        assert isinstance(handler, HandlersProtocolHandler)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.handlers import (
            ProtocolHandler as HandlersProtocolHandler,
        )
        from omnibase_spi.protocols.handlers.protocol_handler import (
            ProtocolHandler as DirectProtocolHandler,
        )

        assert HandlersProtocolHandler is DirectProtocolHandler


class TestProtocolHandlerDocumentation:
    """Test that ProtocolHandler has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolHandler should have a docstring."""
        assert ProtocolHandler.__doc__ is not None
        assert len(ProtocolHandler.__doc__.strip()) > 0

    def test_initialize_has_docstring(self) -> None:
        """initialize method should have a docstring."""
        # Access through protocol's __annotations__ or compliant implementation
        assert CompliantHandler.initialize.__doc__ is not None

    def test_shutdown_has_docstring(self) -> None:
        """shutdown method should have a docstring."""
        assert CompliantHandler.shutdown.__doc__ is not None

    def test_execute_has_docstring(self) -> None:
        """execute method should have a docstring."""
        assert CompliantHandler.execute.__doc__ is not None

    def test_describe_has_docstring(self) -> None:
        """describe method should have a docstring."""
        assert CompliantHandler.describe.__doc__ is not None

    def test_health_check_has_docstring(self) -> None:
        """health_check method should have a docstring."""
        assert CompliantHandler.health_check.__doc__ is not None

    def test_handler_type_has_docstring(self) -> None:
        """handler_type property should have a docstring."""
        # Access the fget from the property descriptor on the class
        prop = CompliantHandler.__dict__["handler_type"]
        assert prop.fget.__doc__ is not None


class TestProtocolHandlerDescribeReturnContract:
    """Test return value contracts for ProtocolHandler.describe() method."""

    def test_describe_returns_model_handler_descriptor(self) -> None:
        """describe() must return ModelHandlerDescriptor."""
        handler = CompliantHandler()
        result = handler.describe()

        assert isinstance(result, ModelHandlerDescriptor)

    def test_describe_has_handler_type(self) -> None:
        """describe() result should have handler_type field."""
        handler = CompliantHandler()
        result = handler.describe()

        assert result.handler_type is not None
        assert isinstance(result.handler_type, CoreEnumHandlerType)

    def test_describe_has_handler_name(self) -> None:
        """describe() result should have handler_name with namespace and name."""
        handler = CompliantHandler()
        result = handler.describe()

        assert result.handler_name is not None
        assert isinstance(result.handler_name, ModelIdentifier)
        assert result.handler_name.namespace is not None
        assert result.handler_name.name is not None

    def test_describe_has_handler_version(self) -> None:
        """describe() result should have handler_version as ModelSemVer."""
        handler = CompliantHandler()
        result = handler.describe()

        assert result.handler_version is not None
        assert isinstance(result.handler_version, ModelSemVer)

    def test_describe_has_required_enum_fields(self) -> None:
        """describe() result should have required enum fields."""
        handler = CompliantHandler()
        result = handler.describe()

        assert result.handler_role is not None
        assert isinstance(result.handler_role, EnumHandlerRole)
        assert result.handler_type_category is not None
        assert isinstance(result.handler_type_category, EnumHandlerTypeCategory)

    def test_describe_capabilities_is_list(self) -> None:
        """describe() capabilities should be a list."""
        handler = CompliantHandler()
        result = handler.describe()

        assert isinstance(result.capabilities, list)


class TestProtocolHandlerHealthCheckReturnContract:
    """Test return value contracts for ProtocolHandler.health_check() method."""

    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self) -> None:
        """health_check() must return dict[str, Any]."""
        handler = CompliantHandler()
        result = await handler.health_check()

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_health_check_contains_healthy_key(self) -> None:
        """health_check() must contain 'healthy' key."""
        handler = CompliantHandler()
        result = await handler.health_check()

        assert "healthy" in result

    @pytest.mark.asyncio
    async def test_health_check_healthy_is_boolean(self) -> None:
        """health_check() 'healthy' value must be boolean."""
        handler = CompliantHandler()
        result = await handler.health_check()

        assert isinstance(result["healthy"], bool)

    @pytest.mark.asyncio
    async def test_health_check_latency_ms_is_numeric_when_present(self) -> None:
        """health_check() 'latency_ms' should be numeric when present."""
        handler = CompliantHandler()
        result = await handler.health_check()

        if "latency_ms" in result:
            assert isinstance(
                result["latency_ms"], (int, float)
            ), f"latency_ms should be numeric, got {type(result['latency_ms'])}"

    @pytest.mark.asyncio
    async def test_health_check_last_error_is_string_when_present(self) -> None:
        """health_check() 'last_error' should be string when present."""
        handler = CompliantHandler()
        result = await handler.health_check()

        if "last_error" in result:
            assert isinstance(
                result["last_error"], str
            ), f"last_error should be string, got {type(result['last_error'])}"

    @pytest.mark.asyncio
    async def test_health_check_details_is_dict_when_present(self) -> None:
        """health_check() 'details' should be dict when present."""
        handler = CompliantHandler()
        result = await handler.health_check()

        if "details" in result:
            assert isinstance(
                result["details"], dict
            ), f"details should be dict, got {type(result['details'])}"


class UnhealthyHandler(CompliantHandler):
    """Handler implementation that returns unhealthy status for testing."""

    async def health_check(self) -> dict[str, Any]:
        """Return unhealthy status with error details."""
        return {
            "healthy": False,
            "latency_ms": 5000.0,
            "last_error": "Connection timeout to database",
            "details": {"attempt_count": 3, "last_attempt": "2024-01-01T00:00:00Z"},
        }


class UnsanitizedHandler(CompliantHandler):
    """Handler that returns unsanitized error for negative testing.

    This handler intentionally includes sensitive credential patterns
    in its error response to verify that sanitization tests correctly
    detect such violations.
    """

    async def health_check(self) -> dict[str, Any]:
        """Return unhealthy status with unsanitized credentials in error."""
        return {
            "healthy": False,
            "latency_ms": 100.0,
            "last_error": "Connection to postgresql://admin:password=secret@host:5432/db failed",
            "details": {
                "connection_string": "redis://user:token=abc123@cache:6379",
                "api_endpoint": "https://api.example.com?api_key=sk-12345",
            },
        }


class UnsanitizedStackTraceHandler(CompliantHandler):
    """Handler that returns error with stack trace and system info.

    This handler demonstrates another common sanitization violation:
    exposing internal file paths and stack traces that reveal system structure.
    """

    async def health_check(self) -> dict[str, Any]:
        """Return unhealthy status with system paths and stack trace."""
        return {
            "healthy": False,
            "latency_ms": 50.0,
            "last_error": (
                "Error at /home/user/.config/secrets/db.json:42 - "
                "File /etc/passwd referenced in config"
            ),
            "details": {
                "stack_trace": (
                    "at process_request (/app/src/handlers/auth.py:128)\n"
                    "at validate_token (/app/src/auth/jwt_secret.py:45)"
                ),
                "config_path": "/opt/app/config/credentials.yaml",
            },
        }


class TestProtocolHandlerHealthCheckUnhealthyContract:
    """Test return value contracts for unhealthy handler scenarios."""

    @pytest.mark.asyncio
    async def test_unhealthy_handler_returns_false_healthy(self) -> None:
        """Unhealthy handler should return healthy=False."""
        handler = UnhealthyHandler()
        result = await handler.health_check()

        assert result["healthy"] is False

    @pytest.mark.asyncio
    async def test_unhealthy_handler_includes_last_error(self) -> None:
        """Unhealthy handler should include last_error string."""
        handler = UnhealthyHandler()
        result = await handler.health_check()

        assert "last_error" in result
        assert isinstance(result["last_error"], str)
        assert len(result["last_error"]) > 0

    @pytest.mark.asyncio
    async def test_unhealthy_handler_error_is_sanitized(self) -> None:
        """Unhealthy handler last_error should not contain credentials."""
        handler = UnhealthyHandler()
        result = await handler.health_check()

        error_msg = result.get("last_error", "")
        # Check that error message doesn't contain typical credential patterns
        forbidden_patterns = ["password=", "api_key=", "secret=", "token=", "://user:"]
        for pattern in forbidden_patterns:
            assert (
                pattern.lower() not in error_msg.lower()
            ), f"Credential pattern '{pattern}' found in error message"


class TestProtocolHandlerSanitizationDetection:
    """Test suite for sanitization detection in health_check responses.

    These tests verify that our sanitization checks correctly identify
    credential patterns, connection strings, and sensitive system information
    in handler responses. This includes negative tests to ensure the detection
    logic actually works.
    """

    # Common forbidden patterns for credential detection
    CREDENTIAL_PATTERNS = [
        "password=",
        "api_key=",
        "secret=",
        "token=",
        "://user:",
        "://admin:",
        "auth_token=",
        "private_key=",
        "access_key=",
        "secret_key=",
    ]

    # Patterns for sensitive file paths
    SENSITIVE_PATH_PATTERNS = [
        "/etc/passwd",
        "/etc/shadow",
        ".ssh/",
        "credentials.",
        "secrets/",
        ".config/secrets",
    ]

    def _check_for_credential_patterns(self, text: str) -> list[str]:
        """Check text for credential patterns and return any found."""
        found: list[str] = []
        text_lower = text.lower()
        for pattern in self.CREDENTIAL_PATTERNS:
            if pattern.lower() in text_lower:
                found.append(pattern)
        return found

    def _check_for_sensitive_paths(self, text: str) -> list[str]:
        """Check text for sensitive path patterns and return any found."""
        found: list[str] = []
        text_lower = text.lower()
        for pattern in self.SENSITIVE_PATH_PATTERNS:
            if pattern.lower() in text_lower:
                found.append(pattern)
        return found

    @pytest.mark.asyncio
    async def test_unsanitized_error_is_detected(self) -> None:
        """Verify test correctly identifies unsanitized credential patterns.

        This is a negative test that ensures our detection logic works by
        using a handler that intentionally contains forbidden patterns.
        """
        handler = UnsanitizedHandler()
        result = await handler.health_check()

        error_msg = result.get("last_error", "")
        # This handler intentionally has unsanitized data - verify detection works
        found_patterns = self._check_for_credential_patterns(error_msg)
        assert len(found_patterns) > 0, (
            "Test setup error: UnsanitizedHandler should contain forbidden patterns. "
            f"Error message was: {error_msg}"
        )

    @pytest.mark.asyncio
    async def test_sanitized_handler_passes_all_checks(self) -> None:
        """Verify properly sanitized handler passes all credential checks."""
        handler = UnhealthyHandler()
        result = await handler.health_check()

        error_msg = result.get("last_error", "")
        found_patterns = self._check_for_credential_patterns(error_msg)
        assert len(found_patterns) == 0, (
            f"Sanitized handler should not contain credential patterns. "
            f"Found: {found_patterns}"
        )

    @pytest.mark.asyncio
    async def test_connection_string_credentials_detected(self) -> None:
        """Verify connection strings with embedded credentials are detected.

        Connection strings like postgresql://user:pass@host are a common
        source of credential leaks in error messages.
        """
        handler = UnsanitizedHandler()
        result = await handler.health_check()

        error_msg = result.get("last_error", "")
        # Check for common connection string credential patterns
        connection_patterns = ["://admin:", "://user:"]
        detected = any(pattern in error_msg.lower() for pattern in connection_patterns)

        # Also check the details for nested credential exposure
        details = result.get("details", {})
        details_str = str(details).lower()
        details_detected = any(
            pattern in details_str for pattern in connection_patterns
        )

        assert (
            detected or details_detected
        ), "UnsanitizedHandler should contain connection string credentials"

    @pytest.mark.asyncio
    async def test_api_key_in_url_detected(self) -> None:
        """Verify API keys in URL query parameters are detected."""
        handler = UnsanitizedHandler()
        result = await handler.health_check()

        details = result.get("details", {})
        details_str = str(details).lower()

        assert (
            "api_key=" in details_str
        ), "UnsanitizedHandler details should contain api_key pattern"

    @pytest.mark.asyncio
    async def test_sensitive_file_paths_detected(self) -> None:
        """Verify sensitive file paths in error messages are detected."""
        handler = UnsanitizedStackTraceHandler()
        result = await handler.health_check()

        error_msg = result.get("last_error", "")
        found_paths = self._check_for_sensitive_paths(error_msg)

        assert len(found_paths) > 0, (
            f"UnsanitizedStackTraceHandler should contain sensitive paths. "
            f"Error message was: {error_msg}"
        )

    @pytest.mark.asyncio
    async def test_stack_trace_with_paths_detected(self) -> None:
        """Verify stack traces with internal paths are detected."""
        handler = UnsanitizedStackTraceHandler()
        result = await handler.health_check()

        details = result.get("details", {})
        stack_trace = details.get("stack_trace", "")

        # Stack traces should not expose internal application structure
        internal_path_indicators = ["/app/src/", "/opt/app/", ".py:"]
        detected = any(
            indicator in stack_trace for indicator in internal_path_indicators
        )

        assert (
            detected
        ), "UnsanitizedStackTraceHandler should contain internal paths in stack trace"

    @pytest.mark.asyncio
    async def test_config_path_exposure_detected(self) -> None:
        """Verify config file paths are detected in details."""
        handler = UnsanitizedStackTraceHandler()
        result = await handler.health_check()

        details = result.get("details", {})
        config_path = details.get("config_path", "")

        # Config paths should not expose credential file locations
        credential_file_indicators = ["credentials", "secrets", "config"]
        detected = any(
            indicator in config_path.lower() for indicator in credential_file_indicators
        )

        assert detected, "UnsanitizedStackTraceHandler should expose config paths"

    @pytest.mark.asyncio
    async def test_healthy_handler_is_clean(self) -> None:
        """Verify healthy handler has no sensitive data exposure."""
        handler = CompliantHandler()
        result = await handler.health_check()

        # Healthy handlers typically have minimal output
        assert result.get("healthy") is True
        assert "last_error" not in result or result.get("last_error") == ""

    @pytest.mark.asyncio
    async def test_multiple_credential_types_detected(self) -> None:
        """Verify detection works for multiple credential types in same response."""
        handler = UnsanitizedHandler()
        result = await handler.health_check()

        # Collect all text from the response
        all_text = str(result).lower()

        # Count how many different credential patterns are present
        patterns_found = self._check_for_credential_patterns(all_text)

        # UnsanitizedHandler should have multiple credential patterns
        assert (
            len(patterns_found) >= 2
        ), f"Expected multiple credential patterns, found: {patterns_found}"

    @pytest.mark.asyncio
    async def test_nested_details_are_checked(self) -> None:
        """Verify sanitization checks work on nested details dictionaries."""
        handler = UnsanitizedHandler()
        result = await handler.health_check()

        details = result.get("details", {})
        assert isinstance(details, dict)

        # Check each value in details for credential patterns
        for key, value in details.items():
            value_str = str(value).lower()
            for pattern in self.CREDENTIAL_PATTERNS:
                if pattern.lower() in value_str:
                    # Found a credential pattern in nested details - test passes
                    return

        pytest.fail("UnsanitizedHandler details should contain credential patterns")

"""
Core Protocol Validator for ONEX SPI.

This module provides the foundational validation infrastructure for protocol
implementations. It uses Python's built-in inspection and typing capabilities
to validate protocol conformance at runtime during development.

Key Features:
- Runtime protocol validation using isinstance and hasattr checks
- Method signature validation using inspect module
- Type annotation validation for protocol compliance
- Clear, actionable error messages for developers
- Zero external dependencies (maintains SPI purity)
- Development-focused validation (not production runtime)
"""

import inspect
import typing
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, get_type_hints

if TYPE_CHECKING:
    from typing_extensions import Protocol
else:
    try:
        from typing import Protocol
    except ImportError:
        from typing_extensions import Protocol

from omnibase.protocols.types.core_types import ContextValue


class ValidationError:
    """
    Represents a single validation error with context.

    Attributes:
        error_type: Type of validation error (missing_method, type_mismatch, etc.)
        message: Human-readable error description
        context: Additional context information for debugging
        severity: Error severity level (error, warning, info)
    """

    def __init__(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
    ):
        self.error_type = error_type
        self.message = message
        self.context = context or {}
        self.severity = severity

    def __str__(self) -> str:
        context_str = ""
        if self.context:
            context_items = [f"{k}={v}" for k, v in self.context.items()]
            context_str = f" ({', '.join(context_items)})"

        return (
            f"[{self.severity.upper()}] {self.error_type}: {self.message}{context_str}"
        )


class ValidationResult:
    """
    Result of protocol validation containing errors and metadata.

    Attributes:
        is_valid: True if validation passed without errors
        errors: List of validation errors found
        warnings: List of validation warnings
        protocol_name: Name of the validated protocol
        implementation_name: Name of the implementation being validated
    """

    def __init__(self, protocol_name: str, implementation_name: str):
        self.protocol_name = protocol_name
        self.implementation_name = implementation_name
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors, warnings are acceptable)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation produced warnings."""
        return len(self.warnings) > 0

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error."""
        self.errors.append(error)

    def add_warning(self, warning: ValidationError) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        status = "VALID" if self.is_valid else "INVALID"
        error_count = len(self.errors)
        warning_count = len(self.warnings)

        summary = f"Protocol validation: {status}\n"
        summary += f"Protocol: {self.protocol_name}\n"
        summary += f"Implementation: {self.implementation_name}\n"
        summary += f"Errors: {error_count}, Warnings: {warning_count}\n"

        if self.errors:
            summary += "\nErrors:\n"
            for i, error in enumerate(self.errors, 1):
                summary += f"  {i}. {error}\n"

        if self.warnings:
            summary += "\nWarnings:\n"
            for i, warning in enumerate(self.warnings, 1):
                summary += f"  {i}. {warning}\n"

        return summary


class ProtocolValidator:
    """
    Core protocol validator for ONEX SPI protocols.

    This validator provides comprehensive validation of protocol implementations
    using Python's introspection capabilities. It validates:
    - Method presence and signatures
    - Type annotations and return types
    - Protocol inheritance and structure
    - Runtime checkable protocol compliance

    Usage:
        validator = ProtocolValidator()
        result = validator.validate_implementation(my_instance, MyProtocol)

        if not result.is_valid:
            print(result.get_summary())
            for error in result.errors:
                print(f"Error: {error}")
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize protocol validator.

        Args:
            strict_mode: If True, perform comprehensive validation including
                       type annotations and method signatures. If False, only
                       check basic method presence.
        """
        self.strict_mode = strict_mode

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ValidationResult:
        """
        Validate an implementation against a protocol.

        Args:
            implementation: The implementation instance to validate
            protocol: The protocol class to validate against

        Returns:
            ValidationResult containing validation errors and warnings
        """
        protocol_name = (
            protocol.__name__ if hasattr(protocol, "__name__") else str(protocol)
        )
        impl_name = (
            implementation.__class__.__name__
            if hasattr(implementation, "__class__")
            else str(type(implementation))
        )

        result = ValidationResult(protocol_name, impl_name)

        # Check if protocol is runtime checkable
        self._validate_runtime_checkable(protocol, result)

        # Basic isinstance check for runtime checkable protocols
        if (
            hasattr(protocol, "__runtime_checkable__")
            and protocol.__runtime_checkable__
        ):
            if not isinstance(implementation, protocol):
                result.add_error(
                    ValidationError(
                        "protocol_compliance",
                        f"Implementation does not satisfy protocol {protocol_name}",
                        {"protocol": protocol_name, "implementation": impl_name},
                    )
                )

        # Validate protocol methods
        self._validate_protocol_methods(implementation, protocol, result)

        # Validate type annotations if in strict mode
        if self.strict_mode:
            self._validate_type_annotations(implementation, protocol, result)

        return result

    def _validate_runtime_checkable(
        self, protocol: Any, result: ValidationResult
    ) -> None:
        """Validate that protocol is properly configured for runtime checking."""
        if not hasattr(protocol, "__runtime_checkable__"):
            result.add_warning(
                ValidationError(
                    "runtime_checkable",
                    f"Protocol {protocol.__name__} is not decorated with @runtime_checkable",
                    {"protocol": protocol.__name__},
                    severity="warning",
                )
            )
        elif not protocol.__runtime_checkable__:
            result.add_warning(
                ValidationError(
                    "runtime_checkable",
                    f"Protocol {protocol.__name__} has __runtime_checkable__ = False",
                    {"protocol": protocol.__name__},
                    severity="warning",
                )
            )

    def _validate_protocol_methods(
        self, implementation: Any, protocol: Any, result: ValidationResult
    ) -> None:
        """Validate that all protocol methods are implemented."""
        protocol_methods = self._get_protocol_methods(protocol)

        for method_name, method_info in protocol_methods.items():
            if not hasattr(implementation, method_name):
                result.add_error(
                    ValidationError(
                        "missing_method",
                        f"Implementation missing required method '{method_name}'",
                        {"method": method_name, "protocol": protocol.__name__},
                    )
                )
                continue

            impl_method = getattr(implementation, method_name)

            # Check if it's callable
            if not callable(impl_method):
                result.add_error(
                    ValidationError(
                        "not_callable",
                        f"Attribute '{method_name}' exists but is not callable",
                        {"method": method_name, "type": type(impl_method).__name__},
                    )
                )
                continue

            # Validate method signature in strict mode
            if self.strict_mode:
                self._validate_method_signature(
                    impl_method, method_info, method_name, result
                )

    def _validate_type_annotations(
        self, implementation: Any, protocol: Any, result: ValidationResult
    ) -> None:
        """Validate type annotations match protocol requirements."""
        try:
            protocol_hints = get_type_hints(protocol)
            impl_hints = get_type_hints(type(implementation))

            # Check for missing type annotations
            for attr_name, expected_type in protocol_hints.items():
                if attr_name not in impl_hints:
                    result.add_warning(
                        ValidationError(
                            "missing_annotation",
                            f"Implementation missing type annotation for '{attr_name}'",
                            {
                                "attribute": attr_name,
                                "expected_type": str(expected_type),
                            },
                            severity="warning",
                        )
                    )
                else:
                    # Basic type compatibility check
                    impl_type = impl_hints[attr_name]
                    if not self._types_compatible(impl_type, expected_type):
                        result.add_warning(
                            ValidationError(
                                "type_mismatch",
                                f"Type annotation mismatch for '{attr_name}': expected {expected_type}, got {impl_type}",
                                {
                                    "attribute": attr_name,
                                    "expected": str(expected_type),
                                    "actual": str(impl_type),
                                },
                                severity="warning",
                            )
                        )

        except Exception as e:
            result.add_warning(
                ValidationError(
                    "annotation_validation_error",
                    f"Could not validate type annotations: {str(e)}",
                    {"error": str(e)},
                    severity="warning",
                )
            )

    def _validate_method_signature(
        self,
        impl_method: Any,
        protocol_method: Any,
        method_name: str,
        result: ValidationResult,
    ) -> None:
        """Validate that method signatures are compatible."""
        try:
            impl_sig = inspect.signature(impl_method)
            protocol_sig = inspect.signature(protocol_method)

            # Compare parameter counts (allowing for self parameter)
            impl_params = list(impl_sig.parameters.values())
            protocol_params = list(protocol_sig.parameters.values())

            # Remove 'self' parameter for comparison
            if impl_params and impl_params[0].name == "self":
                impl_params = impl_params[1:]
            if protocol_params and protocol_params[0].name == "self":
                protocol_params = protocol_params[1:]

            if len(impl_params) != len(protocol_params):
                result.add_warning(
                    ValidationError(
                        "parameter_count_mismatch",
                        f"Method '{method_name}' parameter count mismatch: expected {len(protocol_params)}, got {len(impl_params)}",
                        {
                            "method": method_name,
                            "expected": len(protocol_params),
                            "actual": len(impl_params),
                        },
                        severity="warning",
                    )
                )

            # Check parameter names and types
            for i, (impl_param, protocol_param) in enumerate(
                zip(impl_params, protocol_params)
            ):
                if impl_param.name != protocol_param.name:
                    result.add_warning(
                        ValidationError(
                            "parameter_name_mismatch",
                            f"Method '{method_name}' parameter {i} name mismatch: expected '{protocol_param.name}', got '{impl_param.name}'",
                            {
                                "method": method_name,
                                "parameter": i,
                                "expected": protocol_param.name,
                                "actual": impl_param.name,
                            },
                            severity="warning",
                        )
                    )

        except Exception as e:
            result.add_warning(
                ValidationError(
                    "signature_validation_error",
                    f"Could not validate signature for method '{method_name}': {str(e)}",
                    {"method": method_name, "error": str(e)},
                    severity="warning",
                )
            )

    def _get_protocol_methods(self, protocol: Any) -> Dict[str, Any]:
        """Extract methods from a protocol definition."""
        methods = {}

        for name in dir(protocol):
            if name.startswith("_"):
                continue

            attr = getattr(protocol, name)
            if inspect.isfunction(attr) or inspect.ismethod(attr):
                methods[name] = attr
            elif hasattr(attr, "__call__"):
                methods[name] = attr

        return methods

    def _types_compatible(self, impl_type: Any, expected_type: Any) -> bool:
        """Check if implementation type is compatible with expected protocol type."""
        # Basic compatibility check - this could be enhanced for more sophisticated type checking
        try:
            # Handle simple cases
            if impl_type == expected_type:
                return True

            # Handle Union types, Optional, etc. - basic checks only
            if hasattr(expected_type, "__origin__"):
                return True  # Skip complex generic type checking for now

            if hasattr(impl_type, "__origin__"):
                return True  # Skip complex generic type checking for now

            return False
        except Exception:
            return True  # If we can't determine compatibility, assume it's OK


def validate_protocol_implementation(
    implementation: Any, protocol: Any, strict_mode: bool
) -> ValidationResult:
    """
    Convenience function to validate a protocol implementation.

    Args:
        implementation: The implementation instance to validate
        protocol: The protocol class to validate against
        strict_mode: Whether to perform strict validation

    Returns:
        ValidationResult containing validation results

    Usage:
        result = validate_protocol_implementation(my_container, ProtocolArtifactContainer)
        if not result.is_valid:
            print(result.get_summary())
    """
    validator = ProtocolValidator(strict_mode=strict_mode)
    return validator.validate_implementation(implementation, protocol)

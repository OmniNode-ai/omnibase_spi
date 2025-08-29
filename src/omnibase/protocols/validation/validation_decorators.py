"""
Validation Decorators for ONEX SPI Protocol Implementations.

This module provides decorators and utilities to enable automatic protocol validation
during development. The decorators can be applied to classes or methods to ensure
protocol compliance at runtime.

Key Features:
- Class-level protocol validation decorators
- Method-level validation decorators
- Development-time validation (disabled in production)
- Clear validation error reporting
- Integration with ONEX error handling patterns
- Zero external dependencies (maintains SPI purity)
"""

import functools
import warnings
from typing import Any, Callable, TypeVar, Union
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from .protocol_validator import ProtocolValidator, ValidationResult

# Type variables for generic decorator support  
T = TypeVar('T')
P = TypeVar('P')


class ProtocolValidationError(Exception):
    """
    Exception raised when protocol validation fails.
    
    This exception is raised during development when a class or method
    fails protocol validation checks. It includes the validation result
    for detailed error information.
    """
    
    def __init__(self, validation_result: ValidationResult):
        self.validation_result = validation_result
        super().__init__(validation_result.get_summary())


def validation_decorator(
    protocol: Any, 
    strict_mode: bool = True,
    raise_on_error: bool = False,
    development_only: bool = True
) -> Callable[[Any], Any]:
    """
    Class decorator for protocol validation.
    
    This decorator validates that a class properly implements a protocol
    when the class is instantiated. It's designed for development-time
    validation to catch protocol misuse early.
    
    Args:
        protocol: The protocol class to validate against
        strict_mode: Whether to perform strict validation (type checking, etc.)
        raise_on_error: Whether to raise an exception on validation failure
        development_only: Whether to only validate in development mode
        
    Returns:
        Decorated class with validation
        
    Usage:
        @validation_decorator(ProtocolArtifactContainer)
        class MyArtifactContainer:
            def get_status(self) -> ProtocolArtifactContainerStatus:
                # Implementation...
                pass
            
            def get_artifacts(self) -> List[ProtocolArtifactInfo]:
                # Implementation...
                pass
        
        # Validation occurs when class is instantiated
        container = MyArtifactContainer()  # Validates against protocol
    """
    def decorator(cls: Any) -> Any:
        original_init = cls.__init__
        
        @functools.wraps(original_init)
        def validated_init(self, *args, **kwargs):
            # Call original __init__ first
            original_init(self, *args, **kwargs)
            
            # Skip validation in production if development_only is True
            if development_only and not _is_development_mode():
                return
            
            # Perform protocol validation
            validator = ProtocolValidator(strict_mode=strict_mode)
            result = validator.validate_implementation(self, protocol)
            
            # Handle validation results
            if not result.is_valid:
                error_message = f"Protocol validation failed for {cls.__name__}:\n{result.get_summary()}"
                
                if raise_on_error:
                    raise ProtocolValidationError(result)
                else:
                    warnings.warn(error_message, UserWarning, stacklevel=2)
                    print(f"[PROTOCOL VALIDATION] {error_message}")
            
            elif result.has_warnings:
                warning_message = f"Protocol validation warnings for {cls.__name__}:\n{result.get_summary()}"
                warnings.warn(warning_message, UserWarning, stacklevel=2)
        
        cls.__init__ = validated_init
        cls._protocol_validation_info = {
            'protocol': protocol,
            'strict_mode': strict_mode,
            'raise_on_error': raise_on_error
        }
        
        return cls
    
    return decorator


def validate_method_protocol(
    expected_signature: Callable,
    validate_return_type: bool = True,
    development_only: bool = True
) -> Callable:
    """
    Method decorator for protocol method validation.
    
    This decorator validates that a method signature and return type
    match the expected protocol specification.
    
    Args:
        expected_signature: The expected method signature from protocol
        validate_return_type: Whether to validate return type
        development_only: Whether to only validate in development mode
        
    Returns:
        Method decorator
        
    Usage:
        class MyImplementation:
            @validate_method_protocol(ProtocolArtifactContainer.get_status)
            def get_status(self) -> ProtocolArtifactContainerStatus:
                # Implementation validates against protocol method
                return self._create_status()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Skip validation in production if development_only is True
            if development_only and not _is_development_mode():
                return func(*args, **kwargs)
            
            # Validate method signature (basic check)
            result = _validate_method_signature(func, expected_signature)
            
            if not result.is_valid:
                warning_message = f"Method signature validation failed for {func.__name__}:\n{result.get_summary()}"
                warnings.warn(warning_message, UserWarning, stacklevel=2)
            
            # Call the original method
            return_value = func(*args, **kwargs)
            
            # Validate return type if requested
            if validate_return_type:
                _validate_return_type(return_value, expected_signature, func.__name__)
            
            return return_value
        
        wrapper._protocol_validation_info = {
            'expected_signature': expected_signature,
            'validate_return_type': validate_return_type
        }
        
        return wrapper
    
    return decorator


def validate_protocol_implementation(
    implementation: Any, 
    protocol: Any, 
    strict_mode: bool = True,
    print_results: bool = True
) -> ValidationResult:
    """
    Standalone function to validate protocol implementation.
    
    This is a convenience function that can be called manually to validate
    any implementation against a protocol. Useful for testing or manual
    validation during development.
    
    Args:
        implementation: The implementation instance to validate
        protocol: The protocol to validate against
        strict_mode: Whether to perform strict validation
        print_results: Whether to print validation results
        
    Returns:
        ValidationResult with detailed validation information
        
    Usage:
        class MyContainer:
            def get_status(self):
                return "active"
        
        container = MyContainer()
        result = validate_protocol_implementation(container, ProtocolArtifactContainer)
        
        if not result.is_valid:
            print("Validation failed!")
            for error in result.errors:
                print(f"  - {error}")
    """
    validator = ProtocolValidator(strict_mode=strict_mode)
    result = validator.validate_implementation(implementation, protocol)
    
    if print_results:
        print(result.get_summary())
        
        if not result.is_valid:
            print("\nValidation Errors:")
            for error in result.errors:
                print(f"  • {error}")
        
        if result.has_warnings:
            print("\nValidation Warnings:")
            for warning in result.warnings:
                print(f"  • {warning}")
    
    return result


def enable_protocol_validation(enabled: bool = True) -> None:
    """
    Enable or disable protocol validation globally.
    
    This function allows you to enable or disable protocol validation
    at runtime. Useful for development vs production environments.
    
    Args:
        enabled: Whether to enable protocol validation
        
    Usage:
        # Enable validation for development
        enable_protocol_validation(True)
        
        # Disable validation for production
        enable_protocol_validation(False)
    """
    global _PROTOCOL_VALIDATION_ENABLED
    _PROTOCOL_VALIDATION_ENABLED = enabled


def is_protocol_validation_enabled() -> bool:
    """
    Check if protocol validation is currently enabled.
    
    Returns:
        True if protocol validation is enabled
    """
    return getattr(globals(), '_PROTOCOL_VALIDATION_ENABLED', True)


# Private helper functions

def _is_development_mode() -> bool:
    """
    Determine if we're running in development mode.
    
    This function tries to detect development vs production environment
    using common indicators.
    """
    import os
    
    # Check common development environment indicators
    dev_indicators = [
        os.getenv('ENVIRONMENT', '').lower() in ['dev', 'development', 'local'],
        os.getenv('DEBUG', '').lower() in ['true', '1', 'yes'],
        os.getenv('ONEX_ENV', '').lower() in ['dev', 'development'],
        '__debug__' in globals() and __debug__,  # Python debug mode
    ]
    
    return any(dev_indicators)


def _validate_method_signature(func: Callable, expected_func: Callable) -> ValidationResult:
    """Validate that a method signature matches expected signature."""
    import inspect
    
    func_name = getattr(func, '__name__', 'unknown')
    result = ValidationResult('method_signature', func_name)
    
    try:
        func_sig = inspect.signature(func)
        expected_sig = inspect.signature(expected_func)
        
        # Basic parameter count comparison
        func_params = list(func_sig.parameters.values())
        expected_params = list(expected_sig.parameters.values())
        
        # Remove 'self' parameter for comparison
        if func_params and func_params[0].name == 'self':
            func_params = func_params[1:]
        if expected_params and expected_params[0].name == 'self':
            expected_params = expected_params[1:]
        
        if len(func_params) != len(expected_params):
            from .protocol_validator import ValidationError
            result.add_error(ValidationError(
                "parameter_count_mismatch",
                f"Parameter count mismatch: expected {len(expected_params)}, got {len(func_params)}",
                {"expected": len(expected_params), "actual": len(func_params)}
            ))
    
    except Exception as e:
        from .protocol_validator import ValidationError
        result.add_warning(ValidationError(
            "signature_validation_error",
            f"Could not validate method signature: {str(e)}",
            {"error": str(e)},
            severity="warning"
        ))
    
    return result


def _validate_return_type(return_value: Any, expected_func: Callable, func_name: str) -> None:
    """Validate return type against expected function return type."""
    # Basic return type validation - could be enhanced
    if return_value is None:
        warnings.warn(f"Method {func_name} returned None", UserWarning)


# Global validation state
_PROTOCOL_VALIDATION_ENABLED = True
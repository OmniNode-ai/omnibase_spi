# Validation Protocols API Reference

## Overview

The ONEX validation protocols provide comprehensive type-safe validation capabilities for protocol compliance, input validation, and data integrity checking. These protocols enable robust validation workflows with detailed error reporting, custom validation decorators, and sophisticated validation result handling for distributed systems.

## Protocol Architecture

The validation domain consists of specialized protocols that provide complete validation capabilities:

### Validation Error Protocol

```python
from omnibase_spi.protocols.validation import ProtocolValidationError

@runtime_checkable
class ProtocolValidationError(Protocol):
    """
    Protocol for validation error objects.

    Provides structured error information with context and severity
    for comprehensive error reporting and handling.

    Features:
        - Structured error categorization
        - Contextual error information
        - Severity-based error handling
        - Human-readable error messages
        - Machine-readable error data
    """

    error_type: str
    message: str
    context: Dict[str, Any]
    severity: str

    def __str__(self) -> str:
        """
        Return string representation of the error.

        Returns:
            Human-readable error description
        """
        ...
```

### Validation Result Protocol

```python
from omnibase_spi.protocols.validation import ProtocolValidationResult

@runtime_checkable
class ProtocolValidationResult(Protocol):
    """
    Protocol for validation result objects.

    Comprehensive validation results with error collection,
    warning management, and summary reporting capabilities.

    Features:
        - Success/failure status tracking
        - Error and warning collection
        - Protocol and implementation identification
        - Detailed validation summaries
        - Extensible result context
    """

    is_valid: bool
    protocol_name: str
    implementation_name: str
    errors: List[ProtocolValidationError]
    warnings: List[ProtocolValidationError]

    def add_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
    ) -> None:
        """
        Add a validation error to the result.

        Args:
            error_type: Category/type of validation error
            message: Human-readable error description
            context: Additional error context data
            severity: Error severity level
        """
        ...

    def add_warning(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a validation warning to the result.

        Args:
            error_type: Category/type of validation warning
            message: Human-readable warning description
            context: Additional warning context data
        """
        ...

    def get_summary(self) -> str:
        """
        Get a comprehensive summary of validation results.

        Returns:
            Formatted summary string with error and warning details
        """
        ...
```

### Validation Protocol

```python
from omnibase_spi.protocols.validation import ProtocolValidator

@runtime_checkable
class ProtocolValidator(Protocol):
    """
    Protocol for comprehensive validation functionality.

    Core validation engine that checks protocol compliance,
    validates implementations, and provides detailed validation results.

    Features:
        - Protocol compliance validation
        - Implementation verification
        - Method signature checking
        - Type compatibility validation
        - Comprehensive error reporting
        - Configurable validation strictness
    """

    strict_mode: bool

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """
        Validate an implementation against a protocol.

        Performs comprehensive validation including:
        - Method presence and signature validation
        - Property existence and type checking
        - Protocol compliance verification
        - Implementation completeness assessment

        Args:
            implementation: The implementation instance to validate
            protocol: The protocol class to validate against

        Returns:
            ProtocolValidationResult with detailed validation information

        Raises:
            ValidationError: If validation configuration is invalid
        """
        ...
```

### Validation Decorator Protocol

```python
from omnibase_spi.protocols.validation import ProtocolValidationDecorator

@runtime_checkable
class ProtocolValidationDecorator(Protocol):
    """
    Protocol for validation decorator functionality.

    Provides decorators and utilities for automatic protocol validation
    with runtime compliance checking and validation result caching.

    Features:
        - Automatic protocol validation decorators
        - Runtime compliance checking
        - Validation result caching
        - Configurable validation behavior
        - Integration with dependency injection
    """

    def validate_protocol_implementation(
        self, implementation: Any, protocol: Any, strict: bool = True
    ) -> ProtocolValidationResult:
        """
        Validate protocol implementation with configurable strictness.

        Args:
            implementation: Implementation to validate
            protocol: Protocol to validate against
            strict: Enable strict validation mode

        Returns:
            ProtocolValidationResult with validation details
        """
        ...

    def validation_decorator(self, protocol: Any) -> Any:
        """
        Create decorator for automatic protocol validation.

        Args:
            protocol: Protocol class to validate implementations against

        Returns:
            Decorator function for class or method validation
        """
        ...
```

## Type Definitions

### Validation Types

```python
# Type aliases for backward compatibility and convenience
ValidationError = ProtocolValidationError
ValidationResult = ProtocolValidationResult

# Validation severity levels
ValidationSeverity = Literal["error", "warning", "info", "critical"]

# Validation categories
ValidationCategory = Literal[
    "protocol_compliance",
    "method_signature",
    "property_type",
    "implementation_completeness",
    "runtime_behavior",
    "performance",
    "security"
]

# Validation mode configuration
ValidationMode = Literal["strict", "lenient", "pedantic", "minimal"]
```

### Extended Validation Types

```python
from typing import TypedDict, Optional, List, Dict, Any

class ValidationContext(TypedDict, total=False):
    """Context information for validation operations."""

    file_path: Optional[str]
    line_number: Optional[int]
    method_name: Optional[str]
    expected_type: Optional[str]
    actual_type: Optional[str]
    additional_info: Dict[str, Any]

class ValidationConfig(TypedDict, total=False):
    """Configuration for validation operations."""

    strict_mode: bool
    check_method_signatures: bool
    check_property_types: bool
    check_runtime_behavior: bool
    allow_additional_methods: bool
    allow_missing_optional_methods: bool
    max_validation_time: float
    cache_validation_results: bool

class ValidationMetrics(TypedDict):
    """Metrics collected during validation."""

    total_methods_checked: int
    total_properties_checked: int
    validation_time_seconds: float
    cache_hits: int
    cache_misses: int
    error_count: int
    warning_count: int
```

## Usage Patterns

### Basic Protocol Validation

```python
from omnibase_spi.protocols.validation import ProtocolValidator
from omnibase_spi.protocols.file_handling import ProtocolFileTypeHandler

class BasicProtocolValidator:
    """Example implementation of protocol validator."""

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.validation_cache = {}

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """Validate implementation against protocol."""

        # Create result object
        result = ValidationResult(
            is_valid=True,
            protocol_name=protocol.__name__,
            implementation_name=implementation.__class__.__name__,
            errors=[],
            warnings=[]
        )

        try:
            # Check if implementation satisfies protocol
            if not isinstance(implementation, protocol):
                result.add_error(
                    error_type="protocol_compliance",
                    message=f"Implementation does not satisfy {protocol.__name__} protocol",
                    context={
                        "protocol": protocol.__name__,
                        "implementation": implementation.__class__.__name__,
                        "check_type": "isinstance"
                    },
                    severity="critical"
                )
                result.is_valid = False
                return result

            # Validate required methods
            self._validate_methods(implementation, protocol, result)

            # Validate required properties
            self._validate_properties(implementation, protocol, result)

            # Validate method signatures
            if self.strict_mode:
                self._validate_method_signatures(implementation, protocol, result)

        except Exception as e:
            result.add_error(
                error_type="validation_error",
                message=f"Validation failed with exception: {str(e)}",
                context={"exception_type": type(e).__name__},
                severity="critical"
            )
            result.is_valid = False

        return result

    def _validate_methods(
        self, implementation: Any, protocol: Any, result: ProtocolValidationResult
    ) -> None:
        """Validate required methods exist."""

        # Get protocol methods
        protocol_methods = [
            name for name, value in protocol.__annotations__.items()
            if callable(getattr(protocol, name, None))
        ]

        for method_name in protocol_methods:
            if not hasattr(implementation, method_name):
                result.add_error(
                    error_type="method_missing",
                    message=f"Required method '{method_name}' not found",
                    context={
                        "method_name": method_name,
                        "protocol": protocol.__name__
                    },
                    severity="error"
                )
                result.is_valid = False
            elif not callable(getattr(implementation, method_name)):
                result.add_error(
                    error_type="method_not_callable",
                    message=f"Method '{method_name}' exists but is not callable",
                    context={
                        "method_name": method_name,
                        "actual_type": type(getattr(implementation, method_name)).__name__
                    },
                    severity="error"
                )
                result.is_valid = False

    def _validate_properties(
        self, implementation: Any, protocol: Any, result: ProtocolValidationResult
    ) -> None:
        """Validate required properties exist."""

        # Get protocol properties
        protocol_properties = [
            name for name, value in protocol.__annotations__.items()
            if not callable(getattr(protocol, name, None))
        ]

        for prop_name in protocol_properties:
            if not hasattr(implementation, prop_name):
                result.add_error(
                    error_type="property_missing",
                    message=f"Required property '{prop_name}' not found",
                    context={
                        "property_name": prop_name,
                        "protocol": protocol.__name__
                    },
                    severity="error"
                )
                result.is_valid = False

    def _validate_method_signatures(
        self, implementation: Any, protocol: Any, result: ProtocolValidationResult
    ) -> None:
        """Validate method signatures match protocol."""

        import inspect

        # Get methods from both protocol and implementation
        protocol_methods = inspect.getmembers(protocol, predicate=inspect.isfunction)

        for method_name, protocol_method in protocol_methods:
            if not hasattr(implementation, method_name):
                continue  # Already handled in _validate_methods

            impl_method = getattr(implementation, method_name)

            try:
                # Compare signatures
                protocol_sig = inspect.signature(protocol_method)
                impl_sig = inspect.signature(impl_method)

                # Check parameter compatibility
                if not self._signatures_compatible(protocol_sig, impl_sig):
                    result.add_warning(
                        error_type="signature_mismatch",
                        message=f"Method '{method_name}' signature differs from protocol",
                        context={
                            "method_name": method_name,
                            "protocol_signature": str(protocol_sig),
                            "implementation_signature": str(impl_sig)
                        }
                    )

            except Exception as e:
                result.add_warning(
                    error_type="signature_check_failed",
                    message=f"Could not validate signature for '{method_name}': {str(e)}",
                    context={
                        "method_name": method_name,
                        "error": str(e)
                    }
                )

    def _signatures_compatible(self, protocol_sig: inspect.Signature, impl_sig: inspect.Signature) -> bool:
        """Check if implementation signature is compatible with protocol signature."""

        # Basic compatibility check - same number of parameters
        protocol_params = list(protocol_sig.parameters.keys())
        impl_params = list(impl_sig.parameters.keys())

        # Allow implementation to have additional optional parameters
        if len(impl_params) < len(protocol_params):
            return False

        # Check that all required protocol parameters are present
        for i, param_name in enumerate(protocol_params):
            if i >= len(impl_params):
                return False
            # Could add more sophisticated parameter type checking here

        return True

# Usage example
async def validate_file_handler():
    """Example of validating a file handler implementation."""

    validator = BasicProtocolValidator(strict_mode=True)

    # Create a file handler implementation
    class TestFileHandler:
        def __init__(self):
            self.node_name = "test_handler"
            self.supported_extensions = [".test"]
            self.node_priority = 10
            self.requires_content_analysis = False

        def can_handle(self, path, content):
            return Mock(can_handle=True, confidence=0.8, reason="Test handler")

        def extract_block(self, path, content):
            return Mock(content="test", file_metadata=Mock())

        def stamp(self, path, content, options):
            return Mock(success=True, message="Stamped successfully")

        def validate(self, path, content, options):
            return Mock(success=True, message="Validation passed")

        # Missing some required methods and properties for testing

    # Validate implementation
    handler = TestFileHandler()
    result = validator.validate_implementation(handler, ProtocolFileTypeHandler)

    print(f"Validation Result: {'PASS' if result.is_valid else 'FAIL'}")
    print(f"Protocol: {result.protocol_name}")
    print(f"Implementation: {result.implementation_name}")

    if result.errors:
        print(f"Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error.error_type}: {error.message}")

    if result.warnings:
        print(f"Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {warning.error_type}: {warning.message}")

    print(f"\nSummary:\n{result.get_summary()}")
```

### Advanced Validation with Caching

```python
import time
from typing import Tuple
import hashlib

class CachedProtocolValidator:
    """Protocol validator with result caching for performance."""

    def __init__(self, strict_mode: bool = True, cache_ttl: int = 300):
        self.strict_mode = strict_mode
        self.cache_ttl = cache_ttl
        self.validation_cache: Dict[str, Tuple[ProtocolValidationResult, float]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0
        }

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """Validate with caching support."""

        # Generate cache key
        cache_key = self._generate_cache_key(implementation, protocol)
        current_time = time.time()

        # Check cache
        if cache_key in self.validation_cache:
            cached_result, cache_time = self.validation_cache[cache_key]

            if current_time - cache_time < self.cache_ttl:
                self.cache_stats["hits"] += 1
                return cached_result
            else:
                # Cache expired
                del self.validation_cache[cache_key]
                self.cache_stats["invalidations"] += 1

        # Perform validation
        self.cache_stats["misses"] += 1
        result = self._perform_validation(implementation, protocol)

        # Cache result
        self.validation_cache[cache_key] = (result, current_time)

        return result

    def _generate_cache_key(self, implementation: Any, protocol: Any) -> str:
        """Generate unique cache key for implementation/protocol pair."""

        impl_info = {
            "class": implementation.__class__.__name__,
            "module": implementation.__class__.__module__,
            "methods": sorted([
                name for name in dir(implementation)
                if not name.startswith('_') and callable(getattr(implementation, name))
            ]),
            "properties": sorted([
                name for name in dir(implementation)
                if not name.startswith('_') and not callable(getattr(implementation, name))
            ])
        }

        protocol_info = {
            "name": protocol.__name__,
            "module": protocol.__module__,
            "strict_mode": self.strict_mode
        }

        cache_data = f"{impl_info}|{protocol_info}".encode()
        return hashlib.md5(cache_data).hexdigest()

    def _perform_validation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """Perform actual validation."""

        start_time = time.time()

        # Use the basic validator logic
        basic_validator = BasicProtocolValidator(self.strict_mode)
        result = basic_validator.validate_implementation(implementation, protocol)

        # Add timing information
        validation_time = time.time() - start_time

        if hasattr(result, 'context'):
            result.context["validation_time"] = validation_time

        return result

    def clear_cache(self) -> None:
        """Clear validation cache."""
        cleared_items = len(self.validation_cache)
        self.validation_cache.clear()
        self.cache_stats["invalidations"] += cleared_items

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "cache_invalidations": self.cache_stats["invalidations"],
            "hit_rate": hit_rate,
            "cache_size": len(self.validation_cache),
            "total_requests": total_requests
        }

# Usage
async def use_cached_validation():
    """Example using cached validation."""

    validator = CachedProtocolValidator(strict_mode=True, cache_ttl=60)

    # Create test implementations
    implementations = [TestFileHandler() for _ in range(10)]

    # First round of validations (cache misses)
    start_time = time.time()
    for impl in implementations:
        result = validator.validate_implementation(impl, ProtocolFileTypeHandler)
    first_round_time = time.time() - start_time

    # Second round of validations (cache hits)
    start_time = time.time()
    for impl in implementations:
        result = validator.validate_implementation(impl, ProtocolFileTypeHandler)
    second_round_time = time.time() - start_time

    # Show performance improvement
    print(f"First round (no cache): {first_round_time:.3f}s")
    print(f"Second round (cached): {second_round_time:.3f}s")
    print(f"Performance improvement: {first_round_time / second_round_time:.1f}x")

    # Show cache statistics
    cache_stats = validator.get_cache_stats()
    print(f"Cache Statistics:")
    print(f"  Hit rate: {cache_stats['hit_rate']:.1%}")
    print(f"  Total requests: {cache_stats['total_requests']}")
    print(f"  Cache size: {cache_stats['cache_size']}")
```

### Validation Decorators

```python
from functools import wraps
import warnings

class ValidationDecorator:
    """Decorator for automatic protocol validation."""

    def __init__(self, validator: ProtocolValidator = None):
        self.validator = validator or BasicProtocolValidator()
        self.validation_results = {}

    def validate_protocol_implementation(
        self, implementation: Any, protocol: Any, strict: bool = True
    ) -> ProtocolValidationResult:
        """Validate implementation with optional strictness override."""

        # Temporarily override strict mode if specified
        original_strict = self.validator.strict_mode
        self.validator.strict_mode = strict

        try:
            result = self.validator.validate_implementation(implementation, protocol)

            # Store result for later access
            key = (id(implementation), protocol.__name__)
            self.validation_results[key] = result

            return result
        finally:
            # Restore original strict mode
            self.validator.strict_mode = original_strict

    def validation_decorator(self, protocol: Any) -> Any:
        """Create validation decorator for a protocol."""

        def decorator(cls):
            """Class decorator that validates protocol compliance."""

            # Store original __init__
            original_init = cls.__init__

            @wraps(original_init)
            def validated_init(self, *args, **kwargs):
                # Call original __init__
                original_init(self, *args, **kwargs)

                # Validate protocol compliance
                result = self.validator.validate_implementation(self, protocol)

                if not result.is_valid:
                    error_summary = "; ".join([
                        f"{error.error_type}: {error.message}"
                        for error in result.errors
                    ])
                    raise ValueError(
                        f"Protocol validation failed for {cls.__name__}: {error_summary}"
                    )

                # Issue warnings for validation warnings
                if result.warnings:
                    warning_summary = "; ".join([
                        f"{warning.error_type}: {warning.message}"
                        for warning in result.warnings
                    ])
                    warnings.warn(
                        f"Protocol validation warnings for {cls.__name__}: {warning_summary}",
                        UserWarning,
                        stacklevel=2
                    )

            # Replace __init__ with validated version
            cls.__init__ = validated_init

            # Add validation metadata to class
            cls._protocol_validation_info = {
                "protocol": protocol,
                "validated": True,
                "validator": self.validator
            }

            return cls

        return decorator

    def method_validator(self, protocol_method: str):
        """Create method-level validation decorator."""

        def decorator(method):
            """Method decorator that validates method behavior."""

            @wraps(method)
            def validated_method(self, *args, **kwargs):
                # Validate method signature if possible
                # (This is a simplified example)

                # Call original method
                result = method(self, *args, **kwargs)

                # Could add post-execution validation here

                return result

            return validated_method

        return decorator

    def get_validation_result(self, implementation: Any, protocol_name: str) -> Optional[ProtocolValidationResult]:
        """Get stored validation result."""
        key = (id(implementation), protocol_name)
        return self.validation_results.get(key)

# Usage examples
async def use_validation_decorators():
    """Example using validation decorators."""

    decorator = ValidationDecorator()

    # Create protocol-validated class
    @decorator.validation_decorator(ProtocolFileTypeHandler)
    class ValidatedFileHandler:
        def __init__(self):
            self.node_name = "validated_handler"
            self.node_version = Mock()
            self.node_author = "Test Author"
            self.node_description = "Validated test handler"
            self.supported_extensions = [".test"]
            self.supported_filenames = []
            self.node_priority = 10
            self.requires_content_analysis = False
            self.metadata = Mock()

        def can_handle(self, path, content):
            return Mock(can_handle=True, confidence=0.8, reason="Test")

        def extract_block(self, path, content):
            return Mock(content="test")

        def serialize_block(self, meta):
            return Mock(serialized_data="test")

        def normalize_rest(self, rest):
            return rest

        def stamp(self, path, content, options):
            return Mock(success=True)

        def pre_validate(self, path, content, options):
            return None

        def post_validate(self, path, content, options):
            return None

        def validate(self, path, content, options):
            return Mock(success=True)

    try:
        # This will trigger validation during instantiation
        handler = ValidatedFileHandler()
        print("Handler created successfully - validation passed")

        # Get validation result
        result = decorator.get_validation_result(handler, "ProtocolFileTypeHandler")
        if result:
            print(f"Validation result: {result.get_summary()}")

    except ValueError as e:
        print(f"Validation failed: {e}")

# Method-level validation example
class AdvancedValidatedHandler:
    """Handler with method-level validation."""

    def __init__(self):
        self.decorator = ValidationDecorator()

    @ValidationDecorator().method_validator("can_handle")
    def can_handle(self, path, content):
        """Method with validation."""
        # Method implementation
        return Mock(can_handle=True, confidence=0.9, reason="Advanced handler")

    def validate_method_behavior(self, method_name: str, *args, **kwargs):
        """Validate method behavior dynamically."""
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            result = method(*args, **kwargs)

            # Perform post-execution validation
            if method_name == "can_handle":
                if not hasattr(result, 'can_handle'):
                    raise ValueError("can_handle must return object with can_handle attribute")
                if not isinstance(result.can_handle, bool):
                    raise ValueError("can_handle attribute must be boolean")
                if not hasattr(result, 'confidence'):
                    raise ValueError("can_handle must return object with confidence attribute")
                if not 0.0 <= result.confidence <= 1.0:
                    raise ValueError("confidence must be between 0.0 and 1.0")

            return result
        else:
            raise ValueError(f"Method {method_name} not found")
```

### Batch Validation

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

class BatchValidator:
    """Validator for processing multiple implementations in batch."""

    def __init__(self, validator: ProtocolValidator = None, max_workers: int = 4):
        self.validator = validator or CachedProtocolValidator()
        self.max_workers = max_workers
        self.batch_results = []

    async def validate_batch(
        self,
        implementations: List[Tuple[Any, Any]],  # (implementation, protocol) pairs
        parallel: bool = True
    ) -> List[ProtocolValidationResult]:
        """Validate multiple implementations in batch."""

        if parallel:
            return await self._validate_batch_parallel(implementations)
        else:
            return self._validate_batch_sequential(implementations)

    async def _validate_batch_parallel(
        self,
        implementations: List[Tuple[Any, Any]]
    ) -> List[ProtocolValidationResult]:
        """Validate implementations in parallel."""

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all validation tasks
            futures = [
                executor.submit(
                    self.validator.validate_implementation,
                    impl,
                    protocol
                )
                for impl, protocol in implementations
            ]

            # Collect results
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    results.append(result)
                except Exception as e:
                    # Create error result for failed validation
                    error_result = self._create_error_result(e)
                    results.append(error_result)

        self.batch_results.extend(results)
        return results

    def _validate_batch_sequential(
        self,
        implementations: List[Tuple[Any, Any]]
    ) -> List[ProtocolValidationResult]:
        """Validate implementations sequentially."""

        results = []
        for impl, protocol in implementations:
            try:
                result = self.validator.validate_implementation(impl, protocol)
                results.append(result)
            except Exception as e:
                error_result = self._create_error_result(e)
                results.append(error_result)

        self.batch_results.extend(results)
        return results

    def _create_error_result(self, exception: Exception) -> ProtocolValidationResult:
        """Create error result for failed validation."""

        error_result = ValidationResult(
            is_valid=False,
            protocol_name="unknown",
            implementation_name="unknown",
            errors=[],
            warnings=[]
        )

        error_result.add_error(
            error_type="validation_exception",
            message=f"Validation failed with exception: {str(exception)}",
            context={
                "exception_type": type(exception).__name__,
                "exception_message": str(exception)
            },
            severity="critical"
        )

        return error_result

    def get_batch_summary(self) -> Dict[str, Any]:
        """Get summary of batch validation results."""

        if not self.batch_results:
            return {"message": "No validations performed"}

        total_validations = len(self.batch_results)
        successful_validations = sum(1 for r in self.batch_results if r.is_valid)
        failed_validations = total_validations - successful_validations

        # Error analysis
        error_types = {}
        warning_types = {}

        for result in self.batch_results:
            for error in result.errors:
                error_types[error.error_type] = error_types.get(error.error_type, 0) + 1

            for warning in result.warnings:
                warning_types[warning.error_type] = warning_types.get(warning.error_type, 0) + 1

        return {
            "total_validations": total_validations,
            "successful_validations": successful_validations,
            "failed_validations": failed_validations,
            "success_rate": successful_validations / total_validations,
            "most_common_errors": sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_common_warnings": sorted(warning_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "error_distribution": error_types,
            "warning_distribution": warning_types
        }

    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report."""

        summary = self.get_batch_summary()

        report = []
        report.append("Batch Validation Report")
        report.append("=" * 50)
        report.append(f"Total validations: {summary['total_validations']}")
        report.append(f"Successful: {summary['successful_validations']}")
        report.append(f"Failed: {summary['failed_validations']}")
        report.append(f"Success rate: {summary['success_rate']:.1%}")
        report.append("")

        if summary['most_common_errors']:
            report.append("Most Common Errors:")
            for error_type, count in summary['most_common_errors']:
                report.append(f"  - {error_type}: {count} occurrences")
            report.append("")

        if summary['most_common_warnings']:
            report.append("Most Common Warnings:")
            for warning_type, count in summary['most_common_warnings']:
                report.append(f"  - {warning_type}: {count} occurrences")
            report.append("")

        # Detailed failure analysis
        failed_results = [r for r in self.batch_results if not r.is_valid]
        if failed_results:
            report.append("Failed Validations Details:")
            for i, result in enumerate(failed_results[:10], 1):  # Show first 10 failures
                report.append(f"  {i}. {result.implementation_name} -> {result.protocol_name}")
                for error in result.errors[:3]:  # Show first 3 errors
                    report.append(f"     - {error.error_type}: {error.message}")
                if len(result.errors) > 3:
                    report.append(f"     ... and {len(result.errors) - 3} more errors")
                report.append("")

        return "\n".join(report)

# Usage example
async def run_batch_validation():
    """Example of batch validation."""

    batch_validator = BatchValidator(max_workers=6)

    # Create test implementations
    implementations = []

    # Good implementations
    for i in range(5):
        impl = create_valid_handler(f"handler_{i}")
        implementations.append((impl, ProtocolFileTypeHandler))

    # Bad implementations (missing methods/properties)
    for i in range(3):
        impl = create_invalid_handler(f"bad_handler_{i}")
        implementations.append((impl, ProtocolFileTypeHandler))

    # Run batch validation
    start_time = time.time()
    results = await batch_validator.validate_batch(implementations, parallel=True)
    validation_time = time.time() - start_time

    print(f"Batch validation completed in {validation_time:.2f}s")

    # Get summary
    summary = batch_validator.get_batch_summary()
    print(f"Success rate: {summary['success_rate']:.1%}")

    # Generate detailed report
    report = batch_validator.generate_validation_report()
    print("\n" + report)

    return results

def create_valid_handler(name: str):
    """Create a valid handler implementation for testing."""

    class ValidHandler:
        def __init__(self):
            self.node_name = name
            self.node_version = Mock()
            self.node_author = "Test"
            self.node_description = f"Valid handler {name}"
            self.supported_extensions = [".test"]
            self.supported_filenames = []
            self.node_priority = 10
            self.requires_content_analysis = False
            self.metadata = Mock()

        # Implement all required methods
        def can_handle(self, path, content):
            return Mock(can_handle=True, confidence=0.8)

        def extract_block(self, path, content):
            return Mock(content="test")

        def serialize_block(self, meta):
            return Mock(serialized_data="test")

        def normalize_rest(self, rest):
            return rest

        def stamp(self, path, content, options):
            return Mock(success=True)

        def pre_validate(self, path, content, options):
            return None

        def post_validate(self, path, content, options):
            return None

        def validate(self, path, content, options):
            return Mock(success=True)

    return ValidHandler()

def create_invalid_handler(name: str):
    """Create an invalid handler implementation for testing."""

    class InvalidHandler:
        def __init__(self):
            self.node_name = name
            # Missing many required properties and methods

        def can_handle(self, path, content):
            return Mock(can_handle=True, confidence=0.5)

        # Missing most required methods

    return InvalidHandler()
```

## Advanced Features

### Custom Validation Rules

```python
from typing import Callable, List
from abc import ABC, abstractmethod

class ValidationRule(ABC):
    """Abstract base class for custom validation rules."""

    @abstractmethod
    def validate(
        self,
        implementation: Any,
        protocol: Any,
        context: Dict[str, Any]
    ) -> List[ProtocolValidationError]:
        """
        Validate implementation against custom rule.

        Args:
            implementation: Implementation to validate
            protocol: Protocol being validated against
            context: Validation context data

        Returns:
            List of validation errors (empty if validation passes)
        """
        pass

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable name for this validation rule."""
        pass

class MethodDocstringRule(ValidationRule):
    """Validation rule that checks for method docstrings."""

    @property
    def rule_name(self) -> str:
        return "method_docstring_check"

    def validate(
        self,
        implementation: Any,
        protocol: Any,
        context: Dict[str, Any]
    ) -> List[ProtocolValidationError]:
        """Check that all public methods have docstrings."""

        errors = []

        # Get all public methods
        methods = [
            (name, method) for name, method in inspect.getmembers(implementation, inspect.ismethod)
            if not name.startswith('_')
        ]

        for method_name, method in methods:
            if not method.__doc__ or not method.__doc__.strip():
                errors.append(
                    ValidationError(
                        error_type="missing_docstring",
                        message=f"Method '{method_name}' is missing docstring",
                        context={
                            "method_name": method_name,
                            "rule": self.rule_name
                        },
                        severity="warning"
                    )
                )

        return errors

class PerformanceRule(ValidationRule):
    """Validation rule that checks method performance."""

    def __init__(self, max_execution_time: float = 1.0):
        self.max_execution_time = max_execution_time

    @property
    def rule_name(self) -> str:
        return "performance_check"

    def validate(
        self,
        implementation: Any,
        protocol: Any,
        context: Dict[str, Any]
    ) -> List[ProtocolValidationError]:
        """Check method execution performance."""

        errors = []

        # Test critical methods for performance
        critical_methods = ['can_handle', 'extract_block', 'validate']

        for method_name in critical_methods:
            if hasattr(implementation, method_name):
                method = getattr(implementation, method_name)

                # Simple performance test
                try:
                    start_time = time.time()
                    # Call with dummy parameters
                    if method_name == 'can_handle':
                        method(Path("test.txt"), "test content")
                    elif method_name == 'extract_block':
                        method(Path("test.txt"), "test content")
                    elif method_name == 'validate':
                        method(Path("test.txt"), "test content", Mock())

                    execution_time = time.time() - start_time

                    if execution_time > self.max_execution_time:
                        errors.append(
                            ValidationError(
                                error_type="performance_violation",
                                message=f"Method '{method_name}' took {execution_time:.3f}s (limit: {self.max_execution_time}s)",
                                context={
                                    "method_name": method_name,
                                    "execution_time": execution_time,
                                    "limit": self.max_execution_time,
                                    "rule": self.rule_name
                                },
                                severity="warning"
                            )
                        )

                except Exception as e:
                    # Performance test failed
                    errors.append(
                        ValidationError(
                            error_type="performance_test_failed",
                            message=f"Performance test failed for '{method_name}': {str(e)}",
                            context={
                                "method_name": method_name,
                                "error": str(e),
                                "rule": self.rule_name
                            },
                            severity="info"
                        )
                    )

        return errors

class ExtensibleProtocolValidator(BasicProtocolValidator):
    """Protocol validator with support for custom validation rules."""

    def __init__(self, strict_mode: bool = True):
        super().__init__(strict_mode)
        self.custom_rules: List[ValidationRule] = []

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.custom_rules.append(rule)

    def remove_validation_rule(self, rule_name: str) -> bool:
        """Remove a validation rule by name."""
        for i, rule in enumerate(self.custom_rules):
            if rule.rule_name == rule_name:
                del self.custom_rules[i]
                return True
        return False

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """Validate with custom rules."""

        # Run base validation
        result = super().validate_implementation(implementation, protocol)

        # Run custom validation rules
        validation_context = {
            "protocol_name": protocol.__name__,
            "implementation_name": implementation.__class__.__name__,
            "strict_mode": self.strict_mode
        }

        for rule in self.custom_rules:
            try:
                rule_errors = rule.validate(implementation, protocol, validation_context)

                for error in rule_errors:
                    if error.severity == "error":
                        result.errors.append(error)
                        if result.is_valid:
                            result.is_valid = False
                    else:
                        result.warnings.append(error)

            except Exception as e:
                # Rule execution failed
                result.add_error(
                    error_type="rule_execution_failed",
                    message=f"Custom rule '{rule.rule_name}' failed: {str(e)}",
                    context={
                        "rule_name": rule.rule_name,
                        "error": str(e)
                    },
                    severity="warning"
                )

        return result

# Usage
async def use_custom_validation_rules():
    """Example using custom validation rules."""

    validator = ExtensibleProtocolValidator(strict_mode=True)

    # Add custom rules
    validator.add_validation_rule(MethodDocstringRule())
    validator.add_validation_rule(PerformanceRule(max_execution_time=0.1))

    # Create test implementation
    handler = TestFileHandler()

    # Validate with custom rules
    result = validator.validate_implementation(handler, ProtocolFileTypeHandler)

    print(f"Validation result: {'PASS' if result.is_valid else 'FAIL'}")

    if result.errors:
        print(f"Errors:")
        for error in result.errors:
            print(f"  - {error.error_type}: {error.message}")

    if result.warnings:
        print(f"Warnings:")
        for warning in result.warnings:
            print(f"  - {warning.error_type}: {warning.message}")
```

## Integration with Other Domains

### Event Bus Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

class EventDrivenValidator:
    """Validator that publishes validation events."""

    def __init__(self, validator: ProtocolValidator, event_bus: ProtocolEventBus):
        self.validator = validator
        self.event_bus = event_bus

    async def validate_with_events(
        self,
        implementation: Any,
        protocol: Any
    ) -> ProtocolValidationResult:
        """Validate and publish events."""

        # Publish validation started event
        await self.event_bus.publish_event(
            EventMessage(
                event_id=str(uuid4()),
                event_type="validation.started",
                payload={
                    "implementation": implementation.__class__.__name__,
                    "protocol": protocol.__name__
                },
                metadata=EventMetadata(source="validator"),
                timestamp=datetime.utcnow().isoformat()
            )
        )

        # Perform validation
        start_time = time.time()
        result = self.validator.validate_implementation(implementation, protocol)
        validation_time = time.time() - start_time

        # Publish completion event
        await self.event_bus.publish_event(
            EventMessage(
                event_id=str(uuid4()),
                event_type="validation.completed",
                payload={
                    "implementation": implementation.__class__.__name__,
                    "protocol": protocol.__name__,
                    "is_valid": result.is_valid,
                    "error_count": len(result.errors),
                    "warning_count": len(result.warnings),
                    "validation_time": validation_time
                },
                metadata=EventMetadata(source="validator"),
                timestamp=datetime.utcnow().isoformat()
            )
        )

        # Publish error events if validation failed
        if not result.is_valid:
            for error in result.errors:
                await self.event_bus.publish_event(
                    EventMessage(
                        event_id=str(uuid4()),
                        event_type="validation.error",
                        payload={
                            "implementation": implementation.__class__.__name__,
                            "protocol": protocol.__name__,
                            "error_type": error.error_type,
                            "error_message": error.message,
                            "severity": error.severity
                        },
                        metadata=EventMetadata(source="validator"),
                        timestamp=datetime.utcnow().isoformat()
                    )
                )

        return result
```

### Discovery Integration

```python
from omnibase_spi.protocols.discovery import ProtocolNodeDiscoveryRegistry

async def validate_discovered_handlers(
    discovery_registry: ProtocolNodeDiscoveryRegistry,
    validator: ProtocolValidator
) -> Dict[str, ProtocolValidationResult]:
    """Validate all discovered handlers."""

    # Discover handlers
    discovery_registry.discover_and_register_nodes()

    # Get discovered handlers (this would need to be implemented in registry)
    # discovered_handlers = discovery_registry.get_discovered_handlers()

    validation_results = {}

    # Validate each discovered handler
    # for handler_info in discovered_handlers:
    #     try:
    #         handler_instance = handler_info.node_class()
    #         result = validator.validate_implementation(
    #             handler_instance,
    #             ProtocolFileTypeHandler
    #         )
    #         validation_results[handler_info.name] = result
    #     except Exception as e:
    #         # Create error result for failed instantiation
    #         error_result = ValidationResult(
    #             is_valid=False,
    #             protocol_name="ProtocolFileTypeHandler",
    #             implementation_name=handler_info.name,
    #             errors=[],
    #             warnings=[]
    #         )
    #         error_result.add_error(
    #             "instantiation_failed",
    #             f"Failed to create handler instance: {str(e)}"
    #         )
    #         validation_results[handler_info.name] = error_result

    return validation_results
```

## Testing Strategies

### Validation Protocol Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestValidationProtocols:
    """Test suite for validation protocol compliance."""

    @pytest.fixture
    def basic_validator(self):
        """Create basic validator for testing."""
        return BasicProtocolValidator(strict_mode=True)

    @pytest.fixture
    def mock_valid_implementation(self):
        """Create mock valid implementation."""
        impl = Mock()
        impl.__class__.__name__ = "MockImplementation"
        impl.required_method = Mock()
        impl.required_property = "test_value"
        return impl

    @pytest.fixture
    def mock_invalid_implementation(self):
        """Create mock invalid implementation."""
        impl = Mock()
        impl.__class__.__name__ = "MockInvalidImplementation"
        # Missing required methods and properties
        return impl

    @pytest.fixture
    def mock_protocol(self):
        """Create mock protocol."""
        protocol = Mock()
        protocol.__name__ = "MockProtocol"
        protocol.__annotations__ = {
            "required_method": callable,
            "required_property": str
        }
        return protocol

    def test_valid_implementation(self, basic_validator, mock_valid_implementation, mock_protocol):
        """Test validation of valid implementation."""

        # Mock isinstance check to return True
        with patch('builtins.isinstance', return_value=True):
            result = basic_validator.validate_implementation(
                mock_valid_implementation,
                mock_protocol
            )

        assert isinstance(result, ProtocolValidationResult)
        assert result.is_valid is True
        assert result.protocol_name == "MockProtocol"
        assert result.implementation_name == "MockImplementation"

    def test_invalid_implementation(self, basic_validator, mock_invalid_implementation, mock_protocol):
        """Test validation of invalid implementation."""

        # Mock isinstance check to return False
        with patch('builtins.isinstance', return_value=False):
            result = basic_validator.validate_implementation(
                mock_invalid_implementation,
                mock_protocol
            )

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any(error.error_type == "protocol_compliance" for error in result.errors)

    def test_validation_caching(self):
        """Test validation result caching."""

        cached_validator = CachedProtocolValidator()
        impl = Mock()
        protocol = Mock()
        protocol.__name__ = "TestProtocol"

        # Mock validation to avoid complex setup
        with patch.object(cached_validator, '_perform_validation') as mock_validate:
            mock_result = Mock()
            mock_validate.return_value = mock_result

            # First validation (should call _perform_validation)
            result1 = cached_validator.validate_implementation(impl, protocol)

            # Second validation (should use cache)
            result2 = cached_validator.validate_implementation(impl, protocol)

            # Should only call _perform_validation once
            assert mock_validate.call_count == 1
            assert result1 is mock_result
            assert result2 is mock_result

    def test_batch_validation(self):
        """Test batch validation functionality."""

        batch_validator = BatchValidator()

        implementations = [
            (Mock(), Mock()),
            (Mock(), Mock()),
            (Mock(), Mock())
        ]

        with patch.object(batch_validator.validator, 'validate_implementation') as mock_validate:
            mock_validate.return_value = Mock(is_valid=True)

            # Run batch validation
            results = batch_validator._validate_batch_sequential(implementations)

            assert len(results) == 3
            assert mock_validate.call_count == 3

    async def test_validation_decorators(self):
        """Test validation decorators."""

        decorator = ValidationDecorator()

        # Mock validator
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_result.warnings = []
        mock_validator.validate_implementation.return_value = mock_result
        decorator.validator = mock_validator

        # Create decorated class
        @decorator.validation_decorator(Mock())
        class TestClass:
            def __init__(self):
                pass

        # Should not raise exception since validation passes
        instance = TestClass()
        assert instance is not None
```

## Performance Optimization

### Validation Performance Monitoring

```python
import psutil
import threading
from collections import defaultdict

class ValidationPerformanceMonitor:
    """Monitor validation performance and resource usage."""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.active_validations = 0
        self.lock = threading.Lock()

    def start_validation(self, validation_id: str) -> Dict[str, Any]:
        """Start monitoring a validation operation."""

        with self.lock:
            self.active_validations += 1

        start_metrics = {
            "validation_id": validation_id,
            "start_time": time.time(),
            "start_memory": psutil.Process().memory_info().rss,
            "start_cpu": psutil.Process().cpu_percent(),
            "thread_id": threading.get_ident()
        }

        return start_metrics

    def end_validation(self, start_metrics: Dict[str, Any], result: ProtocolValidationResult) -> None:
        """End monitoring and record metrics."""

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        end_cpu = psutil.Process().cpu_percent()

        with self.lock:
            self.active_validations -= 1

        validation_metrics = {
            "validation_id": start_metrics["validation_id"],
            "duration": end_time - start_metrics["start_time"],
            "memory_delta": end_memory - start_metrics["start_memory"],
            "cpu_usage": end_cpu,
            "is_valid": result.is_valid,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "thread_id": start_metrics["thread_id"]
        }

        self.metrics["validations"].append(validation_metrics)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""

        if not self.metrics["validations"]:
            return {"message": "No validations monitored"}

        validations = self.metrics["validations"]

        # Calculate statistics
        durations = [v["duration"] for v in validations]
        memory_deltas = [v["memory_delta"] for v in validations]

        return {
            "total_validations": len(validations),
            "active_validations": self.active_validations,
            "average_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "average_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "max_memory_delta": max(memory_deltas),
            "success_rate": sum(1 for v in validations if v["is_valid"]) / len(validations),
            "average_errors": sum(v["error_count"] for v in validations) / len(validations),
            "average_warnings": sum(v["warning_count"] for v in validations) / len(validations)
        }

class MonitoredValidator:
    """Validator with performance monitoring."""

    def __init__(self, base_validator: ProtocolValidator):
        self.base_validator = base_validator
        self.monitor = ValidationPerformanceMonitor()

    def validate_implementation(
        self, implementation: Any, protocol: Any
    ) -> ProtocolValidationResult:
        """Validate with performance monitoring."""

        validation_id = f"{implementation.__class__.__name__}_{protocol.__name__}_{time.time()}"
        start_metrics = self.monitor.start_validation(validation_id)

        try:
            result = self.base_validator.validate_implementation(implementation, protocol)
            self.monitor.end_validation(start_metrics, result)
            return result
        except Exception as e:
            # Create error result for monitoring
            error_result = ValidationResult(
                is_valid=False,
                protocol_name=protocol.__name__,
                implementation_name=implementation.__class__.__name__,
                errors=[],
                warnings=[]
            )
            error_result.add_error(
                "validation_exception",
                f"Validation failed: {str(e)}"
            )
            self.monitor.end_validation(start_metrics, error_result)
            raise

    def get_performance_report(self) -> str:
        """Get detailed performance report."""

        summary = self.monitor.get_performance_summary()

        if "message" in summary:
            return summary["message"]

        report = []
        report.append("Validation Performance Report")
        report.append("=" * 40)
        report.append(f"Total validations: {summary['total_validations']}")
        report.append(f"Active validations: {summary['active_validations']}")
        report.append(f"Success rate: {summary['success_rate']:.1%}")
        report.append("")
        report.append("Performance Metrics:")
        report.append(f"  Average duration: {summary['average_duration']:.3f}s")
        report.append(f"  Max duration: {summary['max_duration']:.3f}s")
        report.append(f"  Min duration: {summary['min_duration']:.3f}s")
        report.append("")
        report.append("Memory Usage:")
        report.append(f"  Average delta: {summary['average_memory_delta'] / 1024:.1f} KB")
        report.append(f"  Max delta: {summary['max_memory_delta'] / 1024:.1f} KB")
        report.append("")
        report.append("Error Analysis:")
        report.append(f"  Average errors per validation: {summary['average_errors']:.1f}")
        report.append(f"  Average warnings per validation: {summary['average_warnings']:.1f}")

        return "\n".join(report)

# Usage
async def use_performance_monitoring():
    """Example using performance monitoring."""

    base_validator = CachedProtocolValidator()
    monitored_validator = MonitoredValidator(base_validator)

    # Run multiple validations
    implementations = [create_valid_handler(f"handler_{i}") for i in range(10)]

    for impl in implementations:
        result = monitored_validator.validate_implementation(impl, ProtocolFileTypeHandler)

    # Get performance report
    report = monitored_validator.get_performance_report()
    print(report)
```

## Best Practices

### Validation Design Guidelines

1. **Comprehensive Coverage**: Validate all aspects of protocol compliance including methods, properties, and behavior
2. **Performance Awareness**: Use caching and efficient validation techniques for large-scale validation
3. **Detailed Reporting**: Provide specific, actionable error messages and validation context
4. **Extensibility**: Support custom validation rules and extensible validation frameworks
5. **Error Categorization**: Use consistent error types and severity levels for systematic handling
6. **Graceful Degradation**: Handle validation failures gracefully without disrupting system operation
7. **Monitoring Integration**: Include performance monitoring and metrics collection for validation operations

### Error Handling Best Practices

1. **Structured Errors**: Use structured error objects with consistent categorization and context
2. **Severity Levels**: Implement appropriate severity levels (critical, error, warning, info) for different validation issues
3. **Context Preservation**: Include detailed context information for debugging and troubleshooting
4. **Exception Safety**: Ensure validation operations never crash the system due to validation failures

The validation protocols provide comprehensive type-safe validation capabilities that ensure protocol compliance and data integrity across the entire ONEX distributed orchestration framework.

"""
Protocol Validation Utilities Module.

This module provides runtime validation helpers for protocol implementations in the
omnibase-spi project. These utilities are designed to catch protocol misuse early
during development, providing clear error messages and improving developer experience.

Key Features:
- Runtime protocol validation for development
- Clear, actionable error messages
- Integration with existing @runtime_checkable protocol system
- Zero external dependencies (SPI purity maintained)
- Optional validation decorators
- Type checking and method signature validation

Usage:
    ```python
    from omnibase.protocols.validation import (
        ProtocolValidator,
        validate_protocol_implementation,
        validation_decorator
    )

    # Validate a protocol implementation
    @validation_decorator(ProtocolArtifactContainer)
    class MyArtifactContainer:
        # Implementation...
        pass

    # Manual validation
    validator = ProtocolValidator()
    result = validator.validate_implementation(my_instance, ProtocolArtifactContainer)
    if not result.is_valid:
        print(f"Validation errors: {result.errors}")
    ```
"""

from .protocol_validator import ProtocolValidator, ValidationResult
from .validation_decorators import (
    validate_protocol_implementation,
    validation_decorator,
)
from .validators import (
    ArtifactContainerValidator,
    HandlerDiscoveryValidator,
    NodeRegistryValidator,
    ServiceRegistryValidator,
)

__all__ = [
    "ProtocolValidator",
    "ValidationResult",
    "validate_protocol_implementation",
    "validation_decorator",
    "ArtifactContainerValidator",
    "HandlerDiscoveryValidator",
    "NodeRegistryValidator",
    "ServiceRegistryValidator",
]

"""
Pure SPI Protocol Definitions for Validation.

This module provides only Protocol interface definitions for validation utilities,
following SPI purity principles. Concrete implementations have been moved to
utils/omnibase_spi_validation to maintain SPI architectural boundaries.

Key Features:
- Pure Protocol definitions for validation interfaces
- Zero concrete implementations (SPI purity maintained)
- Type-safe validation contracts  
- Framework-agnostic validation protocols

Usage:
    ```python
    from omnibase_spi.protocols.validation import (
        ProtocolValidator,
        ProtocolValidationResult, 
        ProtocolValidationDecorator
    )
    
    # Concrete implementations available in utils package:
    # from utils.omnibase_spi_validation import ProtocolValidator as ConcreteValidator
    ```

Note: This module contains ONLY Protocol definitions. For concrete implementations
that can be instantiated and used, import from utils.omnibase_spi_validation.
"""

from .protocol_validation import (
    ValidationError,  # Type alias for backward compatibility
)
from .protocol_validation import (
    ValidationResult,  # Type alias for backward compatibility
)
from .protocol_validation import (
    ProtocolValidationDecorator,
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)

__all__ = [
    "ProtocolValidationError",
    "ProtocolValidationResult",
    "ProtocolValidator",
    "ProtocolValidationDecorator",
    "ValidationError",  # Backward compatibility
    "ValidationResult",  # Backward compatibility
]

"""
Pure SPI Protocol Definitions for Validation.

This module provides Protocol interface definitions for validation utilities,
following SPI purity principles with proper duck typing for ONEX node validation.

Key Features:
- Pure Protocol definitions for validation interfaces
- Zero concrete implementations (SPI purity maintained)
- Type-safe validation contracts for ONEX 4-node architecture
- Framework-agnostic validation protocols with proper duck typing

Core Validation Protocols:
- ProtocolValidationResult: Standard validation result structure
- ProtocolValidator: Core validation interface
- ProtocolValidationError: Validation error representation
- ProtocolValidationDecorator: Validation decorator interface

ONEX Validation Node Protocols:
- ProtocolImportValidator: For NodeImportValidatorCompute implementations
- ProtocolValidationOrchestrator: For NodeValidationOrchestratorOrchestrator implementations

Usage:
    ```python
    from omnibase_spi.protocols.validation import (
        ProtocolValidationResult,
        ProtocolValidator,
        ProtocolImportValidator,
        ProtocolValidationOrchestrator,
    )

    # Concrete implementations will be available in omnibase_core nodes
    ```

Note: This module contains ONLY Protocol definitions. Concrete implementations
will be provided by ONEX validation nodes in omnibase_core.
"""

# Core validation protocols (from omnibase_core)
from omnibase_core.protocols.validation import (
    ProtocolValidationDecorator,
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)

# ONEX validation node protocols
from .protocol_import_validator import (
    ProtocolImportAnalysis,
    ProtocolImportValidationConfig,
    ProtocolImportValidator,
)

# Validation orchestrator protocols
from .protocol_validation_orchestrator import (
    ProtocolValidationMetrics,
    ProtocolValidationOrchestrator,
    ProtocolValidationReport,
    ProtocolValidationScope,
    ProtocolValidationSummary,
    ProtocolValidationWorkflow,
)

# Validation protocols moved from core
from .protocol_validation_provider import ProtocolValidationProvider

__all__ = [
    # Core validation protocols
    "ProtocolValidationDecorator",
    "ProtocolValidationError",
    "ProtocolValidationResult",
    "ProtocolValidator",
    # Import validation protocols
    "ProtocolImportAnalysis",
    "ProtocolImportValidationConfig",
    "ProtocolImportValidator",
    # Validation orchestrator protocols
    "ProtocolValidationMetrics",
    "ProtocolValidationOrchestrator",
    "ProtocolValidationProvider",
    "ProtocolValidationReport",
    "ProtocolValidationScope",
    "ProtocolValidationSummary",
    "ProtocolValidationWorkflow",
]

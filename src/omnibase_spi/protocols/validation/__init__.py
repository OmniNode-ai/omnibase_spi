"""
Pure SPI Protocol Definitions for Validation.

This module provides Protocol interface definitions for validation utilities,
following SPI purity principles with proper duck typing for ONEX node validation.

Key Features:
- Pure Protocol definitions for validation interfaces
- Zero concrete implementations (SPI purity maintained)
- Type-safe validation contracts for ONEX 4-node architecture
- Framework-agnostic validation protocols with proper duck typing

ONEX Validation Node Protocols:
- ProtocolImportValidator: For NodeImportValidatorCompute implementations
- ProtocolValidationOrchestrator: For NodeValidationOrchestratorOrchestrator implementations
- ProtocolQualityValidator: For NodeQualityValidatorEffect implementations
- ProtocolComplianceValidator: For NodeComplianceValidatorReducer implementations

Usage:
    ```python
from omnibase_spi.protocols.validation import (
        ProtocolImportValidator,
        ProtocolValidationOrchestrator,
        ProtocolQualityValidator,
        ProtocolComplianceValidator
)

    # Concrete implementations will be available in omnibase_core nodes
    ```

Note: This module contains ONLY Protocol definitions. Concrete implementations
will be provided by ONEX validation nodes in omnibase_core.
"""

# ONEX validation node protocols (new)
from .protocol_compliance_validator import (
    ProtocolArchitectureCompliance,
    ProtocolComplianceReport,
    ProtocolComplianceRule,
    ProtocolComplianceValidator,
    ProtocolComplianceViolation,
    ProtocolONEXStandards,
)
from .protocol_constraint_validator import ProtocolConstraintValidator
from .protocol_import_validator import (
    ProtocolImportAnalysis,
    ProtocolImportValidationConfig,
    ProtocolImportValidator,
)
from .protocol_quality_validator import (
    ProtocolQualityIssue,
    ProtocolQualityMetrics,
    ProtocolQualityReport,
    ProtocolQualityStandards,
    ProtocolQualityValidator,
)

# Core validation protocols (existing)
from .protocol_validation import (
    ProtocolValidationDecorator,
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)
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
    "ProtocolArchitectureCompliance",
    "ProtocolComplianceReport",
    "ProtocolComplianceRule",
    "ProtocolComplianceValidator",
    "ProtocolComplianceViolation",
    "ProtocolConstraintValidator",
    "ProtocolImportAnalysis",
    "ProtocolImportValidationConfig",
    "ProtocolImportValidator",
    "ProtocolONEXStandards",
    "ProtocolQualityIssue",
    "ProtocolQualityMetrics",
    "ProtocolQualityReport",
    "ProtocolQualityStandards",
    "ProtocolQualityValidator",
    "ProtocolValidationDecorator",
    "ProtocolValidationError",
    "ProtocolValidationMetrics",
    "ProtocolValidationOrchestrator",
    "ProtocolValidationProvider",
    "ProtocolValidationReport",
    "ProtocolValidationResult",
    "ProtocolValidationScope",
    "ProtocolValidationSummary",
    "ProtocolValidationWorkflow",
    "ProtocolValidator",
]

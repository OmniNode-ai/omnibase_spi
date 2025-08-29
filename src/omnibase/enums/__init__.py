"""
Shared enums for ONEX ecosystem.

Domain-grouped enums used across multiple ONEX packages (omnibase-core, omnibase-spi, etc.)
organized by functional domains for better maintainability.
"""

# Event and logging enums
from .events import EnumLogLevel

# Execution-related enums
from .execution import EnumExecutionMode, EnumOperationStatus

# Node-related enums
from .node import EnumHealthStatus, EnumNodeStatus, EnumNodeType

# Validation-related enums
from .validation import EnumErrorSeverity, EnumValidationLevel, EnumValidationMode

__all__ = [
    # Node domain
    "EnumNodeType",
    "EnumNodeStatus",
    "EnumHealthStatus",
    # Execution domain
    "EnumExecutionMode",
    "EnumOperationStatus",
    # Validation domain
    "EnumErrorSeverity",
    "EnumValidationLevel",
    "EnumValidationMode",
    # Events domain
    "EnumLogLevel",
]

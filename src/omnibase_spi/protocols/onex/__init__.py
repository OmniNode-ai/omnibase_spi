"""Protocols specific to the ONEX platform or services."""

from __future__ import annotations

from .protocol_compute_node import ProtocolOnexComputeNodeLegacy
from .protocol_effect_node import ProtocolOnexEffectNodeLegacy
from .protocol_envelope import ProtocolEnvelope
from .protocol_node import ProtocolOnexNodeLegacy
from .protocol_orchestrator_node import ProtocolOnexOrchestratorNodeLegacy
from .protocol_reducer_node import ProtocolOnexReducerNodeLegacy
from .protocol_reply import ProtocolReply
from .protocol_validation import (
    ProtocolContractData,
    ProtocolCorrelatedData,
    ProtocolOnexMetadata,
    ProtocolOnexSecurityContext,
    ProtocolOnexValidationReport,
    ProtocolOnexValidationResult,
    ProtocolSchema,
    ProtocolValidation,
)
from .protocol_version_loader import ProtocolVersionLoader

# Short aliases for backward compatibility and convenience
# These allow importing via short names from the main protocols __init__.py
ProtocolMetadata = ProtocolOnexMetadata
ProtocolSecurityContext = ProtocolOnexSecurityContext
ProtocolValidationReport = ProtocolOnexValidationReport
ProtocolValidationResult = ProtocolOnexValidationResult

__all__ = [
    "ProtocolContractData",
    "ProtocolCorrelatedData",
    "ProtocolEnvelope",
    "ProtocolMetadata",  # Alias for ProtocolOnexMetadata
    "ProtocolOnexComputeNodeLegacy",
    "ProtocolOnexEffectNodeLegacy",
    "ProtocolOnexMetadata",
    "ProtocolOnexNodeLegacy",
    "ProtocolOnexOrchestratorNodeLegacy",
    "ProtocolOnexReducerNodeLegacy",
    "ProtocolOnexSecurityContext",
    "ProtocolOnexValidationReport",
    "ProtocolOnexValidationResult",
    "ProtocolReply",
    "ProtocolSchema",
    "ProtocolSecurityContext",  # Alias for ProtocolOnexSecurityContext
    "ProtocolValidation",
    "ProtocolValidationReport",  # Alias for ProtocolOnexValidationReport
    "ProtocolValidationResult",  # Alias for ProtocolOnexValidationResult
    "ProtocolVersionLoader",
]

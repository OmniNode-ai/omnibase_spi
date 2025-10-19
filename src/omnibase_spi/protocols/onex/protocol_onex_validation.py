"""
Onex Validation Protocol Interface

Protocol interface for Onex contract validation and compliance checking.
Defines the contract for validating Onex patterns and contract compliance.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolDateTime,
        ProtocolSemVer,
    )


@runtime_checkable
class ProtocolOnexContractData(Protocol):
    """ONEX contract data structure protocol."""

    contract_version: "ProtocolSemVer"
    node_name: str
    node_type: str
    input_model: str
    output_model: str


@runtime_checkable
class ProtocolOnexSecurityContext(Protocol):
    """ONEX security context data protocol."""

    user_id: str
    session_id: str
    authentication_token: str
    security_profile: str


@runtime_checkable
class ProtocolOnexMetadata(Protocol):
    """ONEX metadata structure protocol."""

    tool_name: str
    tool_version: "ProtocolSemVer"
    timestamp: "ProtocolDateTime"
    environment: str


@runtime_checkable
class ProtocolOnexSchema(Protocol):
    """ONEX schema definition protocol."""

    schema_type: str
    version: "ProtocolSemVer"
    properties: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolOnexValidationReport(Protocol):
    """ONEX validation report protocol."""

    total_validations: int
    passed_validations: int
    failed_validations: int
    overall_status: str
    summary: str


LiteralOnexComplianceLevel = Literal[
    "fully_compliant", "partially_compliant", "non_compliant", "validation_error"
]
LiteralValidationType = Literal[
    "envelope_structure",
    "reply_structure",
    "contract_compliance",
    "security_validation",
    "metadata_validation",
    "full_validation",
]


@runtime_checkable
class ProtocolOnexValidationResult(Protocol):
    """Result of Onex validation protocol."""

    is_valid: bool
    compliance_level: LiteralOnexComplianceLevel
    validation_type: LiteralValidationType
    errors: list[str]
    warnings: list[str]
    metadata: "ProtocolOnexMetadata"


@runtime_checkable
class ProtocolOnexValidation(Protocol):
    """
    Protocol interface for Onex validation and compliance checking.

    All ONEX tools must implement this protocol for Onex pattern validation.
    Provides standardized validation for envelopes, replies, and contract compliance.
    """

    async def validate_envelope(
        self, envelope: "ProtocolOnexContractData"
    ) -> ProtocolOnexValidationResult: ...

    async def validate_reply(
        self, reply: "ProtocolOnexContractData"
    ) -> ProtocolOnexValidationResult: ...

    async def validate_contract_compliance(
        self, contract_data: "ProtocolOnexContractData"
    ) -> ProtocolOnexValidationResult: ...

    async def validate_security_context(
        self, security_context: "ProtocolOnexSecurityContext"
    ) -> ProtocolOnexValidationResult: ...

    async def validate_metadata(
        self, metadata: "ProtocolOnexMetadata"
    ) -> ProtocolOnexValidationResult: ...

    async def validate_full_onex_pattern(
        self, envelope: "ProtocolOnexContractData", reply: "ProtocolOnexContractData"
    ) -> ProtocolOnexValidationResult: ...

    async def check_required_fields(
        self, data: "ProtocolOnexContractData", required_fields: list[str]
    ) -> list[str]: ...

    async def validate_semantic_versioning(self, version: str) -> bool: ...

    async def validate_correlation_id_consistency(
        self, envelope: "ProtocolOnexContractData", reply: "ProtocolOnexContractData"
    ) -> bool: ...

    async def validate_timestamp_sequence(
        self, envelope: "ProtocolOnexContractData", reply: "ProtocolOnexContractData"
    ) -> bool: ...

    async def get_validation_schema(
        self, validation_type: str
    ) -> "ProtocolOnexSchema": ...

    async def validate_against_schema(
        self, data: "ProtocolOnexContractData", schema: "ProtocolOnexSchema"
    ) -> ProtocolOnexValidationResult: ...

    async def generate_validation_report(
        self, results: list[ProtocolOnexValidationResult]
    ) -> ProtocolOnexValidationReport: ...

    async def is_production_ready(
        self, validation_results: list[ProtocolOnexValidationResult]
    ) -> bool: ...

"""
Onex Validation Protocol Interface

Protocol interface for Onex contract validation and compliance checking.
Defines the contract for validating Onex patterns and contract compliance.
"""

from typing import Literal, Protocol

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolDateTime,
    ProtocolSemVer,
)


# Protocol types for ONEX validation data structures
class ProtocolOnexContractData(Protocol):
    """ONEX contract data structure protocol."""

    contract_version: ProtocolSemVer
    node_name: str
    node_type: str
    input_model: str
    output_model: str


class ProtocolOnexSecurityContext(Protocol):
    """ONEX security context data protocol."""

    user_id: str
    session_id: str
    authentication_token: str
    security_profile: str


class ProtocolOnexMetadata(Protocol):
    """ONEX metadata structure protocol."""

    tool_name: str
    tool_version: ProtocolSemVer
    timestamp: ProtocolDateTime
    environment: str


class ProtocolOnexSchema(Protocol):
    """ONEX schema definition protocol."""

    schema_type: str
    version: ProtocolSemVer
    properties: dict[str, str]


class ProtocolOnexValidationReport(Protocol):
    """ONEX validation report protocol."""

    total_validations: int
    passed_validations: int
    failed_validations: int
    overall_status: str
    summary: str


# Onex compliance levels - using Literal instead of Enum
LiteralOnexComplianceLevel = Literal[
    "fully_compliant", "partially_compliant", "non_compliant", "validation_error"
]

# Types of validation to perform - using Literal instead of Enum
LiteralValidationType = Literal[
    "envelope_structure",
    "reply_structure",
    "contract_compliance",
    "security_validation",
    "metadata_validation",
    "full_validation",
]


class ProtocolOnexValidationResult(Protocol):
    """Result of Onex validation protocol."""

    is_valid: bool
    compliance_level: LiteralOnexComplianceLevel
    validation_type: LiteralValidationType
    errors: list[str]
    warnings: list[str]
    metadata: ProtocolOnexMetadata


class ProtocolOnexValidation(Protocol):
    """
    Protocol interface for Onex validation and compliance checking.

    All ONEX tools must implement this protocol for Onex pattern validation.
    Provides standardized validation for envelopes, replies, and contract compliance.
    """

    def validate_envelope(
        self, envelope: ProtocolOnexContractData
    ) -> ProtocolOnexValidationResult:
        """
        Validate an Onex envelope for structure and compliance.

        Args:
            envelope: Onex envelope to validate

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def validate_reply(
        self, reply: ProtocolOnexContractData
    ) -> ProtocolOnexValidationResult:
        """
        Validate an Onex reply for structure and compliance.

        Args:
            reply: Onex reply to validate

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def validate_contract_compliance(
        self, contract_data: ProtocolOnexContractData
    ) -> ProtocolOnexValidationResult:
        """
        Validate contract data for Onex compliance.

        Args:
            contract_data: Contract data to validate

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def validate_security_context(
        self, security_context: ProtocolOnexSecurityContext
    ) -> ProtocolOnexValidationResult:
        """
        Validate security context for Onex compliance.

        Args:
            security_context: Security context to validate

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def validate_metadata(
        self, metadata: ProtocolOnexMetadata
    ) -> ProtocolOnexValidationResult:
        """
        Validate metadata structure for Onex compliance.

        Args:
            metadata: Metadata to validate

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def validate_full_onex_pattern(
        self, envelope: ProtocolOnexContractData, reply: ProtocolOnexContractData
    ) -> ProtocolOnexValidationResult:
        """
        Validate complete Onex pattern (envelope + reply) for compliance.

        Args:
            envelope: Onex envelope to validate
            reply: Onex reply to validate

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def check_required_fields(
        self, data: ProtocolOnexContractData, required_fields: list[str]
    ) -> list[str]:
        """
        Check for required fields in data structure.

        Args:
            data: Data structure to check
            required_fields: List of required field names

        Returns:
            List of missing required fields
        """
        ...

    def validate_semantic_versioning(self, version: str) -> bool:
        """
        Validate semantic versioning format.

        Args:
            version: Version string to validate

        Returns:
            True if version follows semantic versioning, False otherwise
        """
        ...

    def validate_correlation_id_consistency(
        self, envelope: ProtocolOnexContractData, reply: ProtocolOnexContractData
    ) -> bool:
        """
        Validate correlation ID consistency between envelope and reply.

        Args:
            envelope: Onex envelope with correlation ID
            reply: Onex reply with correlation ID

        Returns:
            True if correlation IDs match, False otherwise
        """
        ...

    def validate_timestamp_sequence(
        self, envelope: ProtocolOnexContractData, reply: ProtocolOnexContractData
    ) -> bool:
        """
        Validate timestamp sequence (reply timestamp >= envelope timestamp).

        Args:
            envelope: Onex envelope with timestamp
            reply: Onex reply with timestamp

        Returns:
            True if timestamp sequence is valid, False otherwise
        """
        ...

    def get_validation_schema(
        self, validation_type: LiteralValidationType
    ) -> ProtocolOnexSchema:
        """
        Get validation schema for specified validation type.

        Args:
            validation_type: Type of validation schema to retrieve

        Returns:
            Dictionary containing validation schema
        """
        ...

    def validate_against_schema(
        self, data: ProtocolOnexContractData, schema: ProtocolOnexSchema
    ) -> ProtocolOnexValidationResult:
        """
        Validate data against provided schema.

        Args:
            data: Data to validate
            schema: Validation schema

        Returns:
            Validation result with compliance level and any errors
        """
        ...

    def generate_validation_report(
        self, results: list[ProtocolOnexValidationResult]
    ) -> ProtocolOnexValidationReport:
        """
        Generate comprehensive validation report from multiple results.

        Args:
            results: List of validation results

        Returns:
            Dictionary containing comprehensive validation report
        """
        ...

    def is_production_ready(
        self, validation_results: list[ProtocolOnexValidationResult]
    ) -> bool:
        """
        Determine if validation results indicate production readiness.

        Args:
            validation_results: List of validation results to assess

        Returns:
            True if all validations indicate production readiness, False otherwise
        """
        ...

"""
Onex Validation Protocol Interface

Protocol interface for Onex contract validation and compliance checking.
Defines the contract for validating Onex patterns and contract compliance.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ModelOnexContractData(BaseModel):
    """ONEX contract data structure."""

    contract_version: str = Field(description="Contract version")
    node_name: str = Field(description="Node name")
    node_type: str = Field(description="Node type")
    input_model: str = Field(description="Input model")
    output_model: str = Field(description="Output model")

    class Config:
        frozen = True


class ModelOnexSecurityContext(BaseModel):
    """ONEX security context data."""

    user_id: str = Field(description="User identifier")
    session_id: str = Field(description="Session identifier")
    authentication_token: str = Field(description="Authentication token")
    security_profile: str = Field(description="Security profile")

    class Config:
        frozen = True


class ModelOnexMetadata(BaseModel):
    """ONEX metadata structure."""

    tool_name: str = Field(description="Tool name")
    tool_version: str = Field(description="Tool version")
    timestamp: str = Field(description="ISO timestamp")
    environment: str = Field(description="Environment")

    class Config:
        frozen = True


class ModelOnexSchema(BaseModel):
    """ONEX schema definition."""

    schema_type: str = Field(description="Schema type")
    version: str = Field(description="Schema version")
    properties: Dict[str, str] = Field(description="Schema properties")

    class Config:
        frozen = True


class ModelOnexValidationReport(BaseModel):
    """ONEX validation report."""

    total_validations: int = Field(description="Total number of validations")
    passed_validations: int = Field(description="Number of passed validations")
    failed_validations: int = Field(description="Number of failed validations")
    overall_status: str = Field(description="Overall validation status")
    summary: str = Field(description="Summary of validation results")

    class Config:
        frozen = True


class EnumOnexComplianceLevel(str, Enum):
    """Onex compliance levels."""

    FULLY_COMPLIANT = "fully_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    VALIDATION_ERROR = "validation_error"


class EnumValidationType(str, Enum):
    """Types of validation to perform."""

    ENVELOPE_STRUCTURE = "envelope_structure"
    REPLY_STRUCTURE = "reply_structure"
    CONTRACT_COMPLIANCE = "contract_compliance"
    SECURITY_VALIDATION = "security_validation"
    METADATA_VALIDATION = "metadata_validation"
    FULL_VALIDATION = "full_validation"


class ModelOnexValidationResult(BaseModel):
    """Result of Onex validation."""

    is_valid: bool = Field(description="Whether validation passed")
    compliance_level: EnumOnexComplianceLevel = Field(description="Compliance level")
    validation_type: EnumValidationType = Field(
        description="Type of validation performed"
    )
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    metadata: ModelOnexMetadata = Field(
        default_factory=lambda: ModelOnexMetadata(
            tool_name="", tool_version="", timestamp="", environment=""
        ),
        description="Validation metadata",
    )

    class Config:
        frozen = True


class ProtocolOnexValidation(ABC):
    """
    Protocol interface for Onex validation and compliance checking.

    All ONEX tools must implement this protocol for Onex pattern validation.
    Provides standardized validation for envelopes, replies, and contract compliance.
    """

    @abstractmethod
    def validate_envelope(self, envelope: BaseModel) -> ModelOnexValidationResult:
        """
        Validate an Onex envelope for structure and compliance.

        Args:
            envelope: Onex envelope to validate

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def validate_reply(self, reply: BaseModel) -> ModelOnexValidationResult:
        """
        Validate an Onex reply for structure and compliance.

        Args:
            reply: Onex reply to validate

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def validate_contract_compliance(
        self, contract_data: ModelOnexContractData
    ) -> ModelOnexValidationResult:
        """
        Validate contract data for Onex compliance.

        Args:
            contract_data: Contract data to validate

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def validate_security_context(
        self, security_context: ModelOnexSecurityContext
    ) -> ModelOnexValidationResult:
        """
        Validate security context for Onex compliance.

        Args:
            security_context: Security context to validate

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def validate_metadata(
        self, metadata: ModelOnexMetadata
    ) -> ModelOnexValidationResult:
        """
        Validate metadata structure for Onex compliance.

        Args:
            metadata: Metadata to validate

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def validate_full_onex_pattern(
        self, envelope: BaseModel, reply: BaseModel
    ) -> ModelOnexValidationResult:
        """
        Validate complete Onex pattern (envelope + reply) for compliance.

        Args:
            envelope: Onex envelope to validate
            reply: Onex reply to validate

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def check_required_fields(
        self, data: ModelOnexContractData, required_fields: List[str]
    ) -> List[str]:
        """
        Check for required fields in data structure.

        Args:
            data: Data structure to check
            required_fields: List of required field names

        Returns:
            List of missing required fields
        """
        pass

    @abstractmethod
    def validate_semantic_versioning(self, version: str) -> bool:
        """
        Validate semantic versioning format.

        Args:
            version: Version string to validate

        Returns:
            True if version follows semantic versioning, False otherwise
        """
        pass

    @abstractmethod
    def validate_correlation_id_consistency(
        self, envelope: BaseModel, reply: BaseModel
    ) -> bool:
        """
        Validate correlation ID consistency between envelope and reply.

        Args:
            envelope: Onex envelope with correlation ID
            reply: Onex reply with correlation ID

        Returns:
            True if correlation IDs match, False otherwise
        """
        pass

    @abstractmethod
    def validate_timestamp_sequence(
        self, envelope: BaseModel, reply: BaseModel
    ) -> bool:
        """
        Validate timestamp sequence (reply timestamp >= envelope timestamp).

        Args:
            envelope: Onex envelope with timestamp
            reply: Onex reply with timestamp

        Returns:
            True if timestamp sequence is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_validation_schema(
        self, validation_type: EnumValidationType
    ) -> ModelOnexSchema:
        """
        Get validation schema for specified validation type.

        Args:
            validation_type: Type of validation schema to retrieve

        Returns:
            Dictionary containing validation schema
        """
        pass

    @abstractmethod
    def validate_against_schema(
        self, data: ModelOnexContractData, schema: ModelOnexSchema
    ) -> ModelOnexValidationResult:
        """
        Validate data against provided schema.

        Args:
            data: Data to validate
            schema: Validation schema

        Returns:
            Validation result with compliance level and any errors
        """
        pass

    @abstractmethod
    def generate_validation_report(
        self, results: List[ModelOnexValidationResult]
    ) -> ModelOnexValidationReport:
        """
        Generate comprehensive validation report from multiple results.

        Args:
            results: List of validation results

        Returns:
            Dictionary containing comprehensive validation report
        """
        pass

    @abstractmethod
    def is_production_ready(
        self, validation_results: List[ModelOnexValidationResult]
    ) -> bool:
        """
        Determine if validation results indicate production readiness.

        Args:
            validation_results: List of validation results to assess

        Returns:
            True if all validations indicate production readiness, False otherwise
        """
        pass

"""
Onex Validation Protocol Interface

Protocol interface for Onex contract validation and compliance checking.
Defines the contract for validating Onex patterns and contract compliance.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolDateTime,
        ProtocolSemVer,
    )


@runtime_checkable
class ProtocolContractData(Protocol):
    """
    Protocol for ONEX contract data structure representation.

    Defines the essential elements of an ONEX contract including
    versioning, node identification, and input/output model
    specifications for contract compliance validation.

    Attributes:
        contract_version: Semantic version of the contract
        node_name: Unique identifier for the node
        node_type: ONEX node type classification
        input_model: Name of the input data model
        output_model: Name of the output data model

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        contract = ProtocolContractData(
            contract_version=SemVer(1, 0, 0),
            node_name="NodeDataProcessor",
            node_type="COMPUTE",
            input_model="ModelDataInput",
            output_model="ModelDataOutput"
        )

        result = await validator.validate_contract_compliance(contract)
        print(f"Compliance: {result.compliance_level}")
        ```

    See Also:
        - ProtocolValidation: Validation interface
        - ProtocolOnexValidationResult: Validation outcome
    """

    contract_version: "ProtocolSemVer"
    node_name: str
    node_type: str
    input_model: str
    output_model: str


@runtime_checkable
class ProtocolCorrelatedData(Protocol):
    """
    Protocol for data structures that participate in correlation tracking.

    Defines the essential elements needed for validating correlation ID
    consistency and timestamp sequences between related messages such
    as envelopes and replies in the ONEX request-response pattern.

    Attributes:
        correlation_id: UUID for tracking related requests and responses
        timestamp: Timestamp when the data was created or processed

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()

        # Validate correlation IDs match between envelope and reply
        is_consistent = await validator.validate_correlation_id_consistency(
            envelope, reply
        )

        # Validate reply timestamp follows envelope timestamp
        is_ordered = await validator.validate_timestamp_sequence(
            envelope, reply
        )
        ```

    See Also:
        - ProtocolValidation: Validation interface using this protocol
        - ProtocolContractData: Contract data structure
        - ProtocolEnvelopeData: Combined envelope data with correlation
    """

    correlation_id: UUID
    timestamp: "ProtocolDateTime"


@runtime_checkable
class ProtocolEnvelopeData(Protocol):
    """
    Protocol for complete ONEX envelope/reply data structure representation.

    Combines contract data fields with correlation tracking fields to provide
    a complete representation of an ONEX envelope or reply for validation.
    This protocol should be used when validating envelopes or replies that
    need both contract compliance checking and correlation/timestamp validation.

    Attributes:
        contract_version: Semantic version of the contract
        node_name: Unique identifier for the node
        node_type: ONEX node type classification
        input_model: Name of the input data model
        output_model: Name of the output data model
        correlation_id: UUID for tracking related requests and responses
        timestamp: Timestamp when the data was created or processed

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        envelope = get_envelope_data()  # ProtocolEnvelopeData

        # Full ONEX pattern validation
        result = await validator.validate_full_onex_pattern(envelope, reply)

        # Correlation validation (uses same envelope object)
        is_consistent = await validator.validate_correlation_id_consistency(
            envelope, reply
        )
        is_ordered = await validator.validate_timestamp_sequence(envelope, reply)
        ```

    See Also:
        - ProtocolContractData: Contract-only data structure
        - ProtocolCorrelatedData: Correlation-only data structure
        - ProtocolValidation: Validation interface
    """

    # Contract fields
    contract_version: "ProtocolSemVer"
    node_name: str
    node_type: str
    input_model: str
    output_model: str

    # Correlation fields
    correlation_id: UUID
    timestamp: "ProtocolDateTime"


@runtime_checkable
class ProtocolOnexSecurityContext(Protocol):
    """
    Protocol for ONEX security context data representation.

    Encapsulates security-related information for ONEX operations
    including user identification, session tracking, authentication
    credentials, and security profile classification.

    Note:
        This protocol is distinct from ProtocolSecurityContext in
        protocol_event_bus_types.py which handles event bus authentication.
        This protocol is specific to ONEX validation operations.

    Attributes:
        user_id: Unique identifier for the user
        session_id: Current session identifier
        authentication_token: Token for authentication verification
        security_profile: Security profile level (admin, user, readonly)

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        context = ProtocolOnexSecurityContext(
            user_id="user-123",
            session_id="session-abc",
            authentication_token="token-xyz",
            security_profile="admin"
        )

        result = await validator.validate_security_context(context)
        if result.is_valid:
            print("Security context validated")
        ```

    See Also:
        - ProtocolValidation: Security validation
        - ProtocolOnexValidationResult: Validation outcome
    """

    user_id: str
    session_id: str
    authentication_token: str
    security_profile: str


@runtime_checkable
class ProtocolOnexMetadata(Protocol):
    """
    Protocol for ONEX tool metadata structure representation.

    Captures metadata about the ONEX tool generating or processing
    data including identification, versioning, timing, and
    environment context for validation and auditing.

    Note:
        This protocol is distinct from ProtocolMetadata in
        protocol_state_types.py which handles general state metadata.
        This protocol is specific to ONEX tool validation metadata.

    Attributes:
        tool_name: Name of the ONEX tool
        tool_version: Semantic version of the tool
        timestamp: Timestamp of operation or generation
        environment: Deployment environment (dev, staging, prod)

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        metadata = ProtocolOnexMetadata(
            tool_name="NodeValidator",
            tool_version=SemVer(1, 2, 3),
            timestamp=datetime.now().isoformat(),
            environment="prod"
        )

        result = await validator.validate_metadata(metadata)
        print(f"Metadata valid: {result.is_valid}")
        ```

    See Also:
        - ProtocolValidation: Metadata validation
        - ProtocolOnexValidationResult: Validation outcome
    """

    tool_name: str
    tool_version: "ProtocolSemVer"
    timestamp: "ProtocolDateTime"
    environment: str


@runtime_checkable
class ProtocolSchema(Protocol):
    """
    Protocol for ONEX schema definition representation.

    Defines a schema structure for ONEX validation including
    type classification, versioning, and property definitions
    for data validation against ONEX standards.

    Attributes:
        schema_type: Classification of schema (envelope, reply, contract)
        version: Semantic version of the schema definition
        properties: Schema property definitions with context values

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        schema = await validator.get_validation_schema("envelope_structure")

        print(f"Schema type: {schema.schema_type}")
        print(f"Version: {schema.version}")
        print(f"Properties: {list(schema.properties.keys())}")
        ```

    See Also:
        - ProtocolValidation: Schema-based validation
        - ProtocolOnexValidationResult: Validation outcome
    """

    schema_type: str
    version: "ProtocolSemVer"
    properties: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolOnexValidationReport(Protocol):
    """
    Protocol for ONEX validation report aggregation.

    Provides comprehensive summary of multiple validation operations
    including pass/fail counts, overall status determination, and
    human-readable summary for reporting and compliance tracking.

    Note:
        This protocol is distinct from ProtocolValidationReport in
        protocol_validation_orchestrator.py which is for general validation
        orchestration reports. This protocol is specific to ONEX validation.

    Attributes:
        total_validations: Total number of validation operations
        passed_validations: Count of successful validations
        failed_validations: Count of failed validations
        overall_status: Aggregate status (passed, failed, partial)
        summary: Human-readable validation summary

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        results = [
            await validator.validate_envelope(envelope),
            await validator.validate_reply(reply),
            await validator.validate_metadata(metadata)
        ]

        report = await validator.generate_validation_report(results)
        print(f"Validation Report:")
        print(f"  Total: {report.total_validations}")
        print(f"  Passed: {report.passed_validations}")
        print(f"  Failed: {report.failed_validations}")
        print(f"  Status: {report.overall_status}")
        print(f"  Summary: {report.summary}")
        ```

    See Also:
        - ProtocolValidation: Validation operations
        - ProtocolOnexValidationResult: Individual results
    """

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
    """
    Protocol for individual ONEX validation operation result.

    Captures the complete outcome of a single validation operation
    including validity status, compliance level classification,
    validation type, issues found, and associated metadata.

    Note:
        This protocol is distinct from ProtocolValidationResult in
        protocol_validation.py which is for general protocol validation.
        This protocol is specific to ONEX validation operations.

    Attributes:
        is_valid: Whether validation passed
        compliance_level: ONEX compliance classification
        validation_type: Type of validation performed
        errors: List of error messages for failures
        warnings: List of warning messages for issues
        metadata: Metadata from the validation operation

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        result = await validator.validate_envelope(envelope)

        print(f"Valid: {result.is_valid}")
        print(f"Compliance: {result.compliance_level}")
        print(f"Type: {result.validation_type}")

        if not result.is_valid:
            for error in result.errors:
                print(f"  Error: {error}")
        for warning in result.warnings:
            print(f"  Warning: {warning}")
        ```

    See Also:
        - ProtocolValidation: Validation interface
        - ProtocolOnexValidationReport: Aggregated results
    """

    is_valid: bool
    compliance_level: LiteralOnexComplianceLevel
    validation_type: LiteralValidationType
    errors: list[str]
    warnings: list[str]
    metadata: "ProtocolOnexMetadata"


@runtime_checkable
class ProtocolValidation(Protocol):
    """
    Protocol interface for comprehensive ONEX pattern validation.

    Provides standardized validation for ONEX patterns including envelopes,
    replies, contract compliance, security contexts, and metadata. All ONEX
    tools must implement this protocol for consistent validation behavior.

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()

        # Validate envelope structure
        envelope_result = await validator.validate_envelope(envelope)

        # Validate reply structure
        reply_result = await validator.validate_reply(reply)

        # Validate full ONEX pattern (envelope + reply)
        full_result = await validator.validate_full_onex_pattern(envelope, reply)

        # Check correlation ID consistency
        is_consistent = await validator.validate_correlation_id_consistency(
            envelope, reply
        )

        # Check timestamp sequence
        is_ordered = await validator.validate_timestamp_sequence(envelope, reply)

        # Generate comprehensive report
        report = await validator.generate_validation_report([
            envelope_result, reply_result, full_result
        ])

        # Check production readiness
        is_ready = await validator.is_production_ready([
            envelope_result, reply_result
        ])
        ```

    See Also:
        - ProtocolOnexValidationResult: Individual validation results
        - ProtocolOnexValidationReport: Aggregated validation report
        - ProtocolEnvelopeData: Complete envelope/reply data with contract and correlation fields
        - ProtocolContractData: Contract-only data structure
        - ProtocolCorrelatedData: Correlation-only data with correlation_id and timestamp
    """

    async def validate_envelope(
        self, envelope: "ProtocolEnvelopeData"
    ) -> ProtocolOnexValidationResult:
        """
        Validate an ONEX envelope structure.

        Args:
            envelope: The envelope data to validate (includes contract and correlation fields).

        Returns:
            Validation result with compliance status and any errors.

        Raises:
            TypeError: If envelope is not of the expected type.
        """
        ...

    async def validate_reply(
        self, reply: "ProtocolEnvelopeData"
    ) -> ProtocolOnexValidationResult:
        """
        Validate an ONEX reply structure.

        Args:
            reply: The reply data to validate (includes contract and correlation fields).

        Returns:
            Validation result with compliance status and any errors.

        Raises:
            TypeError: If reply is not of the expected type.
        """
        ...

    async def validate_contract_compliance(
        self, contract_data: "ProtocolContractData"
    ) -> ProtocolOnexValidationResult:
        """
        Validate contract data against ONEX compliance rules.

        Args:
            contract_data: The contract data to validate.

        Returns:
            Validation result with compliance level and any violations.

        Raises:
            TypeError: If contract_data is not of the expected type.
        """
        ...

    async def validate_security_context(
        self, security_context: "ProtocolOnexSecurityContext"
    ) -> ProtocolOnexValidationResult:
        """
        Validate a security context for ONEX operations.

        Args:
            security_context: The security context to validate.

        Returns:
            Validation result indicating security context validity.

        Raises:
            TypeError: If security_context is not of the expected type.
        """
        ...

    async def validate_metadata(
        self, metadata: "ProtocolOnexMetadata"
    ) -> ProtocolOnexValidationResult:
        """
        Validate ONEX tool metadata.

        Args:
            metadata: The metadata to validate.

        Returns:
            Validation result with any metadata issues found.

        Raises:
            TypeError: If metadata is not of the expected type.
        """
        ...

    async def validate_full_onex_pattern(
        self, envelope: "ProtocolEnvelopeData", reply: "ProtocolEnvelopeData"
    ) -> ProtocolOnexValidationResult:
        """
        Validate a complete ONEX envelope-reply pattern.

        Performs comprehensive validation including contract compliance,
        correlation ID consistency, and timestamp sequence validation.

        Args:
            envelope: The envelope data (includes contract and correlation fields).
            reply: The reply data (includes contract and correlation fields).

        Returns:
            Validation result for the complete pattern.

        Raises:
            TypeError: If envelope or reply is not of the expected type.
        """
        ...

    async def check_required_fields(
        self, data: "ProtocolContractData", required_fields: list[str]
    ) -> list[str]:
        """
        Check for missing required fields in contract data.

        Args:
            data: The contract data to check.
            required_fields: List of field names that must be present.

        Returns:
            List of missing field names, empty if all present.

        Raises:
            TypeError: If data is not of the expected type.
        """
        ...

    async def validate_semantic_versioning(self, version: str) -> bool:
        """
        Validate that a version string follows semantic versioning.

        Args:
            version: The version string to validate.

        Returns:
            True if the version follows semver format, False otherwise.

        Raises:
            TypeError: If version is not a string.
        """
        ...

    async def validate_correlation_id_consistency(
        self, envelope: "ProtocolCorrelatedData", reply: "ProtocolCorrelatedData"
    ) -> bool:
        """
        Validate correlation ID consistency between envelope and reply.

        Args:
            envelope: The envelope data with correlation_id and timestamp.
            reply: The reply data with correlation_id and timestamp.

        Returns:
            True if correlation IDs match, False otherwise.

        Raises:
            TypeError: If envelope or reply is not of the expected type.
        """
        ...

    async def validate_timestamp_sequence(
        self, envelope: "ProtocolCorrelatedData", reply: "ProtocolCorrelatedData"
    ) -> bool:
        """
        Validate that reply timestamp follows envelope timestamp.

        Args:
            envelope: The envelope data with correlation_id and timestamp.
            reply: The reply data with correlation_id and timestamp.

        Returns:
            True if timestamps are in correct sequence, False otherwise.

        Raises:
            TypeError: If envelope or reply is not of the expected type.
        """
        ...

    async def get_validation_schema(self, validation_type: str) -> "ProtocolSchema":
        """
        Get the validation schema for a specific validation type.

        Args:
            validation_type: The type of validation schema to retrieve.

        Returns:
            The schema definition for the requested validation type.

        Raises:
            KeyError: If validation_type is not a recognized schema type.
            TypeError: If validation_type is not a string.
        """
        ...

    async def validate_against_schema(
        self, data: "ProtocolContractData", schema: "ProtocolSchema"
    ) -> ProtocolOnexValidationResult:
        """
        Validate contract data against a specific schema.

        Args:
            data: The contract data to validate.
            schema: The schema to validate against.

        Returns:
            Validation result with schema compliance details.

        Raises:
            TypeError: If data or schema is not of the expected type.
        """
        ...

    async def generate_validation_report(
        self, results: list[ProtocolOnexValidationResult]
    ) -> ProtocolOnexValidationReport:
        """
        Generate an aggregated validation report from multiple results.

        Args:
            results: List of individual validation results.

        Returns:
            Aggregated report with summary statistics.

        Raises:
            TypeError: If results is not a list of ProtocolOnexValidationResult.
        """
        ...

    async def is_production_ready(
        self, validation_results: list[ProtocolOnexValidationResult]
    ) -> bool:
        """
        Check if validation results indicate production readiness.

        Args:
            validation_results: List of validation results to evaluate.

        Returns:
            True if all validations pass production criteria, False otherwise.

        Raises:
            TypeError: If validation_results is not a list of ProtocolOnexValidationResult.
        """
        ...

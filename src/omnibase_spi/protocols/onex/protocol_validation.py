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
        - ProtocolValidationResult: Validation outcome
    """

    contract_version: "ProtocolSemVer"
    node_name: str
    node_type: str
    input_model: str
    output_model: str


@runtime_checkable
class ProtocolSecurityContext(Protocol):
    """
    Protocol for ONEX security context data representation.

    Encapsulates security-related information for ONEX operations
    including user identification, session tracking, authentication
    credentials, and security profile classification.

    Attributes:
        user_id: Unique identifier for the user
        session_id: Current session identifier
        authentication_token: Token for authentication verification
        security_profile: Security profile level (admin, user, readonly)

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        context = ProtocolSecurityContext(
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
        - ProtocolValidationResult: Validation outcome
    """

    user_id: str
    session_id: str
    authentication_token: str
    security_profile: str


@runtime_checkable
class ProtocolMetadata(Protocol):
    """
    Protocol for ONEX tool metadata structure representation.

    Captures metadata about the ONEX tool generating or processing
    data including identification, versioning, timing, and
    environment context for validation and auditing.

    Attributes:
        tool_name: Name of the ONEX tool
        tool_version: Semantic version of the tool
        timestamp: Timestamp of operation or generation
        environment: Deployment environment (dev, staging, prod)

    Example:
        ```python
        validator: ProtocolValidation = get_onex_validator()
        metadata = ProtocolMetadata(
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
        - ProtocolValidationResult: Validation outcome
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
        - ProtocolValidationResult: Validation outcome
    """

    schema_type: str
    version: "ProtocolSemVer"
    properties: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolValidationReport(Protocol):
    """
    Protocol for ONEX validation report aggregation.

    Provides comprehensive summary of multiple validation operations
    including pass/fail counts, overall status determination, and
    human-readable summary for reporting and compliance tracking.

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
        - ProtocolValidationResult: Individual results
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
class ProtocolValidationResult(Protocol):
    """
    Protocol for individual ONEX validation operation result.

    Captures the complete outcome of a single validation operation
    including validity status, compliance level classification,
    validation type, issues found, and associated metadata.

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
        - ProtocolValidationReport: Aggregated results
    """

    is_valid: bool
    compliance_level: LiteralOnexComplianceLevel
    validation_type: LiteralValidationType
    errors: list[str]
    warnings: list[str]
    metadata: "ProtocolMetadata"


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
        - ProtocolValidationResult: Individual validation results
        - ProtocolValidationReport: Aggregated validation report
        - ProtocolContractData: Contract data structure
    """

    async def validate_envelope(
        self, envelope: "ProtocolContractData"
    ) -> ProtocolValidationResult: ...

    async def validate_reply(
        self, reply: "ProtocolContractData"
    ) -> ProtocolValidationResult: ...

    async def validate_contract_compliance(
        self, contract_data: "ProtocolContractData"
    ) -> ProtocolValidationResult: ...

    async def validate_security_context(
        self, security_context: "ProtocolSecurityContext"
    ) -> ProtocolValidationResult: ...

    async def validate_metadata(
        self, metadata: "ProtocolMetadata"
    ) -> ProtocolValidationResult: ...

    async def validate_full_onex_pattern(
        self, envelope: "ProtocolContractData", reply: "ProtocolContractData"
    ) -> ProtocolValidationResult: ...

    async def check_required_fields(
        self, data: "ProtocolContractData", required_fields: list[str]
    ) -> list[str]: ...

    async def validate_semantic_versioning(self, version: str) -> bool: ...

    async def validate_correlation_id_consistency(
        self, envelope: "ProtocolContractData", reply: "ProtocolContractData"
    ) -> bool: ...

    async def validate_timestamp_sequence(
        self, envelope: "ProtocolContractData", reply: "ProtocolContractData"
    ) -> bool: ...

    async def get_validation_schema(
        self, validation_type: str
    ) -> "ProtocolSchema": ...

    async def validate_against_schema(
        self, data: "ProtocolContractData", schema: "ProtocolSchema"
    ) -> ProtocolValidationResult: ...

    async def generate_validation_report(
        self, results: list[ProtocolValidationResult]
    ) -> ProtocolValidationReport: ...

    async def is_production_ready(
        self, validation_results: list[ProtocolValidationResult]
    ) -> bool: ...

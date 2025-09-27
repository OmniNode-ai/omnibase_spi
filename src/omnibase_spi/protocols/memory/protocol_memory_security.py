"""
Security protocol definitions for OmniMemory operations.

Defines security contexts, authentication, authorization, and audit trail
protocols for memory operations following ONEX security-by-design principles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from .protocol_memory_base import ProtocolMemoryMetadata


@runtime_checkable
class ProtocolMemorySecurityContext(Protocol):
    """
    Security context for memory operations.

    Provides authentication, authorization, and audit trail information
    for all memory operations with sub-millisecond PII detection.
    """

    @property
    def user_id(self) -> UUID | None:
        """User ID performing the operation."""
        ...

    @property
    def session_id(self) -> UUID | None:
        """Session ID for request tracking."""
        ...

    @property
    def permissions(self) -> list[str]:
        """List of permissions granted to user."""
        ...

    @property
    def access_level(self) -> str:
        """Access level (public, internal, restricted, confidential)."""
        ...

    @property
    def audit_enabled(self) -> bool:
        """Whether audit logging is enabled."""
        ...

    @property
    def rate_limit_key(self) -> str | None:
        """Rate limiting key for this operation."""
        ...

    @property
    def pii_detection_enabled(self) -> bool:
        """Whether PII detection is enabled."""
        ...


@runtime_checkable
class ProtocolAuditTrail(Protocol):
    """
    Audit trail information for compliance and security monitoring.

    Captures detailed operation logs for security analysis and compliance
    reporting with comprehensive event tracking.
    """

    @property
    def operation_id(self) -> UUID:
        """Unique operation identifier."""
        ...

    @property
    def operation_type(self) -> str:
        """Type of operation performed."""
        ...

    @property
    def resource_id(self) -> UUID | None:
        """ID of resource being operated on."""
        ...

    @property
    def user_id(self) -> UUID | None:
        """User performing the operation."""
        ...

    @property
    def timestamp(self) -> "datetime":
        """Timestamp of operation."""
        ...

    @property
    def source_ip(self) -> str | None:
        """Source IP address of request."""
        ...

    @property
    def user_agent(self) -> str | None:
        """User agent string."""
        ...

    @property
    def operation_metadata(self) -> "ProtocolMemoryMetadata":
        """Additional operation metadata."""
        ...

    @property
    def compliance_tags(self) -> list[str]:
        """Compliance tags (GDPR, HIPAA, SOX, etc.)."""
        ...


@runtime_checkable
class ProtocolRateLimitConfig(Protocol):
    """
    Rate limiting configuration for memory operations.

    Defines rate limits and throttling policies to prevent abuse
    and ensure fair resource utilization.
    """

    @property
    def requests_per_minute(self) -> int:
        """Maximum requests per minute."""
        ...

    @property
    def requests_per_hour(self) -> int:
        """Maximum requests per hour."""
        ...

    @property
    def burst_limit(self) -> int:
        """Maximum burst requests allowed."""
        ...

    @property
    def batch_size_limit(self) -> int:
        """Maximum batch operation size."""
        ...

    @property
    def data_size_limit_mb(self) -> float:
        """Maximum data size per operation in MB."""
        ...

    @property
    def concurrent_operations_limit(self) -> int:
        """Maximum concurrent operations per user."""
        ...


@runtime_checkable
class ProtocolInputValidation(Protocol):
    """
    Input validation requirements for memory operations.

    Defines validation rules and sanitization requirements for
    all memory operation inputs to prevent injection attacks.
    """

    @property
    def max_content_length(self) -> int:
        """Maximum content length in characters."""
        ...

    @property
    def allowed_content_types(self) -> list[str]:
        """List of allowed content types."""
        ...

    @property
    def forbidden_patterns(self) -> list[str]:
        """List of forbidden regex patterns."""
        ...

    @property
    def require_sanitization(self) -> bool:
        """Whether input sanitization is required."""
        ...

    @property
    def pii_detection_threshold(self) -> float:
        """PII detection confidence threshold (0.0-1.0)."""
        ...

    @property
    def encoding_requirements(self) -> list[str]:
        """Required encoding standards."""
        ...


@runtime_checkable
class ProtocolMemorySecurityNode(Protocol):
    """
    Security validation and monitoring for memory operations.

    Provides security validation, PII detection, access control,
    and audit trail management for all memory operations.
    """

    async def validate_access(
        self,
        security_context: "ProtocolMemorySecurityContext",
        operation_type: str,
        resource_id: UUID | None = None,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Validate user access for memory operation.

        Args:
            security_context: Security context with user and permissions
            operation_type: Type of operation being attempted
            resource_id: Optional specific resource being accessed
            correlation_id: Request correlation ID

        Returns:
            Validation result with permissions and restrictions

        Raises:
            SecurityError: If access is denied
            AuthenticationError: If authentication fails
        """
        ...

    async def detect_pii(
        self,
        content: str,
        detection_threshold: float = 0.8,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Detect personally identifiable information in content.

        Args:
            content: Content to analyze for PII
            detection_threshold: Confidence threshold for PII detection
            correlation_id: Request correlation ID

        Returns:
            PII detection results with confidence scores

        Raises:
            ValidationError: If content violates PII policies
        """
        ...

    async def validate_input(
        self,
        input_data: "ProtocolMemoryMetadata",
        validation_config: "ProtocolInputValidation",
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Validate and sanitize input data.

        Args:
            input_data: Input data to validate
            validation_config: Validation configuration
            correlation_id: Request correlation ID

        Returns:
            Validation result with sanitized data

        Raises:
            ValidationError: If input validation fails
        """
        ...

    async def check_rate_limits(
        self,
        security_context: "ProtocolMemorySecurityContext",
        operation_type: str,
        rate_limit_config: "ProtocolRateLimitConfig",
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Check rate limits for user and operation.

        Args:
            security_context: Security context with user information
            operation_type: Type of operation being performed
            rate_limit_config: Rate limiting configuration
            correlation_id: Request correlation ID

        Returns:
            Rate limit status and remaining quotas

        Raises:
            RateLimitError: If rate limits are exceeded
        """
        ...

    async def create_audit_trail(
        self,
        audit_info: "ProtocolAuditTrail",
        security_context: "ProtocolMemorySecurityContext",
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Create audit trail entry for operation.

        Args:
            audit_info: Audit trail information
            security_context: Security context
            correlation_id: Request correlation ID

        Returns:
            Audit trail creation result

        Raises:
            AuditError: If audit trail creation fails
        """
        ...

    async def encrypt_sensitive_data(
        self,
        data: "ProtocolMemoryMetadata",
        encryption_level: str,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Encrypt sensitive data before storage.

        Args:
            data: Data to encrypt
            encryption_level: Encryption level (standard, high, maximum)
            correlation_id: Request correlation ID

        Returns:
            Encrypted data with metadata

        Raises:
            EncryptionError: If encryption fails
        """
        ...

    async def decrypt_sensitive_data(
        self,
        encrypted_data: "ProtocolMemoryMetadata",
        security_context: "ProtocolMemorySecurityContext",
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Decrypt sensitive data for authorized access.

        Args:
            encrypted_data: Encrypted data to decrypt
            security_context: Security context with decryption permissions
            correlation_id: Request correlation ID

        Returns:
            Decrypted data

        Raises:
            DecryptionError: If decryption fails
            SecurityError: If user not authorized to decrypt
        """
        ...


@runtime_checkable
class ProtocolMemoryComplianceNode(Protocol):
    """
    Compliance monitoring and enforcement for memory operations.

    Ensures memory operations comply with regulatory requirements
    including GDPR, HIPAA, SOX, and other compliance frameworks.
    """

    async def validate_gdpr_compliance(
        self,
        operation_type: str,
        data_subject_id: UUID | None,
        legal_basis: str,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Validate GDPR compliance for memory operation.

        Args:
            operation_type: Type of data processing operation
            data_subject_id: ID of data subject (if applicable)
            legal_basis: Legal basis for processing
            correlation_id: Request correlation ID

        Returns:
            GDPR compliance validation result

        Raises:
            ComplianceError: If operation violates GDPR
        """
        ...

    async def validate_hipaa_compliance(
        self,
        operation_type: str,
        phi_categories: list[str],
        covered_entity_id: UUID,
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Validate HIPAA compliance for health information.

        Args:
            operation_type: Type of PHI operation
            phi_categories: Categories of PHI being processed
            covered_entity_id: ID of covered entity
            correlation_id: Request correlation ID

        Returns:
            HIPAA compliance validation result

        Raises:
            ComplianceError: If operation violates HIPAA
        """
        ...

    async def generate_compliance_report(
        self,
        report_type: str,
        time_period_start: "datetime",
        time_period_end: "datetime",
        compliance_frameworks: list[str],
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Generate compliance report for specified period.

        Args:
            report_type: Type of compliance report
            time_period_start: Start of reporting period
            time_period_end: End of reporting period
            compliance_frameworks: Frameworks to include in report
            correlation_id: Request correlation ID

        Returns:
            Generated compliance report data

        Raises:
            ReportError: If report generation fails
        """
        ...

    async def handle_data_subject_request(
        self,
        request_type: str,
        data_subject_id: UUID,
        request_details: "ProtocolMemoryMetadata",
        correlation_id: UUID | None = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Handle data subject rights request (GDPR Article 15-20).

        Args:
            request_type: Type of data subject request
            data_subject_id: ID of data subject making request
            request_details: Details of the request
            correlation_id: Request correlation ID

        Returns:
            Request processing result

        Raises:
            ComplianceError: If request cannot be fulfilled
        """
        ...

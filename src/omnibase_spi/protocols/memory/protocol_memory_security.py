"""
Security protocol definitions for OmniMemory operations.

Defines security contexts, authentication, authorization, and audit trail
protocols for memory operations following ONEX security-by-design principles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryMetadata,
    )


@runtime_checkable
class ProtocolMemorySecurityContext(Protocol):
    """
    Security context for memory operations.

    Provides authentication, authorization, and audit trail information
    for all memory operations with sub-millisecond PII detection.
    """

    @property
    def user_id(self) -> UUID | None: ...

    @property
    def session_id(self) -> UUID | None: ...

    @property
    def permissions(self) -> list[str]: ...

    @property
    def access_level(self) -> str: ...

    @property
    def audit_enabled(self) -> bool: ...

    @property
    def rate_limit_key(self) -> str | None: ...

    @property
    def pii_detection_enabled(self) -> bool: ...


@runtime_checkable
class ProtocolAuditTrail(Protocol):
    """
    Audit trail information for compliance and security monitoring.

    Captures detailed operation logs for security analysis and compliance
    reporting with comprehensive event tracking.
    """

    @property
    def operation_id(self) -> UUID: ...

    @property
    def operation_type(self) -> str: ...

    @property
    def resource_id(self) -> UUID | None: ...

    @property
    def user_id(self) -> UUID | None: ...

    @property
    def timestamp(self) -> datetime: ...

    @property
    def source_ip(self) -> str | None: ...

    @property
    def user_agent(self) -> str | None: ...

    async def operation_metadata(self) -> ProtocolMemoryMetadata: ...

    @property
    def compliance_tags(self) -> list[str]: ...


@runtime_checkable
class ProtocolRateLimitConfig(Protocol):
    """
    Rate limiting configuration for memory operations.

    Defines rate limits and throttling policies to prevent abuse
    and ensure fair resource utilization.
    """

    @property
    def requests_per_minute(self) -> int: ...

    @property
    def requests_per_hour(self) -> int: ...

    @property
    def burst_limit(self) -> int: ...

    @property
    def batch_size_limit(self) -> int: ...

    @property
    def data_size_limit_mb(self) -> float: ...

    @property
    def concurrent_operations_limit(self) -> int: ...


@runtime_checkable
class ProtocolInputValidation(Protocol):
    """
    Input validation requirements for memory operations.

    Defines validation rules and sanitization requirements for
    all memory operation inputs to prevent injection attacks.
    """

    @property
    def max_content_length(self) -> int: ...

    @property
    def allowed_content_types(self) -> list[str]: ...

    @property
    def forbidden_patterns(self) -> list[str]: ...

    @property
    def require_sanitization(self) -> bool: ...

    @property
    def pii_detection_threshold(self) -> float: ...

    @property
    def encoding_requirements(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemorySecurityNode(Protocol):
    """
    Security validation and monitoring for memory operations.

    Provides security validation, PII detection, access control,
    and audit trail management for all memory operations.
    """

    async def validate_access(
        self,
        security_context: ProtocolMemorySecurityContext,
        operation_type: str,
        resource_id: UUID | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def detect_pii(
        self,
        content: str,
        detection_threshold: float | None = None,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def validate_input(
        self,
        input_data: ProtocolMemoryMetadata,
        validation_config: ProtocolInputValidation,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def check_rate_limits(
        self,
        security_context: ProtocolMemorySecurityContext,
        operation_type: str,
        rate_limit_config: ProtocolRateLimitConfig,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def create_audit_trail(
        self,
        audit_info: ProtocolAuditTrail,
        security_context: ProtocolMemorySecurityContext,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def encrypt_sensitive_data(
        self,
        data: ProtocolMemoryMetadata,
        encryption_level: str,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def decrypt_sensitive_data(
        self,
        encrypted_data: ProtocolMemoryMetadata,
        security_context: ProtocolMemorySecurityContext,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...


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
    ) -> ProtocolMemoryMetadata: ...

    async def validate_hipaa_compliance(
        self,
        operation_type: str,
        phi_categories: list[str],
        covered_entity_id: UUID,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def generate_compliance_report(
        self,
        report_type: str,
        time_period_start: datetime,
        time_period_end: datetime,
        compliance_frameworks: list[str],
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def handle_data_subject_request(
        self,
        request_type: str,
        data_subject_id: UUID,
        request_details: ProtocolMemoryMetadata,
        correlation_id: UUID | None = None,
    ) -> ProtocolMemoryMetadata: ...

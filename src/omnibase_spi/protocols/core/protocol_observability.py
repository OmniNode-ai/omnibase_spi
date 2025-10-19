"""
Protocol for Observability and Monitoring.

Defines interfaces for metrics collection, distributed tracing,
and audit logging across ONEX services for comprehensive observability.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        LiteralOperationStatus,
        ProtocolAuditEvent,
        ProtocolDateTime,
        ProtocolMetricsPoint,
        ProtocolTraceSpan,
    )


@runtime_checkable
class ProtocolMetricsCollector(Protocol):
    """
    Protocol for metrics collection and reporting.

    Provides standardized metrics collection interface for monitoring
    service performance, health, and business metrics.

    Key Features:
        - Counter, gauge, histogram, and timer metrics
        - Multi-dimensional metrics with tags
        - Batch metrics submission for performance
        - Custom metric types and aggregation
        - Integration with monitoring systems

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "Observability" = get_observability()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        metrics: "ProtocolMetricsCollector" = MetricsCollectorImpl()

        metrics.record_counter(
            name="requests_total",
            value=1,
            tags={"endpoint": "/api/users", "status": "200"}
        )
        ```
    """

    async def record_counter(
        self, name: str, value: float, tags: dict[str, "ContextValue"] | None
    ) -> None: ...

    async def record_gauge(
        self, name: str, value: float, tags: dict[str, "ContextValue"] | None
    ) -> None: ...

    async def record_histogram(
        self, name: str, value: float, tags: dict[str, "ContextValue"] | None
    ) -> None: ...

    async def record_timer(
        self, name: str, duration_seconds: float, tags: dict[str, "ContextValue"] | None
    ) -> None: ...

    async def record_metrics_batch(
        self, metrics: list["ProtocolMetricsPoint"]
    ) -> None: ...

    async def create_metrics_context(
        self, default_tags: dict[str, "ContextValue"]
    ) -> "ProtocolMetricsCollector": ...


@runtime_checkable
class ProtocolDistributedTracing(Protocol):
    """
    Protocol for distributed tracing across services.

    Provides standardized distributed tracing interface for request
    flow visibility and performance analysis in microservices.

    Key Features:
        - Span creation and lifecycle management
        - Parent-child span relationships
        - Cross-service trace propagation
        - Custom span tags and logs
        - Integration with tracing systems

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "Observability" = get_observability()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        tracing: "ProtocolDistributedTracing" = TracingImpl()

        span = tracing.start_span(
            operation_name="process_user_request",
            parent_span_id=request.trace_context.span_id
        )

        try:
            result = process_request()
            tracing.finish_span(span.span_id, "success")
        except Exception as e:
            tracing.add_span_tag(span.span_id, "error", str(e))
            tracing.finish_span(span.span_id, "failed")
        ```
    """

    async def start_span(
        self,
        operation_name: str,
        parent_span_id: "UUID | None",
        trace_id: "UUID | None",
    ) -> "ProtocolTraceSpan": ...

    async def finish_span(
        self, span_id: "UUID", status: "LiteralOperationStatus"
    ) -> None: ...

    async def add_span_tag(self, span_id: "UUID", key: str, value: str) -> None: ...

    async def add_span_log(
        self, span_id: "UUID", message: str, fields: dict[str, object] | None
    ) -> None: ...

    def extract_trace_context(
        self, headers: dict[str, "ContextValue"]
    ) -> tuple["UUID", "UUID"]: ...

    def inject_trace_context(
        self, trace_id: "UUID", span_id: "UUID", headers: dict[str, "ContextValue"]
    ) -> None: ...

    async def get_current_span(self) -> "ProtocolTraceSpan | None": ...


@runtime_checkable
class ProtocolAuditLogger(Protocol):
    """
    Protocol for audit event logging.

    Provides standardized audit logging interface for security,
    compliance, and operational event tracking.

    Key Features:
        - Structured audit event recording
        - Sensitivity level classification
        - Actor and resource tracking
        - Outcome and metadata capture
        - Compliance and security integration

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "Observability" = get_observability()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        audit_logger: "ProtocolAuditLogger" = AuditLoggerImpl()

        audit_logger.log_audit_event(
            event_type="user_access",
            actor="user123",
            resource="/api/sensitive-data",
            action="read",
            outcome="success",
            metadata={"ip_address": "192.168.1.1"},
            sensitivity_level="confidential"
        )
        ```
    """

    async def log_audit_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        outcome: "LiteralOperationStatus",
        metadata: dict[str, object] | None,
        sensitivity_level: str,
    ) -> "ProtocolAuditEvent": ...

    async def query_audit_events(
        self,
        start_time: "ProtocolDateTime",
        end_time: "ProtocolDateTime",
        filters: dict[str, "ContextValue"] | None,
    ) -> list["ProtocolAuditEvent"]: ...

    async def get_audit_statistics(
        self, time_window_hours: int
    ) -> dict[str, object]: ...

    async def archive_audit_events(
        self, before_date: "ProtocolDateTime", archive_location: str
    ) -> int: ...

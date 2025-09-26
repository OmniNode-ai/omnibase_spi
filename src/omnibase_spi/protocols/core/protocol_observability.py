"""
Protocol for Observability and Monitoring.

Defines interfaces for metrics collection, distributed tracing,
and audit logging across ONEX services for comprehensive observability.
"""

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from uuid import UUID

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
        # Implementation example (not part of SPI)
        class MetricsCollectorImpl:
            def record_counter(self, name, value, tags):
                point = MetricsPoint(
                    metric_name=name,
                    value=value,
                    tags=tags,
                    timestamp=datetime.utcnow()
                )
                self._send_to_backend(point)

        # Usage in application code
        metrics: ProtocolMetricsCollector = MetricsCollectorImpl()

        metrics.record_counter(
            name="requests_total",
            value=1,
            tags={"endpoint": "/api/users", "status": "200"}
        )
        ```
    """

    def record_counter(
        self,
        name: str,
        value: float,
        tags: Optional[dict[str, "ContextValue"]],
    ) -> None:
        """
        Record counter metric increment.

        Args:
            name: Metric name
            value: Value to increment counter by
            tags: Optional tags for metric dimensions

        Note:
            Counters are monotonically increasing values used for
            request counts, error counts, and event totals.
        """
        ...

    def record_gauge(
        self,
        name: str,
        value: float,
        tags: Optional[dict[str, "ContextValue"]],
    ) -> None:
        """
        Record gauge metric value.

        Args:
            name: Metric name
            value: Current gauge value
            tags: Optional tags for metric dimensions

        Note:
            Gauges represent current values that can increase or decrease,
            such as memory usage, connection counts, or queue depth.
        """
        ...

    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Optional[dict[str, "ContextValue"]],
    ) -> None:
        """
        Record histogram metric observation.

        Args:
            name: Metric name
            value: Observed value
            tags: Optional tags for metric dimensions

        Note:
            Histograms track distribution of values over time,
            useful for response times, request sizes, and latencies.
        """
        ...

    def record_timer(
        self,
        name: str,
        duration_seconds: float,
        tags: Optional[dict[str, "ContextValue"]],
    ) -> None:
        """
        Record timer metric for operation duration.

        Args:
            name: Metric name
            duration_seconds: Operation duration in seconds
            tags: Optional tags for metric dimensions

        Note:
            Timers are specialized histograms for measuring operation
            durations with automatic rate and percentile calculations.
        """
        ...

    def record_metrics_batch(
        self,
        metrics: list["ProtocolMetricsPoint"],
    ) -> None:
        """
        Record multiple metrics in batch for efficiency.

        Args:
            metrics: List of metrics points to record

        Note:
            Batch submission reduces overhead for high-frequency
            metrics and improves monitoring system performance.
        """
        ...

    def create_metrics_context(
        self,
        default_tags: dict[str, "ContextValue"],
    ) -> "ProtocolMetricsCollector":
        """
        Create metrics collector with default tags.

        Args:
            default_tags: Tags to apply to all metrics

        Returns:
            Metrics collector with default tags applied

        Note:
            Enables context-based metrics with common tags like
            service name, version, or environment applied automatically.
        """
        ...


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
        # Implementation example (not part of SPI)
        class TracingImpl:
            def start_span(self, operation_name, parent_span_id=None):
                span = TraceSpan(
                    span_id=uuid.uuid4(),
                    operation_name=operation_name,
                    parent_span_id=parent_span_id,
                    start_time=datetime.utcnow()
                )
                return span

        # Usage in application code
        tracing: ProtocolDistributedTracing = TracingImpl()

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

    def start_span(
        self,
        operation_name: str,
        parent_span_id: Optional["UUID"],
        trace_id: Optional["UUID"],
    ) -> "ProtocolTraceSpan":
        """
        Start new trace span.

        Args:
            operation_name: Name of operation being traced
            parent_span_id: Optional parent span ID for hierarchy
            trace_id: Optional trace ID (generated if not provided)

        Returns:
            Started trace span

        Note:
            Spans represent individual operations within a request flow.
            Parent-child relationships build call hierarchy for analysis.
        """
        ...

    def finish_span(
        self,
        span_id: "UUID",
        status: "LiteralOperationStatus",
    ) -> None:
        """
        Finish trace span with final status.

        Args:
            span_id: ID of span to finish
            status: Final operation status

        Note:
            Finishing spans records total duration and makes
            trace data available for analysis and visualization.
        """
        ...

    def add_span_tag(
        self,
        span_id: "UUID",
        key: str,
        value: str,
    ) -> None:
        """
        Add tag to trace span.

        Args:
            span_id: ID of span to tag
            key: Tag key
            value: Tag value

        Note:
            Tags provide structured metadata for filtering
            and analyzing traces by operation characteristics.
        """
        ...

    def add_span_log(
        self,
        span_id: "UUID",
        message: str,
        fields: Optional[dict[str, object]],
    ) -> None:
        """
        Add log entry to trace span.

        Args:
            span_id: ID of span to log to
            message: Log message
            fields: Optional structured log fields

        Note:
            Span logs capture events during operation execution
            for detailed debugging and performance analysis.
        """
        ...

    def extract_trace_context(
        self,
        headers: dict[str, "ContextValue"],
    ) -> tuple["UUID", "UUID"]:
        """
        Extract trace context from headers.

        Args:
            headers: Request headers containing trace context

        Returns:
            Tuple of (trace_id, span_id) extracted from headers

        Raises:
            ValueError: If headers don't contain valid trace context

        Note:
            Enables trace propagation across service boundaries
            for distributed request flow visibility.
        """
        ...

    def inject_trace_context(
        self,
        trace_id: "UUID",
        span_id: "UUID",
        headers: dict[str, "ContextValue"],
    ) -> None:
        """
        Inject trace context into headers.

        Args:
            trace_id: Trace ID to inject
            span_id: Span ID to inject
            headers: Headers dictionary to modify

        Note:
            Prepares headers for outbound requests to continue
            trace across service boundaries.
        """
        ...

    def get_current_span(self) -> Optional["ProtocolTraceSpan"]:
        """
        Get currently active trace span.

        Returns:
            Current span or None if no active span

        Note:
            Enables access to current span for tagging and logging
            without explicit span ID management.
        """
        ...


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
        # Implementation example (not part of SPI)
        class AuditLoggerImpl:
            def log_audit_event(self, event):
                if event.sensitivity_level in ["confidential", "restricted"]:
                    self._encrypt_before_storage(event)
                self._store_audit_event(event)

        # Usage in application code
        audit_logger: ProtocolAuditLogger = AuditLoggerImpl()

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

    def log_audit_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        outcome: "LiteralOperationStatus",
        metadata: Optional[dict[str, object]],
        sensitivity_level: str,
    ) -> "ProtocolAuditEvent":
        """
        Log audit event.

        Args:
            event_type: Type of audit event (e.g., "user_access", "data_modification")
            actor: Who performed the action (user ID, service name, etc.)
            resource: What resource was acted upon
            action: What action was performed
            outcome: Result of the action
            metadata: Optional additional event metadata
            sensitivity_level: Data sensitivity classification

        Returns:
            Created audit event with generated ID

        Note:
            All audit events are immutable and include comprehensive
            metadata for security and compliance analysis.
        """
        ...

    def query_audit_events(
        self,
        start_time: "ProtocolDateTime",
        end_time: "ProtocolDateTime",
        filters: Optional[dict[str, "ContextValue"]],
    ) -> list["ProtocolAuditEvent"]:
        """
        Query audit events by time range and filters.

        Args:
            start_time: Start of time range for query
            end_time: End of time range for query
            filters: Optional filters (actor, resource, event_type, etc.)

        Returns:
            List of matching audit events

        Note:
            Enables audit log analysis for security investigations,
            compliance reporting, and operational insights.
        """
        ...

    def get_audit_statistics(
        self,
        time_window_hours: int,
    ) -> dict[str, object]:
        """
        Get audit event statistics.

        Args:
            time_window_hours: Hours of data to analyze

        Returns:
            Audit statistics including event counts, actors, and outcomes

        Note:
            Provides operational visibility into system usage
            and security event patterns for monitoring.
        """
        ...

    def archive_audit_events(
        self,
        before_date: "ProtocolDateTime",
        archive_location: str,
    ) -> int:
        """
        Archive audit events older than specified date.

        Args:
            before_date: Archive events before this date
            archive_location: Location for archived events

        Returns:
            Number of events archived

        Note:
            Supports compliance requirements for audit log retention
            while managing storage costs and performance.
        """
        ...

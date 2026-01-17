"""
Protocol definition for hot-path metrics sink.

This module defines the ProtocolHotPathMetricsSink protocol for synchronous,
low-overhead metrics collection in performance-critical code paths. Unlike
async metrics collectors that may perform I/O on each call, this sink operates
on local state only, deferring any I/O to background flush operations.

The hot-path sink is designed for:
    - High-frequency metrics emission (thousands per second)
    - Zero I/O overhead per metric call
    - Minimal memory allocation per operation
    - Thread-safe or single-thread-only implementations

Related protocols:
    - ProtocolMetricsCollector: Async metrics collection with I/O per call
    - ProtocolPerformanceMetricsCollector: Full-featured async performance monitoring

Related tickets:
    - OMN-1368: Observability sink protocols
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.observability import ModelMetricsPolicy


@runtime_checkable
class ProtocolHotPathMetricsSink(Protocol):
    """
    Synchronous hot-path metrics sink for local state updates.

    This protocol defines a zero-I/O metrics collection interface optimized for
    high-frequency, low-latency code paths. All methods are synchronous and must
    not perform any I/O operations. Metric data is accumulated locally and
    flushed asynchronously by a separate background process.

    Key Differences from ProtocolMetricsCollector:
        - Synchronous methods (no async/await)
        - No I/O per call (local state updates only)
        - Designed for hot paths with strict latency requirements
        - Batches metrics for background export

    Thread-Safety Requirements:
        Implementations MUST document their threading model:
        - Thread-safe: Safe to call from multiple threads concurrently
        - Single-thread: Must only be called from a single thread
        - Thread-local: Each thread has its own isolated state

        For thread-safe implementations, use atomic operations or fine-grained
        locking. Avoid global locks that would create contention bottlenecks.

    Label Typing:
        Labels use `dict[str, str]` exclusively. This ensures:
        - Predictable serialization to Prometheus/StatsD format
        - No runtime type coercion or conversion errors
        - Consistent cardinality management

    Policy Enforcement:
        The get_policy() method returns configuration that governs:
        - Allowed metric names and label keys (allowlists)
        - Maximum label cardinality limits
        - Sampling rates for high-frequency metrics
        - Metric name prefixes and namespacing

    Usage Example:

        .. code-block:: python

            # Get a hot-path sink from the service container
            sink: ProtocolHotPathMetricsSink = container.get(
                ProtocolHotPathMetricsSink
            )

            # In a hot loop - no I/O, just local counter increment
            for request in requests:
                sink.increment_counter(
                    "requests_processed",
                    {"handler": "user_registration", "status": "success"},
                )
                sink.observe_histogram(
                    "request_latency_ms",
                    {"handler": "user_registration"},
                    request.latency_ms,
                )

            # Access policy for validation or logging
            policy = sink.get_policy()
            if policy.sampling_rate < 1.0:
                logger.debug(f"Metrics sampling at {policy.sampling_rate}")

    Performance Characteristics:
        - increment_counter: O(1), single atomic increment
        - set_gauge: O(1), single atomic write
        - observe_histogram: O(1), single bucket update
        - Memory: Bounded by cardinality limits in policy
    """

    def increment_counter(
        self,
        name: str,
        labels: dict[str, str],
        increment: int = 1,
    ) -> None:
        """
        Increment a counter metric by the specified amount.

        Counters are monotonically increasing values that reset only on process
        restart. Use counters for events, requests processed, errors, etc.

        Args:
            name: Metric name following Prometheus naming conventions.
                Should be lowercase with underscores (e.g., "http_requests_total").
                Must match policy allowlist if configured.
            labels: Label key-value pairs. Keys and values must be strings.
                Common labels: "method", "status", "handler", "error_type".
                Label cardinality should be bounded (avoid high-cardinality
                values like user IDs or request IDs).
            increment: Amount to add to the counter. Defaults to 1.
                Must be positive; implementations MAY reject negative values.

        Returns:
            None. This method has no return value.

        Raises:
            No exceptions should be raised on the hot path. Implementations
            SHOULD silently drop metrics that violate policy constraints
            and log violations asynchronously.

        Thread-Safety:
            Depends on implementation. See class docstring for requirements.

        Example:
            .. code-block:: python

                sink.increment_counter(
                    "http_requests_total",
                    {"method": "POST", "status": "200", "handler": "create_user"},
                )

                # Increment by more than 1
                sink.increment_counter(
                    "bytes_processed",
                    {"stream": "events"},
                    increment=len(payload),
                )
        """
        ...

    def set_gauge(
        self,
        name: str,
        labels: dict[str, str],
        value: float,
    ) -> None:
        """
        Set a gauge metric to the specified value.

        Gauges represent point-in-time values that can increase or decrease.
        Use gauges for queue depths, active connections, memory usage, etc.

        Args:
            name: Metric name following Prometheus naming conventions.
                Should be lowercase with underscores (e.g., "queue_depth").
                Must match policy allowlist if configured.
            labels: Label key-value pairs. Keys and values must be strings.
                Common labels: "queue_name", "pool_id", "region".
            value: Current value of the gauge. Can be any float including
                negative values, zero, infinity, or NaN (though NaN is
                discouraged and may be dropped by exporters).

        Returns:
            None. This method has no return value.

        Raises:
            No exceptions should be raised on the hot path. Implementations
            SHOULD silently drop metrics that violate policy constraints.

        Thread-Safety:
            Depends on implementation. See class docstring for requirements.
            For gauges, the last write wins in case of concurrent updates.

        Example:
            .. code-block:: python

                sink.set_gauge(
                    "active_connections",
                    {"pool": "database", "region": "us-west"},
                    value=42.0,
                )

                sink.set_gauge(
                    "memory_usage_bytes",
                    {"component": "cache"},
                    value=process.memory_info().rss,
                )
        """
        ...

    def observe_histogram(
        self,
        name: str,
        labels: dict[str, str],
        value: float,
    ) -> None:
        """
        Record an observation in a histogram metric.

        Histograms track the distribution of values, typically latencies or
        sizes. Values are bucketed for efficient storage and aggregation.

        Args:
            name: Metric name following Prometheus naming conventions.
                Should be lowercase with underscores and include units
                (e.g., "request_duration_seconds", "response_size_bytes").
                Must match policy allowlist if configured.
            labels: Label key-value pairs. Keys and values must be strings.
                Common labels: "method", "handler", "status".
            value: Observed value to record. Should be non-negative for
                most use cases (durations, sizes). The value is assigned
                to the appropriate bucket based on implementation-defined
                bucket boundaries.

        Returns:
            None. This method has no return value.

        Raises:
            No exceptions should be raised on the hot path. Implementations
            SHOULD silently drop metrics that violate policy constraints.

        Thread-Safety:
            Depends on implementation. See class docstring for requirements.
            Histogram updates typically require updating both a bucket counter
            and a sum, which should be atomic.

        Bucket Boundaries:
            Default buckets follow Prometheus conventions:
            [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            Custom buckets may be configured via ModelMetricsPolicy.

        Example:
            .. code-block:: python

                import time

                start = time.perf_counter()
                result = process_request(request)
                duration = time.perf_counter() - start

                sink.observe_histogram(
                    "request_duration_seconds",
                    {"handler": "process_request", "status": "success"},
                    value=duration,
                )
        """
        ...

    def get_policy(self) -> ModelMetricsPolicy:
        """
        Retrieve the metrics policy governing this sink.

        The policy defines constraints and configuration for metrics collection,
        including allowlists, cardinality limits, and sampling rates.

        Returns:
            ModelMetricsPolicy: The active metrics policy. Implementations
                MUST return a consistent policy throughout the sink's lifetime.
                Policy changes require creating a new sink instance.

        Policy Fields (typical):
            - allowed_metric_names: Set of permitted metric names (None = all)
            - allowed_label_keys: Set of permitted label keys (None = all)
            - max_label_cardinality: Maximum unique label combinations per metric
            - sampling_rate: Float 0.0-1.0 for probabilistic sampling
            - metric_prefix: Namespace prefix for all metric names
            - histogram_buckets: Custom bucket boundaries for histograms

        Thread-Safety:
            This method MUST be thread-safe. The returned policy object
            SHOULD be immutable or thread-safe for concurrent reads.

        Example:
            .. code-block:: python

                policy = sink.get_policy()

                # Check if a metric is allowed
                if policy.allowed_metric_names is not None:
                    if "custom_metric" not in policy.allowed_metric_names:
                        logger.warning("Metric 'custom_metric' not in allowlist")

                # Log sampling rate
                if policy.sampling_rate < 1.0:
                    logger.info(f"Metrics sampled at {policy.sampling_rate * 100}%")
        """
        ...

"""Protocol definition for observability sink factory.

This module defines the ProtocolObservabilitySinkFactory protocol, which
specifies the interface for creating observability sinks (metrics and logging)
based on subcontract configuration. This factory is designed to support the
hot path optimization pattern where conditional checks are eliminated from
the critical execution path.

Key Design Decisions:
    - Factory methods return concrete instances, never None/Optional
    - If observability is disabled in config, return a NoOp sink implementation
    - This enables branch-free hot path execution

See Also:
    - ProtocolHotPathMetricsSink: Metrics collection interface for hot paths
    - ProtocolHotPathLoggingSink: Logging interface for hot paths
    - ModelMetricsSubcontract: Configuration for metrics collection
    - ModelLoggingSubcontract: Configuration for logging behavior
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.contracts.subcontracts import (
        ModelLoggingSubcontract,
        ModelMetricsSubcontract,
    )
    from omnibase_spi.protocols.observability.protocol_hot_path_logging_sink import (
        ProtocolHotPathLoggingSink,
    )
    from omnibase_spi.protocols.observability.protocol_hot_path_metrics_sink import (
        ProtocolHotPathMetricsSink,
    )


@runtime_checkable
class ProtocolObservabilitySinkFactory(Protocol):
    """
    Factory for creating observability sinks based on subcontract configuration.

    This protocol defines the interface for creating metrics and logging sinks
    that are optimized for hot path execution. The factory pattern enables
    configuration-driven sink creation while maintaining branch-free execution
    in performance-critical code paths.

    Design Philosophy:
        The factory ALWAYS returns a concrete sink instance, never None or Optional.
        When observability features are disabled in the configuration, the factory
        returns NoOp sink implementations that conform to the protocol interface
        but perform no actual work. This approach eliminates conditional branches
        in the hot path, improving performance and simplifying consuming code.

    NoOp Sink Pattern:
        If metrics or logging is disabled in the configuration subcontract,
        implementations MUST return a NoOp sink that:
        - Implements the full protocol interface
        - Performs no I/O or side effects
        - Returns immediately from all method calls
        - Is safe to call from any context (sync or async)

        This pattern enables callers to unconditionally invoke sink methods
        without checking whether observability is enabled.

    Hot Path Optimization:
        By returning concrete sinks (including NoOp implementations), this factory
        eliminates the need for ``if metrics_enabled:`` checks throughout the
        codebase. The decision about whether to collect metrics or logs is made
        once at factory creation time, not on every operation.

    Thread Safety:
        Implementations should ensure that created sinks are thread-safe and
        can be shared across concurrent operations. The factory itself should
        also be safe to call from multiple threads.

    Example:
        ```python
        from omnibase_core.enums import EnumLogLevel
        from omnibase_spi.protocols.observability import (
            ProtocolObservabilitySinkFactory,
        )

        # Factory always returns concrete sinks
        factory: ProtocolObservabilitySinkFactory = get_sink_factory()

        # Create sinks from configuration
        metrics_sink = factory.create_metrics_sink(contract.metrics)
        logging_sink = factory.create_logging_sink(contract.logging)

        # Use sinks unconditionally - no None checks needed
        # If disabled, these are NoOp implementations
        metrics_sink.increment_counter("requests", {"handler": "example"}, 1)
        logging_sink.emit(EnumLogLevel.DEBUG, "Processing request", {})

        # In hot path code, no branching required:
        async def process_hot_path(data: bytes) -> bytes:
            metrics_sink.observe_histogram("payload_size", {}, len(data))
            result = transform(data)
            metrics_sink.increment_counter("transformations", {}, 1)
            return result
        ```

    See Also:
        - ProtocolHotPathMetricsSink: The metrics sink interface
        - ProtocolHotPathLoggingSink: The logging sink interface
        - ModelMetricsSubcontract: Metrics configuration model
        - ModelLoggingSubcontract: Logging configuration model
    """

    def create_metrics_sink(
        self, config: ModelMetricsSubcontract
    ) -> ProtocolHotPathMetricsSink:
        """
        Create a metrics sink based on the provided configuration.

        Creates a metrics collection sink configured according to the subcontract
        settings. If metrics collection is disabled in the configuration, this
        method returns a NoOp sink that conforms to ProtocolHotPathMetricsSink
        but performs no actual metrics collection.

        The returned sink is optimized for hot path usage and should introduce
        minimal overhead when called, especially for the NoOp implementation.

        Args:
            config: The metrics subcontract configuration that specifies:
                - Whether metrics collection is enabled
                - Collection intervals and batching settings
                - Metric naming conventions and prefixes
                - Backend-specific configuration

        Returns:
            A concrete ProtocolHotPathMetricsSink implementation. This is NEVER
            None - if metrics are disabled, a NoOp sink is returned that safely
            ignores all metric recording calls.

        Raises:
            This method does not raise exceptions. If configuration is invalid,
            a NoOp sink is returned instead.

        Example:
            ```python
            # Metrics enabled - returns real sink
            enabled_config = ModelMetricsSubcontract(enabled=True, ...)
            real_sink = factory.create_metrics_sink(enabled_config)
            real_sink.increment_counter("ops", {}, 1)  # Recorded to backend

            # Metrics disabled - returns NoOp sink
            disabled_config = ModelMetricsSubcontract(enabled=False)
            noop_sink = factory.create_metrics_sink(disabled_config)
            noop_sink.increment_counter("ops", {}, 1)  # No-op, returns immediately
            ```

        Note:
            The factory may cache or reuse sink instances for identical
            configurations. Implementations should document their caching
            behavior if applicable.
        """
        ...

    def create_logging_sink(
        self, config: ModelLoggingSubcontract
    ) -> ProtocolHotPathLoggingSink:
        """
        Create a logging sink based on the provided configuration.

        Creates a logging sink configured according to the subcontract settings.
        If logging is disabled in the configuration, this method returns a NoOp
        sink that conforms to ProtocolHotPathLoggingSink but discards all log
        messages without performing any I/O.

        The returned sink is optimized for hot path usage. Even when logging is
        enabled, implementations should minimize allocation and formatting
        overhead for log messages that will be filtered by level.

        Args:
            config: The logging subcontract configuration that specifies:
                - Whether logging is enabled
                - Minimum log level threshold
                - Output format and destination
                - Structured logging field requirements
                - Backend-specific configuration

        Returns:
            A concrete ProtocolHotPathLoggingSink implementation. This is NEVER
            None - if logging is disabled, a NoOp sink is returned that safely
            ignores all log calls.

        Raises:
            This method does not raise exceptions. If configuration is invalid,
            a NoOp sink is returned instead.

        Example:
            ```python
            from omnibase_core.enums import EnumLogLevel

            # Logging enabled - returns real sink
            enabled_config = ModelLoggingSubcontract(enabled=True, level="DEBUG")
            real_sink = factory.create_logging_sink(enabled_config)
            real_sink.emit(EnumLogLevel.DEBUG, "Processing started", {})  # Written

            # Logging disabled - returns NoOp sink
            disabled_config = ModelLoggingSubcontract(enabled=False)
            noop_sink = factory.create_logging_sink(disabled_config)
            noop_sink.emit(EnumLogLevel.DEBUG, "Processing started", {})  # No-op
            ```

        Note:
            For performance-sensitive hot paths, prefer using the sink's level
            check methods (if provided) before constructing expensive log
            messages, even though NoOp sinks handle this efficiently.
        """
        ...

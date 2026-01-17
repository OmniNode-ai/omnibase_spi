"""Protocol definition for hot-path logging sink.

This module defines the ProtocolHotPathLoggingSink protocol for synchronous,
high-performance logging in performance-critical code paths. Unlike ProtocolLogger
which is async and suitable for general logging, this protocol is designed for
hot-path scenarios where I/O latency cannot be tolerated on each log call.

Domain: Observability - Hot-path logging with buffered I/O
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.enums import EnumLogLevel


@runtime_checkable
class ProtocolHotPathLoggingSink(Protocol):
    """
    Synchronous hot-path logging sink for local state updates.

    This protocol defines a synchronous logging interface optimized for
    performance-critical code paths where I/O latency per call is unacceptable.
    Log entries are buffered locally and flushed to the underlying storage
    backend only when `flush()` is called.

    IMPORTANT: This is fundamentally different from `ProtocolLogger`:
        - `ProtocolLogger`: Async methods, may perform I/O on each call
        - `ProtocolHotPathLoggingSink`: Sync methods, NO I/O per call

    Thread-Safety Requirements:
        Implementations MUST document their thread-safety guarantees:
        - Thread-safe implementations should use appropriate locking
        - Single-thread implementations should document they are NOT thread-safe
        - The `flush()` method is the ONLY method that may block on I/O

    Design Rationale:
        In hot-path code (tight loops, high-frequency operations), async logging
        introduces context switching overhead and potential I/O latency. This
        protocol enables zero-overhead logging during critical sections by:
        1. Buffering log entries in memory (emit)
        2. Flushing to storage in batch (flush)

    Example:
        ```python
        from omnibase_core.enums import EnumLogLevel

        class BufferedLoggingSink:
            '''Thread-safe buffered logging sink implementation.'''

            def __init__(self, backend: LoggingBackend) -> None:
                self._buffer: list[tuple[EnumLogLevel, str, dict[str, str]]] = []
                self._backend = backend
                self._lock = threading.Lock()

            def emit(
                self,
                level: EnumLogLevel,
                message: str,
                context: dict[str, str]
            ) -> None:
                with self._lock:
                    self._buffer.append((level, message, context))

            def flush(self) -> None:
                with self._lock:
                    entries = self._buffer.copy()
                    self._buffer.clear()
                # I/O happens outside the lock
                for level, message, context in entries:
                    self._backend.write(level, message, context)

        # Usage in hot-path code
        sink: ProtocolHotPathLoggingSink = get_sink()

        for item in large_dataset:  # Hot loop
            result = process(item)
            sink.emit(EnumLogLevel.DEBUG, f"Processed {item.id}", {"status": "ok"})

        # Flush after hot-path completes
        sink.flush()
        ```

    See Also:
        - ProtocolLogger: Async logging protocol for general use
        - ProtocolMetricsCollector: Async metrics collection protocol
    """

    def emit(
        self,
        level: EnumLogLevel,
        message: str,
        context: dict[str, str],
    ) -> None:
        """Buffer a log entry for later emission.

        Synchronously buffers a log entry without performing any I/O.
        This method MUST NOT block, perform network calls, or write to disk.
        All I/O is deferred until `flush()` is called.

        Args:
            level: Log level from EnumLogLevel (TRACE, DEBUG, INFO, WARNING,
                   ERROR, CRITICAL, FATAL).
            message: Log message content. Should be a complete, self-contained
                     message suitable for structured logging.
            context: Structured context data for the log entry. All values
                     MUST be strings to ensure serialization safety and
                     prevent type coercion issues in hot paths.

        Note:
            This method is synchronous (`def`, not `async def`) by design.
            It MUST complete without blocking to maintain hot-path performance.

        Example:
            ```python
            sink.emit(
                level=EnumLogLevel.INFO,
                message="Cache hit for user lookup",
                context={"user_id": "u_123", "cache_key": "user:u_123"}
            )
            ```
        """
        ...

    def flush(self) -> None:
        """Flush all buffered log entries to the underlying storage.

        This is the ONLY method in this protocol that may perform I/O.
        All buffered log entries should be written to the configured
        backend (file, network, database, etc.) and the buffer cleared.

        Implementations should handle flush failures gracefully:
        - Log flush errors to stderr or a fallback mechanism
        - Consider retry logic for transient failures
        - Clear the buffer even on partial failure to prevent unbounded growth

        Thread-Safety:
            If the implementation is thread-safe, this method should be
            safe to call concurrently with `emit()`. Implementations may
            choose to block `emit()` during flush or use double-buffering.

        Note:
            This method is synchronous (`def`, not `async def`). For async
            backends, implementations may use `asyncio.run()` internally
            or maintain a separate async flush mechanism.

        Example:
            ```python
            # Periodic flush in a long-running process
            while processing:
                batch = get_next_batch()
                process_batch(batch, sink)

                # Flush every N iterations
                if iteration % 100 == 0:
                    sink.flush()

            # Final flush on shutdown
            sink.flush()
            ```
        """
        ...

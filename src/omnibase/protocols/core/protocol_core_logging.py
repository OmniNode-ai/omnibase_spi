"""
Core Logging Protocol for Bootstrap.

Minimal protocol definition for logging services used during bootstrap
and service discovery. The full implementation resides in node_logger.

This protocol enables core modules to request logging services without
creating circular dependencies.
"""

from typing import Any, Callable, Dict, Optional, Protocol, TypeVar

from omnibase.protocols.types import ContextValue, LogLevel

# Type variable for function decorators - preserves specific function signatures
F = TypeVar("F", bound=Callable[..., Any])


class ProtocolCoreLogging(Protocol):
    """
    Minimal logging protocol for core bootstrap scenarios.

    This protocol defines the essential logging interface needed during
    system bootstrap before the full node_logger service is available.
    """

    def emit_log_event_sync(
        self,
        level: LogLevel,
        message: str,
        event_type: str = "generic",
        node_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        data: Optional[Dict[str, ContextValue]] = None,
    ) -> None:
        """
        Emit a structured log event synchronously.

        Args:
            level: Log level
            message: Log message
            event_type: Event type
            node_id: Node ID
            correlation_id: Correlation ID
            data: Additional data
            **kwargs: Additional arguments
        """
        ...

    def trace_function_lifecycle(self, func: F) -> F:
        """
        Enable function lifecycle tracing.

        Args:
            func: Function to trace

        Returns:
            Function with tracing capability
        """
        ...

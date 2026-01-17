"""Protocols for observability, metrics, and monitoring.

This module provides protocols for observability infrastructure including
metrics collection and logging sinks optimized for hot path execution.

Key Protocols:
    - ProtocolHotPathLoggingSink: Low-overhead synchronous logging sink
    - ProtocolHotPathMetricsSink: Low-overhead synchronous metrics collection
    - ProtocolObservabilitySinkFactory: Factory for creating metrics and logging sinks
"""

from __future__ import annotations

from .protocol_hot_path_logging_sink import ProtocolHotPathLoggingSink
from .protocol_hot_path_metrics_sink import ProtocolHotPathMetricsSink
from .protocol_observability_sink_factory import ProtocolObservabilitySinkFactory

__all__ = [
    "ProtocolHotPathLoggingSink",
    "ProtocolHotPathMetricsSink",
    "ProtocolObservabilitySinkFactory",
]

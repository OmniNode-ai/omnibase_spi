"""
Core Protocol Interfaces

System-level contracts for serialization, error handling, health monitoring,
logging, service discovery, and other truly core functionality.

After the comprehensive reorganization, the core domain now contains only
13 essential protocols that are fundamental to the ONEX system architecture.
"""

from omnibase_spi.protocols.core.protocol_canonical_serializer import (
    ProtocolCanonicalSerializer,
)
from omnibase_spi.protocols.core.protocol_error_handler import ProtocolErrorHandler
from omnibase_spi.protocols.core.protocol_error_sanitizer import (
    ProtocolErrorSanitizer,
    ProtocolErrorSanitizerFactory,
)
from omnibase_spi.protocols.core.protocol_health_details import ProtocolHealthDetails
from omnibase_spi.protocols.core.protocol_health_monitor import ProtocolHealthMonitor
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger
from omnibase_spi.protocols.core.protocol_observability import (
    ProtocolAuditLogger,
    ProtocolDistributedTracing,
    ProtocolMetricsCollector,
)
from omnibase_spi.protocols.core.protocol_performance_metrics import (
    ProtocolPerformanceMetricsCollector,
)
from omnibase_spi.protocols.core.protocol_retryable import ProtocolRetryable
from omnibase_spi.protocols.core.protocol_service_discovery import (
    ProtocolServiceDiscovery,
)
from omnibase_spi.protocols.core.protocol_time_based import ProtocolTimeBasedOperations
from omnibase_spi.protocols.core.protocol_uri_parser import ProtocolUriParser
from omnibase_spi.protocols.core.protocol_version_manager import ProtocolVersionManager

__all__ = [
    "ProtocolAuditLogger",
    "ProtocolCanonicalSerializer",
    "ProtocolDistributedTracing",
    "ProtocolErrorHandler",
    "ProtocolErrorSanitizer",
    "ProtocolErrorSanitizerFactory",
    "ProtocolHealthDetails",
    "ProtocolHealthMonitor",
    "ProtocolLogger",
    "ProtocolMetricsCollector",
    "ProtocolPerformanceMetricsCollector",
    "ProtocolRetryable",
    "ProtocolServiceDiscovery",
    "ProtocolTimeBasedOperations",
    "ProtocolUriParser",
    "ProtocolVersionManager",
]

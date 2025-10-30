# Core Protocols API Reference

## Overview

The ONEX core protocols provide fundamental system contracts for logging, health monitoring, error handling, service discovery, and performance metrics. These protocols serve as the foundation for all ONEX services with consistent patterns and observability.

## 🏗️ Protocol Architecture

The core domain consists of **13 specialized protocols** that provide essential system capabilities:

### Health Monitor Protocol

```python
from omnibase_spi.protocols.core import ProtocolHealthMonitor
from omnibase_spi.protocols.types.protocol_core_types import (
    LiteralHealthCheckLevel,
    LiteralHealthDimension,
    LiteralHealthStatus,
    ProtocolHealthCheck,
    ProtocolHealthMetrics,
    ProtocolHealthMonitoring,
)

@runtime_checkable
class ProtocolHealthMonitor(Protocol):
    """
    Protocol for standardized health monitoring across ONEX services.

    Provides consistent health check patterns, monitoring configuration,
    and availability tracking for distributed system reliability.

    Key Features:
        - Multi-level health checks (quick to comprehensive)
        - Dimensional health assessment (availability, performance, etc.)
        - Configurable monitoring intervals and thresholds
        - Health metrics collection and trending
        - Automated alerting and escalation
        - Service dependency health tracking
    """

    async def perform_health_check(
        self,
        level: LiteralHealthCheckLevel,
        dimensions: list[LiteralHealthDimension],
    ) -> ProtocolHealthCheck: ...

    async def get_current_health_status(self) -> LiteralHealthStatus: ...

    async def get_health_metrics(self) -> ProtocolHealthMetrics: ...

    def configure_monitoring(self, config: ProtocolHealthMonitoring) -> bool: ...

    async def get_monitoring_configuration(self) -> ProtocolHealthMonitoring: ...

    async def start_monitoring(self) -> bool: ...

    async def stop_monitoring(self) -> bool: ...

    def is_monitoring_active(self) -> bool: ...

    async def get_health_history(
        self, hours_back: int
    ) -> list[ProtocolHealthCheck]: ...

    async def register_health_dependency(
        self, dependency_name: str, dependency_monitor: ProtocolHealthMonitor
    ) -> bool: ...

    async def unregister_health_dependency(self, dependency_name: str) -> bool: ...

    async def get_dependency_health_status(
        self, dependency_name: str
    ) -> LiteralHealthStatus: ...

    async def set_health_alert_callback(
        self,
        callback: Callable[[str, LiteralHealthStatus, LiteralHealthStatus], None],
    ) -> bool: ...

    async def get_aggregated_health_status(
        self,
    ) -> dict[str, LiteralHealthStatus]: ...
```

### Logger Protocol

```python
from omnibase_spi.protocols.core import ProtocolLogger
from omnibase_spi.protocols.types.protocol_core_types import LogLevel

@runtime_checkable
class ProtocolLogger(Protocol):
    """
    Protocol for structured logging across ONEX services.

    Provides consistent logging patterns, structured data support,
    and integration with observability systems.

    Key Features:
        - Structured logging with context
        - Multiple log levels (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL)
        - Performance metrics integration
        - Audit trail capabilities
        - Integration with external logging systems
    """

    async def log(
        self,
        level: LogLevel,
        message: str,
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None: ...

    async def log_structured(
        self,
        level: LogLevel,
        event: str,
        data: dict[str, Any],
        correlation_id: str | None = None,
    ) -> None: ...

    async def log_performance(
        self,
        operation: str,
        duration_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

    async def log_audit(
        self,
        action: str,
        user_id: str | None = None,
        resource: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None: ...

    def set_correlation_id(self, correlation_id: str) -> None: ...

    def get_correlation_id(self) -> str | None: ...

    async def flush(self) -> None: ...
```

### Service Discovery Protocol

```python
@runtime_checkable
class ProtocolServiceDiscovery(Protocol):
    """
    Protocol for service discovery and registration.

    Enables dynamic service discovery, health checking, and
    load balancing across distributed systems.

    Key Features:
        - Service registration and deregistration
        - Health-based service filtering
        - Load balancing strategies
        - Service metadata management
        - Discovery event notifications
    """

    async def register_service(
        self,
        service_name: str,
        service_url: str,
        metadata: dict[str, Any] | None = None,
        health_check_url: str | None = None,
    ) -> str: ...

    async def deregister_service(self, service_id: str) -> bool: ...

    async def discover_services(
        self,
        service_name: str,
        healthy_only: bool = True,
        tags: list[str] | None = None,
    ) -> list[ProtocolServiceInfo]: ...

    async def get_service_instances(
        self, service_name: str
    ) -> list[ProtocolServiceInfo]: ...

    async def update_service_health(
        self, service_id: str, health_status: LiteralHealthStatus
    ) -> bool: ...

    async def subscribe_to_service_changes(
        self,
        service_name: str,
        callback: Callable[[list[ProtocolServiceInfo]], None],
    ) -> str: ...

    async def unsubscribe_from_service_changes(self, subscription_id: str) -> None: ...
```

### Error Handler Protocol

```python
@runtime_checkable
class ProtocolErrorHandler(Protocol):
    """
    Protocol for centralized error handling and recovery.

    Provides consistent error handling patterns, recovery strategies,
    and error reporting across ONEX services.

    Key Features:
        - Error classification and categorization
        - Recovery strategy execution
        - Error reporting and alerting
        - Error context preservation
        - Integration with monitoring systems
    """

    async def handle_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
        recovery_strategy: str | None = None,
    ) -> ProtocolErrorResult: ...

    async def classify_error(self, error: Exception) -> LiteralErrorType: ...

    async def execute_recovery_strategy(
        self, error: Exception, strategy: str
    ) -> bool: ...

    async def report_error(
        self,
        error: Exception,
        severity: LiteralErrorSeverity,
        context: dict[str, Any] | None = None,
    ) -> None: ...

    async def get_error_statistics(
        self, time_range_hours: int
    ) -> ProtocolErrorStatistics: ...
```

### Performance Metrics Protocol

```python
@runtime_checkable
class ProtocolPerformanceMetrics(Protocol):
    """
    Protocol for performance metrics collection and analysis.

    Provides comprehensive performance monitoring, metrics collection,
    and performance analysis across ONEX services.

    Key Features:
        - Performance metrics collection
        - Real-time performance monitoring
        - Performance trend analysis
        - Resource utilization tracking
        - Performance alerting
    """

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: dict[str, str] | None = None,
        timestamp: datetime | None = None,
    ) -> None: ...

    async def record_timing(
        self,
        operation: str,
        duration_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

    async def record_counter(
        self,
        counter_name: str,
        increment: int = 1,
        tags: dict[str, str] | None = None,
    ) -> None: ...

    async def get_metrics(
        self,
        metric_name: str | None = None,
        time_range_hours: int = 24,
    ) -> list[ProtocolMetricDataPoint]: ...

    async def get_performance_summary(
        self, time_range_hours: int
    ) -> ProtocolPerformanceSummary: ...

    async def get_resource_utilization(
        self,
    ) -> ProtocolResourceUtilization: ...
```

### Canonical Serializer Protocol

```python
@runtime_checkable
class ProtocolCanonicalSerializer(Protocol):
    """
    Protocol for canonical data serialization.

    Provides consistent serialization patterns, format support,
    and data transformation across ONEX services.

    Key Features:
        - Multiple format support (JSON, MessagePack, Avro, etc.)
        - Schema validation and evolution
        - Compression and optimization
        - Cross-platform compatibility
        - Performance optimization
    """

    async def serialize(
        self,
        data: Any,
        format: LiteralSerializationFormat = "json",
        schema: dict[str, Any] | None = None,
    ) -> bytes: ...

    async def deserialize(
        self,
        data: bytes,
        format: LiteralSerializationFormat = "json",
        schema: dict[str, Any] | None = None,
    ) -> Any: ...

    async def validate_schema(
        self, data: Any, schema: dict[str, Any]
    ) -> ProtocolValidationResult: ...

    async def get_supported_formats(self) -> list[LiteralSerializationFormat]: ...

    async def optimize_serialization(
        self, data: Any, target_size_bytes: int
    ) -> bytes: ...
```

### URI Parser Protocol

```python
@runtime_checkable
class ProtocolUriParser(Protocol):
    """
    Protocol for URI parsing and validation.

    Provides consistent URI handling, validation, and transformation
    across ONEX services.

    Key Features:
        - URI parsing and validation
        - URI component extraction
        - URI transformation and normalization
        - Protocol-specific URI handling
        - URI security validation
    """

    async def parse_uri(self, uri: str) -> ProtocolUriComponents: ...

    async def validate_uri(self, uri: str) -> bool: ...

    async def normalize_uri(self, uri: str) -> str: ...

    async def extract_components(self, uri: str) -> dict[str, str]: ...

    async def build_uri(
        self,
        scheme: str,
        host: str,
        port: int | None = None,
        path: str | None = None,
        query: dict[str, str] | None = None,
        fragment: str | None = None,
    ) -> str: ...

    async def is_secure_uri(self, uri: str) -> bool: ...
```

### Version Manager Protocol

```python
@runtime_checkable
class ProtocolVersionManager(Protocol):
    """
    Protocol for version management and compatibility.

    Provides version checking, compatibility validation, and
    version-based feature management across ONEX services.

    Key Features:
        - Version comparison and validation
        - Compatibility checking
        - Version-based feature flags
        - Migration path planning
        - Version deprecation management
    """

    async def get_current_version(self) -> ProtocolSemVer: ...

    async def compare_versions(
        self, version1: str, version2: str
    ) -> LiteralVersionComparison: ...

    async def is_compatible(
        self, required_version: str, current_version: str
    ) -> bool: ...

    async def get_migration_path(
        self, from_version: str, to_version: str
    ) -> list[ProtocolMigrationStep]: ...

    async def check_deprecation(
        self, version: str
    ) -> ProtocolDeprecationInfo | None: ...

    async def get_feature_flags(
        self, version: str
    ) -> dict[str, bool]: ...
```

## 🔧 Type Definitions

### Health Status Types

```python
LiteralHealthStatus = Literal[
    "healthy", "degraded", "unhealthy", "critical", "unknown",
    "warning", "unreachable", "available", "unavailable",
    "initializing", "disposing", "error"
]
"""
Health status indicators for system components.

Values:
    healthy: Component is operating normally
    degraded: Component is operating with reduced functionality
    unhealthy: Component is not operating correctly
    critical: Component has critical issues requiring immediate attention
    unknown: Health status cannot be determined
    warning: Component has minor issues
    unreachable: Component cannot be reached
    available: Component is available for use
    unavailable: Component is not available
    initializing: Component is starting up
    disposing: Component is shutting down
    error: Component encountered an error
"""

LiteralHealthCheckLevel = Literal["quick", "standard", "comprehensive"]
"""
Health check levels for different monitoring scenarios.

Values:
    quick: Fast health check for basic status
    standard: Standard health check with key metrics
    comprehensive: Full health check with detailed analysis
"""

LiteralHealthDimension = Literal[
    "availability", "performance", "security", "reliability", "scalability"
]
"""
Health dimensions for multi-dimensional health assessment.

Values:
    availability: Service availability and uptime
    performance: Response times and throughput
    security: Security posture and vulnerabilities
    reliability: Error rates and stability
    scalability: Resource utilization and capacity
"""
```

### Logging Types

```python
LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]
"""
Log severity levels used throughout the system.

Values:
    TRACE: Most detailed logging for debugging
    DEBUG: Detailed diagnostic information
    INFO: General informational messages
    WARNING: Warning conditions
    ERROR: Error conditions
    CRITICAL: Critical error conditions
    FATAL: Fatal error requiring immediate attention
"""
```

## 🚀 Usage Examples

### Health Monitoring

```python
from omnibase_spi.protocols.core import ProtocolHealthMonitor

# Initialize health monitor
health_monitor: ProtocolHealthMonitor = get_health_monitor()

# Perform health check
health_check = await health_monitor.perform_health_check(
    level="standard",
    dimensions=["availability", "performance"]
)

# Get current status
status = await health_monitor.get_current_health_status()
print(f"Service status: {status}")

# Register dependency
await health_monitor.register_health_dependency(
    "database", database_health_monitor
)
```

### Structured Logging

```python
from omnibase_spi.protocols.core import ProtocolLogger

# Initialize logger
logger: ProtocolLogger = get_logger()

# Structured logging
await logger.log_structured(
    level="INFO",
    event="user_login",
    data={
        "user_id": "12345",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    },
    correlation_id="req-abc123"
)

# Performance logging
await logger.log_performance(
    operation="database_query",
    duration_ms=45.2,
    metadata={"query_type": "SELECT", "rows_returned": 150}
)
```

### Service Discovery

```python
from omnibase_spi.protocols.core import ProtocolServiceDiscovery

# Initialize service discovery
discovery: ProtocolServiceDiscovery = get_service_discovery()

# Register service
service_id = await discovery.register_service(
    service_name="user-service",
    service_url="http://user-service:8080",
    metadata={"version": "1.2.3", "region": "us-east-1"},
    health_check_url="http://user-service:8080/health"
)

# Discover services
services = await discovery.discover_services(
    service_name="user-service",
    healthy_only=True,
    tags=["production", "api"]
)
```

### Error Handling

```python
from omnibase_spi.protocols.core import ProtocolErrorHandler

# Initialize error handler
error_handler: ProtocolErrorHandler = get_error_handler()

# Handle error with recovery
result = await error_handler.handle_error(
    error=DatabaseConnectionError("Connection timeout"),
    context={"operation": "user_lookup", "user_id": "12345"},
    recovery_strategy="retry_with_backoff"
)

# Classify error
error_type = await error_handler.classify_error(error)
print(f"Error type: {error_type}")
```

### Performance Metrics

```python
from omnibase_spi.protocols.core import ProtocolPerformanceMetrics

# Initialize metrics
metrics: ProtocolPerformanceMetrics = get_performance_metrics()

# Record metrics
await metrics.record_metric(
    metric_name="response_time",
    value=125.5,
    tags={"service": "user-api", "endpoint": "/users"}
)

# Record timing
await metrics.record_timing(
    operation="database_query",
    duration_ms=45.2,
    metadata={"query": "SELECT * FROM users"}
)

# Get performance summary
summary = await metrics.get_performance_summary(time_range_hours=24)
print(f"Average response time: {summary.avg_response_time_ms}ms")
```

## 🔍 Implementation Notes

### Health Monitoring Patterns

The core protocols support comprehensive health monitoring:

```python
# Multi-level health checks
quick_check = await health_monitor.perform_health_check("quick", ["availability"])
standard_check = await health_monitor.perform_health_check("standard", ["availability", "performance"])
comprehensive_check = await health_monitor.perform_health_check("comprehensive", ["availability", "performance", "security"])

# Dependency health
dependency_health = await health_monitor.get_dependency_health_status("database")
```

### Structured Logging Patterns

Consistent logging across all services:

```python
# Correlation ID tracking
logger.set_correlation_id("req-abc123")
await logger.log("INFO", "Processing request", {"user_id": "12345"})

# Audit logging
await logger.log_audit(
    action="user_login",
    user_id="12345",
    resource="authentication_service",
    details={"ip_address": "192.168.1.100"}
)
```

### Service Discovery Patterns

Dynamic service discovery and load balancing:

```python
# Service change notifications
subscription_id = await discovery.subscribe_to_service_changes(
    "user-service",
    callback=lambda services: print(f"Services updated: {len(services)}")
)

# Health-based filtering
healthy_services = await discovery.discover_services(
    "user-service",
    healthy_only=True
)
```

## 🔧 Type Protocols

### Contract Protocol

```python
from omnibase_spi.protocols.types import ProtocolContract

@runtime_checkable
class ProtocolContract(Protocol):
    """
    Protocol for ONEX contract objects.

    Defines the interface for contract objects in the ONEX distributed system,
    including identification, versioning, metadata management, and serialization.
    Contracts define behavioral agreements between system components.

    Key Features:
        - Unique contract identification
        - Semantic versioning support
        - Extensible metadata dictionary
        - Bidirectional serialization (to/from dict)
    """

    @property
    def contract_id(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def metadata(self) -> Dict[str, Any]: ...

    def to_dict(self) -> Dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProtocolContract": ...
```

#### Usage

```python
from omnibase_spi.protocols.types import ProtocolContract

# Get contract instance
contract: ProtocolContract = get_contract()

# Access contract properties
contract_id = contract.contract_id
version = contract.version
metadata = contract.metadata

# Serialization
contract_dict = contract.to_dict()

# Deserialization
restored_contract = ContractImpl.from_dict(contract_dict)
```

### ONEX Error Protocol

```python
from omnibase_spi.protocols.types import ProtocolOnexError

@runtime_checkable
class ProtocolOnexError(Protocol):
    """
    Protocol for ONEX error objects.

    Provides standardized error representation across ONEX services with
    categorization, context, and serialization support. Used for consistent
    error handling and reporting throughout distributed systems.

    Key Features:
        - Error code classification for programmatic handling
        - Human-readable error messages for user feedback
        - Error categorization (validation/execution/configuration)
        - Optional context for debugging and diagnostics
        - Dictionary serialization for transmission and logging

    Error Categories:
        - validation: Input validation failures, schema violations
        - execution: Runtime errors, processing failures
        - configuration: Configuration errors, initialization failures
    """

    @property
    def error_code(self) -> str: ...

    @property
    def error_message(self) -> str: ...

    @property
    def error_category(self) -> str: ...

    @property
    def context(self) -> dict[str, object] | None: ...

    def to_dict(self) -> dict[str, object]: ...
```

#### Usage

```python
from omnibase_spi.protocols.types import ProtocolOnexError

# Create error instance
error: ProtocolOnexError = create_onex_error(
    error_code="VALIDATION_FAILED",
    error_message="Invalid workflow configuration",
    error_category="validation",
    context={"field": "timeout", "value": -1}
)

# Programmatic error handling
if error.error_code == "VALIDATION_FAILED":
    handle_validation_error(error)

# Logging and serialization
logger.error(f"Error: {error.error_message}", extra=error.to_dict())
```

## 📊 Protocol Statistics

- **Total Protocols**: 13 core protocols
- **Type Protocols**: 14 type definition protocols (including ProtocolContract, ProtocolOnexError)
- **Health Monitoring**: Multi-level health checks with dependency tracking
- **Logging**: Structured logging with correlation ID support
- **Service Discovery**: Dynamic service registration and discovery
- **Error Handling**: Centralized error handling with recovery strategies
- **Performance Metrics**: Comprehensive performance monitoring and analysis
- **Serialization**: Multiple format support with schema validation
- **URI Handling**: URI parsing, validation, and normalization
- **Version Management**: Version compatibility and migration support

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*

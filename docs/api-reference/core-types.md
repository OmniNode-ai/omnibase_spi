# Core Types API Reference

## Overview

Core type definitions and fundamental protocols that serve as the foundation for all ONEX SPI interfaces. These types provide strong typing, consistent data structures, and base contracts used throughout the system.

## Type Aliases

### System Types

#### `LogLevel`
```python
LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]
```

Log severity levels used throughout the system.

**Values:**
- `TRACE`: Most detailed logging for debugging
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical error conditions
- `FATAL`: Fatal error requiring immediate attention

#### `NodeType`
```python
NodeType = Literal["COMPUTE", "EFFECT", "REDUCER", "ORCHESTRATOR"]
```

Types of nodes in the ONEX distributed system.

**Values:**
- `COMPUTE`: Computational processing nodes
- `EFFECT`: Side-effect handling nodes (I/O, external calls)
- `REDUCER`: State reduction and aggregation nodes
- `ORCHESTRATOR`: Workflow orchestration and coordination nodes

#### `HealthStatus`
```python
HealthStatus = Literal[
    "healthy", "degraded", "unhealthy", "critical", "unknown",
    "warning", "unreachable", "available", "unavailable",
    "initializing", "disposing", "error"
]
```

Health status indicators for system components.

**Values:**
- `healthy`: Component operating normally
- `degraded`: Component operating with reduced functionality
- `unhealthy`: Component not operating correctly
- `critical`: Component in critical failure state
- `unknown`: Health status cannot be determined
- `warning`: Component operating with warnings
- `unreachable`: Component cannot be contacted
- `available`: Component is available for work
- `unavailable`: Component is not available for work
- `initializing`: Component is starting up
- `disposing`: Component is shutting down
- `error`: Component has encountered an error

### Context and Configuration Types

#### `ContextValue`
```python
ContextValue = str | int | float | bool | list[str] | dict[str, str]
```

Allowed types for context values in logging and metadata. This union ensures type safety while providing flexibility for different data types.

**Supported Types:**
- `str`: String values
- `int`: Integer values  
- `float`: Floating-point values
- `bool`: Boolean values
- `list[str]`: Lists of strings only
- `dict[str, str]`: String-keyed dictionaries with string values

#### `BaseStatus`
```python
BaseStatus = Literal["pending", "processing", "completed", "failed", "cancelled", "skipped"]
```

Base status values used across different operations.

#### `OperationStatus`
```python
OperationStatus = Literal["success", "failed", "in_progress", "cancelled", "pending"]
```

Status values for operation tracking.

### Validation Types

#### `ValidationLevel`
```python
ValidationLevel = Literal["BASIC", "STANDARD", "COMPREHENSIVE", "PARANOID"]
```

Levels of validation intensity.

**Values:**
- `BASIC`: Minimal validation for performance
- `STANDARD`: Standard validation for most use cases
- `COMPREHENSIVE`: Thorough validation for critical operations
- `PARANOID`: Maximum validation for security-critical operations

#### `ValidationMode`
```python
ValidationMode = Literal["strict", "lenient", "smoke", "regression", "integration"]
```

Validation modes for different testing scenarios.

## Protocol Classes

### Core Protocols

#### `ProtocolSemVer`
```python
@runtime_checkable
class ProtocolSemVer(Protocol):
    """Protocol for semantic version objects."""

    major: int
    minor: int  
    patch: int

    def __str__(self) -> str:
        """Return string representation (e.g., '1.2.3')."""
        ...
```

Semantic version protocol ensuring consistent version handling across the system.

**Properties:**
- `major`: Major version number (breaking changes)
- `minor`: Minor version number (new features)
- `patch`: Patch version number (bug fixes)

**Methods:**
- `__str__()`: Returns version as string (e.g., "1.2.3")

#### `ProtocolLogEntry`
```python
@runtime_checkable
class ProtocolLogEntry(Protocol):
    """Protocol for log entry objects."""

    level: LogLevel
    message: str
    correlation_id: UUID
    timestamp: ProtocolDateTime
    context: dict[str, ContextValue]
```

Structured log entry protocol for consistent logging across the system.

**Properties:**
- `level`: Log severity level
- `message`: Human-readable log message
- `correlation_id`: Request correlation identifier
- `timestamp`: When the log entry was created
- `context`: Additional structured context data

#### `ProtocolValidationResult`
```python
class ProtocolValidationResult(Protocol):
    """Protocol for validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
```

Standard validation result structure.

**Properties:**
- `is_valid`: Whether validation passed
- `errors`: List of validation error messages
- `warnings`: List of validation warning messages

### Metadata Protocols

#### `ProtocolMetadata`
```python
@runtime_checkable
class ProtocolMetadata(Protocol):
    """Protocol for structured metadata."""

    data: dict[str, ContextValue]
    version: ProtocolSemVer
    created_at: ProtocolDateTime
    updated_at: Optional[ProtocolDateTime]
```

Metadata protocol for data structures requiring version tracking and timestamps.

**Properties:**
- `data`: Key-value metadata pairs
- `version`: Semantic version of the metadata schema
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

#### `ProtocolMetadataOperations`
```python
class ProtocolMetadataOperations(Protocol):
    """Protocol for metadata operations."""

    def get_value(self, key: str) -> ContextValue: ...
    def has_key(self, key: str) -> bool: ...
    def keys(self) -> list[str]: ...
    def update_value(self, key: str, value: ContextValue) -> None: ...
```

Operations protocol for manipulating metadata.

**Methods:**
- `get_value(key)`: Retrieve value by key
- `has_key(key)`: Check if key exists
- `keys()`: Get all available keys
- `update_value(key, value)`: Update or set a key-value pair

### Configuration Protocols

#### `ProtocolConfigValue`
```python
class ProtocolConfigValue(Protocol):
    """Protocol for configuration values."""

    key: str
    value: ContextValue
    config_type: Literal["string", "int", "float", "bool", "list"]
    default_value: Optional[ContextValue]
```

Configuration value protocol with type information.

**Properties:**
- `key`: Configuration key identifier
- `value`: Current configuration value
- `config_type`: Type of the configuration value
- `default_value`: Default value if not set

### Cache Statistics

#### `ProtocolCacheStatistics`
```python
@runtime_checkable
class ProtocolCacheStatistics(Protocol):
    """Protocol for structured cache service statistics."""

    hit_count: int
    miss_count: int
    total_requests: int
    hit_ratio: float
    memory_usage_bytes: int
    entry_count: int
    eviction_count: int
    last_accessed: Optional[datetime]
    cache_size_limit: Optional[int]
```

Comprehensive cache performance statistics protocol.

**Properties:**
- `hit_count`: Number of cache hits
- `miss_count`: Number of cache misses
- `total_requests`: Total cache requests
- `hit_ratio`: Cache hit ratio (0.0-1.0)
- `memory_usage_bytes`: Memory consumed by cache
- `entry_count`: Number of cached entries
- `eviction_count`: Number of evicted entries
- `last_accessed`: Last access timestamp
- `cache_size_limit`: Maximum cache size limit

### State and Action Protocols

#### `ProtocolAction`
```python
class ProtocolAction(Protocol):
    """Protocol for reducer actions."""

    type: str
    payload: ProtocolActionPayload
    timestamp: ProtocolDateTime
```

Action protocol for state reduction patterns.

#### `ProtocolActionPayload`
```python
class ProtocolActionPayload(Protocol):
    """Protocol for action payload with specific data."""

    target_id: str
    operation: str
    parameters: dict[str, ContextValue]
```

Action payload with typed parameters.

#### `ProtocolState`
```python
class ProtocolState(Protocol):
    """Protocol for reducer state."""

    metadata: ProtocolMetadata
    version: int  # Sequence number, not semver
    last_updated: ProtocolDateTime
```

State protocol for reducer pattern implementations.

### Error and Result Protocols

#### `ProtocolErrorInfo`
```python
class ProtocolErrorInfo(Protocol):
    """Protocol for error information in results."""

    error_type: str
    message: str
    trace: Optional[str]
    retryable: bool
    backoff_strategy: Optional[str]
    max_attempts: Optional[int]
```

Comprehensive error information protocol.

**Properties:**
- `error_type`: Classification of the error
- `message`: Human-readable error message
- `trace`: Optional stack trace
- `retryable`: Whether the operation can be retried
- `backoff_strategy`: Retry backoff strategy
- `max_attempts`: Maximum retry attempts

#### `ProtocolNodeResult`
```python
class ProtocolNodeResult(Protocol):
    """Protocol for node processing results with monadic composition."""

    value: Optional[ContextValue]
    is_success: bool
    is_failure: bool
    error: Optional[ProtocolErrorInfo]
    trust_score: float
    provenance: list[str]
    metadata: dict[str, ContextValue]
    events: list[ProtocolSystemEvent]
    state_delta: dict[str, ContextValue]
```

Rich result protocol supporting monadic composition patterns.

**Properties:**
- `value`: Optional result value
- `is_success`: Success indicator
- `is_failure`: Failure indicator
- `error`: Optional error information
- `trust_score`: Confidence score (0.0-1.0)
- `provenance`: Processing history chain
- `metadata`: Additional result metadata
- `events`: Generated system events
- `state_delta`: State changes caused by processing

## Usage Examples

### Basic Type Usage

```python
from omnibase_spi.protocols.types.core_types import (
    LogLevel, ContextValue, ProtocolValidationResult
)

# Type-safe context values
context: dict[str, ContextValue] = {
    "user_id": "12345",
    "request_count": 42,
    "is_authenticated": True,
    "tags": ["api", "production"]
}

# Log levels
log_level: LogLevel = "INFO"

# Validation result
def validate_input(data: str) -> ProtocolValidationResult:
    return ProtocolValidationResult(
        is_valid=len(data) > 0,
        errors=[] if len(data) > 0 else ["Input cannot be empty"],
        warnings=[]
    )
```

### Metadata Protocol Usage

```python
from omnibase_spi.protocols.types.core_types import (
    ProtocolMetadata, ProtocolSemVer
)
from datetime import datetime

# Create metadata
metadata = ProtocolMetadata(
    data={"component": "api-gateway", "environment": "production"},
    version=ProtocolSemVer(major=1, minor=2, patch=3),
    created_at=datetime.now(),
    updated_at=None
)
```

### Configuration Protocol Usage

```python
from omnibase_spi.protocols.types.core_types import ProtocolConfigValue

# Type-safe configuration
config = ProtocolConfigValue(
    key="max_connections",
    value=100,
    config_type="int",
    default_value=50
)
```

## Integration Notes

### Type Safety

All core types are designed for maximum type safety:

```python
from typing import TYPE_CHECKING
from omnibase_spi.protocols.types.core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import ProtocolValidationResult

def process_data(value: ContextValue) -> "ProtocolValidationResult":
    # Type checker knows ContextValue constraints
    if isinstance(value, str):
        # String-specific processing
        return validate_string(value)
    elif isinstance(value, int):
        # Integer-specific processing  
        return validate_integer(value)
    # ... handle other types
```

### Protocol Compliance

Use runtime checking to validate implementations:

```python
from omnibase_spi.protocols.types.core_types import ProtocolMetadata

def process_metadata(obj: object) -> None:
    if isinstance(obj, ProtocolMetadata):
        # obj is guaranteed to have required attributes
        print(f"Version: {obj.version}")
        print(f"Created: {obj.created_at}")
    else:
        raise ValueError("Object does not implement ProtocolMetadata")
```

### Error Handling

Leverage rich error protocols for better debugging:

```python
from omnibase_spi.protocols.types.core_types import ProtocolErrorInfo

def create_error_info(
    error_type: str,
    message: str,
    retryable: bool = False
) -> ProtocolErrorInfo:
    return ProtocolErrorInfo(
        error_type=error_type,
        message=message,
        trace=None,
        retryable=retryable,
        backoff_strategy="exponential" if retryable else None,
        max_attempts=3 if retryable else None
    )
```

## Best Practices

### Use Type Constraints

```python
# Good - uses type constraints
def log_context(context: dict[str, ContextValue]) -> None:
    # Type checker ensures values are valid ContextValue types
    pass

# Avoid - no type constraints
def log_context_bad(context: dict[str, Any]) -> None:
    # Any type defeats the purpose of type safety
    pass
```

### Leverage Protocol Inheritance

```python
from typing import Protocol
from omnibase_spi.protocols.types.core_types import ProtocolMetadata

class ProtocolEnhancedMetadata(ProtocolMetadata, Protocol):
    """Extended metadata protocol with additional fields."""
    tags: list[str]
    priority: int
```

### Validate at Runtime

```python
from omnibase_spi.protocols.types.core_types import ProtocolValidationResult

def validate_user_input(obj: object) -> bool:
    if isinstance(obj, ProtocolValidationResult):
        return obj.is_valid and len(obj.errors) == 0
    return False
```

---

*This documentation covers all core types and fundamental protocols. For domain-specific protocols, see the respective API reference sections.*

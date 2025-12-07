# Handler Protocols API Reference

![Version](https://img.shields.io/badge/SPI-v0.3.0-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.1.0-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [ProtocolHandler](#protocolhandler)
  - [Description](#description)
  - [Migration Note](#migration-note)
  - [Properties](#properties)
  - [Methods](#methods)
    - [handler_type](#handler_type-property)
    - [initialize](#initialize)
    - [shutdown](#shutdown)
    - [execute](#execute)
    - [describe](#describe)
    - [health_check](#health_check)
  - [Protocol Definition](#protocol-definition)
  - [Lifecycle Diagram](#lifecycle-diagram)
  - [Usage Example](#usage-example)
  - [Handler Type Implementations](#handler-type-implementations)
- [Exception Handling](#exception-handling)
- [Best Practices](#best-practices)
- [Version Information](#version-information)

---

## Overview

The handler protocols define interfaces for protocol-specific I/O handlers in the ONEX platform. Handlers encapsulate the complexity of communicating with external systems (HTTP APIs, databases, message queues) and provide a consistent interface for effect nodes.

## Architecture

Handlers follow a **dependency injection pattern** where [effect nodes](./NODES.md#protocoleffectnode) receive handlers through their constructors, enabling:

- **Loose coupling**: Nodes depend on protocols, not implementations
- **Testability**: Mock handlers for unit testing
- **Flexibility**: Swap implementations without changing node code
- **Lifecycle management**: Consistent initialize/execute/shutdown pattern

```text
ProtocolEffectNode
    |
    +-- uses --> ProtocolHandler (injected)
                     |
                     +-- HttpRestHandler (implementation)
                     +-- PostgresHandler (implementation)
                     +-- KafkaHandler (implementation)
                     +-- BoltHandler (implementation)
```

---

## ProtocolHandler

```python
from omnibase_spi.protocols.handlers import ProtocolHandler
```

### Description

Protocol for protocol-specific handlers (HTTP, Kafka, DB, etc.). This interface enables dependency injection of I/O handlers into effect nodes without tight coupling.

Implementations live in `omnibase_core` or `omnibase_infra`. This is the canonical name as of v0.3.0.

**Handler vs Event Bus Distinction**:
- `ProtocolHandler` is for **request-response I/O operations** where a direct response is expected
- [Event bus protocols](./EVENT-BUS.md) (`ProtocolEventPublisher`/`ProtocolEventConsumer`) handle **asynchronous, fire-and-forget** message passing
- Handlers are typically used within [effect nodes](./NODES.md#protocoleffectnode) to perform external calls
- Event bus protocols coordinate inter-service communication

**Example Implementations**:
- `HttpRestHandler`: HTTP/REST API calls
- `BoltHandler`: Neo4j Cypher queries
- `PostgresHandler`: SQL queries via asyncpg
- `KafkaHandler`: Message publishing

### Migration Note

`ProtocolHandlerV3` was the versioned name during the protocol evolution. As of v0.3.0, `ProtocolHandler` is the canonical name. `ProtocolHandlerV3` is provided as a backwards-compatible alias but will be removed in v0.5.0.

```python
# Old (deprecated)
from omnibase_spi.protocols import ProtocolHandlerV3

# New (recommended)
from omnibase_spi.protocols import ProtocolHandler
```

The protocols are identical - no code changes are needed beyond updating the import statement.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `handler_type` | `str` | Handler type identifier (e.g., `"http"`, `"kafka"`, `"postgresql"`) |

### Methods

#### `handler_type` (property)

```python
@property
def handler_type(self) -> str:
    ...
```

The type of handler as a string identifier.

Used for handler identification, routing, and metrics collection. Implementations should return a consistent, lowercase string identifier that matches the corresponding `EnumHandlerType` values in `omnibase_core`.

**Note**: The return type is `str` (not `EnumHandlerType`) by design to maintain SPI/Core decoupling. Implementations may use `EnumHandlerType.value` or return the string directly.

**Common Values**: `"http"`, `"kafka"`, `"postgresql"`, `"neo4j"`, `"redis"`, `"grpc"`, `"websocket"`, `"file"`, `"memory"`

#### `initialize`

```python
async def initialize(
    self,
    config: ModelConnectionConfig,
) -> None:
    ...
```

Initialize any clients or connection pools.

**Args**:
- `config` (`ModelConnectionConfig`): Connection configuration including URL, auth, pool settings

**Raises**:
- `HandlerInitializationError`: If initialization fails

**Semantic Contract**:
- MUST establish connections or prepare connection pools
- MUST validate configuration before proceeding
- SHOULD be idempotent (safe to call multiple times)
- MUST NOT perform operations that require `execute()` to be called

#### `shutdown`

```python
async def shutdown(self, timeout_seconds: float = 30.0) -> None:
    ...
```

Release resources and close connections.

Should flush pending operations and release all resources gracefully.

**Args**:
- `timeout_seconds` (`float`): Maximum time to wait for shutdown to complete. Defaults to 30.0 seconds.

**Raises**:
- `TimeoutError`: If shutdown does not complete within the specified timeout

**Semantic Contract**:
- MUST close all open connections
- MUST release all held resources
- SHOULD flush pending operations before closing
- MUST NOT raise exceptions other than `TimeoutError`

#### `execute`

```python
async def execute(
    self,
    request: ModelProtocolRequest,
    operation_config: ModelOperationConfig,
) -> ModelProtocolResponse:
    ...
```

Execute a protocol-specific operation.

**Args**:
- `request` (`ModelProtocolRequest`): Protocol-agnostic request model from `omnibase_core`
- `operation_config` (`ModelOperationConfig`): Operation-specific config from `omnibase_core`

**Returns**:
- `ModelProtocolResponse`: Protocol-agnostic response model from `omnibase_core`

**Raises**:
- `ProtocolHandlerError`: If execution fails
- `InvalidProtocolStateError`: If called before `initialize()`

**Semantic Contract**:
- MUST be called after `initialize()`
- MUST translate between protocol-agnostic models and protocol-specific operations
- SHOULD handle transient failures with appropriate retry logic (if configured)
- MUST propagate errors appropriately

#### `describe`

```python
def describe(self) -> dict[str, Any]:
    ...
```

Return handler metadata and capabilities.

Provides introspection information about the handler including its type, supported operations, connection status, and any handler-specific capabilities.

**Returns**:
- `dict[str, Any]`: Dictionary containing handler metadata:
  - `handler_type`: The handler type (string representation)
  - `capabilities`: List of supported operations/features
  - `version`: Handler implementation version (optional)
  - `connection_info`: Non-sensitive connection details (optional)

**Raises**:
- `HandlerNotInitializedError`: If called before `initialize()`

**Security Warning**:

NEVER include in output:
- Credentials (passwords, API keys, tokens, secrets)
- Full connection strings with authentication details
- Internal file paths or system configuration details
- PII or sensitive business data

**Safe Example**:
```python
{
    "handler_type": "postgresql",
    "host": "db.example.com",
    "port": 5432,
    "database": "myapp",
    "capabilities": ["read", "write", "transactions"]
}
```

**UNSAFE Example (DO NOT DO THIS)**:
```python
{
    "handler_type": "postgresql",
    "connection_string": "postgresql://admin:secret123@db.example.com:5432/mydb",
    "api_key": "[REDACTED]"  # Never include actual keys
}
```

#### `health_check`

```python
async def health_check(self) -> dict[str, Any]:
    ...
```

Check handler health and connectivity.

Performs a lightweight check to verify the handler is operational and can communicate with its backing service.

**Returns**:
- `dict[str, Any]`: Dictionary containing health status:
  - `healthy`: Boolean indicating overall health
  - `latency_ms`: Response time in milliseconds (optional)
  - `details`: Additional diagnostic information (optional)
  - `last_error`: Most recent error message if unhealthy (optional)

**Raises**:
- `HandlerNotInitializedError`: If called before `initialize()`

**Caching**:
Implementations SHOULD cache health check results for 5-30 seconds to avoid overwhelming the backend service with repeated health probes.

**Security**:
The `last_error` field may contain sensitive information from exception messages. Implementations SHOULD sanitize error messages before including them by:
- Removing credentials from connection error text
- Redacting internal file paths and system details
- Using generic error categories when possible

**Example of sanitized error**:
```python
{"healthy": False, "last_error": "Connection timeout to database"}
```

**Instead of (UNSAFE)**:
```python
{"healthy": False, "last_error": "Connection to postgresql://user:pass@host failed"}
```

### Protocol Definition

```python
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class ProtocolHandler(Protocol):
    """
    Protocol for protocol-specific handlers (HTTP, Kafka, DB, etc.).

    Implementations live in omnibase_core or omnibase_infra.
    This interface enables dependency injection of I/O handlers
    into effect nodes without tight coupling.
    """

    @property
    def handler_type(self) -> str:
        """The type of handler as a string identifier."""
        ...

    async def initialize(
        self,
        config: ModelConnectionConfig,
    ) -> None:
        """Initialize any clients or connection pools."""
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections."""
        ...

    async def execute(
        self,
        request: ModelProtocolRequest,
        operation_config: ModelOperationConfig,
    ) -> ModelProtocolResponse:
        """Execute a protocol-specific operation."""
        ...

    def describe(self) -> dict[str, Any]:
        """Return handler metadata and capabilities."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Check handler health and connectivity."""
        ...
```

### Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> Created
    Created --> Initialized : initialize()

    Initialized --> Initialized : execute()
    Initialized --> Initialized : health_check()
    Initialized --> Initialized : describe()

    Initialized --> Closed : shutdown()
    Closed --> [*]

    note right of Created : Handler instance created
    note right of Initialized : Ready for operations
    note right of Closed : Resources released
```

### Handler Dependency Injection Pattern

The following diagram shows how effect nodes depend on the `ProtocolHandler` protocol, and how various handler implementations satisfy that contract:

```mermaid
flowchart TB
    subgraph EffectNode["ProtocolEffectNode"]
        N[Effect Node]
    end

    subgraph Handlers["Handler Implementations"]
        H1[HttpRestHandler]
        H2[PostgresHandler]
        H3[KafkaHandler]
        H4[BoltHandler]
    end

    subgraph Protocol["Protocol Contract"]
        P[ProtocolHandler]
    end

    N -->|uses| P
    H1 -.->|implements| P
    H2 -.->|implements| P
    H3 -.->|implements| P
    H4 -.->|implements| P
```

### Usage Example

```python
import asyncio
import time
from typing import Any

from omnibase_spi.protocols.handlers import ProtocolHandler
from omnibase_spi.exceptions import (
    HandlerInitializationError,
    HandlerNotInitializedError,
    InvalidProtocolStateError,
    ProtocolHandlerError,
)
from omnibase_core.models.protocol import (
    ModelConnectionConfig,
    ModelOperationConfig,
    ModelProtocolRequest,
    ModelProtocolResponse,
)


class HttpRestHandler:
    """Example HTTP REST handler implementation.

    Note: This is an illustrative example. A real implementation would
    use an HTTP client library like httpx or aiohttp.

    Production-ready implementations live in omnibase_infra:
    https://github.com/OmniNode-ai/omnibase_infra
    """

    def __init__(self) -> None:
        self._client: Any = None  # Would be httpx.AsyncClient or similar
        self._config: ModelConnectionConfig | None = None

    async def _create_client(self, config: ModelConnectionConfig) -> Any:
        """Create the HTTP client. Implementation would use httpx, aiohttp, etc."""
        # Example: return httpx.AsyncClient(base_url=config.base_url)
        raise NotImplementedError("Use httpx.AsyncClient or similar")

    @property
    def handler_type(self) -> str:
        return "http"

    async def initialize(
        self,
        config: ModelConnectionConfig,
    ) -> None:
        """Initialize HTTP client with connection pool."""
        try:
            self._config = config
            self._client = await self._create_client(config)
        except Exception as e:
            raise HandlerInitializationError(
                f"Failed to initialize HTTP client: {e}",
                context={"base_url": config.base_url}
            )

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Close HTTP client connections."""
        if self._client:
            await asyncio.wait_for(
                self._client.close(),
                timeout=timeout_seconds
            )
            self._client = None

    async def execute(
        self,
        request: ModelProtocolRequest,
        operation_config: ModelOperationConfig,
    ) -> ModelProtocolResponse:
        """Execute HTTP request."""
        if not self._client:
            raise InvalidProtocolStateError(
                "Cannot call execute() before initialize()"
            )

        try:
            response = await self._client.request(
                method=operation_config.method,
                url=request.url,
                headers=request.headers,
                json=request.body,
                timeout=operation_config.timeout_seconds,
            )
            return ModelProtocolResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.json(),
            )
        except Exception as e:
            raise ProtocolHandlerError(
                f"HTTP request failed: {e}",
                context={
                    "url": request.url,
                    "method": operation_config.method,
                }
            )

    def describe(self) -> dict[str, Any]:
        """Return handler metadata."""
        if not self._config:
            raise HandlerNotInitializedError("Handler not initialized")
        return {
            "handler_type": self.handler_type,
            "base_url": self._config.base_url,
            "capabilities": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "version": "1.0.0",
        }

    async def health_check(self) -> dict[str, Any]:
        """Check HTTP connectivity."""
        if not self._client or not self._config:
            raise HandlerNotInitializedError("Handler not initialized")

        start = time.monotonic()
        try:
            await self._client.get(f"{self._config.base_url}/health")
            latency = (time.monotonic() - start) * 1000
            return {"healthy": True, "latency_ms": latency}
        except Exception as e:
            return {
                "healthy": False,
                "last_error": "Connection failed",  # Sanitized
            }

# Usage with effect node
async def main() -> None:
    # These would be provided by your application configuration
    connection_config = ModelConnectionConfig(
        base_url="https://api.example.com",
        # ... other config options
    )
    request = ModelProtocolRequest(
        url="/users",
        headers={"Content-Type": "application/json"},
        body={"name": "Example User"},
    )
    operation_config = ModelOperationConfig(
        method="POST",
        timeout_seconds=30.0,
    )

    handler = HttpRestHandler()
    await handler.initialize(connection_config)

    try:
        # Check health before operations
        health = await handler.health_check()
        if health["healthy"]:
            response = await handler.execute(request, operation_config)
            print(f"Response status: {response.status_code}")
    finally:
        await handler.shutdown()
```

### Handler Type Implementations

| Handler Type | Protocol | Use Case |
|--------------|----------|----------|
| `http` | HTTP/REST | REST APIs, webhooks |
| `grpc` | gRPC | Service-to-service RPC |
| `kafka` | Kafka | Event streaming |
| `postgresql` | PostgreSQL | Relational database |
| `neo4j` / `bolt` | Bolt | Graph database |
| `redis` | Redis | Caching, pub/sub |
| `websocket` | WebSocket | Real-time communication |
| `file` | File system | Local file I/O |
| `memory` | In-memory | Testing, development |

---

## Exception Handling

Handler methods may raise the following exceptions:

| Exception | Method | When |
|-----------|--------|------|
| `HandlerInitializationError` | `initialize()` | Connection/setup failures |
| `ProtocolHandlerError` | `execute()` | Request execution failures |
| `InvalidProtocolStateError` | `execute()`, `describe()`, `health_check()` | Called before `initialize()` |
| `TimeoutError` | `shutdown()` | Shutdown exceeds timeout |

See [EXCEPTIONS.md](EXCEPTIONS.md) for complete exception hierarchy.

---

## Best Practices

### 1. Always Use Context Managers or Try/Finally

```python
handler = HttpRestHandler()
await handler.initialize(config)
try:
    result = await handler.execute(request, operation_config)
finally:
    await handler.shutdown()
```

### 2. Check Health Before Critical Operations

```python
health = await handler.health_check()
if not health["healthy"]:
    raise RuntimeError(f"Handler unhealthy: {health.get('last_error')}")
```

### 3. Never Log Credentials

```python
# BAD - exposes credentials
logger.info(f"Connecting to {config.connection_string}")

# GOOD - sanitized logging
logger.info(f"Connecting to {config.host}:{config.port}")
```

### 4. Cache Health Check Results

```python
from time import time
from typing import Any

_health_cache: dict[str, Any] = {}
_cache_ttl = 10  # seconds

async def health_check(self) -> dict[str, Any]:
    cache_key = self.handler_type
    cached = _health_cache.get(cache_key)
    if cached and time() - cached["timestamp"] < _cache_ttl:
        return cached["result"]

    result = await self._perform_health_check()
    _health_cache[cache_key] = {"result": result, "timestamp": time()}
    return result
```

---

## Version Information

- **API Version**: 0.3.0
- **Python Compatibility**: 3.12+
- **Type Checking**: mypy strict mode compatible
- **Runtime Checking**: All protocols are `@runtime_checkable`

---

## See Also

- **[NODES.md](./NODES.md)** - Node protocols that use handlers for I/O operations, especially [ProtocolEffectNode](./NODES.md#protocoleffectnode)
- **[REGISTRY.md](./REGISTRY.md)** - Handler registry for managing and discovering handlers
- **[EVENT-BUS.md](./EVENT-BUS.md)** - Event bus protocols for asynchronous messaging (alternative to request-response handlers)
- **[EXCEPTIONS.md](./EXCEPTIONS.md)** - Exception hierarchy including `HandlerInitializationError` and `ProtocolHandlerError`
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference is part of the omnibase_spi documentation.*

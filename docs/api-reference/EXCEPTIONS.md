# Exceptions API Reference

![Version](https://img.shields.io/badge/SPI-v0.23.1-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.1.0-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Exception Hierarchy](#exception-hierarchy)
- [Design Principles](#design-principles)
- [SPIError](#spierror)
  - [Constructor](#constructor)
  - [Usage Example](#usage-example)
- [ProtocolHandlerError](#protocolhandlererror)
  - [Usage Example](#usage-example-1)
  - [Common Scenarios](#common-scenarios)
- [HandlerInitializationError](#handlerinitializationerror)
  - [Usage Example](#usage-example-2)
  - [Security Note](#security-note)
- [HandlerDiscoveryError](#handlerdiscoveryerror)
- [IdempotencyStoreError](#idempotencystoreerror)
- [ContractCompilerError](#contractcompilererror)
  - [Usage Example](#usage-example-3)
  - [Common Scenarios](#common-scenarios-1)
- [RegistryError](#registryerror)
  - [Usage Example](#usage-example-4)
- [ProtocolNotImplementedError](#protocolnotimplementederror)
  - [Usage Example](#usage-example-5)
  - [Common Scenarios](#common-scenarios-2)
- [InvalidProtocolStateError](#invalidprotocolstateerror)
  - [Usage Example](#usage-example-6)
  - [Lifecycle State Machine](#lifecycle-state-machine)
- [ProjectorError](#projectorerror)
- [ProjectionReadError](#projectionreaderror)
- [SchemaError](#schemaerror)
- [TemplateError, TemplateNotFoundError, TemplateParseError](#templateerror-templatenotfounderror-templateparseerror)
- [Exception Handling Patterns](#exception-handling-patterns)
- [Exception Summary Table](#exception-summary-table)
- [Version Information](#version-information)

---

## Overview

The SPI exception hierarchy provides a structured approach to error handling across the ONEX platform. All SPI-related exceptions inherit from `SPIError`, enabling both broad exception handling and specific error categorization.

## Exception Hierarchy

```text
Exception (Python built-in)
    |
    +-- SPIError (base for all SPI errors)
            |
            +-- ProtocolHandlerError
            |       |
            |       +-- HandlerInitializationError
            |       +-- HandlerDiscoveryError
            |
            +-- IdempotencyStoreError
            |
            +-- ContractCompilerError
            |
            +-- RegistryError
            |
            +-- ProtocolNotImplementedError
            |
            +-- InvalidProtocolStateError
            |
            +-- ProjectorError
            |
            +-- ProjectionReadError
            |
            +-- SchemaError
            |
            +-- TemplateError
                    |
                    +-- TemplateNotFoundError
                    +-- TemplateParseError
```

## Design Principles

### 1. Context-Rich Errors

All SPI exceptions support an optional `context` dictionary for debugging:

```python
raise SPIError(
    "Operation failed",
    context={
        "node_id": "vectorization.v1",
        "operation": "execute",
        "input_size": 1024,
    }
)
```

### 2. Hierarchical Catching

The hierarchy enables both broad and specific exception handling:

```python
try:
    await handler.execute(request, config)
except HandlerInitializationError:
    # Handle initialization specifically
    logger.error("Handler failed to initialize")
except ProtocolHandlerError:
    # Handle any handler error
    logger.error("Handler execution failed")
except SPIError:
    # Handle any SPI error
    logger.error("SPI operation failed")
```

### 3. Semantic Clarity

Each exception type has a specific semantic meaning:

| Exception | Semantic Meaning |
|-----------|------------------|
| `SPIError` | Generic SPI failure |
| `ProtocolHandlerError` | [Handler](./HANDLERS.md) operation failed |
| `HandlerInitializationError` | [Handler](./HANDLERS.md) startup failed |
| `HandlerDiscoveryError` | Handler discovery/loading failed |
| `IdempotencyStoreError` | Idempotency store operation failed |
| `ContractCompilerError` | [Contract](./CONTRACTS.md) compilation failed |
| `RegistryError` | [Registry](./REGISTRY.md) operation failed |
| `ProtocolNotImplementedError` | Missing implementation |
| `InvalidProtocolStateError` | Lifecycle violation |
| `ProjectorError` | Projection write/persistence failed |
| `ProjectionReadError` | Projection read failed |
| `SchemaError` | Database schema operation failed |
| `TemplateError` | Template loading/processing failed |
| `TemplateNotFoundError` | Template file not found |
| `TemplateParseError` | Template file contains invalid YAML |

---

## SPIError

```python
from omnibase_spi.exceptions import SPIError
```

### Description

Base exception for all SPI-related errors. All SPI exceptions inherit from this base class to enable broad exception handling when needed.

### Constructor

```python
def __init__(
    self,
    message: str = "",
    context: dict[str, Any] | None = None,
) -> None:
    ...
```

**Args**:
- `message` (`str`): The error message describing what went wrong
- `context` (`dict[str, Any] | None`): Optional dictionary containing additional debugging information such as node_id, protocol_type, operation, parameters, etc.

**Attributes**:
- `context` (`dict[str, Any]`): Dictionary containing exception context for debugging. Empty dict if no context was provided.

### Usage Example

```python
from omnibase_spi.exceptions import SPIError

# Basic usage
raise SPIError("Handler execution failed")

# With context
raise SPIError(
    "Handler execution failed",
    context={
        "handler_id": "http_handler_123",
        "protocol_type": "http",
        "operation": "execute",
        "request_id": "req-456"
    }
)

# Catching and logging
try:
    await handler.execute(request, config)
except SPIError as e:
    logger.error(f"SPI error: {e}")
    if e.context:
        logger.debug(f"Context: {e.context}")
```

### When to Use

Use `SPIError` directly when:
- The error doesn't fit a more specific exception type
- Creating a new category of SPI error
- Wrapping external exceptions in SPI context

---

## ProtocolHandlerError

```python
from omnibase_spi.exceptions import ProtocolHandlerError
```

### Description

Errors raised by `ProtocolHandler` implementations. Raised when a protocol handler encounters an error during execution of protocol-specific operations.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import ProtocolHandlerError

# Basic usage
raise ProtocolHandlerError(
    f"HTTP request failed: {response.status_code}"
)

# With context
raise ProtocolHandlerError(
    "HTTP request failed",
    context={
        "status_code": response.status_code,
        "url": request.url,
        "method": "POST",
        "handler_id": self.handler_id,
        "response_body": response.text[:200],  # Truncated for logging
    }
)
```

### When to Use

Raise `ProtocolHandlerError` when:
- An HTTP request fails (non-2xx status, timeout, connection error)
- A database query fails (query error, constraint violation)
- A message publish fails (broker unavailable, serialization error)
- Any protocol-specific operation encounters an error

### Common Scenarios

| Scenario | Example |
|----------|---------|
| HTTP error | `ProtocolHandlerError("HTTP 500: Internal Server Error")` |
| Database error | `ProtocolHandlerError("Query execution failed: syntax error")` |
| Timeout | `ProtocolHandlerError("Request timed out after 30s")` |
| Connection refused | `ProtocolHandlerError("Connection refused to kafka:9092")` |

---

## HandlerInitializationError

```python
from omnibase_spi.exceptions import HandlerInitializationError
```

### Description

Raised when a handler fails to initialize. Indicates that the handler could not establish connections, configure clients, or otherwise prepare for operation.

**Inherits from**: `ProtocolHandlerError` -> `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import HandlerInitializationError

# Basic usage
raise HandlerInitializationError(
    f"Failed to connect to database: {connection_string}"
)

# With context
raise HandlerInitializationError(
    "Failed to connect to database",
    context={
        "host": config.host,
        "port": config.port,
        "database": config.database,
        "timeout": 30,
        "retry_count": 3,
        "last_error": str(original_exception),
    }
)
```

### When to Use

Raise `HandlerInitializationError` when:
- Connection pool creation fails
- Authentication fails
- Configuration is invalid
- Required resources are unavailable at startup
- SSL/TLS handshake fails

### Security Note

Never include credentials in the error message or context:

```python
# BAD - exposes password
raise HandlerInitializationError(
    f"Failed to connect: postgresql://user:password@host/db"
)

# GOOD - sanitized
raise HandlerInitializationError(
    "Failed to connect to database",
    context={
        "host": config.host,
        "port": config.port,
        "database": config.database,
        # No password!
    }
)
```

---

## HandlerDiscoveryError

```python
from omnibase_spi.exceptions import HandlerDiscoveryError
```

### Description

Raised when handler discovery fails. Indicates that a handler source could
not discover or load handlers due to configuration errors, missing
dependencies, invalid manifests, or other issues during the discovery
process.

**Inherits from**: `ProtocolHandlerError` -> `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import HandlerDiscoveryError

raise HandlerDiscoveryError(
    "Handler discovery failed",
    context={
        "source_type": "CONTRACT",
        "search_paths": ["/etc/handlers/", "/opt/handlers/"],
        "handler_type": "http",
    },
)
```

### When to Use

Raise `HandlerDiscoveryError` when `ProtocolHandlerSource.discover_handlers()`
(or an equivalent discovery entry point) cannot enumerate or load handlers —
distinct from `HandlerInitializationError`, which covers failures *after*
discovery, during a specific handler's `initialize()`.

---

## IdempotencyStoreError

```python
from omnibase_spi.exceptions import IdempotencyStoreError
```

### Description

Errors raised by `ProtocolIdempotencyStore` implementations. Raised when
idempotency-store operations fail due to connection issues, constraint
violations, or other storage errors.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import IdempotencyStoreError

raise IdempotencyStoreError(
    "Failed to record event",
    context={
        "event_id": event_id,
        "idempotency_key": key,
        "operation": "record",
        "store_type": "redis",
    },
)
```

---

## ContractCompilerError

```python
from omnibase_spi.exceptions import ContractCompilerError
```

### Description

Errors raised during contract compilation or validation. Raised when YAML contract files cannot be parsed, validated, or compiled into runtime contract objects.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import ContractCompilerError

# Basic usage
raise ContractCompilerError(
    f"Invalid contract at {path}: missing required field 'protocol'"
)

# With context
raise ContractCompilerError(
    "Invalid contract: missing required field 'protocol'",
    context={
        "path": str(path),
        "line_number": 42,
        "missing_fields": ["protocol", "version"],
        "contract_type": "effect",
    }
)

# YAML syntax error
raise ContractCompilerError(
    "YAML syntax error",
    context={
        "path": str(path),
        "line": 15,
        "column": 8,
        "error": "expected block end, but found '<scalar>'",
    }
)
```

### When to Use

Raise `ContractCompilerError` when:
- YAML syntax is invalid
- Required fields are missing
- Field types are incorrect
- Semantic validation fails (e.g., circular dependencies)
- Schema validation fails
- Referenced entities don't exist

### Common Scenarios

| Scenario | Example Context |
|----------|-----------------|
| Missing field | `{"missing_fields": ["protocol"], "line": 5}` |
| Invalid type | `{"field": "timeout", "expected": "int", "got": "string"}` |
| Circular dependency | `{"cycle": ["step1", "step2", "step1"]}` |
| Unknown reference | `{"unknown_state": "completed", "defined_states": [...]}` |

---

## RegistryError

```python
from omnibase_spi.exceptions import RegistryError
```

### Description

Errors raised by handler registry operations. Raised when registration fails or when looking up unregistered protocol types.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import RegistryError

# Lookup failure
raise RegistryError(
    f"Protocol type '{protocol_type}' is not registered"
)

# With context
raise RegistryError(
    f"Protocol type '{protocol_type}' is not registered",
    context={
        "protocol_type": protocol_type,
        "available_types": ["http", "kafka", "postgresql"],
        "operation": "lookup",
    }
)

# Registration failure
raise RegistryError(
    "Handler class does not implement ProtocolHandler",
    context={
        "protocol_type": "custom",
        "handler_class": handler_cls.__name__,
        "missing_methods": ["execute", "initialize"],
    }
)
```

### When to Use

Raise `RegistryError` when:
- Looking up an unregistered protocol type
- Registering an invalid handler class
- Registration conflicts occur (if not allowing override)
- Registry is in an invalid state

---

## ProtocolNotImplementedError

```python
from omnibase_spi.exceptions import ProtocolNotImplementedError
```

### Description

Raised when a required protocol implementation is missing. This exception signals that Core or Infra has not provided an implementation for a protocol that SPI defines. Use this to cleanly signal missing implementations during DI resolution.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import ProtocolNotImplementedError

# Basic usage
raise ProtocolNotImplementedError(
    f"No implementation registered for {IEffectNode.__name__}"
)

# With context
raise ProtocolNotImplementedError(
    "No implementation registered for protocol",
    context={
        "protocol_name": IEffectNode.__name__,
        "required_by": "WorkflowOrchestrator",
        "available_implementations": ["ComputeNodeImpl", "ReducerNodeImpl"],
        "di_container_id": container.id,
    }
)
```

### When to Use

Raise `ProtocolNotImplementedError` when:
- DI container cannot resolve a protocol to an implementation
- Required handler type is not registered
- Node type has no registered implementation
- Plugin or extension is missing required protocol implementation

### Common Scenarios

| Scenario | Example |
|----------|---------|
| Missing DI binding | `ProtocolNotImplementedError("No binding for ProtocolEffectNode")` |
| Missing handler | `ProtocolNotImplementedError("No handler for protocol type 'grpc'")` |
| Missing plugin | `ProtocolNotImplementedError("Plugin 'auth' not installed")` |

---

## InvalidProtocolStateError

```python
from omnibase_spi.exceptions import InvalidProtocolStateError
```

### Description

Raised when a protocol method is called in an invalid lifecycle state. This exception is used to enforce proper lifecycle management. For example, calling `execute()` before `initialize()` on an effect node.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import InvalidProtocolStateError

# Basic usage
raise InvalidProtocolStateError(
    f"Cannot call execute() before initialize() on {self.node_id}"
)

# With context
raise InvalidProtocolStateError(
    "Cannot call execute() before initialize()",
    context={
        "node_id": self.node_id,
        "current_state": "uninitialized",
        "required_state": "initialized",
        "operation": "execute",
        "lifecycle_history": ["created", "configured"],
    }
)
```

### When to Use

Raise `InvalidProtocolStateError` for lifecycle violations:

| Violation | Example |
|-----------|---------|
| Execute before initialize | `InvalidProtocolStateError("Not initialized")` |
| Execute after shutdown | `InvalidProtocolStateError("Handler is closed")` |
| Shutdown before initialize | `InvalidProtocolStateError("Cannot shutdown uninitialized handler")` |
| Double initialization | `InvalidProtocolStateError("Already initialized")` |
| Use after dispose | `InvalidProtocolStateError("Handler has been disposed")` |

### Lifecycle State Machine

```text
        +----------+
        | Created  |
        +----+-----+
             |
             v initialize()
        +----+-----+
   +--->|Initialized|<---+
   |    +----+-----+     |
   |         |           |
   |    execute()        | (success)
   |         |           |
   |         v           |
   |    +----+-----+     |
   +----| Executing |----+
        +----+-----+
             |
             v shutdown()
        +----+-----+
        |  Closed  |
        +----------+
```

---

## ProjectorError

```python
from omnibase_spi.exceptions import ProjectorError
```

### Description

Errors raised by `ProtocolProjector` implementations. Raised when projector
operations fail due to connection issues, storage errors, or other
persistence-layer problems. Stale-update rejections are **not** errors —
they return a rejected status in the `PersistResult`, they do not raise.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import ProjectorError

raise ProjectorError(
    "Failed to persist projection",
    context={
        "entity_id": entity_id,
        "domain": "orders",
        "sequence": 42,
        "operation": "persist",
        "store_type": "postgres",
    },
)
```

---

## ProjectionReadError

```python
from omnibase_spi.exceptions import ProjectionReadError
```

### Description

Raised when reading projection state fails — connection issues, timeout, or
other infrastructure errors during a read operation. Distinct from
`ProjectorError`, which covers write/persistence failures.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import ProjectionReadError

raise ProjectionReadError(
    "Failed to query projection",
    context={
        "entity_id": entity_id,
        "domain": "orders",
        "operation": "get_entity_state",
    },
)
```

---

## SchemaError

```python
from omnibase_spi.exceptions import SchemaError
```

### Description

Raised during database schema operations — table creation, index
management, or schema-compatibility checks during projector initialization.

**Inherits from**: `SPIError`

### Usage Example

```python
from omnibase_spi.exceptions import SchemaError

raise SchemaError(
    "Schema creation failed",
    context={
        "table_name": "order_projections",
        "operation": "create_table",
        "database": "postgres",
    },
)
```

### Common Causes

- Database connection failure during schema creation
- Insufficient permissions to create tables/indexes
- Schema incompatibility (existing table doesn't match contract)
- Invalid column type specifications in contract

---

## TemplateError, TemplateNotFoundError, TemplateParseError

```python
from omnibase_spi.exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateParseError,
)
```

### Description

`TemplateError` is the base exception for template loading and processing
errors in the handler-contract factory system — YAML template files used
for handler contract generation. Two subclasses narrow the failure mode:

- `TemplateNotFoundError` — the requested template file does not exist in
  the expected location (`omnibase_spi/contracts/defaults/`), typically an
  unsupported handler type or a packaging gap.
- `TemplateParseError` — the template file exists but its contents are not
  valid YAML.

**Inherits from**: `SPIError` (`TemplateError`); `TemplateError` -> `SPIError`
(`TemplateNotFoundError`, `TemplateParseError`)

### Usage Example

```python
from omnibase_spi.exceptions import TemplateNotFoundError, TemplateParseError

raise TemplateNotFoundError(
    "Template file not found",
    context={
        "template_name": "default_compute_handler.yaml",
        "handler_type": "COMPUTE",
    },
)

raise TemplateParseError(
    "Failed to parse template YAML",
    context={
        "template_name": "default_effect_handler.yaml",
        "error_line": 42,
        "handler_type": "EFFECT",
    },
)
```

---

## Exception Handling Patterns

### Pattern 1: Layered Exception Handling

```python
async def execute_with_retry(
    handler: ProtocolHandler,
    request: ModelProtocolRequest,
    config: ModelOperationConfig,
    max_retries: int = 3,
) -> ModelProtocolResponse:
    """Execute with retry logic and layered exception handling."""

    last_error = None

    for attempt in range(max_retries):
        try:
            return await handler.execute(request, config)

        except HandlerInitializationError:
            # Don't retry initialization errors
            raise

        except InvalidProtocolStateError:
            # Don't retry state errors
            raise

        except ProtocolHandlerError as e:
            # Retry transient handler errors
            last_error = e
            await asyncio.sleep(2 ** attempt)

    raise ProtocolHandlerError(
        f"Failed after {max_retries} attempts",
        context={"last_error": str(last_error)}
    )
```

### Pattern 2: Error Context Propagation

```python
async def orchestrate_workflow(
    steps: list[WorkflowStep],
) -> WorkflowResult:
    """Orchestrate workflow with context propagation."""

    for i, step in enumerate(steps):
        try:
            await step.execute()
        except SPIError as e:
            # Add workflow context to error
            e.context["workflow_step"] = i
            e.context["step_name"] = step.name
            e.context["completed_steps"] = i
            raise
```

### Pattern 3: Error Translation

```python
async def execute_database_query(
    handler: ProtocolHandler,
    query: str,
) -> list[dict]:
    """Translate database errors to SPI errors."""

    try:
        response = await handler.execute(request, config)
        return response.data

    except asyncpg.PostgresError as e:
        raise ProtocolHandlerError(
            f"Database query failed: {e.sqlstate}",
            context={
                "sqlstate": e.sqlstate,
                "query": query[:100],  # Truncated
                "original_error": str(e),
            }
        )
```

### Pattern 4: Safe Error Logging

```python
def log_spi_error(
    logger: Logger,
    error: SPIError,
) -> None:
    """Log SPI error with sanitized context."""

    # Create sanitized context
    safe_context = {}
    sensitive_keys = {"password", "secret", "token", "key", "auth"}

    for key, value in error.context.items():
        if any(s in key.lower() for s in sensitive_keys):
            safe_context[key] = "[REDACTED]"
        else:
            safe_context[key] = value

    logger.error(
        f"SPI error: {error}",
        exc_info=error,
        extra={"context": safe_context},
    )
```

---

## Exception Summary Table

| Exception | Parent | Raised By | When |
|-----------|--------|-----------|------|
| `SPIError` | `Exception` | Any SPI code | Generic SPI failure |
| `ProtocolHandlerError` | `SPIError` | `ProtocolHandler.execute()` | Handler operation failed |
| `HandlerInitializationError` | `ProtocolHandlerError` | `ProtocolHandler.initialize()` | Handler startup failed |
| `HandlerDiscoveryError` | `ProtocolHandlerError` | `ProtocolHandlerSource.discover_handlers()` | Handler discovery/loading failed |
| `IdempotencyStoreError` | `SPIError` | `ProtocolIdempotencyStore` | Idempotency store operation failed |
| `ContractCompilerError` | `SPIError` | Contract compilers | Contract compilation failed |
| `RegistryError` | `SPIError` | `ProtocolHandlerRegistry` | Registry operation failed |
| `ProtocolNotImplementedError` | `SPIError` | DI containers | Missing implementation |
| `InvalidProtocolStateError` | `SPIError` | Lifecycle methods | Lifecycle violation |
| `ProjectorError` | `SPIError` | `ProtocolProjector` | Projection write/persistence failed |
| `ProjectionReadError` | `SPIError` | Projection readers | Projection read failed |
| `SchemaError` | `SPIError` | Projector initialization | Database schema operation failed |
| `TemplateError` | `SPIError` | `HandlerContractFactory` | Template loading/processing failed |
| `TemplateNotFoundError` | `TemplateError` | `HandlerContractFactory` | Template file not found |
| `TemplateParseError` | `TemplateError` | `HandlerContractFactory` | Template file contains invalid YAML |

---

## Version Information

- **API Reference Version**: current package 0.23.1
- **Python Compatibility**: 3.12+
- **Type Checking**: mypy strict mode compatible
- **Exception count**: 15 classes (verified against `src/omnibase_spi/exceptions.py` on this refresh)

---

## See Also

- **[NODES.md](./NODES.md)** - Node protocols that may raise SPI exceptions
- **[HANDLERS.md](./HANDLERS.md)** - Handler protocols that raise `ProtocolHandlerError` and `HandlerInitializationError`
- **[CONTRACTS.md](./CONTRACTS.md)** - Contract compilers that raise `ContractCompilerError`
- **[REGISTRY.md](./REGISTRY.md)** - Registry protocols that raise `RegistryError`
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference is part of the omnibase_spi documentation.*

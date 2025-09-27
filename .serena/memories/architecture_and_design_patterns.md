# Architecture and Design Patterns for omnibase-spi

## Overall Architecture Philosophy

### 1. Service Provider Interface (SPI) Pattern
The omnibase-spi implements a pure SPI pattern where:
- **Contracts**: Defined through Python Protocol classes
- **Implementations**: Provided by consuming packages (like omnibase-core)
- **Decoupling**: Zero implementation dependencies
- **Duck Typing**: Runtime type checking with Protocol compliance

### 2. Domain-Driven Design (DDD)
Protocols are organized by functional domains:
```
protocols/
├── core/           # Core system contracts
├── event_bus/      # Event-driven architecture contracts
├── container/      # Dependency injection contracts
├── discovery/      # Service discovery contracts
├── file_handling/  # File processing contracts
├── types/          # Domain type definitions
└── validation/     # Validation framework contracts
```

## Key Design Patterns

### 1. Protocol Pattern
```python
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import ProtocolSerializationResult

@runtime_checkable
class ProtocolCanonicalSerializer(Protocol):
    """Contract for canonical serialization services."""

    def serialize(self, data: object) -> "ProtocolSerializationResult":
        """Serialize object to canonical format."""
        ...

    def deserialize(self, serialized: str) -> object:
        """Deserialize from canonical format."""
        ...
```

### 2. Forward Reference Pattern
Avoids circular dependencies by using TYPE_CHECKING imports:
```python
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    # Only imported for type checking, not runtime
    from omnibase_spi.protocols.types.event_bus_types import EventData
    from omnibase_spi.protocols.types.core_types import ProtocolValidationResult

class ProtocolEventHandler(Protocol):
    def handle(self, event: "EventData") -> "ProtocolValidationResult":
        """Handle event data with validation result."""
        ...
```

### 3. Generic Protocol Pattern
Enables type-safe generic protocols:
```python
from typing import Generic, Protocol, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class ProtocolGenericProcessor(Protocol, Generic[T, R]):
    """Generic processing contract."""

    def process(self, input_data: T) -> R:
        """Process input of type T and return result of type R."""
        ...
```

### 4. Composition Pattern
Protocols designed for composition rather than inheritance:
```python
# Multiple focused protocols
class ProtocolReader(Protocol):
    def read(self, path: str) -> str: ...

class ProtocolWriter(Protocol):
    def write(self, path: str, content: str) -> bool: ...

# Composed protocol
class ProtocolFileHandler(ProtocolReader, ProtocolWriter, Protocol):
    """Combined file handling capabilities."""
    pass
```

## Architectural Layers

### 1. Type Definition Layer (`types/` modules)
- **Purpose**: Define domain-specific types and data structures
- **Pattern**: Use Literal, TypedDict, and Union types
- **Example**: LogLevel, ProtocolLogEntry, EventData

### 2. Core Protocol Layer (`core/` modules)
- **Purpose**: System-level service contracts
- **Pattern**: Fundamental operations and system services
- **Example**: Serialization, schema loading, workflow reduction

### 3. Domain Protocol Layer (domain-specific modules)
- **Purpose**: Domain-specific service contracts
- **Pattern**: Business logic and domain operations
- **Example**: Event handling, file processing, service discovery

### 4. Integration Protocol Layer (`container/`, `discovery/`)
- **Purpose**: System integration and wiring contracts
- **Pattern**: Dependency injection and service location
- **Example**: Service registry, artifact containers

## Design Principles

### 1. Interface Segregation
Each protocol focuses on a single responsibility:
```python
# Good: Focused protocols
class ProtocolLogger(Protocol):
    def log(self, level: LogLevel, message: str) -> None: ...

class ProtocolLogFormatter(Protocol):  
    def format(self, entry: ProtocolLogEntry) -> str: ...

# Avoid: Monolithic protocols
class ProtocolLoggingEverything(Protocol):
    def log(self, level: LogLevel, message: str) -> None: ...
    def format(self, entry: ProtocolLogEntry) -> str: ...
    def configure(self, config: dict) -> None: ...  # Too broad
```

### 2. Dependency Inversion
High-level protocols don't depend on low-level implementations:
```python
# High-level protocol
class ProtocolWorkflowReducer(Protocol):
    def reduce_workflow(self, workflow_data: "WorkflowData") -> "ReducedWorkflow":
        """High-level workflow reduction contract."""
        ...

# Low-level protocols implement specific operations
class ProtocolDataProcessor(Protocol):
    def process_step(self, step_data: "StepData") -> "ProcessedStep":
        """Low-level step processing contract."""
        ...
```

### 3. Open/Closed Principle
Protocols designed for extension without modification:
```python
# Base protocol - closed for modification
class ProtocolEventHandler(Protocol):
    def handle_event(self, event: "EventData") -> bool: ...

# Extended protocol - open for extension  
class ProtocolAsyncEventHandler(ProtocolEventHandler, Protocol):
    async def handle_event_async(self, event: "EventData") -> bool: ...
```

## Validation Framework Architecture

### 1. Layered Validation
```python
# Core validation protocol
class ProtocolValidator(Protocol):
    def validate(self, data: object) -> "ProtocolValidationResult": ...

# Specialized validators
class ProtocolSchemaValidator(ProtocolValidator, Protocol):
    def validate_schema(self, schema: str, data: object) -> "ProtocolValidationResult": ...

class ProtocolBusinessRuleValidator(ProtocolValidator, Protocol):
    def validate_business_rules(self, rules: list, data: object) -> "ProtocolValidationResult": ...
```

### 2. Decorator Pattern Support
```python
from typing import Callable, TypeVar

F = TypeVar('F', bound=Callable)

class ProtocolValidationDecorator(Protocol):
    def validate_input(self, func: F) -> F:
        """Decorator for input validation."""
        ...

    def validate_output(self, func: F) -> F:
        """Decorator for output validation."""
        ...
```

## Event-Driven Architecture Support

### 1. Publisher-Subscriber Pattern
```python
class ProtocolEventPublisher(Protocol):
    def publish(self, event: "EventData") -> bool: ...

class ProtocolEventSubscriber(Protocol):
    def subscribe(self, event_type: str, handler: "ProtocolEventHandler") -> bool: ...
    def unsubscribe(self, event_type: str, handler: "ProtocolEventHandler") -> bool: ...
```

### 2. Event Bus Pattern
```python
class ProtocolEventBus(Protocol):
    """Central event coordination contract."""

    def register_handler(self, event_type: str, handler: "ProtocolEventHandler") -> None: ...
    def emit_event(self, event: "EventData") -> None: ...
    def remove_handler(self, event_type: str, handler: "ProtocolEventHandler") -> None: ...
```

## Service Discovery Architecture

### 1. Registry Pattern
```python
class ProtocolServiceRegistry(Protocol):
    """Service location and management contract."""

    def register_service(self, service_id: str, service: object) -> bool: ...
    def get_service(self, service_id: str) -> object: ...
    def list_services(self) -> list[str]: ...
```

### 2. Handler Discovery Pattern
```python
class ProtocolHandlerDiscovery(Protocol):
    """Dynamic handler discovery contract."""

    def discover_handlers(self, handler_type: str) -> list[object]: ...
    def register_handler_factory(self, factory: "ProtocolHandlerFactory") -> None: ...
```

## Error Handling Patterns

### 1. Result Pattern Support
```python
from typing import TypedDict, Union

class ProtocolSuccessResult(TypedDict):
    success: Literal[True]
    data: object

class ProtocolErrorResult(TypedDict):
    success: Literal[False]
    error: str
    error_code: str

ProtocolResult = Union[ProtocolSuccessResult, ProtocolErrorResult]

class ProtocolResultHandler(Protocol):
    def handle_result(self, result: ProtocolResult) -> None: ...
```

### 2. Validation Result Pattern
```python
class ProtocolValidationResult(TypedDict):
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    metadata: dict[str, object]
```

## Guidelines for Protocol Design

### 1. Protocol Naming
- Use descriptive names starting with "Protocol"
- Indicate the service contract clearly
- Avoid implementation-specific details

### 2. Method Design
- Use clear, intention-revealing names
- Keep parameter lists focused
- Return structured results when complex

### 3. Documentation
- Document the contract, not implementation
- Explain expected behavior and constraints  
- Provide usage examples in docstrings

### 4. Evolution Strategy
- Design for backward compatibility
- Use optional methods for new features
- Deprecate gracefully with clear migration paths

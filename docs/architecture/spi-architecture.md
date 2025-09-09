# SPI Architecture

## Service Provider Interface Design Principles

The ONEX Service Provider Interface (omnibase-spi) implements a sophisticated architectural pattern that enables loose coupling, strong typing, and zero-dependency protocol definitions across the ONEX ecosystem.

## Core Architectural Principles

### 1. Protocol-First Design

omnibase-spi uses **Python protocols** as the foundation for all interface contracts:

```python
from typing import Protocol

class ProtocolExample(Protocol):
    """Pure interface definition without implementation."""
    
    def method_name(self, param: str) -> int:
        """Contract specification - no implementation."""
        ...
```

**Benefits:**
- **Duck Typing with Type Safety**: Protocols enable duck typing while maintaining compile-time type checking
- **Implementation Independence**: Multiple implementations can satisfy the same protocol
- **Minimal Coupling**: Protocols define "what" without specifying "how"
- **Evolutionary Design**: Protocols can evolve independently of implementations

### 2. Zero-Dependency Architecture

The package maintains **complete dependency isolation**:

```yaml
Dependencies:
  Runtime:
    - typing-extensions: "^4.5.0"  # Modern typing features
    - pydantic: "^2.11.7"         # Model validation only
  
  Forbidden:
    - omnibase-core: ❌           # Would create circular dependency
    - omnibase-model: ❌          # Violates namespace isolation
    - Any business logic: ❌       # Pure interfaces only
```

**Isolation Benefits:**
- **No Circular Dependencies**: Can be imported by any ONEX component
- **Independent Evolution**: Protocol changes don't break implementations
- **Clear Separation**: Interface vs. implementation concerns
- **Testability**: Easy to mock and test protocol contracts

### 3. Domain-Driven Organization

Protocols are organized by **functional domains**:

```
protocols/
├── core/          # System-level contracts (logging, serialization)
├── event_bus/     # Event-driven architecture patterns
├── container/     # Dependency injection and registry
├── discovery/     # Service location and discovery
├── file_handling/ # File processing operations
└── types/         # Domain-specific type definitions
```

**Domain Benefits:**
- **Cohesion**: Related protocols grouped together
- **Modularity**: Domains can evolve independently
- **Discoverability**: Clear organization for protocol location
- **Scalability**: New domains can be added without affecting existing ones

## Architectural Layers

### Layer 1: Type Definitions

Foundation layer providing strong type contracts:

```python
# src/omnibase/protocols/types/core_types.py
from typing import Literal, Union
from datetime import datetime

# Strong literal types for constants
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
NodeStatus = Literal["active", "inactive", "error", "pending"]

# Union types for flexible but constrained values
ContextValue = Union[str, int, float, bool, List[str], Dict[str, str]]

# Protocol types for structured data
class ProtocolSemVer(Protocol):
    major: int
    minor: int  
    patch: int
    
    def __str__(self) -> str: ...
```

**Layer 1 Characteristics:**
- **No Dependencies**: Only uses Python standard library and typing
- **Strong Constraints**: Literal types prevent invalid values
- **Protocol Interfaces**: Define data structure contracts
- **Type Safety**: Eliminates `Any` usage throughout the system

### Layer 2: Core Protocols

Business logic interfaces that use Layer 1 types:

```python
# src/omnibase/protocols/core/protocol_logger.py
from typing import Protocol, Dict, Any
from omnibase_spi.protocols.types.core_types import LogLevel, ContextValue

class ProtocolLogger(Protocol):
    """Core logging protocol using strong types."""
    
    def log(
        self, 
        level: LogLevel,                    # Strong literal type
        message: str,
        correlation_id: Optional[UUID],
        context: Dict[str, ContextValue]    # Constrained value types
    ) -> None:
        """Log with structured context and correlation tracking."""
        ...
    
    def is_enabled(self, level: LogLevel) -> bool:
        """Check if logging level is active."""
        ...
```

**Layer 2 Characteristics:**
- **Type-Dependent**: Built on Layer 1 type definitions
- **Business Contracts**: Define what services must provide
- **Implementation Agnostic**: No concrete implementation details
- **Composable**: Protocols can reference other protocols

### Layer 3: Domain-Specific Protocols

Specialized interfaces for particular domains:

```python
# src/omnibase/protocols/event_bus/protocol_event_bus.py
from typing import Protocol, TYPE_CHECKING
from omnibase_spi.protocols.types.event_bus_types import EventType
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger

if TYPE_CHECKING:
    from external.event.models import Event

class ProtocolEventBus(Protocol):
    """Event bus protocol with external model references."""
    
    def publish(
        self, 
        event_type: EventType,
        event: "Event",                     # Forward reference to external model
        correlation_id: UUID
    ) -> None:
        """Publish event to bus."""
        ...
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[["Event"], None]  # Forward reference in generic
    ) -> str:
        """Subscribe to events and return subscription ID."""
        ...
```

**Layer 3 Characteristics:**
- **Domain-Focused**: Specialized for particular use cases
- **Protocol Composition**: May combine multiple Layer 2 protocols
- **Forward References**: Can reference external models via TYPE_CHECKING
- **Rich Interfaces**: More complex contracts for specialized domains

### Layer 4: Application Integration

Consumer code that implements and uses protocols:

```python
# In consuming applications (not in omnibase-spi)
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger
from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus

class MyApplication:
    """Application using protocol-based dependencies."""
    
    def __init__(
        self,
        logger: ProtocolLogger,      # Protocol dependency
        event_bus: ProtocolEventBus  # Protocol dependency
    ):
        self._logger = logger
        self._event_bus = event_bus
    
    def process_request(self, request_data: Dict[str, Any]) -> None:
        """Process request using protocol contracts."""
        correlation_id = uuid.uuid4()
        
        self._logger.log(
            "INFO", 
            "Processing request",
            correlation_id=correlation_id,
            context={"request_id": str(correlation_id)}
        )
        
        # Business logic here...
        
        self._event_bus.publish(
            "request.processed",
            ProcessedEvent(data=request_data),
            correlation_id=correlation_id
        )
```

## Design Patterns

### 1. Protocol Composition Pattern

Combine multiple protocols for complex interfaces:

```python
from typing import Protocol
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger
from omnibase_spi.protocols.core.protocol_canonical_serializer import ProtocolCanonicalSerializer

class ProtocolAuditableService(Protocol):
    """Service that requires both logging and serialization."""
    
    # Compose existing protocols
    logger: ProtocolLogger
    serializer: ProtocolCanonicalSerializer
    
    def audit_operation(
        self,
        operation: str,
        data: Dict[str, Any],
        user_id: str
    ) -> None:
        """Audit operation with logging and serialization."""
        ...

class AuditableUserService(ProtocolAuditableService):
    """Implementation using protocol composition."""
    
    def __init__(
        self,
        logger: ProtocolLogger,
        serializer: ProtocolCanonicalSerializer
    ):
        self.logger = logger
        self.serializer = serializer
    
    def audit_operation(
        self,
        operation: str, 
        data: Dict[str, Any],
        user_id: str
    ) -> None:
        # Use composed protocols
        serialized_data = self.serializer.serialize(data)
        if serialized_data.success:
            self.logger.log(
                "INFO",
                f"User {user_id} performed {operation}",
                correlation_id=uuid.uuid4(),
                context={
                    "user_id": user_id,
                    "operation": operation,
                    "data": serialized_data.data
                }
            )
```

### 2. Generic Protocol Pattern

Create reusable protocols with type parameters:

```python
from typing import TypeVar, Generic, Protocol, List, Optional

T = TypeVar('T')
K = TypeVar('K')

class ProtocolRepository(Protocol, Generic[T, K]):
    """Generic repository protocol for any entity type."""
    
    def get(self, key: K) -> Optional[T]:
        """Get entity by key."""
        ...
    
    def save(self, entity: T) -> K:
        """Save entity and return key."""
        ...
    
    def find_all(self) -> List[T]:
        """Find all entities."""
        ...
    
    def delete(self, key: K) -> bool:
        """Delete entity by key."""
        ...

# Specific usage
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str

# Type-specific repository protocol
UserRepository = ProtocolRepository[User, str]

class DatabaseUserRepository(UserRepository):
    """Database implementation of user repository."""
    
    def get(self, key: str) -> Optional[User]:
        # Database implementation
        pass
    
    def save(self, entity: User) -> str:
        # Database implementation
        return entity.id
```

### 3. Behavioral Protocol Pattern

Define protocols for behavioral contracts rather than data:

```python
from typing import Protocol, ContextManager, Any
from omnibase_spi.protocols.types.core_types import ContextValue

class ProtocolTransactional(Protocol):
    """Protocol for transactional behavior."""
    
    def begin_transaction(self) -> str:
        """Begin transaction and return transaction ID."""
        ...
    
    def commit_transaction(self, transaction_id: str) -> None:
        """Commit transaction."""
        ...
    
    def rollback_transaction(self, transaction_id: str) -> None:
        """Rollback transaction."""
        ...
    
    def transaction_context(self) -> ContextManager[str]:
        """Get transaction context manager."""
        ...

class ProtocolCacheable(Protocol):
    """Protocol for cacheable behavior."""
    
    def get_cache_key(self) -> str:
        """Get cache key for this object."""
        ...
    
    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        ...
    
    def is_cacheable(self) -> bool:
        """Check if object should be cached."""
        ...

# Combined behavioral protocol
class ProtocolTransactionalCacheableService(
    ProtocolTransactional, 
    ProtocolCacheable,
    Protocol
):
    """Service with both transactional and cacheable behavior."""
    
    def process_with_cache(self, data: Dict[str, ContextValue]) -> Any:
        """Process data with transaction and cache support."""
        ...
```

## Forward Reference Architecture

Handle complex dependencies without circular imports:

### Basic Forward Reference

```python
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    # Imports only used for type checking - no runtime dependency
    from complex.external.module import ExternalModel
    from another.package.types import CustomType

class ProtocolModelProcessor(Protocol):
    """Protocol with forward references to external types."""
    
    def process(self, model: "ExternalModel") -> "CustomType":
        """Process external model - forward reference prevents import at runtime."""
        ...
```

### Advanced Forward Reference with Generics

```python
from typing import TYPE_CHECKING, Protocol, Generic, TypeVar, List, Dict

if TYPE_CHECKING:
    from external.models import BaseModel, ProcessingResult
    from external.validators import ValidationRule

T = TypeVar('T', bound='BaseModel')
R = TypeVar('R', bound='ProcessingResult')

class ProtocolAdvancedProcessor(Protocol, Generic[T, R]):
    """Advanced processor with generic forward references."""
    
    def process_batch(
        self, 
        models: List[T], 
        rules: List["ValidationRule"]
    ) -> List[R]:
        """Process batch with validation rules."""
        ...
    
    def validate_model(self, model: T) -> List["ValidationRule"]:
        """Get applicable validation rules for model."""
        ...
```

## Benefits and Trade-offs

### Benefits

1. **Type Safety**: Strong typing without runtime overhead
2. **Modularity**: Clear separation between interface and implementation
3. **Testability**: Easy to mock protocols for testing
4. **Evolution**: Protocols can evolve independently
5. **Documentation**: Protocols serve as living documentation
6. **IDE Support**: Full IDE support with autocomplete and type checking

### Trade-offs

1. **Abstraction Overhead**: Additional layer of indirection
2. **Learning Curve**: Developers need to understand protocol concepts
3. **Forward Reference Complexity**: Complex type relationships require careful design
4. **Protocol Evolution**: Breaking changes in protocols affect all implementations

### When to Use SPI Architecture

**Good For:**
- Large systems with multiple implementations
- Plugin architectures
- Framework development
- Systems requiring strong type safety
- Teams needing clear interface contracts

**Consider Alternatives For:**
- Small, single-implementation systems
- Rapid prototyping where flexibility trumps structure
- Systems where runtime performance is critical
- Teams unfamiliar with protocol-based design

## Integration with ONEX Ecosystem

The SPI architecture enables the ONEX ecosystem to:

1. **Maintain Loose Coupling**: Components depend on protocols, not implementations
2. **Enable Plugin Systems**: New implementations can be added without core changes
3. **Provide Type Safety**: Full static type checking across all components
4. **Support Testing**: Easy mocking and testing of component interactions
5. **Allow Independent Evolution**: Components can evolve independently while maintaining contracts

This architectural approach forms the foundation for a robust, maintainable, and scalable system architecture across the entire ONEX ecosystem.
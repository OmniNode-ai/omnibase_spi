# Code Style and Conventions for omnibase-spi

## Core SPI Design Principles

### 1. Protocol-Only Rule
- **ONLY Protocol definitions allowed** - no concrete implementations
- All methods must have `...` (ellipsis) body, no actual implementation
- Use `@runtime_checkable` decorator for runtime type checking
- Never use `@dataclass` - use Protocol instead

### 2. Naming Conventions
- **Protocol Classes**: Must start with "Protocol" (e.g., `ProtocolEventBus`)
- **File Names**: `protocol_*.py` format for protocol definition files
- **Type Files**: `*_types.py` for type definitions and aliases
- **Modules**: Snake_case module names (e.g., `event_bus`, `file_handling`)

### 3. Import Patterns
```python
# CORRECT: TYPE_CHECKING imports for forward references
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import SomeType

@runtime_checkable
class ProtocolExample(Protocol):
    def method(self) -> "SomeType": ...

# FORBIDDEN: Direct imports that create dependencies
from omnibase_spi.model.core.some_model import SomeModel  # ❌ NEVER
```

### 4. Namespace Isolation Rules
- **✅ ALLOWED**: `from omnibase_spi.protocols.* import ...`
- **❌ FORBIDDEN**: `from omnibase_spi.* import ...` (anything outside protocols)
- **❌ FORBIDDEN**: Any imports from external omnibase modules
- **❌ FORBIDDEN**: Implementation library imports (os, sys, json, etc.)

## Type System Conventions

### 1. Strong Typing Requirements
- Use precise types, avoid `Any` when possible
- Use `Literal` types instead of `Enum` for constants
- Use `Union` types sparingly, prefer Protocol composition
- Always provide return type annotations

### 2. Forward Reference Pattern
```python
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.event_bus_types import EventData

class ProtocolEventHandler(Protocol):
    def handle_event(self, data: "EventData") -> bool: ...
```

### 3. Generic Protocol Pattern
```python
from typing import Generic, Protocol, TypeVar

T = TypeVar('T')

class ProtocolGenericHandler(Protocol, Generic[T]):
    def process(self, item: T) -> T: ...
```

## File Organization

### 1. Protocol File Structure
```python
"""Module docstring explaining the protocol's purpose."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward reference imports only
    pass

@runtime_checkable
class ProtocolName(Protocol):
    """Clear protocol documentation."""

    def method_name(self, param: str) -> bool:
        """Method documentation with clear contract."""
        ...
```

### 2. Type Definition Files
```python
"""Type definitions for domain."""

from typing import Literal, Protocol, TypedDict

# Literal types for constants
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# TypedDict for structured data
class ProtocolLogEntry(TypedDict):
    level: LogLevel
    message: str
    timestamp: str
```

## Code Quality Standards

### 1. Formatting (Black)
- Line length: 88 characters
- Target Python version: 3.12
- Automatic string quote normalization
- Trailing commas in multi-line structures

### 2. Import Sorting (isort)
- Black-compatible profile
- Separate sections for standard library, third-party, and local imports
- TYPE_CHECKING imports in separate block

### 3. Type Checking (mypy)
- Strict mode enabled
- All functions must have type hints
- No implicit returns
- Warn on unused configurations

### 4. Docstring Conventions
```python
class ProtocolExample(Protocol):
    """One-line summary of the protocol.

    Longer description explaining the protocol's purpose,
    expected behavior, and usage patterns.

    Example:
        class MyImplementation(ProtocolExample):
            def method(self) -> str:
                return "implemented"
    """

    def method(self) -> str:
        """Method description with clear expectations.

        Returns:
            Description of return value and constraints.

        Raises:
            Exceptions that implementations might raise.
        """
        ...
```

## Forbidden Patterns

### 1. Implementation Violations
```python
# ❌ FORBIDDEN: Concrete implementations
class ProtocolBad(Protocol):
    def method(self) -> str:
        return "implementation"  # Never implement in Protocol

# ❌ FORBIDDEN: __init__ methods
class ProtocolBad(Protocol):
    def __init__(self, param: str): ...  # Use @property instead

# ❌ FORBIDDEN: Default parameter values
class ProtocolBad(Protocol):
    def method(self, param: str = "default") -> str: ...  # No defaults
```

### 2. Import Violations
```python
# ❌ FORBIDDEN: External omnibase imports
from omnibase_spi.core import SomeClass
from omnibase_spi.model.core import SomeModel

# ❌ FORBIDDEN: Implementation library imports
import os
import json
from abc import ABC

# ❌ FORBIDDEN: Dataclasses
from dataclasses import dataclass
```

### 3. Type Violations
```python
# ❌ FORBIDDEN: Enum usage
from enum import Enum
class Status(Enum): ...  # Use Literal instead

# ❌ FORBIDDEN: ABC usage
from abc import ABC
class BaseClass(ABC): ...  # Use Protocol instead
```

## Best Practices

### 1. Protocol Design
- Keep protocols focused and cohesive
- Use composition over inheritance
- Design for extensibility and testability
- Document expected behavior clearly

### 2. Error Handling
- Define expected exceptions in protocol documentation
- Never raise exceptions from protocol definitions
- Document error conditions implementations should handle

### 3. Versioning Considerations
- Design protocols for backward compatibility
- Use optional methods for new features
- Document breaking changes clearly
- Consider deprecation paths for old methods

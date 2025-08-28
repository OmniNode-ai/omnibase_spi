# Code Style and Conventions: omnibase-spi

## Naming Conventions
- **Protocol Classes**: Must start with "Protocol" (e.g., `ProtocolEventBus`)
- **Protocol Files**: Use `protocol_` prefix (e.g., `protocol_event_bus.py`)
- **Type Files**: Use `_types.py` suffix for type definitions
- **Package Names**: Use lowercase with underscores (`event_bus`, `file_handling`)
- **Variables/Methods**: snake_case throughout

## Protocol Design Patterns

### Zero-Dependency Pattern
```python
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from some.external.model import ExternalModel

class ProtocolExample(Protocol):
    def method(self, param: str) -> "ExternalModel":
        """Clear docstring with contract definition."""
        ...
```

### Strong Typing Pattern
- **No Any Types**: Use specific types or Union types
- **Literal Types**: Use `Literal` for string constants
- **Forward References**: Use quoted strings for forward refs
- **Type Aliases**: Define clear type aliases for complex types

## Documentation Standards
- **Module Docstrings**: Include domain and purpose
- **Class Docstrings**: Describe protocol contract clearly  
- **Method Docstrings**: Document parameters, return types, and behavior
- **Type Annotations**: Required for all methods and attributes

## Code Formatting
- **Line Length**: 88 characters (Black default)
- **String Quotes**: Double quotes preferred
- **Import Style**: Absolute imports only, grouped by standard/third-party/local
- **Trailing Commas**: Required in multi-line structures

## Import Organization (isort + Black profile)
```python
# Standard library
from typing import TYPE_CHECKING, Protocol
from datetime import datetime

# Third party (minimal - only typing-extensions, pydantic)
from typing_extensions import Literal
from pydantic import BaseModel

# Local imports (only omnibase.protocols.*)
from omnibase.protocols.types.core_types import ProtocolSemVer

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from external.model import ExternalModel
```

## Protocol Structure Standards
- **Abstract Methods**: Use `...` body (not `pass` or `raise NotImplementedError`)
- **Attribute Protocols**: For data structures and models
- **Method Protocols**: For services and operations  
- **Mixed Protocols**: Combine attributes and methods when needed

## File Organization
- **Domain Separation**: Each domain has its own package
- **Type Separation**: Types in dedicated `_types.py` files
- **Protocol Separation**: One protocol per file when complex
- **Init Files**: Minimal exports in `__init__.py` files

## Error Handling Patterns
- **Protocol Methods**: Don't specify exception handling in protocols
- **Return Types**: Use Result/Optional patterns for error indication
- **Documentation**: Document expected error conditions in docstrings

## Testing Conventions
- **Import Testing**: Verify no external dependencies
- **Namespace Testing**: Validate isolation from omnibase-core
- **Type Checking**: MyPy validation as part of test suite
- **Protocol Validation**: Test protocol contracts are complete
# Developer Guide

## Overview

This comprehensive guide covers everything developers need to know to effectively use omnibase-spi in their applications. Whether you're implementing protocol interfaces, designing new protocols, or integrating with existing systems, this guide provides detailed instructions and best practices.

## Table of Contents

### Getting Started with Development
- [Setting Up Development Environment](#setting-up-development-environment)
- [Project Structure Overview](#project-structure-overview)
- [Understanding Protocol Types](#understanding-protocol-types)

### Core Development Concepts
- [Protocol Implementation Patterns](#protocol-implementation-patterns)
- [Type Safety and Strong Typing](#type-safety-and-strong-typing)
- [Namespace Isolation](#namespace-isolation)
- [Forward References and TYPE_CHECKING](#forward-references)

### Working with Protocols
- [Implementing Core Protocols](#implementing-core-protocols)
- [Event Bus Integration](#event-bus-integration)
- [Container and Registry Patterns](#container-patterns)
- [File Handling Protocols](#file-handling-protocols)

### Advanced Topics
- [Custom Protocol Design](#custom-protocol-design)
- [Testing Protocol Implementations](#testing-protocols)
- [Performance Optimization](#performance-optimization)
- [Error Handling Strategies](#error-handling)

---

## Setting Up Development Environment

### Prerequisites
- Python 3.11+ (supports 3.11, 3.12, 3.13)
- Poetry for dependency management
- Git for version control
- A Python-aware IDE (VS Code, PyCharm, etc.)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/OmniNode-ai/omnibase-spi.git
cd omnibase-spi

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Set up pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml

# Verify installation
poetry run python -c "import omnibase.protocols; print('Import successful')"
```

### IDE Configuration

#### VS Code Settings
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.provider": "isort",
    "editor.formatOnSave": true
}
```

#### MyPy Configuration (`.mypy.ini`)
```ini
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
show_error_codes = True
namespace_packages = True
explicit_package_bases = True
```

---

## Project Structure Overview

### Package Organization
```
src/omnibase/protocols/
├── types/               # Type definitions and aliases
│   ├── core_types.py          # System-wide types
│   ├── event_bus_types.py     # Event system types
│   └── ...
├── core/                # Core system protocols
│   ├── protocol_logger.py         # Logging interfaces
│   ├── protocol_canonical_serializer.py
│   └── ...
├── event_bus/          # Event-driven architecture
│   ├── protocol_event_bus.py      # Main event bus
│   └── ...
├── container/          # Dependency injection
├── discovery/          # Service discovery
└── file_handling/      # File operations
```

### Import Hierarchy
```python
# Level 1: Type definitions (no dependencies)
from omnibase.protocols.types.core_types import LogLevel, ProtocolSemVer

# Level 2: Protocols (depend on types only)
from omnibase.protocols.core.protocol_logger import ProtocolLogger

# Level 3: Your implementations (depend on protocols)
class MyLogger(ProtocolLogger):
    # Your implementation
    pass
```

---

## Understanding Protocol Types

### Type Categories

#### 1. Literal Types
```python
from omnibase.protocols.types.core_types import LogLevel, NodeStatus
from typing import Literal

# LogLevel is defined as:
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# NodeStatus is defined as:
NodeStatus = Literal["active", "inactive", "error", "pending"]

# Usage
def log_message(level: LogLevel, message: str) -> None:
    # Type checker ensures only valid levels
    pass

log_message("INFO", "Valid log level")  # ✅ OK
# log_message("TRACE", "Invalid")      # ❌ Type error
```

#### 2. Protocol Types
```python
from omnibase.protocols.types.core_types import (
    ProtocolSemVer,
    ProtocolMetadata,
    ProtocolConfigValue
)

# ProtocolSemVer defines version interface
class Version(ProtocolSemVer):
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

# Usage in your code
def validate_version(version: ProtocolSemVer) -> bool:
    return version.major > 0 and version.minor >= 0 and version.patch >= 0
```

#### 3. Context Value Types
```python
from omnibase.protocols.types.core_types import ContextValue
from typing import Dict, List

# ContextValue is a Union type for safe value passing
ContextValue = Union[str, int, float, bool, List[str], Dict[str, str]]

def process_context(context: Dict[str, ContextValue]) -> None:
    """Type-safe context processing."""
    for key, value in context.items():
        if isinstance(value, str):
            print(f"String value: {key}={value}")
        elif isinstance(value, int):
            print(f"Integer value: {key}={value}")
        elif isinstance(value, dict):
            print(f"Dict value: {key}={value}")
        # Handle other types...
```

---

## Protocol Implementation Patterns

### 1. Simple Protocol Implementation

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from omnibase.protocols.types.core_types import LogLevel
from typing import Any
import datetime

class FileLogger(ProtocolSimpleLogger):
    """File-based logger implementation."""
    
    def __init__(self, filepath: str, min_level: LogLevel = "INFO"):
        self.filepath = filepath
        self.min_level = min_level
        self._level_values = {
            "DEBUG": 10, "INFO": 20, "WARNING": 30, 
            "ERROR": 40, "CRITICAL": 50
        }
    
    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log message to file with timestamp."""
        if not self.is_enabled(level):
            return
            
        timestamp = datetime.datetime.now().isoformat()
        extras = " ".join(f"{k}={v}" for k, v in kwargs.items())
        log_line = f"{timestamp} [{level}] {message} {extras}\n"
        
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(log_line)
    
    def is_enabled(self, level: LogLevel) -> bool:
        """Check if logging level is enabled."""
        return self._level_values.get(level, 0) >= self._level_values.get(self.min_level, 0)

# Usage
logger: ProtocolSimpleLogger = FileLogger("/tmp/app.log", "WARNING")
logger.log("ERROR", "Database connection failed", retry_count=3)
```

### 2. Complex Protocol Implementation

```python
from omnibase.protocols.core.protocol_canonical_serializer import ProtocolCanonicalSerializer
from omnibase.protocols.types.core_types import ProtocolSerializationResult
from typing import Any, Dict, List, Union
import json
import logging

class JsonCanonicalSerializer(ProtocolCanonicalSerializer):
    """JSON-based canonical serialization."""
    
    def __init__(self, indent: int = 2, sort_keys: bool = True):
        self.indent = indent
        self.sort_keys = sort_keys
        self.logger = logging.getLogger(__name__)
    
    def serialize(self, obj: Any) -> ProtocolSerializationResult:
        """Serialize object to canonical JSON string."""
        try:
            # Convert to JSON with canonical formatting
            data = json.dumps(
                obj, 
                indent=self.indent, 
                sort_keys=self.sort_keys,
                ensure_ascii=False,
                separators=(',', ': ')
            )
            
            return SerializationResult(
                success=True,
                data=data,
                error_message=None
            )
            
        except (TypeError, ValueError) as e:
            error_msg = f"Serialization failed: {e}"
            self.logger.error(error_msg)
            
            return SerializationResult(
                success=False,
                data="",
                error_message=error_msg
            )
    
    def deserialize(self, data: str, expected_type: type[Any]) -> Any:
        """Deserialize JSON string to object."""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Deserialization failed: {e}")
            raise ValueError(f"Invalid JSON data: {e}") from e
    
    def get_canonical_hash(self, obj: Any) -> str:
        """Get canonical hash of object."""
        result = self.serialize(obj)
        if not result.success:
            raise ValueError(f"Cannot hash object: {result.error_message}")
        
        import hashlib
        return hashlib.sha256(result.data.encode('utf-8')).hexdigest()

# Helper class for result protocol
class SerializationResult(ProtocolSerializationResult):
    def __init__(self, success: bool, data: str, error_message: str | None):
        self.success = success
        self.data = data
        self.error_message = error_message
```

### 3. Event Handler Implementation

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleEventHandler
from omnibase.protocols.types.core_types import ContextValue
from typing import Dict, Optional, Any, Set

class UserEventHandler(ProtocolSimpleEventHandler):
    """Handle user-related events."""
    
    def __init__(self):
        self.supported_events: Set[str] = {
            "user.created", 
            "user.updated", 
            "user.deleted",
            "user.login",
            "user.logout"
        }
        self.event_count: Dict[str, int] = {}
    
    def handle_event(
        self, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle user events and return response data."""
        if not self.can_handle(event_type):
            return None
        
        # Track event count
        self.event_count[event_type] = self.event_count.get(event_type, 0) + 1
        
        # Process based on event type
        if event_type == "user.created":
            return self._handle_user_created(event_data)
        elif event_type == "user.updated":
            return self._handle_user_updated(event_data)
        elif event_type == "user.deleted":
            return self._handle_user_deleted(event_data)
        elif event_type in ["user.login", "user.logout"]:
            return self._handle_user_session(event_type, event_data)
        
        return {"status": "processed", "event_type": event_type}
    
    def can_handle(self, event_type: str) -> bool:
        """Check if this handler can process the event type."""
        return event_type in self.supported_events
    
    def _handle_user_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user creation event."""
        user_id = data.get("user_id")
        email = data.get("email", "")
        
        # Your business logic here
        return {
            "status": "user_created",
            "user_id": user_id,
            "welcome_email_sent": bool(email),
            "timestamp": data.get("timestamp")
        }
    
    def _handle_user_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user update event."""
        return {
            "status": "user_updated",
            "user_id": data.get("user_id"),
            "fields_updated": list(data.get("changed_fields", []))
        }
    
    def _handle_user_deleted(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user deletion event."""
        return {
            "status": "user_deleted",
            "user_id": data.get("user_id"),
            "cleanup_scheduled": True
        }
    
    def _handle_user_session(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process login/logout events."""
        return {
            "status": f"session_{event_type.split('.')[1]}",
            "user_id": data.get("user_id"),
            "session_id": data.get("session_id"),
            "timestamp": data.get("timestamp")
        }

# Usage
handler = UserEventHandler()

# Handle events
result = handler.handle_event("user.created", {
    "user_id": "user_12345",
    "email": "user@example.com",
    "timestamp": "2025-08-28T10:00:00Z"
})

print(result)  # {'status': 'user_created', 'user_id': 'user_12345', ...}
```

---

## Type Safety and Strong Typing

### 1. Avoiding Any Types

```python
# ❌ Avoid using Any
from typing import Any

def bad_process(data: Any) -> Any:
    return data.do_something()  # No type safety

# ✅ Use specific types
from omnibase.protocols.types.core_types import ContextValue
from typing import Dict, Union

def good_process(data: Dict[str, ContextValue]) -> str:
    """Process data with full type safety."""
    result_parts = []
    
    for key, value in data.items():
        if isinstance(value, str):
            result_parts.append(f"{key}: {value}")
        elif isinstance(value, (int, float)):
            result_parts.append(f"{key}: {value:,.2f}")
        elif isinstance(value, bool):
            result_parts.append(f"{key}: {'Yes' if value else 'No'}")
        elif isinstance(value, list):
            result_parts.append(f"{key}: {', '.join(map(str, value))}")
        elif isinstance(value, dict):
            nested = ', '.join(f"{k}={v}" for k, v in value.items())
            result_parts.append(f"{key}: {{{nested}}}")
    
    return "; ".join(result_parts)
```

### 2. Type Guards and Validation

```python
from omnibase.protocols.types.core_types import LogLevel, ProtocolSemVer
from typing import TypeGuard

def is_valid_log_level(value: str) -> TypeGuard[LogLevel]:
    """Type guard for log levels."""
    return value in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

def validate_version_protocol(obj: Any) -> TypeGuard[ProtocolSemVer]:
    """Type guard for semantic version protocol."""
    return (
        hasattr(obj, 'major') and isinstance(obj.major, int) and
        hasattr(obj, 'minor') and isinstance(obj.minor, int) and
        hasattr(obj, 'patch') and isinstance(obj.patch, int) and
        hasattr(obj, '__str__') and callable(obj.__str__)
    )

# Usage
def safe_log(level_str: str, message: str, logger: ProtocolSimpleLogger) -> None:
    """Safely log with type validation."""
    if is_valid_log_level(level_str):
        logger.log(level_str, message)  # level_str is now typed as LogLevel
    else:
        logger.log("ERROR", f"Invalid log level: {level_str}")
```

### 3. Generic Protocol Implementation

```python
from typing import TypeVar, Generic, Protocol, Dict, List, Optional
from omnibase.protocols.types.core_types import ContextValue

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class ProtocolCache(Protocol, Generic[K, V]):
    """Generic cache protocol."""
    
    def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        ...
    
    def set(self, key: K, value: V) -> None:
        """Set value for key."""
        ...
    
    def delete(self, key: K) -> bool:
        """Delete key and return True if existed."""
        ...
    
    def clear(self) -> None:
        """Clear all cached values."""
        ...

class MemoryCache(Generic[K, V], ProtocolCache[K, V]):
    """In-memory cache implementation."""
    
    def __init__(self):
        self._store: Dict[K, V] = {}
    
    def get(self, key: K) -> Optional[V]:
        return self._store.get(key)
    
    def set(self, key: K, value: V) -> None:
        self._store[key] = value
    
    def delete(self, key: K) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False
    
    def clear(self) -> None:
        self._store.clear()

# Usage with specific types
string_cache: ProtocolCache[str, str] = MemoryCache[str, str]()
context_cache: ProtocolCache[str, ContextValue] = MemoryCache[str, ContextValue]()

string_cache.set("user:123", "John Doe")
user_name = string_cache.get("user:123")  # Type: Optional[str]

context_cache.set("config:debug", True)
debug_flag = context_cache.get("config:debug")  # Type: Optional[ContextValue]
```

---

## Namespace Isolation

### Understanding the Rules

omnibase-spi maintains **complete namespace isolation** to prevent circular dependencies:

```python
# ✅ ALLOWED - omnibase.protocols imports only
from omnibase.protocols.core.protocol_logger import ProtocolLogger
from omnibase.protocols.types.core_types import LogLevel
from omnibase.protocols.event_bus.protocol_event_bus import ProtocolEventBus

# ❌ FORBIDDEN - External omnibase imports
# from omnibase.core.logger import ConcreteLogger     # Creates circular dependency
# from omnibase.model.event import EventModel        # Violates isolation
# from omnibase.utils.helpers import helper_function # Not allowed
```

### Working with External Models

Use `TYPE_CHECKING` imports for external model references:

```python
from typing import TYPE_CHECKING, Protocol, List
from omnibase.protocols.types.core_types import ProtocolSemVer

if TYPE_CHECKING:
    # These imports are only used for type checking
    # They don't create runtime dependencies
    from external.package.model import ExternalModel
    from another.package.types import CustomType

class ProtocolModelProcessor(Protocol):
    """Protocol that references external models safely."""
    
    def process_model(self, model: "ExternalModel") -> str:
        """Process external model (forward reference)."""
        ...
    
    def validate_custom_type(self, data: "CustomType") -> bool:
        """Validate custom type data."""
        ...
    
    def get_supported_versions(self) -> List[ProtocolSemVer]:
        """Get list of supported versions."""
        ...
```

### Validation Scripts

Use the provided validation scripts to ensure namespace isolation:

```bash
# Validate namespace isolation
./scripts/validate-namespace-isolation.sh

# Check for forbidden imports
grep -r "from omnibase\." src/ | grep -v "from omnibase.protocols"

# Should return no results - any output indicates violation
```

---

## Forward References and TYPE_CHECKING

### Basic Pattern

```python
from typing import TYPE_CHECKING, Protocol
from omnibase.protocols.types.core_types import ContextValue

if TYPE_CHECKING:
    # Runtime-free imports for type checking only
    from complex.external.package import ComplexModel
    from another.package.types import CustomResult

class ProtocolComplexProcessor(Protocol):
    """Protocol with forward references to external types."""
    
    def process_complex(self, model: "ComplexModel") -> "CustomResult":
        """Process complex model and return custom result."""
        ...
    
    def extract_metadata(self, model: "ComplexModel") -> Dict[str, ContextValue]:
        """Extract metadata from complex model."""
        ...
```

### Advanced Forward Reference Patterns

```python
from typing import TYPE_CHECKING, Protocol, Generic, TypeVar, List, Dict, Optional
from omnibase.protocols.types.core_types import ProtocolSemVer, ContextValue

if TYPE_CHECKING:
    from external.models import DataModel, ProcessingResult, ValidationError
    from external.interfaces import ConfigurationInterface

T = TypeVar('T')
R = TypeVar('R')

class ProtocolAdvancedProcessor(Protocol, Generic[T, R]):
    """Advanced processor with generic forward references."""
    
    def process_batch(self, models: List["DataModel"]) -> List["ProcessingResult"]:
        """Process a batch of data models."""
        ...
    
    def configure(self, config: "ConfigurationInterface") -> None:
        """Configure processor with external configuration."""
        ...
    
    def validate_input(self, model: "DataModel") -> Optional["ValidationError"]:
        """Validate input model and return error if invalid."""
        ...
    
    def process_with_callback(
        self, 
        model: "DataModel", 
        callback: Callable[["ProcessingResult"], None]
    ) -> None:
        """Process model and call callback with result."""
        ...

# Generic implementation
class BatchProcessor(Generic[T, R], ProtocolAdvancedProcessor[T, R]):
    """Concrete implementation of advanced processor."""
    
    def __init__(self):
        self._config: Optional["ConfigurationInterface"] = None
        self._results_cache: Dict[str, "ProcessingResult"] = {}
    
    def process_batch(self, models: List["DataModel"]) -> List["ProcessingResult"]:
        """Process batch with caching."""
        results = []
        
        for model in models:
            # In actual implementation, model would be the real type
            # Type checking ensures we use it correctly
            model_id = getattr(model, 'id', str(id(model)))
            
            if model_id in self._results_cache:
                results.append(self._results_cache[model_id])
            else:
                # Process model (implementation details here)
                result = self._process_single(model)
                self._results_cache[model_id] = result
                results.append(result)
        
        return results
    
    def _process_single(self, model: "DataModel") -> "ProcessingResult":
        """Process single model - implementation specific."""
        # Implementation would use actual model methods/attributes
        pass
```

### Circular Reference Resolution

```python
from typing import TYPE_CHECKING, Protocol, ForwardRef
from omnibase.protocols.types.core_types import ProtocolSemVer

if TYPE_CHECKING:
    from external.node import NodeModel
    from external.graph import GraphModel

class ProtocolNodeProcessor(Protocol):
    """Protocol for processing nodes that reference each other."""
    
    def process_node(self, node: "NodeModel", graph: "GraphModel") -> None:
        """Process node within graph context."""
        ...
    
    def find_dependencies(self, node: "NodeModel") -> List["NodeModel"]:
        """Find all nodes that this node depends on."""
        ...
    
    def build_execution_order(self, nodes: List["NodeModel"]) -> List["NodeModel"]:
        """Build execution order resolving circular dependencies."""
        ...

# For very complex circular references, you can use ForwardRef
NodeRef = ForwardRef('NodeModel')
GraphRef = ForwardRef('GraphModel')

class ProtocolGraphAnalyzer(Protocol):
    """Protocol using explicit forward references."""
    
    def analyze_graph(self, graph: GraphRef) -> Dict[str, ContextValue]:
        """Analyze graph structure."""
        ...
    
    def detect_cycles(self, graph: GraphRef) -> List[List[NodeRef]]:
        """Detect circular dependencies in graph."""
        ...
```

This comprehensive developer guide provides the foundation for working effectively with omnibase-spi. Continue with the specific sections for deeper dives into particular topics.

## Next Steps

- [Protocol Implementation Guide](protocol-implementation.md) - Detailed protocol implementation patterns
- [Type Safety Guide](type-safety.md) - Advanced typing techniques
- [Testing Guide](testing.md) - Testing strategies for protocol-based code
- [API Reference](../api-reference/) - Complete protocol documentation
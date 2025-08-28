# Quick Start Guide

Get up and running with omnibase-spi in minutes. This guide covers the essential steps to start using ONEX protocol interfaces in your projects.

## What is omnibase-spi?

omnibase-spi is a **Service Provider Interface (SPI) package** that provides pure Python protocols for the ONEX ecosystem. It enables:

- **Type-safe interfaces** without concrete implementations
- **Zero-dependency architecture** for namespace isolation
- **Protocol-based dependency injection** using duck typing
- **Strong typing** throughout the ONEX ecosystem

## Installation

### Prerequisites
- Python 3.11, 3.12, or 3.13
- pip or Poetry for package management

### Install from PyPI
```bash
pip install omnibase-spi
```

### Install with Poetry
```bash
poetry add omnibase-spi
```

### Development Installation
```bash
git clone https://github.com/OmniNode-ai/omnibase-spi.git
cd omnibase-spi
poetry install
```

## Basic Usage

### Importing Protocols

```python
# Import core protocols
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer
)

# Import event bus protocols
from omnibase.protocols.event_bus.protocol_event_bus import ProtocolEventBus

# Import type definitions
from omnibase.protocols.types.core_types import LogLevel, ProtocolSemVer
```

### Implementing a Protocol

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from omnibase.protocols.types.core_types import LogLevel
from typing import Any

class ConsoleLogger(ProtocolSimpleLogger):
    """Simple console logger implementation."""
    
    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log message to console with level prefix."""
        prefix = f"[{level}]"
        extras = " ".join(f"{k}={v}" for k, v in kwargs.items())
        print(f"{prefix} {message} {extras}".strip())
    
    def is_enabled(self, level: LogLevel) -> bool:
        """Check if logging level is enabled."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        return level in levels

# Usage
logger: ProtocolSimpleLogger = ConsoleLogger()
logger.log("INFO", "Application started", user_id="12345")
```

### Using Protocol Types

```python
from omnibase.protocols.types.core_types import (
    ProtocolSemVer, 
    ProtocolMetadata, 
    ContextValue
)
from datetime import datetime
from typing import Dict

# Creating a semantic version
class AppVersion:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor  
        self.patch = patch
        
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

version: ProtocolSemVer = AppVersion(1, 0, 0)

# Working with metadata
metadata_dict: Dict[str, ContextValue] = {
    "version": str(version),
    "environment": "development",
    "debug": True,
    "max_connections": 100
}
```

## Key Concepts

### Protocol-First Design
omnibase-spi uses Python's `typing.Protocol` for interface definition:

```python
from typing import Protocol

class ProtocolExample(Protocol):
    """Protocol defines interface contract without implementation."""
    
    def process(self, data: str) -> str:
        """Process data and return result."""
        ...  # No implementation - just contract
    
    def is_ready(self) -> bool:
        """Check if processor is ready."""
        ...
```

### Strong Typing
All protocols use strong typing with no `Any` types:

```python
from typing import Dict, List, Optional, Union
from omnibase.protocols.types.core_types import ContextValue

# Strong type definitions
def process_config(
    config: Dict[str, ContextValue],
    options: Optional[List[str]] = None
) -> Union[str, int, bool]:
    """Example of strong typing throughout."""
    pass
```

### Namespace Isolation
omnibase-spi maintains complete namespace isolation:

```python
# ✅ CORRECT - Only omnibase.protocols imports allowed
from omnibase.protocols.core.protocol_logger import ProtocolLogger
from omnibase.protocols.types.core_types import LogLevel

# ❌ FORBIDDEN - No external omnibase imports
# from omnibase.core.logger import Logger  # Would create circular dependency
# from omnibase.model.event import Event   # Violates namespace isolation
```

## Common Patterns

### Dependency Injection with Protocols

```python
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer
)

class ServiceClass:
    """Service using protocol-based dependency injection."""
    
    def __init__(
        self, 
        logger: ProtocolSimpleLogger,
        serializer: ProtocolSimpleSerializer
    ):
        self._logger = logger
        self._serializer = serializer
    
    def process_data(self, data: dict) -> str:
        """Process data with logging and serialization."""
        self._logger.log("INFO", "Processing data", record_count=len(data))
        
        try:
            result = self._serializer.serialize(data)
            self._logger.log("INFO", "Data processed successfully")
            return result
        except Exception as e:
            self._logger.log("ERROR", f"Processing failed: {e}")
            raise

# Usage with concrete implementations
service = ServiceClass(
    logger=ConsoleLogger(),
    serializer=JsonSerializer()  # Your implementation
)
```

### Type-Safe Configuration

```python
from omnibase.protocols.types.core_types import ProtocolConfigValue, ContextValue
from typing import Dict, List

class ConfigManager:
    """Type-safe configuration management."""
    
    def __init__(self):
        self._config: Dict[str, ContextValue] = {}
    
    def set_value(self, key: str, value: ContextValue) -> None:
        """Set configuration value with type safety."""
        self._config[key] = value
    
    def get_string(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
        value = self._config.get(key, default)
        return str(value) if value is not None else default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self._config.get(key, default)
        return int(value) if isinstance(value, (int, str)) else default

# Usage
config = ConfigManager()
config.set_value("database_host", "localhost")
config.set_value("database_port", 5432)
config.set_value("debug_enabled", True)

host = config.get_string("database_host")
port = config.get_int("database_port")
```

## Next Steps

Now that you have omnibase-spi installed and understand the basics:

1. **[Core Concepts](core-concepts.md)** - Deep dive into SPI design principles
2. **[Installation Guide](installation.md)** - Complete installation and setup details
3. **[First Protocol Tutorial](first-protocol.md)** - Step-by-step protocol implementation
4. **[Developer Guide](../developer-guide/README.md)** - Comprehensive development guide
5. **[API Reference](../api-reference/)** - Detailed protocol documentation

## Getting Help

- **Documentation**: Browse the complete documentation in the `docs/` directory
- **Examples**: Check the `src/omnibase/protocols/core/protocol_simple_example.py` for template patterns
- **Issues**: Report issues on the main repository
- **Community**: Join ONEX community discussions for support

## Common Gotchas

### Import Errors
```python
# ❌ Don't do this - violates namespace isolation
from omnibase.core import SomeClass

# ✅ Do this - use only protocols namespace
from omnibase.protocols.core.protocol_logger import ProtocolLogger
```

### Protocol Implementation
```python
# ❌ Don't implement with pass
def method(self) -> str:
    pass  # Will raise NotImplementedError

# ✅ Do implement with actual logic
def method(self) -> str:
    return "actual implementation"
```

### Type Annotations
```python
# ❌ Don't use Any types
from typing import Any
def process(data: Any) -> Any: pass

# ✅ Use specific types
from omnibase.protocols.types.core_types import ContextValue
def process(data: Dict[str, ContextValue]) -> str: pass
```
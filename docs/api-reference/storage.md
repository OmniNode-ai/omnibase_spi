# Storage Protocols

## Overview

Storage protocols provide data persistence and backend capabilities for various storage systems.

## Protocol Categories

### Storage Operations
- **ProtocolStorageProvider** - Storage provider interface
- **ProtocolStorageBackend** - Storage backend operations
- **ProtocolStorageCache** - Storage caching

## Usage Examples

```python
from omnibase_spi.protocols.storage import ProtocolStorageProvider

# Initialize storage provider
storage: ProtocolStorageProvider = get_storage_provider()

# Store data
await storage.store(
    key="user:12345",
    value={"name": "John Doe", "email": "john@example.com"},
    ttl=3600
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

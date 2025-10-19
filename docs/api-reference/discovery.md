# Discovery Protocols

## Overview

Discovery protocols provide service and handler discovery capabilities for dynamic service resolution.

## Protocol Categories

### Service Discovery
- **ProtocolDiscoveryClient** - Discovery client operations
- **ProtocolHandlerDiscovery** - Handler discovery
- **ProtocolHandler** - Handler interface

## Usage Examples

```python
from omnibase_spi.protocols.discovery import ProtocolHandlerDiscovery

# Initialize handler discovery
discovery: ProtocolHandlerDiscovery = get_handler_discovery()

# Discover handlers
handlers = await discovery.discover_handlers(
    service_type="workflow",
    interface=ProtocolWorkflowOrchestrator
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

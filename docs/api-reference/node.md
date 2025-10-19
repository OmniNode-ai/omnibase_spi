# Node Management Protocols

## Overview

Node management protocols provide node configuration and registry capabilities for distributed systems.

## Protocol Categories

### Node Operations
- **ProtocolNode** - Core node interface
- **ProtocolNodeRegistry** - Node registry management
- **ProtocolNodeConfiguration** - Node configuration
- **ProtocolNodeHealth** - Node health monitoring
- **ProtocolNodeDiscovery** - Node discovery

## Usage Examples

```python
from omnibase_spi.protocols.node import ProtocolNodeRegistry

# Initialize node registry
registry: ProtocolNodeRegistry = get_node_registry()

# Register node
await registry.register_node(
    node_id="node-001",
    host="192.168.1.100",
    port=8080,
    capabilities=["workflow", "memory"]
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

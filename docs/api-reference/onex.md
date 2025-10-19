# ONEX Platform Protocols

## Overview

ONEX platform protocols provide platform-specific capabilities and integrations.

## Protocol Categories

### Platform Integration
- **ProtocolONEXPlatform** - Core platform interface
- **ProtocolONEXIntegration** - Platform integration
- **ProtocolONEXWorkflow** - Platform workflow
- **ProtocolONEXMemory** - Platform memory
- **ProtocolONEXEvent** - Platform events
- **ProtocolONEXNode** - Platform nodes

## Usage Examples

```python
from omnibase_spi.protocols.onex import ProtocolONEXPlatform

# Initialize ONEX platform
platform: ProtocolONEXPlatform = get_onex_platform()

# Execute platform operation
result = await platform.execute_operation(
    operation="deploy_workflow",
    parameters={"workflow_id": "wf-123"}
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

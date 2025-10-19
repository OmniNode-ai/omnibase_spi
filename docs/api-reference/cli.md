# CLI Protocols

## Overview

CLI protocols provide command line interface operations and tool discovery capabilities.

## Protocol Categories

### CLI Operations
- **ProtocolCLI** - Core CLI functionality
- **ProtocolCLIWorkflow** - CLI workflow management
- **ProtocolCLIToolDiscovery** - CLI tool discovery

### CLI Fixtures
- **ProtocolCLIDirFixtureCase** - Directory fixture test cases
- **ProtocolCLIDirFixtureRegistry** - Directory fixture registry

### Node Integration
- **ProtocolNodeCLIAdapter** - Node CLI integration

## Usage Examples

```python
from omnibase_spi.protocols.cli import ProtocolCLI

# Initialize CLI
cli: ProtocolCLI = get_cli()

# Execute CLI command
result = await cli.execute_command(
    command="omnibase --version",
    args=["--verbose"]
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

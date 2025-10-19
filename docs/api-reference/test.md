# Test Protocols

## Overview

Test protocols provide testing frameworks and utilities for comprehensive test coverage.

## Protocol Categories

### Testing Framework
- **ProtocolTestRunner** - Test execution
- **ProtocolTestFixture** - Test fixtures
- **ProtocolTestValidator** - Test validation

## Usage Examples

```python
from omnibase_spi.protocols.test import ProtocolTestRunner

# Initialize test runner
runner: ProtocolTestRunner = get_test_runner()

# Execute tests
results = await runner.run_tests(
    test_suite="integration_tests",
    parallel=True
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

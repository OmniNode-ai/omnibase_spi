# Quick Usage Guide - Protocol Validation Utilities

## Quick Start

### 1. Basic Validation
```python
from omnibase_spi.protocols.validation import validate_protocol_implementation
from omnibase_spi.protocols.container.protocol_artifact_container import ProtocolArtifactContainer

# Your implementation
container = MyArtifactContainer()

# Validate it
result = validate_protocol_implementation(container, ProtocolArtifactContainer)

if result.is_valid:
    print("✓ Implementation is valid!")
else:
    print("✗ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

### 2. Automatic Validation with Decorators
```python
from omnibase_spi.protocols.validation import validation_decorator

@validation_decorator(ProtocolArtifactContainer)
class MyContainer:
    # Implementation automatically validated on instantiation
    def get_status(self): ...
    def get_artifacts(self): ...
    # ... other methods

container = MyContainer()  # Validates automatically
```

### 3. Specialized Validators
```python
from omnibase_spi.protocols.validation import ArtifactContainerValidator

# Use domain-specific validator
validator = ArtifactContainerValidator(strict_mode=True)
result = validator.validate_implementation(container, ProtocolArtifactContainer)

print(result.get_summary())  # Detailed report
```

## Common Error Types

| Error | Meaning | Fix |
|-------|---------|-----|
| `missing_method` | Protocol method not implemented | Add the missing method |
| `not_callable` | Attribute exists but isn't a method | Make it callable |
| `parameter_count_mismatch` | Wrong number of parameters | Match protocol signature |

## Environment Setup

The validation utilities automatically detect development vs production:

- **Development**: Full validation enabled
- **Production**: Validation automatically disabled

Override with:
```python
from omnibase_spi.protocols.validation import enable_protocol_validation

enable_protocol_validation(True)   # Force enable
enable_protocol_validation(False)  # Force disable
```

## Running Tests

```bash
# Run examples
python -m omnibase_spi.protocols.validation.examples

# Run integration tests  
python src/omnibase/protocols/validation/test_integration.py
```

## Development Workflow

1. **Early Development**: Use basic validation to identify missing methods
2. **Implementation**: Use decorators for automatic validation  
3. **Testing**: Use specialized validators for comprehensive checks
4. **Deployment**: Final validation before production

## Need Help?

- Check the [README.md](./README.md) for detailed documentation
- Example files are not included in the SPI package
- Integration tests are implementation-specific

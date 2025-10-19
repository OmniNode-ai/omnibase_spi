# Protocol Validation Utilities

Enhanced runtime validation helpers for protocol implementations in the omnibase-spi project.

## ⚠️ Architecture Note

This module contains **reference implementations and validation utilities**, not pure SPI protocol definitions. It is intentionally excluded from SPI purity validation checks to maintain clear architectural separation between:

- **Pure SPI Protocols** (interface definitions only)
- **Reference Implementations** (concrete classes with logic)

This separation ensures the core SPI maintains zero dependencies while providing practical validation tools.

## Overview

This module provides comprehensive runtime validation utilities for ONEX SPI protocol implementations. These tools help catch protocol misuse early during development, providing clear error messages and improving developer experience while maintaining SPI purity (zero external dependencies).

## Key Features

- **Runtime Protocol Validation**: Validate protocol implementations at runtime during development
- **Protocol Contract Enforcement**: Catch protocol misuse early with clear error messages
- **Development-Time Focus**: Designed for development validation, not production runtime
- **Integration Ready**: Works seamlessly with existing `@runtime_checkable` protocol system
- **Zero Dependencies**: Maintains SPI purity with no external dependencies
- **Clear Error Messages**: Actionable validation errors with context and guidance
- **Optional Validation**: Opt-in decorators and utilities that don't break existing code

## Quick Start

### Basic Validation

```python
from omnibase_spi.protocols.validation import validate_protocol_implementation
from omnibase_spi.protocols.container.protocol_artifact_container import ProtocolArtifactContainer

# Your implementation
class MyArtifactContainer:
    def get_status(self):
        # Implementation...
        pass

    def get_artifacts(self):
        # Implementation...
        pass
    # ... other methods

# Validate implementation
container = MyArtifactContainer()
result = validate_protocol_implementation(container, ProtocolArtifactContainer)

if not result.is_valid:
    print("Validation failed!")
    for error in result.errors:
        print(f"  - {error}")
```

### Using Validation Decorators

```python
from omnibase_spi.protocols.validation import validation_decorator

@validation_decorator(ProtocolArtifactContainer)
class MyArtifactContainer:
    def get_status(self):
        # Implementation automatically validated on instantiation
        pass

    # ... other methods

# Validation occurs when creating instance
container = MyArtifactContainer()  # Validates against protocol
```

### Specialized Validators

```python
from omnibase_spi.protocols.validation import ArtifactContainerValidator

# Use specialized validator for domain-specific checks
validator = ArtifactContainerValidator(strict_mode=True)
result = validator.validate_implementation(container, ProtocolArtifactContainer)

# Get detailed analysis
print(result.get_summary())
```

## Architecture

### Core Components

1. **ProtocolValidator**: Core validation engine using Python introspection
2. **ValidationResult**: Comprehensive validation results with errors and warnings
3. **ValidationError**: Detailed error information with context and severity
4. **Validation Decorators**: Automatic validation through decorators
5. **Specialized Validators**: Domain-specific validation for key protocols

### Validation Levels

- **Basic**: Method presence and callable validation
- **Standard**: Method signatures and parameter validation  
- **Strict**: Type annotations and return type validation
- **Specialized**: Domain-specific business rule validation

## Supported Protocols

### Currently Supported

- **ProtocolArtifactContainer**: Artifact container implementations
- **ProtocolNodeRegistry**: Node registry implementations
- **ProtocolHandlerDiscovery**: Handler discovery implementations
- **Generic Service Registries**: Common registry patterns

### Specialized Validators

Each protocol has a specialized validator that extends basic validation:

```python
# Artifact Container Validator
validator = ArtifactContainerValidator()
# - Validates status object consistency
# - Checks artifact count accuracy
# - Tests artifact type filtering
# - Validates business rules

# Node Registry Validator  
validator = NodeRegistryValidator()
# - Validates async method signatures
# - Checks initialization parameters
# - Validates discovery functionality
# - Tests registry patterns

# Handler Discovery Validator
validator = HandlerDiscoveryValidator()
# - Validates discovered handler info
# - Checks source name functionality
# - Tests discovery consistency
# - Validates handler metadata
```

## Usage Patterns

### Development Workflow

1. **Early Validation**: Check basic protocol compliance
2. **Iterative Development**: Identify missing methods and signatures
3. **Business Rule Validation**: Ensure domain-specific correctness
4. **Pre-deployment Check**: Comprehensive validation before production

```python
# Development cycle
class MyImplementation:
    pass

# 1. Early check (non-strict)
result = validate_protocol_implementation(my_impl, MyProtocol, strict_mode=False)
print(f"Completeness: {100 - len(result.errors) * 10}%")

# 2. Identify next steps
missing_methods = [e for e in result.errors if e.error_type == 'missing_method']
print("Implement next:", [e.context['method'] for e in missing_methods[:3]])

# 3. Final validation (strict)
result = MyProtocolValidator().validate_implementation(my_impl, MyProtocol)
if result.is_valid:
    deploy(my_impl)
```

### Error Analysis

```python
# Comprehensive error analysis
result = validator.validate_implementation(implementation, protocol)

# Categorize errors by type
error_types = {}
for error in result.errors:
    error_type = error.error_type
    error_types.setdefault(error_type, []).append(error)

# Show breakdown
for error_type, errors in error_types.items():
    print(f"{error_type}: {len(errors)} occurrences")
```

### Integration with Testing

```python
import unittest
from omnibase_spi.protocols.validation import ArtifactContainerValidator

class TestMyContainer(unittest.TestCase):
    def setUp(self):
        self.container = MyArtifactContainer()
        self.validator = ArtifactContainerValidator()

    def test_protocol_compliance(self):
        result = self.validator.validate_implementation(
            self.container,
            ProtocolArtifactContainer
        )

        self.assertTrue(result.is_valid,
                       f"Protocol validation failed:\\n{result.get_summary()}")

        # Allow warnings but no errors
        self.assertEqual(len(result.errors), 0)
```

## Configuration

### Environment Control

Validation automatically detects development vs production:

```python
# Automatically disabled in production
@validation_decorator(MyProtocol, development_only=True)
class MyImplementation:
    pass

# Manual control
from omnibase_spi.protocols.validation import enable_protocol_validation

enable_protocol_validation(False)  # Disable globally
enable_protocol_validation(True)   # Enable globally
```

### Validation Modes

```python
# Strict mode: Full type checking and signatures
validator = ProtocolValidator(strict_mode=True)

# Lenient mode: Basic method presence only  
validator = ProtocolValidator(strict_mode=False)

# Custom validation
@validation_decorator(MyProtocol,
                     strict_mode=True,
                     raise_on_error=False,  # Warn instead of raising
                     development_only=True)  # Only in development
```

## Error Types and Resolution

### Common Error Types

| Error Type | Description | Resolution |
|------------|-------------|------------|
| `missing_method` | Required protocol method not implemented | Implement the missing method |
| `not_callable` | Attribute exists but is not callable | Make the attribute a method |
| `parameter_count_mismatch` | Method parameter count differs | Match protocol method signature |
| `type_mismatch` | Type annotation doesn't match protocol | Update type annotations |
| `protocol_compliance` | Basic isinstance check fails | Ensure class implements protocol |

### Business Rule Errors

| Error Type | Description | Resolution |
|------------|-------------|------------|
| `status_count_inconsistency` | Status counts don't add up | Fix count calculations |
| `artifact_count_mismatch` | Status vs actual artifact counts differ | Synchronize count logic |
| `artifact_types_mismatch` | Type lists inconsistent | Fix type reporting |
| `non_async_method` | Method should be async but isn't | Make method async |

## Examples

Example files are not included in the SPI package. For usage examples, see:

1. **Basic Validation**: Core protocol validation
2. **Validation Decorators**: Automatic validation on instantiation
3. **Specialized Validators**: Domain-specific validation
4. **Handler Discovery**: Validating discovery implementations  
5. **Error Handling**: Comprehensive error analysis
6. **Development Workflow**: Integration into development process

Run examples:

```bash
python -m omnibase_spi.protocols.validation.examples
```

## Best Practices

### During Development

1. **Start Early**: Use basic validation from the beginning
2. **Iterative Approach**: Fix errors incrementally
3. **Use Decorators**: Automatic validation catches issues early
4. **Check Business Rules**: Use specialized validators for domain logic

### Code Organization

```python
# Good: Separate concerns
@validation_decorator(ProtocolArtifactContainer, development_only=True)
class ProductionArtifactContainer:
    """Production-ready container with validation."""
    pass

# Good: Test validation separately  
class TestValidation(unittest.TestCase):
    def test_container_validation(self):
        validator = ArtifactContainerValidator()
        result = validator.validate_implementation(container, protocol)
        self.assertTrue(result.is_valid)

# Avoid: Validation in production hot paths
def process_request():
    # Don't validate on every request in production
    validate_protocol_implementation(impl, protocol)  # ❌
```

### Error Handling

```python
# Good: Handle validation results appropriately
result = validate_protocol_implementation(impl, protocol)
if not result.is_valid:
    logger.warning(f"Protocol validation failed: {result.get_summary()}")
    # Continue with degraded functionality or fail gracefully

# Good: Use strict validation before deployment
if not specialized_validator.validate_implementation(impl, protocol).is_valid:
    raise DeploymentError("Implementation failed validation")

# Avoid: Ignoring validation results
validate_protocol_implementation(impl, protocol)  # ❌ Not checking result
```

## Contributing

When adding new protocol validators:

1. **Extend ProtocolValidator**: Inherit from base validator
2. **Add Domain Logic**: Implement protocol-specific validation
3. **Provide Examples**: Include usage examples
4. **Document Errors**: Describe error types and resolution
5. **Test Thoroughly**: Validate both correct and incorrect implementations

Example new validator:

```python
class MyProtocolValidator(ProtocolValidator):
    def validate_implementation(self, implementation, protocol=MyProtocol):
        result = super().validate_implementation(implementation, protocol)
        self._validate_my_protocol_rules(implementation, result)
        return result

    def _validate_my_protocol_rules(self, implementation, result):
        # Domain-specific validation logic
        pass
```

## Troubleshooting

### Common Issues

**Q: Validation always passes even with obvious errors**  
A: Check if development mode is detected correctly. Set `ENVIRONMENT=dev` or `DEBUG=true`.

**Q: Too many false positive warnings**  
A: Use `strict_mode=False` during early development, enable strict mode before deployment.

**Q: Performance impact in production**  
A: Validation is automatically disabled in production when `development_only=True` (default).

**Q: Custom protocols not validating**  
A: Ensure protocol is decorated with `@runtime_checkable` and implement a specialized validator.

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get full validation details
result = validator.validate_implementation(impl, protocol)
print(result.get_summary())  # Full detailed output
```

## License

Part of the omnibase-spi project. See project license for details.

# Schema Protocols

## Overview

Schema protocols provide schema loading and validation capabilities for data structure management.

## Protocol Categories

### Schema Management
- **ProtocolSchemaLoader** - Schema loading
- **ProtocolSchemaValidator** - Schema validation
- **ProtocolSchemaRegistry** - Schema registry
- **ProtocolSchemaResolver** - Schema resolution
- **ProtocolSchemaCache** - Schema caching
- **ProtocolSchemaMigration** - Schema migration
- **ProtocolSchemaVersioning** - Schema versioning
- **ProtocolSchemaCompatibility** - Schema compatibility
- **ProtocolSchemaDocumentation** - Schema documentation
- **ProtocolSchemaTesting** - Schema testing

## Usage Examples

```python
from omnibase_spi.protocols.schema import ProtocolSchemaValidator

# Initialize schema validator
validator: ProtocolSchemaValidator = get_schema_validator()

# Validate data against schema
is_valid = await validator.validate(
    data={"name": "John", "age": 30},
    schema_id="user_schema_v1"
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*

# Codebase Structure: omnibase-spi

## Root Directory Structure
```
omnibase-spi/
├── src/omnibase/protocols/           # Main protocol package
├── tests/                           # Test suite
├── scripts/                         # Validation scripts
├── pyproject.toml                   # Poetry configuration
├── README.md                        # Project documentation
├── .mypy.ini                        # MyPy configuration
├── .pre-commit-config.yaml          # Pre-commit hooks
├── .pre-commit-config-push.yaml     # Pre-push validation
└── .gitignore                       # Git ignore patterns
```

## Protocol Package Structure
```
src/omnibase/protocols/
├── __init__.py                      # Package exports
├── types/                           # Type definitions
│   ├── __init__.py
│   ├── core_types.py               # Core system types
│   ├── event_bus_types.py          # Event bus types  
│   ├── container_types.py          # Container types
│   ├── discovery_types.py          # Discovery types
│   └── file_handling_types.py      # File handling types
├── core/                           # Core system protocols
│   ├── __init__.py
│   ├── [removed - template protocols]
│   ├── protocol_canonical_serializer.py
│   ├── protocol_schema_loader.py
│   ├── protocol_workflow_reducer.py
│   ├── protocol_onex_envelope.py
│   ├── protocol_onex_reply.py
│   ├── protocol_onex_node.py
│   ├── protocol_onex_validation.py
│   ├── protocol_reducer.py
│   ├── protocol_core_logging.py
│   └── protocol_logger.py
├── event_bus/                      # Event system protocols
│   ├── __init__.py
│   ├── protocol_event_bus.py
│   └── protocol_event_bus_types.py
├── container/                      # Dependency injection
│   ├── __init__.py
│   └── protocol_registry.py
├── discovery/                      # Service discovery
│   ├── __init__.py
│   └── protocol_handler_discovery.py
└── file_handling/                  # File processing
    ├── __init__.py
    └── protocol_file_type_handler.py
```

## File Naming Conventions
- **Protocol Files**: `protocol_<domain>.py` (e.g., `protocol_event_bus.py`)
- **Type Files**: `<domain>_types.py` (e.g., `core_types.py`)
- **Package Directories**: `<domain>/` (e.g., `event_bus/`, `file_handling/`)
- **Init Files**: `__init__.py` with minimal exports

## Domain Organization

### Core Domain (`protocols/core/`)
- **System Protocols**: Logging, serialization, validation
- **Node Protocols**: ONEX node interfaces
- **Workflow Protocols**: Reducer patterns and workflow management
- **Envelope Protocols**: Message envelope handling

### Event Bus Domain (`protocols/event_bus/`)  
- **Event Bus**: Main event system interface
- **Event Types**: Event-specific type definitions
- **Publisher/Subscriber**: Event publishing and subscription

### Container Domain (`protocols/container/`)
- **Registry**: Service registration and discovery
- **Injection**: Dependency injection interfaces

### Discovery Domain (`protocols/discovery/`)
- **Handler Discovery**: Service and handler discovery
- **Service Location**: Service lookup and registration

### File Handling Domain (`protocols/file_handling/`)
- **File Type Handlers**: File processing interfaces
- **File Operations**: File reading, writing, processing

### Types Domain (`protocols/types/`)
- **Core Types**: System-wide type definitions
- **Domain Types**: Domain-specific type collections
- **Protocol Types**: Supporting types for protocols

## Key Architectural Patterns

### Namespace Isolation
- **Strict Imports**: Only `from omnibase.protocols.*` allowed
- **No External Dependencies**: No imports from omnibase-core or other packages
- **Forward References**: Use `TYPE_CHECKING` for external model types

### Protocol Design Patterns
- **Pure Protocols**: No concrete implementations
- **Method Protocols**: Behavior-based interfaces
- **Attribute Protocols**: Data structure interfaces
- **Mixed Protocols**: Combined attribute and method interfaces

### Type Safety Patterns
- **No Any Types**: Use specific types or Union types
- **Literal Types**: String literals for constants
- **Strong Typing**: Comprehensive type annotations
- **Forward References**: Quoted string references for circular imports

## Import Hierarchy
```
Level 1: types/*_types.py          # Base type definitions
Level 2: protocols/*/protocol_*.py  # Protocol definitions using types
Level 3: protocols/__init__.py      # Package-level exports
Level 4: External packages          # Import protocols (not implementations)
```

## Testing Structure
```
tests/
├── __init__.py
└── test_protocol_imports.py        # Namespace isolation validation
```

## Validation Scripts
```
scripts/
├── validate-namespace-isolation.sh  # Check imports and naming
└── validate-spi-purity.sh          # Validate pure protocol design
```
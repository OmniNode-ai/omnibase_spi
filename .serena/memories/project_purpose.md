# Project Purpose: omnibase-spi

## Overview
omnibase-spi is a **Service Provider Interface (SPI) package** that provides protocol-based typing for the ONEX ecosystem. It serves as the foundation for type safety and architectural contracts across all ONEX components.

## Key Characteristics
- **Zero Implementation Dependencies**: Contains only pure Python protocols with no concrete implementations
- **Namespace Isolation**: Complete separation from omnibase-core to prevent circular dependencies
- **Protocol-First Design**: All services defined through Python typing protocols
- **Strong Type Safety**: No `Any` types, comprehensive typing throughout
- **Semantic Versioning**: Uses ProtocolSemVer for version management

## Architecture Role
- **Contract Definition**: Defines interfaces that other ONEX components implement
- **Type Safety**: Enables duck typing and dependency injection without requiring implementations
- **Domain Organization**: Protocols organized by functional domain (core, event_bus, container, etc.)
- **Forward References**: Uses TYPE_CHECKING imports to avoid circular dependencies

## Target Users
- ONEX ecosystem developers who need protocol contracts
- Service implementers who need interface definitions
- Framework users requiring type-safe dependency injection
- Protocol designers extending ONEX functionality

## Package Structure
- `src/omnibase/protocols/core/`: Core system protocols (logging, serialization, validation)  
- `src/omnibase/protocols/event_bus/`: Event-driven architecture contracts
- `src/omnibase/protocols/container/`: Dependency injection protocols
- `src/omnibase/protocols/discovery/`: Service discovery contracts
- `src/omnibase/protocols/file_handling/`: File processing protocols
- `src/omnibase/protocols/types/`: Type definitions and protocol types

## Version and Compatibility  
- Current Version: 0.0.2
- Python Support: 3.11-3.13
- Dependencies: Only `typing-extensions` and `pydantic` for runtime
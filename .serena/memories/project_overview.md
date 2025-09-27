# ONEX Service Provider Interface (omnibase-spi) - Project Overview

## Project Purpose
This repository contains pure protocol interfaces for the ONEX framework with zero implementation dependencies. It serves as the foundational contract layer that enables duck typing and dependency injection without requiring concrete implementations.

## Core Mission
- **Zero Dependencies**: No implementation dependencies, only typing imports
- **Protocol-First Design**: All services defined through Python protocols
- **Domain Organization**: Protocols organized by functional domain
- **Forward References**: Uses `TYPE_CHECKING` imports to avoid circular dependencies

## Key Architectural Principles
1. **Complete Namespace Isolation**: Only `omnibase_spi.protocols.*` imports allowed
2. **SPI Purity**: No concrete implementations, only pure protocol definitions
3. **Strong Typing**: Minimal use of `Any` types, comprehensive type hints
4. **Protocol Contracts**: All service interfaces defined as Protocol classes
5. **Domain-Driven Organization**: Protocols grouped by functional domains

## Technology Stack
- **Language**: Python 3.12+
- **Build System**: Poetry for dependency management
- **Type Checking**: mypy with strict settings
- **Code Quality**: Black (formatting), isort (import sorting), Ruff (linting)
- **Testing**: pytest for validation tests
- **CI/CD**: GitHub Actions for automated validation

## Repository Structure
```
src/omnibase/protocols/
├── core/                    # Core system protocols
├── event_bus/              # Event system protocols
├── container/              # Dependency injection protocols
├── discovery/              # Service discovery protocols
├── file_handling/          # File processing protocols
├── types/                  # Type definitions and aliases
└── validation/             # Validation framework protocols
```

## Development Environment
- **Python Version**: 3.12+
- **Package Manager**: Poetry
- **Virtual Environment**: Managed by Poetry
- **Pre-commit Hooks**: Automated code quality checks
- **Validation**: Multiple layers of SPI purity enforcement

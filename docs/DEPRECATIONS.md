# Deprecations

![Version](https://img.shields.io/badge/SPI-v0.3.0-blue) ![Status](https://img.shields.io/badge/status-maintained-green)

> **SPI Version**: 0.3.0 | **Last Updated**: 2025-12-07

This document tracks all deprecated APIs, protocols, and modules in the ONEX Service Provider Interface (SPI). Use this guide to plan migrations and ensure compatibility with future releases.

---

## Table of Contents

- [Current Deprecations](#current-deprecations)
  - [ProtocolHandlerV3 Alias](#protocolhandlerv3-alias)
  - [Legacy Node Protocols](#legacy-node-protocols)
  - [Kafka Protocol Renames](#kafka-protocol-renames)
- [Deprecation Policy](#deprecation-policy)
- [Version Timeline](#version-timeline)
- [Migration Checklist](#migration-checklist)
- [See Also](#see-also)

---

## Current Deprecations

The following items are deprecated and scheduled for removal. Each entry includes the deprecation version, target removal version, and migration path.

### Summary Table

| Deprecated Item | Deprecated In | Removal Target | Replacement | Status |
|-----------------|---------------|----------------|-------------|--------|
| `ProtocolHandlerV3` | v0.3.0 | v0.5.0 | `ProtocolHandler` | Active alias |
| `ProtocolComputeNodeLegacy` | v0.3.0 | v0.5.0 | `ProtocolComputeNode` | Emits warning |
| `ProtocolEffectNodeLegacy` | v0.3.0 | v0.5.0 | `ProtocolEffectNode` | Emits warning |
| `ProtocolReducerNodeLegacy` | v0.3.0 | v0.5.0 | `ProtocolReducerNode` | Emits warning |
| `ProtocolOrchestratorNodeLegacy` | v0.3.0 | v0.5.0 | `ProtocolOrchestratorNode` | Emits warning |
| `ProtocolKafkaClient` | v0.3.0 | v0.5.0 | `ProtocolEventBusClient` | Active alias |
| `ProtocolKafkaClientProvider` | v0.3.0 | v0.5.0 | `ProtocolEventBusClientProvider` | Active alias |
| `ProtocolKafkaMessage` | v0.3.0 | v0.5.0 | `ProtocolEventBusMessage` | Active alias |
| `ProtocolKafkaConsumer` | v0.3.0 | v0.5.0 | `ProtocolEventBusConsumer` | Active alias |
| `ProtocolKafkaBatchProducer` | v0.3.0 | v0.5.0 | `ProtocolEventBusBatchProducer` | Active alias |
| `ProtocolKafkaTransactionalProducer` | v0.3.0 | v0.5.0 | `ProtocolEventBusTransactionalProducer` | Active alias |
| `ProtocolKafkaExtendedClient` | v0.3.0 | v0.5.0 | `ProtocolEventBusExtendedClient` | Active alias |
| `ProtocolKafkaClientConfig` | v0.3.0 | v0.5.0 | `ProtocolEventBusClientConfig` | Active alias |
| `ProtocolKafkaProducerConfig` | v0.3.0 | v0.5.0 | `ProtocolEventBusProducerConfig` | Active alias |
| `ProtocolKafkaConsumerConfig` | v0.3.0 | v0.5.0 | `ProtocolEventBusConsumerConfig` | Active alias |

---

### ProtocolHandlerV3 Alias

**Location**: `omnibase_spi.protocols`

**Deprecated In**: v0.3.0

**Removal Target**: v0.5.0

**Status**: Active alias (no warning emitted)

#### Description

`ProtocolHandlerV3` was the versioned name during the protocol evolution from v0.1.x through v0.2.x. As of v0.3.0, `ProtocolHandler` is the canonical name. The `ProtocolHandlerV3` alias is provided for backwards compatibility but will be removed in v0.5.0.

The protocols are identical - no code changes are needed beyond updating the import statement.

#### Migration Path

```python
# Old (deprecated)
from omnibase_spi.protocols import ProtocolHandlerV3

class MyHandler:
    """Implementation using deprecated import."""
    ...

# New (recommended)
from omnibase_spi.protocols import ProtocolHandler

class MyHandler:
    """Implementation using canonical import."""
    ...
```

#### Notes

- The alias does not emit a deprecation warning at runtime
- Both imports point to the identical protocol definition
- Update imports before upgrading to v0.5.0

**See**: [HANDLERS.md - Migration Note](./api-reference/HANDLERS.md#migration-note)

---

### Legacy Node Protocols

**Location**: `omnibase_spi.protocols.nodes.legacy`

**Deprecated In**: v0.3.0

**Removal Target**: v0.5.0

**Status**: Emits `DeprecationWarning` on import

#### Description

The legacy node protocols module contains older interface definitions that predate the standardized 4-node architecture. These protocols have been superseded by the canonical node protocols in `omnibase_spi.protocols.nodes`.

The legacy module emits a `DeprecationWarning` when imported:

```
DeprecationWarning: The omnibase_spi.protocols.nodes.legacy module is deprecated.
Use omnibase_spi.protocols.nodes for standard interfaces.
Legacy interfaces will be removed in v0.5.0.
```

#### Deprecated Protocols

| Legacy Protocol | Replacement |
|-----------------|-------------|
| `ProtocolComputeNodeLegacy` | `ProtocolComputeNode` |
| `ProtocolEffectNodeLegacy` | `ProtocolEffectNode` |
| `ProtocolReducerNodeLegacy` | `ProtocolReducerNode` |
| `ProtocolOrchestratorNodeLegacy` | `ProtocolOrchestratorNode` |

#### Migration Path

```python
# Old (deprecated) - emits DeprecationWarning
from omnibase_spi.protocols.nodes.legacy import (
    ProtocolComputeNodeLegacy,
    ProtocolEffectNodeLegacy,
    ProtocolReducerNodeLegacy,
    ProtocolOrchestratorNodeLegacy,
)

# New (recommended)
from omnibase_spi.protocols.nodes import (
    ProtocolComputeNode,
    ProtocolEffectNode,
    ProtocolReducerNode,
    ProtocolOrchestratorNode,
)
```

#### Interface Differences

The canonical node protocols have the following improvements over legacy:

1. **Standardized Properties**: Consistent `node_id`, `node_type`, and `version` properties across all node types
2. **Type-Safe Models**: Use `omnibase_core` models (`ModelComputeInput`, `ModelEffectOutput`, etc.) instead of generic dictionaries
3. **Lifecycle Management**: Effect nodes have explicit `initialize()` and `shutdown()` methods with timeout parameters
4. **Runtime Checkability**: All protocols are decorated with `@runtime_checkable`

#### Notes

- Legacy protocols will be completely removed in v0.5.0
- The `legacy/` directory and all its contents will be deleted
- Run tests with warnings enabled to identify legacy usage: `pytest -W default::DeprecationWarning`

**See**: [NODES.md](./api-reference/NODES.md)

---

### Kafka Protocol Renames

**Location**: `omnibase_spi.protocols.event_bus`, `omnibase_spi.protocols.container`

**Deprecated In**: v0.3.0

**Removal Target**: v0.5.0

**Status**: Active aliases (no warning emitted)

#### Description

The following protocols have been renamed to use backend-agnostic "EventBus" naming instead of Kafka-specific naming. The SPI defines abstract interfaces; Kafka-specific implementations belong in `omnibase_infra`.

This rename aligns with the SPI's role as a backend-agnostic interface layer. The protocols define event bus operations that could be implemented with Kafka, RabbitMQ, Redis Streams, or other message brokers.

#### Deprecated Protocols

| Deprecated Name | New Name | Module |
|-----------------|----------|--------|
| `ProtocolKafkaClient` | `ProtocolEventBusClient` | `event_bus` |
| `ProtocolKafkaClientProvider` | `ProtocolEventBusClientProvider` | `event_bus` |
| `ProtocolKafkaMessage` | `ProtocolEventBusMessage` | `event_bus` |
| `ProtocolKafkaConsumer` | `ProtocolEventBusConsumer` | `event_bus` |
| `ProtocolKafkaBatchProducer` | `ProtocolEventBusBatchProducer` | `event_bus` |
| `ProtocolKafkaTransactionalProducer` | `ProtocolEventBusTransactionalProducer` | `event_bus` |
| `ProtocolKafkaExtendedClient` | `ProtocolEventBusExtendedClient` | `event_bus` |
| `ProtocolKafkaClientConfig` | `ProtocolEventBusClientConfig` | `container` |
| `ProtocolKafkaProducerConfig` | `ProtocolEventBusProducerConfig` | `container` |
| `ProtocolKafkaConsumerConfig` | `ProtocolEventBusConsumerConfig` | `container` |

#### Migration Path

```python
# Old (deprecated)
from omnibase_spi.protocols.networking import ProtocolKafkaClient
from omnibase_spi.protocols.container import ProtocolKafkaClientConfig

# New (recommended)
from omnibase_spi.protocols.event_bus import ProtocolEventBusClient
from omnibase_spi.protocols.container import ProtocolEventBusClientConfig
```

#### Protocols Retained (NOT Deprecated)

The following Kafka-specific adapter protocols are **NOT** deprecated. They are intentionally Kafka-specific as they represent adapter implementations rather than abstract interfaces:

- `ProtocolKafkaConfig` - Kafka-specific adapter configuration
- `ProtocolKafkaAdapter` - Kafka-specific adapter implementation
- `ProtocolKafkaHealthCheckResult` - Kafka-specific health check result
- `ProtocolKafkaEventBusInputState` - Kafka-specific validation input state
- `ProtocolKafkaEventBusOutputState` - Kafka-specific validation output state

#### Notes

- The aliases do not emit deprecation warnings at runtime
- Both old and new imports point to identical protocol definitions
- Update imports before upgrading to v0.5.0
- Kafka-specific adapter protocols remain in `omnibase_spi.protocols.adapters`

**See**: [EVENT_BUS.md](./api-reference/EVENT_BUS.md)

---

## Deprecation Policy

The ONEX SPI follows a structured deprecation policy to ensure smooth migrations:

### Timeline

1. **Deprecation Announcement**: Feature is marked as deprecated in release notes and documentation
2. **Warning Period**: Deprecated features emit warnings (where applicable) for at least one minor version
3. **Removal**: Feature is removed in a subsequent minor or major version

### Versioning Rules

| Change Type | Version Bump | Deprecation Period |
|-------------|--------------|-------------------|
| Protocol removal | Minor (0.x.0) | 2 minor versions minimum |
| Protocol signature change | Minor (0.x.0) | 1 minor version minimum |
| Module reorganization | Patch (0.0.x) | Immediate alias support |

### Compatibility Guarantees

- **Patch versions** (0.3.x): No breaking changes, bug fixes only
- **Minor versions** (0.x.0): May remove previously deprecated features, add new deprecations
- **Major versions** (x.0.0): May introduce breaking changes without prior deprecation

### Finding Deprecations in Code

Deprecated items are marked with:

1. **Docstring warnings**: `DEPRECATED:` prefix in docstrings
2. **Code comments**: `# DEPRECATED:` comments above declarations
3. **Runtime warnings**: `warnings.warn()` calls with `DeprecationWarning`
4. **Type aliases**: Deprecated names aliased to canonical names

Example from source:

```python
# DEPRECATED: ProtocolHandlerV3 will be removed in v0.5.0.
# Use ProtocolHandler instead.
ProtocolHandlerV3 = ProtocolHandler
```

---

## Version Timeline

This timeline shows the deprecation and removal schedule for current and planned changes:

```text
v0.3.0 (Current)
  |
  +-- ProtocolHandlerV3 deprecated (alias to ProtocolHandler)
  +-- Legacy node protocols deprecated (emits warnings)
  +-- Kafka protocols renamed to EventBus (aliases provided)
  |
  v
v0.4.0 (Planned)
  |
  +-- Final warning period for v0.3.0 deprecations
  +-- New deprecations may be introduced
  |
  v
v0.5.0 (Planned)
  |
  +-- REMOVAL: ProtocolHandlerV3 alias
  +-- REMOVAL: omnibase_spi.protocols.nodes.legacy module
  +-- REMOVAL: ProtocolKafka* aliases (use ProtocolEventBus* equivalents)
  +-- Breaking changes require code updates
```

### Version Milestones

| Version | Release | Key Changes |
|---------|---------|-------------|
| v0.3.0 | 2025-12-04 | Current release, deprecations announced |
| v0.4.0 | TBD | Continued deprecation warnings |
| v0.5.0 | TBD | Deprecated items removed |

---

## Migration Checklist

Use this checklist to ensure your codebase is ready for future SPI versions:

### Before v0.5.0

- [ ] Replace all `ProtocolHandlerV3` imports with `ProtocolHandler`
- [ ] Replace all imports from `omnibase_spi.protocols.nodes.legacy` with `omnibase_spi.protocols.nodes`
- [ ] Update implementations to use canonical node protocols
- [ ] Replace all `ProtocolKafka*` imports with `ProtocolEventBus*` equivalents
- [ ] Update imports from `omnibase_spi.protocols.networking` to `omnibase_spi.protocols.event_bus`
- [ ] Run tests with deprecation warnings enabled
- [ ] Review CI/CD pipelines for deprecated imports

### Automated Detection

Run the following commands to find deprecated usage:

```bash
# Find ProtocolHandlerV3 usage
grep -r "ProtocolHandlerV3" src/ tests/

# Find legacy node imports
grep -r "from omnibase_spi.protocols.nodes.legacy" src/ tests/
grep -r "from omnibase_spi.protocols.nodes import.*Legacy" src/ tests/

# Find deprecated Kafka protocol imports
grep -r "ProtocolKafkaClient\b" src/ tests/
grep -r "ProtocolKafkaClientProvider" src/ tests/
grep -r "ProtocolKafkaMessage\b" src/ tests/
grep -r "ProtocolKafkaConsumer\b" src/ tests/
grep -r "ProtocolKafkaBatchProducer" src/ tests/
grep -r "ProtocolKafkaTransactionalProducer" src/ tests/
grep -r "ProtocolKafkaExtendedClient" src/ tests/
grep -r "ProtocolKafkaClientConfig" src/ tests/
grep -r "ProtocolKafkaProducerConfig" src/ tests/
grep -r "ProtocolKafkaConsumerConfig" src/ tests/

# Run tests with warnings as errors (strict mode)
pytest -W error::DeprecationWarning tests/
```

---

## See Also

- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes
- **[HANDLERS.md](./api-reference/HANDLERS.md)** - ProtocolHandler documentation and migration notes
- **[NODES.md](./api-reference/NODES.md)** - Canonical node protocol documentation
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Development workflow and guidelines
- **[GLOSSARY.md](./GLOSSARY.md)** - Terminology definitions
- **[README.md](./README.md)** - Documentation hub

---

*This deprecation guide is maintained as part of the omnibase_spi documentation. For questions about migrations, please open an issue on GitHub.*

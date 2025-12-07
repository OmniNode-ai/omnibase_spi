# Deprecations

![Version](https://img.shields.io/badge/SPI-v0.3.0-blue) ![Status](https://img.shields.io/badge/status-maintained-green)

> **SPI Version**: 0.3.0 | **Last Updated**: 2025-12-07

This document tracks deprecated APIs, protocols, and modules in the ONEX Service Provider Interface (SPI), including items that have been removed.

---

## Table of Contents

- [Removed Deprecations](#removed-deprecations)
  - [ProtocolHandlerV3 Alias](#protocolhandlerv3-alias)
  - [Legacy Node Protocols](#legacy-node-protocols)
  - [Kafka Protocol Aliases](#kafka-protocol-aliases)
- [Deprecation Policy](#deprecation-policy)
- [Version History](#version-history)
- [See Also](#see-also)

---

## Removed Deprecations

The following items were deprecated in v0.3.0 and **removed immediately** in the same release. These were removed ahead of the originally planned v0.5.0 removal because there are **no downstream consumers** of the SPI at this time.

> **Note**: Early removal was performed to maintain a clean codebase during initial development. The SPI is pre-1.0 and does not yet have external consumers that would be affected by breaking changes.

### Summary Table

| Removed Item | Introduced | Removed | Replacement | Status |
|--------------|------------|---------|-------------|--------|
| `ProtocolHandlerV3` | v0.3.0 | v0.3.0 | `ProtocolHandler` | **Removed** |
| `ProtocolComputeNodeLegacy` | v0.3.0 | v0.3.0 | `ProtocolComputeNode` | **Removed** |
| `ProtocolEffectNodeLegacy` | v0.3.0 | v0.3.0 | `ProtocolEffectNode` | **Removed** |
| `ProtocolReducerNodeLegacy` | v0.3.0 | v0.3.0 | `ProtocolReducerNode` | **Removed** |
| `ProtocolOrchestratorNodeLegacy` | v0.3.0 | v0.3.0 | `ProtocolOrchestratorNode` | **Removed** |
| `ProtocolKafkaClient` | v0.3.0 | v0.3.0 | `ProtocolEventBusClient` | **Removed** |
| `ProtocolKafkaClientProvider` | v0.3.0 | v0.3.0 | `ProtocolEventBusClientProvider` | **Removed** |
| `ProtocolKafkaMessage` | v0.3.0 | v0.3.0 | `ProtocolEventBusMessage` | **Removed** |
| `ProtocolKafkaConsumer` | v0.3.0 | v0.3.0 | `ProtocolEventBusConsumer` | **Removed** |
| `ProtocolKafkaBatchProducer` | v0.3.0 | v0.3.0 | `ProtocolEventBusBatchProducer` | **Removed** |
| `ProtocolKafkaTransactionalProducer` | v0.3.0 | v0.3.0 | `ProtocolEventBusTransactionalProducer` | **Removed** |
| `ProtocolKafkaExtendedClient` | v0.3.0 | v0.3.0 | `ProtocolEventBusExtendedClient` | **Removed** |
| `ProtocolKafkaClientConfig` | v0.3.0 | v0.3.0 | `ProtocolEventBusClientConfig` | **Removed** |
| `ProtocolKafkaProducerConfig` | v0.3.0 | v0.3.0 | `ProtocolEventBusProducerConfig` | **Removed** |
| `ProtocolKafkaConsumerConfig` | v0.3.0 | v0.3.0 | `ProtocolEventBusConsumerConfig` | **Removed** |

---

### ProtocolHandlerV3 Alias

**Status**: **REMOVED** in v0.3.0

#### Description

`ProtocolHandlerV3` was a versioned alias that existed briefly during the protocol evolution. It was removed in favor of the canonical `ProtocolHandler` name.

#### Current Usage

Use `ProtocolHandler` directly:

```python
from omnibase_spi.protocols import ProtocolHandler

class MyHandler:
    """Implementation using canonical import."""
    ...
```

**See**: [HANDLERS.md](./api-reference/HANDLERS.md)

---

### Legacy Node Protocols

**Status**: **REMOVED** in v0.3.0

**Removed Directory**: `omnibase_spi/protocols/nodes/legacy/`

#### Description

The entire `legacy/` directory under `omnibase_spi/protocols/nodes/` has been deleted. This directory contained older interface definitions that predated the standardized 4-node architecture.

#### Removed Protocols

| Removed Protocol | Replacement |
|------------------|-------------|
| `ProtocolComputeNodeLegacy` | `ProtocolComputeNode` |
| `ProtocolEffectNodeLegacy` | `ProtocolEffectNode` |
| `ProtocolReducerNodeLegacy` | `ProtocolReducerNode` |
| `ProtocolOrchestratorNodeLegacy` | `ProtocolOrchestratorNode` |

#### Current Usage

Use the canonical node protocols:

```python
from omnibase_spi.protocols.nodes import (
    ProtocolComputeNode,
    ProtocolEffectNode,
    ProtocolReducerNode,
    ProtocolOrchestratorNode,
)
```

#### Canonical Node Protocol Features

The canonical node protocols provide:

1. **Standardized Properties**: Consistent `node_id`, `node_type`, and `version` properties across all node types
2. **Type-Safe Models**: Use `omnibase_core` models (`ModelComputeInput`, `ModelEffectOutput`, etc.)
3. **Lifecycle Management**: Effect nodes have explicit `initialize()` and `shutdown()` methods
4. **Runtime Checkability**: All protocols are decorated with `@runtime_checkable`

**See**: [NODES.md](./api-reference/NODES.md)

---

### Kafka Protocol Aliases

**Status**: **REMOVED** in v0.3.0

#### Description

The Kafka-specific protocol aliases were removed to enforce the backend-agnostic "EventBus" naming convention. The SPI defines abstract interfaces; Kafka-specific implementations belong in `omnibase_infra`.

This rename aligns with the SPI's role as a backend-agnostic interface layer. The protocols define event bus operations that could be implemented with Kafka, RabbitMQ, Redis Streams, or other message brokers.

#### Removed Aliases

| Removed Name | Replacement | Module |
|--------------|-------------|--------|
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

#### Current Usage

Use the EventBus protocols:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusClient
from omnibase_spi.protocols.container import ProtocolEventBusClientConfig
```

#### Kafka-Specific Adapter Protocols (NOT Removed)

The following Kafka-specific adapter protocols remain in the codebase. They are intentionally Kafka-specific as they represent adapter implementations rather than abstract interfaces:

- `ProtocolKafkaConfig` - Kafka-specific adapter configuration
- `ProtocolKafkaAdapter` - Kafka-specific adapter implementation
- `ProtocolKafkaHealthCheckResult` - Kafka-specific health check result
- `ProtocolKafkaEventBusInputState` - Kafka-specific validation input state
- `ProtocolKafkaEventBusOutputState` - Kafka-specific validation output state

These protocols live in `omnibase_spi.protocols.adapters` and will remain as they define adapter-specific contracts.

**See**: [EVENT_BUS.md](./api-reference/EVENT_BUS.md)

---

## Deprecation Policy

The ONEX SPI follows a structured deprecation policy to ensure smooth migrations:

### Timeline

1. **Deprecation Announcement**: Feature is marked as deprecated in release notes and documentation
2. **Warning Period**: Deprecated features emit warnings (where applicable) for at least one minor version
3. **Removal**: Feature is removed in a subsequent minor or major version

> **Pre-1.0 Exception**: During pre-1.0 development, deprecated items may be removed immediately if there are no downstream consumers.

### Versioning Rules

| Change Type | Version Bump | Deprecation Period |
|-------------|--------------|-------------------|
| Protocol removal | Minor (0.x.0) | 2 minor versions (post-1.0) |
| Protocol signature change | Minor (0.x.0) | 1 minor version (post-1.0) |
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
4. **This document**: Central tracking of all deprecations

---

## Version History

This timeline shows the deprecation and removal history:

```text
v0.3.0 (Current - 2025-12-07)
  |
  +-- ProtocolHandlerV3 alias INTRODUCED and REMOVED
  +-- Legacy node protocols INTRODUCED and REMOVED
  +-- Kafka protocol aliases INTRODUCED and REMOVED
  +-- Early removal due to no downstream consumers
  |
  v
v0.4.0+ (Future)
  |
  +-- Standard deprecation policy resumes
  +-- Full deprecation cycles for any new deprecations
```

### Version Milestones

| Version | Release | Key Changes |
|---------|---------|-------------|
| v0.3.0 | 2025-12-07 | Deprecated items removed (no consumers) |
| v1.0.0 | TBD | Stable API, full deprecation policy enforced |

---

## See Also

- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes
- **[HANDLERS.md](./api-reference/HANDLERS.md)** - ProtocolHandler documentation
- **[NODES.md](./api-reference/NODES.md)** - Canonical node protocol documentation
- **[EVENT_BUS.md](./api-reference/EVENT_BUS.md)** - EventBus protocol documentation
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Development workflow and guidelines
- **[GLOSSARY.md](./GLOSSARY.md)** - Terminology definitions
- **[README.md](./README.md)** - Documentation hub

---

*This deprecation guide is maintained as part of the omnibase_spi documentation. For questions about migrations, please open an issue on GitHub.*

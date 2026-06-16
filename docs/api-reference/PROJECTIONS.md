# Projections API Reference

![Version](https://img.shields.io/badge/SPI-v0.22.0-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.22.0-lightgrey)

> **Package Version**: 0.22.0 | **Status**: Stable | **Since**: v0.22.0 (OMN-12190, migrated from omnibase_compat)

---

## Overview

The ONEX projections domain defines protocols for the projection layer: persistence, reading, and view dispatch. Projections are materialized views of event streams that provide consistent, queryable state for orchestrators.

**Critical architectural constraint:** Orchestrators MUST NEVER scan Kafka/event topics directly for state. All orchestration decisions MUST be projection-backed through these protocols.

## Import Path

```python
from omnibase_spi.protocols.projections import (
    ProtocolProjector,
    ProtocolProjectionReader,
    ProtocolProjectionDatabase,
    ProtocolProjectionDatabaseSync,
    ProtocolProjectionView,
    ProtocolSequenceInfo,
    ProtocolPersistResult,
    ProtocolBatchPersistResult,
)
```

## Architecture

Projections flow from reducers through the projector to persistence, and are later queried by orchestrators through the projection reader:

```text
Reducer -> Runtime -> Projector -> Database <- ProjectionReader <- Orchestrator
```

The `NodeProjectionEffect` registry pattern:

```text
Reducer -> ModelProjectionIntent -> NodeProjectionEffect
        -> ProtocolProjectionView.project_intent() -> ContractProjectionResult
```

## Protocol Distinctions

| Protocol | Sync/Async | Input | Use Case |
|----------|------------|-------|----------|
| `ProtocolProjector` | Async | `(projection, entity_id, domain, sequence_info)` | Persistence with sequence ordering |
| `ProtocolProjectionView` | Sync | `ModelProjectionIntent` | NodeProjectionEffect registry dispatch |
| `ProtocolProjectionReader` | Async | `(entity_id, domain, ...)` | Orchestrator projection queries |
| `ProtocolProjectionDatabase` | Async | Raw SQL + params | Database adapter (AsyncpgAdapter) |
| `ProtocolProjectionDatabaseSync` | Sync | Raw SQL + params | Synchronous database adapter |

---

## ProtocolProjector

Persists projections with ordering and idempotency guarantees. Enforces per-entity monotonic ordering by tracking the last applied sequence for each `(entity_id, domain)` pair.

```python
from omnibase_spi.protocols.projections import ProtocolProjector

@runtime_checkable
class ProtocolProjector(Protocol):

    async def persist(
        self,
        projection: object,
        entity_id: str,
        domain: str,
        sequence_info: ProtocolSequenceInfo,
        *,
        correlation_id: str | None = None,
    ) -> ProtocolPersistResult: ...

    async def batch_persist(
        self,
        projections: Sequence[tuple[object, str, str, ProtocolSequenceInfo]],
        *,
        correlation_id: str | None = None,
    ) -> ProtocolBatchPersistResult: ...

    async def get_last_sequence(
        self,
        entity_id: str,
        domain: str,
    ) -> ProtocolSequenceInfo | None: ...

    async def is_stale(
        self,
        entity_id: str,
        domain: str,
        sequence_info: ProtocolSequenceInfo,
    ) -> bool: ...

    async def cleanup_before_sequence(
        self,
        domain: str,
        sequence: int,
        *,
        batch_size: int = 1000,
        confirmed: bool = False,
    ) -> int: ...
```

### Ordering Semantics

Given `last_applied_sequence L` for `(entity_id, domain)`:
- If `sequence_info.sequence > L`: persist and update L
- If `sequence_info.sequence <= L`: return `rejected_stale`

### Usage

```python
from omnibase_spi.protocols.projections import ProtocolProjector, ProtocolSequenceInfo

projector: ProtocolProjector = get_projector()

result = await projector.persist(
    projection={"order_id": "123", "status": "shipped"},
    entity_id="order-123",
    domain="orders",
    sequence_info=seq_info,
    correlation_id="corr-456",
)

if result.status == "applied":
    print(f"Persisted at sequence {result.applied_sequence}")
elif result.status == "rejected_stale":
    print(f"Stale: {result.rejected_reason}")
```

---

## ProtocolSequenceInfo

Carries ordering information for projection persistence.

```python
@runtime_checkable
class ProtocolSequenceInfo(Protocol):

    @property
    def sequence(self) -> int: ...  # Monotonically increasing sequence number

    @property
    def partition(self) -> str | None: ...  # Optional partition identifier
```

---

## ProtocolPersistResult and ProtocolBatchPersistResult

Result types returned by `ProtocolProjector.persist()` and `batch_persist()`.

```python
@runtime_checkable
class ProtocolPersistResult(Protocol):

    @property
    def status(self) -> Literal["applied", "rejected_stale", "rejected_conflict"]: ...

    @property
    def entity_id(self) -> str: ...

    @property
    def applied_sequence(self) -> int | None: ...

    @property
    def rejected_reason(self) -> str | None: ...


@runtime_checkable
class ProtocolBatchPersistResult(Protocol):

    @property
    def total_count(self) -> int: ...

    @property
    def applied_count(self) -> int: ...

    @property
    def rejected_count(self) -> int: ...

    @property
    def results(self) -> Sequence[ProtocolPersistResult]: ...
```

---

## ProtocolProjectionReader

Queries materialized projection state. Used exclusively by orchestrators — never by event producers or reducers.

```python
from omnibase_spi.protocols.projections import ProtocolProjectionReader

projector_reader: ProtocolProjectionReader = get_projection_reader()
state = await projector_reader.get_projection(entity_id="order-123", domain="orders")
```

---

## ProtocolProjectionView

Simplified synchronous protocol consumed by `NodeProjectionEffect`. Implements the registry-based dispatch pattern: a single generic `NodeProjectionEffect` replaces "one custom effect node per projection type."

```python
from omnibase_spi.protocols.projections import ProtocolProjectionView

@runtime_checkable
class ProtocolProjectionView(Protocol):
    def project_intent(self, intent: ModelProjectionIntent) -> ContractProjectionResult: ...
```

---

## ProtocolProjectionDatabase and ProtocolProjectionDatabaseSync

Low-level database adapter protocols used by projector implementations. These sit below `ProtocolProjector` in the stack — application code should depend on `ProtocolProjector`, not on the database adapters directly.

```python
from omnibase_spi.protocols.projections import ProtocolProjectionDatabase

@runtime_checkable
class ProtocolProjectionDatabase(Protocol):
    async def execute(self, query: str, *params: Any) -> list[dict[str, Any]]: ...
    async def execute_many(self, query: str, params_list: list[tuple[Any, ...]]) -> None: ...
    async def fetchval(self, query: str, *params: Any) -> Any: ...
    async def close(self) -> None: ...
```

`ProtocolProjectionDatabaseSync` provides the same interface with synchronous methods.

---

## Idempotency Layers

The ONEX platform uses two complementary idempotency mechanisms:

| Layer | Protocol | Key | Scope |
|-------|----------|-----|-------|
| Runtime idempotency (B3) | `ProtocolIdempotencyStore` | `message_id` | Prevents duplicate handler execution |
| Projector idempotency (F0) | `ProtocolProjector` | `(entity_id, domain, sequence)` | Ensures monotonic entity state |

Together these layers ensure each message is processed exactly once and each entity's projections are applied in order.

---

## See Also

- **[NODES.md](./NODES.md)** - Reducer nodes produce the projections persisted here
- **[WORKFLOW-ORCHESTRATION.md](./WORKFLOW-ORCHESTRATION.md)** - Orchestrators read projections to make decisions
- **[EVENT-BUS.md](./EVENT-BUS.md)** - Events that drive reducer -> projector flow
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference documents the projections protocols added in OMN-12190 (v0.22.0). Concrete implementations (PostgresProjector, ValkeyProjector) live in `omnibase_infra`.*

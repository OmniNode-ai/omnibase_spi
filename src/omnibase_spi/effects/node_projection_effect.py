"""ProtocolNodeProjectionEffect -- synchronous ProtocolEffect for projection writes.

Defines the ``ProtocolNodeProjectionEffect`` protocol: the SPI contract
that the runtime calls to write a projection to the persistence layer
**before** publishing the corresponding event to Kafka.

Phase 2 of OMN-2363.  The ordering guarantee that eliminates the race
condition between projection persistence and Kafka publish is enforced
by making ``execute()`` synchronous: the caller blocks until the write
is committed.

Architecture Context::

    Reducer Output
         │
         ▼
    [runtime] calls ProtocolNodeProjectionEffect.execute(intent)
         │ [SYNCHRONOUS — blocks until write commits]
         ▼
    Persistence Layer (Postgres / Valkey / …)
         │ write committed
         ▼
    returns ContractProjectionResult(success=True, artifact_ref=…)
         │
         ▼
    [runtime] publishes to Kafka

Critical Constraint:
    ``execute()`` MUST be synchronous — no ``async def``.  If the
    underlying storage layer requires async I/O, implementations bridge
    via ``asyncio.run()`` inside ``execute()``.  The async context MUST NOT
    leak to the caller.

Related:
    - OMN-2508: This ticket.
    - OMN-2460: ModelProjectionIntent (input model consumed by execute()).
    - OMN-2461: Generic ProtocolProjector SPI (abstract machinery this sits on).
    - omnibase_spi.contracts.projections.ContractProjectionResult: return value.
    - omnibase_spi.protocols.effects.ProtocolEffect: base protocol.
    - omnibase_spi.exceptions.ProjectorError: raised on failure.
"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from omnibase_spi.contracts.projections.contract_projection_result import (
    ContractProjectionResult,
)
from omnibase_spi.protocols.effects.protocol_effect import ProtocolEffect


@runtime_checkable
class ProtocolNodeProjectionEffect(ProtocolEffect, Protocol):
    """Synchronous projection write effect node.

    ``ProtocolNodeProjectionEffect`` is the SPI contract for the effect node
    responsible for persisting reducer-produced projections to the
    persistence layer.

    The ONEX runtime invokes ``execute(intent)`` after a reducer node
    completes and before publishing the corresponding event to Kafka.
    Because ``execute()`` is synchronous, the runtime has a blocking
    guarantee: the projection is on disk (or equivalent durable storage)
    before any Kafka message is emitted.

    Synchronous Contract:
        ``execute()`` MUST complete the full projection write before
        returning.  Implementations that use async storage backends MUST
        bridge the async gap inside ``execute()`` using ``asyncio.run()``
        or an equivalent mechanism.  The signature MUST remain synchronous:

        .. code-block:: python

            # Using asyncio.run() — only safe when the caller is NOT inside a running event loop.
            # In async contexts (FastAPI, pytest-asyncio, Jupyter), use anyio.from_thread.run_sync
            # instead. See the Note section in protocol_effect.py for full guidance.
            def execute(self, intent: ModelProjectionIntent) -> ContractProjectionResult:
                return asyncio.run(self._async_write(intent))

            # WRONG — leaks async boundary to caller
            async def execute(self, intent):  # noqa: this is forbidden
                ...

    Error Handling:
        ``execute()`` MUST raise on failure.  Silently returning
        ``success=False`` for infrastructure errors would defeat the
        ordering guarantee because the runtime would proceed to publish
        even though no projection was persisted.

        Acceptable use of ``success=False``:
        - Duplicate / already-applied sequence (idempotent skip).
        - Non-fatal no-op writes the implementation chooses not to surface
          as exceptions.

    isinstance Compliance:
        This protocol is ``@runtime_checkable``.  Concrete implementations
        are checked at DI container registration time:

        .. code-block:: python

            assert isinstance(impl, ProtocolNodeProjectionEffect)

    Example Implementation::

        from omnibase_spi.effects import ProtocolNodeProjectionEffect
        from omnibase_spi.contracts.projections import ContractProjectionResult

        class PostgresProjectionEffect:
            def __init__(self, db_pool: Pool) -> None:
                self._pool = db_pool

            def execute(
                self, intent: ModelProjectionIntent
            ) -> ContractProjectionResult:
                ref = asyncio.run(self._write(intent))
                return ContractProjectionResult(success=True, artifact_ref=ref)

            async def _write(self, intent: ModelProjectionIntent) -> str:
                async with self._pool.acquire() as conn:
                    row = await conn.fetchrow(
                        "INSERT INTO projections ... RETURNING id",
                        intent.entity_id,
                        intent.domain,
                    )
                    return str(row["id"])

        # Registration-time check
        assert isinstance(PostgresProjectionEffect(pool), ProtocolNodeProjectionEffect)

    Attributes:
        synchronous_execution: Inherited contract flag from ``ProtocolEffect``
            that declares all methods on this protocol are intentionally
            synchronous.  Concrete implementations MUST set this to ``True``
            to satisfy the ``isinstance`` check against ``ProtocolEffect`` and
            to exempt the class from the SPI005 async-by-default rule.

    See Also:
        - ``ProtocolEffect``: the parent synchronous effect protocol.
        - ``ContractProjectionResult``: the return contract.
        - ``ProjectorError``: the exception to raise on failure.
        omnibase_core.models.projection.model_projection_intent.ModelProjectionIntent:
            The canonical intent model for projection effects (OMN-2460).
    """

    synchronous_execution: ClassVar[bool]

    def execute(self, intent: object) -> ContractProjectionResult:
        """Write a projection to the persistence layer synchronously.

        Accepts a ``ModelProjectionIntent`` (typed as ``object`` at the
        protocol level for domain-agnosticism) and persists the described
        projection before returning.

        The caller MUST block on this method.  The write MUST be committed
        to durable storage before ``execute()`` returns.

        Args:
            intent: The projection intent.  At the protocol level the type
                is ``object``.  Concrete implementations narrow this to
                ``ModelProjectionIntent`` and validate the payload.

        Returns:
            ``ContractProjectionResult(success=True, artifact_ref=<ref>)``
            when the projection was successfully written.

            ``ContractProjectionResult(success=False, artifact_ref=None,
            error=<reason>)`` for a valid no-op (e.g. sequence already
            applied).  In this case the runtime SHOULD skip the Kafka
            publish.

        Raises:
            ProjectorError: On any infrastructure failure (connection error,
                write timeout, constraint violation).  The runtime MUST
                treat this as a fatal signal and NOT proceed to publish.
            ValueError: When ``intent`` is structurally invalid.

        Note:
            This method MUST be synchronous.  If the underlying storage is
            async, bridge via ``asyncio.run()`` inside the implementation —
            BUT only when the caller is itself synchronous.  If called from
            within an already-running event loop (e.g. FastAPI, pytest-asyncio,
            Jupyter), ``asyncio.run()`` will raise
            ``RuntimeError: This event loop is already running``.  In those
            contexts, use ``anyio.from_thread.run_sync`` or restructure the
            storage layer to expose a synchronous path.
            Never expose ``async def execute()`` — that would violate the
            ordering contract.
        """
        ...

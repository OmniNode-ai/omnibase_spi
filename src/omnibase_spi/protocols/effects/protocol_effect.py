"""ProtocolEffect -- synchronous effect execution boundary.

Defines the synchronous effect interface used by ``NodeProjectionEffect``
and any other effect that must complete before returning to the caller.

Architecture Context:
    This protocol establishes the synchronous execution boundary for
    projection writes.  The runtime invokes ``execute()`` and blocks until
    the projection is persisted, guaranteeing that the persistence layer
    has accepted the write before Kafka publish proceeds.

    Contrast with ``ProtocolPrimitiveEffectExecutor``, which is async and
    used for general-purpose kernel effect dispatch.  This protocol exists
    specifically to enforce the synchronous ordering guarantee required by
    the projection layer (OMN-2363 / OMN-2508).

Design Constraints:
    - ``execute()`` MUST be synchronous (no ``async def``).
    - If the underlying persistence layer is async, implementations MUST
      bridge via ``asyncio.run()`` or an equivalent event-loop call inside
      ``execute()``.  The async context MUST NOT leak to the caller.
    - On failure, ``execute()`` MUST raise rather than return a failure
      result.  Swallowing errors would break the ordering guarantee.

Related:
    - OMN-2508: NodeProjectionEffect as synchronous ProtocolEffect
    - OMN-2460: ModelProjectionIntent (canonical input model)
    - ``ProtocolPrimitiveEffectExecutor``: async primitive effect kernel
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.projections.contract_projection_result import (
        ContractProjectionResult,
    )


@runtime_checkable
class ProtocolEffect(Protocol):
    """Synchronous effect execution contract.

    Implementations of this protocol encapsulate a side-effecting operation
    that must complete **synchronously** before the caller proceeds.  The
    canonical implementation is ``ProtocolNodeProjectionEffect``, which writes a
    projection to the persistence layer before the runtime publishes the
    corresponding event to Kafka.

    Method Contract:
        ``execute(intent)`` MUST:
        - Be synchronous (no ``async def``, no unawaited coroutines).
        - Complete the full persistence write before returning.
        - Return ``ContractProjectionResult`` with ``success=True`` on success.
        - Raise ``ProjectorError`` (or a subclass) on infrastructure failure.
        - NOT swallow errors that would break ordering guarantees.

    Variance:
        The ``intent`` parameter is typed as ``object`` at the protocol level
        to keep the SPI domain-agnostic.  Concrete implementations narrow the
        type to the specific intent model they require (e.g.
        ``ModelProjectionIntent``).

    Example::

        class MyProjectionEffect:
            def execute(
                self, intent: ModelProjectionIntent
            ) -> ContractProjectionResult:
                # Write to DB synchronously
                ref = db.insert(intent.payload)
                return ContractProjectionResult(success=True, artifact_ref=ref)

        assert isinstance(MyProjectionEffect(), ProtocolEffect)
    """

    def execute(self, intent: object) -> ContractProjectionResult:
        """Execute the effect synchronously.

        Performs the side-effecting operation (e.g. projection persistence)
        and returns a result indicating success.  The caller blocks until
        this method returns.

        Args:
            intent: The intent describing the operation to perform.  At the
                protocol level the type is ``object`` to remain domain-agnostic.
                Concrete implementations are expected to narrow this type
                (e.g. ``ModelProjectionIntent``) and validate accordingly.

        Returns:
            ``ContractProjectionResult`` with ``success=True`` when the effect
            completed successfully, or ``success=False`` for a valid no-op
            (e.g. an idempotent skip).

        Raises:
            ProjectorError: When the persistence layer rejects or fails to
                accept the write.  Implementations MUST raise on infrastructure
                failure so the caller can take appropriate action (e.g. abort
                the Kafka publish).
            ValueError: When ``intent`` is structurally invalid and cannot be
                processed.

        Note:
            This method MUST be synchronous.  If the underlying storage is
            async, bridge via ``asyncio.run()`` inside the implementation.
            Never expose ``async def execute()`` — that would violate the
            ordering contract.
        """
        ...

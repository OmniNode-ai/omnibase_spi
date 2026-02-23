"""ProtocolEffect -- synchronous effect execution boundary.

Defines the synchronous effect interface for operations that must complete
before returning to the caller.

Architecture Context:
    This protocol establishes the synchronous execution boundary for effect
    nodes that require a guaranteed-completion semantic before the caller
    proceeds.  Unlike ``ProtocolPrimitiveEffectExecutor`` (which is async and
    used for general-purpose kernel effect dispatch), this protocol exists
    specifically to enforce a synchronous ordering guarantee.

    The ``synchronous_execution = True`` class-level flag is read by the SPI
    validator to exempt methods in this protocol from the async-by-default
    rule (SPI005).  Do not remove it.

Design Constraints:
    - ``execute()`` MUST be synchronous (no ``async def``).
    - If the underlying implementation is async, implementations MUST bridge
      via ``asyncio.run()`` or an equivalent event-loop call inside
      ``execute()``.  The async context MUST NOT leak to the caller.
    - On failure, ``execute()`` MUST raise rather than return a failure
      result.  Swallowing errors would break any ordering guarantee.

Related:
    - ``ProtocolPrimitiveEffectExecutor``: async primitive effect kernel
    - OMN-2508: NodeProjectionEffect as synchronous ProtocolEffect
    - OMN-2460: ModelProjectionIntent (canonical input model)
"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
class ProtocolEffect(Protocol):
    """Synchronous effect execution contract.

    Implementations of this protocol encapsulate a side-effecting operation
    that must complete **synchronously** before the caller proceeds.

    The ``synchronous_execution`` class variable is a contract flag used by the
    SPI validator to indicate that methods on this protocol are intentionally
    synchronous and must not be flagged as SPI005 (sync I/O) violations.

    Method Contract:
        ``execute(intent)`` MUST:
        - Be synchronous (no ``async def``, no unawaited coroutines).
        - Complete the full side-effecting operation before returning.
        - Raise on infrastructure failure rather than swallowing errors.

    Variance:
        The ``intent`` parameter is typed as ``object`` at the protocol level
        to keep the SPI domain-agnostic.  Concrete implementations narrow the
        type to the specific intent model they require (e.g.
        ``ModelProjectionIntent``).

    Attributes:
        synchronous_execution: Contract flag declaring that all methods on
            this protocol are intentionally synchronous.  Set to ``True`` on
            concrete implementations so the SPI validator can exempt the class
            from the async-by-default rule (SPI005).

    Example::

        class MyEffect:
            synchronous_execution: ClassVar[bool] = True

            def execute(self, intent: object) -> object:
                # Perform side effect synchronously
                return db.insert(intent)

        assert isinstance(MyEffect(), ProtocolEffect)
    """

    # Contract flag: signals to the SPI validator that all methods in this
    # protocol are intentionally synchronous.  The validator reads this flag
    # to exempt the class from the async-by-default rule (SPI005) instead of
    # maintaining a static sync_exceptions list.
    synchronous_execution: ClassVar[bool]

    def execute(self, intent: object) -> object:
        """Execute the effect synchronously.

        Performs the side-effecting operation and returns a result.
        The caller blocks until this method returns.

        Args:
            intent: The intent describing the operation to perform.  At the
                protocol level the type is ``object`` to remain domain-agnostic.
                Concrete implementations are expected to narrow this type
                and validate accordingly.

        Returns:
            An implementation-defined result object.  Implementations MAY
            return a typed result (e.g. ``ContractProjectionResult``) or a
            plain ``bool``.  Returns truthily on success; raises on failure.

        Raises:
            RuntimeError: When the side-effecting operation fails.
                Implementations MUST raise on failure so the caller can take
                appropriate action.
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
            Never expose ``async def execute()`` -- that would violate the
            ordering contract.
        """
        ...

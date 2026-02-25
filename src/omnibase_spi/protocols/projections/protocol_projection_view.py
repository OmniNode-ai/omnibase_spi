"""
ProtocolProjectionView — SPI protocol that ProjectionView implementations conform to.

This module defines ``ProtocolProjectionView``, the simplified synchronous SPI
contract for projection view implementations. It is distinct from the existing
``ProtocolProjector`` (which handles persistence ordering with sequence guarantees)
and ``ProtocolEventProjector`` (which takes ``ModelEnvelope`` and is async).

``ProtocolProjectionView`` is the protocol consumed by ``NodeProjectionEffect``:
given a ``ModelProjectionIntent``, produce a ``ContractProjectionResult``.
This enables the registry-based dispatch pattern where a single generic
``NodeProjectionEffect`` replaces "one custom effect node per projection".

Architecture Context::

    Reducer emits ModelProjectionIntent(projector_key=..., envelope=...)
         │
         ▼
    NodeProjectionEffect.execute(intent)
         │
         ▼
    Looks up intent.projector_key in registry → ProtocolProjectionView
         │
         ▼
    ProtocolProjectionView.project_intent(intent) → ContractProjectionResult
         │
         ▼
    Returns to runtime

Distinction from Related Protocols:
    - ``ProtocolProjector`` (projections/): Async, handles persistence ordering,
      takes (projection, entity_id, domain, sequence_info). Production use.
    - ``ProtocolEventProjector`` (projectors/): Async, takes ModelEnvelope,
      materializes state to a persistence store.
    - ``ProtocolProjectionView`` (this module): Synchronous, takes
      ModelProjectionIntent, returns ContractProjectionResult. Used by the
      generic NodeProjectionEffect registry pattern.

Related:
    - OMN-2382: This ticket. Introduces the three-abstraction projection pattern.
    - NodeProjectionEffect: The concrete generic effect node that dispatches via
      this protocol.
    - ModelProjectionIntent (omnibase_core): The intent model this protocol accepts.
    - ContractProjectionResult: The return contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.projectors.model_projection_intent import (
        ModelProjectionIntent,
    )
    from omnibase_spi.contracts.projections.contract_projection_result import (
        ContractProjectionResult,
    )

__all__ = ["ProtocolProjectionView"]


@runtime_checkable
class ProtocolProjectionView(Protocol):
    """SPI protocol that ProjectionView implementations conform to.

    ``ProtocolProjectionView`` defines the synchronous contract for view
    implementations that participate in the ``NodeProjectionEffect`` registry
    pattern. Implementations register themselves under a ``projector_key`` and
    receive fully-formed ``ModelProjectionIntent`` instances from the effect node.

    Design Principles:
        - **Synchronous**: ``project_intent()`` is synchronous. Implementations
          that require async storage should bridge via ``asyncio.run()`` inside
          ``project_intent()`` when not in a running event loop.
        - **Intent-based**: Accepts the full ``ModelProjectionIntent`` rather than
          a bare envelope, giving implementations access to routing metadata
          (``projector_key``, ``event_type``, ``correlation_id``).
        - **Result not exception for no-ops**: Return
          ``ContractProjectionResult(success=False, error=...)`` for skipped/no-op
          writes. Raise ``ProjectorError`` only for infrastructure failures.

    Key Methods:
        - ``projector_key``: The stable key used to register this view in the
          ``NodeProjectionEffect`` registry.
        - ``project_intent(intent)``: Synchronously project the intent to the
          persistence layer and return a ``ContractProjectionResult``.

    isinstance Compliance:
        This protocol is ``@runtime_checkable``. Implementations are checked at
        registration time inside ``NodeProjectionEffect.__init__``:

        .. code-block:: python

            assert isinstance(impl, ProtocolProjectionView)

    Example Implementation::

        from omnibase_spi.protocols.projections import ProtocolProjectionView
        from omnibase_spi.contracts.projections import ContractProjectionResult

        class NodeStateProjectionView:
            @property
            def projector_key(self) -> str:
                return "node_state_projector"

            def project_intent(
                self, intent: ModelProjectionIntent
            ) -> ContractProjectionResult:
                # Cast envelope to expected type
                envelope = cast(NodeCreatedEnvelope, intent.envelope)
                # Persist to DB (bridging async if needed)
                asyncio.run(self._write(envelope))
                return ContractProjectionResult(success=True, artifact_ref=str(envelope.node_id))

    See Also:
        - ``NodeProjectionEffect``: The generic effect node that dispatches to
          registered ``ProtocolProjectionView`` implementations.
        - ``ModelProjectionIntent``: The intent model produced by reducers.
        - ``ContractProjectionResult``: The return wire format.
        - ``ProtocolProjector``: The persistence-ordering protocol (distinct from this).
        - ``ProtocolEventProjector``: The async envelope-based protocol (distinct from this).

    Attributes:
        synchronous_execution: ClassVar flag declaring that all methods on
            this protocol are intentionally synchronous. Set to ``True`` in
            concrete implementations to satisfy the SPI typing validator
            (SPI-T003) and to document the synchronous execution contract.
    """

    synchronous_execution: ClassVar[bool]

    @property
    def projector_key(self) -> str:
        """Unique registry key for this projection view.

        The key is used by ``NodeProjectionEffect`` to resolve the correct
        view implementation for a given ``ModelProjectionIntent.projector_key``.

        Format:
            Snake-case identifier. Examples: ``"node_state_projector"``,
            ``"workflow_summary_projector"``.

        Returns:
            A unique string key that matches ``ModelProjectionIntent.projector_key``
            values routed to this implementation.

        Invariants:
            - Must be unique across all registered views in a given
              ``NodeProjectionEffect`` instance.
            - Must be stable across restarts (used for routing matching).
        """
        ...

    def project_intent(
        self,
        intent: ModelProjectionIntent,
    ) -> ContractProjectionResult:
        """Project a ``ModelProjectionIntent`` to the persistence layer.

        Synchronously processes the intent and materializes the described
        projection to the target persistence store. Returns a result
        indicating success, no-op, or infrastructure error.

        Synchronous Contract:
            This method MUST be synchronous. Implementations that use async
            storage backends must bridge via ``asyncio.run()`` inside this method
            when not in a running event loop. Never expose ``async def project_intent()``.

        Args:
            intent: The projection intent carrying routing metadata and the
                full event envelope. Key fields:
                - ``intent.projector_key``: This view's key (pre-validated by dispatcher).
                - ``intent.event_type``: The event type that triggered this intent.
                - ``intent.envelope``: The full event payload (cast to expected type).
                - ``intent.correlation_id``: For distributed tracing.

        Returns:
            ``ContractProjectionResult(success=True, artifact_ref=<ref>)``
            when the projection was successfully persisted.

            ``ContractProjectionResult(success=False, error=<reason>)``
            for valid no-op writes (e.g. idempotent skip, stale sequence).
            In this case the runtime SHOULD skip the Kafka publish.

        Raises:
            ProjectorError: On infrastructure failure (connection error, write
                timeout, constraint violation). The runtime MUST treat this as
                fatal and NOT proceed to publish.
            ValueError: If the intent's envelope is structurally invalid for
                this view's expected type.

        Note:
            Return ``ContractProjectionResult(success=False, error=...)`` for
            semantically valid non-writes. Raise ``ProjectorError`` only for
            infrastructure failures that must abort the pipeline.
        """
        ...

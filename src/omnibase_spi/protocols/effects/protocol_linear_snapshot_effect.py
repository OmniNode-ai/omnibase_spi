"""ProtocolLinearSnapshotEffect — SPI Protocol for Linear snapshot polling.

Defines the abstract interface that the ONEX runtime calls to poll the
Linear workspace for workstream snapshots and produce events to
``onex.evt.linear.snapshot.v1``.

Architecture Context::

    [Scheduler / Cron]
          │
          ▼
    ProtocolLinearSnapshotEffect.snapshot(workspace_id)
          │ [async — calls Linear API]
          ▼
    [returns ContractLinearSnapshotEvent]
          │
          ▼
    [Runtime publishes to onex.evt.linear.snapshot.v1]

Implementations MUST:
    - Be async (``snapshot()`` is an async method).
    - Generate a stable, globally-unique ``snapshot_id`` per invocation.
    - Return one ``ContractLinearSnapshotEvent`` per call.
    - Raise on unrecoverable API errors.

Related:
    - OMN-2655: This ticket.
    - ContractLinearSnapshotEvent: Return type.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.events.contract_linear_snapshot_event import (
        ContractLinearSnapshotEvent,
    )


@runtime_checkable
class ProtocolLinearSnapshotEffect(Protocol):
    """Async protocol for producing Linear workspace snapshot events.

    Implementations poll the Linear API for workstream state and return a
    ``ContractLinearSnapshotEvent`` for Kafka publication on
    ``onex.evt.linear.snapshot.v1``.

    Method Contract:
        ``snapshot(workspace_id)`` MUST:
        - Be async (``async def``).
        - Generate a globally-unique ``snapshot_id`` for each invocation.
        - Return one ``ContractLinearSnapshotEvent``.
        - Raise ``RuntimeError`` on unrecoverable failure.

    isinstance Compliance:
        This protocol is ``@runtime_checkable``::

            assert isinstance(my_impl, ProtocolLinearSnapshotEffect)
    """

    async def snapshot(
        self,
        workspace_id: str,
    ) -> ContractLinearSnapshotEvent:
        """Poll Linear for workstream state and produce a snapshot event.

        Args:
            workspace_id: Linear workspace identifier to poll.

        Returns:
            A ``ContractLinearSnapshotEvent`` capturing current workstream
            state with a freshly generated ``snapshot_id``.

        Raises:
            RuntimeError: On unrecoverable Linear API errors.
        """
        ...

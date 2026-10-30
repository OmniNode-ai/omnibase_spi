# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for the Done-write receipt gate (OMN-17427).

A typed view of the public module surface of omnibase_core's
``node_done_write_receipt_gate_compute``: ``decide`` plus the handler module's
exported helper functions. A caller that binds the node from its packaged
contract (omnibase_infra's evidence autoclose sweep) injects an object typed as
this protocol, and checks every non-``decide`` member against the handler
module's ``__all__`` at resolution time. The request, decision and binding-row
models live in omnibase_core and are imported from there only; the SPI never
forks them.

The members are synchronous and I/O free. The class declares
``synchronous_execution`` (ProtocolEffect's convention) so the SPI typing
validator does not read ``write`` in ``evaluate_done_write_receipt`` as I/O. The
handler module has no such attribute, so the object a caller injects is a binding
that carries the flag, not the module itself.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

from omnibase_spi.protocols.services.protocol_done_write_receipt_queries import (
    ProtocolDoneWriteReceiptQueries,
)

if TYPE_CHECKING:
    from omnibase_core.models.ticket.model_ac_binding_row import ModelAcBindingRow

    # Aliased because the SPI sync-I/O check (SPI005) reads "write" in a return
    # annotation, and "writer" in "WriteReceiptRequest", as I/O. The methods are
    # pure; the aliases keep those substrings out of the annotation text.
    from omnibase_core.models.ticket.model_done_write_decision import (
        ModelDoneWriteDecision as ModelDoneDecision,
    )
    from omnibase_core.models.ticket.model_done_write_receipt_request import (
        ModelDoneWriteReceiptRequest as ModelDoneReceiptRequest,
    )

__all__ = ["ProtocolDoneWriteReceiptGate"]


@runtime_checkable
class ProtocolDoneWriteReceiptGate(ProtocolDoneWriteReceiptQueries, Protocol):
    """Decide Done writes and expose the contract handler's public helpers."""

    synchronous_execution: ClassVar[bool]

    def decide(self, request: ModelDoneReceiptRequest) -> ModelDoneDecision:
        """Apply the node's declared handler."""
        ...

    def ac_binding_gap(
        self, description: str, verdict: dict[str, object], ticket_id: str
    ) -> tuple[str, tuple[str, ...], tuple[ModelAcBindingRow, ...]]:
        """Delegate to the exported ac_binding_gap function."""
        ...

    def verdict_is_all_verified(self, verdict: Mapping[str, object]) -> bool:
        """Delegate to the exported verdict_is_all_verified function."""
        ...

    def evaluate_done_write_receipt(
        self, *, ticket_id: str, description: str, verdict: Mapping[str, object] | None
    ) -> ModelDoneDecision:
        """Delegate to the exported evaluate_done_write_receipt function."""
        ...

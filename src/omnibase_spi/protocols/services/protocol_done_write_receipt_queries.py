# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for the Done-write receipt gate's verdict-reading functions (OMN-17427).

The read-only half of ``ProtocolDoneWriteReceiptGate``: the public functions of
omnibase_core's ``node_done_write_receipt_gate_compute`` handler module that read
a dod-verify verdict and a ticket's acceptance criteria. A caller that only reads
verdicts types against this protocol and does not need ``decide``.

The members are module-level functions in the handler module, so a conforming
object is that module (or a stand-in with the same callables). They are plain
synchronous functions: no I/O, no ``synchronous_execution`` flag, because a flag
attribute would be absent from the module and fail ``isinstance`` against it.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["ProtocolDoneWriteReceiptQueries"]


@runtime_checkable
class ProtocolDoneWriteReceiptQueries(Protocol):
    """Read verdicts and criteria through the contract handler's public functions."""

    def has_verified_bound_check(self, verdict: dict[str, object]) -> bool:
        """Delegate to the exported has_verified_bound_check function."""
        ...

    def as_int(self, value: object) -> int:
        """Delegate to the exported as_int function."""
        ...

    def extract_dod_verify_verdict(
        self, receipt: dict[str, object]
    ) -> tuple[dict[str, object] | None, str]:
        """Delegate to the exported extract_dod_verify_verdict function."""
        ...

    def live_acceptance_criteria_items(self, description: str) -> list[str]:
        """Delegate to the exported live_acceptance_criteria_items function."""
        ...

    def canonical_ac_label(self, text: str) -> str:
        """Delegate to the exported canonical_ac_label function."""
        ...

    def criterion_is_state_shaped(self, criterion: str) -> bool:
        """Delegate to the exported criterion_is_state_shaped function."""
        ...

    def check_records(
        self, verdict: dict[str, object]
    ) -> tuple[dict[str, object], ...]:
        """Delegate to the exported check_records function."""
        ...

    def check_status(self, check: dict[str, object]) -> str:
        """Delegate to the exported check_status function."""
        ...

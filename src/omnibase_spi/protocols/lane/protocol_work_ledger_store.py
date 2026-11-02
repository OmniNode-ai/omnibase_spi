# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for reading a lane's rows from the work ledger. Rows are raw lines."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolWorkLedgerStore(Protocol):
    """Read ledger rows for one lane."""

    def rows_for_lane(self, lane: str) -> tuple[str, ...]:
        """Return the raw ledger lines whose ``lane=`` cell is ``lane``, oldest first."""
        ...

    def queued_rows(self, lane: str, run_id: str) -> tuple[str, ...]:
        """Return the raw lines the lane queued on its host for relay in ``run_id``."""
        ...


__all__ = ["ProtocolWorkLedgerStore"]

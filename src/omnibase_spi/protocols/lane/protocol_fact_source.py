# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for the facts one floor fill pass reads: the floor, a plan text, the brake and the stop signal."""

from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
class ProtocolFactSource(Protocol):
    """Read the facts a floor fill pass decides from.

    A source that cannot be read raises; the caller names the source and the
    exception's text as the cause and starts nothing on it. The
    ``synchronous_execution = True`` class-level flag is read by the SPI validator
    to exempt the methods from the async-by-default rule: each call is a
    synchronous read.
    """

    synchronous_execution: ClassVar[bool]

    def read_floor(self, url: str) -> str:
        """Return the floor record published at ``url`` as its raw text."""
        ...

    def read_plan(self, plans_root: str, line_id: str) -> str:
        """Return the plan text of line ``line_id`` found under ``plans_root``."""
        ...

    def landing_only(self) -> bool:
        """Return True while the open-count brake holds (the open count rose on two reads)."""
        ...

    def stop_refuses(self, task_class: str) -> str | None:
        """Return the cause when a stop signal refuses ``task_class``, else None."""
        ...


__all__ = ["ProtocolFactSource"]

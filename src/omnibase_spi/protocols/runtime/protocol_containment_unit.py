# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for running a command inside a scope of its own.

A command is born inside a named unit, so every process it starts, including one
that detaches from its session, is a member of the unit. Stopping the unit kills
every member and confirms none is left.
"""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolContainmentUnit(Protocol):
    """Run a command in a unit, list the unit's members, stop the unit and confirm it is empty."""

    def run_contained(self, unit: str, argv: Sequence[str]) -> int:
        """Start ``argv`` inside the new unit ``unit`` and return its process id.

        Raises InvalidProtocolStateError when the unit already has members.
        """
        ...

    def members(self, unit: str) -> tuple[int, ...]:
        """Return the sorted process ids now in ``unit``; empty when none or unknown."""
        ...

    def stop(self, unit: str, timeout_s: float) -> bool:
        """Kill every member of ``unit`` and wait up to ``timeout_s`` for it to be empty.

        Returns True only when the unit was read empty; False means members remain.
        """
        ...


__all__ = ["ProtocolContainmentUnit"]

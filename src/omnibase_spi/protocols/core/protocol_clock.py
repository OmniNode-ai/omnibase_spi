# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for the clock a node reads the current time through.

A node that needs the time takes a clock instead of calling the system clock, so
a test or a lab binding can swap it for a fixed or a stepping one.
"""

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolClock(Protocol):
    """One read of the current time."""

    def now(self) -> datetime:
        """Return the current time."""
        ...


__all__ = ["ProtocolClock"]

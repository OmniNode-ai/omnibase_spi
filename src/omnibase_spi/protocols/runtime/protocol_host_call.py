# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Protocol for one typed call to a host under a timeout.

The caller gets a typed answer: ``ok``, ``refused`` with a cause, or ``unknown``
when no answer came in time. Unknown means the caller cannot tell whether the host
acted, and it must treat the call as possibly done.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services import (
        ModelHostCallAnswer,
        ModelHostCallRequest,
    )


@runtime_checkable
class ProtocolHostCall(Protocol):
    """Send one request to a host and return its typed answer."""

    def call(
        self, request: "ModelHostCallRequest", timeout_s: float
    ) -> "ModelHostCallAnswer":
        """Send ``request`` and wait at most ``timeout_s`` seconds for the answer.

        The answer repeats ``request.request_id``. A call that gets no answer in time
        returns outcome ``unknown``; it does not raise.
        """
        ...


__all__ = ["ProtocolHostCall"]

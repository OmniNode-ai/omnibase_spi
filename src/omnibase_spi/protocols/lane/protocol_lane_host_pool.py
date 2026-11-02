# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for reading the lane host pool: capacity and readiness per host."""

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.contracts.services import (
        ModelLaneHostPoolRequest,
        ModelLaneHostPoolSnapshot,
    )


@runtime_checkable
class ProtocolLaneHostPool(Protocol):
    """Read the pool of hosts a lane can be placed on.

    The ``synchronous_execution = True`` class-level flag is read by the SPI
    validator to exempt ``read_pool`` from the async-by-default rule: the read is
    a synchronous request/snapshot exchange.
    """

    synchronous_execution: ClassVar[bool]

    def read_pool(
        self, request: "ModelLaneHostPoolRequest"
    ) -> "ModelLaneHostPoolSnapshot":
        """Return one reading per host and the pool-wide limits at this moment."""
        ...


__all__ = ["ProtocolLaneHostPool"]

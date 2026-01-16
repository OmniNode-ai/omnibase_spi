"""ProtocolTestableCLI: Protocol for all testable CLI entrypoints.

Requires main(argv) -> ModelResultCLI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_mcp_types import ProtocolModelResultCLI


@runtime_checkable
class ProtocolTestableCLI(Protocol):
    """
    Protocol for all testable CLI entrypoints. Requires main(argv) -> ModelResultCLI.

    Example:
        class MyTestableCLI(ProtocolTestableCLI):
            def main(self, argv: list[str]) -> "ProtocolModelResultCLI":
                ...
    """

    async def main(self, argv: list[str]) -> ProtocolModelResultCLI: ...

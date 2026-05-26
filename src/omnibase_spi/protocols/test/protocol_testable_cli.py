# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ProtocolTestableCLI: Protocol for all testable CLI entrypoints.

Requires main(argv) -> ModelResultCLI.
"""

from typing import Protocol, runtime_checkable

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

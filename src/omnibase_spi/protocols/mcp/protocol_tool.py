"""Protocol for MCP tool operations with dry-run and apply modes.

This module defines the interface for CLI scripts that can modify files,
enforcing safety with dry-run as default and explicit apply mode.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_mcp_types import (
    ProtocolModelResultCLI,
    ProtocolModelToolArguments,
    ProtocolModelToolInputData,
)


@runtime_checkable
class ProtocolTool(Protocol):
    """
    Protocol for CLI scripts that can modify files. Adds --apply flag, defaults to dry-run, and enforces safety messaging.
    All file-modifying logic must be gated behind --apply. Dry-run is always the default.

    Example:
        class MyTool(ProtocolTool):
            def dry_run_main(self, args) -> ModelResultCLI:
                ...
            def apply_main(self, args) -> ModelResultCLI:
                ...
            def execute(self, input_data: ProtocolModelToolInputData) -> ModelResultCLI:
                ...
    """

    async def dry_run_main(
        self, args: ProtocolModelToolArguments
    ) -> ProtocolModelResultCLI: ...

    async def apply_main(
        self, args: ProtocolModelToolArguments
    ) -> ProtocolModelResultCLI: ...

    async def execute(
        self, input_data: ProtocolModelToolInputData
    ) -> ProtocolModelResultCLI: ...

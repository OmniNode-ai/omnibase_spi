# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.122722'
# description: Stamped by ToolPython
# entrypoint: python://protocol_cli
# hash: d1ed8d5010052c5eb8c2189bb4780e6b8e8f54ef9efcdd98e65ddc6c92d7876e
# last_modified_at: '2025-05-29T14:14:00.206328+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_cli.py
# namespace: python://omnibase.protocol.protocol_cli
# owner: OmniNode Team
# protocol_version: 0.1.0
# resource: python://omnibase.spi.protocol.cli
# tags: ['cli', 'protocol', 'tool']
# tool_type: protocol
# version: 0.1.0
# === OmniNode:Metadata ===

"""
CLI Protocol for ONEX Systems

Defines the protocol interface for CLI operations with strict SPI purity compliance.
Provides standardized contract for argument parsing, logging, and CLI result handling.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Import core logger protocol to avoid duplication
from omnibase_spi.protocols.core import ProtocolLogger


@runtime_checkable
class ProtocolCLIResult(Protocol):
    """Protocol for CLI operation results."""

    success: bool
    exit_code: int
    message: str
    data: dict[str, object] | None
    errors: list[str]


@runtime_checkable
class ProtocolCLIFlagDescription(Protocol):
    """Protocol for CLI flag descriptions."""

    name: str
    type: str
    default: str | None
    help: str | None
    required: bool


@runtime_checkable
class ProtocolCLI(Protocol):
    """Protocol for standardized command-line interface operations in ONEX systems.

    Defines the contract for CLI entrypoints providing argument parsing, logging
    configuration, exit code handling, and metadata enforcement. Enables consistent
    CLI behavior across all ONEX tools with structured result handling and flag
    documentation. Serves as the foundation for specialized CLI protocols.

    Example:
        ```python
        from omnibase_spi.protocols.cli import ProtocolCLI, ProtocolCLIResult

        async def run_cli_command(
            cli: ProtocolCLI,
            command_args: list[str]
        ) -> ProtocolCLIResult:
            # Validate arguments before execution
            if not await cli.validate_arguments(command_args):
                return ProtocolCLIResult(
                    success=False,
                    exit_code=1,
                    message="Invalid arguments",
                    data=None,
                    errors=["Argument validation failed"]
                )

            # Get available flags for documentation
            flags = cli.describe_flags(format="json")
            print(f"Available flags: {len(flags)}")

            # Execute command with validated arguments
            result = await cli.run(command_args)

            print(f"Execution {'succeeded' if result.success else 'failed'}")
            print(f"Exit code: {result.exit_code}")

            return result
        ```

    Key Features:
        - Argument parser generation and configuration
        - Command execution with structured results
        - Argument validation before execution
        - Flag documentation and introspection
        - Integrated logging support
        - Exit code standardization
        - Metadata enforcement for CLI tools

    See Also:
        - ProtocolCliWorkflow: Workflow-based CLI operations
        - ProtocolCLIDirFixtureCase: Test fixture management
        - ProtocolLogger: Logging integration
    """

    description: str
    logger: ProtocolLogger

    async def get_parser(self) -> "Any": ...

    async def main(self, argv: list[str] | None = None) -> "ProtocolCLIResult": ...

    async def run(self, args: list[str]) -> "ProtocolCLIResult": ...

    def describe_flags(
        self, format: str | None = None
    ) -> list["ProtocolCLIFlagDescription"]: ...

    async def execute_command(
        self, command: str, args: list[str]
    ) -> "ProtocolCLIResult":
        """
        Execute a CLI command with the given arguments.

        Args:
            command: The command to execute
            args: List of arguments for the command

        Returns:
            CLI result object with execution status and output
        """
        ...

    async def validate_arguments(self, args: list[str]) -> bool:
        """
        Validate CLI arguments before execution.

        Args:
            args: List of arguments to validate

        Returns:
            True if arguments are valid, False otherwise
        """
        ...

"""CLI Protocol for ONEX Systems.

Defines the protocol interface for CLI operations with strict SPI purity compliance.
Provides standardized contract for argument parsing, logging, and CLI result handling.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

# Import core logger protocol to avoid duplication
from omnibase_spi.protocols.core import ProtocolLogger


@runtime_checkable
class ProtocolCLIResult(Protocol):
    """
    Protocol for CLI command execution result representation.

    Captures the complete outcome of CLI command execution including
    success status, exit codes, messages, structured data output, and
    any errors encountered during command processing.

    Attributes:
        success: Whether command executed successfully
        exit_code: UNIX-style exit code (0=success, non-zero=failure)
        message: Human-readable result message
        data: Optional structured data output from command
        errors: List of error messages if any occurred

    Example:
        ```python
        cli: ProtocolCLI = get_cli_handler()
        result = await cli.run(["validate", "--strict", "path/to/node"])

        if result.success:
            print(f"Success: {result.message}")
            if result.data:
                print(f"Output: {result.data}")
        else:
            print(f"Failed (exit {result.exit_code}): {result.message}")
            for error in result.errors:
                print(f"  Error: {error}")
        ```

    See Also:
        - ProtocolCLI: Main CLI protocol
        - ProtocolCliExecutionResult: Extended workflow results
    """

    success: bool
    exit_code: int
    message: str
    data: dict[str, object] | None
    errors: list[str]


@runtime_checkable
class ProtocolCLIFlagDescription(Protocol):
    """
    Protocol for CLI flag/argument metadata description.

    Provides structured information about CLI flags and arguments
    for documentation generation, help text rendering, and
    programmatic CLI introspection.

    Attributes:
        name: Flag name (e.g., "--verbose" or "-v")
        type: Argument type (string, boolean, integer, etc.)
        default: Default value if flag not provided
        help: Human-readable help text describing the flag
        required: Whether the flag must be provided

    Example:
        ```python
        cli: ProtocolCLI = get_cli_handler()
        flags = cli.describe_flags(output_format="json")

        for flag in flags:
            required_marker = "*" if flag.required else ""
            print(f"{flag.name}{required_marker}: {flag.type}")
            if flag.help:
                print(f"  {flag.help}")
            if flag.default:
                print(f"  Default: {flag.default}")
        ```

    See Also:
        - ProtocolCLI: CLI interface using these flag descriptions
        - ProtocolCLI.describe_flags: Method returning flag descriptions
    """

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
            flags = cli.describe_flags(output_format="json")
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

    async def get_parser(self) -> Any:
        """
        Get the argument parser for this CLI.

        Creates and returns the configured argument parser instance used
        for parsing command-line arguments. The parser includes all
        registered flags, subcommands, and help text.

        Returns:
            Configured argument parser instance (typically argparse.ArgumentParser
            or compatible parser implementation).

        Raises:
            SPIError: If parser configuration fails.
        """
        ...

    async def main(self, argv: list[str] | None = None) -> ProtocolCLIResult:
        """
        Main entry point for CLI execution.

        Parses arguments, configures logging, and executes the appropriate
        command handler. This is the primary method called when the CLI
        tool is invoked from the command line.

        Args:
            argv: Command-line arguments to parse. If None, uses sys.argv[1:].

        Returns:
            CLI result object containing success status, exit code,
            message, optional data output, and any errors encountered.

        Raises:
            SPIError: If CLI initialization or execution fails unexpectedly.
        """
        ...

    async def run(self, args: list[str]) -> ProtocolCLIResult:
        """
        Execute CLI with pre-parsed arguments.

        Runs the CLI command using the provided argument list without
        additional parsing. Use this method when arguments have already
        been validated or when programmatically invoking CLI commands.

        Args:
            args: List of pre-parsed command-line arguments.

        Returns:
            CLI result object containing success status, exit code,
            message, optional data output, and any errors encountered.

        Raises:
            SPIError: If command execution fails unexpectedly.
        """
        ...

    def describe_flags(
        self, output_format: str | None = None
    ) -> list[ProtocolCLIFlagDescription]:
        """
        Get descriptions of all available CLI flags and arguments.

        Provides metadata about all registered CLI flags for documentation
        generation, help text rendering, or programmatic introspection
        of CLI capabilities.

        Args:
            output_format: Optional format specifier for flag descriptions.
                If None, returns flag descriptions in the implementation's
                default format (typically structured objects). Common values
                include "json", "yaml", "text", or "markdown" for serialized
                output.

        Returns:
            List of flag description objects containing name, type,
            default value, help text, and required status for each flag.

        Raises:
            SPIError: If flag introspection fails.
        """
        ...

    async def execute_command(self, command: str, args: list[str]) -> ProtocolCLIResult:
        """
        Execute a specific CLI command with the given arguments.

        Dispatches to the appropriate command handler based on the command
        name and passes the provided arguments. This method is typically
        called after argument validation has been performed.

        Args:
            command: The command name to execute (e.g., "validate", "build",
                "run"). Must be a registered command in this CLI instance.
            args: List of arguments to pass to the command handler. These
                are the arguments specific to the command, not including
                the command name itself.

        Returns:
            CLI result object containing success status, exit code,
            message, optional data output, and any errors encountered
            during command execution.

        Raises:
            SPIError: If command execution fails unexpectedly.
            RegistryError: If the command is not registered or recognized.
        """
        ...

    async def validate_arguments(self, args: list[str]) -> bool:
        """
        Validate CLI arguments before execution.

        Performs validation of the provided arguments against the CLI's
        registered flags and argument specifications. This should be
        called before execute_command or run to ensure arguments are
        well-formed and meet requirements.

        Args:
            args: List of command-line arguments to validate. Should
                include all arguments as they would be passed to the CLI,
                potentially including the command name and all flags/values.

        Returns:
            True if all arguments are valid and the command can be executed
            safely. False if any arguments are invalid, missing required
            values, or have incorrect types.

        Raises:
            SPIError: If validation cannot be performed due to internal error.
        """
        ...

"""Protocol for ONEX node CLI adapters.

This module defines the interface for adapters that convert command-line arguments
into node input state objects for seamless CLI-to-node integration.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNodeCliAdapter(Protocol):
    """
    Protocol for ONEX node CLI adapters with argument parsing and state transformation.

    Defines the contract for CLI adapters that convert command-line arguments into
    node input state objects, enabling seamless integration between CLI interfaces
    and ONEX node execution contexts. Supports flexible argument parsing strategies
    and type-safe state generation.

    Example:
        ```python
        from omnibase_spi.protocols.cli import ProtocolNodeCliAdapter

        async def execute_node_from_cli(
            adapter: ProtocolNodeCliAdapter,
            cli_args: list[str]
        ) -> object:
            # Parse CLI arguments into node input state
            input_state = adapter.parse_cli_args(cli_args)

            # Input state can now be passed to node execution
            print(f"Parsed state type: {type(input_state).__name__}")
            print(f"State attributes: {vars(input_state)}")

            return input_state
        ```

    Key Features:
        - CLI argument parsing and validation
        - Type-safe input state generation
        - Support for argparse.Namespace and list[str] inputs
        - Node-specific state transformation
        - Integration with ONEX node execution pipelines
        - Extensible for custom argument patterns

    See Also:
        - ProtocolCLI: Base CLI protocol for command execution
        - ProtocolCLIWorkflow: Workflow-level CLI operations
        - ProtocolCLIToolDiscovery: CLI tool discovery and registration
    """

    def parse_cli_args(self, cli_args: list[str]) -> object: ...

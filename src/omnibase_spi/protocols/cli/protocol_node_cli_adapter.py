# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.212774'
# description: Stamped by ToolPython
# entrypoint: python://protocol_node_cli_adapter
# hash: 7be0d74a66e027be62d464bfa5414f629bc5419a431d39a2c29843002c3f00aa
# last_modified_at: '2025-05-29T14:14:00.283432+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_node_cli_adapter.py
# namespace: python://omnibase.protocol.protocol_node_cli_adapter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: e1f3e769-a996-476e-a659-34ec8a77dee2
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Protocol, runtime_checkable


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
        ) -> Any:
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

    def parse_cli_args(self, cli_args: list[str]) -> Any: ...

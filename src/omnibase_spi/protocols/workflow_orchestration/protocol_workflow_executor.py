"""
Protocol interface for Workflow executor tools.

This protocol defines the interface for tools that execute specific
operations within workflows, such as model generation and bootstrap validation.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
    from omnibase_spi.protocols.node.protocol_node_registry import ProtocolNodeRegistry
    from omnibase_spi.protocols.types.protocol_file_handling_types import (
        ProtocolResult,
    )


@runtime_checkable
class ProtocolWorkflowExecutor(Protocol):
    """
    Protocol for Workflow executor tools that handle execution of specific
    operations within workflows.

    These tools perform the actual work of Workflow operations such as
    model generation, bootstrap validation, and tool extraction.
    """

    def set_registry(self, registry: "ProtocolNodeRegistry") -> None:
        """
        Set the registry for accessing other tools.

        Args:
            registry: The registry containing other tools and dependencies
        """
        ...

    async def run(self, input_state: dict[str, "JsonType"]) -> "ProtocolResult":
        """
        Run the Workflow executor with the provided input state.

        Args:
            input_state: Input state containing action and parameters

        Returns:
            Result of Workflow execution
        """
        ...

    async def execute_operation(
        self,
        operation_type: str,
        scenario_id: str,
        correlation_id: str,
        parameters: dict[str, "JsonType"],
    ) -> "ProtocolResult":
        """
        Execute a specific operation.

        Args:
            operation_type: Type of operation to execute
            scenario_id: ID of the scenario
            correlation_id: Correlation ID for tracking
            parameters: Parameters for the operation

        Returns:
            Result of operation execution
        """
        ...

    def supports_operation(self, operation_type: str) -> bool:
        """
        Check if this executor supports a specific operation type.

        Args:
            operation_type: Type of operation to check

        Returns:
            True if operation is supported
        """
        ...

    async def get_supported_operations(self) -> list[str]:
        """
        Get list of supported operation types.

        Returns:
            List of supported operation type strings
        """
        ...

    def validate_parameters(
        self,
        operation_type: str,
        parameters: dict[str, "JsonType"],
    ) -> list[str]:
        """
        Validate parameters for a specific operation.

        Args:
            operation_type: Type of operation
            parameters: Parameters to validate

        Returns:
            List of validation errors (empty if valid)
        """
        ...

    def health_check(self) -> "JsonType":
        """
        Perform health check for the Workflow executor.

        Returns:
            Health check result with status and capabilities
        """
        ...

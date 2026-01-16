"""
Protocol for ONEX node runners (runtime/placement).

Defines the interface for node execution and event emission in ONEX architecture.
All node runner implementations must conform to this interface.

Domain: Node - Runtime execution protocols
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNodeRunner(Protocol):
    """
    Canonical protocol for ONEX node runners (runtime/placement).

    Provides the standard interface for node execution and event emission
    across different node types and implementations.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        runner: "ProtocolNodeRunner" = get_node_runner()

        # Execute node with arguments
        result = await runner.run(
            node_id="compute-node-001",
            task="process_data",
            input_file="/data/input.csv",
            output_path="/data/output/",
            timeout_ms=30000
        )

        print(f"Node execution result: {result}")

        # Execute with configuration
        config = {
            "cpu_limit": 4,
            "memory_limit": "8GB",
            "gpu_enabled": True
        }

        result = await runner.run(
            node_id="ml-node-002",
            task="train_model",
            model_config=config,
            dataset_path="/models/dataset/"
        )
        ```

    Node Execution Patterns:
        - Synchronous execution with flexible argument passing
        - Event emission for real-time monitoring
        - Resource management and allocation
        - Error handling and failure recovery
        - Performance metrics collection

    Key Features:
        - Flexible argument handling through *args and **kwargs
        - Type-safe execution with configurable return types
        - Support for both CPU and GPU workloads
        - Integration with ONEX resource management
        - Event-driven status reporting
    """

    async def run(self, *args: object, **kwargs: object) -> object:
        """
        Execute the node with provided arguments.

        Args:
            *args: Variable positional arguments for node execution
            **kwargs: Variable keyword arguments for node configuration

        Returns:
            object: Execution result, which can vary by node type and implementation

        Raises:
            NodeExecutionError: If node execution fails
            ResourceLimitError: If resource limits are exceeded
            TimeoutError: If execution exceeds time limits
        """
        ...

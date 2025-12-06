"""Reducer node protocol for state aggregation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.nodes.base import ProtocolNode

if TYPE_CHECKING:
    from omnibase_core.models.reducer import ModelReductionInput, ModelReductionOutput


@runtime_checkable
class ProtocolReducerNode(ProtocolNode, Protocol):
    """
    Protocol for reducer nodes.

    Reducer nodes aggregate state from a stream of inputs.
    They maintain accumulated state and produce outputs
    based on reduction logic.

    Key characteristics:
        - State aggregation from multiple inputs
        - Maintains accumulated state across invocations
        - Produces reduced/aggregated outputs

    Example implementations:
        - Event aggregation nodes
        - State accumulation nodes
        - Metrics collection nodes
        - Log aggregation nodes
    """

    async def execute(
        self,
        input_data: ModelReductionInput,
    ) -> ModelReductionOutput:
        """
        Execute state reduction.

        Args:
            input_data: Reduction input model from core.

        Returns:
            Reduction output model from core.

        Raises:
            SPIError: If reduction fails.
        """
        ...

"""Compute node protocol for pure transformations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from omnibase_spi.protocols.nodes.base import ProtocolNode

if TYPE_CHECKING:
    from omnibase_core.models.compute import ModelComputeInput, ModelComputeOutput


@runtime_checkable
class ProtocolComputeNode(ProtocolNode, Protocol):
    """
    Protocol for pure compute nodes.

    Compute nodes perform deterministic, side-effect-free transformations.
    The same input should always produce the same output.

    Key characteristics:
        - No side effects (no I/O, no state mutation)
        - Deterministic output for given input
        - Suitable for data transformation, validation, and calculations

    Example implementations:
        - Data transformation nodes
        - Validation nodes
        - Algorithm execution nodes
        - Stateless business logic nodes
    """

    async def execute(
        self,
        input_data: ModelComputeInput[Any],
    ) -> ModelComputeOutput[Any]:
        """
        Execute pure computation.

        Args:
            input_data: Compute input model from core.

        Returns:
            Compute output model from core.

        Raises:
            SPIError: If computation fails.
        """
        ...

    @property
    def is_deterministic(self) -> bool:
        """
        Whether the node is expected to be deterministic.

        True means same input_data always yields same output.
        Compute nodes should typically return True.

        Returns:
            True if deterministic, False otherwise.
        """
        ...

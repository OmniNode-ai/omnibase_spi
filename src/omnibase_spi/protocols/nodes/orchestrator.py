"""Orchestrator node protocol for workflow coordination."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.nodes.base import ProtocolNode

if TYPE_CHECKING:
    from omnibase_core.models.orchestrator import (
        ModelOrchestratorInput,
        ModelOrchestratorOutput,
    )


@runtime_checkable
class ProtocolOrchestratorNode(ProtocolNode, Protocol):
    """
    Protocol for orchestrator nodes.

    Orchestrator nodes coordinate the execution of other nodes
    or workflows. They manage complex multi-step processes.

    Key characteristics:
        - Coordinates multiple node executions
        - Manages workflow state and dependencies
        - Handles error recovery and compensation
        - Routes work to appropriate nodes

    Example implementations:
        - Workflow engine nodes
        - Pipeline orchestration nodes
        - Saga coordination nodes
        - Process manager nodes
    """

    async def execute(
        self,
        input_data: ModelOrchestratorInput,
    ) -> ModelOrchestratorOutput:
        """
        Execute orchestration.

        Args:
            input_data: Orchestration input model from core.

        Returns:
            Orchestration output model from core.

        Raises:
            SPIError: If orchestration fails.
        """
        ...

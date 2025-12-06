"""Workflow contract compiler protocol."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.contract import (
        ModelContractValidationResult,
        ModelWorkflowContract,
    )


@runtime_checkable
class ProtocolWorkflowContractCompiler(Protocol):
    """
    Compile and validate workflow contracts from YAML.

    Workflow contracts define multi-step orchestration flows
    with dependencies, error handling, and compensation.

    Note:
        This is a build-time tool for CLI usage, not a runtime node.
        Methods are async to maintain consistency with SPI patterns
        and allow for future flexibility in I/O operations.
    """

    async def compile(
        self,
        contract_path: Path,
    ) -> ModelWorkflowContract:
        """
        Compile workflow contract from YAML file.

        Args:
            contract_path: Path to YAML contract file.

        Returns:
            Compiled workflow contract model.

        Raises:
            ContractCompilerError: If compilation fails.
            FileNotFoundError: If contract file not found.
        """
        ...

    async def validate(
        self,
        contract_path: Path,
    ) -> ModelContractValidationResult:
        """
        Validate contract without compiling.

        Args:
            contract_path: Path to contract file.

        Returns:
            Validation result with errors if any.
        """
        ...

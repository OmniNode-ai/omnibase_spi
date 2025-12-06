"""FSM contract compiler protocol."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.contract import (
        ModelContractValidationResult,
        ModelFSMContract,
    )


@runtime_checkable
class ProtocolFSMContractCompiler(Protocol):
    """
    Compile and validate FSM contracts from YAML.

    FSM contracts define finite state machine configurations
    with states, transitions, guards, and actions.

    Note:
        This is a build-time tool for CLI usage, not a runtime node.
        Methods are async to maintain consistency with SPI patterns
        and allow for future flexibility in I/O operations.
    """

    async def compile(
        self,
        contract_path: Path,
    ) -> ModelFSMContract:
        """
        Compile FSM contract from YAML file.

        Args:
            contract_path: Path to YAML contract file.

        Returns:
            Compiled FSM contract model.

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

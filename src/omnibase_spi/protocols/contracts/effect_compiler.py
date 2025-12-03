"""Effect contract compiler protocol."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.contract import (
        ModelContractValidationResult,
        ModelEffectContract,
    )


@runtime_checkable
class ProtocolEffectContractCompiler(Protocol):
    """
    Compile and validate effect contracts from YAML.

    Effect contracts define side-effecting operations such as
    API calls, database queries, and message publishing.
    """

    async def compile(
        self,
        contract_path: Path,
    ) -> "ModelEffectContract":
        """
        Compile effect contract from YAML file.

        Args:
            contract_path: Path to YAML contract file.

        Returns:
            Compiled effect contract model.

        Raises:
            ContractCompilerError: If compilation fails.
            FileNotFoundError: If contract file not found.
        """
        ...

    async def validate(
        self,
        contract_path: Path,
    ) -> "ModelContractValidationResult":
        """
        Validate contract without compiling.

        Args:
            contract_path: Path to contract file.

        Returns:
            Validation result with errors if any.
        """
        ...

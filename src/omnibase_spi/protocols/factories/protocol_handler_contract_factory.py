"""Protocol for handler contract factory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.enums import EnumHandlerTypeCategory
    from omnibase_core.models.contracts.model_handler_contract import (
        ModelHandlerContract,
    )
    from omnibase_core.models.primitives.model_semver import ModelSemVer


@runtime_checkable
class ProtocolHandlerContractFactory(Protocol):
    """
    Factory interface for creating handler contracts.

    This protocol defines the interface for creating default handler
    contracts based on handler type category. Implementations provide
    safe default templates that can be extended via the patch system.

    The version parameter accepts either a string or a ModelSemVer instance
    for semantic version specification.

    Example:
        ```python
        factory: ProtocolHandlerContractFactory = HandlerContractFactory()

        # Using string version
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="my_effect_handler",
            version="1.0.0"
        )

        # Using ModelSemVer
        from omnibase_core.models.primitives.model_semver import ModelSemVer
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="my_compute_handler",
            version=ModelSemVer(major=2, minor=1, patch=0)
        )
        ```
    """

    def get_default(
        self,
        handler_type: EnumHandlerTypeCategory,
        handler_name: str,
        version: ModelSemVer | str = "1.0.0",
    ) -> ModelHandlerContract:
        """
        Get a default handler contract template for the given type.

        Args:
            handler_type: The category of handler (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE)
            handler_name: Unique identifier for the handler
            version: Contract version as ModelSemVer or string (default: "1.0.0")

        Returns:
            A ModelHandlerContract with safe defaults for the handler type

        Raises:
            ValueError: If handler_type is not supported
        """
        ...

    def available_types(self) -> list[EnumHandlerTypeCategory]:
        """
        Return list of handler types this factory supports.

        Returns:
            List of supported EnumHandlerTypeCategory values
        """
        ...

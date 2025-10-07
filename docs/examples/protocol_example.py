"""
Example protocol definition for ONEX systems.

This file demonstrates the proper protocol structure that should be used
instead of Pydantic models in the SPI layer.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolSomeModel(Protocol):
    """Protocol example for data model structure."""

    name: str
    value: int

    async def process_data(self, input_data: str) -> int:
        """
        Process input data according to the model's business logic.

        Args:
            input_data: Input string data to process

        Returns:
            Processed integer result
        """
        ...

    async def validate_model(self) -> bool:
        """
        Validate the model's internal state and constraints.

        Returns:
            True if model is valid, False otherwise
        """
        ...

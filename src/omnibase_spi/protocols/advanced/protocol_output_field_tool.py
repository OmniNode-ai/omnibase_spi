from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolModelOnexField(Protocol):
    """Protocol for ONEX field model."""

    field_name: str
    field_value: Any
    field_type: str


@runtime_checkable
class ProtocolOutputFieldTool(Protocol):
    async def __call__(
        self, state: Any, input_state_dict: dict[str, Any]
    ) -> "ProtocolModelOnexField": ...

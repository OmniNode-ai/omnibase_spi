from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolLogEntry

from omnibase_spi.protocols.types import LiteralLogLevel, ProtocolLogContext


@runtime_checkable
class ProtocolLogger(Protocol):
    """
    Protocol for ONEX logging services that can be resolved from the registry.

    This protocol defines the interface that all logging implementations must
    implement to be compatible with the ONEX logging system.

    Example:
        class MyLogger:
            async def emit(self, level: LiteralLogLevel, message: str, correlation_id: UUID) -> None:

            async def log(self, entry: "ProtocolLogEntry") -> None:
    """

    async def emit(
        self,
        level: LiteralLogLevel,
        message: str,
        correlation_id: UUID,
        context: ProtocolLogContext | None = None,
    ) -> None: ...

    async def log(self, entry: "ProtocolLogEntry") -> None: ...

    async def is_level_enabled(self, level: LiteralLogLevel) -> bool: ...

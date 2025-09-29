from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types import (
    LiteralLogLevel,
    ProtocolLogContext,
    ProtocolLogEntry,
)


@runtime_checkable
class ProtocolLogger(Protocol):
    """
    Protocol for ONEX logging services that can be resolved from the registry.

    This protocol defines the interface that all logging implementations must
    implement to be compatible with the ONEX logging system.

    Example:
        class MyLogger:
            def emit(self, level: LiteralLogLevel, message: str, correlation_id: UUID) -> None:

            def log(self, entry: "ProtocolLogEntry") -> None:
    """

    def emit(
        self,
        level: LiteralLogLevel,
        message: str,
        correlation_id: UUID,
        context: Optional[ProtocolLogContext] = None,
    ) -> None: ...

    def log(self, entry: "ProtocolLogEntry") -> None: ...

    def is_level_enabled(self, level: LiteralLogLevel) -> bool: ...

"""
Storage Backend Protocol for ONEX Checkpoint Storage.
Defines the interface for pluggable storage backends at the root level.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolCheckpointData,
    ProtocolStorageConfiguration,
    ProtocolStorageCredentials,
    ProtocolStorageHealthStatus,
    ProtocolStorageListResult,
    ProtocolStorageResult,
)


@runtime_checkable
class ProtocolStorageBackend(Protocol):
    """
    Protocol for checkpoint storage backends.

    Follows the same pattern as ProtocolEventBus for consistency.
    Provides pluggable storage interface for different backends
    (filesystem, sqlite, postgresql, cloud storage, etc.).

    Key Features:
        - Checkpoint storage and retrieval
        - Listing with filtering and pagination
        - Health monitoring and status
        - Connection testing
        - Retention policy management
    """

    async def store_checkpoint(
        self, checkpoint_data: "ProtocolCheckpointData"
    ) -> "ProtocolStorageResult": ...

    async def retrieve_checkpoint(
        self, checkpoint_id: str
    ) -> "ProtocolStorageResult": ...

    async def list_checkpoints(
        self,
        workflow_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> "ProtocolStorageListResult": ...

    async def delete_checkpoint(
        self, checkpoint_id: str
    ) -> "ProtocolStorageResult": ...

    async def cleanup_expired_checkpoints(
        self, retention_hours: int
    ) -> "ProtocolStorageResult": ...

    async def get_storage_status(self) -> "ProtocolStorageHealthStatus": ...

    async def test_connection(self) -> "ProtocolStorageResult": ...

    async def initialize_storage(self) -> "ProtocolStorageResult": ...

    @property
    def backend_id(self) -> str: ...

    @property
    def backend_type(self) -> str: ...

    @property
    def is_healthy(self) -> bool: ...


@runtime_checkable
class ProtocolStorageBackendFactory(Protocol):
    """
    Protocol for creating storage backends.

    Follows the same pattern as event bus factory for consistency.
    Provides pluggable factory interface for different backend types.
    """

    async def get_storage_backend(
        self,
        backend_type: str,
        storage_config: "ProtocolStorageConfiguration",
        credentials: "ProtocolStorageCredentials | None" = None,
        **kwargs: object,
    ) -> "ProtocolStorageBackend": ...

    async def list_available_backends(self) -> list[str]: ...

    async def validate_backend_config(
        self, backend_type: str, storage_config: "ProtocolStorageConfiguration"
    ) -> "ProtocolStorageResult": ...

    async def get_default_config(
        self, backend_type: str
    ) -> "ProtocolStorageConfiguration": ...

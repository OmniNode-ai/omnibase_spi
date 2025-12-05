"""
Storage Backend Protocol for ONEX Checkpoint Storage.
Defines the interface for pluggable storage backends at the root level.
"""

from typing import Protocol, runtime_checkable

# Import SPI-internal protocol types
from omnibase_spi.protocols.types.protocol_storage_types import (
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

    This protocol defines the interface for pluggable storage backends that handle
    checkpoint operations including storage, retrieval, listing, deletion, and health
    monitoring. Implementations can support various backend types like filesystem,
    SQLite, PostgreSQL, or cloud storage solutions.

    Example:
        @runtime_checkable
        class FileSystemStorageBackend(Protocol):
            @property
            def config(self) -> ProtocolStorageConfiguration: ...
            @property
            def base_path(self) -> str: ...
            @property
            def backend_id(self) -> str: ...
            @property
            def backend_type(self) -> str: ...
            @property
            def is_healthy(self) -> bool: ...

            async def store_checkpoint(
                self, checkpoint_data: ProtocolCheckpointData
            ) -> ProtocolStorageResult: ...
    """

    async def store_checkpoint(
        self,
        checkpoint_data: ProtocolCheckpointData,
    ) -> ProtocolStorageResult:
        """
        Store a checkpoint to the backend.

        Args:
            checkpoint_data: The checkpoint data to store containing workflow state,
                           metadata, and sequence information

        Returns:
            ProtocolStorageResult: Result of the storage operation with success status,
                                 execution metrics, and any error information
        """
        ...

    async def retrieve_checkpoint(self, checkpoint_id: str) -> ProtocolStorageResult:
        """
        Retrieve a checkpoint by ID.

        Args:
            checkpoint_id: Unique checkpoint identifier to retrieve

        Returns:
            ProtocolStorageResult: Result containing checkpoint data if found,
                                 or error information if not found
        """
        ...

    async def list_checkpoints(
        self,
        workflow_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ProtocolStorageListResult:
        """
        List checkpoints, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID filter to restrict results
            limit: Optional limit on number of results to return
            offset: Optional offset for pagination support

        Returns:
            ProtocolStorageListResult: Paginated result containing list of matching
                                     checkpoints with total count and pagination metadata
        """
        ...

    async def delete_checkpoint(self, checkpoint_id: str) -> ProtocolStorageResult:
        """
        Delete a checkpoint by ID.

        Args:
            checkpoint_id: Unique checkpoint identifier to delete

        Returns:
            ProtocolStorageResult: Result of the deletion operation with success
                                 status and any error details
        """
        ...

    async def cleanup_expired_checkpoints(
        self,
        retention_hours: int | None = None,
    ) -> ProtocolStorageResult:
        """
        Clean up expired checkpoints based on retention policies.

        Args:
            retention_hours: Hours to retain checkpoints before cleanup

        Returns:
            ProtocolStorageResult: Result containing number of checkpoints cleaned up
                                 and operation statistics
        """
        ...

    async def get_storage_status(self) -> ProtocolStorageHealthStatus:
        """
        Get storage backend status and health information.

        Returns:
            ProtocolStorageHealthStatus: Comprehensive status information including
                                        health status, capacity metrics, response times,
                                        and detailed check results
        """
        ...

    async def test_connection(self) -> ProtocolStorageResult:
        """
        Test connectivity to the storage backend.

        Returns:
            ProtocolStorageResult: Result of the connection test with latency
                                 metrics and connectivity status
        """
        ...

    async def initialize_storage(self) -> ProtocolStorageResult:
        """
        Initialize storage backend (create tables, directories, etc.).

        Returns:
            ProtocolStorageResult: Result of the initialization operation with
                                 setup details and any configuration errors
        """
        ...

    @property
    def backend_id(self) -> str: ...
    @property
    def backend_type(self) -> str:
        """
        Get backend type (filesystem, sqlite, postgresql, etc.).

        Returns:
            str: String identifier for the backend type
        """
        ...

    @property
    def is_healthy(self) -> bool:
        """
        Check if backend is healthy and operational.

        Returns:
            bool: True if backend is healthy, False otherwise
        """
        ...


@runtime_checkable
class ProtocolStorageBackendFactory(Protocol):
    """
    Protocol for storage backend factory.

    Defines the interface for creating and managing storage backend instances.
    Implementations provide pluggable backend creation with validation and
    default configuration support for various storage types.

    Example:
        class StorageBackendFactory(ProtocolStorageBackendFactory):
            async def get_storage_backend(self, backend_type: str, storage_config: ProtocolStorageConfiguration):
                if backend_type == "filesystem":
                    return FileSystemStorageBackend(storage_config)
                elif backend_type == "sqlite":
                    return SQLiteStorageBackend(storage_config)
                else:
                    raise ValueError(f"Unsupported backend type: {backend_type}")

            async def list_available_backends(self) -> list[str]:
                return ["filesystem", "sqlite", "postgresql", "s3"]

            async def validate_backend_config(self, backend_type: str, storage_config: ProtocolStorageConfiguration):
                # Validate backend-specific configuration
                return ProtocolStorageResult(
                    success=True,
                    operation="validate_config",
                    message=f"Configuration valid for {backend_type}",
                    execution_time_ms=50,
                    timestamp=datetime.utcnow().isoformat()
                )
    """

    async def get_storage_backend(
        self,
        backend_type: str,
        storage_config: ProtocolStorageConfiguration,
        credentials: ProtocolStorageCredentials | None = None,
        **kwargs: object,
    ) -> ProtocolStorageBackend:
        """
        Create a storage backend instance.

        Args:
            backend_type: Storage backend type (filesystem, sqlite, postgresql, etc.)
            storage_config: Storage configuration model with connection parameters
            credentials: Optional authentication credentials for secure backends
            **kwargs: Additional backend-specific parameters

        Returns:
            ProtocolStorageBackend: Configured storage backend instance ready for use
        """
        ...

    async def list_available_backends(self) -> list[str]:
        """
        List available storage backend types.

        Returns:
            List[str]: List of available backend type names that can be created
        """
        ...

    async def validate_backend_config(
        self,
        backend_type: str,
        storage_config: ProtocolStorageConfiguration,
    ) -> ProtocolStorageResult:
        """
        Validate configuration for a specific backend type.

        Args:
            backend_type: Storage backend type to validate configuration for
            storage_config: Configuration to validate for compatibility and completeness

        Returns:
            ProtocolStorageResult: Result of the validation operation with detailed
                                 validation errors if any
        """
        ...

    async def get_default_config(
        self, backend_type: str
    ) -> ProtocolStorageConfiguration:
        """
        Get default configuration for a backend type.

        Args:
            backend_type: Storage backend type to get default configuration for

        Returns:
            ProtocolStorageConfiguration: Default configuration model for the backend type
                                       with sensible defaults and required parameters
        """
        ...

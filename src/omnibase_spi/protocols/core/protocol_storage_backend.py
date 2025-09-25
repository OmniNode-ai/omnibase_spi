"""
Storage Backend Protocol for ONEX Checkpoint Storage.
Defines the interface for pluggable storage backends at the root level.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
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

    def store_checkpoint(
        self,
        checkpoint_data: "ProtocolCheckpointData",
    ) -> "ProtocolStorageResult":
        """
        Store a checkpoint to the backend.

        Args:
            checkpoint_data: The checkpoint data to store

        Returns:
            StorageResult: Result of the storage operation

        Raises:
            ValueError: If checkpoint_data is invalid
            RuntimeError: If storage operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    def retrieve_checkpoint(self, checkpoint_id: str) -> "ProtocolStorageResult":
        """
        Retrieve a checkpoint by ID.

        Args:
            checkpoint_id: Unique checkpoint identifier

        Returns:
            StorageResult: Result containing checkpoint data if found

        Raises:
            ValueError: If checkpoint_id format is invalid
            KeyError: If checkpoint not found
            RuntimeError: If retrieval operation fails
        """
        ...

    def list_checkpoints(
        self,
        workflow_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> "ProtocolStorageListResult":
        """
        List checkpoints, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID filter
            limit: Optional limit on number of results
            offset: Optional offset for pagination

        Returns:
            StorageListResult: Result containing list of matching checkpoints

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If list operation fails
        """
        ...

    def delete_checkpoint(self, checkpoint_id: str) -> "ProtocolStorageResult":
        """
        Delete a checkpoint by ID.

        Args:
            checkpoint_id: Unique checkpoint identifier

        Returns:
            StorageResult: Result of the deletion operation

        Raises:
            ValueError: If checkpoint_id format is invalid
            KeyError: If checkpoint not found
            RuntimeError: If deletion operation fails
        """
        ...

    def cleanup_expired_checkpoints(
        self,
        retention_hours: int,
    ) -> "ProtocolStorageResult":
        """
        Clean up expired checkpoints based on retention policies.

        Args:
            retention_hours: Hours to retain checkpoints

        Returns:
            StorageResult: Result containing number of checkpoints cleaned up

        Raises:
            ValueError: If retention_hours is invalid
            RuntimeError: If cleanup operation fails
        """
        ...

    def get_storage_status(self) -> "ProtocolStorageHealthStatus":
        """
        Get storage backend status and health information.

        Returns:
            StorageHealthStatus: Status information including health, capacity, etc.

        Raises:
            RuntimeError: If status check fails
        """
        ...

    def test_connection(self) -> "ProtocolStorageResult":
        """
        Test connectivity to the storage backend.

        Returns:
            StorageResult: Result of the connection test

        Raises:
            RuntimeError: If connection test fails
        """
        ...

    def initialize_storage(self) -> "ProtocolStorageResult":
        """
        Initialize storage backend (create tables, directories, etc.).

        Returns:
            StorageResult: Result of the initialization operation

        Raises:
            RuntimeError: If initialization fails
        """
        ...

    @property
    def backend_id(self) -> str:
        """
        Get unique backend identifier.

        Returns:
            Unique string identifying this backend instance
        """
        ...

    @property
    def backend_type(self) -> str:
        """
        Get backend type (filesystem, sqlite, postgresql, etc.).

        Returns:
            String identifying the backend type
        """
        ...

    @property
    def is_healthy(self) -> bool:
        """
        Check if backend is healthy and operational.

        Returns:
            True if backend is healthy, False otherwise
        """
        ...


@runtime_checkable
class ProtocolStorageBackendFactory(Protocol):
    """
    Protocol for creating storage backends.

    Follows the same pattern as event bus factory for consistency.
    Provides pluggable factory interface for different backend types.
    """

    def get_storage_backend(
        self,
        backend_type: str,
        storage_config: "ProtocolStorageConfiguration",
        credentials: "ProtocolStorageCredentials | None" = None,
        **kwargs: object,
    ) -> "ProtocolStorageBackend":
        """
        Create a storage backend instance.

        Args:
            backend_type: Storage backend type (filesystem, sqlite, postgresql)
            storage_config: Storage configuration object
            credentials: Optional authentication credentials
            **kwargs: Additional backend-specific parameters

        Returns:
            ProtocolStorageBackend: Configured storage backend instance

        Raises:
            ValueError: If backend_type is invalid or unsupported
            RuntimeError: If backend creation fails
        """
        ...

    def list_available_backends(self) -> list[str]:
        """
        List available storage backend types.

        Returns:
            list[str]: List of available backend type names
        """
        ...

    def validate_backend_config(
        self,
        backend_type: str,
        storage_config: "ProtocolStorageConfiguration",
    ) -> "ProtocolStorageResult":
        """
        Validate configuration for a specific backend type.

        Args:
            backend_type: Storage backend type
            storage_config: Configuration to validate

        Returns:
            StorageResult: Result of the validation operation

        Raises:
            ValueError: If backend_type is invalid
        """
        ...

    def get_default_config(self, backend_type: str) -> "ProtocolStorageConfiguration":
        """
        Get default configuration for a backend type.

        Args:
            backend_type: Storage backend type

        Returns:
            StorageConfiguration: Default configuration object for the backend type

        Raises:
            ValueError: If backend_type is invalid or unsupported
        """
        ...

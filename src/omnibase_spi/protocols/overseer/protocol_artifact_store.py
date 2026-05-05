# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Overseer artifact store protocol.

Defines the contract for durable artifact persistence used by the overseer:
uploading, retrieving, listing, and expiring versioned workflow artifacts such
as plans, evidence bundles, and replay logs.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolArtifactStore(Protocol):
    """Durable key-value store for overseer workflow artifacts.

    An artifact is any named, versioned blob produced or consumed by an
    overseer workflow step (e.g. execution plans, DoD evidence bundles,
    replay transcripts, diff snapshots). Implementations may target the
    local filesystem, S3, GCS, or any object-storage backend.

    Example:
        ```python
        store: ProtocolArtifactStore = get_artifact_store()

        await store.connect()
        key = await store.put("runs/abc123/plan.json", plan_bytes)
        data = await store.get(key)
        listing = await store.list("runs/abc123/")
        await store.delete(key)
        await store.close()
        ```
    """

    # -- Lifecycle --

    async def connect(self) -> bool:
        """Open a connection to the artifact store backend.

        Returns:
            True if connection was established successfully.
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
        """
        ...

    # -- Core CRUD --

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store an artifact under the given key.

        Args:
            key: Logical path / key for the artifact (e.g. ``"runs/abc/plan.json"``).
            data: Raw bytes to store.
            content_type: MIME type of the artifact.
            metadata: Optional key-value annotations stored alongside the artifact.

        Returns:
            Canonical key under which the artifact was stored (may differ from
            input if the backend normalises or versions the key).
        """
        ...

    async def get(self, key: str) -> bytes:
        """Retrieve an artifact by key.

        Args:
            key: Artifact key as returned by ``put``.

        Returns:
            Raw artifact bytes.

        Raises:
            KeyError: If the artifact does not exist.
        """
        ...

    async def delete(self, key: str) -> bool:
        """Remove an artifact from the store.

        Args:
            key: Artifact key to delete.

        Returns:
            True if the artifact was found and deleted, False if it did not exist.
        """
        ...

    async def exists(self, key: str) -> bool:
        """Check whether an artifact exists without fetching its content.

        Args:
            key: Artifact key to check.

        Returns:
            True if the artifact exists in the store.
        """
        ...

    # -- Listing --

    async def list(self, prefix: str = "", limit: int = 1000) -> list[str]:
        """List artifact keys matching a prefix.

        Args:
            prefix: Optional key prefix to filter results.
            limit: Maximum number of keys to return.

        Returns:
            List of artifact keys matching the prefix.
        """
        ...

    # -- Metadata --

    async def get_metadata(self, key: str) -> dict[str, str]:
        """Retrieve metadata annotations for an artifact.

        Args:
            key: Artifact key.

        Returns:
            Metadata dictionary as stored via ``put``.

        Raises:
            KeyError: If the artifact does not exist.
        """
        ...

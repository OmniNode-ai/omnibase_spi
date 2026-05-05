# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for secret/credential store service integration.

Defines the standard interface for secret management systems (Vault, Infisical,
AWS Secrets Manager, environment variables) used by ONEX services for secure
credential retrieval, rotation awareness, and lifecycle management.

Note: omnibase_core defines ProtocolSecretService with a single get_secret method
for template resolution. This protocol extends the concept to a full service
lifecycle with health checks, listing, and connection management.

Protocol invariants (locked by OMN-10556):
    - ``get_secret`` is a *nullable lookup*: callers receive ``None`` for a
      missing key, never an exception. Required-service validation is the
      caller's responsibility (e.g., omnimarket ``Settings`` raises if a
      mandatory secret is unset). The protocol itself never fails fast on a
      missing key.
    - ``set_secret`` and ``delete_secret`` may raise ``RuntimeError`` for
      read-only implementations (env-var-backed stores, Infisical wrappers
      that surface only the SDK's read path). Callers must treat write paths
      as failable; do not assume mutability.
    - The protocol is ``runtime_checkable`` but ``isinstance`` only verifies
      attribute presence. Async signature compatibility (``await
      impl.get_secret(...)``, ``await impl.list_keys(prefix=None)``,
      ``await impl.health_check()``) is verified by behavioral tests, not by
      ``isinstance``.
    - No ``get_secrets_batch`` method is part of the protocol surface. Batch
      retrieval is a performance concern owned by adapters/handlers, not the
      protocol contract.

RBAC:
    - read: Retrieve secrets by key
    - list: Enumerate available secret keys (no values)
    - write: Store or update secrets
    - admin: Delete secrets, manage access policies
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolSecretStore(Protocol):
    """Protocol for secret/credential store service operations.

    Abstracts secret lifecycle management across providers (Vault, Infisical,
    AWS Secrets Manager, env vars) for use in ONEX effect execution, deployment
    pipelines, and service configuration.

    RBAC:
        - read: get_secret
        - list: list_keys
        - write: set_secret
        - admin: delete_secret, rotate policies

    Example:
        ```python
        store: ProtocolSecretStore = get_secret_store()

        api_key = await store.get_secret("llm/openai-api-key")
        if api_key is None:
            raise RuntimeError("Missing required secret")

        keys = await store.list_keys(prefix="llm/")
        print(f"Available LLM secrets: {keys}")
        ```
    """

    async def get_secret(self, key: str) -> str | None:
        """Retrieve a secret value by key.

        Args:
            key: Secret identifier/path (e.g., "llm/openai-api-key",
                "database/postgres-password")

        Returns:
            Secret value if found, None if not found

        Raises:
            PermissionError: If caller lacks read RBAC role
            ConnectionError: If store is unreachable
        """
        ...

    async def set_secret(self, key: str, value: str) -> bool:
        """Store or update a secret value.

        Args:
            key: Secret identifier/path
            value: Secret value to store

        Returns:
            True if stored successfully, False otherwise

        Raises:
            PermissionError: If caller lacks write RBAC role
            ConnectionError: If store is unreachable
        """
        ...

    async def delete_secret(self, key: str) -> bool:
        """Delete a secret by key.

        Args:
            key: Secret identifier/path

        Returns:
            True if deleted, False if not found

        Raises:
            PermissionError: If caller lacks admin RBAC role
            ConnectionError: If store is unreachable
        """
        ...

    async def list_keys(self, prefix: str | None = None) -> list[str]:
        """List available secret keys (values not returned).

        Args:
            prefix: Optional prefix to filter keys (e.g., "llm/" returns
                all LLM-related secret keys)

        Returns:
            List of secret key paths

        Raises:
            PermissionError: If caller lacks list RBAC role
        """
        ...

    async def health_check(self) -> bool:
        """Check if the secret store is reachable and healthy.

        Returns:
            True if store is healthy, False otherwise
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections to the secret store.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the timeout.
        """
        ...

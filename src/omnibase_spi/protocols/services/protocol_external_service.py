# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Base protocol for external service adapters.

Defines the lifecycle contract shared by all external service integrations
(code hosts, ticket trackers, secret stores, databases, etc.). The kernel
uses this protocol to manage adapter lifecycle uniformly — connect, health
check, capability discovery, and teardown — without knowing the domain.

Every domain-specific service protocol (ProtocolCodeHost, ProtocolTicketService,
etc.) should structurally conform to this base protocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_service_types import (
        ProtocolServiceHealthStatus,
    )


@runtime_checkable
class ProtocolExternalService(Protocol):
    """Base lifecycle protocol for external service adapters.

    All external service protocols share connect/health/close lifecycle
    methods. This base protocol lets the kernel manage adapter lifecycle
    uniformly without knowing the domain-specific operations.

    Example:
        ```python
        service: ProtocolExternalService = get_adapter()

        connected = await service.connect()
        if connected:
            health = await service.health_check()
            caps = await service.get_capabilities()
            print(f"Service healthy={health.is_healthy()}, caps={caps}")

        await service.close(timeout_seconds=10.0)
        ```
    """

    async def connect(self) -> bool:
        """Establish a connection to the external service.

        Returns:
            True if connection was established successfully, False otherwise.

        Raises:
            ConnectionError: If the service is unreachable.
        """
        ...

    async def health_check(self) -> ProtocolServiceHealthStatus:
        """Check the health of the external service connection.

        Returns:
            Health status including service ID, status, last check time,
            and diagnostic details.

        Raises:
            ConnectionError: If the service is unreachable.
        """
        ...

    async def get_capabilities(self) -> list[str]:
        """Discover capabilities supported by this service adapter.

        Returns:
            List of capability identifiers (e.g., ``["read", "write", "admin"]``).
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Release resources and close connections to the external service.

        Args:
            timeout_seconds: Maximum time to wait for cleanup.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the timeout.
        """
        ...
